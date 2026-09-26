"""add_slide.py <lecture_dir> <video_basename> <minutes>  - idempotent: adds an intuition-video slide to the deck (qmd + rendered html)."""
import sys,glob,os,re
d,base,mins=sys.argv[1],sys.argv[2],sys.argv[3]
title=f"🎬 The Idea in {mins} Minutes"
vid=(f'<video controls preload="metadata" style="width:880px;max-width:100%" src="video/{base}.mp4">'
     f'<track kind="captions" src="video/{base}.vtt" srclang="en" label="English">'
     f'</video>')
note='Watch this short intuition video before (or after) the slides. Captions: CC button.'
qmd=[f for f in glob.glob(os.path.join(d,'*.qmd'))][0]
html=qmd[:-4]+'.html'
s=open(qmd,encoding='utf-8').read()
if 'video/'+base+'.mp4' not in s:
    block=f"## {title}\n\n::: {{style=\"text-align:center\"}}\n{vid}\n\n[{note}]{{style=\"font-size:22px\"}}\n:::\n\n---\n\n"
    i=s.index('\n## ',s.index('\n---',3)+4)+1   # before the first slide after the YAML header
    s=s[:i]+block+s[i:]; open(qmd,'w',encoding='utf-8').write(s); print('qmd: slide added')
else: print('qmd: already has slide')
h=open(html,encoding='utf-8').read()
if 'video/'+base+'.mp4' not in h:
    sec=(f'<section id="intuition-video" class="slide level2">\n<h2>{title}</h2>\n'
         f'<div style="text-align:center">\n{vid}\n<p style="font-size:22px">{note}</p>\n</div>\n</section>\n')
    m=re.search(r'<section id="(?!title-slide)[^"]*" class="slide level2',h)
    h=h[:m.start()]+sec+h[m.start():]; open(html,'w',encoding='utf-8').write(h); print('html: slide added before',m.group(0)[:60])
else: print('html: already has slide')
