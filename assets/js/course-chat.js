/*
 * course-chat.js — the site assistant: STAT-2311 on the course pages, the
 * whole of sorujov.net everywhere else.
 *
 * Everything runs in the visitor's browser. The page ships a ~1 MB index of
 * the site; a ~23 MB embedding model is fetched on first use and
 * cached; an optional ~335 MB chat model is fetched only if the student asks
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
 * Qwen3-0.6B was the only model to decline every out-of-context question
 * (12/12) while carrying every figure through (24/24).
 * The f16 build needs the GPU's shader-f16 feature; without it, the same
 * model in f32. Sizes are the weight download (ndarray-cache.json). */
const CHAT_MODELS = {
  f16: { id: "Qwen3-0.6B-q4f16_1-MLC", mb: 335 },
  f32: { id: "Qwen3-0.6B-q4f32_1-MLC", mb: 335 },
};

/* Generation runs only on STAT-2311 material (see canWrite), so the prompt is
 * the course's. It never names "context" or "material": a small model repeats
 * such words back to the student. */
const SYSTEM = [
  "You help students of STAT-2311 Mathematical Statistics I at ADA University.",
  "Use only the notes in the user's message; they are from the syllabus and the lecture slides.",
  "Copy dates, percentages and room numbers exactly; never change a number.",
  "If the notes answer the question, answer it directly in at most three sentences.",
  "If the notes contain a worked example with numbers, walk through that example step by step using its numbers, in at most five sentences.",
  "Never invent a new problem, new numbers or facts that are not in the notes.",
  "If the notes do not answer the question, reply only: I can't find that in the course notes.",
  "Write mathematics as \\( ... \\), never with dollar signs.",
].join(" ");

const WORDING = {
  course: {
    title: "Ask about this course",
    sub: "STAT-2311 · runs on your device, nothing is sent",
    welcome:
      "Dates, deadlines, grading, or a topic from the lectures — answers are quoted " +
      "from the syllabus and this term's slides. The syllabus is authoritative; for " +
      "anything graded, e-mail Dr. Orujov.",
    launcher: "Ask about STAT-2311",
    placeholder: "When is Midterm I?",
    teaser: "Questions about the course? Ask here.",
    suggestions: [
      "When is Quiz II?",
      "How is the grade calculated?",
      "When are problem sets due?",
      "Give me an example of conditional probability",
      "Which textbook do we use?",
    ],
  },
  site: {
    title: "Ask about this site",
    sub: "Research, teaching, CV · runs on your device, nothing is sent",
    welcome:
      "Ask about Dr. Orujov's research, publications, talks, CV or teaching, or about " +
      "the STAT-2311 course. Answers are quoted from this site, with a link to the page " +
      "each one comes from.",
    launcher: "Ask about this site",
    placeholder: "What does Dr. Orujov research?",
    teaser: "Questions about my research or teaching? Ask here.",
    suggestions: [
      "What does he research?",
      "Where did he get his PhD?",
      "What has he published?",
      "Which courses does he teach?",
      "When is Quiz II?",
    ],
  },
};

const SCOPE = document.getElementById("course-chat")?.dataset.scope === "course" ? "course" : "site";
const WORDS = WORDING[SCOPE];

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
      <p class="cc-cite">From the <a href="${escape(result.url)}">${escape(result.label || "course page")}</a>.</p>
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
  const lead = result.passages.every((p) => p.chunk.scope === "course") ? "From the course material" : "From this site";
  return `<p class="cc-lead">${lead}:</p><ul class="cc-passages">${items}</ul>`;
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

/**
 * The notes the model may write from, or null when it must not write at all.
 * Only STAT-2311 material qualifies: anything about Dr. Orujov himself — home
 * page, CV, publications — is shown as quotes and never paraphrased.
 */
function canWrite(result) {
  if (result.kind === "fact") return result.scope === "course" ? result.answer : null;
  if (result.kind !== "passages" || result.passages[0]?.chunk.scope !== "course") return null;
  return result.passages
    .filter((p) => p.chunk.scope === "course")
    .map((p) => p.chunk.text)
    .join("\n\n");
}

// MathJax on this site reads \( \) and \[ \], not dollar signs. Only spans that
// look like TeX are converted: the slides are about money, and "$5 and $6"
// must stay two prices.
const looksTeX = (m) => !/^\d/.test(m) && /[\\^_={}]|^[A-Za-z]$|[A-Za-z]\(/.test(m);
const texDelimiters = (s) =>
  s
    .replace(/\$\$([\s\S]+?)\$\$/g, (all, m) => (looksTeX(m) ? `\\[${m}\\]` : all))
    .replace(/\$([^$\n]+?)\$/g, (all, m) => (looksTeX(m) ? `\\(${m}\\)` : all));

async function generate(question, notes, onToken) {
  const stream = await engine.chat.completions.create({
    messages: [
      { role: "system", content: SYSTEM },
      { role: "user", content: `Notes:\n${notes}\n\nQuestion: ${question}` },
    ],
    temperature: 0.2,
    max_tokens: 320,
    stream: true,
    // Qwen3 reasons aloud by default; the benchmark ran with this off too.
    extra_body: { enable_thinking: false },
  });

  // Belt and braces: never show a <think> block, even an empty one.
  const clean = (s) => texDelimiters(s.replace(/<think>[\s\S]*?(<\/think>|$)/g, "").trimStart());

  let text = "";
  for await (const part of stream) {
    const delta = part.choices?.[0]?.delta?.content || "";
    if (delta) {
      text += delta;
      onToken(clean(text));
    }
  }
  return clean(text);
}

/* ----------------------------------------------------------------- widget -- */

const ICON_CHAT =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5.5A2.5 2.5 0 0 1 6.5 3h11A2.5 2.5 0 0 1 20 5.5v8a2.5 2.5 0 0 1-2.5 2.5H10l-4.2 3.6c-.5.4-1.3.1-1.3-.6V16A2.5 2.5 0 0 1 4 13.5z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><path d="M8.5 8.5h7M8.5 11.5h4.5" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></svg>';
const ICON_SEND =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h13M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICON_EXPAND =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 4h6v6M10 20H4v-6M20 4l-7 7M4 20l7-7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICON_SHRINK =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 11h-6V5M5 13h6v6M13 11l7-7M11 13l-7 7" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const ICON_CLOSE =
  '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6l12 12M18 6L6 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>';

function mount(root, { floating = false } = {}) {
  root.innerHTML = `
    <div class="cc-shell">
      <div class="cc-head">
        <span class="cc-badge">${ICON_CHAT}</span>
        <div class="cc-head-text">
          <h2 class="cc-title">${WORDS.title}</h2>
          <p class="cc-sub">${WORDS.sub}</p>
        </div>
        ${floating ? `<button class="cc-close cc-expand" type="button" aria-label="Full screen" aria-pressed="false">${ICON_EXPAND}</button>` : ""}
        ${floating ? `<button class="cc-close" type="button" aria-label="Close the assistant">${ICON_CLOSE}</button>` : ""}
      </div>

      <div class="cc-body">
        <div class="cc-welcome">
          <p>${WORDS.welcome}</p>
        </div>
        <div class="cc-log" role="log" aria-live="polite" aria-label="Answers"></div>
        <div class="cc-chips"></div>
      </div>

      <form class="cc-form" autocomplete="off">
        <label class="cc-label" for="cc-input">Your question</label>
        <input id="cc-input" class="cc-input" type="text" name="q"
               placeholder="${WORDS.placeholder}" maxlength="200">
        <button class="cc-send" type="submit" aria-label="Ask">${ICON_SEND}</button>
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

  WORDS.suggestions.forEach((text) => {
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

  const body = root.querySelector(".cc-body");
  const welcome = root.querySelector(".cc-welcome");

  // Scroll the transcript, never the page behind it.
  const follow = () => {
    body.scrollTop = body.scrollHeight;
  };

  const say = (html, cls = "") => {
    welcome.hidden = true;
    chips.hidden = true;
    const block = document.createElement("div");
    block.className = `cc-turn ${cls}`.trim();
    block.innerHTML = html;
    log.appendChild(block);
    follow();
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
      // A closed floating panel waits until it is opened.
      if (floating) input.addEventListener("focus", () => upgrade.click(), { once: true });
      else upgrade.click();
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

      const result = ask(question, index, vector, { scope: SCOPE });
      pending.innerHTML = renderAnswer(result);
      typeset(pending);
      follow();

      const notes = smart && engine ? canWrite(result) : null;
      if (notes) {
        const prose = document.createElement("p");
        prose.className = "cc-generated";
        pending.prepend(prose);
        await generate(question, notes, (text) => {
          prose.textContent = text;
          follow();
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
        '<p class="cc-refusal">Something went wrong loading the search index. ' +
        'Reload the page, or browse the <a href="/teaching/">teaching</a> and <a href="/cv/">CV</a> pages directly.</p>';
    } finally {
      busy = false;
      input.focus();
    }
  });

  // Warm the index as soon as the student shows intent, so the first answer is instant.
  input.addEventListener("focus", () => loadIndex().catch(() => {}), { once: true });
}

/* --------------------------------------------------------------- floating -- */

// A launcher in the corner that opens the widget as a panel. It never opens on
// its own; a first-time visitor gets a one-line hint beside the launcher.
function mountFloating(root) {
  root.classList.add("cc-floating");
  root.innerHTML = `
    <div class="cc-backdrop" aria-hidden="true"></div>
    <div class="cc-panel" id="cc-panel" role="dialog" aria-modal="false"
         aria-label="Site assistant" hidden></div>
    <div class="cc-teaser" hidden>
      <button class="cc-teaser-text" type="button">${WORDS.teaser}</button>
      <button class="cc-teaser-x" type="button" aria-label="Dismiss">${ICON_CLOSE}</button>
    </div>
    <button class="cc-launcher" type="button" aria-expanded="false" aria-controls="cc-panel">
      ${ICON_CHAT}<span class="cc-launcher-label">${WORDS.launcher}</span>
    </button>`;

  const panel = root.querySelector(".cc-panel");
  const launcher = root.querySelector(".cc-launcher");
  const teaser = root.querySelector(".cc-teaser");
  mount(panel, { floating: true });

  const hideTeaser = () => {
    teaser.hidden = true;
  };

  const setOpen = (open) => {
    panel.hidden = !open;
    root.classList.toggle("is-open", open);
    launcher.setAttribute("aria-expanded", String(open));
    hideTeaser();
    if (open) {
      store.set("cc-teased", "1");
      panel.querySelector(".cc-input").focus();
    } else {
      launcher.focus();
    }
  };

  const expand = panel.querySelector(".cc-expand");
  const setExpanded = (on) => {
    root.classList.toggle("is-expanded", on);
    expand.setAttribute("aria-pressed", String(on));
    expand.setAttribute("aria-label", on ? "Exit full screen" : "Full screen");
    expand.innerHTML = on ? ICON_SHRINK : ICON_EXPAND;
    store.set("cc-expanded", on ? "1" : "0");
  };
  expand.addEventListener("click", () => setExpanded(!root.classList.contains("is-expanded")));
  setExpanded(store.get("cc-expanded") === "1");
  root.querySelector(".cc-backdrop").addEventListener("click", () => setOpen(false));

  launcher.addEventListener("click", () => setOpen(panel.hidden));
  panel.querySelector(".cc-close:not(.cc-expand)").addEventListener("click", () => setOpen(false));
  root.querySelector(".cc-teaser-text").addEventListener("click", () => setOpen(true));
  root.querySelector(".cc-teaser-x").addEventListener("click", () => {
    store.set("cc-teased", "1");
    hideTeaser();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) setOpen(false);
  });

  if (store.get("cc-teased") !== "1") {
    setTimeout(() => {
      if (!panel.hidden) return;
      teaser.hidden = false;
      store.set("cc-teased", "1");
      setTimeout(hideTeaser, 12000);
    }, 2500);
  }
}

const root = document.getElementById("course-chat");
if (root) {
  if (root.dataset.mode === "floating") mountFloating(root);
  else mount(root);
}
