#!/usr/bin/env python3
"""
optimize_slides.py

Automatically adjusts font sizes in Quarto RevealJS lecture slides
to eliminate text overflow while maximizing readability.

Strategy:
  1. Render QMD -> HTML (once, full execution)
  2. Open HTML in headless Chromium via Playwright
  3. For each slide: reveal all fragments, then iteratively reduce
     inline px font-sizes until no overflow, or min_font is reached
  4. Apply discovered optimal reductions back to QMD source
  5. Report a summary

Usage:
    python optimize_slides.py lecture.qmd
    python optimize_slides.py lecture.qmd --min-font 16 --step 1
    python optimize_slides.py lecture.qmd --dry-run
    python optimize_slides.py lecture.qmd --no-render   # reuse existing HTML

Requirements:
    pip install playwright
    playwright install chromium
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


# ─────────────────────────────────────────────────────────────────────────────
# Step 1: Render QMD → HTML
# ─────────────────────────────────────────────────────────────────────────────

def render_qmd(qmd_path: Path) -> Path:
    print(f"[render] {qmd_path.name} ...", flush=True)
    r = subprocess.run(
        ["quarto", "render", str(qmd_path)],
        capture_output=True, text=True, cwd=qmd_path.parent,
    )
    if r.returncode != 0:
        print("ERROR – quarto render failed:\n" + r.stderr)
        sys.exit(1)
    out = qmd_path.with_suffix(".html")
    if not out.exists():
        print(f"ERROR – expected HTML not found: {out}")
        sys.exit(1)
    print(f"[render] -> {out.name}")
    return out


# ─────────────────────────────────────────────────────────────────────────────
# JavaScript helpers injected into the browser
# ─────────────────────────────────────────────────────────────────────────────

_REVEAL_ALL_FRAGMENTS_JS = """
() => {
    // Advance all fragments on the current slide so we check full content.
    // Reveal.nextFragment() returns true if it advanced, false if no more.
    let i = 0;
    while (Reveal.nextFragment() && i < 50) { i++; }
}
"""

_OVERFLOW_JS = """
() => {
    const slide = document.querySelector(
        '.reveal .slides section.present:not(.stack)'
    );
    if (!slide) return false;
    const TOLERANCE = 8;  // px, accounts for rounding
    const sBot   = slide.getBoundingClientRect().bottom;
    const sRight = slide.getBoundingClientRect().right;
    for (const el of slide.querySelectorAll('*')) {
        const cs = window.getComputedStyle(el);
        if (cs.display === 'none' || cs.visibility === 'hidden') continue;
        if (cs.overflow === 'auto'  || cs.overflow === 'scroll')  continue;
        if (cs.overflowY === 'auto' || cs.overflowY === 'scroll') continue;
        const r = el.getBoundingClientRect();
        if (r.bottom > sBot + TOLERANCE || r.right > sRight + TOLERANCE)
            return true;
    }
    return false;
}
"""


def _reduce_fonts_js(step: int, min_font: int) -> str:
    """JS that reduces all inline px font-sizes on the current slide by `step`."""
    return (
        "() => {"
        "  const slide = document.querySelector('.reveal .slides section.present:not(.stack)');"
        "  if (!slide) return false;"
        "  let changed = false;"
        "  slide.querySelectorAll('[style]').forEach(el => {"
        "    if (!el.style.fontSize) return;"
        r"    const m = el.style.fontSize.match(/^(\d+)px$/);"
        "    if (m) {"
        f"      const cur = parseInt(m[1]); const nxt = Math.max(cur - {step}, {min_font});"
        "      if (nxt !== cur) { el.style.fontSize = nxt + 'px'; changed = true; }"
        "    }"
        "  });"
        "  return changed;"
        "}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 + 3: Browser-side detection and iterative reduction
# ─────────────────────────────────────────────────────────────────────────────

def optimize_in_browser(
    html_path: Path,
    step: int = 1,
    min_font: int = 16,
    max_iter: int = 40,
) -> dict:
    """
    Opens the RevealJS HTML in headless Chromium.
    For each slide that overflows, iteratively reduces inline px font-sizes.

    Returns:
        dict  { slide_idx: {
                    'overflowed': bool,
                    'reductions': int,    # total px reduced per element
                    'at_min':     bool,   # True if min_font was reached
                } }
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("playwright not installed.\n"
              "  pip install playwright && playwright install chromium")
        sys.exit(1)

    results = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(html_path.as_uri())
        page.wait_for_load_state("networkidle")
        page.wait_for_function("window.Reveal !== undefined")
        page.wait_for_function("Reveal.isReady()")

        total = page.evaluate("Reveal.getTotalSlides()")
        print(f"[browser] {total} slides detected")

        reduce_js = _reduce_fonts_js(step, min_font)

        _IS_QUIZ_JS = (
            "() => !!document.querySelector("
            "'.reveal .slides section.present:not(.stack).quiz-question')"
        )

        for idx in range(total):
            # Navigate to slide (h=idx, v=0, f=0)
            page.evaluate(f"Reveal.slide({idx}, 0, 0)")
            page.wait_for_timeout(500)  # allow MathJax to settle

            # Skip quiz slides entirely: the quiz plugin adds score-tracker and
            # other DOM elements that trigger false overflow positives regardless
            # of font size.  These slides are manually sized.
            is_quiz = page.evaluate(_IS_QUIZ_JS)
            if is_quiz:
                results[idx] = {"overflowed": False, "reductions": 0, "at_min": False}
                print(f"  slide {idx:3d}  QUIZ (skipped)")
                continue

            # Reveal all fragments so we check full content
            page.evaluate(_REVEAL_ALL_FRAGMENTS_JS)
            page.wait_for_timeout(150)

            if not page.evaluate(_OVERFLOW_JS):
                results[idx] = {"overflowed": False, "reductions": 0, "at_min": False}
                print(f"  slide {idx:3d}  OK")
                continue

            reductions = 0
            at_min = False

            for _ in range(max_iter):
                changed = page.evaluate(reduce_js)
                if changed:
                    reductions += step
                page.wait_for_timeout(80)
                if not page.evaluate(_OVERFLOW_JS):
                    break
                if not changed:
                    at_min = True
                    break

            results[idx] = {
                "overflowed": True,
                "reductions": reductions,
                "at_min": at_min,
            }

            if at_min:
                print(f"  slide {idx:3d}  OVERFLOW – hit min font ({min_font}px), manual fix needed")
            else:
                print(f"  slide {idx:3d}  OVERFLOW fixed  (-{reductions}px)")

        browser.close()

    return results


# ─────────────────────────────────────────────────────────────────────────────
# Step 4: Patch the QMD source
# ─────────────────────────────────────────────────────────────────────────────

def split_qmd(content: str) -> list:
    """
    Split QMD on '\\n---\\n'.
      sections[0]   = YAML front matter (opening --- included, closing --- is the joiner)
      sections[i+1] = RevealJS slide i  (0-based)
    """
    return content.split("\n---\n")


def join_qmd(sections: list) -> str:
    return "\n---\n".join(sections)


def reduce_fontsizes_in_section(section: str, reduction_px: int, min_font: int) -> str:
    """Lower every 'font-size: Xpx' value in a QMD section string by reduction_px."""
    def _replace(m):
        cur = int(m.group(1))
        new = max(cur - reduction_px, min_font)
        # preserve original whitespace style (e.g. 'font-size:34px' vs 'font-size: 34px')
        return m.group(0).replace(str(cur) + "px", str(new) + "px", 1)

    return re.sub(r"font-size:\s*(\d+)px", _replace, section)


def patch_qmd(qmd_path: Path, results: dict, min_font: int, dry_run: bool) -> None:
    content = qmd_path.read_text(encoding="utf-8")
    sections = split_qmd(content)

    patched_any = False
    for slide_idx, info in sorted(results.items()):
        if not info["overflowed"] or info["reductions"] == 0:
            continue

        # RevealJS slide 0 = title (from YAML = sections[0])
        # RevealJS slide 1 = first ## = sections[1], etc.
        # So: section_idx == slide_idx exactly.
        section_idx = slide_idx
        if section_idx >= len(sections):
            print(f"  WARNING: slide {slide_idx} has no matching QMD section")
            continue

        original = sections[section_idx]
        patched  = reduce_fontsizes_in_section(original, info["reductions"], min_font)

        if patched != original:
            sections[section_idx] = patched
            patched_any = True
            print(f"  [patch] slide {slide_idx}: reduced all font-sizes by {info['reductions']}px")
        else:
            print(f"  [patch] slide {slide_idx}: no font-size: Xpx found – manual fix needed")

    if not patched_any:
        print("[patch] Nothing to patch.")
        return

    if dry_run:
        print("[patch] --dry-run active: QMD NOT modified.")
        return

    backup = qmd_path.with_suffix(".qmd.bak")
    if not backup.exists():
        shutil.copy2(qmd_path, backup)
        print(f"[patch] Backup -> {backup.name}")

    qmd_path.write_text(join_qmd(sections), encoding="utf-8")
    print(f"[patch] Saved   -> {qmd_path.name}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Optimize Quarto RevealJS slide font sizes to eliminate overflow."
    )
    ap.add_argument("qmd_file",    help="Path to the .qmd lecture file")
    ap.add_argument("--min-font",  type=int, default=16,
                    help="Minimum font size in px (default: 16)")
    ap.add_argument("--step",      type=int, default=1,
                    help="Reduction step in px per iteration (default: 1)")
    ap.add_argument("--max-iter",  type=int, default=40,
                    help="Max reduction iterations per slide (default: 40)")
    ap.add_argument("--dry-run",   action="store_true",
                    help="Detect and report only; do not modify the QMD")
    ap.add_argument("--no-render", action="store_true",
                    help="Skip quarto render; use existing .html output")
    args = ap.parse_args()

    qmd_path = Path(args.qmd_file).resolve()
    if not qmd_path.exists():
        print(f"ERROR: file not found: {qmd_path}")
        sys.exit(1)

    # Step 1: Render
    if args.no_render:
        html_path = qmd_path.with_suffix(".html")
        if not html_path.exists():
            print(f"ERROR: --no-render specified but {html_path} does not exist")
            sys.exit(1)
        print(f"[render] Skipped – using {html_path.name}")
    else:
        html_path = render_qmd(qmd_path)

    # Steps 2 + 3: Browser optimization
    print("\n[browser] Checking slides for overflow...")
    results = optimize_in_browser(html_path, args.step, args.min_font, args.max_iter)

    overflowed = [i for i, r in results.items() if r["overflowed"]]
    at_min     = [i for i, r in results.items() if r.get("at_min")]

    print(f"\n[summary] {len(overflowed)} slide(s) overflowed: {overflowed or 'none'}")
    if at_min:
        print(f"[summary] {len(at_min)} slide(s) hit min font ({args.min_font}px) – manual fix needed: {at_min}")

    # Step 4: Patch QMD
    if overflowed:
        print("\n[patch] Applying font-size reductions to QMD source...")
        patch_qmd(qmd_path, results, args.min_font, args.dry_run)
        if not args.dry_run:
            print("\n[done] Re-render the QMD to verify: quarto render " + qmd_path.name)
    else:
        print("\n[done] No overflows detected. No changes made.")


if __name__ == "__main__":
    main()
