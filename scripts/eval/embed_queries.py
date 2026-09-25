#!/usr/bin/env python3
"""Embed the golden questions with the same quantised model the browser uses.

Writes scripts/eval/queries.json so the Node harness can run the real retrieval
code against real vectors without loading an ONNX runtime of its own.
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from build_chat_index import embed  # noqa: E402

cases = json.loads((HERE / "golden.json").read_text(encoding="utf-8"))["cases"]
questions = [c["q"] for c in cases]
vectors = embed(questions)

(HERE / "queries.json").write_text(
    json.dumps({q: [round(float(x), 6) for x in v] for q, v in zip(questions, vectors)}),
    encoding="utf-8",
)
print(f"embedded {len(questions)} questions -> scripts/eval/queries.json")
