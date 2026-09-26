# render.sh N [quality]  -> renders LectureN with the precomputed voice, makes a contact sheet
set -e
N=$1; Q=${2:-h}
cd /home/claude/l8
mkdir -p /home/claude/tts/l$N && tar -xf /mnt/user-data/uploads/.secrets/voice/tts_l$N.tar -C /home/claude/tts/l$N
. /home/claude/mv/bin/activate
rm -rf media/videos/lecture$N
VOICE=precomputed TTS_DIR=/home/claude/tts/l$N manim -q$Q --disable_caching lecture$N.py Lecture$N > log_l$N.txt 2>&1 || { grep -v "it/s" log_l$N.txt | tail -30; exit 1; }
V=$(ls media/videos/lecture$N/*/Lecture$N.mp4)
echo "missing voice clips: $(grep -c '\[voice\] missing' log_l$N.txt || true)"
ffprobe -v error -show_entries format=duration -of csv=p=0 $V
mkdir -p sheets && rm -f sheets/l$N-*.png
ffmpeg -v error -i $V -vf "fps=1/8,scale=384:216,tile=5x6" sheets/l$N-%02d.png
ls sheets/l$N-*
