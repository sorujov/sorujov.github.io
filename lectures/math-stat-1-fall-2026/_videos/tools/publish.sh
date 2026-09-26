# publish.sh <lecture_dir_name> <video_basename> <minutes> "<commit message>"
set -e
cd $HOME/site
git pull -q --rebase origin master
L=$HOME/site/lectures/math-stat-1-fall-2026/$1
mkdir -p $L/video
cp $HOME/mnt/.secrets/voice/out/$2.mp4 $HOME/mnt/.secrets/voice/out/$2.srt $HOME/mnt/.secrets/voice/out/$2.vtt $L/video/
chmod 644 $L/video/*
python3 $HOME/add_slide.py $L $2 $3
git add lectures/math-stat-1-fall-2026/$1
git -c user.name="sorujov" -c user.email="salahaddini.ayyubi@gmail.com" commit -q -m "$4" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01V2MsDtBXcfBxfLmjphEESd"
git push -q origin master || { git pull -q --rebase origin master && git push -q origin master; }
git log --oneline -1
git status --short | head -3
