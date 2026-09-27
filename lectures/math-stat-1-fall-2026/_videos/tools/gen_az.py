# gen_az.py: Azerbaijani narration clips (runs on ooklapc inside tts_az_lN/).
# Reads texts_az.json {md5(english clip): azerbaijani text}; writes md5(az text).mp3.
# Voice: ELEVENLABS_VOICE_ID_AZ (the Azerbaijani clone). Keys are read from the universal .env and never printed.
import json, os, time, urllib.request, hashlib
env = {l.split('=', 1)[0]: l.split('=', 1)[1].strip()
       for l in open(os.path.expanduser('~/mnt/.secrets/.env'), encoding='utf-8') if '=' in l and not l.startswith('#')}
K = env['ELEVENLABS_API_KEY']; V = env.get('ELEVENLABS_VOICE_ID_AZ', env['ELEVENLABS_VOICE_ID'])
MODEL = os.environ.get('AZ_MODEL', 'eleven_v3')
d = json.load(open('texts_az.json', encoding='utf-8')); t0 = time.time(); done = 0
for _, txt in d.items():
    h = hashlib.md5(txt.encode()).hexdigest()
    if os.path.exists(h + '.mp3'): done += 1; continue
    if time.time() - t0 > 140: break
    body = {"text": txt, "model_id": MODEL, "voice_settings": {"stability": 0.5, "similarity_boost": 0.9}}
    if MODEL == 'eleven_v3': body["language_code"] = "az"
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{V}?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(), headers={"xi-api-key": K, "Content-Type": "application/json"})
    open(h + '.mp3', 'wb').write(urllib.request.urlopen(req, timeout=120).read()); done += 1
print(done, '/', len(d))
