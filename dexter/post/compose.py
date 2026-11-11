# -*- coding: utf-8 -*-
# Compositor final: frames 3D -> 1080x1920 + legendas palavra-a-palavra, etiquetas, titulos, icones, transicoes.
# uso: python3 compose.py <frames_dir> <out_video_noaudio.mp4> [--only s01,s02] [--still s01:30 out.png]
import os, sys, json, math, re, subprocess, random
from functools import lru_cache
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from script import HIGHLIGHT
from overlays import O

W, H, FPS = 1080, 1920, 30
FONTS = f"{ROOT}/fonts"
tl = json.load(open(f"{ROOT}/audio/timeline.json"))
SHOTS = tl['shots']

def font(name, size, var):
    f = ImageFont.truetype(f"{FONTS}/{name}", size)
    f.set_variation_by_name(var)
    return f

def hex2rgb(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def dark_text(color):
    r, g, b = hex2rgb(color)
    return (0.299 * r + 0.587 * g + 0.114 * b) > 170

OUT = (18, 18, 24)

# ------------------------------------------------------------------ elementos (cacheados como RGBA)
@lru_cache(maxsize=512)
def word_img(word, yellow):
    f = font('Fredoka.ttf', 104, b'Bold')
    pad = 30
    bb = f.getbbox(word, stroke_width=11)
    w, h = bb[2] - bb[0] + pad * 2, bb[3] - bb[1] + pad * 2
    im = Image.new('RGBA', (w, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # sombra
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    ds.text((pad - bb[0] + 4, pad - bb[1] + 9), word, font=f, fill=(0, 0, 0, 150), stroke_width=11, stroke_fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(4))
    im.alpha_composite(sh)
    fill = (255, 214, 64) if yellow else (255, 255, 255)
    d.text((pad - bb[0], pad - bb[1]), word, font=f, fill=fill, stroke_width=11, stroke_fill=OUT)
    return im

@lru_cache(maxsize=128)
def pill_img(text, color, blink_dot=False):
    f = font('Montserrat.ttf', 42, b'ExtraBold')
    tb = f.getbbox(text)
    th = tb[3] - tb[1]
    hgt = 84; dot = 30
    w = 34 + dot + 20 + (tb[2] - tb[0]) + 38
    im = Image.new('RGBA', (w + 16, hgt + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8 + 0, 8 + 6, 8 + w, 8 + hgt + 4), radius=hgt // 2, fill=(0, 0, 0, 90))
    d.rounded_rectangle((8, 8, 8 + w, 8 + hgt), radius=hgt // 2, fill=color, outline=OUT, width=6)
    tc = OUT if dark_text(color) else (255, 255, 255)
    cy = 8 + hgt // 2
    d.ellipse((8 + 30, cy - dot // 2, 8 + 30 + dot, cy + dot // 2), fill=(255, 255, 255) if not dark_text(color) else (255, 255, 255), outline=OUT, width=5)
    d.text((8 + 30 + dot + 20 - tb[0], cy - th // 2 - tb[1]), text, font=f, fill=tc)
    return im

@lru_cache(maxsize=128)
def tag_img(text, color):
    f = font('Montserrat.ttf', 34, b'ExtraBold')
    tb = f.getbbox(text)
    w, hgt = tb[2] - tb[0] + 44, 64
    im = Image.new('RGBA', (w + 12, hgt + 30), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 6 + w, 6 + hgt), radius=hgt // 2, fill=color, outline=OUT, width=5)
    cx = 6 + w // 2
    d.polygon([(cx - 12, 6 + hgt - 3), (cx + 12, 6 + hgt - 3), (cx, 6 + hgt + 18)], fill=color, outline=None)
    d.line([(cx - 13, 6 + hgt - 1), (cx, 6 + hgt + 20), (cx + 13, 6 + hgt - 1)], fill=OUT, width=5)
    tc = OUT if dark_text(color) else (255, 255, 255)
    d.text((6 + 22 - tb[0], 6 + hgt // 2 - (tb[3] - tb[1]) // 2 - tb[1]), text, font=f, fill=tc)
    return im

@lru_cache(maxsize=128)
def head_img(text, color, size, sub=None):
    f = font('MontserratItalic.ttf', size, b'Black Italic')
    sw = max(8, size // 9)
    lines = [text]
    if f.getlength(text) > W - 120:
        words = text.split(); lines = []; cur = ''
        for w_ in words:
            if f.getlength((cur + ' ' + w_).strip()) > W - 140:
                lines.append(cur); cur = w_
            else:
                cur = (cur + ' ' + w_).strip()
        lines.append(cur)
    lh = int(size * 1.08)
    wmax = int(max(f.getlength(l) for l in lines)) + sw * 2 + 40
    fs = font('Montserrat.ttf', int(size * 0.36), b'Black') if sub else None
    hsub = int(size * 0.5) if sub else 0
    im = Image.new('RGBA', (wmax, lh * len(lines) + sw * 2 + 30 + hsub), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        lw = f.getlength(l)
        x = (wmax - lw) / 2; y = 10 + i * lh
        d.text((x + 5, y + 9), l, font=f, fill=(0, 0, 0, 120), stroke_width=sw, stroke_fill=(0, 0, 0, 120))
        d.text((x, y), l, font=f, fill=color, stroke_width=sw, stroke_fill=OUT)
    if sub:
        sw2 = max(5, size // 18)
        lw = fs.getlength(sub)
        d.text(((wmax - lw) / 2, 10 + lh * len(lines) + 2), sub, font=fs, fill=color, stroke_width=sw2, stroke_fill=OUT)
    return im

_emoji_font = None
@lru_cache(maxsize=64)
def emoji_img(e, size=120):
    global _emoji_font
    e = e.replace('️', '')
    if _emoji_font is None:
        _emoji_font = ImageFont.truetype('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', 109)
    im = Image.new('RGBA', (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), e, font=_emoji_font, embedded_color=True)
    bb = im.getbbox()
    if bb: im = im.crop(bb)
    s = size / max(im.size)
    im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    # contorno branco suave + sombra
    pad = 16
    out = Image.new('RGBA', (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    a = im.split()[3]
    glow = Image.new('RGBA', out.size, (0, 0, 0, 0)); glow.paste((0, 0, 0, 110), (pad + 3, pad + 7), a)
    glow = glow.filter(ImageFilter.GaussianBlur(5))
    out.alpha_composite(glow); out.alpha_composite(im, (pad, pad))
    return out

@lru_cache(maxsize=32)
def bar_img(text, color, fill_frac_q):
    w, hgt = 780, 150
    im = Image.new('RGBA', (w + 12, hgt + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 6 + w, 6 + hgt), radius=50, fill=(255, 255, 255), outline=OUT, width=6)
    f = font('Montserrat.ttf', 34, b'ExtraBold')
    d.text((50, 28), text, font=f, fill=OUT)
    d.rounded_rectangle((44, 86, 44 + w - 76, 86 + 36), radius=18, fill=(225, 225, 232), outline=OUT, width=4)
    fw = int((w - 76) * fill_frac_q / 100)
    if fw > 20:
        d.rounded_rectangle((44, 86, 44 + fw, 86 + 36), radius=18, fill=color, outline=OUT, width=4)
    return im

@lru_cache(maxsize=64)
def check_row(emoji, text, done, w=640):
    hgt = 104
    im = Image.new('RGBA', (w + 12, hgt + 12), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, 6 + w, 6 + hgt), radius=34, fill=(255, 255, 255), outline=OUT, width=6)
    em = emoji_img(emoji, 64)
    im.alpha_composite(em, (22, 6 + (hgt - em.height) // 2))
    f = font('Montserrat.ttf', 40, b'ExtraBold')
    d.text((118, 6 + hgt // 2 - 24), text, font=f, fill=OUT)
    if done:
        cx, cy = 6 + w - 58, 6 + hgt // 2
        d.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(47, 191, 95), outline=OUT, width=5)
        d.line([(cx - 14, cy + 1), (cx - 3, cy + 12), (cx + 16, cy - 12)], fill=(255, 255, 255), width=8)
    return im

# ------------------------------------------------------------------ util
def ease_pop(k, dur=7, over=1.18):
    """escala de pop-in: 0 -> over -> 1"""
    if k < 0: return 0
    if k >= dur: return 1.0
    u = k / dur
    if u < 0.6: return over * (u / 0.6) ** 0.7
    return over + (1 - over) * ((u - 0.6) / 0.4)

def paste_center(base, im, cx, cy, scale=1.0, alpha=1.0):
    if scale <= 0.01 or alpha <= 0: return
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    if alpha < 1:
        im = im.copy(); a = im.split()[3].point(lambda v: int(v * alpha)); im.putalpha(a)
    x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    base.alpha_composite(im, (max(0, x), max(0, y)), (max(0, -x), max(0, -y)))

def paste_left(base, im, x, cy, scale=1.0):
    if scale <= 0.01: return
    w0 = im.width
    if abs(scale - 1) > 0.01:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    base.alpha_composite(im, (int(x + (w0 - im.width) / 2 * 0), int(cy - im.height / 2)))

def norm(w):
    return re.sub(r"[^\wÀ-ÿ]", "", w).lower()

def resolve(sh, at, n):
    """retorna frame local (0-based) a partir da especificacao"""
    if isinstance(at, (int, float)):
        return int(round(at * FPS))
    if at.startswith('frame:'):
        return int(float(at[6:]) * n) - 1
    word = at[2:]; occ = 1
    if '#' in word:
        word, occ = word.split('#'); occ = int(occ)
    cnt = 0
    for wd in sh['words']:
        if norm(wd['w']) == norm(word):
            cnt += 1
            if cnt == occ:
                return int(round((wd['t0'] - sh['v0']) * FPS))
    raise ValueError(f"palavra nao encontrada {sh['id']} {at}")

# ------------------------------------------------------------------ legenda
# juncoes de palavras na legenda (ex.: "sessenta e sete" -> "67")
MERGE = [(('sessenta', 'e', 'sete'), '67')]
ALLW = []
for sh in SHOTS:
    ws = sh['words']; i = 0
    while i < len(ws):
        done = False
        for seq, rep in MERGE:
            n = len(seq)
            if [re.sub(r"[^\wÀ-ÿ]", "", w['w']).lower() for w in ws[i:i + n]] == list(seq):
                ALLW.append({'w': rep, 't0': ws[i]['t0'], 't1': ws[i + n - 1]['t1']}); i += n; done = True; break
        if not done:
            ALLW.append(ws[i]); i += 1
for i, wd in enumerate(ALLW):
    nxt = ALLW[i + 1]['t0'] if i + 1 < len(ALLW) else wd['t1'] + 0.6
    wd['show_until'] = min(nxt, wd['t1'] + 0.55)

def caption_at(t):
    for wd in ALLW:
        if wd['t0'] - 0.02 <= t < wd['show_until']:
            return wd
    return None

FIX = {'póve': 'POV', 'dôuks': 'Doakes'}

def disp_word(w):
    if norm(w) in FIX:
        return FIX[norm(w)]
    s = w.strip()
    s = re.sub(r"^[\"'“”(]+|[\"'“”).,:;!?]+$", "", s)
    if s.upper() in ('POV', 'CBI', 'FBI'):
        return s.upper()
    return s[:1].upper() + s[1:]

def is_hl(w):
    return norm(w) in HIGHLIGHT

# ------------------------------------------------------------------ transicao
TCOL = [(255, 210, 63), (79, 209, 255), (255, 95, 162), (255, 255, 255), (120, 230, 120)]
TR = 4  # frames de cada lado do corte

def band_mask(p, angle_deg=-62):
    """mascara: 1 = mostra proxima cena. p em 0..1 varre da esquerda-baixo p/ direita-cima"""
    yy, xx = np.mgrid[0:H:4, 0:W:4]
    a = math.radians(angle_deg)
    proj = (xx * math.cos(a) - yy * math.sin(a))
    mn, mx = proj.min(), proj.max()
    d = (proj - mn) / (mx - mn)
    return d, p

# ------------------------------------------------------------------ frame
def load_shot_frame(frames_dir, sid, k, n):
    k = max(1, min(n, k))
    p = f"{frames_dir}/{sid}/{k:04d}.png"
    im = Image.open(p).convert('RGB')
    # reducao de ruido (granulado das sombras suaves do EEVEE) antes de ampliar
    arr = cv2.fastNlMeansDenoisingColored(np.asarray(im)[:, :, ::-1].copy(), None, 4, 4, 5, 15)
    im = Image.fromarray(arr[:, :, ::-1].copy())
    if im.size != (W, H):
        im = im.resize((W, H), Image.LANCZOS)
    return im

GRADE_VIG = None
def grade(im):
    global GRADE_VIG
    im = ImageEnhance.Color(im).enhance(1.12)
    im = ImageEnhance.Contrast(im).enhance(1.04)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2))
    if GRADE_VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
        GRADE_VIG = np.clip(1 - 0.28 * np.clip(r - 0.45, 0, 1) ** 1.6, 0, 1)[..., None]
    a = (np.asarray(im).astype(np.float32) * GRADE_VIG).clip(0, 255).astype(np.uint8)
    return Image.fromarray(a)

def build_events():
    """resolve tempos dos overlays (por shot) e gera eventos de som"""
    evs = []; sfx = []
    for sh in SHOTS:
        n = sh['nframes']
        for o in O.get(sh['id'], []):
            o = dict(o)
            o['f'] = resolve(sh, o['at'], n) + int(round(o.get('offset', 0) * FPS))
            o['fu'] = resolve(sh, o['until'], n) if 'until' in o else 10 ** 9
            if o['t'] == 'check':
                o['fi'] = [resolve(sh, it[2], n) for it in o['items']]
            o['sid'] = sh['id']
            evs.append(o)
            tg = (sh['f0'] + max(0, o['f'])) / FPS
            if o['t'] in ('pill', 'head', 'tag', 'icon', 'bar'):
                sfx.append({'type': 'pop', 't': round(tg, 3)})
            if o['t'] == 'check':
                for fi in o['fi']:
                    sfx.append({'type': 'ding', 't': round((sh['f0'] + fi) / FPS, 3)})
            if o['t'] == 'sfx':
                sfx.append({'type': o['s'], 't': round(tg, 3)})
    # remove pops muito proximos
    sfx.sort(key=lambda e: e['t'])
    out = []
    for e in sfx:
        if e['type'] == 'pop' and out and out[-1]['type'] == 'pop' and e['t'] - out[-1]['t'] < 0.15:
            continue
        out.append(e)
    json.dump(out, open(f"{ROOT}/audio/sfx_events.json", 'w'), indent=0)
    return evs

EVS = build_events()

def render_frame(frames_dir, gf):
    # descobre shot
    si = next(i for i, s in enumerate(SHOTS) if s['f0'] <= gf < s['f1'])
    sh = SHOTS[si]; n = sh['nframes']; lf = gf - sh['f0']    # 0-based local
    # shake
    sx = sy = 0
    for o in EVS:
        if o['sid'] == sh['id'] and o['t'] == 'shake' and o['f'] <= lf < o['f'] + int(o.get('dur', 0.3) * FPS):
            rr = random.Random(gf); amp = 22 * (1 - (lf - o['f']) / (o.get('dur', 0.3) * FPS))
            sx, sy = rr.uniform(-amp, amp), rr.uniform(-amp, amp)
    base = load_shot_frame(frames_dir, sh['id'], lf + 1, n)
    # punch-in no inicio do shot
    if si > 0 and lf < 8:
        s = 1 + 0.07 * (1 - lf / 8) ** 2
        cw, ch = int(W / s), int(H / s)
        base = base.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
    if sx or sy:
        base = base.transform((W, H), Image.AFFINE, (1, 0, sx, 0, 1, sy), resample=Image.BILINEAR)
        s = 1.04; cw, ch = int(W / s), int(H / s)
        base = base.crop(((W - cw) // 2, (H - ch) // 2, (W - cw) // 2 + cw, (H - ch) // 2 + ch)).resize((W, H), Image.BILINEAR)
    base = grade(base)
    # transicao (faixa diagonal colorida)
    trans = None
    if si + 1 < len(SHOTS) and lf >= n - TR:
        p = (lf - (n - TR) + 1) / (2 * TR + 1); trans = (p, si + 1, 'out')
    elif si > 0 and lf < TR:
        p = (lf + TR + 1) / (2 * TR + 1); trans = (p, si, 'in')
    if trans:
        p, ni, mode = trans
        if mode == 'out':
            other = grade(load_shot_frame(frames_dir, SHOTS[ni]['id'], 1, SHOTS[ni]['nframes']))
            A, B = base, other
        else:
            prev = SHOTS[ni - 1]
            other = grade(load_shot_frame(frames_dir, prev['id'], prev['nframes'], prev['nframes']))
            A, B = other, base
        d, _ = band_mask(p)
        e = p * 1.5 - 0.25                  # frente da faixa
        bw = 0.16
        show_b = (d < e - bw)
        in_band = (d >= e - bw) & (d < e)
        edge = (d >= e - bw - 0.012) & (d < e - bw + 0.0) | (d >= e - 0.012) & (d < e)
        col = TCOL[ni % len(TCOL)]
        def up(m):
            return Image.fromarray((m * 255).astype(np.uint8)).resize((W, H), Image.NEAREST)
        out = A.copy()
        out.paste(B, (0, 0), up(show_b))
        out.paste(Image.new('RGB', (W, H), col), (0, 0), up(in_band))
        out.paste(Image.new('RGB', (W, H), (255, 255, 255)), (0, 0), up(edge))
        base = out
    canvas = base.convert('RGBA')
    # flash branco
    for o in EVS:
        if o['sid'] == sh['id'] and o['t'] == 'flash' and o['f'] <= lf < o['f'] + 6:
            a = int(230 * (1 - (lf - o['f']) / 6))
            canvas.alpha_composite(Image.new('RGBA', (W, H), (255, 250, 220, a)))
    # overlays do shot
    icons = []; pills_y = []
    for o in EVS:
        if o['sid'] != sh['id']: continue
        k = lf - o['f']
        if k < 0 or lf >= o['fu']: continue
        if o['t'] == 'pill':
            im = pill_img(o['text'], o['color'])
            sc = ease_pop(k)
            y = o.get('y', 300)
            if o.get('blink') and (lf // 15) % 2 == 1:
                im = pill_img(o['text'], o['color'])  # mesmo
            paste_center(canvas, im, 70 + im.width * sc / 2, y, sc)
        elif o['t'] == 'tag':
            im = tag_img(o['text'], o['color'])
            paste_center(canvas, im, o['x'] * W, o['y'] * H, ease_pop(k))
        elif o['t'] == 'head':
            im = head_img(o['text'], o['color'], o.get('size', 110), o.get('sub'))
            paste_center(canvas, im, W / 2, o.get('y', 300), ease_pop(k, 8, 1.22))
        elif o['t'] == 'icon':
            icons.append((o, k))
        elif o['t'] == 'bar':
            frac = min(100, int(max(0, k - 4) * 4))
            frac = int(frac / 4) * 4
            im = bar_img(o['text'], o['color'], frac)
            paste_center(canvas, im, W / 2, o.get('y', 440), ease_pop(k))
        elif o['t'] == 'check':
            y0 = o.get('y', 470)
            fnt = font('Montserrat.ttf', 40, b'ExtraBold')
            cw = max(640, max(int(fnt.getlength(it[1])) for it in o['items']) + 230)
            for r, ((em, tx, _), fi) in enumerate(zip(o['items'], o['fi'])):
                kk = lf - fi
                if kk < 0: continue
                im = check_row(em, tx, kk >= 5, cw)
                paste_center(canvas, im, W / 2, y0 + r * 124, ease_pop(kk, 6))
    # icone: so o mais recente visivel
    if icons:
        o, k = sorted(icons, key=lambda t: t[0]['f'])[-1]
        im = emoji_img(o['e'], 120)
        bob = math.sin(lf / 9) * 8
        # se ha titulo grande no topo, o icone desce para nao cobrir o texto
        head_on = [h for h in EVS if h['sid'] == sh['id'] and h['t'] == 'head' and h['f'] <= lf < h['fu'] and h.get('y', 300) < 360]
        iy = 300
        if head_on:
            hh = head_img(head_on[-1]['text'], head_on[-1]['color'], head_on[-1].get('size', 110), head_on[-1].get('sub'))
            iy = head_on[-1].get('y', 300) + hh.height / 2 + 75
        paste_center(canvas, im, W - 130, iy + bob, ease_pop(k, 8, 1.3))
    # legenda
    t = gf / FPS
    wd = caption_at(t)
    if wd:
        k = int((t - wd['t0']) * FPS)
        im = word_img(disp_word(wd['w']), is_hl(wd['w']))
        sc = 1.22 if k <= 0 else (1.1 if k == 1 else 1.0)
        paste_center(canvas, im, W / 2, 1350, sc)
    return canvas.convert('RGB')

if __name__ == '__main__':
    frames_dir = sys.argv[1]
    if sys.argv[2] == '--still':
        # --still sid:frame out.png
        sid, k = sys.argv[3].split(':')
        sh = [s for s in SHOTS if s['id'] == sid][0]
        render_frame(frames_dir, sh['f0'] + int(k)).save(sys.argv[4])
        sys.exit(0)
    out = sys.argv[2]
    rng_ = sys.argv[3] if len(sys.argv) > 3 else None
    g0, g1 = 0, int(tl['total'] * FPS)
    if rng_:
        a, b = rng_.split(':'); g0, g1 = int(a), int(b)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-c:v', 'libx264', '-preset', 'slow', '-crf', '14', '-pix_fmt', 'yuv420p', '-profile:v', 'high', out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for gf in range(g0, g1):
        p.stdin.write(render_frame(frames_dir, gf).tobytes())
        if gf % 300 == 0: print('frame', gf, flush=True)
    p.stdin.close(); p.wait()
    print('ok', out)
