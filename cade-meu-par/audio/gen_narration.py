"""Narração estilo trailer de cinema para "Cadê Meu Par?".
Cada fala é sintetizada (edge-tts, pt-BR), aparada, acelerada se não couber na janela
da cena e posicionada no tempo. Gera:
  audio/narration.wav  (40 s, 48 kHz mono, voz seca)
  subs.js              (tempo de cada palavra, para as legendas animadas em anim.js)
"""
import asyncio, json, os, ssl, subprocess, sys
import numpy as np, soundfile as sf
import edge_tts, edge_tts.communicate as ec

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(D)
ca = '/root/.ccr/ca-bundle.crt'
if os.path.exists(ca):
    ec._SSL_CTX = ssl.create_default_context(cafile=ca)

SR, DUR = 48000, 40.0
NARR = ("pt-BR-AntonioNeural", "+6%", "-7Hz")
PAR = ("pt-BR-FranciscaNeural", "-12%", "+0Hz")
# (início, fim máximo, texto, voz, legenda?)
LINES = [
    (0.05, 1.95, "Toda semana, uma meia desaparece.", NARR, True),
    (2.25, 4.50, "E ninguém nunca perguntou pra onde elas vão.", NARR, True),
    (6.90, 9.30, "Bem-vinda ao Reino das Meias Perdidas.", NARR, False),  # o título na tela já é a legenda
    (9.55, 12.65, "Tampas, elásticos... e o seu fone sem fio.", NARR, True),
    (14.10, 15.85, "Mas ela tinha um plano.", NARR, True),
    (16.10, 17.85, "Escalar o impossível.", NARR, True),
    (18.10, 19.85, "Enfrentar o terror.", NARR, True),
    (20.15, 21.10, "E voar...", NARR, True),
    (22.15, 23.90, "de volta pro grande amor.", NARR, True),
    (25.30, 27.40, "Até que... ela encontrou seu par.", NARR, True),
    (28.15, 29.80, "Faz três semanas...", PAR, False),
    (30.45, 32.25, "Tem história que não tem final feliz.", NARR, True),
    (32.45, 33.60, "E sabe o pior?", NARR, True),
    (35.95, 37.45, "Ela não foi a primeira.", NARR, True),
    (38.00, 39.75, "E não vai ser a última.", NARR, True),
]

async def synth(text, voice, rate, pitch, path):
    for attempt in range(5):
        try:
            c = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, boundary="WordBoundary")
            words = []
            with open(path, "wb") as f:
                async for ch in c.stream():
                    if ch["type"] == "audio":
                        f.write(ch["data"])
                    elif ch["type"] == "WordBoundary":
                        words.append([ch["text"], ch["offset"] / 1e7, (ch["offset"] + ch["duration"]) / 1e7])
            return words
        except Exception as e:  # rede instável: tenta de novo
            print("retry", e); await asyncio.sleep(2 * (attempt + 1))
    raise SystemExit("TTS falhou")

def load(path, tempo=1.0):
    af = ["-af", f"atempo={tempo:.4f}"] if abs(tempo - 1) > 1e-3 else []
    out = path + ".wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, *af, "-ar", str(SR), "-ac", "1", out], check=True)
    a, _ = sf.read(out); return a

async def main():
    tmp = os.path.join(D, "tts"); os.makedirs(tmp, exist_ok=True)
    buf = np.zeros(int(SR * DUR)); subs = []
    for i, (t0, t1, text, (voice, rate, pitch), sub) in enumerate(LINES):
        mp3 = os.path.join(tmp, f"l{i:02d}.mp3")
        words = await synth(text, voice, rate, pitch, mp3)
        a = load(mp3)
        idx = np.where(np.abs(a) > 0.01)[0]
        s0, s1 = max(0, idx[0] / SR - .02), idx[-1] / SR + .05
        speech, win = s1 - s0, t1 - t0
        tempo = 1.0
        if speech > win:
            tempo = speech / win
            if tempo > 1.35: print(f"AVISO: fala {i} muito longa ({speech:.2f}s > {win:.2f}s)"); tempo = 1.35
            a = load(mp3, tempo)
        seg = a[int(s0 / tempo * SR): int(s1 / tempo * SR)]
        f = int(.01 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
        j = int(t0 * SR); n = min(len(seg), len(buf) - j); buf[j:j + n] += seg[:n]
        print(f"{i:2d} {t0:5.2f}s  fala {speech / tempo:4.2f}s / janela {win:4.2f}s  tempo x{tempo:.2f}  {text}")
        if sub:
            for k, (w, w0, w1) in enumerate(words):
                subs.append({"line": i, "w": w, "t0": round(t0 + (w0 - s0) / tempo, 3), "t1": round(t0 + (w1 - s0) / tempo, 3)})
    sf.write(os.path.join(D, "narration.wav"), buf, SR)
    with open(os.path.join(ROOT, "subs.js"), "w") as f:
        f.write("// gerado por audio/gen_narration.py — tempo de cada palavra da narração\n")
        f.write("window.SUBS = " + json.dumps(subs, ensure_ascii=False) + ";\n")
    print("palavras:", len(subs))

asyncio.run(main())
