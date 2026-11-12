"""Trilha + efeitos de "Cadê Meu Par?" — tudo sintetizado (sem samples externos).
Gera audio/mix.wav (48 kHz, estéreo, 40 s) sincronizado com anim.js."""
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
import wave, os

SR = 48000; DUR = 40.0; N = int(SR * DUR)
rng = np.random.default_rng(7)
music = np.zeros((N, 2)); sfx = np.zeros((N, 2)); verb_send = np.zeros((N, 2))

def T(d): return np.arange(int(d * SR)) / SR
def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def filt(x, f, kind='low', order=2):
    return sosfilt(butter(order, f, kind, fs=SR, output='sos'), x)
def phase(f, n):
    f = np.broadcast_to(np.asarray(f, float), (n,)); return 2 * np.pi * np.cumsum(f) / SR
def saw(f, d):
    n = int(d * SR); p = phase(f, n) / (2 * np.pi); return 2 * (p % 1) - 1
def sq(f, d):
    n = int(d * SR); return np.sign(np.sin(phase(f, n)))
def sine(f, d):
    n = int(d * SR); return np.sin(phase(f, n))
def noise(d): return rng.standard_normal(int(d * SR))
def env(d, a=.01, r=.1, s=1.0):
    n = int(d * SR); e = np.ones(n) * s; na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, s, na); e[-nr:] *= np.linspace(1, 0, nr); return e
def dec(d, k): return np.exp(-T(d) * k)
def add(bus, t, x, g=1.0, pan=0.0, rev=0.0):
    i = int(t * SR); x = np.asarray(x) * g
    if i < 0: x = x[-i:]; i = 0
    j = min(N, i + len(x)); x = x[: j - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[i:j, 0] += x * l * 1.414; bus[i:j, 1] += x * r * 1.414
    if rev: verb_send[i:j, 0] += x * l * rev; verb_send[i:j, 1] += x * r * rev

# ---------- instrumentos ----------
def pluck(m, d=.6, bright=1.0):
    f = hz(m); t = T(d); y = np.zeros_like(t)
    for k in range(1, 9): y += np.sin(2 * np.pi * f * k * t) / k * np.exp(-t * (3 + k * 2.5 / bright))
    return y * env(d, .002, .05)
def bell(m, d=1.2):
    f = hz(m); t = T(d)
    y = np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + .35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + .15 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 10)
    return y * env(d, .002, .1)
def pad(ms, d, cut=1400, a=.4, r=.5):
    y = sum(saw(hz(m) * (1 + det), d) for m in ms for det in (-.004, .004)) / (2 * len(ms))
    return filt(y, cut) * env(d, a, r)
def brass(ms, d, cut=1800):
    y = sum(saw(hz(m) * (1 + det), d) for m in ms for det in (-.003, .003)) / (2 * len(ms))
    return filt(y, cut, order=2) * env(d, .02, .15) * (0.6 + .4 * dec(d, 6))
def formant(x, fs_=((800, 1.0), (1150, .6), (2900, .25))):
    return sum(g * filt(x, [f * .85, f * 1.15], 'band', 2) for f, g in fs_)
def voice(f0, d, vib=6, depth=.02, vowel='a'):
    t = T(d); f = np.broadcast_to(np.asarray(f0, float), t.shape) * (1 + depth * np.sin(2 * np.pi * vib * t))
    F = {'a': ((800, 1.0), (1150, .6), (2900, .25)), 'o': ((450, 1.0), (800, .5), (2830, .15)), 'u': ((325, 1.0), (700, .4), (2530, .1))}[vowel]
    return formant(saw(f, d), F)
def violin(m, d):
    t = T(d); f = hz(m) * (1 + .006 * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / .3, 0, 1))
    y = saw(f, d); y = filt(y, 3200) + .5 * filt(y, [2000, 3200], 'band')
    return y * env(d, .18, .35)
def kick(d=.4):
    t = T(d); f = 45 + 90 * np.exp(-t * 30); return np.sin(phase(f, len(t))) * np.exp(-t * 7)
def snare(d=.22):
    return (filt(noise(d), [1200, 6000], 'band') * .8 + .4 * sine(190, d)) * dec(d, 18)
def hat(d=.06): return filt(noise(d), 7000, 'high') * dec(d, 60)
def crash(d=2.0): return filt(noise(d), 4000, 'high') * dec(d, 2.2)
def whoosh(d, f0=300, f1=3000):
    x = noise(d); n = len(x); out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        p = i / n; fc = f0 * (f1 / f0) ** p
        out[i:i + seg] = filt(x[i:i + seg], [fc * .7, min(fc * 1.4, 20000)], 'band', 1)
    return out * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
def slide(f0, f1, d, kind='sine', curve=1.0):
    t = np.linspace(0, 1, int(d * SR)) ** curve; f = f0 * (f1 / f0) ** t
    return (np.sin(phase(f, len(f))) if kind == 'sine' else saw(f, d)) * env(d, .005, .03)
def thump(d=.35, f0=110, f1=40):
    t = T(d); f = f1 + (f0 - f1) * np.exp(-t * 18)
    return (np.sin(phase(f, len(t))) * np.exp(-t * 9) + .3 * filt(noise(d), 500) * np.exp(-t * 25))
def beep(f=2000, d=.11): return np.sign(np.sin(2 * np.pi * f * T(d))) * env(d, .002, .01) * .5
def blip(f, d=.05): return sine(f, d) * dec(d, 40)

# ---------- 0–2 s e 37.6–40 s: máquina batendo + grito (loop) ----------
t = np.arange(N) / SR
me = np.clip(1 - (t - 2.0) / .6, 0, 1) * (t < 2.6) + np.clip((t - 37.6) / .8, 0, 1)
rum = filt(noise(DUR), 180) * 3 + .6 * np.sin(2 * np.pi * 50 * t)
slosh = filt(noise(DUR), [300, 1400], 'band') * (.5 + .5 * np.sin(2 * np.pi * 1.1 * t)) ** 2 * 1.5
whir = filt(saw(110 + 15 * np.sin(2 * np.pi * .5 * t), DUR), 900) * .25
mach = (rum + slosh + whir) * me * .35
sfx[:, 0] += mach; sfx[:, 1] += mach

def scream(t0, d, f0=620, f1=760, g=.5, rot=True, vowel='a'):
    tt = T(d); f = np.linspace(f0, f1, len(tt)) * (1 + .03 * np.sin(2 * np.pi * 7 * tt))
    y = voice(f, d, vib=7, depth=.0, vowel=vowel) * env(d, .03, .12)
    if rot: y *= .55 + .45 * np.cos(2 * np.pi * (7 / (2 * np.pi)) * 3.0 * (tt + t0) / 3.0) ** 2
    add(sfx, t0, y, g, pan=0)
scream(0.0, 2.05, 640, 720, .9)
scream(39.05, .95, 520, 640, .8)

# ---------- cena 2 ----------
for k, tb in enumerate((2.1, 2.35, 2.6)): add(sfx, tb, beep(2100), .25)
add(sfx, 2.56, filt(noise(.05), 3000, 'high') * dec(.05, 60), .5)          # trava da porta
add(sfx, 3.0, whoosh(.45, 200, 1500), .5, pan=.4)
add(sfx, 3.5, filt(noise(.25), 2500) * dec(.25, 14), .5)                   # pega a roupa
add(sfx, 3.65, whoosh(.5, 1500, 250), .5, pan=.6)
add(sfx, 3.55, slide(900, 1500, .12) * .6, .5)                             # "ei!"
add(sfx, 3.8, slide(1000, 1600, .12) * .6, .45)
add(sfx, 4.05, slide(1100, 1700, .14) * .6, .4)
for k in range(10):                                                        # pizzicato na ponta dos pés
    add(music, 2.7 + k * .19, pluck([62, 65, 69, 65, 64, 67, 70, 67, 69, 61][k], .3, .6), .22, pan=-.2)
add(sfx, 4.6, thump(.5, 90, 35), 1.0); add(sfx, 4.6, filt(noise(.3), 800) * dec(.3, 12), .6)
add(sfx, 4.72, slide(1400, 900, .4) * (1 + .5 * np.sin(2 * np.pi * 35 * T(.4))), .18)  # borracha rangendo
scream(5.15, .85, 700, 260, .7, rot=False)
for k, g in enumerate((1.0, .45, .2)):
    add(sfx, 5.15 + k * .3, filt(slide(320, 90, .16), 2000 - k * 600), .8 * g, pan=(-.5, .5, 0)[k])

# ---------- cena 3: o reino (mistério / fantasia) ----------
add(sfx, 6.5, thump(.4, 130, 50), .9); add(sfx, 6.5, filt(noise(.4), 1200) * dec(.4, 10), .4)
for k in range(5): add(sfx, 6.55 + k * .09, blip(1200 + 150 * k, .07), .18, pan=-.6 + .3 * k)  # "!" das meias
CH = [(6.5, [50, 57, 62, 65, 69]), (8.5, [46, 53, 62, 65, 70]), (10.5, [43, 55, 62, 67, 70]), (12.5, [45, 57, 61, 64, 69])]
for (t0, ch), nxt in zip(CH, [8.5, 10.5, 12.5, 14.05]):
    add(music, t0, pad(ch, nxt - t0 + .4, 1100, .5, .5), .5, rev=.4)
    add(music, t0, pad([ch[0] - 12], nxt - t0 + .3, 400, .2, .4), .5)
    upper = [m + 12 for m in ch[1:]]; pat = [0, 2, 1, 3, 2, 3, 1, 2]
    k = 0; tt = t0
    while tt < nxt - .05:
        add(music, tt, bell(upper[pat[k % 8]] + 12 * (k % 16 >= 8), .9), .14, pan=.4 * np.sin(k), rev=.5); k += 1; tt += .3
add(sfx, 7.0, bell(93, 1.5) + bell(98, 1.5), .12, rev=.6)                    # brilho do título
add(music, 12.75, brass([38, 45, 50], .6, 900), .9, rev=.3); add(music, 12.75, kick(.6), .6)   # dun...
add(music, 13.15, brass([38, 44, 50], 1.0, 900), 1.0, rev=.3); add(music, 13.15, kick(.6), .7) # DUN!
add(sfx, 13.3, slide(500, 220, .25), .3)                                    # glup

# ---------- cena 4: fuga épica (120 bpm) ----------
B = .5
for i, cut in enumerate((14, 16, 18, 20, 22)): add(sfx, cut - .3, whoosh(.38, 400, 5000), .45, pan=(-.4, .4)[i % 2])
BAR = [(14, 50), (16, 46), (18, 48), (20, 45)]
CHD = {50: [50, 57, 62, 65], 46: [46, 53, 58, 62], 48: [48, 55, 60, 64], 45: [45, 52, 57, 61]}
for t0, root in BAR:
    for b in range(8):                                                       # baixo em colcheias
        add(music, t0 + b * B / 2, filt(saw(hz(root - 12 + (12 if b % 4 == 3 else 0)), .22), 700) * env(.22, .005, .05), .5)
    for b in range(16):                                                      # ostinato de cordas
        add(music, t0 + b * B / 4 * 2, filt(saw(hz(CHD[root][[0, 2, 1, 3][b % 4]] + 12), .12), 2500) * env(.12, .005, .04), .16, pan=.3, rev=.2)
    add(music, t0, brass(CHD[root] + [root + 12], .8), .55, rev=.3)
    add(music, t0 + 1.25, brass(CHD[root] + [root + 12], .45), .4, rev=.3)
    for b in range(4):
        add(music, t0 + b * B, kick(), .8)
        if b % 2: add(music, t0 + b * B, snare(), .45, rev=.2)
        add(music, t0 + b * B + B / 2, kick(.3), .45 if b == 3 else 0)
    for b in range(8): add(music, t0 + b * B / 2, hat(), .18, pan=.5)
for k in range(16): add(music, 21.0 + k * .0625, snare(.1), .08 + .25 * k / 16)  # rufada
# efeitos da montagem
for k in range(6): add(sfx, 14.15 + k * .07, filt(noise(.05), 2000, 'high') * dec(.05, 50), .25)  # papel de bala
add(sfx, 15.15, slide(2200, 1600, .1) + slide(1600, 2300, .1), .12)        # X do mapa
for k in range(6): add(sfx, 16.05 + k / 3, slide(700 + 60 * k, 1100 + 60 * k, .12) * (1 + .4 * np.sin(2 * np.pi * 40 * T(.12))), .2, pan=-.3)
gr = filt(saw(62 + 8 * np.sin(2 * np.pi * 9 * T(2.0)), 2.0), 600) * (1 + .5 * filt(noise(2.0), 30)) * env(2.0, .1, .3)
add(sfx, 18.0, gr, .45, pan=-.4)                                              # GRRRR do monstro
for k in range(16): add(sfx, 18.02 + k * .125, blip(400 + 80 * (k % 2), .04), .25, pan=.4)  # passinhos
for k in range(4): scream(18.3 + k * .42, .3, 760, 820, .35, rot=False)
add(sfx, 20.1, slide(300, 900, 1.0) * (1 + .3 * np.sin(2 * np.pi * 25 * T(1.0))), .14)   # elástico esticando
tw = sum(np.sin(2 * np.pi * 110 * k * (1 + .02 * np.exp(-T(1.2) * 4)) * T(1.2)) / k * np.exp(-T(1.2) * (3 + k)) for k in range(1, 7))
add(sfx, 21.15, tw, .7); add(sfx, 21.15, whoosh(.5, 500, 6000), .5, pan=.5)
scream(21.2, .5, 600, 1100, .4, rot=False)
# 22–24 câmera lenta: coral "aaah" + sinos
add(music, 22.0, crash(2.5), .35, rev=.4); add(music, 22.0, kick(.8), .8)
for m in [50, 57, 62, 66, 69]:
    add(music, 22.0, voice(hz(m), 2.3, 5, .01) * env(2.3, .25, .6), .16, pan=.2 * (m % 3 - 1), rev=.8)
add(music, 22.0, pad([38, 50, 57, 62, 66], 2.4, 1600, .1, .7), .45, rev=.5)
for k in range(8): add(music, 22.1 + k * .22, bell(86 + [0, 4, 7, 12, 7, 4, 12, 16][k], 1.2), .1, pan=.6 * np.sin(k), rev=.7)
add(sfx, 22.0, filt(noise(2.0), 600) * env(2.0, .5, .8), .15)               # vento

# ---------- cena 5 ----------
add(sfx, 24.0, slide(1600, 500, .6, curve=.7), .2)                          # assobio de queda
add(sfx, 24.6, thump(.35, 100, 45), .5); add(sfx, 24.6, filt(noise(.3), 900) * dec(.3, 14), .4)
add(sfx, 25.2, bell(93, 1.4) + bell(100, 1.4), .2, rev=.6)                  # *ding* viu o par
for k in range(12): add(music, 25.25 + k * .035, pluck(53 + [0, 4, 7, 12, 16, 19, 24, 28, 31, 36, 40, 43][k], 1.0), .16, pan=-.5 + k / 11, rev=.6)  # harpa
add(music, 25.3, pad([53, 57, 60, 64], 1.15, 1300, .3, .3), .45, rev=.6)
add(music, 26.4, pad([46, 57, 62, 65], 1.1, 1300, .3, .2), .45, rev=.6)
for k, m in enumerate([65, 69, 72, 76, 74, 70, 69, 65]): add(music, 25.6 + k * .23, pluck(m + 12, .9), .14, rev=.6)
for m in (65, 69, 72): add(music, 25.4, voice(hz(m), 2.05, 5, .012, 'o') * env(2.05, .4, .1), .1, rev=.8)
for k in range(9): add(sfx, 25.4 + k * .23, blip(1500 + 200 * (k % 3), .04), .1, pan=np.sin(k * 2))  # coraçõezinhos
# arranhão de disco
sc = noise(.4); n = len(sc); out = np.zeros(n)
for i in range(0, n, 1024):
    p = i / n; fc = 3500 * (1 - p) + 400 if p < .5 else 400 + 2500 * (p - .5) * 2
    out[i:i + 1024] = filt(sc[i:i + 1024], [fc * .6, fc * 1.5], 'band', 1)
add(sfx, 27.45, out * env(.4, .005, .08), .9)
for k in range(5):                                                          # grilos no silêncio constrangedor
    for j in range(3): add(sfx, 27.8 + k * .45 + j * .06, sine(4400, .04) * np.sin(np.pi * np.linspace(0, 1, int(.04 * SR))), .05, pan=.6)
for k in range(14): add(sfx, 28.1 + k * .05, blip(520 + 120 * ((k * 7) % 5), .045), .14, pan=.3)  # "falando"
# violino triste + raio + chuva
for m, t0, d in [(69, 28.8, .95), (67, 29.75, .45), (65, 30.2, .45), (64, 30.65, .75), (65, 31.4, .4), (64, 31.8, .4), (62, 32.2, 1.3)]:
    add(music, t0, violin(m, d + .1), .32, rev=.6)
add(music, 28.8, pad([38, 50, 57], 4.6, 700, .8, 1.2), .45, rev=.5)
thn = filt(noise(2.0), 1500) * dec(2.0, 2.2) * (1 + 2 * dec(2.0, 30)) + .5 * filt(noise(2.0), 120) * dec(2.0, 1.5)
add(sfx, 30.3, thn, .9, rev=.3)
add(sfx, 30.25, filt(noise(1.9), 3000, 'high') * env(1.9, .3, .4), .07)    # chuva

# ---------- cena 6 ----------
add(sfx, 32.35, whoosh(.6, 200, 1200), .4, pan=-.2)
add(sfx, 33.1, slide(1800, 2600, .07), .15)                                  # pinça
add(sfx, 33.25, whoosh(.7, 300, 3000), .45)
scream(33.15, .4, 700, 900, .3, rot=False, vowel='o')
for k, m in enumerate([74, 78, 81, 86]): add(music, 34.0 + k * .25, bell(m, 1.2), .2, rev=.6)   # caixinha de música esperançosa
add(sfx, 34.35, slide(400, 650, .18), .25)                                   # "hm?"
for k, (a, b) in enumerate([(233, 220), (220, 196)]):                        # "wah wah" (dar de ombros)
    x = filt(saw(np.linspace(hz(58 - 2 * k), hz(57 - 3 * k), int(.3 * SR)), .3), 1200) * env(.3, .02, .08)
    add(music, 35.0 + k * .32, x, .35)
add(sfx, 35.3, slide(500, 230, .22), .25)                                    # glup
add(sfx, 35.8, whoosh(.75, 2500, 300), .55, pan=.4)
scream(35.8, .75, 820, 420, .55, rot=False)
add(sfx, 36.55, filt(slide(380, 110, .18), 1800), .7)                        # plop no tambor
add(sfx, 36.85, filt(noise(.08), 2500, 'high') * dec(.08, 40), .2)
add(sfx, 37.2, thump(.5, 90, 35), 1.0); add(sfx, 37.2, filt(noise(.3), 800) * dec(.3, 12), .6)
add(sfx, 37.45, beep(1500, .09), .25); add(sfx, 37.6, beep(2000, .14), .25)
motor = filt(saw(np.linspace(40, 140, int(1.6 * SR)), 1.6), 700) * env(1.6, .3, .05)
add(sfx, 37.6, motor, .35)
add(sfx, 38.45, whoosh(.9, 300, 4000), .5)                                  # zoom pra janela

# ---------- mix ----------
ir_t = T(1.6); ir = rng.standard_normal((len(ir_t), 2)) * np.exp(-ir_t / .45)[:, None]
ir[:, 0] = filt(ir[:, 0], 5000); ir[:, 1] = filt(ir[:, 1], 5000); ir /= np.sqrt((ir ** 2).sum(0))
wet = np.stack([fftconvolve(verb_send[:, c], ir[:, c])[:N] for c in range(2)], 1) * .5
mix = music * .8 + sfx + wet
mix = filt(mix.T, 25, 'high').T
mix /= np.max(np.abs(mix)) + 1e-9; mix = np.tanh(mix * 1.4) / np.tanh(1.4) * .9
f = int(.004 * SR); mix[:f] *= np.linspace(0, 1, f)[:, None]; mix[-f:] *= np.linspace(1, 0, f)[:, None]
out = os.path.join(os.path.dirname(__file__), 'mix.wav')
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', out)
