#!/usr/bin/env python3
"""
Gerador de capas · Grande Resumo
Uso:  python3 gerar_capa.py config.json
Precisa de: ffmpeg, Pillow, playwright (python) com Chromium.

O JSON descreve o vídeo; o script tira os frames, monta o template.html e salva a capa 1080x1920.
"""
import json, os, subprocess, sys, tempfile, html
from PIL import Image, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))


def frame(video, t, crop, saida, largura=None, img=None):
    """Extrai frame no tempo t (ou usa a imagem 'img'), recorta [x0,y0,x1,y1] (coordenadas 1080x1920) e salva."""
    tmp = saida + ".raw.png"
    if img:
        Image.open(img).convert("RGB").save(tmp)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", tmp], check=True)
    im = Image.open(tmp).convert("RGB")
    W, H = im.size
    if crop:
        sx, sy = W / 1080, H / 1920  # aceita vídeos de outra resolução 9:16
        x0, y0, x1, y1 = crop
        im = im.crop((int(x0 * sx), int(y0 * sy), int(x1 * sx), int(y1 * sy)))
    if largura and im.width > largura:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(1.2, 40, 2))
    im.save(saida)
    os.remove(tmp)
    return saida


def esc(s):
    return html.escape(str(s))


def main(cfg_path):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(cfg_path))
    video = os.path.join(base, cfg["video"])
    saida = os.path.join(base, cfg.get("saida", "capa.png"))
    work = tempfile.mkdtemp(prefix="capa_")

    h = cfg["heroi"]
    heroi = frame(video, h.get("t"), h.get("crop", [0, 690, 1080, 1225]), os.path.join(work, "heroi.png"), 1000,
                  os.path.join(base, h["img"]) if h.get("img") else None)

    cenas_html = []
    for i, c in enumerate(cfg["cenas"][:3]):
        p = frame(video, c.get("t"), c.get("crop", [40, 280, 1040, 1240]), os.path.join(work, f"cena{i}.png"), 600,
                  os.path.join(base, c["img"]) if c.get("img") else None)
        cenas_html.append(
            f'<div class="cena s{i+1}"><div class="n">{i+1}</div><img src="file://{p}"><p>{esc(c["rotulo"])}</p></div>')

    t1, t2 = cfg["titulo"]
    letras = len(t1 + t2)
    tam_titulo = cfg.get("tam_titulo") or max(76, min(124, int(1250 / max(letras, 1))))
    gancho = cfg["gancho"]
    tam_gancho = cfg.get("tam_gancho") or max(40, min(58, int(1050 / max(len(gancho), 1))))

    rep = {
        "COR": cfg.get("cor", "#E5172F"),
        "COR2": cfg.get("cor2", "#FFC93C"),
        "ESCURO": cfg.get("escuro", "#12030A"),
        "HEROI": "file://" + heroi,
        "LOGO": "file://" + os.path.join(AQUI, "assets", "logo.png"),
        "NUMERO": esc(cfg.get("numero", "001")),
        "KICKER": esc(cfg.get("kicker", "RESUMO COMPLETO")),
        "T1": esc(t1), "T2": esc(t2),
        "TAM_TITULO": str(tam_titulo),
        "TOP_CHIPS": str(505 + int(tam_titulo * 1.02) + 18),
        "CHIPS": "".join(f"<span>{esc(x)}</span>" for x in cfg.get("chips", [])),
        "TAG_HEROI": esc(cfg.get("tag_heroi", "ASSISTA ATÉ O FIM")),
        "DURACAO": esc(cfg.get("duracao", "2:30")),
        "CENAS": "".join(cenas_html),
        "GANCHO": esc(gancho),
        "TAM_GANCHO": str(tam_gancho),
        "STATS": "".join(f"<div><b>{esc(a)}</b><span>{esc(b)}</span></div>" for a, b in cfg.get("stats", [])),
        "RODAPE": cfg.get("rodape", "SIGA PARA <em>MAIS SÉRIES</em> ➜"),
    }
    tpl = open(os.path.join(AQUI, "template.html"), encoding="utf-8").read()
    for k, v in rep.items():
        tpl = tpl.replace("{{" + k + "}}", v)
    page = os.path.join(work, "capa.html")
    open(page, "w", encoding="utf-8").write(tpl)

    js = ("const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();"
          "const pg=await b.newPage({viewport:{width:1080,height:1920}});"
          f"await pg.goto({json.dumps('file://' + page)});await pg.waitForTimeout(800);"
          f"await pg.screenshot({{path:{json.dumps(saida)}}});await b.close();}})();")
    subprocess.run(["node", "-e", js], check=True)
    print("Capa salva em", saida)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "config.json")
