"""add_video_slide.py NN MINUTES : insert/refresh the 🎬 video slide in deck NN (container clone)."""
import glob, os, re, sys

ROOT = "/home/claude/site/lectures/math-stat-1-fall-2026"
nn, minutes = sys.argv[1].zfill(2), sys.argv[2]
decks = sorted(glob.glob(f"{ROOT}/[0-9][0-9]-*/*.qmd"))
qmd = [d for d in decks if os.path.basename(os.path.dirname(d)).startswith(nn + "-")][0]
i = decks.index(qmd)
n = int(nn)
d = os.path.dirname(qmd)
base = f"lecture{n}_intuition"
assert os.path.exists(f"{d}/video/{base}.mp4"), "video missing"

tracks = f'<track kind="captions" src="video/{base}.vtt" srclang="en" label="English">'
langs = "English"
if os.path.exists(f"{d}/video/{base}.az.vtt"):
    tracks += f'<track kind="captions" src="video/{base}.az.vtt" srclang="az" label="Azərbaycanca">'
    langs = "English / Azərbaycanca"

prev = decks[i - 1]
psub = re.search(r'^subtitle:\s*"([^"]+)"', open(prev, encoding="utf-8").read(), re.M).group(1)
psub = re.split(r"[:;]", psub)[0].strip()
prel = f"../{os.path.basename(os.path.dirname(prev))}/{os.path.basename(prev)[:-4]}.html"
pn = int(os.path.basename(os.path.dirname(prev))[:2])

slide = f'''## 🎬 The Idea in {minutes} Minutes

::: {{style="text-align:center"}}
```{{=html}}
<video controls preload="metadata" style="width:880px;max-width:100%" src="video/{base}.mp4">{tracks}</video>
```
[⬅ Previous lecture: {pn} · {psub}]({prel}){{style="font-size:28px"}}

[Watch this short intuition video before (or after) the slides. Captions ({langs}): CC button.]{{style="font-size:28px"}}
:::

---

'''
s = open(qmd, encoding="utf-8").read()
s = re.sub(r"## 🎬 The Idea in .*?\n---\n\n", "", s, flags=re.S)  # replace an existing one
body_start = s.index("\n## ", s.index("\n---\n", 4)) + 1  # first slide heading after the YAML
s = s[:body_start] + slide + s[body_start:]
open(qmd, "w", encoding="utf-8").write(s)
print("video slide ->", qmd)
