import base64, json, os, subprocess, sys, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = {"narr": "iP95p4xoKVk53GoZ742B", "pedro": "bIHbv24MWmeRgasZH58o", "vo": "EXAVITQu4vr4xnSDxMaL"}
S = json.load(open(os.path.join(HERE, "script.json")))
os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
only = sys.argv[1:]
for tk in S["takes"]:
    if only and tk["id"] not in only: continue
    body = {"text": tk["text"], "model_id": "eleven_v3", "language_code": "pt", "voice_settings": {"stability": 0.5}}
    req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[tk['who']]}/with-timestamps?output_format=mp3_44100_128",
                                 data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    try: r = json.load(urllib.request.urlopen(req, timeout=300))
    except urllib.error.HTTPError as e: print(tk["id"], e.code, e.read()[:300]); sys.exit(1)
    mp3 = os.path.join(HERE, "audio", tk["id"] + ".mp3")
    open(mp3, "wb").write(base64.b64decode(r["audio_base64"]))
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3]).decode())
    json.dump({"alignment": r["alignment"], "duration": dur}, open(os.path.join(HERE, "audio", tk["id"] + ".json"), "w"), ensure_ascii=False)
    print(tk["id"], "%.2fs" % dur, len(tk["text"]), "chars")
