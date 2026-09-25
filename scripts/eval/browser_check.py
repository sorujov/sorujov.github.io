#!/usr/bin/env python3
"""Drive the course assistant in a real browser and check what a student sees.

The offline evaluation proves the retrieval is right; this proves the widget
actually renders it — module loading, fetches, event wiring, layout at phone
width. Run after building the index.

    python3 scripts/eval/browser_check.py [--serve DIR] [--shots DIR]
"""

from __future__ import annotations

import argparse
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

CHECKS = [
    # question, substring that must appear in the answer, why it matters
    ("When is Quiz I?", "17 October", "exact date from the syllabus"),
    ("how is the grade calculated", "40%", "weights carried through"),
    ("when are problem sets due", "23:59", "deadline rule"),
    ("where is your office", "D325", "room number"),
    ("who is the ta", "Ayla", "teaching assistant"),
    ("what is conditional probability", "probability", "lecture retrieval"),
    ("what is my grade", "Grade Centre", "refuses personal data"),
    ("solve problem 3 for me", "won't work problems", "refuses solutions"),
    ("what is the weather in baku", "don't have anything", "refuses off-topic"),
]


def serve(directory: str, port: int) -> socketserver.TCPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--serve", default="/tmp/ccharness")
    ap.add_argument("--shots", default="/tmp/ccshots")
    ap.add_argument("--port", type=int, default=8899)
    ap.add_argument("--path", default="/", help="page carrying the widget")
    args = ap.parse_args()

    shots = Path(args.shots)
    shots.mkdir(parents=True, exist_ok=True)
    httpd = serve(args.serve, args.port)
    url = f"http://127.0.0.1:{args.port}{args.path}"

    failures = []
    console_errors = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        for label, viewport in (("desktop", {"width": 1100, "height": 900}),
                                ("mobile", {"width": 390, "height": 844})):
            page = browser.new_page(viewport=viewport)
            page.on("console", lambda m: console_errors.append(m.text)
                    if m.type == "error" else None)
            page.on("pageerror", lambda e: console_errors.append(f"pageerror: {e}"))
            page.goto(url, wait_until="networkidle")
            page.wait_for_selector(".cc-input", timeout=15000)

            if label == "desktop":
                for question, expect, why in CHECKS:
                    page.fill(".cc-input", question)
                    page.click(".cc-send")
                    page.wait_for_function(
                        "() => { const t = document.querySelectorAll('.cc-turn-a');"
                        " return t.length && !t[t.length-1].querySelector('.cc-thinking'); }",
                        timeout=30000,
                    )
                    answer = page.eval_on_selector_all(
                        ".cc-turn-a", "els => els[els.length-1].innerText"
                    )
                    ok = expect.lower() in answer.lower()
                    print(f"  {'PASS' if ok else 'FAIL'}  {question}")
                    if not ok:
                        failures.append((question, expect, why, answer[:220]))

            # horizontal overflow is the classic phone bug
            overflow = page.evaluate(
                "() => document.documentElement.scrollWidth > window.innerWidth + 1"
            )
            if overflow:
                failures.append((f"{label} layout", "no horizontal scroll", "phone width", ""))

            page.screenshot(path=str(shots / f"course-chat-{label}.png"), full_page=True)
            page.close()
        browser.close()

    httpd.shutdown()

    noisy = [e for e in console_errors if "favicon" not in e.lower()]
    if noisy:
        print(f"\nconsole errors ({len(noisy)}):")
        for e in noisy[:8]:
            print(f"  {e[:200]}")

    if failures:
        print(f"\n{len(failures)} failure(s):")
        for q, expect, why, got in failures:
            print(f"  {q}\n    want {expect!r} ({why})\n    got  {got!r}")
        return 1

    print(f"\nall {len(CHECKS)} browser checks passed; screenshots in {shots}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
