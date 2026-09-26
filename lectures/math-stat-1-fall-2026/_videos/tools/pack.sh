# pack.sh N : generate missing mp3 for tts_lN and tar them
cd $HOME/mnt/.secrets/voice/tts_l$1 && python3 $HOME/gen.py && tar -cf ../tts_l$1.tar *.mp3 && ls -la ../tts_l$1.tar
