"""Generates each line with ElevenLabs (with-timestamps). The API key is injected by the network proxy."""
import base64, json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = {"narr": "nPczCjzI2devNBz1zQrb", "pedro": "TX3LPaxmHKxFdv7VOQHJ", "vo": "EXAVITQu4vr4xnSDxMaL"}
SETTINGS = {
    "narr": {"stability": 0.42, "similarity_boost": 0.8, "style": 0.3, "use_speaker_boost": True},
    "pedro": {"stability": 0.38, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True},
    "vo": {"stability": 0.45, "similarity_boost": 0.8, "style": 0.4, "use_speaker_boost": True},
}
SPEED = {"L10": 0.85, "L11": 0.92, "L12": 0.92, "L13": 0.92}

def tts(line, prev_text, next_text):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICES[line['who']]}/with-timestamps?output_format=mp3_44100_128"
    body = {"text": line.get("tts", line["text"]), "model_id": "eleven_v3", "language_code": "pt", "voice_settings": {"stability": 0.5}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json", "xi-api-key": "proxy-injected"})
    try:
        return json.load(urllib.request.urlopen(req, timeout=120))
    except urllib.error.HTTPError as e:
        print(line["id"], "HTTP", e.code, e.read()[:400]); sys.exit(1)

def main(only=None):
    lines = json.load(open(os.path.join(HERE, "lines.json")))
    os.makedirs(os.path.join(HERE, "audio"), exist_ok=True)
    for i, ln in enumerate(lines):
        if only and ln["id"] not in only: continue
        same = [l for l in lines if l["who"] == ln["who"]]
        k = same.index(ln)
        prev_t = same[k - 1]["text"] if k > 0 else None
        next_t = same[k + 1]["text"] if k + 1 < len(same) else None
        r = tts(ln, prev_t, next_t)
        mp3 = os.path.join(HERE, "audio", ln["id"] + ".mp3")
        open(mp3, "wb").write(base64.b64decode(r["audio_base64"]))
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp3]).decode().strip())
        al = r.get("normalized_alignment") or r["alignment"]
        if r.get("alignment"): al = r["alignment"]
        json.dump({"alignment": al, "duration": dur}, open(os.path.join(HERE, "audio", ln["id"] + ".json"), "w"), ensure_ascii=False)
        print(ln["id"], ln["who"], "%.2fs" % dur)

if __name__ == "__main__":
    main(sys.argv[1:] or None)
