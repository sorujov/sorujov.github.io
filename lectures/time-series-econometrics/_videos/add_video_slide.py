"""add_video_slide.py N MINUTES : insert or refresh the video slide in Time Series deck N.

The video and its captions must already be in NN-slug/video/lectureN_intuition.{mp4,vtt}.
"""
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
n, minutes = int(sys.argv[1]), sys.argv[2]
decks = sorted(glob.glob(f"{ROOT}/[0-9][0-9]-*/*.qmd"))
qmd = [d for d in decks if os.path.basename(os.path.dirname(d)).startswith(f"{n:02d}-")][0]
d = os.path.dirname(qmd)
base = f"lecture{n}_intuition"
assert os.path.exists(f"{d}/video/{base}.mp4"), "video missing"

poster = f' poster="video/{base}.jpg"' if os.path.exists(f"{d}/video/{base}.jpg") else ""
tracks = f'<track kind="captions" src="video/{base}.vtt" srclang="en" label="English">'
prev_line = ""
i = decks.index(qmd)
if i > 0:
    prev = decks[i - 1]
    psub = re.search(r'^subtitle:\s*"([^"]+)"', open(prev, encoding="utf-8").read(), re.M).group(1)
    psub = psub.split(":", 1)[1].strip() if ":" in psub else psub
    prel = f"../{os.path.basename(os.path.dirname(prev))}/{os.path.basename(prev)[:-4]}.html"
    prev_line = f"[⬅ Previous lecture: {n - 1} · {psub}]({prel}){{style=\"font-size:28px\"}}\n\n"

slide = f'''## 🎬 The Idea in {minutes} Minutes

::: {{style="text-align:center"}}
```{{=html}}
<video controls preload="metadata" style="width:780px;max-width:100%;aspect-ratio:16/9;background:#111"{poster} src="video/{base}.mp4">{tracks}</video>
```
{prev_line}[A short film with the intuition. Watch it before the slides, or after. Captions: CC button.]{{style="font-size:28px"}}
:::

---

'''
s = open(qmd, encoding="utf-8").read()
s = re.sub(r"## 🎬 The Idea in .*?\n---\n\n", "", s, flags=re.S)
yaml_end = s.index("\n---\n", 4) + 5
body_start = s.index("\n## ", yaml_end) + 1
s = s[:body_start] + slide + s[body_start:]
open(qmd, "w", encoding="utf-8").write(s)
print("video slide ->", os.path.relpath(qmd, ROOT))
