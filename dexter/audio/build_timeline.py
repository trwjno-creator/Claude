# Monta a narracao continua (48k mono) e o timeline.json com inicio/fim de cada shot e de cada palavra.
import json, sys, os
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from script import SHOW

D = os.path.dirname(os.path.abspath(__file__))
TOTAL = 150.0
FPS = 30
T0 = 0.20          # silencio no inicio
TAIL = 1.6         # respiro no fim (depois da ultima palavra)
PAD = 0.04

d = json.load(open(f"{D}/tts/tts.json"))
clips = []
for r in d:
    a, sr = sf.read(f"{D}/tts/{r['id']}.wav")
    idx = np.where(np.abs(a) > 0.008)[0]
    s = max(0, idx[0] / sr - PAD); e = min(len(a) / sr, idx[-1] / sr + PAD)
    clips.append((r, a, sr, s, e))
speech = sum(e - s for _, _, _, s, e in clips)
G = (TOTAL - T0 - TAIL - speech) / (len(clips) - 1)
print("speech", round(speech, 2), "gap", round(G, 3))
assert 0.15 < G < 0.8, G

sr = clips[0][2]
out = np.zeros(int(TOTAL * sr) + sr)
t = T0
shots = []
for i, (r, a, _, s, e) in enumerate(clips):
    seg = a[int(s * sr):int(e * sr)].copy()
    # fades curtos para nao estalar
    n = int(0.01 * sr); seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
    p = int(t * sr); out[p:p + len(seg)] += seg
    words = []
    for w, ws, we in r["words"]:
        words.append({"w": SHOW.get(w, w), "t0": round(t + ws - s, 3), "t1": round(t + we - s, 3)})
    shots.append({"id": r["id"], "text": r["text"], "a0": round(t, 3), "a1": round(t + e - s, 3), "words": words})
    t += (e - s) + G
# limites visuais de cada shot: corte acontece no meio do gap (antes da proxima fala)
for i, sh in enumerate(shots):
    v0 = 0.0 if i == 0 else shots[i - 1]["v1"]
    v1 = TOTAL if i == len(shots) - 1 else (sh["a1"] + shots[i + 1]["a0"]) / 2 + 0.02
    sh["v0"] = v0; sh["v1"] = round(v1, 4)
    sh["f0"] = int(round(v0 * FPS)); sh["f1"] = int(round(v1 * FPS))
    sh["nframes"] = sh["f1"] - sh["f0"]
out = out[:int(TOTAL * sr)]
out = out / max(1e-6, np.abs(out).max()) * 0.89
sf.write(f"{D}/narration.wav", out, sr)
json.dump({"fps": FPS, "total": TOTAL, "shots": shots}, open(f"{D}/timeline.json", "w"), ensure_ascii=False, indent=1)
for sh in shots:
    print(sh["id"], sh["f0"], sh["f1"], sh["nframes"], round(sh["nframes"] / FPS, 2))
