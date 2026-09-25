#!/usr/bin/env python3
"""Benchmark candidate in-browser models on grounded answering.

Run on one GPU. For each model and each prompt it applies the chat template the
production widget will use, generates greedily, and scores three things that can
be decided mechanically:

    figure     the exact date or percentage in the context is reproduced, and no
               other date or percentage appears anywhere in the answer
    refuse     the model declines when the context does not contain the answer
    faithful   every number in the answer appears in the context

Nothing here is judged by a model, so the numbers are reproducible.

    python3 run_bench.py --out results.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Candidates present in WebLLM's prebuilt list and ungated on the Hub.
# gemma-3-1b-it and Llama-3.2-1B-Instruct are gated and need an HF token; pass
# --models to include them once the licences are accepted on the account.
DEFAULT_MODELS = [
    "HuggingFaceTB/SmolLM2-360M-Instruct",
    "Qwen/Qwen2.5-0.5B-Instruct",
    "Qwen/Qwen3-0.6B",
    "Qwen/Qwen2.5-1.5B-Instruct",
    "HuggingFaceTB/SmolLM2-1.7B-Instruct",
]

# Keep in step with SYSTEM and the user message in assets/js/course-chat.js:
# the benchmark is only worth running on the prompt visitors actually get.
SYSTEM = (
    "You help students of STAT-2311 Mathematical Statistics I at ADA University. "
    "Use only the notes in the user's message; they are from the syllabus and the lecture slides. "
    "Copy dates, percentages and room numbers exactly; never change a number. "
    "If the notes answer the question, answer it directly in at most three sentences. "
    "If the notes contain a worked example with numbers, walk through that example step by step "
    "using its numbers, in at most five sentences. "
    "Never invent a new problem, new numbers or facts that are not in the notes. "
    "If the notes do not answer the question, reply only: I can't find that in the course notes. "
    "Write mathematics as \\( ... \\), never with dollar signs."
)

USER = "Notes:\n{context}\n\nQuestion: {question}"

DATE = re.compile(
    r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|"
    r"October|November|December)\b",
    re.I,
)
PCT = re.compile(r"\b\d{1,3}%")
NUM = re.compile(r"\b\d+(?:\.\d+)?\b")
REFUSED = re.compile(
    r"(don'?t have that|not in the (course|context|material)|cannot find|can'?t find|"
    r"does not (contain|say|mention)|doesn'?t (contain|say|mention)|no information|"
    r"not (?:stated|specified|provided|given|mentioned|available))",
    re.I,
)


def score(item: dict, answer: str) -> tuple[int, str]:
    kind = item["kind"]
    if kind == "figure":
        gold = item["gold"]
        pattern = DATE if item["forbid"] == "date" else PCT
        found = {m.group(0).lower() for m in pattern.finditer(answer)}
        if gold.lower() not in found:
            return 0, f"missing {gold}"
        extra = found - {gold.lower()}
        if extra:
            return 0, f"invented {sorted(extra)}"
        return 1, ""
    if kind == "refuse":
        return (1, "") if REFUSED.search(answer) else (0, "answered anyway")
    context_numbers = set(NUM.findall(item["context"]))
    answer_numbers = set(NUM.findall(answer))
    stray = answer_numbers - context_numbers
    return (0, f"numbers not in context: {sorted(stray)}") if stray else (1, "")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="*", default=DEFAULT_MODELS)
    ap.add_argument("--prompts", default=str(HERE / "prompts.json"))
    ap.add_argument("--out", default=str(HERE / "results.csv"))
    ap.add_argument("--max-new", type=int, default=120)
    args = ap.parse_args()

    # One unit = one model, so a pilot measures a real model end to end and the
    # chunks write distinct files. Defaults keep the script runnable anywhere.
    models = list(args.models)
    start = int(os.environ.get("UNIT_START", 0))
    end = int(os.environ.get("UNIT_END", len(models)))
    models = models[start:end]
    chunk = os.environ.get("CHUNK_ID", "0")
    results_dir = Path(os.environ.get("RESULTS_DIR", "results"))
    results_dir.mkdir(parents=True, exist_ok=True)
    if os.environ.get("UNIT_END"):
        args.out = str(results_dir / f"chunk_{chunk}.csv")

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        print(f"MISSING DEPENDENCY: {exc}", file=sys.stderr)
        print("transformers and torch are required on the compute node.", file=sys.stderr)
        return 3

    items = json.loads(Path(args.prompts).read_text())["items"]
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"device={device} gpu={torch.cuda.get_device_name(0) if device == 'cuda' else 'n/a'}")
    print(f"{len(items)} prompts x {len(models)} models (units {start}..{end})", flush=True)

    rows = []
    for name in models:
        print(f"\n=== {name}", flush=True)
        started = time.time()
        try:
            tok = AutoTokenizer.from_pretrained(name)
            model = AutoModelForCausalLM.from_pretrained(
                name,
                dtype=torch.float16 if device == "cuda" else torch.float32,
                device_map=device,
            )
            model.eval()
        except Exception as exc:  # noqa: BLE001 - report and continue to next model
            print(f"  load failed: {exc}", flush=True)
            rows.append({"model": name, "id": "-", "kind": "load-error",
                         "score": 0, "note": str(exc)[:200], "answer": ""})
            continue
        print(f"  loaded in {time.time() - started:.0f}s", flush=True)

        for n, item in enumerate(items, 1):
            messages = [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": USER.format(**item)},
            ]
            try:
                text = tok.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True,
                    **({"enable_thinking": False} if "Qwen3" in name else {}),
                )
            except Exception:
                text = f"{SYSTEM}\n\n{USER.format(**item)}\n\nAnswer:"
            inputs = tok(text, return_tensors="pt").to(device)
            with torch.no_grad():
                generated = model.generate(
                    **inputs,
                    max_new_tokens=args.max_new,
                    do_sample=False,
                    pad_token_id=tok.pad_token_id or tok.eos_token_id,
                )
            answer = tok.decode(
                generated[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
            ).strip()
            answer = re.sub(r"<think>.*?</think>", " ", answer, flags=re.S).strip()
            value, note = score(item, answer)
            rows.append({"model": name, "id": item["id"], "kind": item["kind"],
                         "score": value, "note": note, "answer": answer.replace("\n", " ")[:400]})
            if n % 20 == 0:
                print(f"  {n}/{len(items)}", flush=True)

        del model
        if device == "cuda":
            torch.cuda.empty_cache()

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["model", "id", "kind", "score", "note", "answer"])
        writer.writeheader()
        writer.writerows(rows)

    print("\n=== summary ===")
    kinds = ["figure", "refuse", "faithful"]
    print(f"{'model':42} " + " ".join(k.rjust(9) for k in kinds) + "   overall")
    for name in models:
        mine = [r for r in rows if r["model"] == name and r["kind"] in kinds]
        if not mine:
            print(f"{name:42}  (no results)")
            continue
        cells = []
        for kind in kinds:
            sub = [r["score"] for r in mine if r["kind"] == kind]
            cells.append(f"{100 * sum(sub) / len(sub):8.1f}%" if sub else "       -")
        overall = 100 * sum(r["score"] for r in mine) / len(mine)
        print(f"{name:42} " + " ".join(cells) + f"   {overall:6.1f}%")
    print(f"\nwrote {args.out}")
    print(f"UNITS_DONE={len(models)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
