"""Create (once) an ElevenLabs Instant Voice Clone from Sam's sample(s).

Usage:  ELEVENLABS_API_KEY=... python clone_voice.py voice_sample.m4a [more files...]
Prints the voice_id; store it as ELEVENLABS_VOICE_ID in .env.
"""
import os
import sys
import requests

key = os.environ["ELEVENLABS_API_KEY"]
files = [("files", (os.path.basename(p), open(p, "rb"))) for p in sys.argv[1:]]
r = requests.post(
    "https://api.elevenlabs.io/v1/voices/add",
    headers={"xi-api-key": key},
    data={"name": "Samir Orujov (lectures)",
          "description": "Sam's own voice, for STAT-2311 lecture videos",
          "remove_background_noise": "true"},
    files=files,
    timeout=300,
)
r.raise_for_status()
print(r.json()["voice_id"])
