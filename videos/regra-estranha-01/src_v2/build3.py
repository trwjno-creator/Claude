"""Compress long silences inside each take, apply tempo, sequence takes tightly,
and write timeline.json (+ voice.wav). Alignment times are remapped through every edit."""
import json, os, subprocess, unicodedata, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100
TEMPO = {"narr": 0.96, "pedro": 1.0, "vo": 1.0}
MAX_PAUSE = 0.24          # longest silence kept inside a take (reference style)
DRAMA = {"frio": 0.55, "ele esquenta": 0.6, "só às vezes": 0.4}  # longer breath before these phrases
GAP = {"narr>narr": 0.4, "narr>pedro": 0.35, "pedro>narr": 0.45, "narr>vo": 0.35, "vo>narr": 0.45}
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

TARGET = {".": 0.36, "!": 0.36, "?": 0.38, ":": 0.3, ",": 0.17}
CAP_PLAIN = 0.2
DRAMA2 = {"frio": 0.85, "ele esquenta": 0.8, "só às vezes": 0.45, "foi aí": 0.6, "hoje,": 0.6}
def process_take(tk):
    a = json.load(open(os.path.join(HERE, "audio", tk["id"] + ".json")))
    x = decode(os.path.join(HERE, "audio", tk["id"] + ".mp3"))
    chars, cs, ce = clean_alignment(a["alignment"])
    hop = SR // 100; n = len(x) // hop
    db = 20 * np.log10(np.sqrt((x[: n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-9)
    speech = np.median(db[db > np.percentile(db, 30)]); quiet = db < speech - 26
    # words with original times
    words, cur = [], None
    for i, c in enumerate(chars):
        if c.isspace():
            if cur: words.append(cur); cur = None
            continue
        if cur is None: cur = {"w": "", "s": cs[i], "e": ce[i]}
        cur["w"] += c; cur["e"] = ce[i]
    if cur: words.append(cur)
    text_after = lambda k: " ".join(w["w"].lower() for w in words[k:k + 3])
    ops = []  # (pos, delta): delta<0 cut |delta| starting at pos; delta>0 insert silence at pos
    # leading / trailing silence
    lead_q = 0
    while lead_q < n and quiet[lead_q]: lead_q += 1
    if lead_q / 100 > 0.05: ops.append((0.0, -(lead_q / 100 - 0.04)))
    for k in range(len(words) - 1):
        w0, w1 = words[k], words[k + 1]
        lo, hi = int(w0["e"] * 100) - 8, int(w1["s"] * 100) + 8
        best, bs, run, rs = 0, None, 0, None
        for f in range(max(lo, 0), min(hi, n)):
            if quiet[f]:
                if run == 0: rs = f
                run += 1
                if run > best: best, bs = run, rs
            else: run = 0
        sil = best / 100 if best >= 3 else 0.0
        pos = (bs / 100 if best >= 3 else (w0["e"] + w1["s"]) / 2)
        p = w0["w"][-1]
        tgt = TARGET.get(p, None)
        nxt = text_after(k + 1)
        for ph, v in DRAMA2.items():
            if nxt.startswith(ph): tgt = max(tgt or 0, v)
        if tgt is None:
            if sil > CAP_PLAIN: ops.append((pos + CAP_PLAIN / 2, -(sil - CAP_PLAIN)))
            continue
        if sil > tgt: ops.append((pos + tgt / 2, -(sil - tgt)))
        elif tgt - sil > 0.02: ops.append((pos + sil / 2, tgt - sil))
    ops.sort()
    # render edit list
    out, tm, t_prev = [], [], 0.0   # tm: list of (orig_start, orig_end, new_start)
    newt = 0.0
    fade = int(0.006 * SR)
    def seg(s, e):
        y = x[int(s * SR): int(e * SR)].copy()
        if len(y) > 2 * fade: y[:fade] *= np.linspace(0, 1, fade); y[-fade:] *= np.linspace(1, 0, fade)
        return y
    for pos, d in ops:
        if pos < t_prev: pos = t_prev
        out.append(seg(t_prev, pos)); tm.append((t_prev, pos, newt)); newt += pos - t_prev
        if d < 0: t_prev = pos - d
        else:
            out.append(np.zeros(int(d * SR), np.float32)); newt += d; t_prev = pos
    out.append(seg(t_prev, len(x) / SR)); tm.append((t_prev, len(x) / SR, newt))
    y = np.concatenate(out)
    def tmap(t):
        for s0, e0, ns in tm:
            if t <= e0: return ns + max(0.0, t - s0)
        return tm[-1][2] + (tm[-1][1] - tm[-1][0])
    tempo = TEMPO[tk["who"]]
    raw = os.path.join(HERE, "audio", tk["id"] + "_edit.wav")
    with wave.open(raw, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes())
    fin = os.path.join(HERE, "audio", tk["id"] + "_final.wav")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", raw, "-af", f"atempo={tempo}", "-ar", str(SR), fin], check=True)
    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", fin]).decode())
    cs2 = [tmap(t) / tempo for t in cs]; ce2 = [tmap(t) / tempo for t in ce]
    return chars, cs2, ce2, dur, len(x) / SR - len(y) / SR

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
        print(f"{tk['id']}: {dur:.2f}s (silêncio removido(-)/adicionado(+) {removed:.2f}s) start {start:.2f}")
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
