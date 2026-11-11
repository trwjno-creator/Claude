# Gera a narracao frase a frase com edge-tts (pt-BR-AntonioNeural) + tempos de cada palavra.
import ssl, sys, os, json, asyncio, subprocess
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import edge_tts, edge_tts.communicate as ec
from script import LINES

ca = '/root/.ccr/ca-bundle.crt'
if os.path.exists(ca):
    ec._SSL_CTX = ssl.create_default_context(cafile=ca)

OUT = sys.argv[1]
RATE = sys.argv[2] if len(sys.argv) > 2 else "+8%"
PITCH = sys.argv[3] if len(sys.argv) > 3 else "-2Hz"
os.makedirs(OUT, exist_ok=True)

async def one(sid, text):
    mp3 = f"{OUT}/{sid}.mp3"
    words = []
    for attempt in range(5):
        try:
            c = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate=RATE, pitch=PITCH, boundary="WordBoundary")
            words = []
            with open(mp3, "wb") as f:
                async for ch in c.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append([ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7])
            break
        except Exception as e:
            print("retry", sid, e); await asyncio.sleep(2 * (attempt + 1))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "48000", "-ac", "1", f"{OUT}/{sid}.wav"], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{OUT}/{sid}.wav"]))
    return {"id": sid, "text": text, "words": words, "dur": dur}

async def main():
    res = []
    for sid, text in LINES:
        r = await one(sid, text); res.append(r)
        print(sid, round(r["dur"], 2), len(r["words"]), len(text.split()))
    json.dump(res, open(f"{OUT}/tts.json", "w"), ensure_ascii=False, indent=1)
    print("TOTAL", sum(r["dur"] for r in res))

asyncio.run(main())
