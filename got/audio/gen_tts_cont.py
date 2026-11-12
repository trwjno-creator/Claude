# Narracao CONTINUA: o roteiro inteiro numa unica passada de TTS (entonacao e pausas naturais),
# com o tempo de cada palavra. Depois divide as palavras por frase (shot) e monta o timeline.json.
# uso: python3 gen_tts_cont.py <rate> [pitch]
import ssl, sys, os, json, asyncio, subprocess, re
import numpy as np, soundfile as sf
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(D))
import edge_tts, edge_tts.communicate as ec
from script import LINES

ca = '/root/.ccr/ca-bundle.crt'
if os.path.exists(ca):
    ec._SSL_CTX = ssl.create_default_context(cafile=ca)

RATE = sys.argv[1] if len(sys.argv) > 1 else "+6%"
PITCH = sys.argv[2] if len(sys.argv) > 2 else "-2Hz"
TOTAL, FPS, T0 = 150.0, 30, 0.25

text = " ".join(t for _, t in LINES)

async def run():
    for attempt in range(5):
        try:
            c = edge_tts.Communicate(text, "pt-BR-AntonioNeural", rate=RATE, pitch=PITCH, boundary="WordBoundary")
            words = []
            with open(f"{D}/narr_raw.mp3", "wb") as f:
                async for ch in c.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append([ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7])
            return words
        except Exception as e:
            print("retry", e); await asyncio.sleep(2 * (attempt + 1))
    raise SystemExit("TTS falhou")

words = asyncio.run(run())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{D}/narr_raw.mp3", "-ar", "48000", "-ac", "1", f"{D}/narr_raw.wav"], check=True)
a, sr = sf.read(f"{D}/narr_raw.wav")
# encurta pausas longas entre frases (>0.55s) para ~0.45s, com crossfade - ritmo de narrador humano
KEEP, MAXG = 0.32, 0.38
cuts = []
for i in range(len(words) - 1):
    g = words[i + 1][1] - words[i][2]
    if g > MAXG:
        c0 = words[i][2] + 0.16; c1 = words[i + 1][1] - (KEEP - 0.16)
        if c1 > c0:
            seg_ = a[int(c0 * sr):int(c1 * sr)]
            if np.abs(seg_).max() < 0.03:          # so corta se for silencio de verdade
                cuts.append((c0, c1))
pieces, last = [], 0
xf = int(0.008 * sr)
for c0, c1 in cuts:
    pieces.append(a[last:int(c0 * sr)]); last = int(c1 * sr)
pieces.append(a[last:])
b = pieces[0]
for pc in pieces[1:]:
    ramp = np.linspace(0, 1, xf)
    b = np.concatenate([b[:-xf], b[-xf:] * (1 - ramp) + pc[:xf] * ramp, pc[xf:]])
def remap(t):
    # cada corte remove (c1-c0) e o crossfade sobrepoe mais XF segundos
    XF = xf / sr
    return t - sum((min(c1, max(c0, t)) - c0) + (XF if t >= c1 else 0) for c0, c1 in cuts)
words = [[w, remap(t0), remap(t1)] for w, t0, t1 in words]
a = b
print("pausas encurtadas:", len(cuts))
idx = np.where(np.abs(a) > 0.008)[0]
s0, s1 = idx[0] / sr - 0.03, idx[-1] / sr + 0.06
speech = s1 - s0
print("palavras", len(words), "fala", round(speech, 2))

# divide palavras por frase (mesma contagem de tokens)
def ntok(t):
    return len([w for w in t.split() if re.search(r"\w", w)])
counts = [ntok(t) for _, t in LINES]
assert sum(counts) == len(words), (sum(counts), len(words))

if T0 + speech > TOTAL - 0.8:
    raise SystemExit(f"FALA LONGA DEMAIS: {speech:.2f}s (aumente a velocidade)")

out = np.zeros(int(TOTAL * sr))
seg = a[int(s0 * sr):int(s1 * sr)].copy()
n = int(0.01 * sr); seg[:n] *= np.linspace(0, 1, n); seg[-n:] *= np.linspace(1, 0, n)
p = int(T0 * sr); out[p:p + len(seg)] = seg
out = out / np.abs(out).max() * 0.89
sf.write(f"{D}/narration.wav", out, sr)

shift = T0 - s0
shots = []; k = 0
for (sid, txt), c in zip(LINES, counts):
    ws = [{"w": w, "t0": round(t0 + shift, 3), "t1": round(t1 + shift, 3)} for w, t0, t1 in words[k:k + c]]
    k += c
    shots.append({"id": sid, "text": txt, "a0": ws[0]["t0"], "a1": ws[-1]["t1"], "words": ws})
for i, sh in enumerate(shots):
    v0 = 0.0 if i == 0 else shots[i - 1]["v1"]
    v1 = TOTAL if i == len(shots) - 1 else round((sh["a1"] + shots[i + 1]["a0"]) / 2, 4)
    sh["v0"], sh["v1"] = v0, v1
    sh["f0"], sh["f1"] = int(round(v0 * FPS)), int(round(v1 * FPS))
    sh["nframes"] = sh["f1"] - sh["f0"]
json.dump({"fps": FPS, "total": TOTAL, "shots": shots}, open(f"{D}/timeline.json", "w"), ensure_ascii=False, indent=1)
gaps = [round(shots[i + 1]["a0"] - shots[i]["a1"], 2) for i in range(len(shots) - 1)]
print("fim da fala", round(shots[-1]["a1"], 2), "| pausas entre frases: min", min(gaps), "max", max(gaps))
for sh in shots:
    print(sh["id"], sh["nframes"], end="  ")
print()
