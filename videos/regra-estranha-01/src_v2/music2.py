import json, os, wave, numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 44100
D = json.load(open(os.path.join(HERE, "timeline.json"))); T = D["total"]; N = int(T * SR) + SR
mus = np.zeros(N); sfx = np.zeros(N); rng = np.random.default_rng(7)
WORDS = [w for l in D["lines"] for w in l["words"]]
def P(ph, which="s"):
    toks = [x.lower().strip(".,?!:") for x in ph.split()]; ws = [w["w"].lower().strip(".,?!:") for w in WORDS]
    for i in range(len(ws)):
        if ws[i:i + len(toks)] == toks: return WORDS[i if which == "s" else i + len(toks) - 1][which]
    raise SystemExit("missing " + ph)
def note(f, d, a=0.2):
    t = np.arange(int(d * SR)) / SR; env = np.exp(-t * 2.2) * np.minimum(1, t * 200)
    return sum(np.sin(2 * np.pi * f * h * t) * 0.6 ** (h - 1) for h in (1, 2, 3, 4)) * env * a
def add(buf, st, sig):
    i = int(st * SR)
    if i < len(buf): sig = sig[:len(buf) - i]; buf[i:i + len(sig)] += sig
hz = lambda n: 440 * 2 ** ((n - 69) / 12)
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]; MEL = [76, 74, 72, 71, 72, 74, 76, 79]; beat = 60 / 76
def play(a, b, amp, mel=True):
    t, k = a, 0
    while t < b:
        ch = CH[(k // 4) % 4]
        if k % 4 == 0:
            for n in ch: add(mus, t, note(hz(n - 12), beat * 4, amp * 0.8))
        add(mus, t, note(hz(ch[k % 3]), beat * 1.5, amp * 0.6))
        if mel and k % 2 == 0: add(mus, t + beat * 0.5, note(hz(MEL[(k // 2) % 8]), beat * 2, amp * 0.5))
        t += beat; k += 1
def ramp(a, b, g0, g1):
    i, j = int(a * SR), int(b * SR); mus[i:j] *= np.linspace(g0, g1, max(1, j - i))
tAi, tMeio, tFoi = P("Aí veio"), P("Eu tava no meio"), P("Foi aí")
play(0, tAi, 0.10); play(tAi, tMeio + 2.0, 0.08, mel=False); play(tFoi - 0.2, T - 0.8, 0.15)
ramp(P("frio") - 1.2, P("frio") - 0.2, 1, 0); mus[int((P("frio") - 0.2) * SR):int((tFoi - 0.2) * SR)] = 0; ramp(T - 2.0, T, 1, 0)
def whoosh(at, d=0.6, a=0.25):
    n = int(d * SR); y = np.convolve(rng.standard_normal(n), np.ones(30) / 30, "same") * np.sin(np.linspace(0, np.pi, n)) ** 2 * a * 3; add(sfx, at, y)
def plim(at, f=1568, a=0.16):
    t = np.arange(int(0.6 * SR)) / SR; add(sfx, at, (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 7) * a)
def thump(at, f=55, a=0.5, d=0.25):
    t = np.arange(int(d * SR)) / SR; add(sfx, at, np.sin(2 * np.pi * f * t) * np.exp(-t * 18) * a)
def noise(a, b, amp, smooth=200):
    n = int((b - a) * SR); y = np.convolve(rng.standard_normal(n), np.ones(smooth) / smooth, "same") * 12
    env = np.minimum(1, np.minimum(np.arange(n) / (0.3 * SR), (n - np.arange(n)) / (0.4 * SR))); add(sfx, a, y * env * amp)
whoosh(P("E a minha") - 0.4); thump(P("Até a terça-feira"), 45, 0.5, 0.5)
plim(P("sua mãe") + 0.4, 1318, 0.12); noise(P("pega fogo") - 0.1, P("pega fogo") + 1.0, 0.18, 40)
for w in ("A Júlia", "O Pedro", "olhar"): plim(P(w), 1568 if w != "olhar" else 2093)
plim(P("Eu sou o Caio"), 1046, 0.12); whoosh(P("Relaxa") - 0.7, 0.5, 0.15)
for ph in ("Fiz aniversário", "Me formei"): thump(P(ph) + 0.35, 70, 0.35, 0.3)
plim(P("Cida"), 1318, 0.1); plim(P("Põe"), 1046, 0.12)
thump(P("Aí veio") + 0.1, 45, 0.5, 0.5)
for k in range(6): thump(P("frio") - 1.0 + k * 0.8, 55, 0.5); thump(P("frio") - 1.0 + k * 0.8 + 0.22, 55, 0.4)
noise(P("frio") - 1.2, P("Eu larguei"), 0.16)
t0 = P("Eu larguei")
for k in range(int((P("Quando eu cheguei") - t0) / 0.28)): thump(t0 + k * 0.28, 90, 0.25, 0.08)
thump(P("fechando") + 0.6, 40, 0.7, 0.5)
plim(P("Desde o dia"), 1318, 0.12); plim(P("ele esquenta") + 0.25, 1760, 0.2)
mix = mus * 0.9 + sfx; mix /= max(1.0, np.abs(mix).max() / 0.9)
pcm = (np.stack([mix, mix], 1) * 32767).astype(np.int16)
with wave.open(os.path.join(HERE, "music.wav"), "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("music ok", round(T, 2))
