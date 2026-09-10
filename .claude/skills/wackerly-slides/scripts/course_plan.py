#!/usr/bin/env python3
"""Read the Math Stat I course plan and resolve a session to its Wackerly sections.

The course plan on the teaching page is the single source of truth for what
each session covers. Copying it into the skill would let the two drift, and
the copy would be the one that is wrong, so this parses the page itself.

Usage:
    python course_plan.py                        # list every session
    python course_plan.py "16 September"         # one session, by date
    python course_plan.py --sections "16 September"   # just "2.1-2.5"
    python course_plan.py --todo                 # sessions with no slides yet

Default page: _teaching/2026-fall-mathematical-statistics-I.md
Override with --page <path>.
"""

import html
import os
import re
import sys

DEFAULT_PAGE = os.path.join("_teaching", "2026-fall-mathematical-statistics-I.md")

# Exam and quiz rows carry <tr class="schedule-highlight">, so the attribute
# has to be optional or those sessions vanish from the plan silently.
ROW = re.compile(r"<tr[^>]*>\s*(.*?)\s*</tr>", re.DOTALL)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.DOTALL)

# Sentences about homework cite sections that are not what the lecture covers.
NOT_LECTURE = re.compile(r"exercise|problem set|tutorial|supplementary|for the quiz",
                         re.IGNORECASE)
ASSESSMENT = re.compile(r"\b(midterm|examination|quiz)\b", re.IGNORECASE)


def clean(fragment):
    """Strip tags and decode entities, keeping the text a human would read."""
    text = re.sub(r"<[^>]+>", "", fragment)
    text = html.unescape(text)
    # The page uses en dashes in section ranges and &mdash; for "nothing yet".
    return " ".join(text.split()).strip()


def parse_sections(reading):
    """Pull "1.1-1.3" out of a reading cell like "Wackerly ... 7th ed., SS1.1-1.3"."""
    # Normalise the typographic dash the page uses inside ranges.
    text = reading.replace("–", "-").replace("—", "-")
    # A reading cell mixes the lecture's own sections with homework and prep
    # ("Wackerly SS3.7-3.8. Supplementary exercises, Chapters 1-3 (SS3.1-3.8)").
    # Keeping only the sentences that are not about homework leaves the
    # sections the lecture actually covers.
    keep = [s for s in re.split(r"\.\s+(?=[A-Z])", text) if not NOT_LECTURE.search(s)]
    nums = []
    for sentence in keep:
        nums += re.findall(r"§{1,2}\s*(\d{1,2}\.\d{1,2}(?:\s*-\s*\d{1,2}\.\d{1,2})?)", sentence)
    return [n.replace(" ", "") for n in nums]


def load(page):
    if not os.path.exists(page):
        sys.exit("Course plan not found: %s" % page)
    with open(page, encoding="utf-8") as fh:
        text = fh.read()

    # The page has several tables; the course plan is the one after <h2 id="schedule">.
    start = text.find('id="schedule"')
    if start == -1:
        sys.exit('No <h2 id="schedule"> section in %s' % page)
    end = text.find('id="literature"', start)
    block = text[start: end if end != -1 else len(text)]

    sessions = []
    for row in ROW.findall(block):
        cells = [clean(c) for c in CELL.findall(row)]
        if len(cells) < 3:
            continue                      # header row, or a malformed one
        date, topic, reading = cells[0], cells[1], cells[2]
        materials = cells[3] if len(cells) > 3 else ""
        if not re.match(r"^\d{1,2}\s+\w+", date):
            continue                      # not a session row
        link = re.search(r'href="([^"]+)"', row)
        sessions.append({
            "date": date,
            "topic": topic,
            "reading": reading,
            "sections": parse_sections(reading),
            "has_slides": bool(link),
            "slides": link.group(1) if link else None,
            "materials": materials,
            # A quiz or exam day is not a normal lecture: some have no teaching
            # at all, others only a half session. Worth saying so before slides
            # get built for a sitting.
            "assessment": bool(ASSESSMENT.search(topic)),
        })
    return sessions


def show(s, verbose=True):
    mark = "[slides]" if s["has_slides"] else "[  --  ]"
    flag = "  (assessment day)" if s["assessment"] else ""
    print("%s %-14s %s%s"
          % (mark, s["date"], ", ".join("§" + x for x in s["sections"]) or "-", flag))
    if verbose:
        print("    topic:   %s" % s["topic"])
        print("    reading: %s" % s["reading"])
        if s["slides"]:
            print("    slides:  %s" % s["slides"])
        print()


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = sys.argv[1:]

    page = DEFAULT_PAGE
    if "--page" in args:
        i = args.index("--page")
        page = args[i + 1]
        del args[i:i + 2]

    sections_only = "--sections" in args
    if sections_only:
        args.remove("--sections")
    todo = "--todo" in args
    if todo:
        args.remove("--todo")

    sessions = load(page)

    if todo:
        for s in sessions:
            if not s["has_slides"]:
                show(s, verbose=False)
        return

    if not args:
        for s in sessions:
            show(s, verbose=False)
        print("\n%d session(s). Pass a date for detail, --todo for the ones "
              "without slides." % len(sessions))
        return

    want = " ".join(args).strip().lower()
    hits = [s for s in sessions if want in s["date"].lower()]
    if not hits:
        hits = [s for s in sessions if want in s["topic"].lower()]
    if not hits:
        sys.exit('No session matches "%s". Run with no arguments to list them all.' % want)

    for s in hits:
        if sections_only:
            print(" ".join(s["sections"]))
        else:
            show(s)


if __name__ == "__main__":
    main()
