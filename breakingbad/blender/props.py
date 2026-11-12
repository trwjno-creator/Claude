# Props e cenarios procedurais
import bpy, math, random
from mathutils import Vector
from lib import *

def smiley(loc=(0, 0, 0), size=1.0, rot=(math.pi / 2, 0, 0), color='#c0141c', drips=True, parent=None, emit=0.0):
    """o 'rosto sorridente' (desenhado na parede). plano XY local, normal +Z -> rot para parede"""
    p = empty("smiley", loc, parent, rot)
    m = mat(color, 0.55, emit=emit)
    n = 40
    r = size
    pts = [(r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), 0) for i in range(n)]
    curve_path(pts, bevel=size * 0.06, m=m, parent=p, closed=True)
    for sx in (-1, 1):
        sphere(1, (sx * r * 0.35, r * 0.28, 0), (size * 0.1, size * 0.16, size * 0.03), m, p)
    sm = [(r * 0.55 * math.cos(a), r * 0.55 * math.sin(a) - r * 0.05, 0) for a in [math.radians(x) for x in range(200, 341, 20)]]
    curve_path(sm, bevel=size * 0.055, m=m, parent=p)
    if drips:
        rnd = random.Random(3)
        for i in range(7):
            a = math.radians(rnd.uniform(220, 320))
            x, y = r * math.cos(a), r * math.sin(a)
            L = rnd.uniform(0.15, 0.45) * size
            box((size * 0.04, size * 0.04, L), (x, y - L / 2, 0), rot=(math.pi / 2, 0, 0), m=m, parent=p, bevel=size * 0.015)
            sphere(size * 0.035, (x, y - L, 0), m=m, parent=p, seg=12)
    return p

def bulbs_row(x0, x1, z, y, n=10, c1='#ff5fae', c2='#ffffff', r=0.09):
    for i in range(n):
        x = x0 + (x1 - x0) * i / (n - 1)
        sphere(r, (x, y, z), m=mat(c1 if i % 2 == 0 else c2, 0.3, emit=2.5), seg=16)

def armchair(loc, rot=0, color='#c0392b'):
    p = empty("chair", loc, rot=(0, 0, rot))
    box((0.8, 0.7, 0.35), (0, 0, 0.3), m=color, parent=p, bevel=0.08)
    box((0.8, 0.18, 0.7), (0, 0.3, 0.6), m=color, parent=p, bevel=0.08)
    for sx in (-1, 1):
        box((0.16, 0.7, 0.4), (sx * 0.4, 0, 0.5), m=color, parent=p, bevel=0.07)
    return p

def couch(loc, rot=0, color='#7a4a2a', w=2.2):
    p = empty("couch", loc, rot=(0, 0, rot))
    box((w, 0.85, 0.4), (0, 0, 0.3), m=mat(color, 0.35), parent=p, bevel=0.1)
    box((w, 0.25, 0.75), (0, 0.33, 0.65), m=mat(color, 0.35), parent=p, bevel=0.1)
    for sx in (-1, 1):
        box((0.25, 0.85, 0.55), (sx * w / 2, 0, 0.5), m=mat(color, 0.35), parent=p, bevel=0.1)
    for i in range(2):
        box((w / 2 - 0.2, 0.7, 0.12), ((i - 0.5) * (w / 2 - 0.15), -0.05, 0.55), m=mat(color, 0.3), parent=p, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.04, 0.12, (sx * (w / 2 - 0.05), sy * 0.33, 0.06), m='#3a2414', parent=p)
    return p

def table(loc, size=(1.4, 0.8), h=0.75, color='#c98a4b', leg='#7a4a2a', parent=None, round_=False):
    p = empty("table", loc, parent)
    if round_:
        cyl(size[0] / 2, 0.06, (0, 0, h), m=color, parent=p)
        cyl(0.06, h, (0, 0, h / 2), m=leg, parent=p)
        cyl(0.3, 0.04, (0, 0, 0.02), m=leg, parent=p)
    else:
        box((size[0], size[1], 0.06), (0, 0, h), m=color, parent=p, bevel=0.02)
        for sx in (-1, 1):
            for sy in (-1, 1):
                box((0.06, 0.06, h), (sx * (size[0] / 2 - 0.08), sy * (size[1] / 2 - 0.08), h / 2), m=leg, parent=p, bevel=0.01)
    return p

def chair(loc, rot=0, color='#3a7bd5'):
    p = empty("chair", loc, rot=(0, 0, rot))
    box((0.45, 0.45, 0.06), (0, 0, 0.45), m=color, parent=p, bevel=0.02)
    box((0.45, 0.06, 0.45), (0, 0.2, 0.7), m=color, parent=p, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.025, 0.45, (sx * 0.19, sy * 0.19, 0.225), m='#555555', parent=p)
    return p

def desk_pc(loc, rot=0, color='#ececec'):
    p = empty("desk", loc, rot=(0, 0, rot))
    table((0, 0, 0), (1.5, 0.75), 0.75, color, '#9a9a9a', parent=p)
    box((0.6, 0.05, 0.4), (0, 0.15, 1.05), m='#222831', parent=p, bevel=0.02)
    box((0.54, 0.02, 0.33), (0, 0.12, 1.06), m=mat('#4fc3f7', 0.3, emit=0.8), parent=p)
    box((0.08, 0.08, 0.15), (0, 0.18, 0.84), m='#222831', parent=p)
    box((0.45, 0.15, 0.02), (0, -0.15, 0.79), m='#333333', parent=p, bevel=0.005)
    # papeis
    box((0.25, 0.32, 0.01), (-0.5, -0.1, 0.785), rot=(0, 0, 0.2), m='#ffffff', parent=p)
    return p

def door(loc, rot=0, color='#8b5a2b', w=1.0, h=2.1, frame='#f5f0e6'):
    p = empty("door", loc, rot=(0, 0, rot))
    box((w + 0.16, 0.12, h + 0.08), (0, 0, (h + 0.08) / 2), m=frame, parent=p)
    box((w, 0.1, h), (0, -0.03, h / 2), m=color, parent=p, bevel=0.01)
    for z in (0.55, 1.45):
        box((w * 0.7, 0.02, 0.6), (0, -0.09, z), m=mat(color, 0.4), parent=p, bevel=0.01)
    sphere(0.05, (w * 0.38, -0.12, 1.0), m=mat('#e8c34a', 0.2, metal=0.8), parent=p)
    return p

def window(loc, rot=0, w=1.4, h=1.2, sky='#9be7ff', bars=False, frame='#ffffff', emit=0.6):
    p = empty("win", loc, rot=(0, 0, rot))
    box((w, 0.05, h), (0, 0, 0), m=mat(sky, 0.2, emit=emit), parent=p)
    for z in (-h / 2, h / 2):
        box((w + 0.12, 0.1, 0.08), (0, -0.03, z), m=frame, parent=p)
    for x in (-w / 2, w / 2, 0):
        box((0.06 if x == 0 else 0.08, 0.1, h), (x, -0.03, 0), m=frame, parent=p)
    if bars:
        for i in range(6):
            cyl(0.02, h, (-w / 2 + w * (i + 0.5) / 6, -0.09, 0), m='#777777', parent=p)
    return p

def frame_photo(loc, rot=(0, 0, 0), w=0.5, h=0.62, color='#c99a3b', parent=None, bg='#bfe7ff'):
    p = empty("photo", loc, parent, rot)
    box((w, 0.05, h), (0, 0, 0), m=mat(color, 0.3, metal=0.4), parent=p, bevel=0.015)
    box((w * 0.82, 0.02, h * 0.84), (0, -0.025, 0), m=bg, parent=p)
    return p

def tree(loc, s=1.0, leaf='#3fbf5f', trunk='#8a5a32', seed=0):
    p = empty("tree", loc)
    cyl(0.12 * s, 1.4 * s, (0, 0, 0.7 * s), m=trunk, parent=p)
    rnd = random.Random(seed)
    for i in range(5):
        sphere(rnd.uniform(0.5, 0.7) * s, (rnd.uniform(-0.4, 0.4) * s, rnd.uniform(-0.4, 0.4) * s, (1.7 + rnd.uniform(-0.2, 0.4)) * s), m=mat(leaf, 0.7), parent=p, seg=24)
    return p

def palm(loc, s=1.0, lean=0.15, seed=0):
    p = empty("palm", loc, rot=(0, lean, 0))
    for i in range(8):
        cyl(0.13 * s * (1 - i * 0.05), 0.42 * s, (i * 0.03 * s, 0, (0.2 + i * 0.4) * s), m='#b07a42' if i % 2 else '#9a6a38', parent=p)
    top = (0.24 * s, 0, 3.3 * s)
    for i in range(7):
        a = 2 * math.pi * i / 7
        sphere(1, (top[0] + 0.6 * s * math.cos(a), 0.6 * s * math.sin(a), top[2] - 0.15 * s), (0.75 * s, 0.2 * s, 0.05 * s), mat('#2fbf4f', 0.6), p, rot=(0, 0.35, a))
    for i in range(3):
        sphere(0.11 * s, (top[0] + 0.1 * math.cos(i * 2), 0.1 * math.sin(i * 2), top[2] - 0.2 * s), m='#6b4a2a', parent=p, seg=12)
    return p

def cloud(loc, s=1.0, seed=0, color='#ffffff'):
    p = empty("cloud", loc)
    rnd = random.Random(seed)
    for i in range(6):
        sphere(rnd.uniform(0.5, 0.9) * s, (rnd.uniform(-1.2, 1.2) * s, rnd.uniform(-0.3, 0.3) * s, rnd.uniform(-0.1, 0.4) * s), m=mat(color, 0.9), parent=p, seg=20)
    return p

def dove(loc, s=0.3, parent=None):
    p = empty("dove", loc, parent)
    m = mat('#ffffff', 0.6)
    sphere(1, (0, 0, 0), (0.35 * s, 0.6 * s, 0.3 * s), m, p)
    sphere(0.22 * s, (0, -0.55 * s, 0.18 * s), m=m, parent=p)
    cone(0.06 * s, 0, 0.14 * s, (0, -0.78 * s, 0.16 * s), (math.pi / 2, 0, 0), m='#f2a33a', parent=p)
    for sx in (-1, 1):
        sphere(0.035 * s, (sx * 0.1 * s, -0.68 * s, 0.24 * s), m='#111111', parent=p, seg=8)
    wings = []
    for sx in (-1, 1):
        wp = empty("wing", (sx * 0.25 * s, 0, 0.1 * s), p)
        sphere(1, (sx * 0.45 * s, 0, 0), (0.5 * s, 0.3 * s, 0.05 * s), m, wp)
        wings.append(wp)
    cone(0.25 * s, 0.05 * s, 0.4 * s, (0, 0.65 * s, 0.05 * s), (-math.pi / 2, 0, 0), m=m, parent=p)
    return p, wings

def flap(wings, f0, f1, speed=4):
    for f in range(f0, f1 + 1, 2):
        a = math.sin(f / speed * math.pi) * 0.9
        for k, w in enumerate(wings):
            w.rotation_euler = (0, (1 if k == 0 else -1) * a, 0)
            w.keyframe_insert('rotation_euler', frame=f)

def money_stack(loc, n=5, parent=None, rot=0):
    p = empty("money", loc, parent, rot=(0, 0, rot))
    for i in range(n):
        box((0.4, 0.2, 0.06), (0, 0, 0.035 + i * 0.065), m=mat('#4fd06a', 0.5), parent=p, bevel=0.01)
        box((0.41, 0.06, 0.062), (0, 0, 0.035 + i * 0.065), m='#e9f7e0', parent=p)
    return p

def candle(loc, h=0.25, parent=None):
    p = empty("candle", loc, parent)
    cyl(0.04, h, (0, 0, h / 2), m='#fff6dc', parent=p)
    sphere(1, (0, 0, h + 0.04), (0.025, 0.025, 0.045), mat('#ffb12a', emit=6), p, seg=12)
    return p

def teacup(loc, s=1.0, parent=None, color='#5aa0e6'):
    p = empty("tea", loc, parent)
    cyl(0.11 * s, 0.015 * s, (0, 0, 0.008 * s), m='#ffffff', parent=p)
    cyl(0.06 * s, 0.07 * s, (0, 0, 0.05 * s), m=color, parent=p)
    cyl(0.052 * s, 0.01 * s, (0, 0, 0.083 * s), m='#a8622a', parent=p)
    torus(0.025 * s, 0.007 * s, (0.07 * s, 0, 0.05 * s), (math.pi / 2, 0, 0), m=color, parent=p)
    return p

def tv_camera(loc, rot=0):
    p = empty("tvcam", loc, rot=(0, 0, rot))
    for a in range(3):
        an = a * 2 * math.pi / 3
        cyl(0.025, 1.1, (0.25 * math.cos(an), 0.25 * math.sin(an), 0.5), (0.25 * math.sin(an), -0.25 * math.cos(an), 0), m='#333333', parent=p)
    box((0.35, 0.6, 0.35), (0, 0, 1.2), m='#2d2d34', parent=p, bevel=0.04)
    cyl(0.12, 0.25, (0, -0.4, 1.2), (math.pi / 2, 0, 0), m='#1a1a1a', parent=p)
    cyl(0.09, 0.02, (0, -0.53, 1.2), (math.pi / 2, 0, 0), m=mat('#5a7aff', 0.1, emit=0.5), parent=p)
    sphere(0.04, (0.12, -0.25, 1.4), m=mat('#ff2a2a', emit=8), parent=p)
    return p

def bed(loc, rot=0, color='#ffffff', blanket='#a8d8ea'):
    p = empty("bed", loc, rot=(0, 0, rot))
    box((1.0, 2.0, 0.3), (0, 0, 0.35), m='#d0d0d0', parent=p, bevel=0.03)
    box((0.95, 1.95, 0.15), (0, 0, 0.55), m=color, parent=p, bevel=0.06)
    box((0.97, 1.2, 0.08), (0, -0.35, 0.64), m=blanket, parent=p, bevel=0.04)
    box((0.6, 0.35, 0.12), (0, 0.75, 0.68), m='#ffffff', parent=p, bevel=0.05)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.03, 0.3, (sx * 0.45, sy * 0.95, 0.15), m='#999999', parent=p)
    return p

def mattress(loc, rot=0):
    p = empty("mattress", loc, rot=(0, 0, rot))
    box((1.0, 1.9, 0.2), (0, 0, 0.1), m='#e8e2d4', parent=p, bevel=0.07)
    box((0.55, 0.3, 0.1), (0, 0.7, 0.24), m='#ffffff', parent=p, bevel=0.04)
    box((1.02, 1.0, 0.04), (0, -0.3, 0.22), m='#7d8aa8', parent=p, bevel=0.02)
    return p

def gavel(loc, parent=None):
    p = empty("gavel", loc, parent)
    cyl(0.05, 0.22, (0, 0, 0), (0, math.pi / 2, 0), m='#6b3a1a', parent=p)
    cyl(0.015, 0.3, (0, 0.15, 0), (math.pi / 2, 0, 0), m='#6b3a1a', parent=p)
    return p

def flower_arch(loc, w=2.2, h=2.6):
    p = empty("arch", loc)
    pts = []
    for i in range(25):
        a = math.pi * i / 24
        pts.append((math.cos(a) * w / 2, 0, h - w / 2 + math.sin(a) * w / 2))
    # colunas
    for sx in (-1, 1):
        cyl(0.07, h - w / 2, (sx * w / 2, 0, (h - w / 2) / 2), m='#ffffff', parent=p)
    rnd = random.Random(5)
    cols = ['#ff7eb6', '#ffffff', '#ffd1e3', '#ff4f8b', '#fff07a']
    for i in range(25):
        a = math.pi * i / 24
        x, z = math.cos(a) * w / 2, h - w / 2 + math.sin(a) * w / 2
        for k in range(2):
            sphere(rnd.uniform(0.09, 0.14), (x + rnd.uniform(-0.06, 0.06), rnd.uniform(-0.08, 0.08), z + rnd.uniform(-0.06, 0.06)), m=rnd.choice(cols), parent=p, seg=12)
        sphere(0.1, (x, 0.03, z), m=mat('#4caf50', 0.7), parent=p, seg=10)
    for sx in (-1, 1):
        for j in range(6):
            z = j * (h - w / 2) / 6 + 0.2
            sphere(rnd.uniform(0.08, 0.12), (sx * w / 2 + rnd.uniform(-0.05, 0.05), -0.05, z), m=rnd.choice(cols), parent=p, seg=12)
    return p

def house_ext(loc, wall='#f2e6d0', roof='#5a6b8a', night=True):
    p = empty("house", loc)
    box((6, 4, 3), (0, 0, 1.5), m=wall, parent=p, bevel=0.05)
    box((6.6, 4.6, 0.25), (0, 0, 3.1), m=roof, parent=p, bevel=0.05)
    box((2.2, 3.6, 1.6), (1.4, 0.2, 4.0), m=wall, parent=p, bevel=0.05)
    box((2.6, 4.0, 0.2), (1.4, 0.2, 4.85), m=roof, parent=p, bevel=0.05)
    d = door((-1.2, -2.03, 0), 0, '#3b2a20'); d.parent = p
    for x in (0.8, 2.2):
        w = window((x, -2.03, 1.6), 0, 1.0, 1.0, '#ffd27a' if night else '#9be7ff', emit=1.5 if night else 0.4); w.parent = p
    w = window((1.4, -1.63, 4.0), 0, 1.4, 0.9, '#ffd27a' if night else '#9be7ff', emit=1.2 if night else 0.4); w.parent = p
    # escada / caminho
    box((1.4, 2.5, 0.05), (-1.2, -3.3, 0.02), m='#b8b0a0', parent=p)
    return p

def stall(loc, color='#ff5a5a', sign='PIZZA', rot=0, sign_col='#ffffff'):
    p = empty("stall", loc, rot=(0, 0, rot))
    box((2.0, 0.9, 1.1), (0, 0, 0.55), m=color, parent=p, bevel=0.05)
    box((2.0, 0.9, 0.06), (0, 0, 1.12), m='#ffffff', parent=p)
    for i in range(6):
        box((2.0 / 6, 1.0, 0.08), (-1 + 2.0 / 6 * (i + 0.5), -0.1, 2.1), rot=(0.25, 0, 0), m=color if i % 2 else '#ffffff', parent=p)
    for sx in (-1, 1):
        cyl(0.04, 1.0, (sx * 0.95, -0.35, 1.6), m='#dddddd', parent=p)
    box((1.6, 0.08, 0.4), (0, 0.4, 2.5), m='#2d2d34', parent=p, bevel=0.04)
    t = text3d(sign, (0, 0.35, 2.5), size=0.28, m=mat(sign_col, emit=1.5), extrude=0.01)
    t.parent = p
    return p

def corkboard(loc, w=3.2, h=2.0, rot=0):
    p = empty("cork", loc, rot=(0, 0, rot))
    box((w + 0.15, 0.08, h + 0.15), (0, 0.02, 0), m='#8b5a2b', parent=p, bevel=0.02)
    box((w, 0.06, h), (0, 0, 0), m='#d4a46a', parent=p)
    return p

def card(loc, parent=None, bg='#ffffff', who='#2d2d34', w=0.42, h=0.55, rot=(0, 0, 0)):
    """cartao com silhueta (cabeca+ombros)"""
    p = empty("card", loc, parent, rot)
    box((w, 0.02, h), (0, 0, 0), m=bg, parent=p, bevel=0.01)
    sphere(1, (0, -0.012, h * 0.12), (w * 0.2, 0.01, w * 0.2), who, p)
    sphere(1, (0, -0.012, -h * 0.3), (w * 0.34, 0.01, h * 0.2), who, p)
    sphere(0.03, (0, -0.02, h * 0.44), m=mat('#e53935', 0.3), parent=p, seg=12)
    return p

def generic_person(seed, loc=(0, 0, 0), rot=0, **kw):
    rnd = random.Random(seed)
    skins = ['#f7c29c', '#e0a97f', '#c68a5e', '#8d5a3b', '#f3d0b0']
    hairs = ['#2a1a10', '#5a3a1a', '#c9a24a', '#111111', '#8a4a20', '#7a7a7a']
    shirts = ['#e84a5f', '#2a9df4', '#ffb400', '#5cc66b', '#9b59b6', '#ff7f50', '#1abc9c']
    female = rnd.random() < 0.5
    d = dict(name=f"p{seed}", skin=rnd.choice(skins), hair=rnd.choice(hairs),
             hair_style=rnd.choice(['long', 'bun']) if female else rnd.choice(['short', 'buzz', 'short']),
             eyes='#3a2a1a', jacket=rnd.choice(shirts), vest=None, shirt='#ffffff', pants=rnd.choice(['#2c3e50', '#34495e', '#5d4037', '#1f2a44']),
             female=female, body_w=0.92 if female else 1.0, height=rnd.uniform(0.92, 1.05), collar=False, loc=loc, rot=rot)
    d.update(kw)
    return Char(**d)


# ================================================================ Supernatural
def impala(loc=(0, 0, 0), rot=0.0, color='#0d0d10', parent=None):
    """Chevrolet Impala 67 estilizado (sedan preto, cromados). Frente para -Y."""
    p = empty("impala", loc, parent, rot=(0, 0, rot))
    body = mat(color, 0.18, metal=0.6, spec=0.8)
    chrome = mat('#d8dde4', 0.12, metal=1.0)
    glass = mat('#1a2a3a', 0.05, spec=1.0)
    L, Wd = 4.6, 1.8
    box((Wd, L, 0.5), (0, 0, 0.62), m=body, parent=p, bevel=0.08)            # corpo baixo e comprido
    box((Wd * 0.92, L * 0.42, 0.42), (0, 0.25, 1.05), m=body, parent=p, bevel=0.1)   # cabine
    box((Wd * 0.94, L * 0.36, 0.05), (0, 0.25, 1.27), m=body, parent=p, bevel=0.03)  # teto
    box((Wd * 0.86, 0.05, 0.32), (0, 0.25 - L * 0.21 - 0.01, 1.05), rot=(-0.45, 0, 0), m=glass, parent=p)   # para-brisa
    box((Wd * 0.86, 0.05, 0.3), (0, 0.25 + L * 0.21 + 0.01, 1.05), rot=(0.45, 0, 0), m=glass, parent=p)    # vidro traseiro
    for sx in (-1, 1):
        box((0.04, L * 0.36, 0.28), (sx * Wd * 0.465, 0.25, 1.06), m=glass, parent=p)                     # janelas
        box((0.03, L * 0.98, 0.04), (sx * Wd * 0.505, 0, 0.7), m=chrome, parent=p)                       # friso
    for sy in (-1, 1):
        box((Wd * 1.02, 0.12, 0.14), (0, sy * L * 0.505, 0.45), m=chrome, parent=p, bevel=0.04)          # para-choques
    # grade e farois (frente = -Y)
    box((Wd * 0.8, 0.04, 0.2), (0, -L * 0.5 - 0.01, 0.66), m=mat('#30343a', 0.3, metal=0.8), parent=p)
    for sx in (-1, 1):
        for k in (0.62, 0.8):
            cyl(0.085, 0.05, (sx * Wd * k / 2 + sx * 0.18, -L * 0.5 - 0.02, 0.66), (math.pi / 2, 0, 0), m=mat('#fff6d8', 0.1, emit=2.5), parent=p)
        box((0.32, 0.04, 0.1), (sx * Wd * 0.36, L * 0.5 + 0.02, 0.68), m=mat('#d02020', 0.2, emit=1.5), parent=p)   # lanternas
    # rodas
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.36, 0.26, (sx * Wd * 0.47, sy * L * 0.31, 0.36), (0, math.pi / 2, 0), m='#141414', parent=p)
            cyl(0.2, 0.28, (sx * Wd * 0.47, sy * L * 0.31, 0.36), (0, math.pi / 2, 0), m=chrome, parent=p)
    return p

def crib(loc, rot=0):
    p = empty("crib", loc, rot=(0, 0, rot))
    box((0.7, 1.2, 0.08), (0, 0, 0.45), m='#ffffff', parent=p, bevel=0.02)
    box((0.66, 1.16, 0.08), (0, 0, 0.52), m='#bfe4ff', parent=p, bevel=0.03)
    for sx in (-1, 1):
        for i in range(9):
            cyl(0.015, 0.5, (sx * 0.34, -0.55 + i * 0.1375, 0.75), m='#ffffff', parent=p)
        box((0.05, 1.22, 0.05), (sx * 0.34, 0, 1.0), m='#ffffff', parent=p)
    for sy in (-1, 1):
        box((0.72, 0.05, 0.6), (0, sy * 0.6, 0.72), m='#ffffff', parent=p, bevel=0.02)
        for sx in (-1, 1):
            cyl(0.03, 1.0, (sx * 0.34, sy * 0.6, 0.5), m='#ffffff', parent=p)
    return p

def flames(loc, n=10, spread=1.0, h=0.6, seed=0, parent=None, rot=(0, 0, 0)):
    """chamas estilizadas (cones emissivos laranja/amarelo) - retorna lista p/ animar"""
    p = empty("fire", loc, parent, rot)
    rnd = random.Random(seed); out = []
    for i in range(n):
        x, y = rnd.uniform(-spread, spread), rnd.uniform(-spread * 0.3, spread * 0.3)
        hh = h * rnd.uniform(0.6, 1.3)
        c1 = cone(0.12 * hh / h + 0.05, 0, hh, (x, y, hh / 2), m=mat('#ff6a1a', 0.5, emit=6), parent=p, verts=12)
        c2 = cone(0.07 * hh / h + 0.03, 0, hh * 0.6, (x, y - 0.03, hh * 0.3), m=mat('#ffd34a', 0.5, emit=8), parent=p, verts=12)
        out += [c1, c2]
    return p, out

def flicker(objs, f0, f1, seed=0, amp=0.25):
    rnd = random.Random(seed)
    for o in objs:
        s0 = tuple(o.scale)
        for f in range(f0, f1 + 1, 3):
            k = 1 + rnd.uniform(-amp, amp)
            o.scale = (s0[0] * (1 + rnd.uniform(-amp, amp) * 0.5), s0[1], s0[2] * k)
            o.keyframe_insert('scale', frame=f)

def shotgun(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    p = empty("shotgun", loc, parent, rot)
    cyl(0.022 * s, 0.75 * s, (0, -0.32 * s, 0), (math.pi / 2, 0, 0), m=mat('#2a2a2e', 0.3, metal=0.8), parent=p)
    cyl(0.022 * s, 0.75 * s, (0.045 * s, -0.32 * s, 0), (math.pi / 2, 0, 0), m=mat('#2a2a2e', 0.3, metal=0.8), parent=p)
    box((0.08 * s, 0.4 * s, 0.1 * s), (0.02 * s, 0.2 * s, -0.04 * s), rot=(0.2, 0, 0), m='#6b3a1a', parent=p, bevel=0.02)
    return p

def colt(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    p = empty("colt", loc, parent, rot)
    cyl(0.018 * s, 0.24 * s, (0, -0.14 * s, 0), (math.pi / 2, 0, 0), m=mat('#c9ccd2', 0.15, metal=1.0), parent=p)
    cyl(0.04 * s, 0.07 * s, (0, -0.02 * s, 0), (math.pi / 2, 0, 0), m=mat('#a8acb2', 0.2, metal=1.0), parent=p)
    box((0.035 * s, 0.06 * s, 0.13 * s), (0, 0.04 * s, -0.07 * s), rot=(0.35, 0, 0), m='#5a3a1a', parent=p, bevel=0.01)
    return p

def hellhound(loc, rot=0, s=1.0):
    p = empty("hound", loc, rot=(0, 0, rot))
    m = mat('#121014', 0.8)
    sphere(1, (0, 0, 0.55 * s), (0.28 * s, 0.6 * s, 0.3 * s), m, p)
    sphere(1, (0, -0.62 * s, 0.75 * s), (0.2 * s, 0.26 * s, 0.2 * s), m, p)
    sphere(1, (0, -0.85 * s, 0.7 * s), (0.11 * s, 0.14 * s, 0.09 * s), m, p)
    for sx in (-1, 1):
        sphere(0.04 * s, (sx * 0.09 * s, -0.8 * s, 0.82 * s), m=mat('#ff1a1a', emit=10), parent=p, seg=12)
        cone(0.06 * s, 0, 0.16 * s, (sx * 0.12 * s, -0.55 * s, 0.97 * s), m=m, parent=p, verts=8)
        for sy in (-1, 1):
            cyl(0.06 * s, 0.45 * s, (sx * 0.17 * s, sy * 0.38 * s, 0.25 * s), m=m, parent=p)
    cone(0.06 * s, 0.01 * s, 0.4 * s, (0, 0.7 * s, 0.7 * s), (-0.9, 0, 0), m=m, parent=p)
    return p

def wings_shadow(loc, s=1.0, rot=(math.pi / 2, 0, 0), color='#0a0a0a'):
    """sombra de asas na parede (Castiel)"""
    p = empty("wings", loc, rot=rot)
    m = mat(color, 0.9)
    for sx in (-1, 1):
        for i in range(7):
            a = math.radians(10 + i * 14)
            L = s * (1.6 - i * 0.12)
            sphere(1, (sx * math.cos(a) * L * 0.55, math.sin(a) * L * 0.5 - 0.1 * s, 0), (L * 0.55, 0.13 * s, 0.01), m, p, rot=(0, 0, sx * a))
    return p

def tombstone(loc, rot=0, text=None, s=1.0):
    p = empty("tomb", loc, rot=(0, 0, rot))
    box((0.6 * s, 0.15 * s, 0.7 * s), (0, 0, 0.35 * s), m='#9aa0a8', parent=p, bevel=0.04)
    cyl(0.3 * s, 0.15 * s, (0, 0, 0.7 * s), (math.pi / 2, 0, 0), m='#9aa0a8', parent=p)
    if text:
        t = text3d(text, (0, -0.08 * s, 0.45 * s), size=0.12 * s, m='#4a4e56', extrude=0.005); t.parent = p
    return p

def junk_car(loc, rot=0, color='#8a5a3a', seed=0):
    p = empty("junk", loc, rot=(0, 0, rot))
    m = mat(color, 0.85)
    box((1.6, 3.6, 0.6), (0, 0, 0.55), m=m, parent=p, bevel=0.1)
    box((1.4, 1.6, 0.45), (0, 0.2, 1.05), m=m, parent=p, bevel=0.1)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.3, 0.2, (sx * 0.75, sy * 1.1, 0.3), (0, math.pi / 2, 0), m='#1a1a1a', parent=p)
    return p

def typewriter(loc, rot=0, parent=None):
    p = empty("typewriter", loc, parent, rot=(0, 0, rot))
    box((0.5, 0.4, 0.14), (0, 0, 0.07), m='#2a2a2e', parent=p, bevel=0.03)
    box((0.48, 0.2, 0.1), (0, 0.12, 0.17), m='#2a2a2e', parent=p, bevel=0.03)
    cyl(0.04, 0.55, (0, 0.18, 0.24), (0, math.pi / 2, 0), m='#111111', parent=p)
    box((0.24, 0.01, 0.18), (0, 0.2, 0.33), rot=(-0.2, 0, 0), m='#ffffff', parent=p)
    for i in range(12):
        sphere(0.018, (-0.18 + (i % 6) * 0.07, -0.08 - (i // 6) * 0.06, 0.15), m='#d8d8d8', parent=p, seg=8)
    return p

def lamp_green(loc, parent=None):
    p = empty("lamp", loc, parent)
    cyl(0.07, 0.03, (0, 0, 0.015), m=mat('#c9a64a', 0.2, metal=0.9), parent=p)
    cyl(0.012, 0.35, (0, 0, 0.18), m=mat('#c9a64a', 0.2, metal=0.9), parent=p)
    sphere(1, (0, -0.05, 0.36), (0.18, 0.09, 0.07), mat('#1f7a3f', 0.2, emit=0.6), p)
    return p


# ================================================================ Dexter
def container(loc, rot=0, color='#a8462e', L=4.0, Wd=2.4, H=2.6, open_doors=True):
    """conteiner de carga (frente aberta em -Y)"""
    p = empty("container", loc, rot=(0, 0, rot))
    m = mat(color, 0.55, metal=0.3)
    box((Wd, L, 0.1), (0, 0, 0.05), m=mat('#5a3a2a', 0.8), parent=p)                    # piso
    box((Wd, L, 0.1), (0, 0, H), m=m, parent=p)                                         # teto
    box((Wd, 0.1, H), (0, L / 2, H / 2), m=m, parent=p)                                 # fundo
    for sx in (-1, 1):
        box((0.1, L, H), (sx * Wd / 2, 0, H / 2), m=m, parent=p)
        for i in range(14):                                                             # nervuras
            box((0.06, 0.1, H), (sx * (Wd / 2 + 0.04), -L / 2 + 0.15 + i * L / 14, H / 2), m=mat(color, 0.6, metal=0.3), parent=p)
    if open_doors:
        for sx in (-1, 1):
            box((Wd / 2, 0.08, H), (sx * (Wd / 2 + Wd / 4), -L / 2 - Wd / 4, H / 2), rot=(0, 0, sx * -1.2), m=m, parent=p)
    return p

def blood_pool(loc, r=0.5, sx=1.0, sy=0.8, parent=None):
    o = cyl(r, 0.01, loc, m=mat('#6a0a0e', 0.08, spec=0.9), parent=parent, scale=(sx, sy, 1), verts=48)
    return o

def plastic_sheet(loc, w=2.0, h=2.4, rot=(0, 0, 0), seed=0):
    p = empty("plastic", loc, rot=rot)
    rnd = random.Random(seed)
    for i in range(6):
        box((w / 6 + 0.02, 0.01, h), (-w / 2 + w / 6 * (i + 0.5), rnd.uniform(-0.03, 0.03), h / 2), rot=(0, 0, rnd.uniform(-0.06, 0.06)),
            m=mat('#e4eef6', 0.12, spec=1.0), parent=p)
    return p

def slide_box(loc, parent=None, n=8, rot=0):
    p = empty("slides", loc, parent, rot=(0, 0, rot))
    box((0.36, 0.2, 0.08), (0, 0, 0.04), m='#6a3a1e', parent=p, bevel=0.01)
    for i in range(n):
        x = -0.15 + i * 0.043
        box((0.012, 0.16, 0.1), (x, 0, 0.1), m=mat('#d8eef8', 0.05, spec=1.0), parent=p)
        sphere(0.01, (x - 0.008, 0, 0.12), m=mat('#b0101a', 0.1), parent=p, seg=8)
    return p

def boat(loc, rot=0, name="SLICE OF LIFE"):
    """lancha branca. Proa em -Y"""
    p = empty("boat", loc, rot=(0, 0, rot))
    hull = mat('#f4f4f2', 0.3, spec=0.6)
    box((1.6, 4.4, 0.7), (0, 0.2, 0.35), m=hull, parent=p, bevel=0.15)
    cone(0.8, 0.0, 1.2, (0, -2.4, 0.35), (math.pi / 2, 0, 0), m=hull, parent=p, verts=4)
    box((1.62, 4.42, 0.12), (0, 0.2, 0.62), m=mat('#1f4a8a', 0.4), parent=p, bevel=0.03)
    box((1.2, 1.6, 0.7), (0, 0.7, 1.0), m=hull, parent=p, bevel=0.1)
    box((1.22, 0.05, 0.4), (0, -0.12, 1.1), rot=(-0.4, 0, 0), m=mat('#2a3a4a', 0.05, spec=1.0), parent=p)
    for sx in (-1, 1):
        t = text3d(name, (sx * 0.82, 0.6, 0.38), rot=(math.pi / 2, 0, sx * math.pi / 2), size=0.16, m='#1f4a8a', extrude=0.005)
        t.parent = p
    return p

def sea(size=200, color='#1f8ab8', z=0.0, rough=0.12):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    o = bpy.context.object; o.data.materials.append(mat(color, rough, spec=0.7))
    return o

def waves(n=60, area=12, y0=-2, seed=0, color='#2a5a7a', h=0.5):
    out = []
    rnd = random.Random(seed)
    for i in range(n):
        o = sphere(1, (rnd.uniform(-area, area), rnd.uniform(y0, y0 + area * 2), 0), (rnd.uniform(0.8, 1.6), rnd.uniform(0.5, 1.0), h * rnd.uniform(0.5, 1.2)),
                   mat(color, 0.2, spec=0.7), seg=20)
        out.append(o)
    return out

def donut_box(loc, parent=None, rot=0):
    p = empty("donuts", loc, parent, rot=(0, 0, rot))
    box((0.6, 0.45, 0.06), (0, 0, 0.03), m='#ff9ec6', parent=p)
    box((0.6, 0.02, 0.4), (0, 0.23, 0.22), rot=(-0.5, 0, 0), m='#ff9ec6', parent=p)
    cols = ['#ff5fa2', '#7a4a2a', '#ffe08a', '#ff5fa2', '#7a4a2a', '#ffffff']
    for i in range(6):
        x, y = -0.18 + (i % 3) * 0.18, -0.09 + (i // 3) * 0.17
        torus(0.055, 0.03, (x, y, 0.08), m='#e0a860', parent=p)
        torus(0.055, 0.022, (x, y, 0.095), m=mat(cols[i], 0.3), parent=p)
    return p

def pastel_building(loc, w=3, d=2, h=4, color='#ffc9d9', trim='#ffffff', rot=0):
    p = empty("bld", loc, rot=(0, 0, rot))
    box((w, d, h), (0, 0, h / 2), m=color, parent=p, bevel=0.05)
    box((w + 0.1, d + 0.1, 0.18), (0, 0, h + 0.05), m=trim, parent=p)
    for r in range(int(h // 1.2)):
        for c in range(int(w // 1.0)):
            box((0.5, 0.05, 0.6), (-w / 2 + 0.5 + c * 1.0, -d / 2 - 0.02, 0.9 + r * 1.2), m=mat('#7fd4ff', 0.1, emit=0.2), parent=p)
    box((w, 0.06, 0.12), (0, -d / 2 - 0.03, h * 0.62), m=trim, parent=p)
    return p

def ice_truck(loc, rot=0):
    p = empty("truck", loc, rot=(0, 0, rot))
    box((2.0, 4.0, 2.2), (0, 0.6, 1.4), m=mat('#f2f6fa', 0.4), parent=p, bevel=0.06)
    box((1.9, 1.5, 1.4), (0, -2.2, 1.0), m=mat('#d8dde4', 0.3, metal=0.3), parent=p, bevel=0.1)
    box((1.6, 0.05, 0.6), (0, -2.96, 1.3), m=mat('#2a3a4a', 0.05, spec=1.0), parent=p)
    for sx in (-1, 1):
        t = text3d("GELO", (sx * 1.02, 0.6, 1.6), rot=(math.pi / 2, 0, sx * math.pi / 2), size=0.5, m=mat('#3ab0e8', 0.3), font='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', extrude=0.02)
        t.parent = p
        for sy in (-2.2, 1.6):
            cyl(0.42, 0.3, (sx * 0.95, sy, 0.42), (0, math.pi / 2, 0), m='#141414', parent=p)
    return p

def trash_bag(loc, s=1.0, seed=0, rot=0):
    p = empty("bag", loc, rot=(0, 0, rot))
    m = mat('#151518', 0.25, spec=0.8)
    rnd = random.Random(seed)
    sphere(1, (0, 0, 0.25 * s), (0.32 * s, 0.26 * s, 0.26 * s), m, p)
    for i in range(3):
        sphere(0.14 * s, (rnd.uniform(-0.15, 0.15) * s, rnd.uniform(-0.1, 0.1) * s, (0.3 + rnd.uniform(0, 0.1)) * s), m=m, parent=p, seg=16)
    cone(0.06 * s, 0.02 * s, 0.12 * s, (0, 0, 0.55 * s), m=m, parent=p)
    return p

def pine(loc, s=1.0, color='#1f5a3a'):
    p = empty("pine", loc)
    cyl(0.12 * s, 1.0 * s, (0, 0, 0.5 * s), m='#6a4228', parent=p)
    for i in range(4):
        cone((0.9 - i * 0.18) * s, 0, 1.1 * s, (0, 0, (1.0 + i * 0.6) * s), m=mat(color, 0.8), parent=p, verts=20)
    return p

def pew(loc, rot=0, w=2.4):
    p = empty("pew", loc, rot=(0, 0, rot))
    box((w, 0.45, 0.08), (0, 0, 0.45), m='#6a3e22', parent=p, bevel=0.02)
    box((w, 0.08, 0.6), (0, 0.22, 0.8), m='#6a3e22', parent=p, bevel=0.02)
    for sx in (-1, 1):
        box((0.08, 0.5, 0.9), (sx * w / 2, 0.02, 0.45), m='#5a3218', parent=p)
    return p

def stained_glass(loc, w=1.4, h=2.6, seed=0):
    p = empty("glass", loc)
    rnd = random.Random(seed)
    cols = ['#e83a3a', '#3a7ae8', '#ffd23f', '#3ac86a', '#b05ae8']
    nx, ny = 4, 7
    for i in range(nx):
        for j in range(ny):
            box((w / nx - 0.03, 0.04, h / ny - 0.03), (-w / 2 + w / nx * (i + 0.5), 0, h / ny * (j + 0.5)), m=mat(rnd.choice(cols), 0.3, emit=1.6), parent=p)
    box((w + 0.1, 0.06, 0.08), (0, -0.02, h), m='#3a3a3a', parent=p)
    return p


# ============================================================ Breaking Bad
def rv(loc, rot=0, smoke_pipe=True):
    """trailer (motorhome) bege com faixas marrons. Comprido em X, cabine em +X, porta/janelas no lado -Y."""
    p = empty("rv", loc, rot=(0, 0, rot))
    wh = mat('#efe4cc', 0.45); br = mat('#7a4a28', 0.5); og = mat('#c8803a', 0.5)
    glass = mat('#1e2a36', 0.08, spec=1.0); dk = mat('#2a2a2a', 0.8)
    W = 2.3
    box((5.0, W, 2.4), (-0.5, 0, 0.5 + 1.2), m=wh, parent=p, bevel=0.14)          # caixa x -3..2
    box((1.1, W * 0.96, 1.45), (2.5, 0, 0.5 + 0.72), m=wh, parent=p, bevel=0.16)   # cabine x 1.95..3.05
    box((1.2, W * 0.98, 0.75), (2.15, 0, 2.5), m=wh, parent=p, bevel=0.2)         # 'nariz' sobre a cabine
    box((0.05, W * 0.86, 0.6), (3.04, 0, 1.55), rot=(0, -0.25, 0), m=glass, parent=p)   # para-brisa
    for sy in (-1, 1):
        y = sy * (W / 2 + 0.004)
        for z, mm, hh in ((1.05, br, 0.16), (1.25, og, 0.08), (1.36, br, 0.05)):
            box((5.0, 0.02, hh), (-0.5, y, z), m=mm, parent=p)
            box((1.1, 0.02, hh), (2.5, y * 0.96 / 0.99, z), m=mm, parent=p)
        for x in (-2.3, -1.2):
            box((0.8, 0.03, 0.55), (x, y, 1.85), m=glass, parent=p)
        box((0.7, 0.03, 0.5), (2.5, y * 0.965, 1.6), m=glass, parent=p)         # janela da cabine
        for x in (-2.0, 1.4):
            cyl(0.42, 0.28, (x, sy * (W / 2 - 0.12), 0.42), (math.pi / 2, 0, 0), m=dk, parent=p)
            cyl(0.18, 0.3, (x, sy * (W / 2 - 0.1), 0.42), (math.pi / 2, 0, 0), m='#b8b8b8', parent=p)
    # porta (lado -Y)
    box((0.75, 0.04, 1.85), (0.2, -W / 2 - 0.01, 0.5 + 0.98), m=mat('#e6dac0', 0.5), parent=p, bevel=0.02)
    box((0.4, 0.04, 0.35), (0.2, -W / 2 - 0.035, 1.95), m=glass, parent=p)
    sphere(0.04, (0.48, -W / 2 - 0.05, 1.4), m='#c8c8c8', parent=p)
    box((0.8, 0.35, 0.08), (0.2, -W / 2 - 0.2, 0.3), m='#8a8a8a', parent=p)        # degrau
    box((0.9, 0.7, 0.3), (-1.5, 0, 3.05), m='#d8d8d8', parent=p, bevel=0.05)        # ar-condicionado
    for sy in (-1, 1):
        sphere(0.1, (3.06, sy * 0.75, 0.85), m=mat('#fff6c8', 0.2, emit=0.6), parent=p)
    box((0.1, W * 0.9, 0.25), (3.08, 0, 0.55), m='#bdbdbd', parent=p, bevel=0.03)   # para-choque
    if smoke_pipe:
        cyl(0.07, 0.6, (-2.4, 0.5, 3.1), m='#9a9a9a', parent=p)
    return p

def puffs(loc, f0, f1, color='#e8e8e8', n=10, seed=0, rise=2.5, s=0.35, spread=0.3, emit=0.0, every=None):
    """fumaca cartunesca (bolhas que sobem e crescem)"""
    rnd = random.Random(seed)
    m = mat(color, 0.95, emit=emit)
    every = every or max(1, (f1 - f0) // n)
    out = []
    for i in range(n):
        fa = f0 + i * every
        if fa >= f1:
            break
        o = sphere(1, loc, (0.01, 0.01, 0.01), m, seg=16)
        life_ = rnd.randint(40, 60)
        dx, dy = rnd.uniform(-spread, spread), rnd.uniform(-spread, spread)
        key(o, 'location', fa, loc); key(o, 'scale', fa, (0.01, 0.01, 0.01))
        key(o, 'location', fa + life_, (loc[0] + dx, loc[1] + dy, loc[2] + rise))
        sc = s * rnd.uniform(0.8, 1.2)
        key(o, 'scale', fa + int(life_ * 0.4), (sc, sc, sc)); key(o, 'scale', fa + life_, (0.01, 0.01, 0.01))
        out.append(o)
    return out

def crystals(loc, n=14, spread=0.25, seed=0, parent=None, s=1.0, color='#3cc0ff'):
    rnd = random.Random(seed)
    p = empty("cryst", loc, parent)
    m = mat(color, 0.12, emit=0.6, spec=1.0)
    for i in range(n):
        r = rnd.uniform(0.025, 0.05) * s
        cone(r, 0, r * rnd.uniform(2.0, 3.2), (rnd.uniform(-spread, spread), rnd.uniform(-spread * 0.6, spread * 0.6), r),
             (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(0, 6)), m=m, parent=p, verts=5)
    return p

def meth_tray(loc, parent=None, rot=0, seed=3):
    p = empty("tray", loc, parent, rot=(0, 0, rot))
    box((0.7, 0.45, 0.04), (0, 0, 0.02), m=mat('#c8ccd2', 0.25, metal=0.8), parent=p, bevel=0.01)
    rnd = random.Random(seed)
    m = mat('#3cc0ff', 0.1, emit=0.5, spec=1.0)
    for i in range(4):
        for j in range(3):
            box((0.15, 0.125, 0.025), (-0.24 + i * 0.16 + rnd.uniform(-0.01, 0.01), -0.135 + j * 0.135, 0.055),
                rot=(0, 0, rnd.uniform(-0.05, 0.05)), m=m, parent=p, bevel=0.006)
    return p

def flask(loc, liquid='#3cc0ff', parent=None, s=1.0):
    p = empty("flask", loc, parent)
    g = mat('#d8f0ff', 0.05, spec=1.0)
    cone(0.09 * s, 0.03 * s, 0.16 * s, (0, 0, 0.08 * s), m=g, parent=p)
    cyl(0.028 * s, 0.1 * s, (0, 0, 0.21 * s), m=g, parent=p)
    cone(0.082 * s, 0.05 * s, 0.07 * s, (0, 0, 0.037 * s), m=mat(liquid, 0.2, emit=0.4), parent=p)
    return p

def cactus(loc, s=1.0, seed=0):
    rnd = random.Random(seed)
    p = empty("cactus", loc)
    m = mat('#4a8a4a', 0.7)
    cyl(0.14 * s, 1.5 * s, (0, 0, 0.75 * s), m=m, parent=p)
    sphere(0.14 * s, (0, 0, 1.5 * s), m=m, parent=p)
    for sx in (-1, 1):
        h = rnd.uniform(0.6, 0.9) * s
        cyl(0.09 * s, 0.3 * s, (sx * 0.24 * s, 0, h), (0, math.pi / 2, 0), m=m, parent=p)
        cyl(0.09 * s, 0.4 * s, (sx * 0.38 * s, 0, h + 0.2 * s), m=m, parent=p)
        sphere(0.09 * s, (sx * 0.38 * s, 0, h + 0.4 * s), m=m, parent=p)
    return p

def desert_world(sky='#ffc98a', sand='#e7b77a', mesa='#c8724a', back=24, seed=2, n_cactus=6, xr=14, cact_y=(6, 16), strength=1.0):
    setup_render(sky=sky, sky_strength=strength)
    floor(sand, 160)
    rnd = random.Random(seed)
    for i in range(7):
        w, h = rnd.uniform(6, 14), rnd.uniform(3, 7)
        x = -36 + i * 12 + rnd.uniform(-3, 3)
        box((w, 5, h), (x, back + rnd.uniform(0, 8), h / 2), m=mat(mesa, 0.85), bevel=0.4)
        box((w * 1.06, 5.3, 0.5), (x, back + 0.0, h), m=mat('#a85a3a', 0.85), bevel=0.2) if rnd.random() < 0.5 else None
    for i in range(n_cactus):
        x = rnd.uniform(-xr, xr); y = rnd.uniform(*cact_y)
        cactus((x, y, 0), rnd.uniform(0.8, 1.3), i)
    for i in range(10):
        sphere(1, (rnd.uniform(-xr, xr), rnd.uniform(4, 18), 0), (rnd.uniform(0.2, 0.5), rnd.uniform(0.2, 0.4), rnd.uniform(0.12, 0.25)), mat('#b88a5a', 0.9), seg=12)

def chalkboard(loc, w=3.2, h=1.4, lines=(), rot=0, size=0.2, font=None):
    p = empty("board", loc, rot=(0, 0, rot))
    box((w + 0.16, 0.08, h + 0.16), (0, 0, 0), m='#8a5a32', parent=p, bevel=0.02)
    box((w, 0.04, h), (0, -0.04, 0), m=mat('#2a4a38', 0.9), parent=p)
    box((w, 0.12, 0.04), (0, -0.08, -h / 2 - 0.08), m='#8a5a32', parent=p)
    n = len(lines)
    for i, s in enumerate(lines):
        t = text3d(s, (0, -0.07, h / 2 - (i + 0.8) * (h / max(n, 1)) * 0.9), size=size, m=mat('#f2f2ea', 0.9, emit=0.15), parent=p, extrude=0.003, font=font)
    return p

def sedan(loc, rot=0, color='#2a5aa8', parent=None):
    """carro simples. Frente para -Y."""
    p = empty("sedan", loc, parent, rot=(0, 0, rot))
    body = mat(color, 0.25, metal=0.4, spec=0.7)
    glass = mat('#1a2a3a', 0.05, spec=1.0)
    L, Wd = 4.2, 1.75
    box((Wd, L, 0.55), (0, 0, 0.6), m=body, parent=p, bevel=0.12)
    box((Wd * 0.9, L * 0.45, 0.45), (0, 0.15, 1.08), m=body, parent=p, bevel=0.14)
    box((Wd * 0.84, 0.05, 0.34), (0, 0.15 - L * 0.225 - 0.02, 1.08), rot=(-0.5, 0, 0), m=glass, parent=p)
    box((Wd * 0.84, 0.05, 0.32), (0, 0.15 + L * 0.225 + 0.02, 1.08), rot=(0.5, 0, 0), m=glass, parent=p)
    for sx in (-1, 1):
        box((0.04, L * 0.38, 0.3), (sx * Wd * 0.455, 0.15, 1.1), m=glass, parent=p)
        for sy in (-1, 1):
            cyl(0.33, 0.24, (sx * Wd / 2 * 0.92, sy * L * 0.31, 0.34), (0, math.pi / 2, 0), m='#1a1a1a', parent=p)
            cyl(0.15, 0.26, (sx * Wd / 2 * 0.93, sy * L * 0.31, 0.34), (0, math.pi / 2, 0), m='#c8c8c8', parent=p)
        sphere(0.1, (sx * Wd * 0.34, -L / 2 + 0.02, 0.7), (1, 0.4, 0.8), mat('#fff6d0', 0.2, emit=1.0), p)
        sphere(0.08, (sx * Wd * 0.36, L / 2 - 0.02, 0.7), (1, 0.4, 0.8), mat('#e02020', 0.3, emit=0.6), p)
    for sy in (-1, 1):
        box((Wd * 1.02, 0.12, 0.16), (0, sy * L / 2, 0.42), m='#bdbdbd', parent=p, bevel=0.04)
    return p

def light_bar(parent, loc=(0, 0.15, 1.33)):
    p = empty("lbar", loc, parent)
    box((1.2, 0.25, 0.12), (0, 0, 0), m='#333333', parent=p, bevel=0.03)
    r = box((0.5, 0.22, 0.12), (-0.3, 0, 0.03), m=mat('#ff2a2a', 0.2, emit=3), parent=p, bevel=0.03)
    b = box((0.5, 0.22, 0.12), (0.3, 0, 0.03), m=mat('#2a6aff', 0.2, emit=3), parent=p, bevel=0.03)
    return p

def police_lights(f0, f1, loc_r, loc_b, energy=400, every=8):
    lr = point(loc_r, energy, '#ff2020', 0.3); lb = point(loc_b, energy, '#2050ff', 0.3)
    for i, f in enumerate(range(f0, f1 + 1, every)):
        on = i % 2 == 0
        lr.data.energy = energy if on else 0; lr.data.keyframe_insert('energy', frame=f)
        lb.data.energy = 0 if on else energy; lb.data.keyframe_insert('energy', frame=f)
    for l in (lr, lb):
        for fc in l.data.animation_data.action.fcurves:
            for k in fc.keyframe_points:
                k.interpolation = 'CONSTANT'
    return lr, lb

def xray_box(loc, rot=0, spot=True):
    p = empty("xray", loc, rot=(0, 0, rot))
    box((0.95, 0.08, 0.8), (0, 0, 0), m='#d8d8d8', parent=p, bevel=0.02)
    box((0.85, 0.02, 0.7), (0, -0.045, 0), m=mat('#dff0ff', 0.4, emit=1.6), parent=p)
    lung = mat('#2a3a4a', 0.6)
    for sx in (-1, 1):
        sphere(1, (sx * 0.17, -0.06, -0.02), (0.13, 0.01, 0.25), lung, p)
    box((0.04, 0.012, 0.5), (0, -0.06, 0.05), m='#8aa0b8', parent=p)
    for i in range(5):
        torus(0.27, 0.008, (0, -0.062, 0.18 - i * 0.08), (math.pi / 2, 0, 0), m='#9ab0c8', parent=p, scale=(1, 0.35, 1))
    if spot:
        sphere(0.05, (-0.2, -0.07, 0.08), (1, 0.2, 1), mat('#f2f2f2', 0.4, emit=2.0), p)
    return p

def pt_tile(sym, num, loc, size=0.8, rot=(math.pi / 2, 0, 0), parent=None, font=None):
    """quadrado verde de tabela periodica"""
    p = empty("tile", loc, parent, rot)
    box((size, size, size * 0.12), (0, 0, 0), m=mat('#1f6a3a', 0.45), parent=p, bevel=size * 0.03)
    box((size * 0.9, size * 0.9, size * 0.02), (0, 0, size * 0.06), m=mat('#2f8a4a', 0.45), parent=p)
    text3d(sym, (0, -size * 0.12, size * 0.075), (0, 0, 0), size=size * 0.55, m=mat('#ffffff', 0.4, emit=0.4), parent=p, extrude=size * 0.01, font=font)
    text3d(str(num), (size * 0.28, size * 0.3, size * 0.075), (0, 0, 0), size=size * 0.16, m=mat('#ffffff', 0.4, emit=0.4), parent=p, extrude=size * 0.005, font=font)
    return p

def wheelchair(loc, rot=0, bell=True, bell_side=1):
    """cadeira de rodas; assento no z=0.5, sentado olha para -Y local. Sino na ponta do braco (lado bell_side)."""
    p = empty("wchair", loc, rot=(0, 0, rot))
    met = mat('#b8bcc4', 0.25, metal=0.8)
    box((0.5, 0.48, 0.06), (0, 0, 0.47), m='#2a2a2e', parent=p, bevel=0.02)
    box((0.5, 0.05, 0.55), (0, 0.24, 0.8), m='#2a2a2e', parent=p, bevel=0.02)
    for sx in (-1, 1):
        torus(0.3, 0.025, (sx * 0.31, 0.05, 0.32), (0, math.pi / 2, 0), m='#1a1a1a', parent=p)
        cyl(0.02, 0.06, (sx * 0.31, 0.05, 0.32), (0, math.pi / 2, 0), m=met, parent=p)
        for a in range(4):
            box((0.012, 0.56, 0.012), (sx * 0.31, 0.05, 0.32), rot=(a * math.pi / 4, 0, 0), m=met, parent=p)
        cyl(0.07, 0.04, (sx * 0.2, -0.3, 0.07), (0, math.pi / 2, 0), m='#1a1a1a', parent=p)
        box((0.05, 0.5, 0.04), (sx * 0.27, -0.07, 0.68), m='#2a2a2e', parent=p, bevel=0.015)
        cyl(0.015, 0.2, (sx * 0.27, -0.24, 0.58), m=met, parent=p)
        cyl(0.015, 0.6, (sx * 0.22, 0.27, 0.95), (0.15, 0, 0), m=met, parent=p)
    box((0.3, 0.1, 0.02), (0, -0.4, 0.15), m=met, parent=p)
    if bell:
        bx = bell_side * 0.27
        cyl(0.038, 0.012, (bx, -0.27, 0.706), m=met, parent=p)
        sphere(1, (bx, -0.27, 0.715), (0.036, 0.036, 0.03), mat('#e8c34a', 0.2, metal=0.9), p)
        sphere(0.01, (bx, -0.27, 0.748), m=met, parent=p)
    return p

def pollos_store(loc=(0, 0, 0), back_y=2.5, font=None):
    """Los Pollos Hermanos: parede amarela, letreiro, cardapio e balcao (balcao em y=0.4..1.0)"""
    p = empty("pollos", loc)
    box((14, 0.2, 6), (0, back_y + 0.1, 3), m=mat('#f2c84a', 0.6), parent=p)
    box((14, 0.22, 0.5), (0, back_y + 0.08, 0.25), m='#c0392b', parent=p)
    box((4.4, 0.1, 0.75), (0, back_y - 0.02, 3.15), m='#c0392b', parent=p, bevel=0.04)
    text3d("LOS POLLOS HERMANOS", (0, back_y - 0.09, 3.06), size=0.3, m=mat('#ffe27a', 0.4, emit=0.6), parent=p, extrude=0.02, font=font)
    for x in (-2.2, 2.2):
        box((1.6, 0.08, 0.9), (x, back_y - 0.02, 2.2), m='#2a2a2e', parent=p, bevel=0.03)
        for i in range(4):
            box((1.2, 0.02, 0.06), (x, back_y - 0.07, 2.5 - i * 0.18), m=mat('#ffe27a', 0.5, emit=0.3), parent=p)
    # logo (frango)
    cyl(0.4, 0.06, (0, back_y - 0.05, 4.05), (math.pi / 2, 0, 0), m='#c0392b', parent=p)
    sphere(1, (0, back_y - 0.1, 4.05), (0.2, 0.04, 0.16), '#ffe27a', p)
    sphere(0.08, (0.12, back_y - 0.11, 4.2), m='#ffe27a', parent=p)
    # balcao
    box((4.2, 0.6, 0.78), (0, 0.7, 0.39), m=mat('#c0392b', 0.45), parent=p, bevel=0.03)
    box((4.3, 0.7, 0.06), (0, 0.7, 0.81), m=mat('#e8e2d0', 0.3), parent=p, bevel=0.02)
    box((0.4, 0.32, 0.25), (1.4, 0.7, 0.97), m='#3a3a3e', parent=p, bevel=0.03)      # caixa registradora
    box((0.3, 0.02, 0.18), (1.4, 0.55, 1.08), rot=(0.3, 0, 0), m=mat('#7affaa', 0.3, emit=0.6), parent=p)
    # balde de frango
    cone(0.13, 0.17, 0.25, (-1.2, 0.7, 0.97), m='#f2f2ee', parent=p)
    cyl(0.171, 0.06, (-1.2, 0.7, 1.0), m='#c0392b', parent=p)
    for i in range(5):
        sphere(0.06, (-1.2 + math.cos(i * 1.3) * 0.08, 0.7 + math.sin(i * 1.3) * 0.08, 1.11), m='#c8782a', parent=p)
    return p

def lab_tank(loc, r=0.55, h=2.4, parent=None):
    p = empty("tank", loc, parent)
    st = mat('#c8ccd2', 0.18, metal=0.9, spec=0.8)
    cyl(r, h, (0, 0, h / 2 + 0.25), m=st, parent=p)
    sphere(1, (0, 0, h + 0.25), (r, r, r * 0.45), st, p)
    for a in range(3):
        cyl(0.04, 0.3, (r * 0.7 * math.cos(a * 2.1), r * 0.7 * math.sin(a * 2.1), 0.13), m=st, parent=p)
    cyl(0.05, 0.6, (0, 0, h + 0.5), m=st, parent=p)
    box((0.25, 0.04, 0.18), (0, -r - 0.01, h * 0.6), m='#2a2a2e', parent=p)
    sphere(0.025, (0.06, -r - 0.04, h * 0.6), m=mat('#4aff6a', 0.3, emit=3), parent=p)
    return p

def superlab(back_y=3.0, font=None):
    setup_render(sky='#d8e4ec', sky_strength=0.8)
    checker_floor('#d8c87a', '#c8b86a', size=40, scale=0.9)
    box((20, 0.2, 7), (0, back_y + 0.6, 3.5), m='#b8c0c8')
    for i, x in enumerate((-3.6, -2.2, 2.2, 3.6)):
        lab_tank((x, back_y - 0.3, 0), 0.55, 2.2)
    # passarela e tubos
    box((8, 0.8, 0.06), (0, back_y - 0.4, 3.1), m='#9aa0a8')
    for x in range(-4, 5):
        cyl(0.025, 0.9, (x, back_y - 0.8, 3.55), m='#e8c34a')
    cyl(0.025, 8, (0, back_y - 0.8, 4.0), (0, math.pi / 2, 0), m='#e8c34a')
    for z in (2.6, 2.75):
        cyl(0.06, 12, (0, back_y + 0.35, z), (0, math.pi / 2, 0), m=mat('#c8ccd2', 0.2, metal=0.9))

def lab_table(loc, rot=0, w=1.8, d=0.8, flasks=True, seed=0):
    p = empty("ltable", loc, rot=(0, 0, rot))
    st = mat('#c8ccd2', 0.2, metal=0.85)
    box((w, d, 0.05), (0, 0, 0.92), m=st, parent=p, bevel=0.01)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.03, 0.9, (sx * (w / 2 - 0.08), sy * (d / 2 - 0.08), 0.45), m=st, parent=p)
    box((w - 0.1, d - 0.1, 0.03), (0, 0, 0.3), m=st, parent=p)
    if flasks:
        rnd = random.Random(seed)
        for i, col in enumerate(('#3cc0ff', '#ffd23f', '#7aff8a')):
            flask((-w / 2 + 0.3 + i * 0.35, rnd.uniform(-0.1, 0.15), 0.945), col, p)
    return p

def money_pile(loc, w=1.6, d=1.0, h=1.0, rot=0, seed=0):
    """cubo de dinheiro: nucleo + macos nas faces visiveis"""
    p = empty("mpile", loc, rot=(0, 0, rot))
    rnd = random.Random(seed)
    g1, g2, band = mat('#4fae5a', 0.6), mat('#5fc06a', 0.6), mat('#efe8d0', 0.6)
    box((w - 0.02, d - 0.02, h - 0.02), (0, 0, h / 2), m=g1, parent=p)
    bw, bh = 0.2, 0.07
    nx, nz = int(w / bw), int(h / bh)
    for i in range(nx):
        for k in range(nz):
            x = -w / 2 + bw * (i + 0.5); z = bh * (k + 0.5)
            box((bw - 0.008, 0.1, bh - 0.006), (x, -d / 2 + 0.04 + rnd.uniform(-0.01, 0.01), z), m=g1 if (i + k) % 2 else g2, parent=p, bevel=0.006)
            box((0.04, 0.102, bh - 0.004), (x, -d / 2 + 0.04, z), m=band, parent=p)
    ny = int(d / 0.1)
    for i in range(nx):
        for j in range(ny):
            box((bw - 0.008, 0.095, bh), (-w / 2 + bw * (i + 0.5), -d / 2 + 0.1 * (j + 0.5), h - bh / 2 + 0.005), m=g1 if (i + j) % 2 else g2, parent=p, bevel=0.006)
    return p

def toilet(loc, rot=0):
    """vaso: assento z=0.43; sentado olha para -Y local"""
    p = empty("toilet", loc, rot=(0, 0, rot))
    w = mat('#f4f4f2', 0.2, spec=0.8)
    cyl(0.16, 0.38, (0, -0.05, 0.19), m=w, parent=p, scale=(1, 1.25, 1))
    torus(0.17, 0.035, (0, -0.07, 0.4), m=w, parent=p, scale=(1, 1.3, 1))
    box((0.42, 0.2, 0.42), (0, 0.27, 0.62), m=w, parent=p, bevel=0.04)
    box((0.45, 0.23, 0.04), (0, 0.27, 0.85), m=w, parent=p, bevel=0.015)
    return p

def book(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), color='#3a7a4a', s=1.0):
    p = empty("book", loc, parent, rot)
    box((0.2 * s, 0.03 * s, 0.26 * s), (0, 0, 0), m=mat(color, 0.6), parent=p, bevel=0.005)
    box((0.19 * s, 0.032 * s, 0.25 * s), (0.006 * s, 0, 0), m='#f6f0dc', parent=p)
    return p

def cabin(loc, rot=0):
    p = empty("cabin", loc, rot=(0, 0, rot))
    wood = mat('#7a5232', 0.8); wood2 = mat('#6a4428', 0.8); snow = mat('#ffffff', 0.7)
    for k in range(9):
        box((4.0, 3.0, 0.28), (0, 0, 0.14 + k * 0.28), m=wood if k % 2 else wood2, parent=p, bevel=0.1)
    for sx in (-1, 1):
        box((2.5, 3.6, 0.15), (sx * 1.05, 0, 2.95), rot=(0, sx * 0.55, 0), m=wood2, parent=p)
        box((2.5, 3.6, 0.12), (sx * 1.06, 0, 3.07), rot=(0, sx * 0.55, 0), m=snow, parent=p, bevel=0.05)
    door((0.9, -1.52, 0), 0, '#4a3020').parent = p
    w = window((-0.8, -1.53, 1.35), 0, 0.9, 0.7, '#ffcf6a', emit=2.0); w.parent = p
    cyl(0.18, 1.2, (-1.3, 0.6, 3.8), m='#5a5a5a', parent=p)
    return p

def snow_pine(loc, s=1.0):
    pine(loc, s, '#1f4a32')
    for k, z in enumerate((1.3, 2.0, 2.6)):
        cone((0.75 - k * 0.2) * s, 0, 0.25 * s, (loc[0], loc[1], loc[2] + z * s), m='#ffffff')

def snowfall(n, center, area=(6, 4), h=4.0, f0=1, f1=200, seed=0, r=0.025, avoid=()):
    rnd = random.Random(seed)
    m = mat('#ffffff', 0.5, emit=0.5)
    for i in range(n):
        x = center[0] + rnd.uniform(-area[0] / 2, area[0] / 2); y = center[1] + rnd.uniform(-area[1] / 2, area[1] / 2)
        if any(math.hypot(x - ax, y - ay) < ar for ax, ay, ar in avoid):
            continue
        z0 = rnd.uniform(0, h); spd = rnd.uniform(0.012, 0.022)
        o = sphere(r, (x, y, z0), m=m, seg=8)
        # cai e volta ao topo (ciclos)
        f = f0; z = z0
        key(o, 'location', f, (x, y, z), 'LINEAR')
        while f < f1:
            dt = int(z / spd)
            if f + dt > f1:
                dt = f1 - f; key(o, 'location', f + dt, (x + 0.1, y, z - dt * spd), 'LINEAR'); break
            key(o, 'location', f + dt, (x + 0.1, y, 0.0), 'CONSTANT')
            f += dt + 1; z = h
            key(o, 'location', f, (x, y, z), 'LINEAR')

def phone(parent, loc=(0, 0, -0.47), rot=(0, 0, 0)):
    return box((0.06, 0.02, 0.13), loc, rot=rot, m=mat('#1a1a1a', 0.3), parent=parent, bevel=0.01)

def handgun(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    p = empty("gun", loc, parent, rot)
    m = mat('#2a2a2e', 0.35, metal=0.6)
    box((0.03 * s, 0.17 * s, 0.05 * s), (0, -0.05 * s, 0), m=m, parent=p, bevel=0.008)
    box((0.028 * s, 0.05 * s, 0.11 * s), (0, 0.02 * s, -0.06 * s), rot=(-0.25, 0, 0), m=m, parent=p, bevel=0.008)
    return p

def kitchen(back_y=2.5, wall='#e8dcc0', counter='#f2f0ea', cab='#8a6a4a'):
    """cozinha da casa dos White (balcao no fundo)"""
    box((16, 0.2, 7), (0, back_y + 0.1, 3.5), m=wall)
    box((5, 0.6, 0.9), (0, back_y - 0.3, 0.45), m=cab, bevel=0.02)
    box((5.1, 0.7, 0.05), (0, back_y - 0.32, 0.93), m=counter, bevel=0.01)
    box((5, 0.35, 0.7), (0, back_y - 0.18, 2.1), m=cab, bevel=0.02)
    window((0, back_y - 0.02, 1.55), 0, 1.2, 0.6, '#ffe2a8', emit=0.8)
    for x in (-1.6, -0.6, 1.0, 1.9):
        sphere(0.02, (x, back_y - 0.62, 0.7), m='#c8c8c8')
