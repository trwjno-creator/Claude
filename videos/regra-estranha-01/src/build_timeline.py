"""Builds timeline.json (line/word/viseme timings + scene ranges) from lines.json
and, when present, audio/<id>.json (ElevenLabs with-timestamps alignment)."""
import json, os, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TAIL = 2.0
TEMPO = 1.05

def strip_accents(c):
    return unicodedata.normalize("NFD", c)[0].lower()

def viseme(c):
    b = strip_accents(c)
    if b in "a": return "A"
    if b in "ei": return "E"
    if b in "ou": return "O"
    if b in "mbp": return "M"
    if b in "fv": return "F"
    if b.isalpha(): return "D"
    return "X"

def estimate(text):
    chars, st, en = [], [], []
    t = 0.0
    for c in text:
        d = 0.068
        if c in ",": d = 0.22
        elif c in ".?!": d = 0.38
        elif c == " ": d = 0.03
        chars.append(c); st.append(t); en.append(t + d); t += d
    return {"characters": chars, "character_start_times_seconds": st,
            "character_end_times_seconds": en}, t

def build():
    lines = json.load(open(os.path.join(HERE, "lines.json")))
    t = 0.0
    out_lines = []
    for ln in lines:
        ap = os.path.join(HERE, "audio", ln["id"] + ".json")
        if os.path.exists(ap):
            a = json.load(open(ap))
            al = dict(a["alignment"]); dur = a["duration"] / TEMPO
            al["character_start_times_seconds"] = [x / TEMPO for x in al["character_start_times_seconds"]]
            al["character_end_times_seconds"] = [x / TEMPO for x in al["character_end_times_seconds"]]
        else:
            al, dur = estimate(ln["text"])
        t += ln["gap"]
        start = t
        t += dur
        chars, cs, ce, inb = [], [], [], False
        for c, s0, e0 in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
            if c == "[": inb = True; continue
            if c == "]": inb = False; continue
            if inb: continue
            chars.append(c); cs.append(s0); ce.append(e0)
        while chars and chars[0].isspace(): chars.pop(0); cs.pop(0); ce.pop(0)
        lead = cs[0] if cs else 0.0
        start -= lead; t -= lead  # align so first spoken char lands right after the gap
        # words
        words, cur = [], None
        for c, s, e in zip(chars, cs, ce):
            if c.isspace():
                if cur: words.append(cur); cur = None
                continue
            if cur is None: cur = {"w": "", "s": s + start, "e": e + start}
            cur["w"] += c; cur["e"] = e + start
        if cur: words.append(cur)
        # visemes (merged)
        vis = []
        for c, s, e in zip(chars, cs, ce):
            v = viseme(c)
            if vis and vis[-1]["v"] == v and abs(vis[-1]["e"] - (s + start)) < 0.02:
                vis[-1]["e"] = e + start
            else:
                vis.append({"v": v, "s": s + start, "e": e + start})
        sm = []
        for v in vis:
            if sm and (v["e"] - v["s"] < 0.07 or sm[-1]["e"] - sm[-1]["s"] < 0.07) and v["v"] != "X":
                sm[-1]["e"] = v["e"]
                if sm[-1]["v"] == "X": sm[-1]["v"] = v["v"]
            else:
                sm.append(dict(v))
        vis = sm
        out_lines.append({"id": ln["id"], "who": ln["who"], "scene": ln["scene"], "gap": ln["gap"],
                          "text": ln["text"], "start": start, "end": start + dur, "dur": dur,
                          "words": words, "visemes": vis})
    total = out_lines[-1]["end"] + TAIL
    scenes, order = {}, []
    for ln in out_lines:
        if ln["scene"] not in scenes:
            order.append(ln["scene"])
            scenes[ln["scene"]] = {"id": ln["scene"], "first": ln["start"],
                                   "lead": min(ln["gap"] * 0.6, 0.6)}
    res = []
    for i, sid in enumerate(order):
        s = scenes[sid]
        start = 0.0 if i == 0 else s["first"] - s["lead"]
        res.append({"id": sid, "start": start})
    for i in range(len(res)):
        res[i]["end"] = res[i + 1]["start"] if i + 1 < len(res) else total
    data = {"lines": out_lines, "scenes": res, "total": total, "fps": 30}
    json.dump(data, open(os.path.join(HERE, "timeline.json"), "w"), ensure_ascii=False, indent=1)
    print("total %.2fs" % total)
    for s in res: print(s["id"], "%.2f-%.2f" % (s["start"], s["end"]))

if __name__ == "__main__":
    build()
