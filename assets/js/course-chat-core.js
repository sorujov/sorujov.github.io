/*
 * course-chat-core.js — retrieval logic for the site assistant (STAT-2311 and
 * the rest of sorujov.net).
 *
 * Pure functions, no DOM, no network. The browser widget and the offline
 * evaluation harness both import this file, so what is measured in
 * scripts/eval is exactly what students run.
 *
 * Answering is a pipeline with four stages, in this order:
 *
 *   1. guard    — questions the assistant must not answer at all
 *   2. facts    — deterministic answers extracted from the syllabus
 *   3. retrieve — BM25 and cosine over the course corpus, fused
 *   4. floor    — refuse when nothing retrieved is close enough
 *
 * Order matters. The guard runs before the facts so that "give me the answers
 * to week 6" is declined rather than matched to the week 6 reading.
 *
 * Every passage and fact has a scope, "course" or "site". A page asks with a
 * preferred scope; that is a nudge in the ranking, never a filter.
 */

const RRF_K = 60;
const BM25_K1 = 1.2;
const BM25_B = 0.75;
const FACT_FLOOR = 3;
const COS_STRONG = 0.55;
const COS_FLOOR = 0.40;
const COS_SOFT = 0.32;
const COVERAGE_FLOOR = 0.60;
const COVERAGE_HIGH = 0.90;
const LEX_FLOOR = 2.5;
const SCOPE_BONUS = 0.008;   // about eight RRF ranks at the top of the list

/* ---------------------------------------------------------------- text --- */

/** Lowercase, punctuation to spaces, single-spaced and padded for phrase tests. */
export function normalize(text) {
  return (
    " " +
    String(text)
      .toLowerCase()
      .normalize("NFKC")
      .replace(/[^a-z0-9§]+/g, " ")
      .trim()
      .replace(/\s+/g, " ") +
    " "
  );
}

/**
 * Mirrors tokenize() in scripts/build_chat_index.py. The stop list travels in
 * lexical.json rather than being duplicated here, so the two cannot drift.
 * scripts/eval/run_eval.mjs asserts the two tokenizers agree.
 */
export function tokenize(text, stop) {
  const stopSet = stop instanceof Set ? stop : new Set(stop || []);
  const cleaned = String(text)
    .toLowerCase()
    .normalize("NFKC")
    .replace(/[^a-z0-9§.\- ]+/g, " ");
  const out = [];
  for (const piece of cleaned.split(/\s+/)) {
    const raw = piece.replace(/^[.\-]+/, "").replace(/[.\-]+$/, "");
    if (!raw || stopSet.has(raw) || raw.length < 2) continue;
    out.push(raw);
    if (raw.endsWith("s") && raw.length > 3) out.push(raw.slice(0, -1));
  }
  return out;
}

/* --------------------------------------------------------------- guard --- */

const GUARDS = [
  {
    kind: "personal",
    test: /(\bmy (grade|score|mark|result|average|standing)\b)|(\bwhat did i (get|score|make)\b)|(\bam i (passing|failing)\b)|(\bhow am i doing\b)/,
    message:
      "I can't see anyone's grades — those live in the Blackboard Grade Centre. " +
      "For a question about your own marks, e-mail Dr. Orujov directly.",
  },
  {
    kind: "admin",
    test: /\b(extension|extend the deadline|late submission|make-up|makeup exam|resit|retake|defer)\b/,
    message:
      "Anything about deadlines, extensions or make-up assessment is a decision " +
      "for Dr. Orujov, not for me. E-mail him at sorujov@ada.edu.az — he answers " +
      "within 48 hours on working days.",
  },
  {
    kind: "solutions",
    test: /(\b(solve|work out)\b)|(\bshow me the (solution|answer)\b)|(\b(answers?|solutions?)\s+(to|for)\b)|(\bwrite my\b)|(\b(do|finish)\s+(my|the)\s+(homework|assignment|problem set)\b)/,
    message:
      "I won't work problems out for you — that is what the tutorials and office " +
      "hours are for. I can point you at the lecture that covers the method, " +
      "and the practice set beside it.",
  },
  {
    kind: "speculation",
    test: /\bwill (this|that|it|there) (be|been) (on|in) the (exam|test|quiz|midterm|final)\b/,
    message:
      "I can only tell you the coverage the syllabus states; I can't predict what " +
      "any particular paper will ask. The coverage for each quiz and midterm is on " +
      "the course page.",
  },
  {
    kind: "private",
    // Only about Dr. Orujov: "a family with three children" is a probability
    // question, "does he have children" is not.
    test: /(\b(he|his|him|samir|samirs|orujov|orujovs|professor|professors|instructor|dr)\b.*\b(phone|mobile|cell|whatsapp|address|live|lives|salary|earn|earns|paid|age|old|married|wife|girlfriend|children|kids|family|religion)\b)|(\b(phone|mobile|cell|whatsapp|address|salary|age|married|wife|children|kids|family|religion)\b.*\b(he|his|him|samir|samirs|orujov|orujovs|professor|instructor|dr)\b)|(\bhow old is (he|samir|orujov|the (professor|instructor))\b)/,
    message:
      "I only know what this site publishes about Dr. Orujov — his work, research, " +
      "teaching and CV. For anything else, e-mail him at sorujov@ada.edu.az.",
  },
  {
    kind: "opinion",
    test: /\b(is|are)\s+(he|she|they|prof|professor|dr|orujov|the (professor|instructor|ta|course))\b[^?]*\b(hard|easy|strict|fair|unfair|good|bad|nice|harsh|lenient)\b/,
    message:
      "I'm not the right source for opinions about the course or the people " +
      "teaching it. I can tell you how the course is structured and assessed.",
  },
];

export function guard(question) {
  const q = normalize(question).trim();
  for (const rule of GUARDS) {
    if (rule.test.test(q)) return { kind: rule.kind, message: rule.message };
  }
  return null;
}

/* --------------------------------------------------------------- facts --- */

/** Precompute normalized keys once, at load. */
export function prepareFacts(facts) {
  return {
    ...facts,
    entries: facts.entries.map((entry) => ({
      ...entry,
      _keys: entry.keys.map((k) => normalize(k)).filter((k) => k.trim().length > 1),
      _question: normalize(entry.question),
    })),
  };
}

function overlapScore(a, b) {
  const A = new Set(a);
  const B = new Set(b);
  if (!A.size) return 0;
  let hits = 0;
  for (const t of A) if (B.has(t)) hits += 1;
  return hits / A.size;
}

export function matchFact(question, facts, stop) {
  const nq = normalize(question);
  const qTokens = tokenize(question, stop);
  let best = null;
  let bestScore = 0;

  for (const entry of facts.entries) {
    let phrase = 0;
    for (const key of entry._keys) {
      if (nq.indexOf(key) !== -1) {
        phrase = Math.max(phrase, key.trim().split(" ").length * 2 + 1);
      }
    }
    if (!phrase) continue;
    const score = phrase + 2 * overlapScore(qTokens, tokenize(entry.question, stop));
    if (score > bestScore) {
      bestScore = score;
      best = entry;
    }
  }
  return bestScore >= FACT_FLOOR ? { entry: best, score: bestScore } : null;
}

/* ----------------------------------------------------------- retrieval --- */

export function bm25(question, lexical) {
  const { postings, lengths, avgdl, n } = lexical;
  const scores = new Float64Array(n);
  const seen = new Set();

  for (const term of tokenize(question, lexical.stop)) {
    if (seen.has(term)) continue;
    seen.add(term);
    const list = postings[term];
    if (!list) continue;
    const idf = Math.log(1 + (n - list.length + 0.5) / (list.length + 0.5));
    for (const [idx, tf] of list) {
      const norm = tf * (BM25_K1 + 1);
      const denom = tf + BM25_K1 * (1 - BM25_B + (BM25_B * lengths[idx]) / avgdl);
      scores[idx] += idf * (norm / denom);
    }
  }
  return scores;
}

/** Cosine against int8 rows of unit vectors; queryVec must be L2-normalised. */
export function cosine(queryVec, embeddings, dims, scale) {
  const rows = embeddings.length / dims;
  const scores = new Float64Array(rows);
  for (let r = 0; r < rows; r += 1) {
    let dot = 0;
    const base = r * dims;
    for (let d = 0; d < dims; d += 1) dot += queryVec[d] * embeddings[base + d];
    scores[r] = dot / scale;
  }
  return scores;
}

function ranked(scores) {
  const order = [];
  for (let i = 0; i < scores.length; i += 1) if (scores[i] > 0) order.push(i);
  order.sort((a, b) => scores[b] - scores[a]);
  return order;
}

/** Reciprocal rank fusion — scale-free, so BM25 and cosine need no calibration. */
export function fuse(lexScores, vecScores, k = 5) {
  const lexOrder = ranked(lexScores);
  const vecOrder = vecScores ? ranked(vecScores) : [];
  const fused = new Map();

  lexOrder.slice(0, 40).forEach((idx, rank) => {
    fused.set(idx, (fused.get(idx) || 0) + 1 / (RRF_K + rank + 1));
  });
  vecOrder.slice(0, 40).forEach((idx, rank) => {
    fused.set(idx, (fused.get(idx) || 0) + 1 / (RRF_K + rank + 1));
  });

  return [...fused.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, k)
    .map(([idx, score]) => ({
      idx,
      score,
      lexical: lexScores[idx] || 0,
      cosine: vecScores ? vecScores[idx] || 0 : null,
    }));
}

/* ------------------------------------------------------------- pipeline --- */

/** Share of the question's content words that appear anywhere in the corpus. */
export function termCoverage(question, lexical) {
  const terms = [...new Set(tokenize(question, lexical.stop))];
  if (!terms.length) return 0;
  let known = 0;
  for (const t of terms) if (lexical.postings[t]) known += 1;
  return known / terms.length;
}

const NOTHING = {
  course:
    "I don't have anything on that. I know the STAT-2311 course page, this term's " +
    "lectures and the rest of this site — try asking about dates, assessment, " +
    "policies or a topic from the course.",
  site:
    "I don't have anything on that. I know what this site holds — Dr. Orujov's " +
    "research, publications, talks, CV and teaching, including the STAT-2311 " +
    "course and its lectures.",
};

/* "Give me an example with calculations" wants a worked slide, not the definition. */
const EXAMPLE_INTENT = /\b(example|examples|worked|calculat\w*|compute|numerical|numbers|numeric|illustrat\w*|walk me through|show me how)\b/;

/** A lecture slide that works something through with numbers. */
export function isWorked(chunk) {
  if (chunk.source !== "lecture") return false;
  const heading = chunk.heading || "";
  if (/\b(practice|exercises?|summary|key formulas|questions|learning objectives)\b/i.test(heading)) return false;
  if (/\b(example|worked|case)\b/i.test(heading)) return true;
  // Multi-digit numbers and decimals; TeX subscripts such as y_1 are single digits.
  return (String(chunk.text).match(/\d*\.\d+|\d{2,}/g) || []).length >= 5;
}

/**
 * For "give me an example of X": find the lecture that best matches X, then
 * lead with that lecture's worked slides and keep the defining passage after
 * them. Ranking alone cannot do this: a worked slide about bond defaults
 * shares few words with "conditional probability", so it is never retrieved.
 */
function workedFirst(ranked, index, lexScores, vecScores) {
  // The anchor is the lecture passage most about the topic, by meaning and by
  // shared words together; either alone picks the wrong lecture on some topics.
  const relevance = (h) => (h.cosine || 0) + 0.02 * (h.lexical || 0);
  const lectures = ranked
    .slice(0, 5)
    .filter((h) => h.chunk.source === "lecture" && !/\b(practice|summary|questions)\b/i.test(h.chunk.heading || ""));
  if (!lectures.length) return ranked;
  const anchor = lectures.reduce((a, b) => (relevance(b) > relevance(a) ? b : a));
  const examples = [];
  index.chunks.forEach((chunk, idx) => {
    if (chunk.url !== anchor.chunk.url || !isWorked(chunk)) return;
    const cos = vecScores ? vecScores[idx] || 0 : 0;
    const lex = lexScores[idx] || 0;
    examples.push({ idx, chunk, score: anchor.score, lexical: lex, cosine: vecScores ? cos : null, rel: cos + 0.02 * lex });
  });
  if (!examples.length) return ranked;
  examples.sort((a, b) => b.rel - a.rel);
  const picked = examples.slice(0, 2);
  const taken = new Set([anchor.idx, ...picked.map((p) => p.idx)]);
  return [...picked, anchor, ...ranked.filter((h) => !taken.has(h.idx))];
}

/**
 * @param {string} question
 * @param {object} index  {facts, chunks, lexical, embeddings, meta}
 * @param {Float32Array|null} queryVec  null falls back to lexical-only retrieval
 * @param {{scope?: "course"|"site"}} [options]  the scope the page prefers
 */
export function ask(question, index, queryVec, options = {}) {
  const scope = options.scope === "course" ? "course" : "site";
  const text = String(question || "").trim();
  if (text.length < 2) return { kind: "empty" };

  const blocked = guard(text);
  if (blocked) return { kind: "refusal", reason: blocked.kind, message: blocked.message };

  const fact = matchFact(text, index.facts, index.lexical.stop);

  const lexScores = bm25(text, index.lexical);
  const vecScores = queryVec
    ? cosine(queryVec, index.embeddings, index.meta.dims, index.meta.scale)
    : null;
  let ranked = fuse(lexScores, vecScores, 15)
    .map((hit) => {
      const chunk = index.chunks[hit.idx];
      const bonus = scope === "course" && chunk.scope === "course" ? SCOPE_BONUS : 0;
      return { ...hit, score: hit.score + bonus, chunk };
    })
    .sort((a, b) => b.score - a.score);
  // "How is the grade calculated" is a logistics question, not a request for
  // a worked example; a matched fact settles which it is.
  if (!fact && EXAMPLE_INTENT.test(normalize(text))) ranked = workedFirst(ranked, index, lexScores, vecScores);
  const hits = ranked.slice(0, 5);

  if (fact) {
    // Related material comes from the page the fact is on; a slide about credit
    // grades is not related to "how is the grade calculated".
    const page = (url) => String(url).split("#")[0].replace(/\/$/, "");
    const seen = new Set();
    const related = hits.filter((h) => {
      const key = `${h.chunk.url}|${h.chunk.heading}`;
      const here = page(h.chunk.url);
      const there = page(fact.entry.url);
      const same = there ? here === there || here.startsWith(`${there}/`) : here === "";
      if (seen.has(key) || !same) return false;
      seen.add(key);
      return true;
    });
    return {
      kind: "fact",
      answer: fact.entry.answer,
      url: fact.entry.url,
      question: fact.entry.question,
      label: fact.entry.label || "course page",
      scope: fact.entry.scope || "course",
      score: fact.score,
      passages: related.slice(0, 3),
    };
  }

  const bestCos = vecScores ? Math.max(0, ...hits.map((h) => h.cosine || 0)) : 0;
  const bestLex = Math.max(0, ...hits.map((h) => h.lexical || 0));

  // A question made largely of words the corpus has never seen is off topic,
  // however fluently it embeds: "what is the weather in Baku" reaches cosine
  // 0.43 against the course page on the strength of the word Baku alone.
  // Similarity alone is therefore not enough — it has to be backed either by a
  // very strong match or by the question's own words appearing in the corpus.
  const coverage = termCoverage(text, index.lexical);
  const confident = vecScores
    ? bestCos >= COS_STRONG ||
      (bestCos >= COS_FLOOR && coverage >= COVERAGE_FLOOR) ||
      (bestCos >= COS_SOFT && coverage >= COVERAGE_HIGH)
    : bestLex >= LEX_FLOOR && coverage >= COVERAGE_HIGH;

  if (!hits.length || !confident) {
    return { kind: "refusal", reason: "out-of-scope", message: NOTHING[scope], passages: hits.slice(0, 2) };
  }

  return { kind: "passages", passages: hits.slice(0, 3), bestCos, bestLex, coverage };
}

export const TUNING = { SCOPE_BONUS, RRF_K, BM25_K1, BM25_B, FACT_FLOOR, COS_STRONG, COS_FLOOR, COS_SOFT, COVERAGE_FLOOR, COVERAGE_HIGH, LEX_FLOOR };
