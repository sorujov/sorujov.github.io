# pack_az.sh N...: generate missing Azerbaijani clips (about 120 s per call) and tar complete lectures
T0=$(date +%s)
for N in "$@"; do
  [ $(( $(date +%s) - T0 )) -gt 120 ] && break
  cd $HOME/mnt/.secrets/voice/tts_az_l$N || continue
  r=$(python3 $HOME/gen_az.py | tail -1); echo "L$N $r"
  a=${r%% /*}; b=${r##*/ }; [ "$a" = "$b" ] && tar -cf ../tts_az_l$N.tar *.mp3
done
