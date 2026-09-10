#!/usr/bin/env python3
"""Screenshot and exercise every slide of a rendered deck, so it can be looked at.

`verify_deck.py` reads the source and the HTML; it cannot see that a
histogram's y-scale collapsed and every bar is drawn full height, or that a
control's label wrapped to three lines and pushed the plot off the canvas.
Both of those shipped in lecture 1 while every automated check passed.

Two things this script does that a naive screenshotter does not:

1. **It serves the deck over HTTP.** Quarto emits this guard into every deck
   that contains OJS:

       if (window.location.protocol === "file:") { alert("The OJS runtime
       does not work with file:// URLs...") }

   Opened as `file://`, that `alert()` blocks the renderer's main thread
   forever: no CDP call is ever answered, `--print-to-pdf` hangs, and the
   renderer is eventually killed. It also means the OJS cells never run, so
   screenshots taken that way would show dead sliders on exactly the slides
   the QA pass exists to check. A throwaway `http.server` on loopback, rooted
   at the repository, fixes both at once.

2. **It drives the controls.** A static screenshot of a slider proves the
   slider was drawn, not that moving it redraws the chart. The interaction
   pass moves every range and select, clicks through every quiz question, and
   compares the pixels before and after. A control that changes nothing is
   reported as dead.

Requires: playwright (with chromium), pillow.
    python -m pip install playwright pillow && python -m playwright install chromium

Usage:
    python qa_slides.py lecture.html                 # -> lecture_qa/slide-NN.png
    python qa_slides.py lecture.html --out DIR       # write images elsewhere
    python qa_slides.py lecture.html --settle 2      # seconds to wait per slide
    python qa_slides.py lecture.html --only 12,13    # just these slides
    python qa_slides.py lecture.html --no-interact   # screenshots only

Exit status is 1 if any defect was measured, 0 otherwise.

After it finishes, READ THE IMAGES. The measurements below catch a specific
list of defects; they cannot tell you whether a chart means what the slide
says it means.
"""

import functools
import http.server
import os
import socket
import socketserver
import subprocess
import sys
import threading
import urllib.parse

VIEWPORT = (1280, 720)          # replaced by the deck's own width/height
OJS_SETTLE_TIMEOUT = 25000      # ms to wait for OJS cells to produce output


# --------------------------------------------------------------------------
# serving
# --------------------------------------------------------------------------

def repo_root(path):
    """The directory to serve from. A deck's asset paths are written relative
    to the site root, so serve the repository, not the deck's own folder."""
    start = os.path.dirname(os.path.abspath(path))
    try:
        out = subprocess.run(["git", "-C", start, "rev-parse", "--show-toplevel"],
                             capture_output=True, text=True, timeout=15)
        if out.returncode == 0 and out.stdout.strip():
            return os.path.abspath(out.stdout.strip())
    except Exception:
        pass
    return start


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def serve(root):
    """Start a loopback static server on a free port. Returns (port, shutdown)."""
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    handler = functools.partial(_QuietHandler, directory=root)
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return port, httpd.shutdown


# --------------------------------------------------------------------------
# in-page measurements
# --------------------------------------------------------------------------

JS_READY = "typeof Reveal !== 'undefined' && !!Reveal.isReady && Reveal.isReady()"

# An OJS cell that has produced nothing, or produced an error, is the single
# most common way for an explorable to be silently broken.
JS_OJS_STATE = """() => {
  const cells = [...document.querySelectorAll('div[id^="ojs-cell"]')];
  return {
    total: cells.length,
    empty: cells.filter(c => c.childElementCount === 0).map(c => c.id),
    errors: [...document.querySelectorAll('.observablehq--error, .ojs-error')]
              .map(e => (e.textContent || '').trim().slice(0, 200)),
  };
}"""

JS_SLIDE_CHECKS = r"""() => {
  const slide = document.querySelector('.reveal .slides section.present');
  if (!slide) return {notes: ['no .present slide']};
  const notes = [];
  const box = slide.getBoundingClientRect();

  // --- content escaping the canvas -------------------------------------
  // Reveal gives every slide a fixed box; anything outside it is off the
  // projector. Only flag real, visible, sized elements.
  let worstX = 0, worstY = 0, culpritX = null, culpritY = null;
  const name = el => el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className.trim()
      ? '.' + el.className.trim().split(/\s+/).slice(0, 2).join('.') : '');
  for (const el of slide.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none' || st.opacity === '0') continue;
    if (st.position === 'fixed') continue;          // timer, footer, controls
    // A closed <details> -- Quarto's `code-fold` -- keeps layout boxes for its
    // hidden children in Chromium, so the folded code block reports itself as
    // hanging off the slide when nothing is drawn there at all.
    if (el.closest('details:not([open])')) continue;
    const dx = r.right - box.right, dy = r.bottom - box.bottom;
    if (dx > worstX) { worstX = dx; culpritX = name(el); }
    if (dy > worstY) { worstY = dy; culpritY = name(el); }
  }
  if (worstY > 4) notes.push('content runs ' + Math.round(worstY) + 'px below the slide (' + culpritY + ')');
  if (worstX > 4) notes.push('content runs ' + Math.round(worstX) + 'px past the right edge (' + culpritX + ')');

  // --- tiny type --------------------------------------------------------
  // 28px floor, measured on rendered text rather than on the stylesheet.
  // Walk text nodes, not elements: a <p> containing a <strong> is not a leaf,
  // and an element-only walk skipped exactly the callout prose that needed
  // measuring. Rendered math and sub/superscripts are legitimately smaller
  // than their line, so they are excluded rather than reported every time.
  //
  // Two floors, because one number cannot serve both. Prose -- what the class
  // has to read off the wall -- is held to the skill's 28px. Chart axes and
  // control labels are furniture: they must still be legible from the back
  // row, but 28px tick labels would swamp the plot, so they get 18px -- low
  // enough to pass a deliberate 22px code block or slider label, high enough
  // to catch Observable Plot's 10px default and reveal's 15px `pre`.
  const CHROME = 'svg, button, pre, code, .countdown, .score, ' +
                 '.quiz-question .action-buttons, form[class^="oi-"], ' +
                 '[id^="ojs-cell"] form, .cell-output-display form';
  let smallest = 999, smallText = '', smallChrome = 999, chromeText = '';
  const walker = document.createTreeWalker(slide, NodeFilter.SHOW_TEXT);
  for (let node = walker.nextNode(); node; node = walker.nextNode()) {
    const txt = (node.nodeValue || '').trim();
    if (txt.length < 3) continue;
    const el = node.parentElement;
    if (!el || el.closest('mjx-container, .katex, .math, sub, sup')) continue;
    if (el.closest('details:not([open])')) continue;
    const r = el.getBoundingClientRect();
    if (r.width < 2 || r.height < 2) continue;
    const st = getComputedStyle(el);
    if (st.visibility === 'hidden' || st.display === 'none') continue;
    const px = parseFloat(st.fontSize);
    if (!px) continue;
    if (el.closest(CHROME)) {
      if (px < smallChrome) { smallChrome = px; chromeText = txt.slice(0, 40); }
    } else if (px < smallest) {
      smallest = px; smallText = txt.slice(0, 40);
    }
  }
  if (smallest < 28) {
    notes.push('text at ' + smallest.toFixed(0) + 'px (floor is 28px): "' + smallText + '"');
  }
  if (smallChrome < 18) {
    notes.push('chart/control text at ' + smallChrome.toFixed(0) +
               'px (floor is 18px): "' + chromeText + '"');
  }

  // --- Observable Plot charts ------------------------------------------
  // This is the lecture-1 defect made measurable: a y-axis that collapsed to
  // a single tick, and bars all drawn the same (full) height.
  const charts = [];
  for (const svg of slide.querySelectorAll('svg')) {
    const yTicks = [...svg.querySelectorAll('g[aria-label="y-axis tick label"] text')]
                     .map(t => t.textContent.trim());
    const xTicks = [...svg.querySelectorAll('g[aria-label="x-axis tick label"] text')]
                     .map(t => t.textContent.trim());
    const rects = [...svg.querySelectorAll('g[aria-label="rect"] rect, g[aria-label="bar"] rect')]
                    .map(r => Math.round(parseFloat(r.getAttribute('height') || '0')));
    if (!yTicks.length && !rects.length) continue;           // not a Plot chart
    charts.push({yTicks: yTicks.length, xTicks: xTicks.length, bars: rects.length,
                 distinctBarHeights: new Set(rects).size, yLabels: yTicks.slice(0, 8)});
    if (yTicks.length === 1) {
      notes.push('chart y-axis has a single tick (' + JSON.stringify(yTicks) + ') -- collapsed scale');
    }
    if (yTicks.length > 1 && new Set(yTicks).size === 1) {
      notes.push('chart y-axis ticks all read "' + yTicks[0] + '" -- collapsed scale');
    }
    if (rects.length >= 5 && new Set(rects).size === 1) {
      notes.push('all ' + rects.length + ' bars are exactly ' + rects[0] + 'px tall -- collapsed scale');
    }
  }

  // --- interactive furniture -------------------------------------------
  const controls = [...slide.querySelectorAll('input[type=range], select')].map((el, i) => ({
    i: i, kind: el.tagName === 'SELECT' ? 'select' : 'range',
    label: (el.closest('label') ? el.closest('label').textContent : '').trim().slice(0, 40),
  }));

  return {notes: notes, charts: charts, controls: controls,
          quiz: slide.querySelectorAll('.option-button').length};
}"""

# Move every control on the current slide as far as it will go from where it
# sits now, so a chart that depends on it has to redraw.
JS_DRIVE_CONTROLS = """() => {
  const slide = document.querySelector('.reveal .slides section.present');
  if (!slide) return [];
  const moved = [];
  for (const el of slide.querySelectorAll('input[type=range]')) {
    const min = parseFloat(el.min || '0'), max = parseFloat(el.max || '100');
    const now = parseFloat(el.value);
    const target = (now - min) > (max - now) ? min : max;
    el.value = String(target);
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
    moved.push('range ' + now + ' -> ' + target);
  }
  for (const el of slide.querySelectorAll('select')) {
    if (el.options.length < 2) continue;
    const from = el.selectedIndex;
    el.selectedIndex = (from + 1) % el.options.length;
    el.dispatchEvent(new Event('input', {bubbles: true}));
    el.dispatchEvent(new Event('change', {bubbles: true}));
    moved.push('select ' + from + ' -> ' + el.selectedIndex);
  }
  return moved;
}"""

# Answer the quiz: pick the first option, then press Check.
JS_DRIVE_QUIZ = """() => {
  const slide = document.querySelector('.reveal .slides section.present');
  if (!slide) return {clicked: 0};
  const opts = [...slide.querySelectorAll('.option-button')];
  if (!opts.length) return {clicked: 0};
  opts[0].click();
  const check = slide.querySelector('.check-button');
  if (check) check.click();
  return {clicked: opts.length,
          selected: slide.querySelectorAll('.option-button.selected').length,
          marked: slide.querySelectorAll('.option-button.correct, .option-button.incorrect').length,
          feedback: [...slide.querySelectorAll('.feedback')]
                      .map(f => (f.textContent || '').trim()).filter(Boolean).length};
}"""


# --------------------------------------------------------------------------
# pixels
# --------------------------------------------------------------------------

def ink_fraction(path):
    from PIL import Image
    im = Image.open(path).convert("L")
    im.thumbnail((160, 90))
    px = im.tobytes()
    return sum(1 for v in px if v < 235) / max(1, len(px))


def pixel_delta(a, b):
    """Fraction of pixels that differ appreciably between two screenshots."""
    from PIL import Image, ImageChops
    ia = Image.open(a).convert("L")
    ib = Image.open(b).convert("L")
    if ia.size != ib.size:
        return 1.0
    ia.thumbnail((320, 180))
    ib.thumbnail((320, 180))
    px = ImageChops.difference(ia, ib).tobytes()
    return sum(1 for v in px if v > 12) / max(1, len(px))


# --------------------------------------------------------------------------
# the run
# --------------------------------------------------------------------------

def run(html, outdir, settle, only, interact):
    from playwright.sync_api import sync_playwright

    root = repo_root(html)
    rel = os.path.relpath(os.path.abspath(html), root).replace("\\", "/")
    if rel.startswith(".."):
        root = os.path.dirname(os.path.abspath(html))
        rel = os.path.basename(html)
    port, shutdown = serve(root)
    url = "http://127.0.0.1:%d/%s" % (port, urllib.parse.quote(rel))
    print("Serving %s" % root)
    print("Opening %s\n" % url)

    os.makedirs(outdir, exist_ok=True)
    findings = []       # (slide number or None, message)
    page_errors, dialogs = [], []

    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--force-device-scale-factor=1"])
        page = browser.new_page(viewport={"width": VIEWPORT[0], "height": VIEWPORT[1]})

        page.on("pageerror", lambda e: page_errors.append(str(e)[:300]))
        page.on("console", lambda m: page_errors.append("console error: " + m.text[:300])
                if m.type == "error" else None)
        # A deck must never pop a dialog. Record it and dismiss, so one cannot
        # wedge the run the way the file:// guard used to.
        page.on("dialog", lambda d: (dialogs.append(d.message[:200]), d.dismiss()))

        # Run straight after `quarto render` and the browser can arrive while
        # the `_files/` directory is still being rewritten, so reveal.js never
        # initialises. One reload clears it; a second failure is real.
        page.goto(url, wait_until="load", timeout=60000)
        for attempt in (1, 2):
            try:
                page.wait_for_function(JS_READY, timeout=45000)
                break
            except Exception:
                if attempt == 2:
                    browser.close()
                    shutdown()
                    sys.exit("reveal.js never became ready after a reload. Is this a "
                             "revealjs deck, and did `quarto render` finish cleanly?")
                print("reveal.js not ready -- reloading once")
                page.reload(wait_until="load", timeout=60000)

        # Match the viewport to the deck's declared canvas.
        cfg = page.evaluate("() => ({w: Reveal.getConfig().width, h: Reveal.getConfig().height})")
        if isinstance(cfg.get("w"), (int, float)) and (cfg["w"], cfg["h"]) != VIEWPORT:
            page.set_viewport_size({"width": int(cfg["w"]), "height": int(cfg["h"])})
            page.wait_for_timeout(500)
            print("Canvas: %dx%d (from the deck)" % (cfg["w"], cfg["h"]))

        # Show every fragment, so nothing is hidden behind a keypress.
        page.evaluate("() => Reveal.configure({fragments: false})")

        # Give OJS time to actually produce output before judging any of it.
        try:
            page.wait_for_function(
                """() => {
                  const c = [...document.querySelectorAll('div[id^="ojs-cell"]')];
                  return c.length === 0 || c.every(x => x.childElementCount > 0);
                }""", timeout=OJS_SETTLE_TIMEOUT)
        except Exception:
            pass
        ojs = page.evaluate(JS_OJS_STATE)
        print("OJS:    %d cell(s), %d empty, %d error(s)"
              % (ojs["total"], len(ojs["empty"]), len(ojs["errors"])))
        for cid in ojs["empty"]:
            findings.append((None, "OJS cell %s produced no output" % cid))
        for err in ojs["errors"]:
            findings.append((None, "OJS error: %s" % err))

        total = page.evaluate("() => Reveal.getSlides().length")
        print("Slides: %d\n" % total)

        wanted = [n for n in (only or range(1, total + 1)) if 1 <= n <= total]
        shots = []
        for n in wanted:
            page.evaluate(
                """(i) => { const s = Reveal.getSlides()[i];
                            const ix = Reveal.getIndices(s);
                            Reveal.slide(ix.h, ix.v || 0); }""", n - 1)
            page.wait_for_timeout(int(settle * 1000))

            shot = os.path.join(outdir, "slide-%02d.png" % n)
            page.screenshot(path=shot)
            shots.append((n, shot))

            checks = page.evaluate(JS_SLIDE_CHECKS)
            for note in checks.get("notes", []):
                findings.append((n, note))

            ink = ink_fraction(shot)
            if ink < 0.004:
                findings.append((n, "looks blank (%.1f%% ink) -- did a cell fail to render?"
                                 % (ink * 100)))
            elif ink > 0.55:
                findings.append((n, "very dense (%.0f%% ink) -- flooded chart or overfull slide?"
                                 % (ink * 100)))

            if not interact:
                continue

            # --- interaction pass -------------------------------------------
            if checks.get("controls"):
                moved = page.evaluate(JS_DRIVE_CONTROLS)
                page.wait_for_timeout(max(800, int(settle * 1000)))
                after = os.path.join(outdir, "slide-%02d-controls.png" % n)
                page.screenshot(path=after)
                delta = pixel_delta(shot, after)
                kinds = ", ".join(c["kind"] for c in checks["controls"])
                if delta < 0.002:
                    findings.append((n, "controls (%s) changed nothing on screen (%.2f%% of "
                                        "pixels moved) -- explorable is dead"
                                     % (kinds, delta * 100)))
                else:
                    print("  slide %-3d controls responded (%s; %.1f%% of pixels moved)"
                          % (n, "; ".join(moved), delta * 100))

            if checks.get("quiz"):
                q = page.evaluate(JS_DRIVE_QUIZ)
                page.wait_for_timeout(700)
                after = os.path.join(outdir, "slide-%02d-quiz.png" % n)
                page.screenshot(path=after)
                delta = pixel_delta(shot, after)
                if not q.get("selected") and not q.get("marked"):
                    findings.append((n, "quiz options do not respond to a click -- is the "
                                        "quiz plugin loaded?"))
                elif not q.get("feedback") and not q.get("marked"):
                    findings.append((n, "quiz accepted a click but showed no feedback"))
                else:
                    print("  slide %-3d quiz responded (%d option(s), %d marked, %.1f%% of "
                          "pixels moved)" % (n, q["clicked"], q.get("marked", 0), delta * 100))

        browser.close()
    shutdown()

    for d in dialogs:
        findings.append((None, "the deck opened a JavaScript dialog: %s" % d))
    seen = set()
    for e in page_errors:
        if e not in seen:
            seen.add(e)
            findings.append((None, e))
    return shots, findings


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    html = sys.argv[1]
    if not os.path.exists(html):
        sys.exit("No such file: %s" % html)
    args = sys.argv[2:]

    def opt(name, default, cast=str):
        return cast(args[args.index(name) + 1]) if name in args else default

    outdir = opt("--out", os.path.splitext(html)[0] + "_qa")
    settle = opt("--settle", 1.2, float)
    only_raw = opt("--only", "")
    only = [int(x) for x in only_raw.split(",") if x.strip()] if only_raw else None
    interact = "--no-interact" not in args

    shots, findings = run(html, outdir, settle, only, interact)

    print("\n%d slide image(s) written to %s" % (len(shots), outdir))
    if findings:
        print("\n%d finding(s):" % len(findings))
        for n, msg in findings:
            print("  %-9s %s" % ("slide %d" % n if n else "deck", msg))
    else:
        print("\nNothing measurable is wrong.")

    print("\nNow READ the images -- every one. Measurement catches collapsed axes,")
    print("dead controls, overflow and tiny type. It cannot tell you whether a")
    print("chart shows the shape the slide claims it shows.")
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
