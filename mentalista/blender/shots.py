# Definicao de cada shot (cenario + personagens + animacao + camera)
import bpy, math, random
from mathutils import Vector
from lib import *
from props import *

BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
PI = math.pi

class Ctx:
    def __init__(self, n, f0, env):
        self.n, self.f0, self.env = n, f0, env
    def g(self, f):           # frame local -> indice global do envelope
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

def cam_move(cam, tgt, c, p0, p1, t0=None, t1=None, lens0=None, lens1=None, fa=1, fb=None):
    fb = fb or c.n
    key(cam, 'location', fa, p0); key(cam, 'location', fb, p1)
    if t0 is not None:
        key(tgt, 'location', fa, t0); key(tgt, 'location', fb, t1 if t1 is not None else t0)
    if lens0 is not None:
        cam.data.lens = lens0; cam.data.keyframe_insert('lens', frame=fa)
        cam.data.lens = lens1 or lens0; cam.data.keyframe_insert('lens', frame=fb)

def room(wall='#7ecbff', wall2=None, fl1='#f6b33c', fl2='#ffd36a', back_y=3.0, side_x=None, w=16, h=7, sq=0.7, trim='#ffffff'):
    checker_floor(fl1, fl2, size=40, scale=sq)
    if wall2:
        stripes_wall(wall, wall2, w=w, h=h, n=int(w / 0.8), loc=(0, back_y, 0), horizontal=False)
    else:
        box((w, 0.2, h), (0, back_y + 0.1, h / 2), m=wall)
    box((w, 0.25, 0.3), (0, back_y - 0.05, 0.15), m=trim)
    if side_x is not None:
        box((0.2, 12, h), (side_x, back_y - 6, h / 2), m=wall)

def tv_set():
    """estudio de TV: listras azuis/roxas, lampadas, palco"""
    checker_floor('#1d3a8a', '#2a52c9', size=40, scale=0.8)
    stripes_wall('#3b5bff', '#6a3bff', w=16, h=8, n=16, loc=(0, 3.2, 0), horizontal=True)
    box((16, 0.3, 0.35), (0, 3.0, 4.2), m='#ff3fa4')
    bulbs_row(-6, 6, 3.9, 2.9, n=17)
    box((16, 0.3, 0.2), (0, 3.0, 3.6), m='#ffffff')
    cyl(2.6, 0.25, (0, 1.0, 0.125), m='#ff4f9a', verts=64)
    cyl(2.4, 0.27, (0, 1.0, 0.13), m='#ffd23f', verts=64)
    # letreiro AO VIVO
    box((1.5, 0.12, 0.5), (0.0, 2.8, 2.7), m='#1a1a1a', bevel=0.05)
    text3d("AO VIVO", (0.0, 2.72, 2.7), size=0.26, m=mat('#ff2a2a', emit=4), font=BOLD, extrude=0.01)

# ======================================================================== SHOTS
def s01(c):
    setup_render(sky='#3b5bff')
    tv_set()
    j = jane(loc=(0, 1.0, 0.25), rot=PI)
    life(c, j, 1)
    # vira de costas -> frente
    key(j.root, 'rotation_euler', 1, (0, 0, PI)); key(j.root, 'rotation_euler', 10, (0, 0, PI))
    key(j.root, 'rotation_euler', 24, (0, 0, 0))
    j.arm(1, 40, (0, 0.5, 0.0)); j.arm(1, 52, (-1.2, 0.6, 0.4))  # acena
    j.arm(1, c.n, (-1.25, 0.65, 0.4))
    talk(c, j, 26)
    sun(rot=(0.9, 0.2, 0.3), energy=3.0)
    point((0, -1.5, 3.0), 400, '#ffd8f0', 1.0)
    cam, t = camera((0, -2.2, 1.75), (0, 1.0, 1.5), 40)
    cam_move(cam, t, c, (0, -2.6, 1.8), (0, -1.6, 1.72), (0, 1.0, 1.45), (0, 1.0, 1.55))

def s02(c):
    setup_render(sky='#ffd1e8')
    room('#ff8fc4', '#ffb3d6', '#8a3fa8', '#a855c8', back_y=3.0)
    box((16, 0.2, 0.25), (0, 2.95, 2.6), m=mat('#ffd23f', 0.3, metal=0.5))
    # mesa de sessao
    table((0, 0.8, 0), (1.6, 1.6), 0.75, '#5a2a7a', '#3a1a4a', round_=True)
    cyl(0.85, 0.02, (0, 0.8, 0.79), m='#ffd23f')
    sphere(0.18, (0, 0.8, 0.98), m=mat('#a8e6ff', 0.05, emit=1.5))
    cyl(0.12, 0.08, (0, 0.8, 0.82), m='#3a1a4a')
    for x in (-0.55, 0.55):
        candle((x, 0.6, 0.79))
    lady = generic_person(11, (0.75, 1.3, 0), rot=-PI * 0.3, female=True, hair='#e6e6e6', hair_style='bun',
                          jacket='#c2185b', skin='#f3d0b0', collar=False)
    sphere(1, (0, -0.12, 0.6), (0.17, 0.03, 0.03), '#ffffff', lady.chest)  # colar de perolas
    j = jane(loc=(-0.65, 1.3, 0), rot=PI * 0.3)
    for ch in (j, lady):
        ch.sit()
    chair((-0.65, 1.4, 0), PI * 0.3, '#ffd23f'); chair((0.75, 1.4, 0), -PI * 0.3, '#ffd23f')
    j.root.location = (-0.65, 1.3, 0.0); lady.root.location = (0.75, 1.3, 0.0)
    life(c, j, 2); life(c, lady, 3)
    # maos nas temporas
    j.arm(0, 12, (-2.3, 0.0, -0.5)); j.arm(1, 12, (-2.3, 0.0, 0.5))
    j.arm(0, 70, (-2.3, 0.0, -0.5)); j.arm(1, 70, (-2.3, 0.0, 0.5))
    j.arm(0, 84, (-1.2, 0.2, 0)); j.arm(1, 84, (-1.2, -0.2, 0))
    j.brows_set(10, 0.25)
    lady.look(30, 0.1, 0); lady.brows_set(30, -0.25)
    # dinheiro surgindo
    for i, (x, y) in enumerate([(-0.3, 0.45), (0.0, 0.42), (0.3, 0.45), (-0.15, 0.6), (0.15, 0.6)]):
        m = money_stack((x, y, 0.8), n=3 + i % 3)
        pop_in(m, int(c.n * 0.62) + i * 5, 8)
    sun(rot=(0.8, 0.1, 0.9), energy=2.5)
    point((0, 0.8, 1.6), 120, '#9fe3ff', 0.5)
    cam, t = camera((0, -2.0, 2.0), (0, 0.9, 1.0), 32)
    cam_move(cam, t, c, (0.35, -2.2, 1.75), (-0.1, -1.7, 1.6), (0, 1.0, 1.15), (0, 0.95, 1.1))

def s03(c):
    setup_render(sky='#ffe066')
    room('#ffcf3f', '#ffe27a', '#ff8a3d', '#ffa866', back_y=1.6)
    j = jane(loc=(0, 0, 0))
    life(c, j, 4, 0.6)
    # olhar para os lados, desconfiado, depois sorriso/piscadela
    j.look(20, 0, 0.0); j.look(34, 0, 0.35); j.look(60, 0, 0.35); j.look(74, 0, -0.35); j.look(100, 0, -0.35); j.look(114, 0, 0)
    j.brows_set(30, -0.22); j.brows_set(110, -0.12)
    # piscadela (olho direito)
    e = j.eyes[1]; f = int(c.n * 0.82)
    key(e, 'scale', f - 3, (1, 1, 1)); key(e, 'scale', f, (1, 1, 0.08)); key(e, 'scale', f + 10, (1, 1, 0.08)); key(e, 'scale', f + 14, (1, 1, 1))
    key(j.mouth, 'scale', f - 6, (1, 1, 0.35)); key(j.mouth, 'scale', f, (1.4, 1, 0.6))
    key(j.mouth, 'rotation_euler', f - 6, (0.3, 0, 0)); key(j.mouth, 'rotation_euler', f, (0.3, 0, 0.18))
    sun(rot=(0.8, 0.0, 0.5), energy=3.5)
    cam, t = camera((0, -1.0, 1.42), (0, 0, 1.36), 50)
    cam_move(cam, t, c, (0, -1.25, 1.42), (0, -0.95, 1.40), (0, 0, 1.36), (0, 0, 1.36))

def s03b(c):
    setup_render(sky='#bde6ff')
    room('#53c6ff', '#8bdcff', '#e9e4ff', '#d4ccff', back_y=2.5)
    sus = generic_person(21, (0, 0.6, 0), jacket='#ff7043', hair_style='short', hair='#4a3020', female=False, collar=False)
    life(c, sus, 5, 0.5)
    # alianca na mao (bracos levemente para frente)
    sus.arms[0].rotation_euler = (-1.25, 0.0, -0.35)
    torus(0.05, 0.016, (0, 0, -0.43), (0, PI / 2, 0), m=mat('#ffd23f', 0.15, metal=1.0, emit=0.3), parent=sus.arms[0])
    bpy.context.view_layer.update()
    hp = sus.arms[0].matrix_world @ Vector((0, 0, -0.44))
    # sapato gasto: remendo
    sphere(1, (0.03, -0.12, -sus.leg_len + 0.05), (0.035, 0.02, 0.03), '#b0a090', sus.legs[1])
    # suor
    drop = sphere(1, (0.17, -0.24, 0.16), (0.02, 0.02, 0.03), mat('#7fd4ff', 0.05), sus.head)
    f3 = int(c.n * 0.5)
    key(drop, 'location', f3, (0.17, -0.24, 0.16)); key(drop, 'location', c.n, (0.18, -0.25, -0.02))
    sus.look(f3, 0, 0.0); sus.look(f3 + 10, 0, 0.25); sus.look(f3 + 22, 0, -0.25); sus.look(f3 + 34, 0, 0.2)
    sus.brows_set(f3, 0.35)
    sun(rot=(0.8, 0.0, 0.5), energy=3.2)
    cam, t = camera((0, -1, 1), (0, 0, 1), 50)
    hand = sus.arms[0].matrix_world  # nao usado; posicoes aproximadas abaixo
    f1, f2 = int(c.n * 0.26), int(c.n * 0.5)
    hx, hy, hz = hp
    # 1) mao com alianca
    key(cam, 'location', 1, (hx - 0.15, hy - 0.75, hz + 0.08)); key(t, 'location', 1, (hx, hy, hz))
    key(cam, 'location', f1 - 4, (hx - 0.08, hy - 0.55, hz + 0.05)); key(t, 'location', f1 - 4, (hx, hy, hz))
    # 2) sapato
    key(cam, 'location', f1 + 4, (0.25, -0.4, 0.3)); key(t, 'location', f1 + 4, (0.09, 0.5, 0.06))
    key(cam, 'location', f2 - 6, (0.2, -0.3, 0.28)); key(t, 'location', f2 - 6, (0.09, 0.5, 0.06))
    # 3) rosto nervoso -> recua
    key(cam, 'location', f2 + 4, (0, -0.55, 1.42)); key(t, 'location', f2 + 4, (0, 0.6, 1.38))
    key(cam, 'location', c.n, (0, -1.1, 1.38)); key(t, 'location', c.n, (0, 0.6, 1.3))
    cam.data.lens = 45

def s04(c):
    setup_render(sky='#3b5bff')
    tv_set()
    armchair((-0.7, 1.0, 0.25), PI * 0.18, '#ffffff'); armchair((0.7, 1.0, 0.25), -PI * 0.18, '#ffffff')
    host = generic_person(31, (0.7, 1.05, 0.25), rot=-PI * 0.18, female=False, jacket='#2d2d34', hair='#222222', hair_style='short', collar=True, vest=None, tie='#d32f2f')
    j = jane(loc=(-0.7, 1.05, 0.25), rot=PI * 0.18)
    for ch in (j, host):
        ch.sit(); ch.root.location.z = 0.25 + 0.12
    life(c, j, 6); life(c, host, 7)
    talk(c, j, 1)
    host.look(10, 0, -0.4); host.brows_set(20, -0.25)
    # Jane gesticula
    for k, f in enumerate(range(10, c.n, 22)):
        j.arm(1, f, (-1.0 - 0.3 * (k % 2), 0.4, 0.3))
    j.brows_set(20, -0.2)
    tv_camera((1.9, -1.0, 0), PI * 0.2)
    sun(rot=(0.9, 0.2, 0.3), energy=3.0)
    point((0, -1, 3.2), 350, '#ffe0f5', 1.0)
    cam, t = camera((0, -2.2, 1.6), (0, 1.0, 1.35), 32)
    cam_move(cam, t, c, (-0.3, -2.4, 1.65), (0.1, -1.9, 1.55), (0, 1.0, 1.4), (-0.1, 1.0, 1.4))

def s05(c):
    setup_render(sky='#6a3bff')
    tv_set()
    j = jane(loc=(-0.7, 1.05, 0.25), rot=PI * 0.05)
    j.sit(); j.root.location.z = 0.37
    armchair((-0.7, 1.0, 0.25), PI * 0.05, '#ffffff')
    life(c, j, 8)
    talk(c, j, 1, gain=1.2)
    j.brows_set(6, -0.3)
    j.arm(1, 10, (-1.4, 0.5, 0.5)); j.arm(1, 30, (-1.6, 0.5, 0.2)); j.arm(1, 50, (-1.4, 0.5, 0.5)); j.arm(1, 70, (-1.6, 0.5, 0.2))
    sun(rot=(0.9, 0.2, 0.3), energy=3.0)
    point((-0.7, -1, 2.5), 250, '#ffd0ff', 0.8)
    cam, t = camera((-0.7, -0.4, 1.5), (-0.7, 1.05, 1.4), 50)
    cam_move(cam, t, c, (-0.75, -0.6, 1.5), (-0.7, -0.15, 1.5), (-0.7, 1.05, 1.36), (-0.7, 1.05, 1.42))

def night_world(sky='#0d1b3d', amb=0.35):
    setup_render(sky=sky, sky_strength=amb)

def s06(c):
    night_world('#13235a', 0.35)
    floor('#1f5a3a', 80)
    house_ext((0, 4, 0), night=True)
    box((80, 0.2, 30), (0, 30, 15), m=mat('#152a6a', 0.9))
    sphere(1.2, (-4, 25, 11), m=mat('#fff6d0', emit=3))
    rnd = random.Random(1)
    for i in range(40):
        sphere(0.06, (rnd.uniform(-20, 20), 29, rnd.uniform(6, 22)), m=mat('#ffffff', emit=4), seg=8)
    for x in (-5, 5.5):
        tree((x, 3, 0), 1.3, '#1f7a3f', seed=int(x))
    j = jane(loc=(-1.2, -2.5, 0), rot=PI)
    j.walk(1, c.n, (-1.2, -2.6, 0), (-1.2, 0.9, 0), steps_per_sec=1.8)
    j.auto_blink(1, c.n, 2)
    sun(rot=(0.9, 0.3, -0.8), energy=0.7, color='#8fb0ff')
    point((-1.2, 1.4, 2.6), 220, '#ffd27a', 0.5)
    cam, t = camera((1.5, -6.5, 1.6), (-1.0, 0.5, 1.4), 32)
    cam_move(cam, t, c, (1.8, -7.0, 1.5), (0.8, -5.0, 1.7), (-1.1, -1.5, 1.3), (-1.2, 1.5, 1.6))

def s07(c):
    night_world('#120a1a', 0.18)
    floor('#3a2a2a', 40)
    # corredor: parede com porta + parede com o rosto
    box((12, 0.2, 4), (0, 2.1, 2), m=mat('#e8dcc8', 0.8))
    door((-1.6, 2.0, 0), 0, '#5a3a24')
    paper = box((0.24, 0.01, 0.3), (-1.6, 1.9, 1.5), m='#ffffff', rot=(0, 0, 0))
    text3d("Sr. Jane...", (-1.6, 1.885, 1.55), size=0.035, m='#c0141c', font=BOLD, extrude=0.001, bevel=0)
    for z in (1.47, 1.43, 1.39, 1.35):
        box((0.16, 0.002, 0.008), (-1.6, 1.885, z), m='#555555')
    sm = smiley((1.3, 1.98, 1.9), size=0.75, rot=(PI / 2, 0, 0), color='#b5121b')
    # luz
    point((-1.6, 0.3, 2.4), 60, '#ffe2b0', 0.4)
    lred = point((1.3, 0.4, 2.0), 0, '#ff3a3a', 0.6)
    f1 = int(c.n * 0.45)
    lred.data.energy = 0; lred.data.keyframe_insert('energy', frame=f1)
    lred.data.energy = 90; lred.data.keyframe_insert('energy', frame=f1 + 14)
    cam, t = camera((-1.6, -0.6, 1.5), (-1.6, 2.0, 1.45), 45)
    key(cam, 'location', 1, (-1.6, 0.6, 1.5)); key(t, 'location', 1, (-1.6, 2.0, 1.48))
    key(cam, 'location', f1 - 6, (-1.6, 1.1, 1.5)); key(t, 'location', f1 - 6, (-1.6, 2.0, 1.48))
    key(cam, 'location', f1 + 16, (0.9, -0.3, 1.7)); key(t, 'location', f1 + 16, (1.3, 2.0, 1.85))
    key(cam, 'location', c.n, (1.15, 0.2, 1.8)); key(t, 'location', c.n, (1.3, 2.0, 1.9))

def s08(c):
    night_world('#1a1030', 0.25)
    floor('#2a2040', 40)
    box((12, 0.2, 5), (0, 2.6, 2.5), m=mat('#3a2e55', 0.9))
    table((0, 0.9, 0), (1.2, 0.6), 0.8, '#6b4a2a', '#4a3020')
    ph = frame_photo((0, 0.95, 1.12), rot=(-0.12, 0, 0), w=0.62, h=0.5, bg='#9fd0f0')
    # mini familia dentro da foto
    w = Char(name='wife', hair='#5a3420', hair_style='long', eyes='#5a4a3a', jacket='#e57399', vest=None, shirt='#ffffff', female=True, collar=False, body_w=0.9)
    d = Char(name='kid', hair='#e2b04a', hair_style='child', eyes='#3f8ed8', jacket='#ffd23f', vest=None, female=True, collar=False, height=0.7, body_w=0.75)
    for ch, x in ((w, -0.08), (d, 0.09)):
        ch.root.parent = ph; ch.root.location = (x, -0.04, -0.22); ch.root.scale = (0.2, 0.2, 0.2)
        ch.mouth.scale = (1.2, 1, 0.5)
    d.root.scale = (0.17, 0.17, 0.17)
    # vidro rachado (linhas)
    f1 = int(c.n * 0.35)
    cracks = empty("cracks", (0.05, 0.9, 1.16), rot=(-0.12, 0, 0))
    rnd = random.Random(2)
    for i in range(7):
        a = rnd.uniform(0, 2 * PI); L = rnd.uniform(0.12, 0.26)
        b = box((L, 0.004, 0.006), (math.cos(a) * L / 2, 0, math.sin(a) * L / 2), rot=(0, -a, 0), m=mat('#ffffff', emit=2), parent=cracks)
    hide_between(cracks, f1, None)
    cracks.scale = (1, 1, 1)
    # Jane ajoelhado (de costas p/ camera, lado)
    j = jane(loc=(0.55, 0.15, 0), rot=-PI * 0.68)
    j.kneel()
    j.look(10, 0.4, 0); j.arm(0, 20, (-0.3, 0, 0)); j.arm(1, 20, (-0.3, 0, 0))
    life(c, j, 9, 0.4)
    j.brows_set(5, 0.4)
    point((0, 0.2, 2.0), 90, '#ffd8b0', 0.4)
    point((-1.5, -1, 2.2), 50, '#7f8cff', 1)
    cam, t = camera((0, -0.4, 1.2), (0, 0.95, 1.12), 50)
    keys(cam.data, 'lens', [(f1 + 30, 50), (c.n, 32)])
    cam_move(cam, t, c, (0.05, 0.0, 1.18), (-0.05, 0.25, 1.15), (0, 0.95, 1.12), (0, 0.95, 1.12))
    key(cam, 'location', f1 + 30, (-0.05, 0.25, 1.15))
    key(cam, 'location', c.n, (-0.9, 1.0, 1.35)); key(t, 'location', f1 + 30, (0, 0.95, 1.12)); key(t, 'location', c.n, (0.5, 0.15, 0.88))

def s09(c):
    setup_render(sky='#d8fff4', sky_strength=0.9)
    room('#bff3e6', None, '#e8f7f3', '#d3efe8', back_y=2.0, side_x=-2.2)
    window((0.6, 1.95, 1.9), 0, 1.2, 1.0, '#ffffff', bars=True, emit=2.0)
    bed((-1.0, 0.8, 0), PI / 2)
    j = jane(loc=(-0.9, 0.3, 0.2), rot=0, jacket='#f2f2f2', vest=None, shirt='#f2f2f2', pants='#f2f2f2', shoes='#cfcfcf')
    j.sit(); j.root.location = (-0.9, 0.3, 0.26)
    j.look(1, 0.45, 0); j.arm(0, 1, (-0.6, 0.1, 0)); j.arm(1, 1, (-0.6, -0.1, 0))
    life(c, j, 10, 0.4); j.brows_set(1, 0.45, 1)
    sun(rot=(0.8, 0.1, 0.4), energy=3.4)
    cam, t = camera((0.6, -2.3, 1.5), (-0.7, 0.5, 0.9), 35)
    cam_move(cam, t, c, (0.9, -2.6, 1.6), (0.3, -1.9, 1.4), (-0.7, 0.5, 0.95), (-0.85, 0.4, 1.0))

def s10(c):
    setup_render(sky='#ff3b3b')
    floor('#2a0a0a', 60)
    tri_bg(['#d81b1b', '#7a0a0a'], loc=(0, 4, -1), n=10, w=18, h=10)
    smiley((0, 3.8, 3.4), size=1.25, rot=(PI / 2, 0, 0), color='#ff4a4a', drips=True, emit=1.0)
    j = jane(loc=(0, 0, 0))
    life(c, j, 11, 0.4)
    j.brows_set(5, -0.5)
    f1 = int(c.n * 0.55)
    j.arm(1, f1, (-0.5, 0.1, 0)); j.arm(1, f1 + 10, (-2.2, 0.3, 0.2))  # punho erguido
    sphere(0.075, (0, 0, -0.45), m=SKIN, parent=j.arms[1])
    sun(rot=(0.7, 0.0, -2.6), energy=4.0, color='#ffb0a0')
    point((0, -1.2, 1.8), 200, '#ffd0c0', 0.6)
    cam, t = camera((0, -2.5, 1.0), (0, 0, 1.2), 35)
    cam_move(cam, t, c, (0, -4.2, 0.8), (0, -2.4, 1.0), (0, 0, 1.6), (0, 0, 1.45))

def cbi_office(extra=True):
    setup_render(sky='#bde6ff')
    room('#7ec8ff', '#a3d8ff', '#e8e8f0', '#d6d6e4', back_y=3.0, side_x=-3.5, sq=0.8)
    text3d("CBI", (0, 2.86, 2.75), size=0.6, m=mat('#1a3a7a', 0.3), font=BOLD, extrude=0.06)
    box((1.9, 0.06, 0.06), (0, 2.85, 2.35), m='#ffd23f')
    for x in (-2.3, 2.3):
        window((x, 2.85, 2.0), 0, 1.3, 1.1, '#e8f8ff', emit=1.2)
    if extra:
        desk_pc((1.6, 1.3, 0), PI)
        desk_pc((-1.6, 1.3, 0), PI)
        couch((0, 2.3, 0), 0, '#8a5530', 2.0)

def s11(c):
    cbi_office()
    j = jane(loc=(-0.6, -1.5, 0))
    j.walk(1, int(c.n * 0.65), (-1.6, -1.6, 0), (0.0, 0.6, 0), 1.8)
    key(j.root, 'rotation_euler', 1, (0, 0, -0.6)); key(j.root, 'rotation_euler', int(c.n * 0.6), (0, 0, -0.6)); key(j.root, 'rotation_euler', int(c.n * 0.75), (0, 0, 0))
    j.auto_blink(1, c.n, 3)
    j.arm(0, int(c.n * 0.8), (0, -0.45, 0)); j.arm(1, int(c.n * 0.8), (0, 0.45, 0))
    j.brows_set(int(c.n * 0.8), -0.1)
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -4, 1.6), (0, 0, 1.2), 30)
    cam_move(cam, t, c, (0.6, -4.2, 1.7), (0.2, -2.6, 1.55), (-0.8, -0.8, 1.2), (0.0, 0.6, 1.3))

def s12(c):
    cbi_office()
    L = lisbon(loc=(0.15, 0.2, 0))
    life(c, L, 12)
    # maos na cintura
    L.arm(0, 6, (-1.15, 0, 0.75)); L.arm(1, 6, (-1.25, 0, -0.75))
    L.brows_set(6, -0.45)
    L.mouth.scale = (1, 1, 0.3)
    # Jane ao fundo derrubando papeis
    j = jane(loc=(-1.0, 1.3, 0), rot=-0.3)
    life(c, j, 13)
    papers = []
    for i in range(6):
        p = box((0.22, 0.3, 0.01), (-1.4 + i * 0.05, 1.05, 0.8 + i * 0.012), m='#ffffff')
        papers.append(p)
    f1 = int(c.n * 0.4)
    rnd = random.Random(4)
    for i, p in enumerate(papers):
        p0 = tuple(p.location)
        key(p, 'location', f1, p0)
        key(p, 'location', f1 + 25 + i * 2, (p0[0] + rnd.uniform(-0.5, 0.5), p0[1] - rnd.uniform(0.3, 0.9), 0.01 + i * 0.002))
        key(p, 'rotation_euler', f1, (0, 0, 0)); key(p, 'rotation_euler', f1 + 25, (rnd.uniform(-0.2, 0.2), 0, rnd.uniform(-2, 2)))
    j.arm(1, f1 - 6, (-0.9, 0.2, 0.6)); j.arm(1, f1 + 4, (-0.5, 0.2, -0.3))
    L.look(f1 + 10, 0, -0.5); L.look(c.n, 0, -0.5)
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2, 1.4), (0, 0, 1.2), 40)
    cam_move(cam, t, c, (0.6, -2.3, 1.45), (0.3, -1.6, 1.4), (0.0, 0.2, 1.25), (-0.1, 0.3, 1.25))

def s12b(c):
    cbi_office(extra=False)
    L = lisbon(loc=(0.4, 0.2, 0), rot=-PI * 0.36)
    j = jane(loc=(-0.4, 0.2, 0), rot=PI * 0.36)
    life(c, L, 14); life(c, j, 15)
    talk(c, j, 1, int(c.n * 0.45))
    L.brows_set(5, -0.35)
    # Lisbon cruza os bracos e depois sorri
    L.arm(0, 8, (-1.15, 0, 0.75)); L.arm(1, 8, (-1.25, 0, -0.75))
    f1 = int(c.n * 0.55)
    L.look(f1 - 10, 0.0, 0.0); L.look(f1, -0.25, -0.5)  # revira/olha pro lado
    L.look(f1 + 25, 0.0, 0.0)
    L.brows_set(f1 + 25, 0.15)
    key(L.mouth, 'scale', f1 + 18, (1, 1, 0.3)); key(L.mouth, 'scale', f1 + 30, (1.5, 1, 0.55))
    L.arm(0, f1 + 25, (0, -0.12, 0)); L.arm(1, f1 + 25, (0, 0.12, 0))
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2.2, 1.45), (0, 0.2, 1.3), 40)
    cam_move(cam, t, c, (0, -3.0, 1.45), (0, -2.4, 1.42), (0, 0.2, 1.3), (0, 0.2, 1.32))

def s13(c):
    cbi_office(extra=False)
    team = [vanpelt(loc=(-0.78, 0.75, 0)), cho(loc=(-0.42, 0.38, 0)), lisbon(loc=(0, 0.0, 0)), jane(loc=(0.42, 0.38, 0)), rigsby(loc=(0.8, 0.75, 0))]
    for i, ch in enumerate(team):
        life(c, ch, 20 + i)
        x = ch.root.location.x
        ch.root.rotation_euler = (0, 0, x * 0.25)
        pop_in(ch.root, 1 + i * 5, 8, 1.08)
    team[1].brows_set(4, -0.2)
    key(team[3].mouth, 'scale', 20, (1.4, 1, 0.55))
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2.4, 1.3), (0, 0.4, 1.15), 28)
    cam_move(cam, t, c, (0, -2.6, 1.15), (0, -2.15, 1.3), (0, 0.4, 1.15), (0, 0.4, 1.2))

def s14(c):
    setup_render(sky='#9fa8c8')
    room('#8f9bc4', '#a4aed4', '#5a6488', '#68739a', back_y=2.2, side_x=-2.5)
    box((2.6, 0.05, 1.0), (0.8, 2.08, 1.7), m=mat('#1a1f2e', 0.05))  # espelho
    table((0, 0.8, 0), (1.4, 0.8), 0.75, '#c9ccd6', '#666a7a')
    sus = generic_person(41, (0.3, 1.25, 0), rot=0, jacket='#ff9800', pants='#ff9800', collar=False)
    sus.sit(); chair((0.3, 1.3, 0), 0, '#555b6e')
    j = jane(loc=(-0.75, 0.75, 0), rot=PI * 0.62)
    life(c, sus, 42); life(c, j, 43)
    # relogio de bolso pendurado (hipnose)
    j.arm(1, 1, (-1.9, 0.0, 0.0))
    comp = empty("comp", (0, 0, -0.47), j.arms[1], rot=(1.9, 0, 0))   # compensa o braco: corrente pende p/ baixo
    orient = empty("orient", (0, 0, 0), comp, rot=(0, 0, -PI * 0.62))  # anula a rotacao do Jane
    piv = empty("piv", (0, 0, 0), orient)
    cyl(0.005, 0.24, (0, 0, -0.12), m=mat('#ffd23f', 0.2, metal=1), parent=piv)
    w = cyl(0.065, 0.022, (0, 0, -0.29), (PI / 2, 0, 0), m=mat('#ffd23f', 0.15, metal=1), parent=piv)
    cyl(0.053, 0.026, (0, 0, -0.29), (PI / 2, 0, 0), m='#ffffff', parent=piv)
    f1 = int(c.n * 0.55)
    for f in range(1, f1, 2):
        piv.rotation_euler = (0, 0.55 * math.sin(f / 9.0), 0); piv.keyframe_insert('rotation_euler', frame=f)
    j.arm(1, f1 + 6, (-0.1, 0.12, 0))
    # olhos do suspeito acompanham o relogio
    for f in range(1, f1, 4):
        sus.neck.rotation_euler = (0, 0, -0.35 - 0.2 * math.sin(f / 9.0)); sus.neck.keyframe_insert('rotation_euler', frame=f)
    for e in sus.eyes:
        key(e, 'scale', 1, (1, 1, 0.55)); key(e, 'scale', f1, (1, 1, 0.55)); key(e, 'scale', f1 + 6, (1, 1, 1))
    # Lisbon irritada na porta (fim)
    L = lisbon(loc=(-1.25, -0.2, 0), rot=PI * 0.15)
    life(c, L, 44); L.brows_set(f1, -0.4)
    L.arm(0, f1 + 10, (-1.15, 0, 0.75)); L.arm(1, f1 + 10, (-1.25, 0, -0.75))
    sun(rot=(0.8, 0.2, 0.3), energy=2.6)
    point((0, 0.8, 2.4), 150, '#ffffff', 0.4)
    cam, t = camera((0, -1.5, 1.6), (0, 0.8, 1.1), 35)
    key(cam, 'location', 1, (0.5, -1.4, 1.45)); key(t, 'location', 1, (-0.15, 1.0, 1.15))
    key(cam, 'location', f1, (0.35, -0.9, 1.4)); key(t, 'location', f1, (-0.15, 1.0, 1.15))
    key(cam, 'location', f1 + 12, (0.3, -2.9, 1.6)); key(t, 'location', f1 + 12, (-0.45, 0.5, 1.1))
    key(cam, 'location', c.n, (0.2, -2.6, 1.6)); key(t, 'location', c.n, (-0.5, 0.45, 1.15))

def s15(c):
    cbi_office(extra=False)
    desk_pc((1.9, 1.0, 0), PI * 1.1)
    couch((0, 1.8, 0), 0, '#8a5530', 2.4)
    j = jane(loc=(0, 1.75, 0.62), rot=0)
    j.root.rotation_euler = (0, -PI / 2, 0)  # deitado
    j.root.location = (-0.85, 1.72, 0.85)
    j.root.rotation_euler = (0, PI / 2 * 0.95, 0)
    # olhos fechados
    for e in j.eyes:
        e.scale = (1, 1, 0.1)
    j.arm(1, 1, (-0.4, -0.2, -0.6))
    tea = teacup((0, 0, -0.5), 1.0, parent=j.arms[1])
    tea.rotation_euler = (0, -PI / 2 * 0.95, 0)
    # respiracao
    for f in range(1, c.n + 1, 12):
        j.chest.scale = (1, 1 + 0.03 * (f // 12 % 2), 1); j.chest.keyframe_insert('scale', frame=f)
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -1.6, 1.4), (0, 1.7, 0.85), 35)
    cam_move(cam, t, c, (0.5, -0.9, 1.5), (0.35, -0.3, 1.3), (0.1, 1.7, 0.9), (0.2, 1.7, 0.95))

def s16(c):
    night_world('#0a0f24', 0.15)
    floor('#3a3530', 30)
    box((10, 0.2, 4), (0, 2.0, 2), m=mat('#e8dcc8', 0.85))
    box((0.2, 10, 4), (-2.4, -2, 2), m=mat('#d8ccb8', 0.85))
    smiley((0.2, 1.88, 2.35), size=0.6, rot=(PI / 2, 0, 0), color='#b5121b')
    window((-2.28, 0.0, 2.0), PI / 2, 1.0, 1.2, '#5d7bd6', emit=1.2)
    mattress((0.2, 0.9, 0), PI / 2)
    j = jane(loc=(0.2, 0.9, 0.24), rot=0)
    j.root.rotation_euler = (-PI / 2, 0, 0)
    j.root.location = (0.2, -0.02, 0.33)
    j.auto_blink(1, c.n, 5)
    j.look(1, 0, 0); j.neck.rotation_euler = (0, 0, 0)
    j.arm(0, 1, (0, 0, 0)); j.arm(1, 1, (0, 0, 0))
    moon = sun(rot=(1.0, 0.0, -1.2), energy=1.6, color='#9fb4ff')
    point((0.2, 0.6, 3.0), 45, '#ff5050', 0.4)
    point((1.2, -0.5, 1.8), 40, '#c0d0ff', 0.6)
    cam, t = camera((0.2, -2.5, 2.0), (0.2, 1.4, 1.2), 30)
    cam_move(cam, t, c, (1.5, -0.9, 2.4), (1.1, -0.5, 2.1), (0.2, 0.8, 0.35), (0.2, 1.3, 1.3))

def s16b(c):
    setup_render(sky='#2a3355', sky_strength=0.6)
    floor('#e8e2d4', 20)
    box((10, 0.2, 4), (0, 1.2, 2), m=mat('#2a3355', 0.9))
    # mao grande com alianca (palma + dedos em capsulas)
    box((0.5, 0.2, 0.42), (0, 0, 0.32), m=SKIN, bevel=0.09, seg=6)
    for i, (x, L) in enumerate([(-0.17, 0.32), (-0.057, 0.38), (0.057, 0.36), (0.17, 0.28)]):
        sphere(1, (x, 0, 0.47 + L / 2), (0.056, 0.056, L / 2 + 0.05), SKIN, rot=(0, x * 0.4, 0))
    sphere(1, (-0.3, -0.02, 0.38), (0.055, 0.055, 0.16), SKIN, rot=(0, 0.75, 0))
    ring = torus(0.066, 0.02, (0.058, 0, 0.6), (0, 0.023, 0), m=mat('#ffd23f', 0.1, metal=1.0, emit=0.25))
    cyl(0.27, 1.0, (0, 0, -0.42), m='#545a66', scale=(1, 0.55, 1))
    cyl(0.275, 0.07, (0, 0, 0.1), m='#f5f3ea', scale=(1, 0.55, 1))
    sun(rot=(0.6, 0.2, 0.6), energy=4.0)
    pl = point((0.6, -0.6, 1.2), 0, '#ffffff', 0.1)
    keys(pl.data, 'energy', [(1, 10), (int(c.n * 0.5), 120), (c.n, 30)])
    cam, t = camera((0.1, -1.6, 0.8), (0.1, 0, 0.5), 50)
    cam_move(cam, t, c, (0.25, -1.9, 0.62), (0.12, -1.3, 0.62), (0.0, 0, 0.48), (0.05, 0, 0.56))

def s17(c):
    setup_render(sky='#1a1a24', sky_strength=0.5)
    floor('#2a2a33', 30)
    box((10, 0.2, 5), (0, 1.0, 2.5), m='#3a3a48')
    corkboard((0, 0.85, 1.8), 3.4, 2.2)
    sm = smiley((0, 0.8, 1.85), 0.32, (PI / 2, 0, 0), '#c0141c', drips=False)
    pos = [(-1.2, 2.5), (-0.5, 2.6), (0.6, 2.55), (1.25, 2.45), (-1.3, 1.25), (1.3, 1.2), (-0.6, 1.05), (0.65, 1.05)]
    cards = []
    for i, (x, z) in enumerate(pos):
        cd = card((x, 0.78, z), bg='#fffdf2', who=['#2d2d34', '#5a3a2a', '#1a3a7a', '#3a5a2a'][i % 4])
        cards.append(cd)
        pop_in(cd, 4 + i * 4, 8)
    # fios vermelhos ate o centro
    for i, (x, z) in enumerate(pos):
        o = curve_path([(x, 0.76, z + 0.22), ((x + 0) * 0.5, 0.755, (z + 1.85) * 0.5 + 0.05), (0, 0.75, 1.85)], bevel=0.007, m=mat('#e53935', 0.4, emit=0.3))
        pop_in(o, 40 + i * 3, 6, 1.0)
    # olho / "?" sobre cards
    f1 = int(c.n * 0.6)
    for i, cd in enumerate(cards):
        q = text3d("?", (0, -0.03, -0.03), size=0.28, m=mat('#ffd23f', emit=1.5), font=BOLD, parent=cd)
        pop_in(q, f1 + i * 2, 6)
    point((0, -0.8, 2.6), 160, '#ffe9c0', 0.6)
    point((0, 0.3, 1.8), 25, '#ff3a3a', 0.3)
    cam, t = camera((0, -1.0, 1.85), (0, 0.8, 1.85), 40)
    cam_move(cam, t, c, (0, -0.4, 1.85), (0, -2.6, 1.85), (0, 0.8, 1.85), (0, 0.8, 1.85))

def s18(c):
    setup_render(sky='#ffe0a8')
    checker_floor('#ffffff', '#ffd9e6', size=40, scale=0.8)
    box((16, 0.2, 7), (0, 4.6, 3.5), m='#ffcf7a')
    stall((-2.2, 3.8, 0), '#ff5a5a', 'PIZZA'); stall((0.2, 3.8, 0), '#2aa4f4', 'TACOS'); stall((2.6, 3.8, 0), '#5cc66b', 'SUCOS')
    rnd = random.Random(8)
    for i, (x, y) in enumerate([(-2.0, 1.8), (1.9, 1.9), (-1.6, -0.2), (2.0, 0.0)]):
        table((x, y, 0), (0.9, 0.9), 0.72, '#ffffff', '#cccccc', round_=True)
        p = generic_person(60 + i, (x + 0.35, y + 0.35, 0), rot=PI * 0.75)
        p.sit(); life(c, p, 60 + i)
    for i, (x, y) in enumerate([(-0.9, 2.6), (1.0, 2.8), (-2.8, 1.0), (3.0, 1.2)]):
        p = generic_person(70 + i, (x, y, 0), rot=rnd.uniform(-0.6, 0.6))
        life(c, p, 70 + i)
    # mesa de Jane
    table((0, 0.6, 0), (0.9, 0.9), 0.72, '#ffffff', '#cccccc', round_=True)
    teacup((-0.2, 0.5, 0.75), 0.9)
    carter = generic_person(80, (0.5, 0.65, 0), rot=-PI * 0.4, jacket='#795548', hair='#2a1a10', hair_style='short', female=False)
    carter.sit(); life(c, carter, 80)
    talk(c, carter, 1, int(c.n * 0.6), 0.8)
    j = jane(loc=(-0.5, 0.6, 0), rot=PI * 0.4)
    j.sit(); life(c, j, 81)
    chair((-0.58, 0.61, 0), PI * 0.4, '#ff7eb6'); chair((0.58, 0.67, 0), -PI * 0.4, '#ff7eb6')
    j.brows_set(10, -0.4)
    f1 = int(c.n * 0.68)
    j.arm(1, f1 - 6, (-0.4, 0, 0))
    j.arm(1, f1, (-1.5, 0.0, 0.25))
    gun = box((0.04, 0.16, 0.08), (0, -0.08, -0.47), m='#222222', parent=j.arms[1], bevel=0.01)
    box((0.035, 0.05, 0.11), (0, 0.02, -0.53), m='#5a3a24', parent=j.arms[1], bevel=0.01)
    hide_between(gun, f1 - 6, None)
    fl = sphere(0.12, (0, -0.3, -0.47), m=mat('#fff3a0', emit=12), parent=j.arms[1])
    fl.scale = (1, 1, 1)
    hide_between(fl, f1 + 6, f1 + 9)
    flash = point((0, 0.6, 1.2), 0, '#fff0b0', 0.2)
    keys(flash.data, 'energy', [(f1 + 5, 0), (f1 + 6, 1500), (f1 + 10, 0)], 'LINEAR')
    for ch in [carter]:
        ch.brows_set(f1 + 8, 0.5)
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -2.5, 2.0), (0, 0.8, 1.0), 30)
    key(cam, 'location', 1, (0.6, -3.6, 2.6)); key(t, 'location', 1, (0, 1.4, 1.1))
    key(cam, 'location', f1 - 4, (0.1, -2.0, 1.6)); key(t, 'location', f1 - 4, (0, 0.6, 1.15))
    key(cam, 'location', f1 + 6, (-0.1, -1.6, 1.5)); key(t, 'location', f1 + 6, (-0.15, 0.6, 1.15))
    key(cam, 'location', c.n, (-0.15, -1.45, 1.5))

def s19(c):
    setup_render(sky='#d7b98a')
    room('#c79a5f', '#b5884f', '#8a5a32', '#7a4e2a', back_y=3.2, sq=0.9)
    box((2.4, 0.9, 1.3), (0, 2.4, 0.65), m=mat('#6b3a1a', 0.4), bevel=0.04)  # bancada do juiz
    box((2.6, 1.0, 0.1), (0, 2.4, 1.32), m=mat('#4a2810', 0.4), bevel=0.02)
    text3d("JUSTIÇA", (0, 3.05, 2.9), size=0.32, m=mat('#ffd23f', 0.3, metal=0.6), font=BOLD, extrude=0.03)
    judge = generic_person(90, (0, 2.6, 0.35), female=False, jacket='#111111', hair='#d0d0d0', hair_style='gray', collar=False)
    life(c, judge, 90)
    gv = gavel((0.45, 1.95, 1.42))
    f1 = int(c.n * 0.33)
    judge.arm(1, 1, (-1.3, 0, 0.3))
    for k in range(2):
        judge.arm(1, f1 + k * 8, (-2.0, 0, 0.3)); judge.arm(1, f1 + 4 + k * 8, (-1.2, 0, 0.3))
    key(gv, 'rotation_euler', f1, (0.0, 0, 0)); key(gv, 'rotation_euler', f1 + 4, (0.0, 0.6, 0)); key(gv, 'rotation_euler', f1 + 8, (0, 0, 0))
    table((-0.6, 0.6, 0), (1.4, 0.7), 0.75, '#8a5a32', '#5a3a1a')
    j = jane(loc=(-0.6, 0.2, 0), rot=0)
    life(c, j, 91)
    j.brows_set(f1 + 8, 0.2); key(j.mouth, 'scale', f1 + 4, (1, 1, 0.35)); key(j.mouth, 'scale', f1 + 14, (1.4, 1, 0.5))
    f2 = int(c.n * 0.62)
    j.brows_set(f2 + 4, 0.45); key(j.mouth, 'scale', f2, (1.4, 1, 0.5)); key(j.mouth, 'scale', f2 + 8, (0.8, 1, 0.3))
    for i in range(3):
        p = generic_person(95 + i, (1.6 + i * 0.5, 1.2, 0), rot=PI * 0.55); p.sit(); p.root.location.z = 0.1; life(c, p, 95 + i)
    sun(rot=(0.8, 0.1, 0.5), energy=3.0)
    cam, t = camera((0, -2.5, 1.8), (0, 1.5, 1.3), 30)
    key(cam, 'location', 1, (0.2, -2.4, 1.9)); key(t, 'location', 1, (0, 1.8, 1.5))
    key(cam, 'location', f2 - 4, (0.0, -1.9, 1.8)); key(t, 'location', f2 - 4, (-0.1, 1.4, 1.4))
    key(cam, 'location', f2 + 6, (-0.6, -0.9, 1.45)); key(t, 'location', f2 + 6, (-0.6, 0.2, 1.38))
    key(cam, 'location', c.n, (-0.6, -0.7, 1.43))

def s20(c):
    setup_render(sky='#1f1f33', sky_strength=0.6)
    floor('#26263a', 30)
    box((12, 0.2, 5), (0, 1.4, 2.5), m='#33334d')
    corkboard((0, 1.25, 2.0), 2.6, 1.7)
    cards = []
    for i in range(7):
        x = (-0.81 + i * 0.54) if i < 4 else (-0.54 + (i - 4) * 0.54)
        z = 2.35 if i < 4 else 1.66
        cd = card((x, 1.18, z), bg='#fffdf2', who='#2d2d34', w=0.44, h=0.58)
        cards.append(cd)
        pop_in(cd, 6 + i * 6, 8)
        n = text3d(str(i + 1), (0, -0.03, -0.38), size=0.14, m='#ffffff', font=BOLD, parent=cd)
    j = jane(loc=(0.62, -0.75, 0), rot=PI * 0.9)
    life(c, j, 100)
    j.arm(1, 10, (-1.0, 0, -0.3))
    j.look(30, -0.25, 0)
    point((0, -0.6, 3.0), 220, '#fff0d0', 0.8)
    cam, t = camera((0, -2.2, 1.8), (0, 1.2, 1.7), 30)
    cam_move(cam, t, c, (-0.1, -3.0, 1.5), (0.0, -2.55, 1.6), (0.05, 1.2, 1.7), (0.05, 1.2, 1.8))

def s21(c):
    setup_render(sky='#3a0a0a', sky_strength=0.5)
    floor('#1a0808', 30)
    tri_bg(['#7a0a0a', '#3a0505'], loc=(0, 3, -1), n=10, w=14, h=8)
    smiley((0, 2.8, 2.0), 1.3, (PI / 2, 0, 0), '#ff2a2a', drips=False, emit=1.2)
    sh = sheriff(loc=(0, 0.6, 0))
    life(c, sh, 110, 0.5)
    sh.brows_set(1, -0.35)
    f1 = int(c.n * 0.5)
    key(sh.mouth, 'scale', f1, (1, 1, 0.35)); key(sh.mouth, 'scale', f1 + 10, (1.6, 1, 0.45))
    key(sh.mouth, 'rotation_euler', f1, (0.3, 0, 0))
    sun(rot=(0.9, 0.0, 0.3), energy=1.5, color='#ff9a8a')
    point((0, -0.4, 2.3), 160, '#ff6a5a', 0.6)
    point((0.8, 0.0, 1.8), 60, '#ffffff', 0.3)
    cam, t = camera((0, -2.4, 1.4), (0, 0.6, 1.3), 40)
    cam_move(cam, t, c, (0, -2.6, 1.3), (0, -0.55, 1.45), (0, 0.6, 1.25), (0, 0.6, 1.42))

def park_set(seed=0, evening=False, trees=None):
    setup_render(sky='#ffb36b' if evening else '#8fd6ff')
    floor('#5ccf5c', 100)
    box((80, 0.2, 40), (0, 25, 15), m=mat('#ffb36b' if evening else '#8fd6ff', 1.0, emit=1.0))
    if evening:
        sphere(2.5, (3, 24, 5), m=mat('#fff0a0', emit=3))
    for i, (x, y) in enumerate(trees or [(-3.5, 4), (3.8, 5), (-6, 9), (6.5, 10), (0.5, 12), (-1.8, 7)]):
        tree((x, y, 0), 1.2 + 0.2 * (i % 3), '#3fbf5f' if i % 2 else '#2fa84f', seed=seed + i)
    for i, (x, z) in enumerate([(-6, 9), (5, 11), (0, 13)]):
        cloud((x, 22, z), 1.4, seed + i)
    # caminho
    box((1.6, 40, 0.02), (0, 10, 0.01), m='#e8d6a8')

def s22(c):
    park_set(1)
    j = jane(loc=(-0.55, 0.6, 0), rot=PI * 0.45)
    sh = sheriff(loc=(0.55, 0.6, 0), rot=-PI * 0.45)
    life(c, j, 120); life(c, sh, 121)
    j.brows_set(1, -0.4); sh.brows_set(1, 0.3)
    f1 = int(c.n * 0.5)
    j.arm(1, f1 - 8, (0, 0.1, 0)); j.arm(1, f1, (-1.4, 0, 0)); j.arm(0, f1, (-1.4, 0, 0))
    # pombas voando
    rnd = random.Random(9)
    for i in range(9):
        x0, y0 = rnd.uniform(-1.6, 1.6), rnd.uniform(-0.6, 1.5)
        d, wings = dove((x0, y0, 0.12), 0.22)
        d.rotation_euler = (0, 0, rnd.uniform(-0.6, 0.6))
        fs = f1 + rnd.randint(-6, 10)
        key(d, 'location', fs, (x0, y0, 0.12))
        key(d, 'location', c.n, (x0 * 2.2 + rnd.uniform(-0.5, 0.5), y0 + rnd.uniform(-1.5, 1.5), rnd.uniform(3.0, 4.5)))
        key(d, 'rotation_euler', fs, (0, 0, d.rotation_euler[2])); key(d, 'rotation_euler', fs + 8, (-0.6, 0, d.rotation_euler[2]))
        flap(wings, fs, c.n, speed=2.2 + rnd.random())
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -3, 1.4), (0, 0.6, 1.2), 32)
    key(cam, 'location', 1, (0, -2.4, 1.25)); key(t, 'location', 1, (0, 0.6, 1.25))
    key(cam, 'location', f1, (0, -2.7, 1.2)); key(t, 'location', f1, (0, 0.6, 1.3))
    key(cam, 'location', c.n, (0, -3.6, 0.9)); key(t, 'location', c.n, (0, 0.6, 2.2))

def s23(c):
    park_set(5, evening=True, trees=[(-3.5, 6), (3.8, 7), (-6, 11), (6.5, 12)])
    # banco
    box((1.6, 0.5, 0.08), (0, 0.6, 0.45), m='#8a5a32', bevel=0.02)
    box((1.6, 0.08, 0.4), (0, 0.85, 0.75), m='#8a5a32', bevel=0.02)
    for sx in (-0.7, 0.7):
        box((0.06, 0.45, 0.45), (sx, 0.6, 0.22), m='#333333')
    j = jane(loc=(0, 0.6, 0.0), rot=0)
    j.sit(); j.root.location.z = 0.2
    life(c, j, 130, 0.5)
    for e in j.eyes:
        key(e, 'scale', 10, (1, 1, 1)); key(e, 'scale', 20, (1, 1, 0.12))
    j.look(10, 0, 0); j.look(28, -0.25, 0)
    sun(rot=(1.0, 0.0, 0.5), energy=3.0, color='#ffc89a')
    cam, t = camera((0, -3, 1.2), (0, 0.6, 1.0), 35)
    cam_move(cam, t, c, (0.0, -2.2, 1.1), (0.0, -3.4, 1.4), (0, 0.6, 1.0), (0, 0.6, 1.3))

def s24(c):
    setup_render(sky='#5fd3ff')
    floor('#ffe39a', 80)
    sea = box((80, 40, 0.1), (0, 22, 0.02), m=mat('#1ec8e8', 0.15))
    box((80, 0.2, 30), (0, 42, 15), m='#7fdcff')
    box((80, 2.5, 0.12), (0, 2.6, 0.03), m=mat('#7ff0ff', 0.2))
    palm((-1.8, 1.4, 0), 1.0, 0.2, 1); palm((2.0, 2.5, 0), 1.2, -0.18, 2)
    sphere(1.6, (6, 40, 9), m=mat('#fff4b0', emit=3))
    for i, (x, z) in enumerate([(-8, 9), (6, 12)]):
        cloud((x, 38, z), 2.0, i)
    j = jane(loc=(0.1, 0.4, 0), hat='straw', beard='#b8892e', jacket='#ffffff', vest=None, shirt='#f5f0e0', pants='#e8dcc0', shoes='#8a5a32', collar=True)
    life(c, j, 140)
    j.look(10, -0.1, 0.25)
    sun(rot=(0.7, 0.1, 0.8), energy=4.0)
    cam, t = camera((0, -3, 1.3), (0, 0.4, 1.2), 32)
    cam_move(cam, t, c, (-0.5, -3.4, 1.0), (0.3, -2.6, 1.3), (0, 0.6, 1.4), (0.1, 0.4, 1.25))

def s25(c):
    setup_render(sky='#0f2a5a')
    room('#123a7a', '#184a96', '#0d1f44', '#132a5a', back_y=2.6)
    text3d("FBI", (0, 2.45, 2.7), size=0.75, m=mat('#ffd23f', 0.3, emit=0.6), font=BOLD, extrude=0.06)
    table((0, 0.8, 0), (0.9, 0.8), 0.75, '#e0e4ee', '#7a8094')
    doc = box((0.3, 0.4, 0.01), (0.35, 0.85, 0.79), m='#ffffff')
    f1 = int(c.n * 0.45)
    key(doc, 'location', f1, (0.25, 0.75, 0.79)); key(doc, 'location', f1 + 18, (-0.2, 0.7, 0.79))
    tx = text3d("IMUNIDADE", (0, 0, 0.007), rot=(0, 0, 0), size=0.04, m='#1a3a7a', font=BOLD, extrude=0.001, bevel=0, parent=doc)
    for z in (-0.06, -0.1, -0.14):
        box((0.22, 0.008, 0.002), (0, z, 0.006), m='#9aa0b0', parent=doc)
    agent = generic_person(150, (0.62, 0.8, 0), rot=-PI * 0.4, skin='#8d5a3b', hair='#111111', hair_style='buzz', female=False, jacket='#1f2a44', collar=True, tie='#2a4a8a')
    agent.sit(); life(c, agent, 150); agent.root.location.z = 0.05
    agent.arm(1, f1, (-1.2, 0, 0)); agent.arm(1, f1 + 18, (-1.4, 0, -0.3))
    talk(c, agent, int(c.n * 0.3), c.n, 0.8)
    j = jane(loc=(-0.62, 0.8, 0), rot=PI * 0.4, beard='#b8892e')
    chair((-0.68, 0.82, 0), PI * 0.4, '#2a3a6a'); chair((0.68, 0.82, 0), -PI * 0.4, '#2a3a6a')
    j.sit(); life(c, j, 151); j.root.location.z = 0.05
    j.brows_set(f1 + 20, 0.25)
    sun(rot=(0.8, 0.1, 0.5), energy=2.8)
    point((0, 0.8, 2.3), 120, '#ffffff', 0.5)
    cam, t = camera((0, -2.3, 1.8), (0, 0.8, 1.0), 32)
    cam_move(cam, t, c, (0.3, -2.5, 1.75), (0.0, -1.9, 1.6), (0, 0.8, 1.1), (-0.05, 0.8, 1.1))

def s26(c):
    cbi_office(extra=False)
    j = jane(loc=(-0.4, 0.3, 0), rot=0.15)
    life(c, j, 160)
    talk(c, j, 1, int(c.n * 0.35))
    j.arm(1, 10, (-0.3, 0, 0)); j.arm(1, 22, (-1.5, 0, 0.0))  # dedo levantado "1 condicao"
    f1 = int(c.n * 0.45)
    j.arm(1, f1 + 6, (-1.35, 0, 0.95))  # aponta para Lisbon (direita)
    j.look(f1, 0, 0.55)
    L = lisbon(loc=(1.3, 0.0, 0), rot=PI * 0.3)
    L.walk(f1, int(c.n * 0.85), (2.8, 0.3, 0), (0.45, 0.25, 0), 1.8)
    key(L.root, 'rotation_euler', f1, (0, 0, PI * 0.5)); key(L.root, 'rotation_euler', int(c.n * 0.85), (0, 0, PI * 0.5)); key(L.root, 'rotation_euler', int(c.n * 0.85) + 8, (0, 0, 0.2))
    L.auto_blink(1, c.n, 6)
    key(L.mouth, 'scale', int(c.n * 0.85), (1, 1, 0.35)); key(L.mouth, 'scale', int(c.n * 0.85) + 10, (1.5, 1, 0.55))
    key(j.mouth, 'scale', int(c.n * 0.85), (1, 1, 0.35)); key(j.mouth, 'scale', int(c.n * 0.85) + 10, (1.5, 1, 0.55))
    sun(rot=(0.8, 0.1, 0.5), energy=3.2)
    cam, t = camera((0, -3, 1.5), (0, 0.3, 1.2), 32)
    cam_move(cam, t, c, (-0.2, -2.6, 1.5), (0.3, -3.1, 1.5), (-0.2, 0.3, 1.25), (0.2, 0.3, 1.2))

def s27(c):
    setup_render(sky='#ffb3c7')
    floor('#7fd67f', 100)
    box((80, 0.2, 40), (0, 25, 15), m=mat('#ffb3a0', 1.0, emit=1.0))
    sphere(3, (0, 24, 4), m=mat('#fff0b0', emit=2.5))
    for i, (x, y) in enumerate([(-3.5, 5), (3.8, 6), (-6, 10), (6.5, 10)]):
        tree((x, y, 0), 1.3, '#4fcf6f', seed=200 + i)
    box((1.6, 40, 0.02), (0, 10, 0.01), m='#f2e2b8')
    j = jane(loc=(-0.3, 0, 0), rot=PI)
    L = lisbon(loc=(0.3, 0, 0), rot=PI)
    j.walk(1, c.n, (-0.3, -1.0, 0), (-0.3, 2.2, 0), 1.6)
    L.walk(1, c.n, (0.3, -1.0, 0), (0.3, 2.2, 0), 1.6)
    j.auto_blink(1, c.n); L.auto_blink(1, c.n, 2)
    sun(rot=(1.1, 0.0, 3.0), energy=3.0, color='#ffd0a8')
    cam, t = camera((0, -4, 1.3), (0, 0.5, 1.2), 32)
    cam_move(cam, t, c, (0, -3.6, 1.2), (0, -2.0, 1.4), (0, 0.0, 1.2), (0, 2.5, 1.3))

def s28(c):
    setup_render(sky='#bfe9ff')
    floor('#8fe08f', 100)
    box((80, 0.2, 40), (0, 25, 15), m=mat('#bfe9ff', 1.0))
    for i, (x, z) in enumerate([(-5, 8), (5, 10)]):
        cloud((x, 22, z), 1.5, 10 + i)
    flower_arch((0, 1.2, 0), 2.2, 2.7)
    box((1.2, 6, 0.02), (0, -1.5, 0.012), m='#ffffff')
    L = lisbon(loc=(0.33, 0.8, 0), rot=PI * 0.12, dress='#ffffff', hat='veil')
    j = jane(loc=(-0.33, 0.8, 0), rot=-PI * 0.12, jacket='#3a3f4a', vest='#4a505c')
    sphere(0.035, (-0.1, -0.13, 0.48), m='#ff4f8b', parent=j.chest)
    life(c, j, 170); life(c, L, 171)
    for ch in (j, L):
        key(ch.mouth, 'scale', 1, (1.5, 1, 0.55))
    j.arm(1, 1, (-0.5, 0, 0.6)); L.arm(0, 1, (-0.5, 0, -0.6))
    # confete
    rnd = random.Random(12)
    cols = ['#ff7eb6', '#ffd23f', '#7fd4ff', '#ffffff', '#b388ff']
    for i in range(60):
        x, y, z = rnd.uniform(-1.6, 1.6), rnd.uniform(-0.5, 1.6), rnd.uniform(2.5, 4.0)
        cf = box((0.04, 0.04, 0.008), (x, y, z), m=rnd.choice(cols))
        key(cf, 'location', 1, (x, y, z), 'LINEAR')
        key(cf, 'location', c.n, (x + rnd.uniform(-0.4, 0.4), y, z - rnd.uniform(2.0, 3.0)), 'LINEAR')
        key(cf, 'rotation_euler', 1, (0, 0, 0), 'LINEAR'); key(cf, 'rotation_euler', c.n, (rnd.uniform(-6, 6), rnd.uniform(-6, 6), 0), 'LINEAR')
    for i in range(4):
        p = generic_person(180 + i, (-1.8 + i * 1.2 + (0.0 if i < 2 else 0.0), -1.4, 0), rot=PI)
        p.root.location.x = [-1.6, -1.0, 1.0, 1.6][i]
        p.sit(); p.root.location.z = 0.1
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -3, 1.4), (0, 0.8, 1.3), 32)
    cam_move(cam, t, c, (0, -3.4, 1.3), (0, -2.2, 1.45), (0, 0.9, 1.4), (0, 0.8, 1.4))

def s29(c):
    setup_render(sky='#ff9a6b')
    floor('#f2c38a', 100)
    sea = box((80, 40, 0.1), (0, 22, 0.02), m=mat('#ff8a7a', 0.15))
    box((80, 0.2, 40), (0, 40, 15), m=mat('#ff9f7a', 1.0, emit=1.0))
    box((80, 0.2, 6), (0, 39.8, 1.5), m=mat('#ffc58a', 1.0, emit=1.0))
    sphere(3.2, (0, 38, 5.5), m=mat('#fff0b0', emit=3))
    for i, (x, z) in enumerate([(-7, 8), (6, 10), (-2, 12)]):
        cloud((x, 36, z), 2.2, 30 + i, color='#ffd3e0')
    j = jane(loc=(-0.36, 0.3, 0), rot=PI * 0.33)
    L = lisbon(loc=(0.36, 0.3, 0), rot=-PI * 0.33)
    life(c, j, 190, 0.6); life(c, L, 191, 0.6)
    f1 = int(c.n * 0.55)
    key(L.mouth, 'scale', f1, (1, 1, 0.35)); key(L.mouth, 'scale', f1 + 15, (1.5, 1, 0.55))
    key(j.mouth, 'scale', f1 + 10, (1, 1, 0.35)); key(j.mouth, 'scale', f1 + 25, (1.5, 1, 0.55))
    # mãos dadas
    j.arm(1, 1, (-0.25, 0.25, 0)); L.arm(0, 1, (-0.25, -0.25, 0))
    sun(rot=(1.2, 0.0, 3.1), energy=3.2, color='#ffc49a')
    point((0, -1.2, 2.0), 90, '#ffe0c0', 1.0)
    cam, t = camera((0, -2.4, 1.4), (0, 0.3, 1.35), 40)
    cam_move(cam, t, c, (0, -2.7, 1.35), (0, -1.5, 1.42), (0, 0.3, 1.3), (0, 0.3, 1.42))

SHOTS = {k: v for k, v in globals().items() if k.startswith('s') and k[1:3].isdigit()}
