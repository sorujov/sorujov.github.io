/*
 * course-chat.js — the STAT-2311 course assistant.
 *
 * Everything runs in the student's browser. The page ships a ~300 KB index of
 * the course material; a ~23 MB embedding model is fetched on first use and
 * cached; an optional ~900 MB chat model is fetched only if the student asks
 * for it. No question ever leaves the device, and nothing is logged.
 *
 * Retrieval lives in course-chat-core.js, which the offline evaluation in
 * scripts/eval imports unchanged.
 */

import { ask, prepareFacts } from "./course-chat-core.js";

// document.currentScript is null inside a module, so find the tag by its src.
const BASE =
  document.querySelector('script[src*="course-chat.js"]')?.dataset.base || "/assets/chat";
const TRANSFORMERS = "https://cdn.jsdelivr.net/npm/@huggingface/transformers@4.3.0";
// jsDelivr, not esm.run: the site's Content-Security-Policy allows only the former.
const WEBLLM = "https://cdn.jsdelivr.net/npm/@mlc-ai/web-llm@0.2.85/+esm";
const EMBED_MODEL = "Xenova/all-MiniLM-L6-v2";

/* Chosen by scripts/eval/bench on the IRISA cluster — see CLAUDE.md.
 * The f16 build needs the GPU's shader-f16 feature; without it, the same
 * model in f32. Sizes are WebLLM's own vram_required_MB. */
const CHAT_MODELS = {
  f16: { id: "Llama-3.2-1B-Instruct-q4f16_1-MLC", mb: 879 },
  f32: { id: "Llama-3.2-1B-Instruct-q4f32_1-MLC", mb: 1129 },
};

const SYSTEM = [
  "You are the assistant for STAT-2311 Mathematical Statistics I at ADA University.",
  "Answer using ONLY the course material given in CONTEXT.",
  "Quote dates, percentages and room numbers exactly as they appear; never adjust them.",
  "If CONTEXT does not contain the answer, say you don't have it in the course material.",
  "Never work a problem out for the student; point them to the lecture and the tutorial.",
  "Answer in at most three sentences, in plain prose.",
].join(" ");

const SUGGESTIONS = [
  "When is Quiz II?",
  "How is the grade calculated?",
  "When are problem sets due?",
  "What is conditional probability?",
  "Which textbook do we use?",
];

const store = {
  get(key) {
    try {
      return window.localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  set(key, value) {
    try {
      window.localStorage.setItem(key, value);
    } catch {
      /* private mode, blocked storage — the widget works without it */
    }
  },
};

/* ----------------------------------------------------------------- state -- */

let index = null;
let indexPromise = null;
let embedder = null;
let embedderPromise = null;
let embedderFailed = false;
let engine = null;
let enginePromise = null;

async function loadIndex() {
  if (index) return index;
  if (indexPromise) return indexPromise;
  indexPromise = (async () => {
    const [facts, chunks, lexical, meta, bin] = await Promise.all([
      fetch(`${BASE}/facts.json`).then((r) => r.json()),
      fetch(`${BASE}/chunks.json`).then((r) => r.json()),
      fetch(`${BASE}/lexical.json`).then((r) => r.json()),
      fetch(`${BASE}/meta.json`).then((r) => r.json()),
      fetch(`${BASE}/embeddings.bin`).then((r) => r.arrayBuffer()),
    ]);
    index = {
      facts: prepareFacts(facts),
      chunks,
      lexical,
      meta,
      embeddings: new Int8Array(bin),
    };
    return index;
  })();
  return indexPromise;
}

async function loadEmbedder(onProgress) {
  if (embedder || embedderFailed) return embedder;
  if (embedderPromise) return embedderPromise;
  embedderPromise = (async () => {
    try {
      const { pipeline } = await import(/* webpackIgnore: true */ TRANSFORMERS);
      embedder = await pipeline("feature-extraction", EMBED_MODEL, {
        dtype: "q8",
        progress_callback: onProgress,
      });
      return embedder;
    } catch (error) {
      // Offline, blocked CDN, or an unsupported runtime. Keyword search still
      // answers most questions, so degrade rather than fail.
      console.warn("course-chat: embedding model unavailable, using keyword search", error);
      embedderFailed = true;
      return null;
    }
  })();
  return embedderPromise;
}

async function embed(text) {
  const model = await loadEmbedder();
  if (!model) return null;
  const output = await model(text, { pooling: "mean", normalize: true });
  return Float32Array.from(output.data);
}

/* -------------------------------------------------------------- rendering -- */

const escape = (s) =>
  String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );

function sourceLink(chunk) {
  const where = chunk.heading ? `${chunk.title} — ${chunk.heading}` : chunk.title;
  return `<a class="cc-source" href="${escape(chunk.url)}">${escape(where)}</a>`;
}

/** The site loads MathJax 3; typeset any TeX that came through in a passage. */
function typeset(element) {
  const mj = window.MathJax;
  if (!mj?.typesetPromise) return;
  Promise.resolve(mj.startup?.promise)
    .then(() => mj.typesetPromise([element]))
    .catch(() => {});
}

function renderAnswer(result) {
  if (result.kind === "empty") return "";

  if (result.kind === "refusal") {
    return `<p class="cc-refusal">${escape(result.message)}</p>`;
  }

  if (result.kind === "fact") {
    const extra = result.passages
      .slice(0, 2)
      .map((p) => `<li>${sourceLink(p.chunk)}</li>`)
      .join("");
    return `
      <p class="cc-fact">${escape(result.answer)}</p>
      <p class="cc-cite">From the <a href="${escape(result.url)}">course page</a>.</p>
      ${extra ? `<details class="cc-more"><summary>Related material</summary><ul>${extra}</ul></details>` : ""}
    `;
  }

  const items = result.passages
    .map(
      (p) => `
      <li class="cc-passage">
        <blockquote>${escape(p.chunk.text)}</blockquote>
        ${sourceLink(p.chunk)}
      </li>`
    )
    .join("");
  return `<p class="cc-lead">From the course material:</p><ul class="cc-passages">${items}</ul>`;
}

/* ------------------------------------------------------------ generation -- */

let chatModelPromise = null;

// Resolves to the CHAT_MODELS entry this device can run, or null when WebGPU
// is absent or no adapter is available (blocklisted driver, remote desktop).
function chatModel() {
  if (chatModelPromise) return chatModelPromise;
  chatModelPromise = (async () => {
    if (typeof navigator === "undefined" || !("gpu" in navigator)) return null;
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (!adapter) return null;
      return adapter.features.has("shader-f16") ? CHAT_MODELS.f16 : CHAT_MODELS.f32;
    } catch {
      return null;
    }
  })();
  return chatModelPromise;
}

async function loadEngine(onProgress) {
  if (engine) return engine;
  if (enginePromise) return enginePromise;
  enginePromise = (async () => {
    const model = await chatModel();
    if (!model) throw new Error("no usable WebGPU adapter");
    const webllm = await import(/* webpackIgnore: true */ WEBLLM);
    engine = await webllm.CreateMLCEngine(model.id, { initProgressCallback: onProgress });
    return engine;
  })();
  // A failed attempt must not stick, or the button can never retry.
  enginePromise.catch(() => {
    enginePromise = null;
  });
  return enginePromise;
}

async function generate(question, result, onToken) {
  const context =
    result.kind === "fact"
      ? result.answer
      : result.passages.map((p) => p.chunk.text).join("\n\n");

  const stream = await engine.chat.completions.create({
    messages: [
      { role: "system", content: SYSTEM },
      { role: "user", content: `CONTEXT:\n${context}\n\nQUESTION: ${question}` },
    ],
    temperature: 0.2,
    max_tokens: 200,
    stream: true,
  });

  let text = "";
  for await (const part of stream) {
    const delta = part.choices?.[0]?.delta?.content || "";
    if (delta) {
      text += delta;
      onToken(text);
    }
  }
  return text;
}

/* ----------------------------------------------------------------- widget -- */

function mount(root) {
  root.innerHTML = `
    <div class="cc-shell">
      <div class="cc-head">
        <h2 class="cc-title">Ask about this course</h2>
        <p class="cc-sub">Answers come from the syllabus and this term's lectures, and are
          worked out on your own device. The syllabus is authoritative; for anything graded,
          e-mail Dr. Orujov.</p>
      </div>

      <div class="cc-log" role="log" aria-live="polite" aria-label="Answers"></div>

      <div class="cc-chips"></div>

      <form class="cc-form" autocomplete="off">
        <label class="cc-label" for="cc-input">Your question</label>
        <input id="cc-input" class="cc-input" type="text" name="q"
               placeholder="When is Midterm I?" maxlength="200">
        <button class="cc-send" type="submit">Ask</button>
      </form>

      <div class="cc-foot">
        <button class="cc-upgrade" type="button" hidden></button>
        <span class="cc-status" aria-live="polite"></span>
      </div>
    </div>`;

  const log = root.querySelector(".cc-log");
  const form = root.querySelector(".cc-form");
  const input = root.querySelector(".cc-input");
  const chips = root.querySelector(".cc-chips");
  const status = root.querySelector(".cc-status");
  const upgrade = root.querySelector(".cc-upgrade");

  SUGGESTIONS.forEach((text) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "cc-chip";
    chip.textContent = text;
    chip.addEventListener("click", () => {
      input.value = text;
      form.requestSubmit();
    });
    chips.appendChild(chip);
  });

  const say = (html, cls = "") => {
    const block = document.createElement("div");
    block.className = `cc-turn ${cls}`.trim();
    block.innerHTML = html;
    log.appendChild(block);
    block.scrollIntoView({ block: "nearest", behavior: "smooth" });
    return block;
  };

  /* --- optional generation ------------------------------------------- */
  let smart = false;
  let model = null; // set once the GPU has been probed

  function paintUpgrade() {
    if (!model) {
      upgrade.hidden = true;
      return;
    }
    upgrade.hidden = false;
    upgrade.textContent = smart
      ? "Conversational answers: on"
      : `Turn on conversational answers (${model.mb} MB, once)`;
    upgrade.classList.toggle("is-on", smart);
  }

  upgrade.addEventListener("click", async () => {
    if (smart) {
      smart = false;
      store.set("cc-smart", "0");
      paintUpgrade();
      status.textContent = "Back to quoting the course material directly.";
      return;
    }
    upgrade.disabled = true;
    try {
      await loadEngine((report) => {
        const pct = Math.round((report.progress || 0) * 100);
        status.textContent = report.text || `Downloading the model… ${pct}%`;
      });
      smart = true;
      store.set("cc-smart", "1");
      status.textContent = "Ready — the model is cached for next time.";
    } catch (error) {
      console.warn("course-chat: model failed to load", error);
      status.textContent = "The model could not be loaded. Answers stay as direct quotes.";
    } finally {
      upgrade.disabled = false;
      paintUpgrade();
    }
  });

  paintUpgrade();
  chatModel().then((found) => {
    model = found;
    paintUpgrade();
    if (model && store.get("cc-smart") === "1") {
      // Previously enabled on this device, so the weights are already cached.
      upgrade.click();
    }
  });

  /* --- asking ---------------------------------------------------------- */
  let busy = false;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const question = input.value.trim();
    if (!question || busy) return;
    busy = true;
    input.value = "";
    say(`<p class="cc-q">${escape(question)}</p>`, "cc-turn-q");
    const pending = say('<p class="cc-thinking">Looking…</p>', "cc-turn-a");

    try {
      await loadIndex();
      if (!embedder && !embedderFailed) {
        status.textContent = "Preparing search (one-time, ~23 MB)…";
      }
      const vector = await embed(question);
      status.textContent = embedderFailed ? "Keyword search only — the model CDN is unreachable." : "";

      const result = ask(question, index, vector);
      pending.innerHTML = renderAnswer(result);
      typeset(pending);

      if (smart && engine && (result.kind === "fact" || result.kind === "passages")) {
        const prose = document.createElement("p");
        prose.className = "cc-generated";
        pending.prepend(prose);
        await generate(question, result, (text) => {
          prose.textContent = text;
        });
        typeset(pending);
        const note = document.createElement("p");
        note.className = "cc-note";
        note.textContent = "Written by a small model from the quoted material below. Check it against the source.";
        prose.after(note);
      }
    } catch (error) {
      console.error("course-chat", error);
      pending.innerHTML =
        '<p class="cc-refusal">Something went wrong loading the course material. ' +
        'Reload the page, or read the <a href="/teaching/2026-fall-mathematical-statistics-I">course page</a> directly.</p>';
    } finally {
      busy = false;
      input.focus();
    }
  });

  // Warm the index as soon as the student shows intent, so the first answer is instant.
  input.addEventListener("focus", () => loadIndex().catch(() => {}), { once: true });
}

const root = document.getElementById("course-chat");
if (root) mount(root);
