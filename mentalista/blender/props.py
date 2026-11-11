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
