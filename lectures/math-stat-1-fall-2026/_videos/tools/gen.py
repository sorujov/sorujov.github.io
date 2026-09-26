import json,os,time,urllib.request
K=[l.split('=',1)[1].strip() for l in open(os.path.expanduser('~/mnt/.secrets/.env'),encoding='utf-8') if l.startswith('ELEVENLABS_API_KEY=')][0]
V=[l.split('=',1)[1].strip() for l in open(os.path.expanduser('~/mnt/.secrets/.env'),encoding='utf-8') if l.startswith('ELEVENLABS_VOICE_ID=')][0]
d=json.load(open('texts.json',encoding='utf-8')); t0=time.time(); done=0
for h,txt in d.items():
    if os.path.exists(h+'.mp3'): done+=1; continue
    if time.time()-t0>140: break
    body=json.dumps({"text":txt,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.55,"similarity_boost":0.85}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{V}?output_format=mp3_44100_128",data=body,headers={"xi-api-key":K,"Content-Type":"application/json"})
    a=urllib.request.urlopen(req,timeout=90).read(); open(h+'.mp3','wb').write(a); done+=1
print(done,'/',len(d))
