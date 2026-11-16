import json, os, subprocess, numpy as np, wave
SR = 44100; HERE = os.path.dirname(os.path.abspath(__file__)); REF = os.path.join(HERE, "..", "ref", "ref_music.wav")
def dec(p, ch=2):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", p, "-ac", str(ch), "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32).reshape(-1, ch) / 32768
D = json.load(open(os.path.join(HERE, "timeline.json"))); mk = json.load(open(os.path.join(HERE, "marks.json"))); T = D["total"]; N = int(T * SR)
ref = dec(REF); voice = dec(os.path.join(HERE, "voice.wav")); sfx = dec(os.path.join(HERE, "sfx.wav"))
rl = len(ref) / SR; sting_len = 4.2; sting = ref[int((rl - sting_len) * SR):]
bed = np.zeros((N, 2), np.float32)
end_bed = int((mk["speech_end"] + 0.4) * SR)
src = ref[:min(end_bed, len(ref) - int(sting_len * SR))]; bed[:len(src)] = src
s0 = int((mk["speech_end"] + 0.4 - 1.0) * SR); L = min(len(sting), N - s0); fade = int(SR)
env = np.ones(L); env[:fade] = np.linspace(0, 1, fade)
bed[s0:s0 + fade] *= np.linspace(1, 0, fade)[:, None]; bed[s0 + fade:] = 0; bed[s0:s0 + L] += sting[:L] * env[:, None]
g = np.ones(N); a, b = int(mk["cold_a"] * SR), int(mk["cold_b"] * SR); r = int(0.5 * SR)
g[a:a + r] = np.linspace(1, 0.18, r); g[a + r:b] = 0.18; g[b:b + r] = np.linspace(0.18, 1, r); bed *= g[:, None]
rms = lambda x: np.sqrt((x ** 2).mean() + 1e-12)
vv = voice[np.abs(voice).max(1) > 0.01]; bed *= rms(vv) * 10 ** (-11 / 20) / rms(bed[:int(40 * SR)])
n = min(N, len(voice), len(sfx)); mix = voice[:n] + bed[:n] + sfx[:n] * 0.9; mix /= max(1, np.abs(mix).max() / 0.97)
with wave.open(os.path.join(HERE, "mix_refmusic.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype(np.int16).tobytes())
print("mix ok", round(n / SR, 2))
