#!/bin/bash
# pubvid.sh N : put the rendered intuition video for lecture N into its deck, re-render, commit, bundle
set -e
N=$1; NN=$(printf %02d $N)
cd /home/claude/l8 && bash prep.sh $N >/dev/null
DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 /mnt/user-data/outputs/vid/lecture${N}_intuition.mp4)
MIN=$(python3 -c "print(max(2,round($DUR/60)))")
DECK=$(ls -d /home/claude/site/lectures/math-stat-1-fall-2026/${NN}-*)
mkdir -p $DECK/video && cp /mnt/user-data/outputs/vid/lecture${N}_intuition.{mp4,srt,vtt} $DECK/video/
python3 /home/claude/add_video_slide.py $NN $MIN
cd $DECK && Q=$(ls *.qmd) && quarto render $Q --to revealjs > /tmp/render_$N.log 2>&1
grep -qi unclosed /tmp/render_$N.log && { echo "UNCLOSED div in $Q"; exit 1; }
H=${Q%.qmd}
for f in ${H}_files/libs/quarto-html/quarto-syntax-highlighting-*.css ${H}_files/libs/revealjs/dist/theme/quarto-*.css; do
  [ -e "$f" ] && ! grep -q "$(basename $f)" $H.html && rm "$f"
done
cd /home/claude/site
MINW=$(python3 -c "print({2:'two',3:'three',4:'four',5:'five'}.get($MIN,'$MIN'))")
git add -A lectures/math-stat-1-fall-2026/${NN}-*
git commit -q -m "Lecture $N: add a $MINW-minute intuition video

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01V2MsDtBXcfBxfLmjphEESd"
echo "lecture $N: $MIN min, committed $(git log --oneline -1 | cut -c1-8)"
