# Supernatural - definicao de cada shot (cenario + personagens + animacao + camera)
# Convencao: personagem com rot=θ olha para (sin θ, -cos θ). θ=0 -> camera (-Y); θ=+π/2 -> +X; θ=-π/2 -> -X.
import bpy, math, random
from mathutils import Vector
from lib import *
from props import *

BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PI = math.pi

class Ctx:
    def __init__(self, n, f0, env):
        self.n, self.f0, self.env = n, f0, env
    def g(self, f):
        return self.f0 + f - 1

def talk(c, ch, fa=1, fb=None, gain=1.0):
    fb = fb or c.n
    for f in range(fa, fb + 1, 2):
        a = c.env[c.g(f)] if 0 <= c.g(f) < len(c.env) else 0
        ch.mouth.scale = (1 - 0.15 * a, 1, 0.35 + 1.9 * min(1, a * gain))
        ch.mouth.keyframe_insert('scale', frame=f)

def life(c, ch, seed=0, amp=1.0):
    ch.idle(1, c.n + 5, amp, seed)
    ch.auto_blink(1, c.n, seed)

def cam_move(cam, tgt, c, p0, p1, t0=None, t1=None, fa=1, fb=None):
    fb = fb or c.n
    key(cam, 'location', fa, p0); key(cam, 'location', fb, p1)
    if t0 is not None:
        key(tgt, 'location', fa, t0); key(tgt, 'location', fb, t1 if t1 is not None else t0)

def room(wall='#7ecbff', wall2=None, fl1='#f6b33c', fl2='#ffd36a', back_y=3.0, side_x=None, w=16, h=7, sq=0.7, trim='#ffffff'):
    checker_floor(fl1, fl2, size=40, scale=sq)
    if wall2:
        stripes_wall(wall, wall2, w=w, h=h, n=int(w / 0.8), loc=(0, back_y, 0), horizontal=False)
    else:
        box((w, 0.2, h), (0, back_y + 0.1, h / 2), m=wall)
    box((w, 0.25, 0.3), (0, back_y - 0.05, 0.15), m=trim)
    if side_x is not None:
        box((0.2, 12, h), (side_x, back_y - 6, h / 2), m=wall)

def night_world(sky='#0d1b3d', amb=0.35):
    setup_render(sky=sky, sky_strength=amb)

def little_dean(**kw):
    d = dict(name='ldean', hair='#a07a48', hair_style='dean', eyes='#3f9a5a', jacket='#4a7ac0', vest=None,
             shirt='#4a7ac0', pants='#4a7ac0', shoes='#d8d8e8', collar=False, height=0.62, body_w=0.78, brows='#8a6a3a')
    d.update(kw); return Char(**d)

def baby(parent=None, loc=(0, 0, 0)):
    p = empty("baby", loc, parent)
    sphere(1, (0, 0, 0), (0.12, 0.2, 0.1), mat('#bfe0ff', 0.8), p)
    sphere(0.075, (0, -0.17, 0.04), m=SKIN, parent=p)
    for sx in (-1, 1):
        sphere(0.008, (sx * 0.025, -0.235, 0.06), m='#222222', parent=p, seg=8)
    return p

def stars(n=60, y=30, seed=1, zr=(5, 22), xr=20):
    rnd = random.Random(seed)
    for i in range(n):
        sphere(0.06, (rnd.uniform(-xr, xr), y, rnd.uniform(*zr)), m=mat('#ffffff', emit=4), seg=8)

def road(length=80, y0=-10, width=4.0):
    box((width, length, 0.02), (0, y0 + length / 2, 0.01), m=mat('#2a2a30', 0.8))
    for i in range(int(length / 3)):
        box((0.12, 1.4, 0.022), (0, y0 + i * 3, 0.012), m=mat('#ffd23f', 0.6))

def ghost(loc, rot=0):
    g = generic_person(301, loc, rot=rot, skin='#cfe8ff', hair='#e8f4ff', jacket='#d8ecff', pants='#d8ecff',
                       shoes='#d8ecff', eye_mode='white', female=True, hair_style='long')
    for o in bpy.data.objects:
        if o.name.startswith('p301') or (o.parent and o.parent.name.startswith('p301')):
            pass
    return g

# ============================================================================ SHOTS
def s01(c):
    night_world('#2a0f05', 0.3)
    floor('#5a3a2a', 40)
    box((12, 0.2, 4), (0, 2.2, 2), m=mat('#c9b48a', 0.85))
    box((0.2, 12, 4), (-1.8, -2, 2), m=mat('#b8a47a', 0.85))
    door((0.4, 2.1, 0), 0, '#6a4a2a')
    fp, fl = flames((0.4, 2.0, 0), n=10, spread=0.55, h=1.4, seed=1)
    flicker(fl, 1, c.n, 1)
    fp2, fl2 = flames((-1.5, 1.4, 0), n=6, spread=0.4, h=1.0, seed=2)
    flicker(fl2, 1, c.n, 2)
    d = little_dean(loc=(0, 0.2, 0))
    life(c, d, 1)
    d.brows_set(6, 0.4)
    key(d.mouth, 'scale', 1, (1, 1, 0.4)); key(d.mouth, 'scale', 20, (1.1, 1, 1.0))
    point((0.4, 1.4, 1.2), 250, '#ff7a2a', 0.8)
    point((-1.3, 1.0, 1.0), 120, '#ff8a3a', 0.6)
    point((0, -1.5, 1.6), 25, '#ffd0a0', 1.0)
    cam, t = camera((0, -2.2, 1.1), (0, 0.4, 0.9), 35)
    cam_move(cam, t, c, (0, -2.6, 1.15), (0, -1.5, 1.05), (0, 0.4, 0.95), (0, 0.2, 0.92))

def s02(c):
    night_world('#2a0f05', 0.3)
    floor('#5a3a2a', 40)
    box((12, 0.2, 4), (0, 2.6, 2), m=mat('#c9b48a', 0.85))
    fp, fl = flames((0, 2.4, 0), n=14, spread=1.6, h=1.6, seed=3)
    flicker(fl, 1, c.n, 3)
    jn = john(loc=(0.35, 0.9, 0), rot=-PI * 0.42)
    d = little_dean(loc=(-0.35, 0.5, 0), rot=PI * 0.42)
    life(c, jn, 2); life(c, d, 3)
    b = baby(loc=(0.05, 0.62, 1.0))
    b.rotation_euler = (0, 0, PI / 2)
    f1 = int(c.n * 0.25)
    jn.arm(0, 6, (-1.0, 0, 0.25)); jn.arm(1, 6, (-1.0, 0, -0.25))
    d.arm(0, f1, (-1.1, 0, 0.3)); d.arm(1, f1, (-1.1, 0, -0.3))
    key(b, 'location', 1, (0.1, 0.72, 1.0)); key(b, 'location', f1, (0.1, 0.72, 1.0))
    key(b, 'location', f1 + 18, (-0.12, 0.52, 0.66))
    jn.arm(0, f1 + 22, (-0.3, 0, 0)); jn.arm(1, f1 + 22, (-1.6, 0, -0.5))   # aponta p/ fora
    talk(c, jn, f1 + 10, c.n, 1.0)
    jn.brows_set(10, -0.35)
    d.brows_set(10, 0.4)
    # Dean vira e corre para a camera
    f2 = int(c.n * 0.7)
    key(d.root, 'rotation_euler', f2, (0, 0, PI * 0.42)); key(d.root, 'rotation_euler', f2 + 8, (0, 0, 0))
    b.parent = None
    key(b, 'location', f2, (-0.12, 0.52, 0.66)); key(b, 'location', f2 + 8, (-0.35, 0.27, 0.64))
    d.walk(f2 + 8, c.n, (-0.35, 0.5, 0), (-0.25, -0.8, 0), 3.0, 0.02)
    key(b, 'location', c.n, (-0.25, -1.03, 0.64))
    key(b, 'rotation_euler', f2, (0, 0, PI / 2)); key(b, 'rotation_euler', f2 + 8, (0, 0, 0))
    d.arm(0, c.n, (-1.1, 0, 0.3)); d.arm(1, c.n, (-1.1, 0, -0.3))
    point((0, 1.8, 1.2), 350, '#ff7a2a', 1.0)
    point((0, -1.5, 1.8), 40, '#ffd0a0', 1.0)
    cam, t = camera((0, -2.4, 1.2), (0, 0.6, 0.95), 32)
    cam_move(cam, t, c, (0.2, -2.6, 1.25), (0, -2.9, 1.1), (0, 0.7, 1.0), (-0.2, 0.0, 0.8))

def s03(c):
    night_world('#1a0805', 0.25)
    floor('#6a5a7a', 30)
    H = 2.6
    box((6, 0.2, H), (0, 1.6, H / 2), m=mat('#a8c8e8', 0.85))
    box((0.2, 6, H), (-1.6, 0, H / 2), m=mat('#9ab8d8', 0.85))
    box((6, 6, 0.2), (0, 0, H + 0.1), m=mat('#e8e0d0', 0.85))          # teto
    crib((0.2, 0.6, 0), PI / 2)
    # Mary presa ao teto (de frente para baixo)
    mr = mary(loc=(0, 0, 0))
    mr.root.location = (0.2, 1.1, H - 0.14)
    mr.root.rotation_euler = (PI / 2, 0, 0)
    mr.brows_set(1, 0.45, 1)
    key(mr.mouth, 'scale', 1, (1.2, 1, 1.2))
    fp, fl = flames((0.2, 0.55, H - 0.02), n=12, spread=0.9, h=0.7, seed=5, rot=(PI, 0, 0))
    flicker(fl, 1, c.n, 5)
    # demonio de olhos amarelos nas sombras (no fim)
    f1 = int(c.n * 0.68)
    az = generic_person(310, (-1.0, 1.1, 0), rot=PI * 0.2, eye_mode='yellow', jacket='#1a1a1a', pants='#1a1a1a',
                        hair='#2a2a2a', hair_style='short', female=False, skin='#a88a78')
    hide_between(az.root, f1, None)
    point((0.2, 0.6, 1.8), 260, '#ff7a2a', 1.0)
    point((-1.0, 0.4, 1.4), 0, '#ffd23f', 0.3)
    cam, t = camera((0.2, -1.6, 1.0), (0.2, 0.9, 2.3), 30)
    key(cam, 'location', 1, (0.2, -1.4, 0.9)); key(t, 'location', 1, (0.2, 1.0, 2.4))
    key(cam, 'location', f1 - 4, (0.3, -1.0, 1.0)); key(t, 'location', f1 - 4, (0.2, 1.0, 2.4))
    key(cam, 'location', f1 + 6, (0.4, -1.4, 1.5)); key(t, 'location', f1 + 6, (-0.9, 1.1, 1.4))
    key(cam, 'location', c.n, (0.2, -0.9, 1.45)); key(t, 'location', c.n, (-0.95, 1.1, 1.42))

def s04(c):
    night_world('#141a3a', 0.35)
    floor('#2a3a2a', 120)
    road(120, -20, 4.0)
    box((120, 0.2, 40), (0, 60, 15), m=mat('#1a2250', 1.0, emit=0.6))
    stars(70, 59, 4)
    car = impala((0.9, 6, 0), PI)                       # indo para longe da camera
    key(car, 'location', 1, (0.9, 4, 0), 'LINEAR'); key(car, 'location', c.n, (0.9, 16, 0), 'LINEAR')
    # placa de motel em neon
    mp = empty("motel", (-3.0, 12, 0))
    cyl(0.12, 4.0, (0, 0, 2.0), m='#555555', parent=mp)
    box((2.6, 0.2, 1.0), (0, 0, 4.2), m='#1a1a2a', parent=mp, bevel=0.05)
    t1 = text3d("MOTEL", (0, -0.12, 4.25), size=0.55, m=mat('#ff3a8a', emit=6), font=BOLD, extrude=0.02); t1.parent = mp
    t2 = text3d("VAGAS", (0, -0.12, 3.5), size=0.3, m=mat('#3affd0', emit=6), font=BOLD, extrude=0.02); t2.parent = mp
    box((6, 3, 2.6), (-6.0, 15, 1.3), m=mat('#c9a86a', 0.8), bevel=0.05)
    for i in range(4):
        box((0.6, 0.05, 1.6), (-8 + i * 1.4, 13.48, 0.8), m=mat('#8a3a2a', 0.6))
        box((0.5, 0.05, 0.4), (-8 + i * 1.4 + 0.6, 13.48, 1.6), m=mat('#ffd27a', emit=1.2))
    for x in (-8, 8):
        for y in range(0, 40, 10):
            tree((x, y, 0), 1.4, '#1f5a3a', seed=y + x)
    sun(rot=(0.9, 0.2, -0.6), energy=0.8, color='#8fb0ff')
    point((-3.0, 11.5, 4.0), 120, '#ff3a8a', 1.0)
    cam, t = camera((2.0, -3.5, 1.6), (0.9, 6, 0.8), 32)
    cam_move(cam, t, c, (2.2, -3.8, 1.4), (1.6, 2.0, 2.2), (0.9, 6, 0.8), (-1.5, 14, 2.6))

def s05(c):
    setup_render(sky='#ff9a5a')
    floor('#c9a45a', 80)
    box((80, 0.2, 30), (0, 30, 15), m=mat('#ffab6b', 1.0, emit=1.0))
    sphere(2.2, (5, 29, 3.5), m=mat('#fff0b0', emit=3))
    # cerca com latas
    for i in range(7):
        box((0.1, 0.1, 1.0), (-1.8 + i * 0.6, 3.0, 0.5), m='#7a5a3a')
    box((4.0, 0.1, 0.1), (0, 3.0, 0.95), m='#7a5a3a')
    cans = []
    for i in range(5):
        cn = cyl(0.09, 0.24, (-1.2 + i * 0.6, 3.0, 1.13), m=mat('#e04a3a', 0.3, metal=0.4))
        cans.append(cn)
    # saco de sal e fogueira com ossos
    box((0.35, 0.25, 0.45), (0.75, -0.2, 0.22), m='#efe6d0', bevel=0.08)
    text3d("SAL", (0.75, -0.33, 0.25), size=0.1, m='#3a3a3a', font=BOLD, extrude=0.005)
    fp, fl = flames((-0.9, 0.2, 0), n=6, spread=0.2, h=0.6, seed=7)
    flicker(fl, 1, c.n, 7)
    for i in range(4):
        cyl(0.03, 0.4, (-0.9, 0.2, 0.08), (PI / 2, 0, i * 0.8), m='#f2ead8')
    td = dean(loc=(0, 0, 0), height=0.85, rot=PI)
    life(c, td, 5)
    td.arm(1, 1, (-1.55, 0, 0.1)); td.arm(0, 1, (-1.45, 0, -0.35))
    sg = shotgun(td.arms[1], (0, 0, -0.42), (PI / 2, 0, 0))
    f1 = int(c.n * 0.35)
    for k, cn in enumerate(cans[:3]):
        fk = f1 + k * 14
        key(cn, 'location', fk, tuple(cn.location)); key(cn, 'location', fk + 8, (cn.location.x + 0.2, 3.5, 0.08))
        key(cn, 'rotation_euler', fk, (0, 0, 0)); key(cn, 'rotation_euler', fk + 8, (1.4, 0.5, 0))
    sun(rot=(1.1, 0.0, 2.8), energy=2.5, color='#ffc89a')
    point((0, -1.5, 2.0), 120, '#ffe0c0', 1.5)
    cam, t = camera((2.4, -1.2, 1.3), (-0.2, 1.2, 1.0), 30)
    cam_move(cam, t, c, (3.0, -2.0, 1.35), (2.5, -1.4, 1.3), (-0.5, 1.0, 1.0), (-0.5, 1.4, 1.0))

def s06(c):
    setup_render(sky='#8fd6ff')
    floor('#cfe8a0', 80)
    box((3.0, 30, 0.02), (0, 5, 0.01), m='#e8d6b0')
    # predio estilo campus (arcos)
    b = empty("bldg", (0, 5, 0))
    box((9, 1.5, 4.2), (0, 0, 2.1), m='#e8c99a', parent=b, bevel=0.05)
    box((9.6, 1.9, 0.5), (0, 0, 4.4), m='#c0603a', parent=b, bevel=0.05)
    for i in range(5):
        x = -3.2 + i * 1.6
        box((1.0, 0.1, 1.8), (x, -0.76, 1.0), m='#6a4a3a', parent=b)
        cyl(0.5, 0.12, (x, -0.77, 1.9), (PI / 2, 0, 0), m='#6a4a3a', parent=b)
    t1 = text3d("STANFORD", (0, -0.8, 3.4), size=0.6, m=mat('#8c1515', 0.4), font=BOLD, extrude=0.04); t1.parent = b
    for x in (-5.5, 5.5):
        palm((x, 3.5, 0), 1.0, 0.0, int(x))
    for i, (x, y) in enumerate([(-2.5, 1.5), (2.6, 2.2)]):
        p = generic_person(320 + i, (x, y, 0), rot=PI * (0.3 if x < 0 else -0.3))
        life(c, p, 320 + i)
    s = sam(loc=(0.0, -1.0, 0), rot=PI)
    s.walk(1, int(c.n * 0.6), (0.0, -1.2, 0), (0.0, 1.0, 0), 1.8)
    key(s.root, 'rotation_euler', int(c.n * 0.6), (0, 0, PI)); key(s.root, 'rotation_euler', int(c.n * 0.6) + 10, (0, 0, 0))
    s.auto_blink(1, c.n, 6)
    box((0.3, 0.12, 0.38), (0, 0.15, 0.35), m='#2a4a7a', parent=s.chest, bevel=0.05)   # mochila
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -3.5, 1.4), (0, 2, 1.6), 30)
    cam_move(cam, t, c, (0.6, -4.2, 1.2), (0.2, -1.6, 1.4), (0, 3.0, 2.4), (0, 1.0, 1.4))

def s07(c):
    night_world('#101830', 0.35)
    floor('#2a2e36', 60)
    box((60, 0.2, 30), (0, 14, 15), m=mat('#121a3a', 1.0, emit=0.5))
    stars(50, 13.8, 7, (3, 14), 12)
    box((8, 1.0, 3.0), (-1.5, 6, 1.5), m=mat('#8a7a6a', 0.8), bevel=0.05)
    for i in range(4):
        box((0.7, 0.05, 0.7), (-4 + i * 1.6, 5.48, 1.7), m=mat('#ffd27a', emit=1.4))
    car = impala((0.7, 1.4, 0), PI * 0.5 - 0.35)
    d = dean(loc=(-0.6, 0.0, 0), rot=PI * 0.15)
    life(c, d, 7)
    d.arm(0, 1, (0, -0.35, 0)); d.arm(1, 1, (0, 0.35, 0))
    f1 = int(c.n * 0.4)
    s = sam(loc=(-2.5, -0.3, 0), rot=PI / 2)
    s.walk(f1, int(c.n * 0.85), (-3.2, -0.3, 0), (-1.25, -0.2, 0), 1.8)
    key(s.root, 'rotation_euler', int(c.n * 0.85), (0, 0, PI / 2)); key(s.root, 'rotation_euler', int(c.n * 0.85) + 8, (0, 0, PI * 0.35))
    s.auto_blink(1, c.n, 8)
    d.look(f1 + 10, 0, -0.5)
    key(d.mouth, 'scale', int(c.n * 0.8), (1, 1, 0.35)); key(d.mouth, 'scale', int(c.n * 0.8) + 8, (1.4, 1, 0.5))
    sun(rot=(0.9, 0.2, -0.6), energy=0.9, color='#9fb4ff')
    point((-0.6, -1.2, 2.4), 120, '#ffd8a8', 1.0)
    point((1.0, -0.8, 1.6), 60, '#9fc4ff', 1.0)
    cam, t = camera((0.5, -4.5, 1.5), (0, 0.8, 1.0), 30)
    cam_move(cam, t, c, (1.2, -5.0, 1.3), (0.4, -3.6, 1.5), (0.3, 1.0, 0.9), (-0.7, 0.3, 1.2))

def s08(c):
    night_world('#1a0a10', 0.25)
    floor('#5a4a4a', 30)
    H = 2.6
    box((6, 0.2, H), (0, 1.8, H / 2), m=mat('#c9a8a0', 0.85))
    box((6, 6, 0.2), (0, 0, H + 0.1), m=mat('#e8e0d0', 0.85))
    bed((0.0, 0.8, 0), 0, '#ffffff', '#c06a8a')
    jess = Char(name='jess', hair='#e2c070', hair_style='curly_long', eyes='#4a7ab0', jacket='#f4f1ea', vest=None,
                dress='#f4f1ea', female=True, collar=False, body_w=0.9)
    jess.root.location = (0.0, 1.25, H - 0.14); jess.root.rotation_euler = (PI / 2, 0, 0)
    jess.brows_set(1, 0.45, 1); key(jess.mouth, 'scale', 1, (1.2, 1, 1.1))
    fp, fl = flames((0.0, 0.65, H - 0.02), n=12, spread=0.9, h=0.7, seed=9, rot=(PI, 0, 0))
    flicker(fl, 1, c.n, 9)
    s = sam(loc=(0, 0.6, 0.62))
    s.root.rotation_euler = (-PI / 2 + 0.25, 0, 0)    # deitado na cama, acordando
    s.root.location = (0.0, -0.15, 0.78)
    f1 = int(c.n * 0.3)
    for e in s.eyes:
        key(e, 'scale', 1, (1, 1, 0.1)); key(e, 'scale', f1, (1, 1, 0.1)); key(e, 'scale', f1 + 4, (1, 1, 1.15))
    key(s.mouth, 'scale', f1, (1, 1, 0.35)); key(s.mouth, 'scale', f1 + 8, (1.2, 1, 1.4))
    s.brows_set(f1 + 4, 0.45)
    point((0.0, 0.8, 1.9), 280, '#ff7a2a', 1.0)
    cam, t = camera((0.0, -1.8, 1.3), (0, 0.6, 1.6), 30)
    key(cam, 'location', 1, (0.6, -1.9, 1.0)); key(t, 'location', 1, (0, 1.0, 2.2))
    key(cam, 'location', f1, (0.5, -1.7, 1.1)); key(t, 'location', f1, (0, 1.0, 2.2))
    key(cam, 'location', c.n, (0.9, -0.2, 1.9)); key(t, 'location', c.n, (0, 1.05, 1.0))

def s09(c):
    setup_render(sky='#ff8a5a')
    floor('#c98a5a', 120)
    road(120, -20, 4.0)
    box((120, 0.2, 40), (0, 50, 15), m=mat('#ff9a6a', 1.0, emit=1.0))
    box((120, 0.2, 6), (0, 49.8, 1.5), m=mat('#ffc58a', 1.0, emit=1.0))
    sphere(4.0, (0, 48, 5.0), m=mat('#fff0b0', emit=3))
    car = impala((0, 3.2, 0), 0)
    d = dean(loc=(-0.55, 0.3, 0)); s = sam(loc=(0.55, 0.4, 0))
    d.walk(1, int(c.n * 0.7), (-0.55, 1.4, 0), (-0.55, -0.6, 0), 1.6)
    s.walk(1, int(c.n * 0.7), (0.55, 1.5, 0), (0.55, -0.5, 0), 1.6)
    d.auto_blink(1, c.n, 9); s.auto_blink(1, c.n, 10)
    f1 = int(c.n * 0.72)
    sg = shotgun(d.arms[1], (0, 0, -0.42), (PI / 2, 0, 0))
    d.arm(1, f1 + 8, (-0.6, 0, 0.2))
    key(d.mouth, 'scale', f1, (1, 1, 0.35)); key(d.mouth, 'scale', f1 + 8, (1.4, 1, 0.5))
    sun(rot=(1.1, 0.0, 3.0), energy=2.6, color='#ffc49a')
    point((0, -2.0, 2.2), 140, '#ffe0c0', 1.5)
    cam, t = camera((0, -4, 1.0), (0, 1.0, 1.2), 30)
    cam_move(cam, t, c, (0, -4.6, 0.6), (0, -3.6, 0.9), (0, 1.5, 1.4), (0, 0.5, 1.3))

def s10(c):
    night_world('#1a0a2a', 0.45)
    checker_floor('#2a1a4a', '#3a2a5a', size=40, scale=0.8)
    box((16, 0.2, 8), (0, 3.0, 4), m=mat('#2a1450', 0.9))
    for i in range(14):
        sphere(0.6, (-6 + i, 2.6, 0.2), (1, 0.6, 0.4), mat('#8a7aaa', 1.0, emit=0.3))   # nevoa
    mons = []
    g = Char(name='ghost', skin='#cfe8ff', hair='#e8f4ff', hair_style='long', jacket='#e0f0ff', vest=None, collar=False,
             dress='#e0f0ff', female=True, eye_mode='white', shoes='#e0f0ff', body_w=0.9)
    v = generic_person(330, (0, 0, 0), skin='#ece6e4', jacket='#1a1a24', pants='#1a1a24', hair='#141414', hair_style='short',
                       female=False, fangs=True, eye_mode='red')
    w = Char(name='wolf', skin='#8a6a4a', hair='#5a3a22', hair_style='short', jacket='#6a5a4a', vest=None, collar=False,
             eye_mode='yellow', fangs=True, pointy_ears=True, beard='#5a3a22', shoes='#5a3a22')
    dm = generic_person(331, (0, 0, 0), jacket='#2a2a2a', pants='#2a2a2a', female=False, hair_style='short', hair='#2a2a2a', eye_mode='black')
    xs = [-0.9, -0.3, 0.3, 0.9]
    words = [0.15, 0.32, 0.5, 0.68]
    for i, ch in enumerate([g, v, w, dm]):
        ch.root.location = (xs[i], 0.4 + 0.15 * abs(xs[i]), 0)
        ch.root.rotation_euler = (0, 0, xs[i] * 0.25)
        life(c, ch, 40 + i)
        pop_in(ch.root, int(c.n * words[i]), 8, 1.1)
        key(ch.mouth, 'scale', 1, (1.2, 1, 1.0))
    ch = None
    point((0, -1.2, 2.6), 200, '#c9a8ff', 1.5)
    point((0, 1.5, 0.6), 120, '#7a3aff', 1.0)
    cam, t = camera((0, -3.0, 1.3), (0, 0.4, 1.15), 30)
    cam_move(cam, t, c, (0, -3.3, 1.2), (0, -2.6, 1.3), (0, 0.4, 1.15), (0, 0.4, 1.2))

def s11(c):
    setup_render(sky='#d8f0f0')
    room('#cdeee6', None, '#e8f2f0', '#d8e8e4', back_y=1.8, side_x=-2.2)
    bed((-0.6, 0.6, 0), -PI / 2, '#ffffff', '#9fc8e8')
    d = dean(loc=(-0.6, 0.6, 0.62), jacket='#9fc8e8', shirt='#9fc8e8', pants='#9fc8e8')
    d.root.rotation_euler = (0, PI / 2, 0); d.root.location = (-1.45, 0.6, 0.86)
    for e in d.eyes:
        e.scale = (1, 1, 0.1)
    # monitor cardiaco
    box((0.4, 0.3, 0.35), (-1.6, 1.4, 1.3), m='#2a2e36', bevel=0.03)
    box((0.34, 0.02, 0.26), (-1.6, 1.24, 1.3), m=mat('#2aff8a', 0.3, emit=1.2))
    jn = john(loc=(0.6, 0.2, 0), rot=-PI * 0.4)
    life(c, jn, 11)
    jn.brows_set(5, 0.35)
    f1 = int(c.n * 0.72)
    key(jn.root, 'rotation_euler', f1, (0, 0, -PI * 0.4)); key(jn.root, 'rotation_euler', f1 + 10, (-PI / 2 + 0.05, 0, -PI * 0.4))
    for e in jn.eyes:
        key(e, 'scale', f1, (1, 1, 1)); key(e, 'scale', f1 + 6, (1, 1, 0.1))
    sun(rot=(0.8, 0.1, 0.5), energy=3.0)
    cam, t = camera((0.5, -2.2, 1.5), (0, 0.6, 1.0), 30)
    cam_move(cam, t, c, (0.8, -2.4, 1.5), (0.6, -1.8, 1.3), (-0.2, 0.6, 1.0), (0.3, 0.4, 0.7))

def s12(c):
    night_world('#0e1424', 0.3)
    floor('#3a2e26', 60)
    box((60, 0.2, 30), (0, 14, 15), m=mat('#101828', 1.0, emit=0.4))
    for x in (-2.5, 2.0):
        box((2.4, 2.0, 2.8), (x, 5, 1.4), m=mat('#4a4038', 0.9), bevel=0.05)
    d = dean(loc=(0.4, 0.1, 0), rot=-PI / 2)
    d.kneel()
    life(c, d, 12, 0.5)
    d.look(1, 0.55, 0)
    d.brows_set(1, 0.5, 1)
    d.arm(0, 1, (-0.55, 0, 0.3)); d.arm(1, 1, (-0.55, 0, -0.3))
    s = sam(loc=(0, 0, 0))
    s.root.rotation_euler = (-PI / 2 + 0.14, 0, -PI / 2)
    s.root.location = (-1.62, 0.1, 0.24)
    for e in s.eyes:
        e.scale = (1, 1, 0.1)
    point((-0.6, -1.2, 2.2), 220, '#c0d0ff', 1.2)
    sun(rot=(0.9, 0.2, -0.6), energy=1.0, color='#8fa8ff')
    cam, t = camera((-0.9, -2.2, 1.5), (0.1, 0.1, 0.6), 32)
    cam_move(cam, t, c, (-1.2, -2.6, 1.6), (-0.8, -1.9, 1.45), (0.0, 0.1, 0.6), (0.1, 0.1, 0.65))

def s13(c):
    night_world('#0a1020', 0.3)
    floor('#3a4a2a', 100)
    box((2.2, 80, 0.03), (0, 0, 0.015), m='#a08a6a')
    box((80, 2.2, 0.03), (0, 1.6, 0.016), m='#a08a6a')
    box((100, 0.2, 30), (0, 40, 15), m=mat('#0e1830', 1.0, emit=0.4))
    stars(60, 39.8, 13)
    # placa
    cyl(0.06, 2.4, (1.4, 2.8, 1.2), m='#6a4a2a')
    box((1.0, 0.06, 0.22), (1.75, 2.8, 2.1), m='#c9a86a', bevel=0.02)
    box((1.0, 0.06, 0.22), (1.05, 2.8, 1.8), m='#c9a86a', bevel=0.02)
    # caixinha enterrada
    box((0.2, 0.14, 0.08), (0, 1.6, 0.04), m=mat('#8a8e94', 0.3, metal=0.8))
    d = dean(loc=(-0.45, 1.3, 0), rot=PI * 0.42)
    dm = Char(name='xdemon', hair='#2a1a14', hair_style='long', eyes='#000000', jacket='#3a0a14', vest=None, dress='#3a0a14',
              female=True, collar=False, eye_mode='red', body_w=0.9)
    dm.root.location = (0.45, 1.6, 0); dm.root.rotation_euler = (0, 0, -PI * 0.42)
    life(c, d, 13); life(c, dm, 14)
    d.brows_set(5, -0.35)
    talk(c, d, 1, int(c.n * 0.6), 0.8)
    key(dm.mouth, 'scale', 1, (1.4, 1, 0.45))
    f1 = int(c.n * 0.65)
    d.arm(1, f1, (-1.2, 0, 0.45)); dm.arm(0, f1, (-1.2, 0, -0.45))    # aperto de mao
    point((0, 0.5, 2.6), 90, '#ffd8a8', 1.0)
    point((0.45, 1.0, 1.4), 40, '#ff3a3a', 0.4)
    sun(rot=(0.9, 0.2, -0.6), energy=0.8, color='#8fa8ff')
    cam, t = camera((0, -2.0, 1.5), (0, 1.5, 1.2), 30)
    cam_move(cam, t, c, (0.3, -2.6, 1.4), (0, -1.4, 1.45), (0, 1.5, 1.15), (0, 1.5, 1.3))

def s14(c):
    night_world('#0a1222', 0.3)
    floor('#2e3a2a', 60)
    box((60, 0.2, 30), (0, 14, 15), m=mat('#0e1830', 1.0, emit=0.4))
    stars(50, 13.8, 14, (3, 14), 12)
    for i, (x, y) in enumerate([(-2.2, 3.0), (2.4, 3.4), (-1.0, 4.4), (1.2, 5.0), (-3.0, 5.6)]):
        tombstone((x, y, 0), 0, None)
    az = generic_person(340, (0.4, 1.4, 0), rot=-PI * 0.42, eye_mode='yellow', jacket='#2a2a30', pants='#2a2a30',
                        hair='#3a3a3a', hair_style='short', female=False, skin='#c8a890')
    d = dean(loc=(-0.55, 1.0, 0), rot=PI * 0.42)
    life(c, az, 15); life(c, d, 16)
    key(az.mouth, 'scale', 1, (1.4, 1, 0.45))
    d.brows_set(1, -0.45, 1)
    f1 = int(c.n * 0.62)
    d.arm(1, f1 - 10, (-0.4, 0, 0)); d.arm(1, f1, (-1.55, 0, 0.0))
    cg = colt(d.arms[1], (0, 0, -0.46), (PI / 2, 0, 0), 1.3)
    fl = sphere(0.1, (0, -0.35, -0.47), m=mat('#fff3a0', emit=14), parent=d.arms[1])
    hide_between(fl, f1 + 4, f1 + 7)
    flash = point((0, 1.1, 1.2), 0, '#fff0b0', 0.2)
    keys(flash.data, 'energy', [(f1 + 3, 0), (f1 + 4, 1800), (f1 + 9, 0)], 'LINEAR')
    key(az.root, 'rotation_euler', f1 + 6, (0, 0, -PI * 0.42)); key(az.root, 'rotation_euler', f1 + 18, (-PI / 2 + 0.05, 0, -PI * 0.42))
    # brilho dos olhos apaga
    point((0, -0.5, 2.6), 90, '#c0d0ff', 1.0)
    sun(rot=(0.9, 0.2, -0.6), energy=0.8, color='#8fa8ff')
    cam, t = camera((0, -2.4, 1.4), (0, 1.2, 1.2), 30)
    cam_move(cam, t, c, (0.6, -2.6, 1.3), (0.1, -2.0, 1.4), (0.2, 1.3, 1.3), (0, 1.2, 1.2))

def s15(c):
    night_world('#200508', 0.25)
    floor('#3a2a2a', 40)
    box((12, 0.2, 4), (0, 2.4, 2), m=mat('#6a4a42', 0.9))
    box((0.2, 12, 4), (-2.2, -2, 2), m=mat('#5a3e38', 0.9))
    d = dean(loc=(0, 0.6, 0), rot=0)
    life(c, d, 17)
    d.brows_set(1, 0.45, 1)
    key(d.mouth, 'scale', 1, (1, 1, 0.4)); key(d.mouth, 'scale', 25, (1.1, 1, 1.0))
    hs = [hellhound((-0.8, -0.2, 0), -PI * 0.6, 0.7), hellhound((0.85, 0.0, 0), PI * 0.6, 0.7)]
    for k, h in enumerate(hs):
        p0 = tuple(h.location)
        key(h, 'location', 1, (p0[0] * 1.9, p0[1] - 0.5, 0)); key(h, 'location', c.n, (p0[0] * 0.8, p0[1] + 0.15, 0))
    # garras na parede
    for i in range(4):
        box((0.03, 0.02, 0.6), (-0.8 + i * 0.1, 2.28, 1.6), rot=(0, 0.3, 0), m=mat('#1a0a0a', 0.8))
    pr = point((0, -0.5, 2.6), 160, '#ff2a2a', 1.0)
    keys(pr.data, 'energy', [(1, 60), (c.n, 220)])
    cam, t = camera((0, -2.5, 1.3), (0, 0.5, 1.0), 30)
    cam_move(cam, t, c, (0, -2.9, 1.3), (0, -2.2, 1.3), (0, 0.4, 0.95), (0, 0.5, 1.05))

def s16(c):
    night_world('#0a0a14', 0.25)
    floor('#4a3a2a', 40)
    # celeiro de madeira com simbolos
    for i in range(16):
        box((0.5, 0.15, 4.0), (-4 + i * 0.52, 2.6, 2.0), m=mat('#6a4a2e' if i % 2 else '#5e4228', 0.9))
    for k, (x, z) in enumerate([(-2.2, 2.2), (1.8, 2.6), (-0.6, 3.2)]):
        o = curve_path([(x + 0.4 * math.cos(a), 2.5, z + 0.4 * math.sin(a)) for a in [i * PI / 4 for i in range(8)]], bevel=0.02, m=mat('#d8d0c0', 0.8), closed=True)
    wg = wings_shadow((0, 2.48, 2.2), 1.6)
    f1 = int(c.n * 0.25)
    wg.scale = (1, 1, 1)
    hide_between(wg, f1 + 6, int(c.n * 0.6))
    cas = castiel(loc=(0, -0.4, 0), rot=PI)
    cas.walk(1, f1, (0, 1.8, 0), (0, 0.8, 0), 1.4)
    key(cas.root, 'rotation_euler', 1, (0, 0, 0)); key(cas.root, 'rotation_euler', f1, (0, 0, 0))
    cas.auto_blink(1, c.n, 18)
    d = dean(loc=(-0.75, -0.5, 0), rot=PI * 0.85)
    life(c, d, 19)
    # faiscas / lampadas estourando
    sparks = []
    rnd = random.Random(3)
    for i in range(14):
        sp = sphere(0.035, (rnd.uniform(-2.5, 2.5), rnd.uniform(0.5, 2.3), rnd.uniform(2.6, 3.4)), m=mat('#fff3a0', emit=12), seg=8)
        hide_between(sp, f1 + rnd.randint(0, 10), f1 + rnd.randint(14, 26))
    lb = point((0, 1.0, 3.0), 0, '#e8f2ff', 1.5)
    keys(lb.data, 'energy', [(f1, 30), (f1 + 6, 900), (int(c.n * 0.6), 900), (int(c.n * 0.6) + 8, 60)])
    point((0, -1.5, 2.2), 70, '#ffd8a8', 1.0)
    cam, t = camera((0, -3.4, 1.4), (0, 0.9, 1.6), 30)
    cam_move(cam, t, c, (0.4, -3.6, 1.3), (0.15, -2.2, 1.45), (0, 1.0, 1.6), (0, 0.8, 1.4))

def s17(c):
    setup_render(sky='#e8f4ff', sky_strength=1.1)
    floor('#f4f8ff', 60)
    box((60, 0.2, 30), (0, 8, 15), m=mat('#dceeff', 1.0, emit=1.0))
    for i in range(8):
        sphere(1.2, (-5 + i * 1.5, 7.5, 0.5), (1.3, 0.6, 0.6), mat('#ffffff', 1.0, emit=0.6))
    cas = castiel(loc=(0, 0.3, 0))
    life(c, cas, 19)
    angels = []
    for i, x in enumerate([-1.0, -0.5, 0.5, 1.0]):
        a = generic_person(350 + i, (x, 1.1 + abs(x) * 0.3, 0), rot=-x * 0.2, jacket='#2a2a34', pants='#2a2a34', female=(i % 2 == 1),
                           collar=True, tie='#3a3a4a')
        life(c, a, 350 + i)
        angels.append(a)
    f1 = int(c.n * 0.55)
    for a in angels:
        for e in a.eyes:
            pass
        a.brows_set(f1, -0.45)
    # olhos ficam brancos (luz) - esfera emissiva aparece nos olhos dos anjos maus
    for a in angels[1:3]:
        for e in a.eyes:
            g = sphere(0.054, (0, -0.005, 0), m=mat('#e8f6ff', 0.2, emit=6), parent=e)
            g.scale = (1, 0.62, 1.08)
            hide_between(g, f1 + 4, None)
    point((0, -1.0, 2.8), 120, '#ffffff', 1.5)
    sun(rot=(0.6, 0.1, 0.3), energy=3.0)
    cam, t = camera((0, -2.6, 1.4), (0, 0.6, 1.35), 32)
    cam_move(cam, t, c, (0, -2.0, 1.4), (0, -3.0, 1.45), (0, 0.4, 1.35), (0, 0.8, 1.4))

def s18(c):
    setup_render(sky='#5a0a0a', sky_strength=0.6)
    floor('#2a1210', 80)
    box((80, 0.2, 30), (0, 14, 15), m=mat('#a0201a', 1.0, emit=1.0))
    box((80, 0.2, 6), (0, 13.8, 2.0), m=mat('#ff6a2a', 1.0, emit=1.2))
    for i in range(6):
        fp, fl = flames((-6 + i * 2.4, 6 + (i % 2) * 2, 0), n=5, spread=0.6, h=1.6, seed=60 + i)
        flicker(fl, 1, c.n, 60 + i)
    luc = generic_person(360, (-0.3, 2.6, 0), jacket='#1a1a1a', pants='#1a1a1a', female=False, hair_style='short',
                         hair='#c9a86a', eye_mode='red', collar=True, shirt='#2a2a2a')
    amara = Char(name='amara', hair='#141014', hair_style='long', eyes='#1a1a1a', jacket='#141014', vest=None, dress='#141014',
                 female=True, collar=False, body_w=0.9, eye_mode='black')
    amara.root.location = (0.38, 3.4, 0)
    amara.root.rotation_euler = (0, 0, -0.1)
    life(c, luc, 21); life(c, amara, 22)
    key(luc.mouth, 'scale', 1, (1.4, 1, 0.45))
    hide_between(luc.root, int(c.n * 0.4), None)
    hide_between(amara.root, int(c.n * 0.72), None)
    d = dean(loc=(-0.6, -0.3, 0), rot=PI); s = sam(loc=(0.6, -0.3, 0), rot=PI)
    life(c, d, 23); life(c, s, 24)
    point((0, 1.5, 3.0), 200, '#ff4a2a', 1.5)
    point((0, -2.0, 2.0), 60, '#ffd8a8', 1.0)
    cam, t = camera((0, -3.4, 1.0), (0, 2.0, 1.6), 30)
    cam_move(cam, t, c, (0.0, -3.8, 0.95), (0, -3.0, 1.1), (0, 2.0, 1.5), (-0.3, 2.6, 1.4))

def s19(c):
    night_world('#141a30', 0.4)
    floor('#2e3a2a', 60)
    box((60, 0.2, 30), (0, 12, 15), m=mat('#1a2244', 1.0, emit=0.5))
    stars(50, 11.8, 19, (3, 14), 12)
    rnd = random.Random(19)
    k = 0
    for row in range(3):
        for i in range(6):
            x = -2.6 + i * 1.05 + (0.5 if row % 2 else 0)
            tb = tombstone((x, 1.2 + row * 1.3, 0), rnd.uniform(-0.15, 0.15), None, 0.8)
            pop_in(tb, 2 + k * 4, 6)
            k += 1
    d = dean(loc=(-0.4, -0.2, 0), rot=0.15); s = sam(loc=(0.4, -0.1, 0), rot=-0.15)
    life(c, d, 25); life(c, s, 26)
    key(d.mouth, 'scale', int(c.n * 0.5), (1, 1, 0.35)); key(d.mouth, 'scale', int(c.n * 0.5) + 8, (1.5, 1, 0.5))
    d.brows_set(int(c.n * 0.5), 0.25)
    point((0, -1.5, 2.6), 110, '#d8e0ff', 1.5)
    sun(rot=(0.9, 0.2, -0.6), energy=0.8, color='#8fa8ff')
    cam, t = camera((0, -3, 1.4), (0, 0.8, 1.2), 30)
    cam_move(cam, t, c, (0, -2.4, 1.3), (0, -3.3, 1.6), (0, 0.6, 1.25), (0, 1.0, 1.25))

def s20(c):
    setup_render(sky='#ffcf8a')
    floor('#b89a6a', 80)
    box((80, 0.2, 30), (0, 14, 15), m=mat('#ffc88a', 1.0, emit=1.0))
    for i, (x, y, r, col) in enumerate([(-3.5, 4, 0.3, '#8a5a3a'), (3.2, 4.5, -0.4, '#5a7a8a'), (-1.2, 6.5, 0.1, '#7a3a2a'), (1.8, 7.0, 0.6, '#6a6a4a')]):
        junk_car((x, y, 0), r, col)
    junk_car((-3.5, 4, 1.2), 0.5, '#4a6a5a')
    d = dean(loc=(-0.3, 0.4, 0), rot=0.1); s = sam(loc=(0.3, 0.45, 0), rot=-0.1)
    b = bobby(loc=(-0.9, 0.7, 0), rot=0.25); cas = castiel(loc=(0.9, 0.75, 0), rot=-0.25)
    for k, ch in enumerate([d, s, b, cas]):
        life(c, ch, 30 + k)
    pop_in(b.root, int(c.n * 0.25), 8, 1.08)
    pop_in(cas.root, int(c.n * 0.38), 8, 1.08)
    f1 = int(c.n * 0.6)
    for ch in (d, s, b, cas):
        key(ch.mouth, 'scale', f1, (1, 1, 0.35)); key(ch.mouth, 'scale', f1 + 10, (1.5, 1, 0.55))
    sun(rot=(0.8, 0.1, 0.6), energy=3.2, color='#ffe0b8')
    cam, t = camera((0, -2.6, 1.3), (0, 0.6, 1.25), 28)
    cam_move(cam, t, c, (0, -2.9, 1.2), (0, -2.3, 1.35), (0, 0.6, 1.25), (0, 0.6, 1.3))

def s21(c):
    setup_render(sky='#3a2a1a', sky_strength=0.6)
    floor('#5a4030', 40)
    box((12, 0.2, 5), (0, 3.2, 2.5), m=mat('#7a5a3a', 0.8))
    for i in range(6):     # estantes
        x = -3 + i * 1.2
        box((1.0, 0.4, 2.6), (x, 2.9, 1.3), m=mat('#5a3a22', 0.7))
        for r in range(4):
            for b_ in range(5):
                box((0.14, 0.3, 0.42), (x - 0.36 + b_ * 0.18, 2.75, 0.35 + r * 0.62), m=random.Random(i * 20 + r * 5 + b_).choice(['#8a2a2a', '#2a4a7a', '#3a6a3a', '#7a6a3a', '#5a3a6a']))
    for x in (-1.2, 1.2):
        table((x, 1.0, 0), (1.6, 0.8), 0.78, '#6a4228', '#4a2e1a')
        lamp_green((x - 0.3, 1.0, 0.81)); lamp_green((x + 0.3, 1.0, 0.81))
    # mesa do mapa iluminada
    box((1.8, 1.1, 0.75), (0, -0.4, 0.375), m=mat('#4a3020', 0.6), bevel=0.03)
    box((1.6, 0.9, 0.02), (0, -0.4, 0.76), m=mat('#7ac8ff', 0.3, emit=1.2))
    d = dean(loc=(-0.5, 0.3, 0), rot=0.15); s = sam(loc=(0.5, 0.3, 0), rot=-0.15)
    life(c, d, 33); life(c, s, 34)
    key(d.mouth, 'scale', 20, (1.4, 1, 0.5))
    point((0, -0.4, 1.6), 35, '#7ac8ff', 0.8)
    point((0, 1.0, 2.6), 160, '#ffd8a0', 1.5)
    cam, t = camera((0, -3.5, 1.9), (0, 0.6, 1.0), 30)
    cam_move(cam, t, c, (0.4, -3.9, 2.1), (-0.1, -3.2, 1.8), (0, 0.8, 1.1), (0, 0.4, 1.0))

def s22(c):
    setup_render(sky='#f4f8ff', sky_strength=1.0)
    room('#eef4ff', '#f8fbff', '#e0e8f4', '#d0dcec', back_y=2.5)
    table((0, 0.9, 0), (1.2, 0.7), 0.75, '#c9a87a', '#8a6a4a')
    typewriter((0, 0.85, 0.78), PI)
    ch = Char(name='chuck', hair='#5a3a26', hair_style='short', eyes='#4a6a8a', jacket='#9aa8b8', vest=None, shirt='#f4f4f0',
              pants='#5a6a7a', beard='#5a3a26', collar=True, coat='#9aa8b8')   # roupão
    ch.root.location = (0, 1.45, 0); ch.sit(); chair((0, 1.5, 0), 0, '#8a6a4a')
    life(c, ch, 35)
    ch.arm(0, 1, (-1.1, 0, 0.2)); ch.arm(1, 1, (-1.1, 0, -0.2))
    for f in range(1, int(c.n * 0.55), 6):
        for k, a in enumerate(ch.arms):
            a.rotation_euler = (-1.1 + 0.08 * ((f // 6 + k) % 2), 0, 0.2 * (1 if k == 0 else -1)); a.keyframe_insert('rotation_euler', frame=f)
    # paginas voando
    rnd = random.Random(22)
    for i in range(14):
        pg = box((0.2, 0.28, 0.005), (0, 1.0, 1.1), m='#ffffff')
        f0 = 5 + i * 5
        key(pg, 'location', f0, (0, 1.0, 1.1)); key(pg, 'location', f0 + 30, (rnd.uniform(-1.8, 1.8), rnd.uniform(-0.5, 1.5), rnd.uniform(1.4, 2.8)))
        key(pg, 'rotation_euler', f0, (0, 0, 0)); key(pg, 'rotation_euler', f0 + 30, (rnd.uniform(-3, 3), rnd.uniform(-3, 3), rnd.uniform(-3, 3)))
        hide_between(pg, f0, None)
    f1 = int(c.n * 0.62)
    d = dean(loc=(-0.9, 0.2, 0), rot=PI * 0.25); s = sam(loc=(0.9, 0.2, 0), rot=-PI * 0.25)
    for k, x in enumerate([d, s]):
        life(c, x, 36 + k); x.brows_set(f1, -0.35)
        pop_in(x.root, f1 - 6 + k * 4, 8, 1.06)
    ch.brows_set(f1 + 6, 0.5); key(ch.mouth, 'scale', f1 + 4, (1, 1, 0.35)); key(ch.mouth, 'scale', f1 + 12, (1.2, 1, 1.2))
    sun(rot=(0.7, 0.1, 0.4), energy=3.0)
    cam, t = camera((0, -2.6, 1.6), (0, 1.0, 1.15), 32)
    key(cam, 'location', 1, (0.3, -1.4, 1.5)); key(t, 'location', 1, (0, 1.0, 1.15))
    key(cam, 'location', f1 - 8, (0.2, -1.6, 1.5)); key(t, 'location', f1 - 8, (0, 1.0, 1.15))
    key(cam, 'location', f1 + 4, (0, -3.2, 1.55)); key(t, 'location', f1 + 4, (0, 0.8, 1.15))
    key(cam, 'location', c.n, (0, -3.0, 1.5))

def barn_set(dusk=True):
    setup_render(sky='#ff9a5a' if dusk else '#1a1a2a', sky_strength=0.5)
    floor('#6a5038', 40)
    for i in range(18):
        box((0.5, 0.15, 4.0), (-4.5 + i * 0.52, 2.6, 2.0), m=mat('#7a4e2e' if i % 2 else '#6a4228', 0.9))
    for i in range(18):
        box((0.15, 0.5, 4.0), (-2.6, 2.4 - i * 0.52, 2.0), m=mat('#7a4e2e' if i % 2 else '#6a4228', 0.9))
    # feno
    for k, (x, y) in enumerate([(1.8, 1.8), (2.4, 1.2), (-1.8, 1.9)]):
        box((0.9, 0.6, 0.5), (x, y, 0.25), m=mat('#d8b85a', 0.95), bevel=0.06)
    box((0.22, 0.22, 3.6), (0.3, 1.0, 1.8), m=mat('#5a3a22', 0.85))      # pilar
    # luz pelas frestas
    for i in range(5):
        box((0.06, 0.02, 3.4), (-3.6 + i * 1.6, 2.5, 1.9), m=mat('#ffd8a0', emit=2.5))

def s23(c):
    barn_set()
    d = dean(loc=(0.3, 0.7, 0), rot=0)
    life(c, d, 40, 0.5)
    vamps = []
    for k, x in enumerate([-1.3, 1.4]):
        v = generic_person(380 + k, (x, 0.8, 0), rot=-x * 0.6, skin='#e8e2de', jacket='#1a1a24', pants='#1a1a24',
                           hair='#141414', hair_style='short', female=False, fangs=True)
        life(c, v, 380 + k); key(v.mouth, 'scale', 1, (1.3, 1, 0.9))
        vamps.append(v)
    f1 = int(c.n * 0.62)
    for v in vamps:
        hide_between(v.root, None, f1)
    # Dean recua ate o pilar e se fere (sem mostrar ferimento)
    key(d.root, 'location', f1 - 10, (0.3, 0.7, 0)); key(d.root, 'location', f1, (0.3, 0.88, 0))
    d.brows_set(f1, 0.5); key(d.mouth, 'scale', f1 - 2, (1, 1, 0.35)); key(d.mouth, 'scale', f1 + 4, (1.2, 1, 1.2))
    key(d.root, 'rotation_euler', f1 + 6, (0, 0, 0)); key(d.root, 'rotation_euler', f1 + 20, (0.12, 0, 0))
    d.arm(0, f1 + 10, (-0.7, 0, 0.6))
    point((0, -1.0, 2.6), 120, '#ffc89a', 1.2)
    point((0.3, 0.0, 1.5), 40, '#ffd8a8', 0.6)
    cam, t = camera((0, -2.8, 1.5), (0.2, 0.8, 1.2), 30)
    key(cam, 'location', 1, (0.2, -3.2, 1.6)); key(t, 'location', 1, (0.1, 0.8, 1.2))
    key(cam, 'location', f1, (0.25, -2.4, 1.5)); key(t, 'location', f1, (0.25, 0.8, 1.25))
    key(cam, 'location', c.n, (0.3, -1.3, 1.45)); key(t, 'location', c.n, (0.3, 0.9, 1.3))

def s24(c):
    barn_set()
    d = dean(loc=(0.3, 0.75, 0), rot=0)
    d.root.location = (0.3, 0.86, 0)
    d.root.rotation_euler = (0.12, 0, 0)
    life(c, d, 41, 0.4)
    d.brows_set(1, 0.45, 1)
    talk(c, d, 1, c.n, 0.6)
    s = sam(loc=(0.85, 0.35, 0), rot=-PI * 0.4)
    life(c, s, 42, 0.5)
    s.brows_set(1, 0.5, 1)
    s.arm(0, 1, (-1.3, 0, -0.55))
    s.look(1, 0.1, 0)
    point((0, -1.0, 2.6), 110, '#ffc89a', 1.2)
    cam, t = camera((0.2, -1.6, 1.45), (0.5, 0.7, 1.35), 40)
    cam_move(cam, t, c, (0.1, -1.8, 1.45), (0.3, -1.2, 1.42), (0.5, 0.7, 1.35), (0.5, 0.7, 1.38))

def s25(c):
    setup_render(sky='#bfe9ff')
    floor('#8fdc7f', 100)
    box((80, 0.2, 40), (0, 25, 15), m=mat('#c8ecff', 1.0, emit=1.0))
    for i, (x, z) in enumerate([(-5, 8), (5, 10), (0, 12)]):
        cloud((x, 22, z), 1.6, 70 + i)
    # Roadhouse (casa de madeira) com varanda
    rh = empty("roadhouse", (0.6, 4.0, 0))
    box((5.0, 3.0, 2.6), (0, 0, 1.3), m=mat('#8a5a3a', 0.85), parent=rh, bevel=0.04)
    box((5.4, 3.4, 0.25), (0, 0, 2.75), m='#5a3a2a', parent=rh, bevel=0.04)
    box((5.0, 1.0, 0.15), (0, -2.0, 0.3), m='#7a5a3a', parent=rh)
    for x in (-2.3, 2.3):
        box((0.12, 0.12, 2.3), (x, -2.4, 1.15), m='#6a4a2a', parent=rh)
    box((5.0, 1.2, 0.1), (0, -2.0, 2.3), m='#5a3a2a', parent=rh)
    box((2.2, 0.1, 0.5), (0, -1.55, 2.0), m='#2a2a2a', parent=rh)
    t1 = text3d("ROADHOUSE", (0, -1.62, 2.0), size=0.26, m=mat('#ffd23f', emit=1.2), font=BOLD, extrude=0.01); t1.parent = rh
    door((0.6, 2.48, 0.3), 0, '#4a2e1a')
    impala((-2.4, 1.6, 0), PI * 0.35)
    b = bobby(loc=(1.0, 1.7, 0.3), rot=-0.3)
    life(c, b, 43)
    key(b.mouth, 'scale', 15, (1.5, 1, 0.55))
    b.arm(1, 20, (-2.2, 0, 0.3))      # aceno
    d = dean(loc=(0.4, -1.4, 0), rot=PI)
    d.walk(1, int(c.n * 0.55), (-0.5, -1.8, 0), (-0.2, 0.7, 0), 1.6)
    d.auto_blink(1, c.n, 44)
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -4, 1.5), (0.4, 1.2, 1.4), 30)
    cam_move(cam, t, c, (0.2, -4.6, 1.4), (0.4, -3.2, 1.55), (0.3, 1.2, 1.4), (0.5, 1.6, 1.45))

def s26(c):
    setup_render(sky='#bfe9ff')
    floor('#8fdc7f', 100)
    box((80, 0.2, 40), (0, 25, 15), m=mat('#c8ecff', 1.0, emit=1.0))
    house_ext((0.5, 5.5, 0), wall='#f2e6d0', roof='#7a4a3a', night=False)
    for i in range(10):
        box((0.08, 0.08, 0.8), (-3 + i * 0.66, 2.0, 0.4), m='#ffffff')
    box((6.0, 0.06, 0.08), (0, 2.0, 0.7), m='#ffffff')
    old = sam(loc=(-0.35, 0.6, 0), rot=PI * 0.3, hair='#c8c8c8', brows='#a8a8a8', jacket='#6a7a5a')
    kid = Char(name='kid', hair='#7a5a38', hair_style='dean', eyes='#3f9a5a', jacket='#3a7ac0', vest=None, shirt='#3a7ac0',
               pants='#2a3a5a', collar=False, height=0.62, body_w=0.78, brows='#6a4a2e')
    kid.root.location = (0.4, 0.4, 0); kid.root.rotation_euler = (0, 0, -PI * 0.35)
    life(c, old, 45); life(c, kid, 46)
    old.arm(1, 10, (-0.9, 0, 0.5))
    key(old.mouth, 'scale', 10, (1.5, 1, 0.55)); key(kid.mouth, 'scale', 10, (1.5, 1, 0.6))
    # bola
    ball = sphere(0.1, (0.1, 0.3, 0.1), m='#ff5a3a')
    for f in range(1, c.n + 1, 4):
        ball.location = (0.1 + 0.25 * math.sin(f / 10), 0.3, 0.1 + abs(math.sin(f / 7)) * 0.5); ball.keyframe_insert('location', frame=f)
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -3, 1.3), (0, 0.6, 1.0), 30)
    cam_move(cam, t, c, (0.3, -3.4, 1.3), (0.1, -2.4, 1.25), (0, 0.6, 1.0), (0, 0.5, 1.05))

def bridge_set():
    setup_render(sky='#ff9a7a')
    floor('#2a8a5a', 100)
    box((80, 30, 0.1), (0, 0, -0.6), m=mat('#3ab0d8', 0.2))      # rio
    box((80, 0.2, 40), (0, 25, 15), m=mat('#ff9f7a', 1.0, emit=1.0))
    box((80, 0.2, 6), (0, 24.8, 1.5), m=mat('#ffc58a', 1.0, emit=1.0))
    sphere(2.6, (0, 23, 4.5), m=mat('#fff0b0', emit=3))
    for i, (x, z) in enumerate([(-6, 8), (6, 10)]):
        cloud((x, 21, z), 1.8, 80 + i, color='#ffd3e0')
    # ponte de madeira
    box((2.4, 14, 0.15), (0, 2, 0.0), m=mat('#8a5a3a', 0.8))
    for sx in (-1, 1):
        box((0.08, 14, 0.08), (sx * 1.15, 2, 0.95), m='#6a4228')
        for i in range(15):
            box((0.08, 0.08, 0.95), (sx * 1.15, -5 + i, 0.5), m='#6a4228')

def s27(c):
    bridge_set()
    d = dean(loc=(0.5, 1.2, 0), rot=PI * 0.75)
    life(c, d, 50, 0.5)
    d.arm(0, 1, (-0.5, 0, 0)); d.arm(1, 1, (-0.5, 0, 0))
    f1 = int(c.n * 0.6)
    key(d.root, 'rotation_euler', f1, (0, 0, PI * 0.75)); key(d.root, 'rotation_euler', f1 + 14, (0, 0, 0.1))
    key(d.mouth, 'scale', f1 + 10, (1, 1, 0.35)); key(d.mouth, 'scale', f1 + 20, (1.5, 1, 0.55))
    sun(rot=(1.1, 0.0, 0.2), energy=2.8, color='#ffc49a')
    cam, t = camera((0, -3, 1.3), (0.5, 1.2, 1.2), 32)
    cam_move(cam, t, c, (-0.6, -3.4, 1.2), (0.1, -2.2, 1.35), (0.5, 1.2, 1.3), (0.5, 1.2, 1.35))

def s28(c):
    bridge_set()
    d = dean(loc=(-0.35, 1.0, 0), rot=PI * 0.45); s = sam(loc=(0.35, 1.0, 0), rot=-PI * 0.45)
    f1 = int(c.n * 0.15)
    s.walk(1, f1, (1.4, 1.0, 0), (0.33, 1.0, 0), 1.8)
    key(s.root, 'rotation_euler', 1, (0, 0, -PI * 0.5)); key(s.root, 'rotation_euler', f1, (0, 0, -PI * 0.5))
    life(c, d, 51); s.auto_blink(1, c.n, 52)
    # abraco
    d.arm(0, f1 + 10, (-1.4, 0, 0.6)); d.arm(1, f1 + 10, (-1.4, 0, -0.6))
    s.arm(0, f1 + 10, (-1.4, 0, 0.6)); s.arm(1, f1 + 10, (-1.4, 0, -0.6))
    for ch in (d, s):
        key(ch.mouth, 'scale', f1, (1, 1, 0.35)); key(ch.mouth, 'scale', f1 + 10, (1.5, 1, 0.55))
        for e in ch.eyes:
            key(e, 'scale', f1 + 10, (1, 1, 1)); key(e, 'scale', f1 + 16, (1, 1, 0.12))
    sun(rot=(1.1, 0.0, 0.2), energy=2.8, color='#ffc49a')
    cam, t = camera((0, -2.4, 1.35), (0, 1.0, 1.35), 32)
    cam_move(cam, t, c, (0.4, -2.8, 1.35), (0, -1.8, 1.42), (0, 1.0, 1.35), (0, 1.0, 1.38))

def s29(c):
    night_world('#0a1234', 0.35)
    floor('#24302a', 120)
    road(120, -60, 4.0)
    box((120, 0.2, 40), (0, -45, 15), m=mat('#101a44', 1.0, emit=0.6))
    stars(140, -44.8, 29, (1.5, 26), 30)
    sphere(1.6, (5, -44, 11), m=mat('#fff6d0', emit=3))
    for x in (-9, 9):
        for y in range(-40, 0, 8):
            tree((x, y, 0), 1.6, '#1a3a2a', seed=y + x)
    car = impala((0, 0.6, 0), PI)      # de costas para a camera? frente para +Y
    car.rotation_euler = (0, 0, PI)
    # irmaos sentados no capo (capo em +Y por causa da rotacao)
    d = dean(loc=(0, 0, 0)); s = sam(loc=(0, 0, 0))
    for ch, x in ((d, -0.42), (s, 0.42)):
        ch.root.location = (x, 2.15, 0.62); ch.root.rotation_euler = (0, 0, PI)
        ch.sit(); ch.root.location.z = 0.62
        life(c, ch, 60 + int(x * 10), 0.5)
    f1 = int(c.n * 0.5)
    d.look(f1, -0.35, -0.3); s.look(f1, -0.35, 0.3)
    key(d.mouth, 'scale', f1 + 6, (1, 1, 0.35)); key(d.mouth, 'scale', f1 + 16, (1.5, 1, 0.55))
    key(s.mouth, 'scale', f1 + 10, (1, 1, 0.35)); key(s.mouth, 'scale', f1 + 20, (1.5, 1, 0.55))
    sun(rot=(0.9, 0.2, 2.6), energy=0.9, color='#9fb4ff')
    point((0, 4.0, 2.6), 160, '#ffd8a8', 1.2)
    cam, t = camera((0, 6.5, 1.8), (0, 2.0, 1.3), 30)
    cam_move(cam, t, c, (0.5, 7.2, 1.7), (0.1, 4.6, 1.5), (0, 2.0, 1.3), (0, 2.0, 1.4))

SHOTS = {k: v for k, v in globals().items() if k.startswith('s') and k[1:3].isdigit()}
