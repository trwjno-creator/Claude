"""Synthesizes a soft piano score + simple SFX following timeline.json -> music.wav (44.1k stereo)."""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
D = json.load(open(os.path.join(HERE, "timeline.json")))
T = D["total"]
N = int(T * SR) + SR
mus = np.zeros(N); sfx = np.zeros(N)
rng = np.random.default_rng(7)

def line(i): return next(l for l in D["lines"] if l["id"] == i)
def scene(i): return next(s for s in D["scenes"] if s["id"] == i)
def word(lid, pre):
    for w in line(lid)["words"]:
        if w["w"].lower().strip(".,?!").startswith(pre): return w["s"]
    return line(lid)["start"]

def note(freq, dur, amp=0.2):
    t = np.arange(int(dur * SR)) / SR
    env = np.exp(-t * 2.2) * np.minimum(1, t * 200)
    sig = sum(np.sin(2 * np.pi * freq * h * t) * (0.6 ** (h - 1)) for h in (1, 2, 3, 4))
    return sig * env * amp

def add(buf, start, sig):
    i = int(start * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i]; buf[i:i + len(sig)] += sig

def hz(n): return 440 * 2 ** ((n - 69) / 12)
# progression Am F C G (MIDI)
CH = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
MEL = [76, 74, 72, 71, 72, 74, 76, 79]
beat = 60 / 72

def play(a, b, amp=0.12, mel=True):
    t = a; k = 0
    while t < b:
        ch = CH[(k // 4) % 4]
        if k % 4 == 0:
            for n in ch: add(mus, t, note(hz(n - 12), beat * 4, amp * 0.8))
        add(mus, t, note(hz(ch[k % 3]), beat * 1.5, amp * 0.6))
        if mel and k % 2 == 0: add(mus, t + beat * 0.5, note(hz(MEL[(k // 2) % 8]), beat * 2, amp * 0.5))
        t += beat; k += 1

s6 = scene("S6"); s7 = scene("S7"); s8 = scene("S8")
# light bed until hospital, music stops before "Frio", swell from "porque"
play(0, scene("S3")["start"], 0.10, mel=True)
play(scene("S3")["start"], s6["start"], 0.12, mel=True)
play(s6["start"], line("L9")["end"] - 0.2, 0.09, mel=False)
play(word("L11", "porque") - 0.3, T - 1.0, 0.15, mel=True)

# fades: silence window
def gain_ramp(buf, a, b, g0, g1):
    i, j = int(a * SR), int(b * SR); buf[i:j] *= np.linspace(g0, g1, max(1, j - i))
gain_ramp(mus, line("L9")["end"] - 0.6, line("L9")["end"], 1, 0)
mus[int(line("L9")["end"] * SR): int((word("L11", "porque") - 0.3) * SR)] = 0
gain_ramp(mus, T - 2.0, T, 1, 0)

# SFX
def whoosh(at, dur=0.6, amp=0.25):
    n = int(dur * SR); x = rng.standard_normal(n)
    # crude band sweep via moving average of varying size
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    y = np.convolve(x, np.ones(30) / 30, mode="same") * env * amp * 3
    add(sfx, at, y)
def plim(at, f=1568, amp=0.18):
    t = np.arange(int(0.6 * SR)) / SR
    add(sfx, at, (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 7) * amp)
def heartbeat(at, amp=0.6):
    for off in (0, 0.22):
        t = np.arange(int(0.25 * SR)) / SR
        add(sfx, at + off, np.sin(2 * np.pi * 55 * t) * np.exp(-t * 18) * amp)
def wind(a, b, amp=0.12):
    n = int((b - a) * SR); x = rng.standard_normal(n)
    y = np.convolve(x, np.ones(200) / 200, mode="same") * 12
    env = np.minimum(1, np.minimum(np.arange(n) / (0.3 * SR), (n - np.arange(n)) / (0.4 * SR)))
    add(sfx, a, y * env * amp)

whoosh(line("L2")["start"] - 0.4)
for w in ("júlia", "pedro", "olhar"): plim(word("L3", w), 1568 if w != "olhar" else 2093)
plim(scene("S2")["start"] + 0.3, 1318, 0.1)
whoosh(line("L5")["start"] - 0.9, 0.5, 0.15)
for i in range(6): add(sfx, scene("S4")["start"] + i * 0.45, note(hz(96), 0.08, 0.05))  # tick
plim(word("L8", "põe"), 1046, 0.12)
for k in range(8): heartbeat(s7["start"] + 0.1 + k * 0.85, 0.5)
wind(s7["start"], s8["start"] + 1.0, 0.16)
plim(word("L12", "desde"), 1318, 0.12)
plim(word("L13", "esquenta"), 1760, 0.2)

mix = mus * 0.9 + sfx
mix /= max(1.0, np.abs(mix).max() / 0.9)
st = np.stack([mix, mix], axis=1)
pcm = (st * 32767).astype(np.int16)
with wave.open(os.path.join(HERE, "music.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("music.wav", round(T, 2), "s")
