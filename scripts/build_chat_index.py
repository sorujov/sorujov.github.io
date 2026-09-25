#!/usr/bin/env python3
"""Build the search index for the STAT-2311 course assistant.

Reads the course pages and lecture sources in this repository and emits, into
assets/chat/:

    facts.json       deterministic answers extracted from the course page
    chunks.json      retrievable passages with their source anchors
    lexical.json     BM25 inverted index over those passages
    embeddings.bin   int8-quantised MiniLM vectors, one row per passage
    meta.json        build metadata and index dimensions

Nothing here is written by hand: every date, weight and room comes out of
_teaching/2026-fall-mathematical-statistics-I.md, so the syllabus stays the
single source of truth. Re-run after editing a course page or a lecture.

    python3 scripts/build_chat_index.py

The embedding model is the same quantised ONNX file the browser downloads
(Xenova/all-MiniLM-L6-v2, q8), so build-time and query-time vectors come from
identical weights and no drift is possible.
"""

from __future__ import annotations

import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from bs4 import BeautifulSoup

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "chat"
COURSE = REPO / "_teaching" / "2026-fall-mathematical-statistics-I.md"
LECTURES = REPO / "lectures" / "math-stat-1-fall-2026"
COURSE_URL = "/teaching/2026-fall-mathematical-statistics-I"

MODEL_REPO = "Xenova/all-MiniLM-L6-v2"
MODEL_FILE = "onnx/model_quantized.onnx"
MAX_TOKENS = 256
TARGET_WORDS = 110
MIN_WORDS = 25

# --------------------------------------------------------------------------
# front matter and HTML helpers
# --------------------------------------------------------------------------


def split_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        return {}, text
    end = text.index("\n---", 3)
    raw, body = text[3:end], text[end + 4 :]
    meta: dict[str, str] = {}
    for line in raw.splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip().strip('"')
    return meta, body


def clean(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace(" ", " ").replace("→", "->")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def table_rows(table) -> tuple[list[str], list[list[str]]]:
    head = [clean(th.get_text()) for th in table.select("thead th")]
    body = []
    for tr in table.select("tbody tr"):
        cells = [clean(td.get_text()) for td in tr.find_all("td")]
        if cells:
            body.append(cells)
    return head, body


# --------------------------------------------------------------------------
# facts: deterministic answers, extracted not authored
# --------------------------------------------------------------------------


def extract_facts(soup: BeautifulSoup, meta: dict) -> dict:
    facts: list[dict] = []

    def add(fid, keys, question, answer, anchor):
        facts.append(
            {
                "id": fid,
                "keys": [k.lower() for k in keys],
                "question": question,
                "answer": answer,
                "url": f"{COURSE_URL}#{anchor}",
            }
        )

    # --- course information grid -----------------------------------------
    info = {}
    for item in soup.select(".info-item"):
        label = item.select_one(".info-label")
        value = item.select_one(".info-value")
        if label and value:
            info[clean(label.get_text())] = clean(value.get_text())

    label_intents = {
        "Office hours": (["office hours", "when can i see you", "consultation"],
                         "When are your office hours?"),
        "Office": (["office", "which room is your office", "where is your office"],
                   "Where is your office?"),
        "Contact": (["email", "e-mail", "contact", "how do i reach you"],
                    "How do I contact the instructor?"),
        "Teaching assistant": (["ta", "teaching assistant", "who is the ta"],
                               "Who is the teaching assistant?"),
        "TA contact": (["ta email", "ta contact", "teaching assistant email"],
                       "What is the TA's e-mail?"),
        "Credits": (["credits", "ects", "how many credits"], "How many credits is the course?"),
        "Course code": (["course code", "code"], "What is the course code?"),
        "Instructor": (["instructor", "who teaches", "lecturer", "professor"],
                       "Who teaches the course?"),
        "Prerequisite": (["prerequisite", "prereq", "what do i need before"],
                         "What is the prerequisite?"),
    }
    for label, (keys, question) in label_intents.items():
        if label in info:
            add(f"info-{label.lower().replace(' ', '-')}", keys, question,
                f"{label}: {info[label]}.", "course-info")

    prereq = soup.select_one(".prereq-box")
    if prereq:
        add("prerequisite", ["prerequisite", "prereq"], "What is the prerequisite?",
            clean(prereq.get_text()), "course-info")

    # --- sections, times and rooms ---------------------------------------
    section_rows: list[list[str]] = []
    for table in soup.select(".schedule-table table"):
        head, body = table_rows(table)
        if head[:1] == ["Section"]:
            section_rows = body
            break

    if section_rows:
        lines = [f"Section {r[0]}: Wednesday {r[1]}, Saturday {r[2]}." for r in section_rows]
        add("sections", ["section", "sections", "what time", "when is class", "class time",
                         "which room", "room", "where is class", "timetable", "schedule of classes"],
            "When and where does each section meet?", " ".join(lines), "sections")
        for row in section_rows:
            add(f"section-{row[0]}", [row[0], f"section {row[0]}"],
                f"When does section {row[0]} meet?",
                f"Section {row[0]} meets Wednesday {row[1]} and Saturday {row[2]}.",
                "sections")

    # --- assessment -------------------------------------------------------
    assessments = []
    for item in soup.select(".assessment-item"):
        name = clean(item.find("h4").get_text()) if item.find("h4") else ""
        pct = item.select_one(".assessment-percentage")
        rng = item.select_one(".grade-range")
        assessments.append(
            {
                "name": name,
                "weight": clean(pct.get_text()) if pct else "",
                "detail": clean(rng.get_text()) if rng else "",
            }
        )

    alias = {
        "Quiz I": ["quiz i", "quiz 1", "first quiz", "quiz one"],
        "Quiz II": ["quiz ii", "quiz 2", "second quiz", "quiz two"],
        "Midterm Examination I": ["midterm i", "midterm 1", "midterm one", "first midterm",
                                  "midterm exam i", "midterm examination i"],
        "Midterm Examination II": ["midterm ii", "midterm 2", "midterm two", "second midterm",
                                   "midterm exam ii", "final", "final exam", "last exam"],
        "Problem sets": ["problem set", "problem sets", "homework", "hw", "webwork sets"],
    }
    for a in assessments:
        keys = alias.get(a["name"], [a["name"].lower()])
        detail = f" {a['detail']}." if a["detail"] else ""
        answer = f"{a['name']} is worth {a['weight']} of the grade.{detail}"
        add(f"assess-{a['name'].lower().replace(' ', '-')}", keys,
            f"When is {a['name']} and what is it worth?", answer, "assessment")

    if assessments:
        grid = "; ".join(f"{a['name']} {a['weight']}" for a in assessments)
        add("weights", ["grade", "grading", "weights", "how is the grade calculated",
                        "grade breakdown", "how am i graded", "percentage", "marks"],
            "How is the final grade calculated?",
            f"The grade is made up of: {grid}.", "assessment")
        dated = [f"{a['name']} on {a['detail'].split(' · ')[0]}" for a in assessments
                 if "·" in a["detail"] or re.search(r"\d", a["detail"])]
        if dated:
            add("all-dates", ["dates", "exam dates", "important dates", "when are the exams",
                              "calendar", "deadlines"],
                "What are the assessment dates?",
                "; ".join(dated) + ".", "assessment")

    synonyms = {
        "no-final": ["do we have a final", "is there a final exam", "final or not"],
        "prerequisite": ["calculus", "math1202", "do i need", "what do i need to take first"],
        "info-prerequisite": ["calculus", "math1202", "do i need"],
        "sections": ["when do classes meet", "when do we meet", "class schedule",
                     "meeting times", "lecture time", "what days"],
        "ps-rule": ["how many attempts", "attempts", "when does the homework close",
                    "when do sets close", "when does homework close", "unlimited attempts",
                    "how long do i have"],
        "tech-academic-integrity": ["cheat", "copying", "copy someone"],
        "weights": ["what is worth what", "how much is each"],
    }

    bonus = soup.select_one(".bonus-callout")
    if bonus:
        add("bonus", ["bonus", "tutorial bonus", "extra credit", "extra points"],
            "Is there a bonus for tutorials?", clean(bonus.get_text()), "assessment")
        add("no-final", ["is there a final", "final examination", "no final"],
            "Is there a final examination?",
            "There is no final examination. Midterm Examination II on the last day of "
            "classes closes the assessment.", "assessment")

    # --- problem set deadlines -------------------------------------------
    ps_rows: list[list[str]] = []
    for table in soup.select(".schedule-table table"):
        head, body = table_rows(table)
        if "ps1 covers" in [h.lower() for h in head]:
            ps_rows = body
            break

    if ps_rows:
        # The rule itself is prose on the page and Sam edits it; read it, never restate it.
        heading = soup.find(id="problem-sets")
        rule = heading.find_next("p") if heading else None
        if rule is not None:
            add("ps-rule", ["when are problem sets due", "problem set deadline",
                            "homework deadline", "when is homework due", "due date",
                            "when do sets close"],
                "When are the problem sets due?", clean(rule.get_text()), "problem-sets")
        for row in ps_rows:
            add(f"ps-week-{row[0]}", [f"week {row[0]}"],
                f"What do the week {row[0]} problem sets cover?",
                f"Week {row[0]} ({row[1]}): ps1 covers {row[2]}, ps2 covers {row[3]}. "
                f"Both close {row[4]}.", "problem-sets")

    # --- course plan ------------------------------------------------------
    plan_rows: list[list[str]] = []
    plan_links: list[list[str]] = []
    for table in soup.select(".schedule-table table"):
        head, _ = table_rows(table)
        if head[:2] == ["Date", "Topic"]:
            for tr in table.select("tbody tr"):
                cells = tr.find_all("td")
                if len(cells) >= 3:
                    plan_rows.append([clean(c.get_text()) for c in cells[:3]])
                    plan_links.append([a.get("href", "") for a in cells[-1].find_all("a")])
            break

    for row, links in zip(plan_rows, plan_links):
        date, topic, reading = row[0], row[1], row[2]
        slides = next((l for l in links if l.endswith(".html")), "")
        answer = f"{date}: {topic} Reading: {reading}"
        keys = [date.lower()]
        for m in re.finditer(r"§+\s*([\d.]+)(?:\s*[–-]\s*([\d.]+))?", reading):
            keys.append(f"§{m.group(1)}")
            keys.append(m.group(1))
            if m.group(2):
                keys.append(m.group(2))
        entry = {
            "id": f"plan-{date.lower().replace(' ', '-')}",
            "keys": [k.lower() for k in keys],
            "question": f"What is covered on {date}?",
            "answer": answer,
            "url": slides or f"{COURSE_URL}#schedule",
        }
        facts.append(entry)

    # --- practical matters ------------------------------------------------
    tech_keys = {
        "Blackboard Learn": ["blackboard", "where are the slides", "announcements"],
        "WeBWorK": ["webwork", "where do i do homework", "platform"],
        "Tutorials": ["tutorial", "tutorials", "when are tutorials"],
        "Contact": ["how fast do you reply", "reply", "response time"],
        "Attendance and grading": ["attendance", "absence", "missing class"],
        "Academic integrity": ["integrity", "cheating", "plagiarism", "honor code"],
    }
    for item in soup.select(".tech-item"):
        h4 = item.find("h4")
        if not h4:
            continue
        title = clean(h4.get_text())
        body = clean(" ".join(p.get_text() for p in item.find_all("p")))
        keys = tech_keys.get(title, [title.lower()])
        add(f"tech-{title.lower().replace(' ', '-')}", keys + [title.lower()],
            f"{title}?", body, "policies")

    # --- reading ----------------------------------------------------------
    for book in soup.select(".book-item"):
        h4 = book.find("h4")
        if not h4:
            continue
        kind = clean(h4.get_text())
        body = clean(" ".join(p.get_text() for p in book.find_all("p")))
        keys = ["textbook", "book", "which book", "reading", "wackerly"] if kind == "Required" \
            else ["recommended reading", "other books", "extra reading"]
        add(f"book-{kind.lower()}", keys, f"What is the {kind.lower()} reading?",
            body, "literature")

    for entry in facts:
        extra = synonyms.get(entry["id"])
        if extra:
            entry["keys"] = sorted(set(entry["keys"]) | {k.lower() for k in extra})

    return {
        "course": {
            "title": meta.get("title", "Mathematical Statistics I"),
            "term": meta.get("term", ""),
            "url": COURSE_URL,
            "instructor": info.get("Instructor", ""),
            "email": info.get("Contact", ""),
        },
        "entries": facts,
    }


# --------------------------------------------------------------------------
# chunks: retrievable passages
# --------------------------------------------------------------------------


def paragraphs_from_course(soup: BeautifulSoup) -> list[dict]:
    """Walk the course page, carrying the nearest heading anchor with each block."""
    out: list[dict] = []
    anchor, heading = "course-info", "Course information"

    for el in soup.find_all(["h2", "h3", "p", "table", "div"], recursive=True):
        if el.name in ("h2", "h3"):
            candidate = el.get("id") or (el.parent.get("id") if el.parent else None)
            if candidate:
                anchor = candidate
            heading = clean(el.get_text())
            continue
        if el.name == "div":
            if el.get("id"):
                anchor = el["id"]
            continue
        if el.name == "table":
            head, body = table_rows(el)
            if not body:
                continue
            lines = []
            for row in body:
                pairs = [f"{h}: {c}" for h, c in zip(head, row) if c and c != "—"]
                lines.append("; ".join(pairs) if pairs else " ".join(row))
            out.append({"heading": heading, "anchor": anchor, "text": " | ".join(lines)})
            continue
        text = clean(el.get_text())
        if len(text.split()) >= MIN_WORDS:
            out.append({"heading": heading, "anchor": anchor, "text": text})
    return out


CARD_SELECTORS = [
    (".objective-card", "Learning outcomes", True),
    (".assessment-item", "Assessment", True),
    (".tech-item", "Practical matters", False),
    (".book-item", "Reading", False),
    (".bonus-callout", "Assessment", False),
    (".prereq-box", "Course information", False),
    (".info-item", "Course information", True),
]


def card_passages(soup: BeautifulSoup) -> list[dict]:
    """Structured cards carry the syllabus facts; the paragraph walker skips them."""
    out: list[dict] = []
    for selector, heading, merge in CARD_SELECTORS:
        items = soup.select(selector)
        if not items:
            continue
        anchor = "course-info"
        for parent in items[0].parents:
            if parent.get("id"):
                anchor = parent["id"]
                break
        texts = [clean(el.get_text(" ")) for el in items]
        texts = [t for t in texts if t]
        if merge:
            joined = f"{heading}. " + " ".join(texts)
            out.append({"heading": heading, "anchor": anchor, "text": joined})
        else:
            for text in texts:
                if len(text.split()) >= 8:
                    out.append({"heading": heading, "anchor": anchor, "text": text})
    return out


EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2190-\u21FF\u2300-\u27BF\u2B00-\u2BFF\uFE0F\u200d]"
)
QUIZ_HEADING = re.compile(r"quiz\s*#|\bpoll\b", re.I)


MATH = re.compile(r"\$\$.+?\$\$|\$[^$\n]+?\$", re.S)


def strip_markup(text: str) -> str:
    """Clean Quarto markup but keep TeX intact — the site loads MathJax, so the
    widget can typeset it. Stripping $ and backslashes turns a formula into
    rubble ("P(B j mid A) = frac { sum ..."), which is worse than no formula."""
    math: list[str] = []

    def stash(match: re.Match) -> str:
        math.append(match.group(0))
        return f" \x00{len(math) - 1}\x00 "

    text = re.sub(r"```\{[^}]*\}.*?```", " ", text, flags=re.S)   # executable blocks
    text = re.sub(r"```.*?```", " ", text, flags=re.S)             # plain blocks
    text = re.sub(r"^:::.*$", " ", text, flags=re.M)               # fenced divs
    text = MATH.sub(stash, text)                                   # protect the maths
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)            # images
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)         # links
    text = re.sub(r"\[([^\]]*)\]\{[^}]*\}", r"\1", text)         # spans: keep the words
    text = re.sub(r"\{[^{}]*\}", " ", text)                       # leftover attributes
    text = EMOJI.sub(" ", text)
    text = re.sub(r"[#*_>`$\\|]+", " ", text)
    text = re.sub(r"-{3,}", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    def restore(match: re.Match) -> str:
        # MathJax 3's default config does not treat $...$ as inline maths, and
        # the site loads it without a custom config. Emit the delimiters it does
        # recognise rather than reconfiguring MathJax for every page.
        raw = math[int(match.group(1))]
        if raw.startswith("$$"):
            return r"\[" + raw[2:-2].strip() + r"\]"
        return r"\(" + raw[1:-1].strip() + r"\)"

    return re.sub(r"\x00(\d+)\x00", restore, text)


def qmd_passages(path: Path) -> list[dict]:
    """Slide-level passages from a Quarto lecture source.

    Slides marked {.quiz-question} are skipped entirely: their bullets carry the
    correct answer in a [ ]{.correct} span, and an assistant that quotes those
    back hands students the in-class poll answers.
    """
    raw = path.read_text(encoding="utf-8", errors="ignore")
    _, body = split_front_matter(raw)

    sections: list[tuple[str, str, list[str]]] = []
    title, attrs, buf = "", "", []
    for line in body.splitlines():
        match = re.match(r"^(#{1,3})\s+(.*)$", line)
        if match:
            sections.append((title, attrs, buf))
            head = match.group(2)
            found = re.search(r"\{([^}]*)\}\s*$", head)
            attrs = found.group(1) if found else ""
            title = EMOJI.sub("", re.sub(r"\{[^}]*\}\s*$", "", head)).strip()
            buf = []
        else:
            buf.append(line)
    sections.append((title, attrs, buf))

    passages = []
    for title, attrs, buf in sections:
        if "quiz-question" in attrs.lower() or QUIZ_HEADING.search(title or ""):
            continue
        text = strip_markup("\n".join(buf))
        if len(text.split()) >= MIN_WORDS:
            passages.append({"heading": title or path.stem, "text": text})
    return passages


def split_long(text: str) -> list[str]:
    words = text.split()
    if len(words) <= TARGET_WORDS * 1.6:
        return [text]
    parts, current = [], []
    for sentence in re.split(r"(?<=[.!?]) ", text):
        current.append(sentence)
        if len(" ".join(current).split()) >= TARGET_WORDS:
            parts.append(" ".join(current))
            current = []
    if current:
        tail = " ".join(current)
        if len(tail.split()) < MIN_WORDS and parts:
            parts[-1] += " " + tail
        else:
            parts.append(tail)
    return parts


def build_chunks() -> list[dict]:
    chunks: list[dict] = []
    meta, body = split_front_matter(COURSE.read_text(encoding="utf-8"))
    soup = BeautifulSoup(body, "lxml")

    for block in paragraphs_from_course(soup) + card_passages(soup):
        for piece in split_long(block["text"]):
            chunks.append(
                {
                    "text": piece,
                    "title": "Mathematical Statistics I — course page",
                    "heading": block["heading"],
                    "url": f"{COURSE_URL}#{block['anchor']}",
                    "source": "course",
                }
            )

    for qmd in sorted(LECTURES.rglob("*.qmd")):
        folder = qmd.parent.name
        url = f"/lectures/math-stat-1-fall-2026/{folder}/{qmd.stem}.html"
        lecture_title = folder.split("-", 1)[-1].replace("-", " ").title()
        for passage in qmd_passages(qmd):
            for piece in split_long(passage["text"]):
                chunks.append(
                    {
                        "text": piece,
                        "title": f"Lecture: {lecture_title}",
                        "heading": passage["heading"],
                        "url": url,
                        "source": "lecture",
                    }
                )

    seen, unique = set(), []
    for c in chunks:
        key = c["text"][:160].lower()
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique, meta, soup


# --------------------------------------------------------------------------
# lexical index
# --------------------------------------------------------------------------

STOP = set("""a an the and or but if of in on at to for with from by is are was were be been being
this that these those it its as not no do does did so such than then there here we you your our their
what when where which who whom how why can could should would will shall may might must about into over
under again further once each few more most other some only own same too very s t just don now i me my""".split())


def tokenize(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"[^a-z0-9§.\- ]+", " ", text)
    tokens = []
    for raw in text.split():
        raw = raw.strip(".-")
        if not raw or raw in STOP or len(raw) < 2:
            continue
        tokens.append(raw)
        if raw.endswith("s") and len(raw) > 3:
            tokens.append(raw[:-1])
    return tokens


def build_lexical(chunks: list[dict]) -> dict:
    postings: dict[str, list[list[int]]] = defaultdict(list)
    lengths = []
    for idx, chunk in enumerate(chunks):
        terms = tokenize(f"{chunk['heading']} {chunk['text']}")
        lengths.append(len(terms))
        for term, tf in Counter(terms).items():
            postings[term].append([idx, tf])
    probe = [
        "When is Quiz I? §3.4-3.6",
        "professor's office-hours, rooms and classes",
        "Tchebysheff's theorem 1.3 bounds",
    ]
    return {
        "postings": {t: p for t, p in postings.items() if len(p) < len(chunks) * 0.9},
        "lengths": lengths,
        "avgdl": sum(lengths) / max(len(lengths), 1),
        "n": len(chunks),
        # shipped so the browser tokenizer cannot drift from the build-time one
        "stop": sorted(STOP),
        "probe": [{"text": t, "tokens": tokenize(t)} for t in probe],
    }


# --------------------------------------------------------------------------
# embeddings — the same quantised ONNX the browser runs
# --------------------------------------------------------------------------


def embed(texts: list[str]) -> np.ndarray:
    from huggingface_hub import hf_hub_download
    from tokenizers import Tokenizer
    import onnxruntime as ort

    tok = Tokenizer.from_file(hf_hub_download(MODEL_REPO, "tokenizer.json"))
    tok.enable_truncation(max_length=MAX_TOKENS)
    tok.enable_padding(length=None)
    session = ort.InferenceSession(
        hf_hub_download(MODEL_REPO, MODEL_FILE), providers=["CPUExecutionProvider"]
    )
    names = {i.name for i in session.get_inputs()}

    vectors = []
    for start in range(0, len(texts), 32):
        batch = tok.encode_batch(texts[start : start + 32])
        ids = np.array([e.ids for e in batch], dtype=np.int64)
        mask = np.array([e.attention_mask for e in batch], dtype=np.int64)
        feed = {"input_ids": ids, "attention_mask": mask}
        if "token_type_ids" in names:
            feed["token_type_ids"] = np.zeros_like(ids)
        hidden = session.run(None, feed)[0]
        m = mask[..., None].astype(np.float32)
        pooled = (hidden * m).sum(axis=1) / np.clip(m.sum(axis=1), 1e-9, None)
        pooled /= np.clip(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9, None)
        vectors.append(pooled.astype(np.float32))
    return np.vstack(vectors)


# --------------------------------------------------------------------------


def main() -> int:
    if not COURSE.exists():
        print(f"course page not found: {COURSE}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    chunks, meta, soup = build_chunks()
    facts = extract_facts(soup, meta)
    lexical = build_lexical(chunks)

    print(f"{len(chunks)} chunks, {len(facts['entries'])} facts, "
          f"{len(lexical['postings'])} terms")

    vectors = embed([f"{c['heading']}. {c['text']}" for c in chunks])
    quantised = np.clip(np.round(vectors * 127.0), -127, 127).astype(np.int8)

    (OUT / "embeddings.bin").write_bytes(quantised.tobytes())
    (OUT / "chunks.json").write_text(
        json.dumps([{k: c[k] for k in ("text", "title", "heading", "url", "source")}
                    for c in chunks], ensure_ascii=False), encoding="utf-8")
    (OUT / "facts.json").write_text(json.dumps(facts, ensure_ascii=False), encoding="utf-8")
    (OUT / "lexical.json").write_text(json.dumps(lexical, ensure_ascii=False), encoding="utf-8")
    (OUT / "meta.json").write_text(json.dumps({
        "built": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "chunks": len(chunks),
        "dims": int(vectors.shape[1]),
        "scale": 127.0,
        "model": MODEL_REPO,
        "facts": len(facts["entries"]),
    }, indent=2), encoding="utf-8")

    total = sum((OUT / f).stat().st_size for f in
                ("embeddings.bin", "chunks.json", "facts.json", "lexical.json", "meta.json"))
    print(f"wrote assets/chat/ — {total / 1024:.0f} KB total")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
