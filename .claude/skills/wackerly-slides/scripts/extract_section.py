#!/usr/bin/env python3
"""Extract a numbered section range from the Wackerly PDF.

The course plan cites the book by section ("Wackerly, 7th ed., SS1.1-1.3"),
not by PDF page, so this resolves sections to pages via the PDF's embedded
bookmarks. A hardcoded page table goes stale the moment a different printing
is dropped in; the bookmarks travel with the file.

Usage:
    python extract_section.py <pdf> 1.1-1.3        # a range of sections
    python extract_section.py <pdf> 2.6            # a single section
    python extract_section.py <pdf> --toc 3        # list what chapter 3 has
    python extract_section.py <pdf> 1.1-1.3 --images out/   # + figures
    python extract_section.py <pdf> 1.1-1.3 --out ch1.txt    # to a file

Text is written as UTF-8. On Windows the console defaults to cp1252 and
chokes on the ligatures and Greek the book is full of, so --out (or a
redirect) is the reliable path for anything you intend to read back.
"""

import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("PyMuPDF missing. Install with: python -m pip install pymupdf")

# Bookmark titles look like "3.11: Tchebysheff's Theorem".
ENTRY = re.compile(r"^(\d{1,2})\.(\d{1,2}):\s*(.+)$")


def section_map(doc):
    """Ordered list of (key, page_index, title) for every numbered section."""
    out = []
    for _level, title, page in doc.get_toc():
        m = ENTRY.match(title.strip())
        if m:
            out.append((f"{m.group(1)}.{m.group(2)}", page - 1, m.group(3).strip()))
    if not out:
        sys.exit(
            "This PDF has no section bookmarks, so sections cannot be resolved.\n"
            "Fall back to page numbers with a plain page-range extractor."
        )
    return out


def sort_key(key):
    chap, sec = key.split(".")
    return (int(chap), int(sec))


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    # The book is full of ligatures, Greek and typographic dashes; the
    # Windows console is cp1252 and raises on all of them.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    pdf, spec = sys.argv[1], sys.argv[2]
    if "--out" in sys.argv:
        target = sys.argv[sys.argv.index("--out") + 1]
        sys.stdout = open(target, "w", encoding="utf-8")
    doc = fitz.open(pdf)
    sections = section_map(doc)

    if spec == "--toc":
        want_chap = sys.argv[3] if len(sys.argv) > 3 else None
        for key, page, title in sections:
            if want_chap is None or key.split(".")[0] == want_chap:
                print(f"{key:>6}  PDF p.{page + 1:<4} {title}")
        return

    first, last = (spec.split("-", 1) if "-" in spec else (spec, spec))
    first, last = first.strip(), last.strip()

    index = {key: (page, title) for key, page, title in sections}
    for want in (first, last):
        if want not in index:
            sys.exit(
                f"Section {want} is not in this book's bookmarks.\n"
                f"Run:  python {sys.argv[0]} \"{pdf}\" --toc {want.split('.')[0]}"
            )

    start_page = index[first][0]
    # Stop at the section that follows `last`, so `last` is included whole
    # rather than truncated at its own heading.
    later = [p for k, p, _t in sections if sort_key(k) > sort_key(last)]
    end_page = (min(later) - 1) if later else doc.page_count - 1

    covered = [f"{k} {t}" for k, _p, t in sections
               if sort_key(first) <= sort_key(k) <= sort_key(last)]

    print(f"### Wackerly SS{first}-{last}  (PDF pages {start_page + 1}-{end_page + 1})")
    print("### Sections covered:")
    for line in covered:
        print(f"###   {line}")
    print()

    for pageno in range(start_page, min(end_page + 1, doc.page_count)):
        print(f"\n{'=' * 60}\nPAGE {pageno + 1}\n{'=' * 60}")
        print(doc[pageno].get_text())

    if "--images" in sys.argv:
        import os
        outdir = sys.argv[sys.argv.index("--images") + 1]
        os.makedirs(outdir, exist_ok=True)
        n = 0
        for pageno in range(start_page, min(end_page + 1, doc.page_count)):
            for i, img in enumerate(doc[pageno].get_images()):
                pix = fitz.Pixmap(doc, img[0])
                if pix.n - pix.alpha >= 4:      # CMYK needs converting first
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                path = os.path.join(outdir, f"p{pageno + 1}_{i}.png")
                pix.save(path)
                n += 1
        print(f"\n### Wrote {n} figure(s) to {outdir}", file=sys.stderr)

    doc.close()


if __name__ == "__main__":
    main()
