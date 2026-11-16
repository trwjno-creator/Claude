"""Compress long silences inside each take, apply tempo, sequence takes tightly,
and write timeline.json (+ voice.wav). Alignment times are remapped through every edit."""
import json, os, subprocess, unicodedata, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
TEMPO = {"narr": 1.0, "pedro": 1.0, "vo": 1.0}
MAX_PAUSE = 0.24          # longest silence kept inside a take (reference style)
DRAMA = {"frio": 0.55, "ele esquenta": 0.6, "só às vezes": 0.4}  # longer breath before these phrases
GAP = {"narr>narr": 0.18, "narr>pedro": 0.22, "pedro>narr": 0.25, "narr>vo": 0.25, "vo>narr": 0.25}
TAIL = 2.2

def strip_acc(c): return unicodedata.normalize("NFD", c)[0].lower()
def viseme(c):
    b = strip_acc(c)
    if b == "a": return "A"
    if b in "ei": return "E"
    if b in "ou": return "O"
    if b in "mbp": return "M"
    if b in "fv": return "F"
    if b.isalpha(): return "D"
    return "X"

def decode(path):
    raw = subprocess.check_output(["ffmpeg", "-loglevel", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"])
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768

def clean_alignment(al):
    chars, cs, ce, inb = [], [], [], False
    for c, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if c == "[": inb = True; continue
        if c == "]": inb = False; continue
        if inb: continue
        chars.append(c); cs.append(s); ce.append(e)
    while chars and chars[0].isspace(): chars.pop(0); cs.pop(0); ce.pop(0)
    return chars, cs, ce

def process_take(tk):
    a = json.load(open(os.path.join(HERE, "audio", tk["id"] + ".json")))
    x = decode(os.path.join(HERE, "audio", tk["id"] + ".mp3"))
    chars, cs, ce = clean_alignment(a["alignment"])
    text = "".join(chars).lower()
    # silence detection (10ms frames)
    hop = SR // 100
    n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    speech = np.median(db[db > np.percentile(db, 30)])
    quiet = db < speech - 26
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            runs.append((i / 100, j / 100)); i = j
        else: i += 1
    # allowed pause per run: default MAX_PAUSE, more before drama phrases; trim leading/trailing silence
    first_speech = cs[0] if cs else 0
    last_speech = ce[-1] if ce else len(x) / SR
    cuts = []  # (start, end) segments of audio to remove
    for (s, e) in runs:
        if e <= first_speech + 0.02:
            cuts.append((s, max(s, e - 0.04))); continue
        if s >= last_speech - 0.02:
            cuts.append((min(e, s + 0.12), e)); continue
        dur = e - s
        allow = MAX_PAUSE
        # which char follows this silence?
        nxt = next((k for k, t in enumerate(cs) if t >= e - 0.05), None)
        if nxt is not None:
            ahead = text[nxt: nxt + 14]
            for ph, v in DRAMA.items():
                if ahead.startswith(ph): allow = v
        if dur > allow:
            mid = s + allow / 2
            cuts.append((mid, mid + (dur - allow)))
    cuts.sort()
    # build edited audio + time map
    keep, t_prev = [], 0.0
    for s, e in cuts:
        if s > t_prev: keep.append((t_prev, s))
        t_prev = max(t_prev, e)
    keep.append((t_prev, len(x) / SR))
    pieces, fade = [], int(0.006 * SR)
    for s, e in keep:
        seg = x[int(s * SR): int(e * SR)].copy()
        if len(seg) > 2 * fade:
            seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        pieces.append(seg)
    y = np.concatenate(pieces)
    def tmap(t):
        out = 0.0
        for s, e in keep:
            if t <= s: return out
            if t <= e: return out + (t - s)
            out += e - s
        return out
    tempo = TEMPO[tk["who"]]
    raw = os.path.join(HERE, "audio", tk["id"] + "_edit.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    fin = os.path.join(HERE, "audio", tk["id"] + "_final.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", f"atempo={tempo}", "-ar", str(SR), fin], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fin]).decode())
    cs2 = [tmap(t) / tempo for t in cs]; ce2 = [tmap(t) / tempo for t in ce]
    removed = len(x) / SR - len(y) / SR
    return chars, cs2, ce2, dur, removed

def main():
    S = json.load(open(os.path.join(HERE, "script.json")))
    t, prev, lines = 0.3, None, []
    for tk in S["takes"]:
        chars, cs, ce, dur, removed = process_take(tk)
        if prev: t += GAP.get(f"{prev}>{tk['who']}", 0.2)
        start = t - (cs[0] if cs else 0) + 0.0
        words, cur = [], None
        for c, s, e in zip(chars, cs, ce):
            if c.isspace():
                if cur: words.append(cur); cur = None
                continue
            if cur is None: cur = {"w": "", "s": s + start, "e": e + start}
            cur["w"] += c; cur["e"] = e + start
        if cur: words.append(cur)
        vis = []
        for c, s, e in zip(chars, cs, ce):
            v = viseme(c)
            if vis and vis[-1]["v"] == v: vis[-1]["e"] = e + start
            else: vis.append({"v": v, "s": s + start, "e": e + start})
        sm = []
        for v in vis:
            if sm and (v["e"] - v["s"] < 0.07 or sm[-1]["e"] - sm[-1]["s"] < 0.07) and v["v"] != "X":
                sm[-1]["e"] = v["e"]
                if sm[-1]["v"] == "X": sm[-1]["v"] = v["v"]
            else: sm.append(dict(v))
        end = start + dur
        lines.append({"id": tk["id"], "who": tk["who"], "start": start, "end": end, "dur": dur,
                      "speechEnd": words[-1]["e"], "words": words, "visemes": sm})
        print(f"{tk['id']}: {dur:.2f}s (silêncio removido {removed:.2f}s) start {start:.2f}")
        t = words[-1]["e"]; prev = tk["who"]
    total = lines[-1]["speechEnd"] + TAIL
    # scenes from phrases
    def find(take, phrase):
        L = next(l for l in lines if l["id"] == take)
        toks = [p.lower().strip(".,?!:") for p in phrase.split()]
        ws = [w["w"].lower().strip(".,?!:") for w in L["words"]]
        for i in range(len(ws)):
            if ws[i: i + len(toks)] == toks: return L["words"][i]["s"]
        raise SystemExit(f"phrase not found: {phrase}")
    scenes = []
    for k, sc in enumerate(S["scenes"]):
        st = 0.0 if k == 0 else find(sc["take"], sc["phrase"]) - 0.12
        scenes.append({"id": sc["id"], "start": st})
    for i in range(len(scenes)): scenes[i]["end"] = scenes[i + 1]["start"] if i + 1 < len(scenes) else total
    json.dump({"lines": lines, "scenes": scenes, "total": total, "fps": 30}, open(os.path.join(HERE, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    # voice mix
    inputs, filt = [], []
    for i, l in enumerate(lines):
        inputs += ["-i", os.path.join(HERE, "audio", l["id"] + "_final.wav")]
        ms = int(round(l["start"] * 1000))
        filt.append(f"[{i}:a]aformat=channel_layouts=stereo,volume={1.0 if l['who']=='narr' else 1.1},adelay={ms}|{ms}[a{i}]")
    filt.append("".join(f"[a{i}]" for i in range(len(lines))) + f"amix=inputs={len(lines)}:normalize=0:duration=longest,apad=whole_dur={total:.2f}[o]")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", *inputs, "-filter_complex", ";".join(filt), "-map", "[o]", "-t", f"{total:.2f}", os.path.join(HERE, "voice.wav")], check=True)
    nw = sum(len(l["words"]) for l in lines)
    print(f"total {total:.2f}s | {nw} palavras | {nw / (lines[-1]['speechEnd'] - lines[0]['start']) * 60:.0f} palavras/min")
    for s in scenes: print(f"  {s['id']:7s} {s['start']:6.2f} - {s['end']:6.2f}")

if __name__ == "__main__":
    main()
