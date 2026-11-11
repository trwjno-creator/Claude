# Dexter - definicao de cada shot (cenario + personagens + animacao + camera)
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

def smile(ch, f, big=False):
    key(ch.mouth, 'scale', f - 6, tuple(ch.mouth.scale)); key(ch.mouth, 'scale', f, (1.6 if big else 1.4, 1, 0.55))

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

def stars(n=60, y=30, seed=1, zr=(5, 22), xr=20):
    rnd = random.Random(seed)
    for i in range(n):
        sphere(0.06, (rnd.uniform(-xr, xr), y, rnd.uniform(*zr)), m=mat('#ffffff', emit=4), seg=8)

def baby(parent=None, loc=(0, 0, 0)):
    p = empty("baby", loc, parent)
    sphere(1, (0, 0, 0), (0.12, 0.2, 0.1), mat('#bfe0ff', 0.8), p)
    sphere(0.075, (0, -0.17, 0.04), m=SKIN, parent=p)
    for sx in (-1, 1):
        sphere(0.008, (sx * 0.025, -0.235, 0.06), m='#222222', parent=p, seg=8)
    return p

def ghostify(ch, color='#8fbaff'):
    m = mat(color, 0.6, emit=0.35)
    for o in ch.root.children_recursive:
        if o.type in ('MESH', 'CURVE') and o.data.materials:
            for i in range(len(o.data.materials)):
                o.data.materials[i] = m

def station(extra=True):
    """delegacia / laboratorio de sangue"""
    setup_render(sky='#cfe8f4')
    room('#9fd0e4', '#b8dcec', '#e8ecef', '#d8dee4', back_y=3.0, side_x=-3.5, sq=0.8)
    text3d("MIAMI METRO", (0.0, 2.86, 2.75), size=0.42, m=mat('#1a3a6a', 0.3), font=BOLD, extrude=0.05)
    box((3.0, 0.06, 0.06), (0, 2.85, 2.4), m='#ffd23f')
    # tela com padrao de respingos de sangue
    box((1.4, 0.08, 0.9), (-2.0, 2.86, 1.8), m='#1a1f2a', bevel=0.03)
    box((1.3, 0.02, 0.8), (-2.0, 2.81, 1.8), m=mat('#f4f4f4', 0.4, emit=0.4))
    rnd = random.Random(7)
    for i in range(22):
        sphere(rnd.uniform(0.01, 0.04), (-2.0 + rnd.uniform(-0.55, 0.55), 2.795, 1.8 + rnd.uniform(-0.3, 0.3)), (1, 0.2, 1), mat('#b0101a', 0.3), seg=8)
    if extra:
        desk_pc((1.6, 1.2, 0), PI)
        desk_pc((-1.6, 1.2, 0), PI)

# ============================================================================ SHOTS
def s01(c):
    night_world('#0a0d18', 0.25)
    floor('#2a2a30', 60)
    box((60, 0.2, 30), (0, 20, 15), m=mat('#0e1428', 1.0, emit=0.3))
    for x, col in ((-3.2, '#2a5a8a'), (3.2, '#3a7a4a')):
        container((x, 2.0, 0), 0, col, open_doors=False)
    container((0, 2.0, 0), 0, '#a8462e')
    k = kid(loc=(0, 1.9, 0.05), age_h=0.5)
    k.sit(); k.root.location.z = 0.05
    life(c, k, 1, 0.4)
    k.brows_set(1, 0.4, 1)
    k.arm(0, 1, (-0.4, 0, 0.15)); k.arm(1, 1, (-0.4, 0, -0.15))
    blood_pool((0, 1.75, 0.105), 0.55, 1.2, 0.9)
    point((0, 2.4, 2.2), 70, '#ffb070', 0.3)
    point((0, -0.5, 1.5), 40, '#9fb4ff', 0.6)
    sun(rot=(0.9, 0.2, -0.6), energy=0.6, color='#8fa8ff')
    cam, t = camera((0, -3.5, 1.3), (0, 1.8, 0.7), 32)
    cam_move(cam, t, c, (0, -4.2, 1.4), (0, -0.2, 0.95), (0, 1.8, 0.7), (0, 1.9, 0.62))

def s02(c):
    night_world('#0a0d18', 0.2)
    floor('#2a2a30', 60)
    container((0, 2.0, 0), 0, '#a8462e')
    k = kid(loc=(0, 1.9, 0.05), age_h=0.5)
    k.sit(); k.root.location.z = 0.05
    life(c, k, 2, 0.3)
    k.brows_set(1, 0.45, 1)
    k.arm(0, 1, (-0.4, 0, 0.15)); k.arm(1, 1, (-0.4, 0, -0.15))
    k.look(1, 0.3, 0)
    blood_pool((0, 1.75, 0.105), 0.55, 1.2, 0.9)
    # luz da porta: noite -> dia -> noite (dois dias)
    sl = point((0, -0.2, 1.6), 60, '#ffffff', 0.6)
    for f, (e, col) in zip([1, int(c.n * 0.3), int(c.n * 0.55), int(c.n * 0.8), c.n],
                           [(30, '#6f86ff'), (160, '#ffd8a0'), (30, '#6f86ff'), (160, '#ffd8a0'), (40, '#6f86ff')]):
        sl.data.energy = e; sl.data.keyframe_insert('energy', frame=f)
        sl.data.color = hexc(col); sl.data.keyframe_insert('color', frame=f)
    point((0, 2.4, 2.2), 40, '#ffb070', 0.3)
    cam, t = camera((0, 0.4, 0.9), (0, 1.9, 0.75), 45)
    cam_move(cam, t, c, (0.25, 0.5, 0.95), (0.0, 0.9, 0.85), (0, 1.9, 0.75), (0, 1.9, 0.78))

def s03(c):
    setup_render(sky='#ffcf8a', sky_strength=0.6)
    floor('#6a5a4a', 60)
    box((60, 0.2, 30), (0, -20, 15), m=mat('#ffc88a', 1.0, emit=1.0))
    container((0, 2.0, 0), 0, '#a8462e')
    k = kid(loc=(0, 2.3, 0.05), age_h=0.5)
    k.sit(); k.root.location.z = 0.05
    life(c, k, 3, 0.3)
    blood_pool((0, 2.15, 0.105), 0.55, 1.2, 0.9)
    h = harry(loc=(0, -0.6, 0), rot=PI)
    f1 = int(c.n * 0.45)
    h.walk(1, f1, (0, -0.4, 0), (0, 1.15, 0), 1.4)
    h.auto_blink(1, c.n, 4)
    key(h.hips, 'location', f1 + 4, (0, 0, h.leg_len)); key(h.hips, 'location', f1 + 16, (0, 0, 0.1))
    for l in h.legs:
        key(l, 'rotation_euler', f1 + 4, (0, 0, 0)); key(l, 'rotation_euler', f1 + 16, (math.radians(88), 0, 0))
    h.arm(0, f1 + 22, (-1.1, 0, 0.3)); h.arm(1, f1 + 22, (-1.1, 0, -0.3))
    k.look(f1, -0.35, 0)
    k.arm(0, f1 + 26, (-1.0, 0, 0.2)); k.arm(1, f1 + 26, (-1.0, 0, -0.2))
    point((0, 1.0, 2.2), 90, '#ffd8a0', 0.4)
    sun(rot=(1.2, 0.0, 3.1), energy=2.2, color='#ffc89a')
    cam, t = camera((0.7, 3.7, 1.4), (0, 1.0, 0.9), 30)
    cam_move(cam, t, c, (0.75, 3.75, 1.45), (0.55, 3.5, 1.3), (0, 0.6, 1.1), (0, 1.1, 0.8))

def s04(c):
    night_world('#101a34', 0.4)
    floor('#2a4a2a', 60)
    box((60, 0.2, 30), (0, 14, 15), m=mat('#121c40', 1.0, emit=0.4))
    stars(40, 13.8, 4, (3, 14), 12)
    house = empty("house", (0, 5.0, 0))
    box((6, 3, 3), (0, 0, 1.5), m=mat('#e8dcc0', 0.8), parent=house, bevel=0.04)
    box((6.6, 3.6, 0.25), (0, 0, 3.1), m='#6a4a3a', parent=house)
    d = door((1.2, 3.48, 0), 0, '#5a3a24')
    window((-1.2, 3.47, 1.6), 0, 1.0, 0.9, '#ffd27a', emit=1.4)
    # monte de terra + pa
    sphere(1, (0.3, 1.2, 0), (0.5, 0.35, 0.18), mat('#5a3a22', 0.95))
    cyl(0.02, 1.0, (-0.1, 1.0, 0.5), (0.3, 0.2, 0), m='#8a6a42')
    box((0.18, 0.02, 0.22), (-0.06, 0.86, 0.06), rot=(0.3, 0.2, 0), m=mat('#9aa0a8', 0.3, metal=0.8))
    td = kid(name='teen', age_h=0.8, loc=(-0.45, 0.8, 0), rot=PI * 0.3, jacket='#4a6a4a', shirt='#4a6a4a', pants='#3a3a4a', body_w=0.86)
    life(c, td, 5, 0.5)
    h = harry(loc=(1.2, 3.1, 0), rot=PI * 0.08)
    life(c, h, 6)
    f1 = int(c.n * 0.45)
    h.brows_set(f1, 0.4); key(h.mouth, 'scale', f1, (1, 1, 0.35)); key(h.mouth, 'scale', f1 + 8, (1.1, 1, 0.9))
    td.look(f1 + 10, 0, 0.3)
    point((1.2, 2.6, 2.4), 90, '#ffd8a0', 0.5)
    point((0, -0.5, 2.2), 50, '#9fb4ff', 0.8)
    sun(rot=(0.9, 0.2, -0.6), energy=0.7, color='#8fa8ff')
    cam, t = camera((0, -3, 1.4), (0.2, 1.8, 1.1), 30)
    cam_move(cam, t, c, (-0.6, -3.2, 1.3), (0.2, -2.4, 1.45), (-0.2, 1.4, 1.0), (0.4, 2.0, 1.25))

def s05(c):
    night_world('#0e1424', 0.35)
    floor('#2a3a22', 60)
    box((60, 0.2, 30), (0, 12, 15), m=mat('#101830', 1.0, emit=0.35))
    stars(50, 11.8, 5, (3, 14), 12)
    for i, (x, y) in enumerate([(-3, 4), (3.2, 4.5), (-1.6, 6), (1.8, 6.5), (-4.5, 7), (4.6, 7.5)]):
        pine((x, y, 0), 1.2 + 0.2 * (i % 2), '#1a4a2a')
    fp, fl = flames((0, 0.6, 0), n=6, spread=0.18, h=0.55, seed=5)
    flicker(fl, 1, c.n, 5)
    for i in range(4):
        cyl(0.04, 0.5, (0, 0.6, 0.06), (PI / 2, 0, i * 0.8), m='#6a4228')
    for x in (-0.8, 0.8):
        cyl(0.18, 0.9, (x, 0.75, 0.18), (0, PI / 2, 0), m='#7a5232')
    h = harry(loc=(-0.85, 0.75, 0), rot=PI * 0.42, jacket='#5a5a3a', tie=None, badge=False)
    td = kid(name='teen', age_h=0.8, loc=(0.85, 0.75, 0), rot=-PI * 0.42, jacket='#4a6a4a', shirt='#4a6a4a', pants='#3a3a4a', body_w=0.86)
    for ch in (h, td):
        ch.sit(); ch.root.location.z = 0.12
    life(c, h, 7); life(c, td, 8)
    talk(c, h, 1, c.n, 0.9)
    h.arm(1, 20, (-1.0, 0, 0.3)); h.arm(1, 60, (-1.3, 0, 0.1)); h.arm(1, 100, (-1.0, 0, 0.3))
    h.brows_set(10, -0.25)
    pf = point((0, 0.6, 0.7), 140, '#ff9a4a', 0.3)
    for f in range(1, c.n + 1, 4):
        pf.data.energy = 120 + 30 * math.sin(f * 1.7); pf.data.keyframe_insert('energy', frame=f)
    sun(rot=(0.9, 0.2, -0.6), energy=0.6, color='#8fa8ff')
    cam, t = camera((0, -2.5, 1.2), (0, 0.8, 0.9), 30)
    cam_move(cam, t, c, (0.3, -2.8, 1.25), (0.0, -2.0, 1.15), (0, 0.8, 0.9), (0, 0.8, 0.95))

def s06(c):
    night_world('#0e1424', 0.35)
    floor('#2a3a22', 60)
    box((60, 0.2, 30), (0, 12, 15), m=mat('#101830', 1.0, emit=0.35))
    stars(40, 11.8, 6, (3, 14), 12)
    for i, (x, y) in enumerate([(-3, 4), (3.2, 4.5), (-1.6, 6), (1.8, 6.5)]):
        pine((x, y, 0), 1.3, '#1a4a2a')
    h = harry(loc=(0, 0.75, 0), rot=0, jacket='#5a5a3a', tie=None, badge=False)
    h.sit(); h.root.location.z = 0.12
    life(c, h, 9)
    talk(c, h, 1, c.n, 1.0)
    h.brows_set(4, -0.4)
    h.arm(1, 8, (-1.5, 0, -0.2))     # dedo apontado para a camera
    sphere(0.025, (0, -0.02, -0.5), m=SKIN, parent=h.arms[1])
    pf = point((0.2, 0.2, 0.5), 120, '#ff9a4a', 0.3)
    for f in range(1, c.n + 1, 4):
        pf.data.energy = 100 + 30 * math.sin(f * 1.7); pf.data.keyframe_insert('energy', frame=f)
    point((0, -1.0, 1.8), 30, '#9fb4ff', 0.8)
    cam, t = camera((0, -1.0, 1.25), (0, 0.75, 1.15), 45)
    cam_move(cam, t, c, (0, -1.2, 1.22), (0, -0.85, 1.2), (0, 0.75, 1.15), (0, 0.75, 1.17))

def miami_set(night=False):
    if night:
        night_world('#1a0a3a', 0.45)
    else:
        setup_render(sky='#7fd6ff')
    floor('#e8dcc0' if not night else '#3a2a4a', 120)
    box((120, 0.2, 40), (0, 24, 15), m=mat('#1a0a3a' if night else '#8fdcff', 1.0, emit=0.6 if night else 1.0))
    cols = ['#ffc9d9', '#b8f0e0', '#fff0a8', '#c9d8ff', '#ffd8b8']
    for i in range(6):
        pastel_building((-7.5 + i * 3.0, 9 + (i % 2) * 1.5, 0), 2.6, 2.0, 3.5 + (i % 3), cols[i % len(cols)])
    for i, x in enumerate([-5, -2, 2.2, 5]):
        palm((x, 5.5 + (i % 2), 0), 1.1, 0.12 * (-1) ** i, i)

def s07(c):
    miami_set()
    b = empty("pd", (0.6, 4.2, 0))
    box((5.0, 2.0, 3.6), (0, 0, 1.8), m=mat('#f2f2ee', 0.6), parent=b, bevel=0.05)
    box((5.4, 2.4, 0.25), (0, 0, 3.7), m='#3a6aa0', parent=b)
    t1 = text3d("MIAMI METRO POLICE", (0, -1.02, 3.1), size=0.3, m=mat('#1a3a6a', 0.3), font=BOLD, extrude=0.03); t1.parent = b
    door((0.6, 3.18, 0), 0, '#2a4a7a')
    for x in (-1.4, 2.4):
        window((x, 3.17, 1.6), 0, 1.2, 1.0, '#9fe0ff', emit=0.5)
    d = dexter(loc=(-1.6, 0.0, 0), rot=PI * 0.5)
    d.walk(1, int(c.n * 0.75), (-2.2, 0.2, 0), (0.2, 1.6, 0), 1.7)
    key(d.root, 'rotation_euler', 1, (0, 0, PI * 0.66)); key(d.root, 'rotation_euler', int(c.n * 0.75), (0, 0, PI * 0.66))
    key(d.root, 'rotation_euler', int(c.n * 0.75) + 8, (0, 0, 0.15))
    d.auto_blink(1, c.n, 10)
    box((0.12, 0.38, 0.28), (0, 0, -0.6), m=mat('#2a2a2e', 0.3), parent=d.arms[0], bevel=0.02)   # maleta
    smile(d, int(c.n * 0.85))
    sun(rot=(0.8, 0.1, 0.6), energy=3.8)
    cam, t = camera((0, -4, 1.5), (0, 1.5, 1.6), 30)
    cam_move(cam, t, c, (0.6, -4.6, 1.3), (0.4, -2.8, 1.45), (-0.6, 2.0, 2.0), (0.2, 1.4, 1.35))

def s08(c):
    station()
    d = dexter(loc=(-0.2, 0.0, 0), rot=0.2)
    life(c, d, 11)
    donut_box((0, -0.32, -0.02), parent=d.chest)
    d.arm(0, 1, (-1.2, 0, 0.35)); d.arm(1, 1, (-1.2, 0, -0.35))
    smile(d, 10, big=True)
    deb = debra(loc=(0.75, 0.55, 0), rot=-PI * 0.3)
    cop = generic_person(401, (-1.0, 0.7, 0), rot=PI * 0.3, jacket='#2a3a5a', collar=True, tie='#1a2a4a', female=False)
    life(c, deb, 12); life(c, cop, 13)
    f1 = int(c.n * 0.5)
    for ch in (deb, cop):
        smile(ch, f1)
    deb.arm(1, f1 + 6, (-1.2, 0, 0.5))
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2.4, 1.45), (0, 0.3, 1.25), 32)
    cam_move(cam, t, c, (0.2, -2.6, 1.5), (0, -2.0, 1.45), (0, 0.3, 1.25), (0, 0.3, 1.3))

def s09(c):
    miami_set(night=True)
    for i in range(6):
        sphere(0.1, (-7.5 + i * 3.0, 7.9 + (i % 2) * 1.5, 3.0), m=mat(['#ff3a8a', '#3affd0', '#ffd23f'][i % 3], emit=8), seg=12)
    d = dexter_kill(loc=(0, 0.4, 0), rot=0)
    life(c, d, 14, 0.5)
    d.brows_set(1, -0.3, 1)
    # calcando as luvas
    d.arm(0, 1, (-1.3, 0, 0.6)); d.arm(1, 1, (-1.2, 0, -0.5))
    d.arm(1, 30, (-1.25, 0, -0.62)); d.arm(1, 50, (-1.2, 0, -0.5)); d.arm(1, 70, (-1.25, 0, -0.62))
    point((1.5, -0.5, 2.0), 160, '#ff3a8a', 0.6)
    point((-1.5, -0.5, 2.0), 140, '#3affd0', 0.6)
    point((0, -1.0, 2.6), 40, '#ffffff', 0.6)
    cam, t = camera((0, -1.6, 1.3), (0, 0.4, 1.2), 40)
    cam_move(cam, t, c, (0, -2.2, 1.0), (0, -1.3, 1.25), (0, 0.4, 1.3), (0, 0.4, 1.25))

def s10(c):
    night_world('#0a0a10', 0.3)
    floor('#3a3a3e', 40)
    plastic_sheet((0, 2.0, 0), 5.0, 3.0, seed=1)
    plastic_sheet((-2.2, 0.0, 0), 4.0, 3.0, (0, 0, PI / 2), seed=2)
    plastic_sheet((2.2, 0.0, 0), 4.0, 3.0, (0, 0, -PI / 2), seed=3)
    box((2.6, 3.0, 0.02), (0, 0.5, 0.012), m=mat('#e4eef6', 0.12, spec=1.0))
    table((0, 0.8, 0), (0.9, 2.0), 0.8, '#d8dde4', '#7a8090')
    tgt = generic_person(410, (0, 0, 0), jacket='#5a4a3a', female=False, hair_style='short')
    tgt.root.rotation_euler = (-PI / 2, 0, 0); tgt.root.location = (0, -0.05, 1.0)
    box((0.62, 1.95, 0.34), (0, 0.8, 1.0), m=mat('#e8f2fa', 0.08, spec=1.0), bevel=0.12)   # embalado em plastico
    d = dexter_kill(loc=(1.0, 0.25, 0), rot=-0.15)
    life(c, d, 15, 0.5)
    f1 = int(c.n * 0.55)
    d.arm(1, f1 - 8, (-0.2, 0, 0)); d.arm(1, f1, (-2.05, 0, 0.35))
    d.look(f1 + 2, -0.15, 0.25)
    sl = box((0.06, 0.16, 0.008), (0, -0.06, -0.52), rot=(PI / 2, 0, 0), m=mat('#e4f4fc', 0.05, spec=1.0, emit=0.15), parent=d.arms[1])
    sphere(1, (0, -0.066, -0.52), (0.018, 0.004, 0.018), mat('#b0101a', 0.1), d.arms[1], seg=12)
    bpy.context.view_layer.update()
    slide_box((1.6, 0.9, 0.0), rot=0.3)
    table((1.6, 0.9, 0), (0.6, 0.4), 0.7, '#8a8e96', '#5a5e66')
    for o in bpy.data.objects:
        if o.name.startswith('slides'):
            o.location.z = 0.73
    point((0, 0.8, 2.6), 220, '#f4f8ff', 0.4)
    point((0, -1.5, 1.6), 30, '#9fb4ff', 0.8)
    cam, t = camera((0, -2.6, 1.8), (0, 0.6, 1.0), 32)
    key(cam, 'location', 1, (-0.9, -2.6, 2.0)); key(t, 'location', 1, (0.3, 0.6, 1.0))
    key(cam, 'location', f1 - 6, (-0.2, -2.1, 1.75)); key(t, 'location', f1 - 6, (0.6, 0.4, 1.15))
    d.arms[1].rotation_euler = (-2.05, 0, 0.35); bpy.context.view_layer.update()
    hp = d.arms[1].matrix_world @ Vector((0, -0.06, -0.52))
    key(cam, 'location', f1 + 10, (hp.x - 0.22, hp.y - 1.25, hp.z - 0.02)); key(t, 'location', f1 + 10, (hp.x - 0.12, hp.y, hp.z - 0.04))
    key(cam, 'location', c.n, (hp.x - 0.2, hp.y - 1.05, hp.z - 0.02)); key(t, 'location', c.n, (hp.x - 0.12, hp.y, hp.z - 0.04))

def s11(c):
    night_world('#0a1028', 0.4)
    sea(200, '#123a5a', 0.0, 0.1)
    box((200, 0.2, 40), (0, 60, 15), m=mat('#0e1838', 1.0, emit=0.45))
    stars(80, 59.8, 11, (2, 26), 40)
    sphere(2.2, (-10, 59, 14), m=mat('#fff6d0', emit=3))
    bt = boat((0, 1.5, 0.0), 0)
    d = dexter_kill(loc=(0, 0, 0), rot=0)
    d.root.parent = bt; d.root.location = (-0.35, 1.75, 0.68); d.root.rotation_euler = (0, 0, -PI * 0.42)
    life(c, d, 16, 0.4)
    bags = []
    f1 = int(c.n * 0.4)
    for k in range(2):
        b = trash_bag((0, 0, 0), 0.8, 20 + k)
        fk = f1 + k * 18
        key(b, 'location', 1, (-0.75, 3.0 + k * 0.45, 0.95)); key(b, 'location', fk, (-0.75, 3.0 + k * 0.45, 0.95))
        key(b, 'location', fk + 10, (-1.5, 3.0 + k * 0.45, 0.2)); key(b, 'location', fk + 24, (-1.6, 3.0 + k * 0.45, -1.0))
        bags.append(b)
    d.arm(0, f1 - 6, (-1.2, 0, 0)); d.arm(0, f1 + 6, (-0.6, 0, 0)); d.arm(0, f1 + 18, (-1.2, 0, 0)); d.arm(0, f1 + 30, (-0.4, 0, 0))
    for f in range(1, c.n + 1, 6):     # balanco do barco
        bt.rotation_euler = (0.03 * math.sin(f / 8), 0.02 * math.sin(f / 11), 0); bt.keyframe_insert('rotation_euler', frame=f)
    sun(rot=(0.9, 0.2, -0.9), energy=1.0, color='#9fb4ff')
    point((0, -1.0, 3.0), 120, '#c0d0ff', 1.5)
    cam, t = camera((-5.0, 0.0, 2.2), (0, 2.2, 0.8), 32)
    cam_move(cam, t, c, (-5.4, -0.6, 2.4), (-4.2, 0.6, 1.8), (0, 2.0, 0.9), (-0.8, 3.0, 0.6))

def s12(c):
    station()
    deb = debra(loc=(0.42, 0.2, 0), rot=-PI * 0.36)
    d = dexter(loc=(-0.42, 0.2, 0), rot=PI * 0.36)
    life(c, deb, 17); life(c, d, 18)
    talk(c, deb, 1, c.n, 1.0)
    deb.brows_set(5, -0.3)
    for k, f in enumerate(range(10, c.n, 26)):
        deb.arm(1, f, (-1.0 - 0.3 * (k % 2), 0, -0.4))
    smile(d, 20)
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2.4, 1.45), (0, 0.2, 1.3), 38)
    cam_move(cam, t, c, (0, -2.8, 1.45), (0, -2.2, 1.42), (0, 0.2, 1.3), (0, 0.2, 1.32))

def s13(c):
    setup_render(sky='#bfe9ff')
    room('#ffe0c0', '#fff0dc', '#e8c9a0', '#d8b890', back_y=2.6, side_x=-3.0)
    couch((0, 2.0, 0), 0, '#5a8ab0', 2.4)
    window((1.8, 2.45, 1.6), 0, 1.2, 1.0, '#bfe9ff', emit=0.8)
    r = rita(loc=(0.15, 0.6, 0))
    d = dexter(loc=(-0.45, 0.55, 0), rot=0.12)
    a = kid(name='astor', age_h=0.62, loc=(0.75, 0.3, 0), hair='#e8cf8a', hair_style='long', jacket='#9a5ae8', shirt='#9a5ae8', pants='#3a3a5a', female=True)
    co = kid(name='cody', age_h=0.5, loc=(0.6, -0.1, 0), hair='#e8cf8a', jacket='#3ab0e8', shirt='#3ab0e8')
    for k, ch in enumerate((r, d, a, co)):
        life(c, ch, 20 + k)
    for ch in (r, a, co):
        smile(ch, 10)
    smile(d, 15, big=True)
    f1 = int(c.n * 0.6)
    key(d.mouth, 'scale', f1, (1.6, 1, 0.55)); key(d.mouth, 'scale', f1 + 6, (0.8, 1, 0.3))   # sorriso falso some
    d.look(f1 + 4, 0, -0.35)
    sun(rot=(0.8, 0.1, 0.4), energy=3.0)
    cam, t = camera((0, -2.6, 1.3), (0.1, 0.4, 1.0), 32)
    cam_move(cam, t, c, (0.2, -3.0, 1.3), (-0.2, -2.0, 1.4), (0.1, 0.4, 1.0), (-0.35, 0.5, 1.3))

def s14(c):
    night_world('#0a0d18', 0.3)
    floor('#2a2a2e', 60)
    box((60, 0.2, 30), (0, 14, 15), m=mat('#0e1428', 1.0, emit=0.35))
    ice_truck((-0.6, 3.6, 0), PI / 2 - 0.25)
    b = brian(loc=(0.45, 0.6, 0), rot=-PI * 0.4)
    d = dexter_kill(loc=(-0.45, 0.6, 0), rot=PI * 0.4)
    life(c, b, 24); life(c, d, 25)
    smile(b, 10)
    d.brows_set(5, -0.35)
    f1 = int(c.n * 0.7)
    # no fim: so o Dexter, de cabeca baixa
    hide_between(b.root, None, f1)
    d.look(f1 + 6, 0.35, 0)
    d.brows_set(f1 + 6, 0.35)
    point((0, 0.0, 2.6), 120, '#c0d0ff', 0.6)
    lr = point((-0.6, 2.0, 1.6), 60, '#7fd4ff', 0.6)
    keys(lr.data, 'energy', [(f1, 60), (f1 + 8, 0)])
    sun(rot=(0.9, 0.2, -0.6), energy=0.6, color='#8fa8ff')
    cam, t = camera((0, -2.6, 1.4), (0, 0.6, 1.3), 32)
    key(cam, 'location', 1, (0.4, -3.0, 1.5)); key(t, 'location', 1, (-0.3, 1.2, 1.4))
    key(cam, 'location', f1 - 4, (0.0, -2.2, 1.45)); key(t, 'location', f1 - 4, (0, 0.6, 1.35))
    key(cam, 'location', f1 + 6, (0.45, -0.9, 1.42)); key(t, 'location', f1 + 6, (-0.45, 0.6, 1.32))
    key(cam, 'location', c.n, (0.4, -0.75, 1.4))

def s15(c):
    setup_render(sky='#0a3a5a', sky_strength=0.7)
    floor('#c9b88a', 60)
    box((60, 0.2, 30), (0, 14, 15), m=mat('#0e4a6e', 1.0, emit=0.6))
    for i in range(10):
        cone(0.4, 0.05, 6, (-6 + i * 1.4, 6, 3), (0.2, 0, 0.1 * (i - 5)), m=mat('#7fd4ff', 0.5, emit=0.25), verts=12)   # raios de luz
    rnd = random.Random(15)
    for i in range(14):
        trash_bag((rnd.uniform(-2.4, 2.4), rnd.uniform(0.2, 4.0), 0), rnd.uniform(0.7, 1.0), 40 + i, rnd.uniform(0, 3))
    for i in range(6):
        sphere(1, (rnd.uniform(-3, 3), rnd.uniform(1, 5), 0.1), (0.6, 0.6, 0.12), mat('#3a8a5a', 0.8))   # algas/pedras
    bubbles = []
    for i in range(18):
        x, y = rnd.uniform(-2, 2), rnd.uniform(0, 3)
        bb = sphere(rnd.uniform(0.03, 0.06), (x, y, 0.2), m=mat('#e8f8ff', 0.05, emit=0.5), seg=10)
        key(bb, 'location', 1, (x, y, rnd.uniform(0.0, 0.6)), 'LINEAR'); key(bb, 'location', c.n, (x, y, rnd.uniform(2.5, 4.0)), 'LINEAR')
    sun(rot=(0.3, 0.1, 0.3), energy=2.0, color='#9fe0ff')
    point((0, 0, 3), 150, '#7fd4ff', 2.0)
    cam, t = camera((0, -3, 1.6), (0, 1.8, 0.4), 30)
    cam_move(cam, t, c, (-0.8, -3.2, 1.8), (0.6, -2.4, 1.3), (0, 1.8, 0.4), (0, 2.2, 0.3))

def s16(c):
    setup_render(sky='#bfe9ff')
    station(extra=False)
    d = dexter(loc=(0, 0.3, 0))
    life(c, d, 26, 0.5)
    d.brows_set(4, -0.3)
    smile(d, 14)
    key(d.mouth, 'rotation_euler', 8, (0.3, 0, 0)); key(d.mouth, 'rotation_euler', 14, (0.3, 0, 0.15))
    for e in d.eyes[1:]:
        key(e, 'scale', 30, (1, 1, 1)); key(e, 'scale', 34, (1, 1, 0.1)); key(e, 'scale', 46, (1, 1, 0.1)); key(e, 'scale', 50, (1, 1, 1))
    sun(rot=(0.8, 0.1, 0.4), energy=3.4)
    cam, t = camera((0, -1.0, 1.42), (0, 0.3, 1.38), 50)
    cam_move(cam, t, c, (0, -1.25, 1.42), (0, -0.95, 1.41), (0, 0.3, 1.38), (0, 0.3, 1.38))

def s17(c):
    station()
    dk = doakes(loc=(0.45, 0.3, 0), rot=-PI * 0.38)
    d = dexter(loc=(-0.45, 0.3, 0), rot=PI * 0.38)
    life(c, dk, 27); life(c, d, 28)
    dk.brows_set(1, -0.5, 1)
    talk(c, dk, 1, int(c.n * 0.55), 1.0)
    dk.arm(1, 15, (-1.45, 0, -0.35))    # aponta para o Dexter
    sphere(0.025, (0, -0.02, -0.5), m='#6a4430', parent=dk.arms[1])
    smile(d, 12)
    f1 = int(c.n * 0.62)
    d.look(f1, 0, 0.3)
    key(d.mouth, 'scale', f1, (1.4, 1, 0.55)); key(d.mouth, 'scale', f1 + 6, (0.9, 1, 0.3))
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2.4, 1.45), (0, 0.3, 1.32), 36)
    key(cam, 'location', 1, (0.2, -2.6, 1.45)); key(t, 'location', 1, (0, 0.3, 1.32))
    key(cam, 'location', f1 - 4, (0.2, -2.2, 1.45)); key(t, 'location', f1 - 4, (0.1, 0.3, 1.32))
    key(cam, 'location', f1 + 8, (0.4, -0.85, 1.45)); key(t, 'location', f1 + 8, (-0.45, 0.3, 1.38))
    key(cam, 'location', c.n, (0.35, -0.72, 1.44))

def s18(c):
    setup_render(sky='#bfe9ff')
    floor('#8fe08f', 100)
    box((80, 0.2, 40), (0, 25, 15), m=mat('#bfe9ff', 1.0, emit=1.0))
    for i, (x, z) in enumerate([(-5, 8), (5, 10)]):
        cloud((x, 22, z), 1.5, 10 + i)
    palm((-3.2, 2.5, 0), 1.0, 0.1, 1); palm((3.4, 3.0, 0), 1.1, -0.1, 2)
    flower_arch((0, 1.2, 0), 2.2, 2.7)
    box((1.2, 6, 0.02), (0, -1.5, 0.012), m='#ffffff')
    r = rita(loc=(0.33, 0.8, 0), rot=-PI * 0.12, dress='#ffffff', hat='veil')
    d = dexter(loc=(-0.33, 0.8, 0), rot=PI * 0.12, jacket='#2a2e38', shirt='#ffffff', pants='#2a2e38', tie='#2a2e38')
    life(c, d, 30); life(c, r, 31)
    smile(d, 8); smile(r, 8)
    f1 = 80      # 'filho, o Harrison'
    bb = baby(loc=(0, 0.35, 1.05))
    bb.scale = (1.3, 1.3, 1.3)
    pop_in(bb, f1, 10, 1.2)
    rnd = random.Random(18)
    cols = ['#ff7eb6', '#ffd23f', '#7fd4ff', '#ffffff', '#b388ff']
    for i in range(50):
        x, y, z = rnd.uniform(-1.6, 1.6), rnd.uniform(-0.5, 1.6), rnd.uniform(2.5, 4.0)
        cf = box((0.04, 0.04, 0.008), (x, y, z), m=rnd.choice(cols))
        key(cf, 'location', 1, (x, y, z), 'LINEAR'); key(cf, 'location', c.n, (x + rnd.uniform(-0.4, 0.4), y, z - rnd.uniform(2.0, 3.0)), 'LINEAR')
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -3, 1.4), (0, 0.8, 1.3), 32)
    cam_move(cam, t, c, (0, -3.3, 1.3), (0, -2.3, 1.42), (0, 0.9, 1.4), (0, 0.6, 1.25))

def bathroom(dark=True):
    night_world('#0a0a12', 0.28) if dark else setup_render(sky='#dfe8ef')
    checker_floor('#e8e8ec', '#c9ccd4', size=20, scale=0.35)
    box((8, 0.2, 3.0), (0, 2.2, 1.5), m=mat('#bfe0e8', 0.4))
    box((0.2, 8, 3.0), (-1.8, -1.0, 1.5), m=mat('#a8d0dc', 0.4))
    # banheira
    box((1.9, 0.9, 0.6), (-0.6, 1.55, 0.3), m=mat('#f8f8f8', 0.2, spec=0.8), bevel=0.12)
    box((1.6, 0.6, 0.02), (-0.6, 1.55, 0.55), m=mat('#7a0a12', 0.05, spec=1.0))
    cyl(0.03, 0.3, (-1.45, 1.55, 0.8), m=mat('#c9ccd4', 0.2, metal=1.0))

def s19(c):
    night_world('#0a0a12', 0.3)
    f1 = int(c.n * 0.61)     # 'E a Rita...'
    # parte 1 (longe, em x=20): Trindade nas sombras
    floor('#1a1a22', 10, loc=(20, 0, 0))
    box((8, 0.2, 4), (20, 2.2, 2), m=mat('#2a2a34', 0.9))
    tr = trinity(loc=(20, 0.8, 0))
    life(c, tr, 32, 0.4)
    tr.brows_set(1, -0.3, 1)
    smile(tr, 20)
    point((20.6, 0.0, 2.2), 90, '#ffd8a8', 0.3)
    # parte 2: banheiro fechado (agua vermelha, sem corpo), Dexter na porta
    checker_floor('#e8e8ec', '#c9ccd4', size=8, scale=0.35)
    box((8, 0.2, 3.0), (0, 2.2, 1.5), m=mat('#bfe0e8', 0.4))
    box((0.2, 8, 3.0), (-1.8, -1.0, 1.5), m=mat('#a8d0dc', 0.4))
    box((0.2, 2.4, 3.0), (2.0, 1.0, 1.5), m=mat('#a8d0dc', 0.4))
    box((0.2, 2.4, 3.0), (2.0, -1.9, 1.5), m=mat('#a8d0dc', 0.4))
    box((0.2, 1.0, 0.8), (2.0, -0.7, 2.6), m=mat('#a8d0dc', 0.4))
    box((0.1, 1.1, 2.3), (2.25, -0.7, 1.15), m=mat('#1a1a22', 0.9))
    box((1.9, 0.9, 0.6), (-0.6, 1.55, 0.3), m=mat('#f8f8f8', 0.2, spec=0.8), bevel=0.12)
    box((1.6, 0.6, 0.02), (-0.6, 1.55, 0.55), m=mat('#7a0a12', 0.05, spec=1.0))
    cyl(0.03, 0.3, (-1.45, 1.55, 0.8), m=mat('#c9ccd4', 0.2, metal=1.0))
    d = dexter(loc=(1.4, -0.6, 0), rot=-PI * 0.62)
    life(c, d, 33, 0.3)
    point((0, 0.4, 2.6), 90, '#ffe8d8', 0.4)
    pr = point((-0.6, 1.0, 1.4), 0, '#ff2a2a', 0.4)
    keys(pr.data, 'energy', [(f1, 0), (f1 + 10, 45)])
    cam, t = camera((20, -1.3, 1.45), (20, 0.8, 1.38), 45)
    key(cam, 'location', 1, (20.0, -1.5, 1.45)); key(t, 'location', 1, (20.0, 0.8, 1.38))
    key(cam, 'location', f1 - 1, (20.0, -1.1, 1.43), 'CONSTANT'); key(t, 'location', f1 - 1, (20.0, 0.8, 1.38), 'CONSTANT')
    key(cam, 'location', f1, (-1.3, 0.6, 1.7), 'CONSTANT'); key(t, 'location', f1, (1.3, -0.5, 1.15), 'CONSTANT')
    key(cam, 'location', c.n, (-1.1, 0.75, 1.62)); key(t, 'location', c.n, (1.4, -0.6, 1.3))
    d.brows_set(f1 + 4, 0.5); key(d.mouth, 'scale', f1 + 2, (1, 1, 0.35)); key(d.mouth, 'scale', f1 + 10, (1.1, 1, 1.0))

def s20(c):
    bathroom(dark=True)
    hb = kid(name='harrison', age_h=0.4, loc=(0.2, 0.6, 0.0), hair='#c9a46a', jacket='#bfe0ff', shirt='#bfe0ff', pants='#bfe0ff', body_w=0.7)
    hb.sit(); hb.root.location.z = 0.03
    life(c, hb, 34, 0.4)
    hb.arm(0, 1, (-0.5, 0, 0.2)); hb.arm(1, 1, (-0.5, 0, -0.2))
    blood_pool((0.2, 0.5, 0.012), 0.5, 1.2, 0.9)
    point((0, 0.0, 2.6), 90, '#ffe8d8', 0.4)
    point((-0.6, 1.0, 1.4), 40, '#ff2a2a', 0.4)
    cam, t = camera((0.2, -1.2, 0.6), (0.2, 0.6, 0.55), 40)
    cam_move(cam, t, c, (0.25, -1.6, 0.75), (0.2, -0.75, 0.6), (0.2, 0.6, 0.55), (0.2, 0.6, 0.58))

def s21(c):
    night_world('#0a0812', 0.35)
    floor('#4a3a30', 60)
    box((10, 0.2, 6), (0, 4.0, 3), m=mat('#5a4e48', 0.9))
    for sx in (-1, 1):
        box((0.2, 14, 6), (sx * 3.2, -2, 3), m=mat('#4e4440', 0.9))
    stained_glass((0, 3.88, 1.6), 1.6, 2.8, 3)
    for x in (-2.0, 2.0):
        stained_glass((x, 3.88, 1.8), 0.9, 2.2, int(x + 5))
    box((2.0, 0.9, 1.0), (0, 2.8, 0.5), m='#7a5a3a', bevel=0.03)          # altar
    plastic_sheet((0, 3.6, 0), 3.0, 2.4, seed=4)
    for i in range(4):
        for x in (-1.3, 1.3):
            pew((x, 0.4 - i * 1.0, 0), 0, 1.6)
    d = dexter_kill(loc=(0.3, 2.1, 0), rot=PI)
    life(c, d, 35, 0.5)
    f1 = int(c.n * 0.35)
    key(d.root, 'rotation_euler', f1, (0, 0, PI)); key(d.root, 'rotation_euler', f1 + 10, (0, 0, 0.1))
    d.brows_set(f1 + 10, 0.45); key(d.mouth, 'scale', f1 + 8, (1, 1, 0.35)); key(d.mouth, 'scale', f1 + 16, (1.1, 1, 1.0))
    deb = debra(loc=(0.0, -1.3, 0), rot=PI * 0.95)
    life(c, deb, 36)
    deb.brows_set(f1, 0.5); key(deb.mouth, 'scale', f1, (1, 1, 0.35)); key(deb.mouth, 'scale', f1 + 8, (1.2, 1, 1.3))
    point((0, 2.0, 3.0), 200, '#ffd8a8', 0.6)
    point((0, 3.0, 1.6), 60, '#b05ae8', 1.0)
    point((0.8, -2.2, 2.6), 90, '#ffe8c8', 0.8)
    cam, t = camera((1.9, -3.4, 1.6), (-0.1, 0.4, 1.2), 26)
    cam_move(cam, t, c, (2.1, -3.7, 1.65), (1.7, -3.0, 1.55), (-0.1, 0.5, 1.2), (-0.1, 0.3, 1.25))

def s22(c):
    night_world('#0a0d18', 0.35)
    floor('#2a2a2e', 80)
    box((80, 0.2, 30), (0, 16, 15), m=mat('#0e1428', 1.0, emit=0.35))
    cols = ['#a8462e', '#2a5a8a', '#3a7a4a', '#c9a23a']
    for i in range(5):
        container((-6 + i * 3.0, 5.5, 0), 0, cols[i % 4], open_doors=False)
        container((-6 + i * 3.0, 5.5, 2.65), 0, cols[(i + 2) % 4], open_doors=False)
    deb = debra(loc=(0, 0.6, 0), rot=PI * 0.08)
    life(c, deb, 37)
    f1 = int(c.n * 0.35)
    deb.arm(1, f1 - 8, (-0.4, 0, 0)); deb.arm(1, f1, (-1.55, 0, 0.0)); deb.arm(0, f1, (-1.5, 0, -0.35))
    gun = box((0.04, 0.15, 0.07), (0, -0.07, -0.47), m='#222222', parent=deb.arms[1], bevel=0.01)
    hide_between(gun, f1 - 8, None)
    fl = sphere(0.1, (0, -0.28, -0.47), m=mat('#fff3a0', emit=12), parent=deb.arms[1])
    f2 = 97      # na palavra 'matar'
    hide_between(fl, f2, f2 + 3)
    flash = point((0, 0.0, 1.3), 0, '#fff0b0', 0.2)
    keys(flash.data, 'energy', [(f2 - 1, 0), (f2, 1600), (f2 + 5, 0)], 'LINEAR')
    deb.brows_set(f2 + 4, 0.5); key(deb.mouth, 'scale', f2 + 4, (1, 1, 0.35)); key(deb.mouth, 'scale', f2 + 10, (1.1, 1, 0.9))
    point((0, -1.5, 2.6), 140, '#c0d0ff', 0.8)
    sun(rot=(0.9, 0.2, -0.6), energy=0.6, color='#8fa8ff')
    cam, t = camera((0.6, -2.0, 1.5), (0, 0.6, 1.35), 36)
    cam_move(cam, t, c, (0.9, -2.4, 1.5), (0.5, -1.6, 1.45), (0, 0.6, 1.35), (0, 0.6, 1.35))

def s23(c):
    setup_render(sky='#d8f0f0')
    room('#cdeee6', None, '#e8f2f0', '#d8e8e4', back_y=1.8, side_x=-2.4)
    bed((-0.4, 0.6, 0), -PI / 2, '#ffffff', '#9fc8e8')
    deb = debra(loc=(0, 0, 0), jacket='#9fc8e8', shirt='#9fc8e8', pants='#9fc8e8', badge=False)
    deb.root.rotation_euler = (0, PI / 2, 0); deb.root.location = (-1.25, 0.6, 0.86)
    for e in deb.eyes:
        e.scale = (1, 1, 0.1)
    box((0.4, 0.3, 0.35), (-1.6, 1.4, 1.3), m='#2a2e36', bevel=0.03)
    mon = box((0.34, 0.02, 0.26), (-1.6, 1.24, 1.3), m=mat('#2aff8a', 0.3, emit=1.2))
    d = dexter(loc=(0.75, 0.0, 0), rot=-PI * 0.42)
    d.sit(); chair((0.78, 0.02, 0), -PI * 0.42, '#7a8a9a')
    life(c, d, 38, 0.5)
    d.brows_set(1, 0.45, 1)
    d.arm(1, 1, (-1.1, 0, -0.35))
    sun(rot=(0.8, 0.1, 0.5), energy=2.8)
    cam, t = camera((0.6, -2.2, 1.5), (-0.1, 0.5, 1.0), 30)
    cam_move(cam, t, c, (0.9, -2.5, 1.55), (0.5, -1.8, 1.4), (-0.2, 0.5, 1.0), (0.1, 0.4, 1.0))

def s24(c):
    setup_render(sky='#bfe9ff')
    floor('#c9c0b0', 80)
    box((80, 0.2, 40), (0, 20, 15), m=mat('#bfe9ff', 1.0, emit=1.0))
    for i, x in enumerate([-4, 4]):
        palm((x, 4, 0), 1.0, 0.1 * (-1) ** i, i)
    pastel_building((-2.5, 7, 0), 3.0, 2, 4, '#c9d8ff'); pastel_building((2.5, 7, 0), 3.0, 2, 3.5, '#ffd8b8')
    d = dexter(loc=(-0.45, 0.4, 0), rot=PI * 0.4)
    hb = kid(name='harrison', age_h=0.46, loc=(0.25, 0.4, 0), rot=-PI * 0.4, hair='#c9a46a', jacket='#3ab0e8', shirt='#3ab0e8')
    hn = hannah(loc=(0.75, 0.55, 0), rot=-PI * 0.3)
    life(c, hb, 39); life(c, hn, 40)
    d.kneel(); life(c, d, 41, 0.4)
    d.arm(0, 8, (-1.3, 0, 0.45)); d.arm(1, 8, (-1.3, 0, -0.45))
    hb.arm(0, 8, (-1.3, 0, 0.45)); hb.arm(1, 8, (-1.3, 0, -0.45))
    d.brows_set(1, 0.45, 1)
    f1 = int(c.n * 0.55)
    d.arm(0, f1, (-0.3, 0, 0)); d.arm(1, f1, (-0.3, 0, 0))
    hb.walk(f1, c.n, (0.25, 0.4, 0), (1.3, 1.4, 0), 2.4, 0.015)
    key(hb.root, 'rotation_euler', f1, (0, 0, -PI * 0.4)); key(hb.root, 'rotation_euler', f1 + 6, (0, 0, PI * 0.8))
    hn.walk(f1, c.n, (0.75, 0.55, 0), (1.8, 1.6, 0), 1.6)
    key(hn.root, 'rotation_euler', f1, (0, 0, -PI * 0.3)); key(hn.root, 'rotation_euler', f1 + 6, (0, 0, PI * 0.78))
    sun(rot=(0.8, 0.1, 0.6), energy=3.4)
    cam, t = camera((0, -2.8, 1.3), (0.1, 0.6, 0.9), 32)
    cam_move(cam, t, c, (-0.2, -2.6, 1.2), (0.3, -3.0, 1.4), (0.0, 0.5, 0.85), (0.5, 0.9, 1.0))

def s25(c):
    night_world('#0a0e18', 0.35)
    sea(200, '#1a2a38', 0.0, 0.15)
    box((200, 0.2, 60), (0, 40, 20), m=mat('#1a2230', 1.0, emit=0.35))
    for i in range(6):
        cloud((-14 + i * 6, 30, 9 + (i % 2) * 2), 3.0, 50 + i, color='#3a4250')
    ws = waves(70, 10, -2, 25, '#2e4a62', 0.28)
    for w in ws:
        w.scale = (w.scale[0] * 1.8, w.scale[1] * 1.3, w.scale[2])
        w.data.materials[0] = mat('#2e4a62', 0.4, spec=0.5)
    for k, w in enumerate(ws):
        z0 = w.location.z
        for f in range(1, c.n + 1, 8):
            w.location.z = z0 + 0.25 * math.sin(f / 9 + k); w.keyframe_insert('location', frame=f)
    bt = boat((0, 1.0, 0.15), PI)
    key(bt, 'location', 1, (0, 0.5, 0.15)); key(bt, 'location', c.n, (0, 8.0, 0.15))
    for f in range(1, c.n + 1, 4):
        bt.rotation_euler = (0.12 * math.sin(f / 5), 0.1 * math.sin(f / 7), PI); bt.keyframe_insert('rotation_euler', frame=f)
    # chuva
    rnd = random.Random(25)
    for i in range(140):
        x, y, z = rnd.uniform(-5, 5), rnd.uniform(-2, 10), rnd.uniform(0.5, 8)
        r = cyl(0.008, 0.5, (x, y, z), (0.25, 0, 0), m=mat('#bcd0e8', 0.3, emit=0.4), verts=6)
        ph = rnd.randint(0, 20)
        for f in range(1, c.n + 1, 20):
            key(r, 'location', f, (x, y, 8.0), 'LINEAR'); key(r, 'location', f + 19, (x - 1.5, y, 0.0), 'LINEAR')
    lt = point((2, 6, 10), 0, '#e8f0ff', 3.0)
    ev = [(1, 0)]
    for fl in (int(c.n * 0.25), int(c.n * 0.6), int(c.n * 0.85)):
        ev += [(fl - 1, 0), (fl, 4000), (fl + 2, 500), (fl + 3, 3000), (fl + 6, 0)]
    keys(lt.data, 'energy', ev, 'LINEAR')
    sun(rot=(0.9, 0.2, -0.6), energy=0.5, color='#8fa8ff')
    point((0, -2.0, 3.0), 80, '#c0d0ff', 2.0)
    cam, t = camera((0, -5, 2.4), (0, 4, 0.8), 30)
    cam_move(cam, t, c, (1.0, -5.5, 2.2), (0.3, -3.5, 2.6), (0, 3, 0.8), (0, 6, 1.0))

def s26(c):
    setup_render(sky='#c9d8e8')
    sea(200, '#4a7a9a', 0.0, 0.12)
    box((200, 0.2, 60), (0, 50, 20), m=mat('#d8e4ee', 1.0, emit=1.0))
    rnd = random.Random(26)
    for i in range(9):
        x, y = rnd.uniform(-2.5, 2.5), rnd.uniform(0.5, 6)
        p = box((rnd.uniform(0.3, 0.9), rnd.uniform(0.15, 0.3), 0.06), (x, y, 0.03), rot=(0, 0, rnd.uniform(0, 3)), m='#f4f4f2' if i % 3 else '#1f4a8a')
        key(p, 'location', 1, (x, y, 0.03)); key(p, 'location', c.n, (x + 0.2, y + 0.1, 0.03))
    torus(0.3, 0.08, (0.8, 1.5, 0.05), m='#ff5a3a')
    sun(rot=(0.8, 0.1, 0.6), energy=2.4, color='#e8f0ff')
    cam, t = camera((0, -3, 2.2), (0, 2.5, 0), 30)
    cam_move(cam, t, c, (0, -3.2, 2.4), (0, -2.6, 2.0), (0, 2.5, 0), (0, 2.8, 0))

def forest_set(dusk=False):
    setup_render(sky='#ffb07a' if dusk else '#b8d8e8', sky_strength=0.9)
    floor('#4a5a32', 100)
    box((100, 0.2, 40), (0, 30, 15), m=mat('#ffb07a' if dusk else '#c8dce8', 1.0, emit=1.0))
    if dusk:
        sphere(2.4, (4, 29, 4.5), m=mat('#fff0b0', emit=3))
    rnd = random.Random(27)
    for i in range(18):
        x = rnd.uniform(-8, 8); y = rnd.uniform(3.5, 14)
        if abs(x) < 1.5 and y < 6:
            x += 3 * (1 if x >= 0 else -1)
        pine((x, y, 0), rnd.uniform(1.1, 1.7), rnd.choice(['#1f5a3a', '#2a6a42', '#1a4a32']))

def s27(c):
    forest_set()
    for i in range(4):
        cyl(0.22, 2.2, (-1.6, 1.6 + i * 0.05, 0.22 + i * 0.4 if i < 2 else 0.6), (0, PI / 2, 0.1), m='#8a5a32')
    cyl(0.22, 2.2, (-1.6, 2.1, 0.22), (0, PI / 2, -0.05), m='#7a4e2a')
    d = dexter_lumber(loc=(0.2, 0.6, 0), rot=PI * 0.5)
    d.walk(1, int(c.n * 0.6), (1.8, 0.8, 0), (0.1, 0.6, 0), 1.6)
    key(d.root, 'rotation_euler', 1, (0, 0, -PI * 0.5)); key(d.root, 'rotation_euler', int(c.n * 0.6), (0, 0, -PI * 0.5))
    key(d.root, 'rotation_euler', int(c.n * 0.6) + 10, (0, 0, 0.1))
    d.auto_blink(1, c.n, 42)
    cyl(0.14, 1.1, (0, -0.15, 0.2), (0, PI / 2, 0), m='#8a5a32', parent=d.chest)     # tora no ombro
    d.arm(1, 1, (-2.6, 0, -0.3))
    sun(rot=(0.8, 0.1, 0.6), energy=3.0)
    cam, t = camera((0, -3.4, 1.4), (0.2, 0.6, 1.2), 30)
    cam_move(cam, t, c, (0.8, -3.8, 1.3), (0.2, -2.6, 1.4), (0.8, 0.8, 1.2), (0.1, 0.6, 1.25))

def s28(c):
    setup_render(sky='#2a2a3a', sky_strength=0.5)
    floor('#5a4030', 30)
    box((10, 0.2, 4), (0, 1.6, 2), m=mat('#7a5232', 0.85))
    for i in range(9):
        box((10, 0.22, 0.04), (0, 1.5, 0.3 + i * 0.42), m='#5a3a22')
    window((0.9, 1.48, 1.7), 0, 1.0, 0.9, '#3a4a6a', emit=0.4)
    rnd = random.Random(28)
    for i in range(18):
        x, z = rnd.uniform(0.45, 1.35), rnd.uniform(1.3, 2.1)
        dr = sphere(0.012, (x, 1.43, z), m=mat('#bfe0ff', 0.1, emit=0.8), seg=8)
        key(dr, 'location', 1, (x, 1.43, 2.12), 'LINEAR'); key(dr, 'location', c.n, (x, 1.43, 1.28), 'LINEAR')
    lamp_green((-0.8, 0.9, 0.8))
    table((-0.8, 0.9, 0), (0.6, 0.5), 0.78, '#6a4228', '#4a2e1a')
    d = dexter_lumber(loc=(0, 0.3, 0))
    life(c, d, 43, 0.4)
    d.brows_set(1, 0.3, 1)
    point((-0.8, 0.6, 1.4), 70, '#ffc87a', 0.4)
    point((0.9, 0.8, 1.7), 30, '#7f9fff', 0.5)
    cam, t = camera((0, -1.1, 1.42), (0, 0.3, 1.38), 45)
    cam_move(cam, t, c, (0, -1.3, 1.42), (0, -0.9, 1.4), (0, 0.3, 1.38), (0, 0.3, 1.38))

def s29(c):
    forest_set(dusk=True)
    cyl(0.25, 1.6, (0, 0.6, 0.25), (0, PI / 2, 0), m='#7a4e2a')
    d = dexter_lumber(loc=(0, 0.6, 0.0))
    d.sit(); d.root.location.z = 0.22
    life(c, d, 44, 0.4)
    d.look(1, 0.25, 0)
    d.brows_set(1, 0.35, 1)
    mems = [rita(loc=(-0.9, 1.6, 0), rot=0.2), debra(loc=(0.0, 2.0, 0), rot=0.0), harry(loc=(0.9, 1.6, 0), rot=-0.2)]
    f1 = int(c.n * 0.15)
    for k, m_ in enumerate(mems):
        ghostify(m_)
        life(c, m_, 45 + k, 0.4)
        smile(m_, f1 + 10)
        pop_in(m_.root, f1 + k * 10, 14, 1.0)
        s0 = tuple(m_.root.scale)
        key(m_.root, 'scale', int(c.n * 0.58) + k * 8, (1, 1, 1)); key(m_.root, 'scale', int(c.n * 0.68) + k * 8, (0.001, 0.001, 0.001))
    sun(rot=(1.1, 0.0, 0.4), energy=2.6, color='#ffc49a')
    point((0, -1.0, 2.0), 60, '#ffe0c0', 1.0)
    cam, t = camera((0, -2.6, 1.3), (0, 1.0, 1.2), 32)
    cam_move(cam, t, c, (0, -1.8, 1.1), (0, -3.2, 1.6), (0, 0.8, 1.0), (0, 1.2, 1.4))

SHOTS = {k: v for k, v in globals().items() if k.startswith('s') and k[1:3].isdigit()}
