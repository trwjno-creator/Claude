# Trilha original sintetizada (sem direitos autorais) + efeitos sonoros + mix final com a narracao.
import json, os, sys
import numpy as np, soundfile as sf

D = os.path.dirname(os.path.abspath(__file__))
SR = 48000
tl = json.load(open(f"{D}/timeline.json"))
TOTAL = tl['total']
N = int(TOTAL * SR)
rng = np.random.default_rng(1)

def t_(d):
    return np.arange(int(d * SR)) / SR

def env_ad(n, a=0.005, d=0.3):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
    return e

def lp(x, k=0.15):
    # filtro passa-baixa 1 polo
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += k * (x[i] - acc); y[i] = acc
    return y

def lp_fast(x, cutoff):
    # passa-baixa via FFT (rapido)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))

def hp_fast(x, cutoff):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / cutoff) ** 4)
    return np.fft.irfft(X, len(x))

def note_hz(n):  # midi
    return 440 * 2 ** ((n - 69) / 12)

def marimba(n, dur=0.6, vel=1.0):
    t = t_(dur); f = note_hz(n)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 7) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 22) + 0.1 * np.sin(2 * np.pi * f * 10 * t) * np.exp(-t * 40)
    x[:60] *= np.linspace(0, 1, 60)
    return x * vel

def pluck_bass(n, dur=0.45, vel=1.0):
    t = t_(dur); f = note_hz(n)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) + 0.12 * np.sin(2 * np.pi * 3 * f * t)) * np.exp(-t * 6)
    x[:40] *= np.linspace(0, 1, 40)
    return x * vel

def pad(notes, dur, vel=1.0):
    t = t_(dur); x = np.zeros_like(t)
    for n in notes:
        f = note_hz(n)
        for det in (-0.12, 0.0, 0.11):
            ph = rng.uniform(0, 2 * np.pi)
            x += np.sign(np.sin(2 * np.pi * f * (1 + det / 100) * t + ph)) * 0.3 + np.sin(2 * np.pi * f * (1 + det / 100) * t + ph)
    x = lp_fast(x, 1400)
    a = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.6)
    return x * a * vel / (len(notes) * 3)

def kick(vel=1.0):
    t = t_(0.35); f = 110 * np.exp(-t * 18) + 45
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 9) * vel

def hat(vel=1.0, dur=0.05):
    t = t_(dur); x = hp_fast(rng.standard_normal(len(t)), 7000) * np.exp(-t * 70)
    return x * vel * 0.5

def snap(vel=1.0):
    t = t_(0.18); x = hp_fast(rng.standard_normal(len(t)), 1500) * np.exp(-t * 30) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.6
    return x * vel * 0.6

def add(buf, x, t0, g=1.0):
    p = int(t0 * SR)
    if p >= len(buf) or p + len(x) <= 0: return
    if p < 0: x = x[-p:]; p = 0
    e = min(len(buf), p + len(x)); buf[p:e] += x[:e - p] * g

shot = {s['id']: s for s in tl['shots']}
def T(sid): return shot[sid]['v0']

# ------------------------------------------------- secoes (por tempo de shot)
sections = [
    # (inicio, fim, modo)  -- Breaking Bad
    (0.0, T('s02'), 'tense'),          # gancho
    (T('s02'), T('s06'), 'playful'),   # vida comum
    (T('s06'), T('s11'), 'groove'),    # comeca o negocio
    (T('s11'), T('s17'), 'dark'),      # Heisenberg
    (T('s17'), T('s23'), 'tense'),     # Gus
    (T('s23'), T('s27'), 'dark'),      # queda
    (T('s27'), TOTAL, 'calm'),         # final
]
BPM = 104; beat = 60 / BPM
mus = np.zeros(N + SR * 2)
# progressoes (raiz midi, acorde)
prog = {
    'playful': [(57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62]), (52, [52, 56, 59])],   # Am F G E
    'dark':    [(45, [57, 60, 64]), (46, [58, 62, 65]), (45, [57, 60, 64]), (44, [56, 60, 63])],
    'groove':  [(50, [62, 65, 69]), (48, [60, 64, 67]), (46, [58, 62, 65]), (45, [57, 61, 64])],  # Dm C Bb A
    'tense':   [(45, [57, 60, 64]), (46, [58, 61, 65]), (45, [57, 60, 64]), (47, [59, 62, 66])],
    'calm':    [(53, [65, 69, 72]), (48, [64, 67, 72]), (50, [62, 65, 69]), (46, [62, 65, 70])],
    'hope':    [(48, [60, 64, 67]), (55, [59, 62, 67]), (57, [60, 64, 69]), (53, [60, 65, 69])],  # C G Am F
}
for (a, b, mode) in sections:
    bar = beat * 4
    nb = int(np.ceil((b - a) / bar))
    for i in range(nb):
        t0 = a + i * bar
        if t0 >= b: break
        root, ch = prog[mode][i % 4]
        span = min(bar, b - t0)
        if mode in ('dark', 'tense', 'calm', 'hope'):
            add(mus, pad([n - 12 for n in ch], span + 0.3, 0.9 if mode != 'tense' else 0.7), t0, 0.55)
        for k in range(8):           # colcheias
            tk = t0 + k * beat / 2
            if tk >= b: break
            if mode == 'playful':
                if k % 2 == 0: add(mus, pluck_bass(root - 12 + (7 if k == 4 else 0)), tk, 0.55)
                add(mus, marimba(ch[(k * 2) % 3] + 12, 0.5, 0.55 if k % 2 == 0 else 0.35), tk, 0.45)
                if k in (2, 6): add(mus, snap(), tk, 0.35)
                add(mus, hat(0.5 if k % 2 else 0.3), tk, 0.35)
                if k in (0, 4): add(mus, kick(), tk, 0.5)
            elif mode == 'dark':
                if k == 0: add(mus, pluck_bass(root - 12, 1.2), tk, 0.6)
                if k in (3, 7): add(mus, marimba(ch[k % 3] + 12, 0.9, 0.35), tk, 0.35)
                if k == 0 and i % 2 == 0: add(mus, kick(0.6), tk, 0.45)
            elif mode == 'groove':
                if k in (0, 3, 4, 6): add(mus, pluck_bass(root - 12 + (12 if k == 6 else 0)), tk, 0.6)
                add(mus, marimba(ch[(k * 5) % 3] + (12 if k % 4 == 1 else 0), 0.4, 0.4), tk, 0.42)
                add(mus, hat(0.6 if k % 2 else 0.3), tk, 0.35)
                if k in (2, 6): add(mus, snap(), tk, 0.4)
                if k in (0, 5): add(mus, kick(), tk, 0.55)
            elif mode == 'tense':
                add(mus, pluck_bass(root - 12, 0.25, 0.7), tk, 0.55)
                if k % 2 == 0: add(mus, hat(0.4), tk, 0.3)
                if k in (0, 4): add(mus, kick(0.9), tk, 0.55)
                if k == 7: add(mus, marimba(ch[2] + 12, 0.4, 0.4), tk, 0.35)
            elif mode == 'calm':
                if k in (0, 3, 5): add(mus, marimba(ch[k % 3] + 12, 1.0, 0.35), tk, 0.35)
                if k == 0: add(mus, pluck_bass(root - 12, 1.2, 0.6), tk, 0.5)
            elif mode == 'hope':
                add(mus, marimba(ch[(k * 2) % 3] + 12, 0.7, 0.45 if k % 2 == 0 else 0.3), tk, 0.42)
                if k in (0, 3, 4): add(mus, pluck_bass(root - 12), tk, 0.55)
                if k in (2, 6): add(mus, snap(0.7), tk, 0.3)
                add(mus, hat(0.35), tk, 0.25)
                if k in (0, 4): add(mus, kick(0.8), tk, 0.45)
mus = mus[:N]
# fade in/out
fi = int(0.4 * SR); mus[:fi] *= np.linspace(0, 1, fi)
fo = int(2.5 * SR); mus[-fo:] *= np.linspace(1, 0, fo) ** 1.5
mus /= np.abs(mus).max() + 1e-9

# ------------------------------------------------- efeitos
sfx = np.zeros(N + SR)
def whoosh(d=0.35):
    t = t_(d); n = rng.standard_normal(len(t))
    # varredura: passa-banda que sobe
    out = np.zeros_like(n)
    seg = 8; L = len(n) // seg
    for i in range(seg):
        c = 400 * (2 ** (i * 0.6))
        part = n[i * L:(i + 1) * L]
        out[i * L:(i + 1) * L] = lp_fast(hp_fast(part, c * 0.5), c * 2)
    e = np.sin(np.pi * np.minimum(1, t / d)) ** 2
    return out * e / (np.abs(out).max() + 1e-9)

def pop():
    t = t_(0.09); f = 500 + 900 * np.exp(-t * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)

def ding():
    t = t_(0.7)
    return (np.sin(2 * np.pi * 1318 * t) + 0.5 * np.sin(2 * np.pi * 1975 * t)) * np.exp(-t * 6) * 0.6

def bang():
    t = t_(0.6); n = rng.standard_normal(len(t))
    return (lp_fast(n, 2500) * np.exp(-t * 14) * 1.2 + np.sin(2 * np.pi * 60 * t) * np.exp(-t * 8))

def knock():
    t = t_(0.15)
    return (np.sin(2 * np.pi * 320 * t) + 0.5 * lp_fast(rng.standard_normal(len(t)), 3000)) * np.exp(-t * 40)

def boom():
    t = t_(1.4); f = 70 * np.exp(-t * 1.5) + 30
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.5) + 0.3 * lp_fast(rng.standard_normal(len(t)), 300) * np.exp(-t * 3)

W = whoosh(); P = pop(); Dg = ding(); B = bang(); K = knock(); BM = boom()
for s in tl['shots'][1:]:
    add(sfx, W, s['v0'] - 0.18, 0.22)
# eventos sincronizados com a pos (lidos de overlays_events.json se existir)
ev_path = f"{D}/sfx_events.json"
if os.path.exists(ev_path):
    for e in json.load(open(ev_path)):
        snd = {'pop': (P, 0.18), 'ding': (Dg, 0.16), 'bang': (B, 0.55), 'knock': (K, 0.5), 'boom': (BM, 0.5)}[e['type']]
        add(sfx, snd[0], e['t'], snd[1])
sfx = sfx[:N]

# ------------------------------------------------- mix
voice, vsr = sf.read(f"{D}/narration.wav")
assert vsr == SR
voice = voice[:N]
# ducking da musica sob a voz
venv = np.abs(voice)
k = int(0.05 * SR)
venv = np.convolve(venv, np.ones(k) / k, mode='same')
duck = 1 - 0.45 * np.clip(venv / 0.05, 0, 1)
duck = np.convolve(duck, np.ones(int(0.12 * SR)) / int(0.12 * SR), mode='same')
music_gain = 10 ** (-17 / 20)
mix = voice * 1.0 + mus * music_gain * duck + sfx
peak = np.abs(mix).max()
mix = mix / peak * 0.93
sf.write(f"{D}/final_mix.wav", np.stack([mix, mix], 1), SR, subtype='PCM_16')
print("ok mix", TOTAL)
