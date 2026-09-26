# prep.sh N -> copies HQ video + srt + vtt to outputs/vid
N=$1; D=/home/claude/l8/media/videos/lecture$N/1080p60
cp $D/Lecture$N.mp4 /mnt/user-data/outputs/vid/lecture${N}_intuition.mp4
cp $D/Lecture$N.srt /mnt/user-data/outputs/vid/lecture${N}_intuition.srt
ffmpeg -v error -y -i $D/Lecture$N.srt /mnt/user-data/outputs/vid/lecture${N}_intuition.vtt
ls -la /mnt/user-data/outputs/vid/lecture${N}_*
