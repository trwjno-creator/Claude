"""Voice + clean generated music bed (looped with crossfades) + SFX. No audio taken from the reference."""
import json, os, subprocess, numpy as np, wave
SR = 44100; HERE = os.path.dirname(os.path.abspath(__file__)); BED = os.path.join(HERE, "bgm", "bed1.mp3")
def dec(p, ch=2):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", str(ch), "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, ch) / 32768
D = json.load(open(os.path.join(HERE, "timeline.json"))); mk = json.load(open(os.path.join(HERE, "marks.json"))); T = D["total"]; N = int(T * SR)
loop = dec(BED); voice = dec(os.path.join(HERE, "voice.wav")); sfx = dec(os.path.join(HERE, "sfx.wav"))
xf = int(0.6 * SR); step = len(loop) - xf
bed = np.zeros((N + len(loop), 2), np.float32); pos = 0
win_in = np.linspace(0, 1, xf)[:, None]; win_out = win_in[::-1]
while pos < N:
    seg = loop.copy()
    if pos > 0: seg[:xf] *= win_in
    seg[-xf:] *= win_out
    bed[pos:pos + len(seg)] += seg; pos += step
bed = bed[:N]
g = np.ones(N)
a, b = int(mk["cold_a"] * SR), int(mk["cold_b"] * SR); r = int(0.5 * SR)
g[a:a + r] = np.linspace(1, 0.15, r); g[a + r:b] = 0.15; g[b:b + r] = np.linspace(0.15, 1, r)
e = int((mk["speech_end"] + 0.3) * SR); g[e:] *= np.linspace(1, 0, N - e)  # fade out after the last line
g[:int(0.5 * SR)] *= np.linspace(0, 1, int(0.5 * SR))
bed *= g[:, None]
rms = lambda x: np.sqrt((x ** 2).mean() + 1e-12)
vv = voice[np.abs(voice).max(1) > 0.01]; bed *= rms(vv) * 10 ** (-13 / 20) / rms(bed[:int(40 * SR)])
n = min(N, len(voice), len(sfx)); mix = voice[:n] + bed[:n] + sfx[:n] * 0.9; mix /= max(1, np.abs(mix).max() / 0.95)
with wave.open(os.path.join(HERE, "mix_bed.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ok", round(n / SR, 2))
