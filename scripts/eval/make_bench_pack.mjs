/*
 * make_bench_pack.mjs — build the prompt pack the cluster benchmark runs.
 *
 * The question the benchmark answers is narrow and decidable: given retrieved
 * context, which small model can be trusted to (a) carry an exact figure
 * through without altering it, (b) invent nothing, and (c) decline when the
 * context does not contain the answer. That is the whole job of the optional
 * generation layer, so it is the whole benchmark.
 *
 *   node scripts/eval/make_bench_pack.mjs
 */

import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { ask, prepareFacts } from "../../assets/js/course-chat-core.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "../..");
const read = (p) => JSON.parse(readFileSync(resolve(REPO, p), "utf-8"));

const chunks = read("assets/chat/chunks.json");
const lexical = read("assets/chat/lexical.json");
const meta = read("assets/chat/meta.json");
const rawFacts = read("assets/chat/facts.json");
const facts = prepareFacts(rawFacts);
const embeddings = new Int8Array(readFileSync(resolve(REPO, "assets/chat/embeddings.bin")));
const index = { chunks, lexical, meta, facts, embeddings };
const queries = read("scripts/eval/queries.json");
const golden = read("scripts/eval/golden.json").cases;

const DATE = /\b\d{1,2}\s+(January|February|March|April|May|June|July|August|September|October|November|December)\b/gi;
const PCT = /\b\d{1,3}%/g;

const items = [];

/* 1. figure fidelity — context holds exactly one date or one percentage ---- */
for (const entry of rawFacts.entries) {
  const dates = [...new Set(entry.answer.match(DATE) || [])];
  const pcts = [...new Set(entry.answer.match(PCT) || [])];
  if (dates.length === 1 && pcts.length <= 1) {
    items.push({
      id: `figure-${entry.id}`,
      kind: "figure",
      question: entry.question,
      context: entry.answer,
      gold: dates[0],
      forbid: "date",
    });
  } else if (pcts.length === 1 && dates.length === 0) {
    items.push({
      id: `figure-${entry.id}`,
      kind: "figure",
      question: entry.question,
      context: entry.answer,
      gold: pcts[0],
      forbid: "pct",
    });
  }
  if (items.filter((i) => i.kind === "figure").length >= 24) break;
}

/* 2. refusal — the context genuinely does not answer the question ---------- */
const decoys = chunks.filter((c) => c.source === "lecture").slice(0, 40);
const unanswerable = [
  "When is the final examination?",
  "What is my current grade in the course?",
  "How many students are enrolled in section 10462?",
  "What is the pass mark for this course?",
  "Who marks the midterm papers?",
  "Is attendance compulsory at lectures?",
  "What happens if I miss the quiz because I am ill?",
  "Can I take the course without the prerequisite?",
  "What is the average grade in this course?",
  "Where do I buy the textbook in Baku?",
  "Is the midterm open book?",
  "How long is each quiz in minutes?",
];
unanswerable.forEach((question, i) => {
  items.push({
    id: `refuse-${i}`,
    kind: "refuse",
    question,
    context: decoys[(i * 3) % decoys.length].text,
    gold: null,
  });
});

/* 3. faithfulness — real retrieval output for real content questions ------- */
for (const testCase of golden.filter((c) => c.type === "content")) {
  const vec = queries[testCase.q] ? Float32Array.from(queries[testCase.q]) : null;
  const out = ask(testCase.q, index, vec);
  if (!out.passages || !out.passages.length) continue;
  items.push({
    id: `faithful-${items.length}`,
    kind: "faithful",
    question: testCase.q,
    context: out.passages.map((p) => p.chunk.text).join("\n\n"),
    gold: null,
  });
}

mkdirSync(resolve(REPO, "scripts/eval/bench"), { recursive: true });
writeFileSync(
  resolve(REPO, "scripts/eval/bench/prompts.json"),
  JSON.stringify({ built: new Date().toISOString(), items }, null, 1)
);

const counts = items.reduce((acc, i) => ({ ...acc, [i.kind]: (acc[i.kind] || 0) + 1 }), {});
console.log(`prompt pack: ${items.length} items`, counts);
