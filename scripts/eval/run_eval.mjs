/*
 * run_eval.mjs — offline evaluation of the course assistant.
 *
 *   python3 scripts/build_chat_index.py
 *   python3 scripts/eval/embed_queries.py
 *   node scripts/eval/run_eval.mjs
 *
 * Imports the same retrieval module the browser loads, so a passing run here
 * is a statement about what students actually get. Exits non-zero if any gate
 * fails, which makes it usable as a CI step.
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

import { ask, prepareFacts, tokenize } from "../../assets/js/course-chat-core.js";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, "../..");
const read = (p) => JSON.parse(readFileSync(resolve(REPO, p), "utf-8"));

const GATES = { logistics: 0.95, content: 0.85, refuse: 0.9 };

const chunks = read("assets/chat/chunks.json");
const lexical = read("assets/chat/lexical.json");
const meta = read("assets/chat/meta.json");
const facts = prepareFacts(read("assets/chat/facts.json"));
const embeddings = new Int8Array(readFileSync(resolve(REPO, "assets/chat/embeddings.bin")));
const index = { chunks, lexical, meta, facts, embeddings };

const cases = read("scripts/eval/golden.json").cases;
const queries = read("scripts/eval/queries.json");

/* --- guard: the two tokenizers must agree ------------------------------- */
const stop = new Set(lexical.stop);
let probeFailures = 0;
for (const { text, tokens } of lexical.probe) {
  const mine = tokenize(text, stop);
  if (JSON.stringify(mine) !== JSON.stringify(tokens)) {
    probeFailures += 1;
    console.error(`tokenizer drift on ${JSON.stringify(text)}`);
    console.error(`  python: ${JSON.stringify(tokens)}`);
    console.error(`  js    : ${JSON.stringify(mine)}`);
  }
}
if (probeFailures) {
  console.error("\nFAIL — the browser tokenizer no longer matches the index build.");
  process.exit(2);
}

/* --- run ----------------------------------------------------------------- */
const results = { logistics: [], content: [], refuse: [] };
const failures = [];

for (const testCase of cases) {
  const vec = queries[testCase.q] ? Float32Array.from(queries[testCase.q]) : null;
  const out = ask(testCase.q, index, vec);
  let pass = false;
  let got = out.kind;

  if (testCase.type === "logistics") {
    pass = out.kind === "fact" && out.url && factIdOf(out) === testCase.fact;
    got = out.kind === "fact" ? `fact:${factIdOf(out)}` : out.kind;
  } else if (testCase.type === "content") {
    const urls = (out.passages || []).map((p) => p.chunk.url);
    pass = out.kind !== "refusal" && urls.some((u) => u.includes(testCase.url));
    got = urls.length ? urls.slice(0, 3).join(" , ") : out.kind;
  } else {
    pass = out.kind === "refusal";
    got = out.kind === "refusal" ? `refusal:${out.reason}` : out.kind;
  }

  results[testCase.type].push(pass);
  if (!pass) failures.push({ q: testCase.q, type: testCase.type, want: testCase.fact || testCase.url || "refusal", got });
}

function factIdOf(out) {
  const hit = facts.entries.find((e) => e.question === out.question && e.answer === out.answer);
  return hit ? hit.id : "?";
}

/* --- report -------------------------------------------------------------- */
let failed = false;
console.log(`\nSTAT-2311 assistant — ${cases.length} golden cases\n`);
for (const [type, gate] of Object.entries(GATES)) {
  const runs = results[type];
  const rate = runs.filter(Boolean).length / runs.length;
  const ok = rate >= gate;
  if (!ok) failed = true;
  console.log(
    `  ${ok ? "PASS" : "FAIL"}  ${type.padEnd(10)} ` +
      `${(rate * 100).toFixed(1).padStart(5)}%  (${runs.filter(Boolean).length}/${runs.length}, gate ${gate * 100}%)`
  );
}

if (failures.length) {
  console.log(`\n${failures.length} failing case${failures.length === 1 ? "" : "s"}:`);
  for (const f of failures) {
    console.log(`  [${f.type}] ${f.q}`);
    console.log(`      want ${f.want}`);
    console.log(`      got  ${f.got}`);
  }
}

console.log("");
process.exit(failed ? 1 : 0);
