# Breaking Bad - definicao de cada shot (cenario + personagens + animacao + camera)
# Convencao: personagem com rot=θ olha para (sin θ, -cos θ). θ=0 -> camera (-Y); θ=+π/2 -> +X; θ=-π/2 -> -X.
# Cadeiras/cadeira de rodas/vaso usam o mesmo rot de quem senta. Eventos sincronizados com as palavras (wf).
import bpy, math, random, json, os, re
from mathutils import Vector, Matrix
from lib import *
from props import *

BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SERIF = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
PI = math.pi
_TL = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'audio', 'timeline.json')))


class Ctx:
    def __init__(self, n, f0, env):
        self.n, self.f0, self.env = n, f0, env
    def g(self, f):
        return self.f0 + f - 1


def _norm(w):
    return re.sub(r'[^\w-]', '', w.lower())

def wf(c, word, n=1, off=0):
    """frame local (1 = inicio do shot) em que a palavra comeca a ser falada"""
    sh = [s for s in _TL['shots'] if s['f0'] == c.f0][0]
    k = 0
    for w in sh['words']:
        if _norm(w['w']) == _norm(word):
            k += 1
            if k == n:
                return max(1, min(c.n, int(round(w['t0'] * 30)) - c.f0 + 1 + off))
    raise KeyError(word)

def talk(c, ch, fa=1, fb=None, gain=1.0):
    fb = fb or c.n
    for f in range(fa, fb + 1, 2):
        a = c.env[c.g(f)] if 0 <= c.g(f) < len(c.env) else 0
        ch.mouth.scale = (1 - 0.15 * a, 1, 0.35 + 1.9 * min(1, a * gain))
        ch.mouth.keyframe_insert('scale', frame=f)
    key(ch.mouth, 'scale', fb + 2, (1, 1, 0.35))

def life(c, ch, seed=0, amp=1.0, blink=True):
    ch.idle(1, c.n + 5, amp, seed)
    if blink:
        ch.auto_blink(1, c.n, seed)

def cam_move(cam, tgt, c, p0, p1, t0=None, t1=None, fa=1, fb=None):
    fb = fb or c.n
    key(cam, 'location', fa, p0); key(cam, 'location', fb, p1)
    if t0 is not None:
        key(tgt, 'location', fa, t0); key(tgt, 'location', fb, t1 if t1 is not None else t0)

def cam_path(cam, tgt, pts):
    """pts: [(frame, cam_loc, tgt_loc), ...]"""
    for f, p, t in pts:
        key(cam, 'location', f, p); key(tgt, 'location', f, t)

def shot_cam(f, loc, tgt, lens=32):
    """camera extra ativada por marcador a partir do frame f (corte seco)"""
    cam, t = camera(loc, tgt, lens, name=f'cam{f}')
    m = bpy.context.scene.timeline_markers.new(f'c{f}', frame=f)
    m.camera = cam
    return cam, t

def smile(ch, f, big=False):
    key(ch.mouth, 'scale', f - 6, tuple(ch.mouth.scale)); key(ch.mouth, 'scale', f, (1.6 if big else 1.4, 1, 0.55))

def room(wall='#7ecbff', wall2=None, fl1='#f6b33c', fl2='#ffd36a', back_y=3.0, side_x=None, w=16, h=7, sq=0.7, trim='#ffffff', ox=0.0):
    checker_floor(fl1, fl2, size=24, scale=sq, loc=(ox, 0, 0))
    if wall2:
        stripes_wall(wall, wall2, w=w, h=h, n=int(w / 0.8), loc=(ox, back_y, 0), horizontal=False)
    else:
        box((w, 0.2, h), (ox, back_y + 0.1, h / 2), m=wall)
    box((w, 0.25, 0.3), (ox, back_y - 0.05, 0.15), m=trim)
    if side_x is not None:
        box((0.2, 12, h), (ox + side_x, back_y - 6, h / 2), m=wall)

def ground(ox, color, size=30, z=0.0):
    box((size, size, 0.02), (ox, 0, z - 0.009), m=mat(color, 0.8))

def night_world(sky='#0d1b3d', amb=0.35):
    setup_render(sky=sky, sky_strength=amb)

def baby(parent=None, loc=(0, 0, 0), rot=(0, 0, 0)):
    p = empty("baby", loc, parent, rot)
    sphere(1, (0, 0, 0), (0.12, 0.2, 0.1), mat('#ffd0e0', 0.8), p)
    sphere(0.075, (0, -0.17, 0.04), m=SKIN, parent=p)
    for sx in (-1, 1):
        sphere(0.008, (sx * 0.025, -0.235, 0.06), m='#222222', parent=p, seg=8)
    return p

# ----------------------------------------------------------------- poses
def upd():
    bpy.context.view_layer.update()

def chest_pt(ch, v):
    upd()
    return ch.chest.matrix_world @ Vector(v)

def aim_rot(ch, side, target):
    """rotacao do braco para a mao apontar para target (mundo)"""
    upd()
    a = ch.arms[side]
    pm = a.parent.matrix_world
    sh = pm @ a.location
    d = pm.to_3x3().inverted() @ (Vector(target) - sh)
    q = Vector((0, 0, -1)).rotation_difference(d.normalized())
    e = q.to_euler('XYZ')
    return (e.x, e.y, e.z)

def aim(ch, side, target, f=None, ease=8, fit=False):
    r = aim_rot(ch, side, target)
    if fit:      # encurta o braco para a mao chegar exatamente no alvo (ex.: telefone na orelha)
        upd()
        a = ch.arms[side]
        dist = (Vector(target) - a.parent.matrix_world @ a.location).length
        a.scale = (1, 1, max(0.72, min(1.0, dist / 0.44)))
    if f is None:
        ch.arms[side].rotation_euler = r
    else:
        ch.arm(side, f, r, ease=ease)
    return r

def hand_obj(ch, side):
    """empty na mao (para segurar objetos)"""
    return empty("hand", (0, 0, -0.47), ch.arms[side])

def sit_on(ch, seat):
    ch.sit()
    ch.root.location.z = seat + 0.075 - ch.leg_len * 0.55

def lie(ch, z, tilt=0.12, yaw=0.0):
    """deitado de costas, cabeca para +Y (girado por yaw)"""
    ch.root.rotation_euler = (-(PI / 2 - tilt), 0, yaw)
    ch.root.location.z = z

def close_eyes(ch):
    for e in ch.eyes:
        e.scale = (1, 1, 0.1)

def show_from(ch, f):
    hide_between(ch.root, f, None)

def hide_from(ch, f):
    hide_between(ch.root, None, f)

def spike(f, loc, color='#ffffff', e=3000, dur=5, radius=0.5):
    l = point(loc, 0, color, radius)
    l.data.keyframe_insert('energy', frame=max(1, f - 1))
    l.data.energy = e; l.data.keyframe_insert('energy', frame=f)
    l.data.energy = 0; l.data.keyframe_insert('energy', frame=f + dur)
    return l

def porkpie(parent, R=0.27):
    p = empty("hat", (0, 0, 0), parent)
    cyl(0.36, 0.022, (0, 0.0, R * 0.78), m=mat('#141416', 0.6), parent=p, scale=(1, 0.95, 1))
    cyl(0.24, 0.17, (0, 0.0, R * 0.9), m=mat('#141416', 0.6), parent=p)
    cyl(0.243, 0.035, (0, 0.0, R * 0.84), m=mat('#2a2a30', 0.5), parent=p)
    cyl(0.2, 0.02, (0, 0.0, R * 0.99), m=mat('#1e1e22', 0.6), parent=p)
    return p

def walt_final(**kw):
    d = dict(name='waltf', jacket='#5a4a3a', shirt='#8a7a6a', pants='#4a4a42', beard='#a8a39a', mustache='#a8a39a', hair='#a8a39a')
    d.update(kw); return walt(**d)

def hazmat(fn, **kw):
    d = dict(jacket='#f2d21a', shirt='#f2d21a', pants='#f2d21a', sleeves='#f2d21a', shoes='#3a3a3a', respirator=True, collar=False)
    d.update(kw); return fn(**d)

def krazy8(**kw):
    d = dict(name='k8', skin='#c89a72', hair='#1a1a1a', hair_style='buzz', eyes='#2a1a10', jacket='#2a2a32', vest=None,
             shirt='#2a2a32', pants='#3a3a32', shoes='#1a1a1a', collar=False, goatee='#1a1a1a', brows='#1a1a1a', body_w=1.04)
    d.update(kw); return Char(**d)

def emilio(**kw):
    d = dict(name='emilio', skin='#d8a882', hair='#2a1a10', hair_style='short', eyes='#2a1a10', jacket='#7a7a7a', vest=None,
             shirt='#7a7a7a', pants='#2a3a5a', shoes='#e8e8e8', collar=False, brows='#2a1a10', body_w=0.95)
    d.update(kw); return Char(**d)

def doctor(**kw):
    d = dict(name='doc', skin='#e0a97f', hair='#3a2a1a', hair_style='short', eyes='#3a2a1a', jacket='#f2f2ee', vest=None,
             shirt='#9fc8e8', tie='#2a4a7a', pants='#4a4a52', coat='#f2f2ee', glasses=True, brows='#3a2a1a')
    d.update(kw); return Char(**d)

def crutches(ch, color='#b8bcc4'):
    """muletas de antebraco presas no chao sob cada mao"""
    upd()
    m = mat(color, 0.25, metal=0.8)
    for a in ch.arms:
        hp = a.matrix_world @ Vector((0, 0, -0.44))
        x, y = hp.x, hp.y - 0.06
        h = hp.z
        cyl(0.017, h + 0.08, (x, y, (h + 0.08) / 2), m=m)
        cyl(0.03, 0.05, (x, y, 0.025), m='#2a2a2a')
        cyl(0.015, 0.1, (x, y - 0.05, h), (PI / 2, 0, 0), m='#2a2a2a')
        torus(0.05, 0.012, (x, y + 0.02, h + 0.2), m=m)


# ============================================================================ SHOTS
def s01(c):
    """GANCHO: o professor vira Heisenberg; cristais azuis, sirenes, Br/Ba"""
    desert_world(sky='#ffb978', sand='#e3ac6c', mesa='#c06a42', back=20, n_cactus=5, cact_y=(5, 12))
    rv((2.6, 4.2, 0), 0)
    w = walt(loc=(0, 0.4, 0), rot=0)
    h = heisenberg(loc=(0, 0.4, 0), rot=0)
    fv = wf(c, 'virou')
    for ch, s in ((w, 1), (h, 1)):
        life(c, ch, s, 0.8)
    hide_from(w, fv); show_from(h, fv)
    w.brows_set(8, 0.2)
    h.brows_set(fv + 2, -0.35, 1)
    key(h.mouth, 'scale', fv + 30, (1.2, 1, 0.35)); key(h.mouth, 'scale', fv + 40, (1.35, 1, 0.45))
    spike(fv, (0, -0.6, 1.6), '#ffffff', 600, 4)
    # Br / Ba
    t1 = pt_tile('Br', 35, (-0.47, 1.0, 2.5), 0.78, font=BOLD)
    t2 = pt_tile('Ba', 56, (0.47, 1.0, 2.5), 0.78, font=BOLD)
    pop_in(t1, wf(c, 'Esse'), 10); pop_in(t2, wf(c, 'Esse') + 5, 10)
    # cristais + dinheiro ao redor
    fd = wf(c, 'drogas')
    for i, (x, y) in enumerate(((-0.75, 0.0), (0.8, 0.05), (-0.45, -0.45), (0.5, -0.5))):
        cr = crystals((x, y, 0), 12, 0.16, seed=i, s=1.6)
        pop_in(cr, fd + i * 3, 8)
    for i, (x, y) in enumerate(((-1.25, 0.6), (1.3, 0.7))):
        ms = money_stack((x, y, 0), 6, rot=0.3 * (i - 0.5))
        pop_in(ms, fd + 10 + i * 3, 8)
    fp = wf(c, 'procurado')
    police_lights(fp, c.n, (-2.2, -0.6, 1.4), (2.2, -0.6, 1.4), 350, 7)
    sun(rot=(1.15, 0.0, -0.9), energy=3.6, color='#ffd6a0')
    point((0, -1.2, 2.2), 60, '#ffe6c8', 1.0)
    cam, t = camera((0, -3.0, 1.5), (0, 0.6, 1.55), 32)
    fe = wf(c, 'E')
    cam_path(cam, t, [(1, (0, -3.0, 1.5), (0, 0.6, 1.6)), (fe, (0, -2.5, 1.5), (0, 0.6, 1.6)),
                      (c.n, (0, -1.35, 1.42), (0, 0.4, 1.38))])


def s02(c):
    """POV: professor de quimica (sala de aula) -> lava-jato"""
    setup_render(sky='#bfe6ff')
    room('#cfe3cf', None, '#c8b89a', '#b8a88a', back_y=2.2, sq=0.7, trim='#8a6a4a')
    chalkboard((0, 2.13, 1.72), 3.0, 1.3, ['QUÍMICA', 'C₁₀H₁₅N'], size=0.26, font=BOLD)
    for i, (sym, n) in enumerate((('H', 1), ('C', 6), ('N', 7), ('O', 8))):
        pt_tile(sym, n, (-0.75 + i * 0.5, 2.06, 2.78), 0.42, font=BOLD)
    td = table((-1.0, 0.75, 0), (1.0, 0.6), 0.78, '#9a6a3a', '#6a4a2a')
    flask((-1.25, 0.72, 0.81), '#3cc0ff'); flask((-0.95, 0.8, 0.81), '#ffd23f'); book(None, (-0.72, 0.7, 0.94), (0, 0, 0.3), '#c0392b')
    w = walt(loc=(0.45, 0.8, 0), rot=-0.15)
    life(c, w, 3)
    ce = wf(c, 'e')
    talk(c, w, 1, ce - 4, 0.8)
    ch_ = hand_obj(w, 1)
    box((0.02, 0.02, 0.07), (0, 0, -0.02), m='#f2f2ea', parent=ch_)          # giz
    aim(w, 1, (0.85, 0.2, 1.45), wf(c, 'professor'))
    aim(w, 1, (0.75, 0.25, 1.25), wf(c, 'Albuquerque'))
    sun(rot=(0.8, 0.1, 0.5), energy=3.0)
    point((0, -0.5, 2.6), 80, '#fff2dc', 1.0)
    cam, t = camera((0, -3.0, 1.45), (0.0, 0.9, 1.4), 32)
    cam_move(cam, t, c, (-0.1, -3.0, 1.45), (0.05, -2.55, 1.42), (0.0, 0.9, 1.4), (0.2, 0.9, 1.35), 1, ce - 1)
    # ---- lava-jato (x=40)
    X = 40
    ground(X, '#9aa0a6')
    box((30, 0.2, 6), (X, 6.0, 3), m='#cfe8f8')
    for x in (-1.6, 1.6):
        cyl(0.07, 3.0, (X + x + 0.3, 3.2, 1.5), m='#c8c8c8')
    box((3.8, 0.15, 0.9), (X + 0.3, 3.2, 3.2), m='#2f6bff', bevel=0.05)
    text3d('A1A CAR WASH', (X + 0.3, 3.1, 3.2), size=0.4, m=mat('#ffffff', 0.4, emit=0.5), font=BOLD, extrude=0.03)
    sedan((X + 1.1, 1.55, 0), PI / 2, '#c0392b')
    rnd = random.Random(4)
    for i in range(16):
        dx = rnd.uniform(-1.7, 1.7)
        sphere(rnd.uniform(0.05, 0.1), (X + 1.1 + dx, 1.55 + rnd.uniform(-0.7, 0.7), 1.32 if abs(dx + 0.15) < 0.75 else 0.89), m=mat('#ffffff', 0.4), seg=12)
    cyl(0.16, 0.3, (X - 0.75, -0.1, 0.15), m='#2f6bff')
    for i in range(6):
        sphere(0.06, (X - 0.75 + rnd.uniform(-0.1, 0.1), -0.1 + rnd.uniform(-0.1, 0.1), 0.32), m=mat('#ffffff', 0.4), seg=12)
    w2 = walt(name='walt2', loc=(X - 0.1, 0.05, 0), rot=0.1, jacket='#cdbf9a')
    life(c, w2, 4)
    sp = hand_obj(w2, 1)
    box((0.14, 0.08, 0.08), (0, 0, -0.02), m=mat('#ffd23f', 0.9), parent=sp, bevel=0.02)
    aim(w2, 1, (X + 0.45, -0.45, 1.05))
    w2.brows_set(ce + 10, 0.35)
    w2.look(ce + 30, 0.2, 0)
    cam2, t2 = shot_cam(ce, (X + 0.2, -2.9, 1.45), (X + 0.3, 0.7, 1.2), 32)
    cam_move(cam2, t2, c, (X + 0.2, -2.9, 1.45), (X + 0.1, -2.5, 1.4), (X + 0.3, 0.7, 1.2), (X + 0.1, 0.7, 1.2), ce, c.n)


def s03(c):
    """50 anos -> diagnostico de cancer"""
    setup_render(sky='#e8f4f8')
    room('#d8ecf2', None, '#e0e4e8', '#d0d6dc', back_y=2.0, sq=0.7)
    # painel de raio-X em pe
    xb = xray_box((-0.05, 1.2, 1.55), 0, spot=True)
    for sx in (-1, 1):
        cyl(0.025, 1.15, (-0.05 + sx * 0.4, 1.2, 0.575), m='#9aa0a8')
        box((0.3, 0.3, 0.03), (-0.05 + sx * 0.4, 1.2, 0.015), m='#9aa0a8')
    cb = box((0.12, 0.25, 0.02), (1.3, 1.85, 1.5), m='#ffffff')
    doc = doctor(loc=(0.85, 1.0, 0), rot=-0.3)
    life(c, doc, 5)
    fd = wf(c, 'vem')
    talk(c, doc, fd, wf(c, 'cirurgia') + 18, 0.9)
    fc = wf(c, 'câncer')
    aim(doc, 0, (0.2, 1.05, 1.6), fc - 4)
    aim(doc, 0, (0.55, 0.85, 0.75), fc + 40)
    doc.brows_set(fc, 0.3)
    w = walt(loc=(-0.8, 0.25, 0), rot=0.35)
    chair((-0.8, 0.25, 0), 0.35, '#5a7a9a')
    sit_on(w, 0.48)
    life(c, w, 6, 0.6)
    w.arm(0, 1, (-0.35, -0.1, 0)); w.arm(1, 1, (-0.35, 0.1, 0))
    w.brows_set(fc, 0.5)
    w.look(fc + 2, 0, -0.35)
    w.look(wf(c, 'sem') + 4, 0.3, -0.1)
    # mancha acende no raio-X
    pl = point((-0.25, 1.0, 1.65), 0, '#ff6a4a', 0.2)
    pl.data.keyframe_insert('energy', frame=fc - 2); pl.data.energy = 25; pl.data.keyframe_insert('energy', frame=fc + 6)
    sun(rot=(0.8, 0.1, 0.5), energy=2.8)
    point((0, -0.8, 2.5), 60, '#ffffff', 1.0)
    cam, t = camera((0, -2.9, 1.4), (0, 0.8, 1.2), 32)
    cam_path(cam, t, [(1, (0.1, -2.9, 1.4), (0.0, 0.8, 1.25)), (fc - 6, (0.0, -2.65, 1.38), (0.0, 0.8, 1.22)),
                      (c.n, (-0.45, -1.6, 1.25), (-0.7, 0.3, 1.05))])


def s04(c):
    """Skyler gravida e Walter Jr."""
    setup_render(sky='#ffe8c8')
    checker_floor('#e8d8b8', '#d8c8a8', size=24, scale=0.7)
    kitchen(back_y=2.5)
    box((0.9, 0.8, 2.0), (3.05, 1.9, 1.0), m=mat('#f2f2ee', 0.3), bevel=0.04)   # geladeira
    sk = skyler(loc=(-0.6, 0.6, 0), rot=0.3, belly='#4a8aa8')
    jr = walt_jr(loc=(0.7, 0.55, 0), rot=-0.3)
    life(c, sk, 7); life(c, jr, 8, 0.4)
    fs = wf(c, 'Skáiler')
    smile(sk, fs + 4)
    fg = wf(c, 'grávida')
    aim(sk, 0, chest_pt(sk, (-0.02, -0.3, 0.22)), fg)
    aim(sk, 1, chest_pt(sk, (0.06, -0.3, 0.12)), fg + 4)
    crutches(jr)
    fj = wf(c, 'Djúnior')
    smile(jr, fj + 6)
    jr.look(fj + 10, 0.05, 0.25)
    sun(rot=(0.8, 0.1, 0.6), energy=3.0)
    point((0, -0.6, 2.4), 70, '#fff0dc', 1.0)
    cam, t = camera((-0.5, -2.8, 1.35), (-0.55, 0.6, 1.15), 35)
    cam_path(cam, t, [(1, (-0.55, -2.9, 1.38), (-0.6, 0.6, 1.15)), (wf(c, 'e') - 4, (-0.45, -2.6, 1.36), (-0.5, 0.6, 1.15)),
                      (wf(c, 'filho') + 14, (0.55, -2.65, 1.3), (0.6, 0.55, 1.05)), (c.n, (0.6, -2.35, 1.28), (0.65, 0.55, 1.05))])


def s05(c):
    """Hank, agente federal; batida policial"""
    setup_render(sky='#9fd8ff')
    floor('#8ac46a', 160)
    box((40, 3.0, 0.02), (0, 2.6, 0.005), m='#5a5a60')
    house_ext((0, 7.2, 0), wall='#e8dcc0', roof='#7a5a4a', night=False)
    car = sedan((2.8, 2.6, 0), PI / 2, '#1a1a1e')
    light_bar(car)
    hk = hank(loc=(-0.45, 0.3, 0), rot=0.35)
    w = walt(loc=(0.55, 0.4, 0), rot=-0.35)
    life(c, hk, 9); life(c, w, 10)
    talk(c, hk, wf(c, 'cunhado'), wf(c, 'policial') + 15, 1.0)
    fa = wf(c, 'agente')
    bh = hand_obj(hk, 1)
    bdg = empty('bdg', (0, 0, 0), bh, (0, 0, 0))
    box((0.1, 0.02, 0.13), (0, -0.01, 0), m='#3a2a1a', parent=bdg, bevel=0.01)
    sphere(1, (0, -0.025, 0.0), (0.035, 0.008, 0.04), mat('#e8c34a', 0.2, metal=0.9), bdg)
    hide_between(bdg, fa - 4, None)
    aim(hk, 1, chest_pt(hk, (0.25, -0.75, 0.62)), fa)
    aim(hk, 1, chest_pt(hk, (0.3, -0.1, -0.2)), wf(c, 'e') + 6)
    hide_between(bdg, None, wf(c, 'e') + 6)
    smile(hk, fa + 20)
    fl = wf(c, 'leva')
    hk.look(fl, 0, -0.35)
    aim(hk, 0, chest_pt(hk, (-0.6, -0.4, 0.55)), fl + 4)
    fb = wf(c, 'batida')
    police_lights(fb - 6, c.n, (2.5, 2.4, 1.6), (3.1, 2.4, 1.6), 300, 7)
    w.brows_set(fb, 0.3)
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0, -3.2, 1.45), (0.1, 0.8, 1.25), 32)
    cam_move(cam, t, c, (0, -3.2, 1.45), (0.1, -2.6, 1.4), (0.1, 0.8, 1.25), (0.2, 0.9, 1.25))


def s06(c):
    """Jesse foge pela janela"""
    setup_render(sky='#a8dcff')
    floor('#8ab46a', 160)
    sid = '#d8c49a'
    # parede com abertura de janela (x -0.55..0.55, z 0.6..2.5)
    box((3.5, 0.2, 3.3), (-2.3, 2.0, 1.65), m=sid)
    box((3.5, 0.2, 3.3), (2.3, 2.0, 1.65), m=sid)
    box((1.1, 0.2, 0.6), (0, 2.0, 0.3), m=sid)
    box((1.1, 0.2, 0.8), (0, 2.0, 2.9), m=sid)
    fr = mat('#ffffff', 0.4)
    for x in (-0.6, 0.6):
        box((0.1, 0.26, 2.0), (x, 1.98, 1.55), m=fr)
    box((1.3, 0.3, 0.1), (0, 1.95, 0.57), m=fr); box((1.3, 0.26, 0.1), (0, 1.98, 2.53), m=fr)
    box((8, 0.4, 0.3), (0, 2.0, 3.4), m='#7a5a4a')
    # interior escuro
    box((1.3, 2.0, 0.05), (0, 3.1, 0.575), m='#6a5040')
    box((3, 0.2, 3.3), (0, 4.1, 1.65), m='#5a4a3e')
    box((0.2, 2.2, 3.3), (-0.75, 3.1, 1.65), m='#5a4a3e'); box((0.2, 2.2, 3.3), (0.75, 3.1, 1.65), m='#5a4a3e')
    point((0, 3.3, 2.2), 40, '#ffd8a0', 0.3)
    tree((-2.6, 3.0, 0), 1.2, seed=2); tree((2.9, 3.4, 0), 1.0, seed=5)
    j = jesse(loc=(0, 2.75, 0.6), rot=0)
    life(c, j, 11)
    j.brows_set(1, 0.35, 1)
    ff = wf(c, 'fugindo')
    # sai pela janela (passa dentro da abertura) e pula no chao
    key(j.root, 'location', ff - 6, (0, 2.75, 0.6))
    key(j.root, 'location', ff + 6, (0, 2.0, 0.7))
    key(j.root, 'location', ff + 12, (0, 1.4, 0.62))
    key(j.root, 'location', ff + 18, (0, 1.2, 0.0))
    for l in j.legs:
        key(l, 'rotation_euler', ff + 4, (0, 0, 0)); key(l, 'rotation_euler', ff + 9, (-0.5, 0, 0)); key(l, 'rotation_euler', ff + 18, (0, 0, 0))
    aim(j, 0, chest_pt(j, (-0.2, -0.45, 0.45)), ff + 6, 6); aim(j, 1, chest_pt(j, (0.2, -0.45, 0.45)), ff + 6, 6)
    j.arm(0, ff + 20, (0, -0.12, 0)); j.arm(1, ff + 20, (0, 0.12, 0))
    fn = wf(c, 'Djéssi')
    j.look(fn - 8, 0, 0.35)
    # corre para a direita
    fr0 = wf(c, 'Pínkmen') + 2
    key(j.root, 'rotation_euler', fr0, (0, 0, 0)); key(j.root, 'rotation_euler', fr0 + 4, (0, 0, PI / 2))
    j.walk(fr0 + 2, c.n + 8, (0, 1.2, 0), (3.4, 0.9, 0), steps_per_sec=4.0, bob=0.05)
    w = walt(loc=(-0.7, -0.75, 0), rot=2.85)
    life(c, w, 12)
    sun(rot=(0.8, 0.1, 0.6), energy=3.6)
    cam, t = camera((0.3, -3.0, 1.5), (0.1, 1.5, 1.35), 30)
    cam_move(cam, t, c, (0.3, -3.1, 1.5), (0.35, -2.7, 1.45), (0.1, 1.5, 1.4), (0.3, 1.4, 1.25))


def s07(c):
    """proposta: voce cozinha, ele vende"""
    setup_render(sky='#a8dcff')
    floor('#9ac47a', 160)
    house_ext((0, 6.0, 0), wall='#d8c8a8', roof='#6a5a4a', night=False)
    box((40, 2.6, 0.02), (0, 2.4, 0.005), m='#b8b0a0')
    w = walt(loc=(-0.52, 0.6, 0), rot=1.26)
    j = jesse(loc=(0.52, 0.6, 0), rot=-1.26)
    life(c, w, 13); life(c, j, 14)
    talk(c, w, 1, wf(c, 'ele', 2) - 2, 0.9)
    fp = wf(c, 'proposta')
    aim(w, 0, (-0.1, 0.25, 1.2), fp)
    w.arm(0, wf(c, 'você', 2) - 6, (0, -0.12, 0))
    j.brows_set(fp, 0.3)
    fc = wf(c, 'cozinha')
    fh = hand_obj(w, 0)
    fl = flask((0, 0, -0.06), '#3cc0ff', fh, 0.9)
    aim(w, 0, (-0.05, 0.3, 1.08), fc)
    hide_between(fl, fc - 2, None)
    fv = wf(c, 'vende')
    mh = hand_obj(j, 1)
    ms = money_stack((0, 0, -0.08), 3, mh)
    ms.rotation_euler = (PI / 2, 0, 0)
    hide_between(ms, fv - 2, None)
    aim(j, 1, (0.08, 0.3, 1.2), fv)
    smile(j, fv + 8, True); smile(w, fv + 10)
    j.brows_set(fv, -0.1)
    sun(rot=(0.8, 0.1, 0.6), energy=3.5)
    cam, t = camera((0, -2.9, 1.35), (0, 0.6, 1.2), 32)
    cam_move(cam, t, c, (0, -2.95, 1.38), (0, -2.45, 1.33), (0, 0.6, 1.22), (0, 0.6, 1.18))


def s08(c):
    """trailer velho no deserto"""
    desert_world(sky='#ffd9a0', sand='#e6b67a', back=22, n_cactus=7, cact_y=(5, 14))
    rv((0.2, 2.3, 0), 0)
    w = walt(loc=(-0.75, 0.15, 0), rot=0.15)
    j = jesse(loc=(0.7, 0.2, 0), rot=-0.15)
    life(c, w, 15); life(c, j, 16)
    fv = wf(c, 'velho')
    for f0 in (fv - 4,):
        key(j.root, 'location', f0, (0.7, 0.2, 0)); key(j.root, 'location', f0 + 5, (0.7, 0.2, 0.18)); key(j.root, 'location', f0 + 10, (0.7, 0.2, 0))
    aim(j, 1, (2.0, 0.6, 1.35), fv + 2)
    smile(j, fv + 4, True)
    fc = wf(c, 'cozinhar')
    puffs((0.2 - 2.4, 2.8, 3.45), fc, c.n, '#eeeeee', n=14, seed=2, rise=2.2, s=0.32)
    w.look(fc, -0.05, -0.2)
    sun(rot=(1.0, 0.0, -0.7), energy=3.8, color='#ffe2b8')
    cam, t = camera((0, -9.0, 4.0), (0.2, 1.5, 1.6), 32)
    cam_path(cam, t, [(1, (0.3, -9.5, 4.2), (0.2, 1.6, 1.6)), (fc - 4, (0.1, -4.6, 1.7), (0.1, 1.0, 1.4)), (c.n, (0.0, -4.0, 1.55), (0.0, 1.0, 1.35))])


def s09(c):
    """laboratorio no trailer: cristal azul, 99% puro"""
    setup_render(sky='#f2e2c0')
    floor('#7a6a5a', 40)
    box((4, 0.2, 2.6), (0, 1.6, 1.3), m='#e8dcc0')
    box((0.2, 4, 2.6), (-1.35, 0.0, 1.3), m='#ddd0b0'); box((0.2, 4, 2.6), (1.35, 0.0, 1.3), m='#ddd0b0')
    box((4, 4, 0.1), (0, 0, 2.45), m='#efe6d0')
    window((0.6, 1.48, 1.7), 0, 0.7, 0.45, '#ffd9a0', emit=1.5)
    lab_table((0, 0.35, 0), 0, 1.8, 0.8, flasks=False)
    flask((-0.7, 0.35, 0.945), '#3cc0ff'); flask((-0.45, 0.5, 0.945), '#7aff8a', s=0.8)
    meth_tray((0.25, 0.35, 0.945))
    w = hazmat(walt, loc=(-0.3, 1.02, 0), rot=0)
    j = hazmat(jesse, loc=(0.62, 1.05, 0), rot=-0.15, beanie=None, hair_style='buzz')
    life(c, w, 17); life(c, j, 18)
    fa = wf(c, 'azul')
    hh = hand_obj(w, 0)
    cr = cone(0.045, 0, 0.16, (0, 0, -0.05), (0.3, 0, 0.4), m=mat('#3cc0ff', 0.1, emit=0.9, spec=1.0), parent=hh, verts=5)
    hide_between(cr, fa - 10, None)
    aim(w, 0, (-0.45, 0.35, 1.5), fa - 2)
    w.look(fa + 2, -0.1, -0.15)
    f99 = wf(c, 'noventa')
    aim(j, 1, chest_pt(j, (0.35, -0.2, 0.95)), f99 + 4)
    j.brows_set(f99, 0.2)
    pl = point((0.1, 0.3, 1.3), 0, '#3cc0ff', 0.3)
    pl.data.keyframe_insert('energy', frame=fa - 4); pl.data.energy = 60; pl.data.keyframe_insert('energy', frame=fa + 6)
    pl.data.energy = 30; pl.data.keyframe_insert('energy', frame=wf(c, 'pura') - 4); pl.data.energy = 90; pl.data.keyframe_insert('energy', frame=wf(c, 'pura') + 4)
    point((0, -0.6, 2.2), 70, '#fff0d8', 1.0)
    sun(rot=(0.8, 0.1, 0.6), energy=2.0)
    cam, t = camera((0, -1.75, 1.45), (0, 0.7, 1.2), 30)
    cam_move(cam, t, c, (0, -1.8, 1.48), (-0.1, -1.3, 1.42), (0, 0.7, 1.22), (-0.15, 0.7, 1.25))


def s10(c):
    """Krazy-8 e Emilio; gas no trailer"""
    desert_world(sky='#ffd6a0', sand='#e2b07a', back=22, n_cactus=6, cact_y=(6, 14))
    rv((0.6, 3.2, 0), 0)
    k = krazy8(loc=(-0.95, 0.3, 0), rot=1.25)
    e = emilio(loc=(-0.3, 1.3, 0), rot=1.4)
    w = walt(loc=(0.95, 0.65, 0), rot=-1.2)
    for i, ch in enumerate((k, e, w)):
        life(c, ch, 20 + i)
    ft = wf(c, 'tentam')
    for ch, side in ((k, 1), (e, 1)):
        gh = hand_obj(ch, side)
        handgun(gh, (0, 0, 0.02), (PI / 2, 0, 0))
        aim(ch, side, chest_pt(w, (0, 0, 0.45)), wf(c, 'traficantes'))
        ch.brows_set(wf(c, 'traficantes'), -0.4)
    aim(w, 0, chest_pt(w, (-0.33, -0.05, 0.98)), ft); aim(w, 1, chest_pt(w, (0.33, -0.05, 0.98)), ft)
    w.brows_set(ft, 0.5)
    fm = wf(c, 'Você', 1)
    for ch in (k, e, w):
        hide_from(ch, fm - 3)
    # parte 2: gas vermelho saindo do trailer; Walt de mascara
    w2 = walt(name='walt2', loc=(-0.85, 0.55, 0), rot=0.3, respirator=True)
    show_from(w2, fm - 3)
    life(c, w2, 24)
    w2.brows_set(fm, -0.3)
    puffs((0.8, 2.0, 1.5), fm, c.n, '#c84a6a', n=14, seed=3, rise=2.0, s=0.45, spread=0.4, every=3)
    puffs((-1.7, 2.0, 2.0), fm + 4, c.n, '#b8406a', n=10, seed=4, rise=2.0, s=0.4, spread=0.3, every=4)
    pr = point((0.8, 1.6, 1.4), 0, '#ff4a6a', 0.5)
    pr.data.keyframe_insert('energy', frame=fm - 2); pr.data.energy = 120; pr.data.keyframe_insert('energy', frame=fm + 8)
    sun(rot=(1.0, 0.0, -0.7), energy=3.6, color='#ffe2b8')
    fk = wf(c, 'Créizi'); fe = wf(c, 'Emílio')
    cam, t = camera((0, -3.4, 1.4), (0, 0.7, 1.25), 32)
    cam_path(cam, t, [(1, (0.0, -3.5, 1.42), (0.0, 0.75, 1.25)), (fk - 4, (0.0, -3.1, 1.4), (0.0, 0.75, 1.25)),
                      (fk + 8, (-0.75, -2.3, 1.42), (-0.85, 0.5, 1.35)), (fe - 4, (-0.7, -2.2, 1.42), (-0.8, 0.5, 1.35)),
                      (fe + 6, (-0.45, -2.2, 1.42), (-0.55, 1.1, 1.35)), (fm - 4, (-0.4, -2.0, 1.42), (-0.55, 1.1, 1.35))])
    cam2, t2 = shot_cam(fm - 3, (-0.2, -4.6, 1.7), (0.1, 1.5, 1.45), 32)
    cam_move(cam2, t2, c, (-0.2, -4.6, 1.7), (-0.3, -4.0, 1.6), (0.1, 1.5, 1.45), (0.0, 1.4, 1.4), fm - 3, c.n)


def s11(c):
    """nasce Heisenberg: careca, barbicha, chapeu"""
    setup_render(sky='#141018', sky_strength=0.35)
    floor('#1e1a22', 40)
    box((20, 0.2, 8), (0, 2.5, 4), m=mat('#1a1620', 0.9))
    for i, (s_, n_) in enumerate((('Br', 35), ('Ba', 56))):
        tl_ = pt_tile(s_, n_, (-1.35 + i * 2.7, 2.3, 2.1), 0.9, font=BOLD)
    fh = wf(c, 'Raisenberg'); fb = wf(c, 'barbicha'); fc = wf(c, 'chapéu')
    w = walt(loc=(0, 0.4, 0))
    b1 = heisenberg(name='hb1', loc=(0, 0.4, 0), hat=None, goatee=None)
    b2 = heisenberg(name='hb2', loc=(0, 0.4, 0), hat=None)
    for ch in (w, b1, b2):
        life(c, ch, 30, 0.7)
        ch.brows_set(1, -0.2, 1)
    hide_from(w, fh); show_from(b1, fh); hide_from(b1, fb); show_from(b2, fb)
    hat = porkpie(b2.head)
    hide_between(hat, fc - 2, None)
    key(hat, 'location', fc - 1, (0, 0, 1.6)); key(hat, 'location', fc + 9, (0, 0, -0.01)); key(hat, 'location', fc + 13, (0, 0, 0.02)); key(hat, 'location', fc + 16, (0, 0, 0))
    b2.brows_set(fc + 12, -0.4)
    key(b2.mouth, 'scale', fc + 14, (1.0, 1, 0.35)); key(b2.mouth, 'scale', fc + 20, (1.3, 1, 0.4))
    spike(fh, (0, -0.8, 1.6), '#ffffff', 500, 4)
    area((0, 0.2, 3.4), (0, 0, 0), 500, 1.6, '#fff0dc')
    point((-1.6, 0.9, 1.8), 120, '#ff3a2a', 0.4)
    point((1.6, 0.9, 1.8), 90, '#2ad06a', 0.4)
    point((0, -1.5, 1.6), 40, '#ffe8d0', 1.0)
    cam, t = camera((0, -2.4, 1.5), (0, 0.4, 1.45), 35)
    cam_path(cam, t, [(1, (0, -2.6, 1.5), (0, 0.4, 1.4)), (fh, (0, -2.2, 1.5), (0, 0.4, 1.42)),
                      (fb, (0, -1.6, 1.5), (0, 0.4, 1.45)), (fc - 2, (0, -1.7, 1.55), (0, 0.4, 1.5)), (c.n, (0, -1.95, 1.5), (0, 0.4, 1.48))])


def s12(c):
    """Tuco Salamanca (ferro-velho)"""
    setup_render(sky='#f2d8a0')
    floor('#b89a72', 160)
    junk_car((-2.4, 3.4, 0), 0.4, '#8a5a3a', 1); junk_car((2.2, 3.6, 0), -0.3, '#5a6a7a', 2); junk_car((0.0, 5.5, 0), 1.5, '#7a7a4a', 3)
    for x in range(-8, 9):
        box((1.0, 0.08, 2.2), (x, 7.0, 1.1), m='#8a8a8a')
    t = tuco(loc=(0.7, 0.55, 0), rot=-0.95)
    h = heisenberg(loc=(-0.6, 0.45, 0), rot=0.95)
    j = jesse(loc=(-1.25, 1.2, 0), rot=0.7)
    life(c, t, 31, 1.2); life(c, h, 32); life(c, j, 33)
    t.brows_set(1, -0.45, 1)
    talk(c, t, wf(c, 'Tuco') - 4, c.n, 1.7)
    fvd = wf(c, 'vender')
    mh = hand_obj(h, 1)
    bag = box((0.25, 0.12, 0.18), (0, 0, -0.06), m=mat('#3a5a3a', 0.8), parent=mh, bevel=0.03)
    aim(h, 1, (0.0, 0.3, 1.05), fvd)
    hide_between(bag, None, fvd + 18)
    th_ = hand_obj(t, 0)
    bag2 = box((0.25, 0.12, 0.18), (0, 0, -0.06), m=mat('#3a5a3a', 0.8), parent=th_, bevel=0.03)
    hide_between(bag2, fvd + 18, None)
    aim(t, 0, (0.1, 0.25, 1.05), fvd + 12)
    h.arm(1, fvd + 26, (0, 0.12, 0))
    t.arm(0, fvd + 30, (-0.3, -0.12, 0))
    fv = wf(c, 'violento')
    aim(t, 1, chest_pt(t, (0.15, -0.7, 0.55)), fv, 4)
    t.arm(1, fv + 8, (0, 0.12, 0), ease=6)
    j.brows_set(fv, 0.4); h.brows_set(fv, -0.2)
    key(j.root, 'location', fv - 2, (-1.25, 1.2, 0)); key(j.root, 'location', fv + 6, (-1.35, 1.3, 0))
    sun(rot=(0.85, 0.1, 0.6), energy=3.6)
    cam, tt = camera((0, -3.0, 1.4), (0, 0.7, 1.25), 28)
    cam_path(cam, tt, [(1, (-0.3, -3.1, 1.42), (-0.3, 0.75, 1.25)), (fv - 6, (-0.2, -2.8, 1.4), (-0.2, 0.75, 1.25)),
                      (c.n, (0.45, -2.0, 1.4), (0.55, 0.55, 1.38))])


def s13(c):
    """Saul Goodman -> nasce Holly"""
    setup_render(sky='#e8e0d0')
    room('#7a8ab8', '#6a7aa8', '#6a4a3a', '#5a3e30', back_y=2.0, sq=0.8, trim='#e8d070')
    box((3.6, 0.08, 0.6), (0, 1.95, 2.55), m='#c0392b', bevel=0.04)
    text3d('BETTER CALL SAUL!', (0, 1.9, 2.55), size=0.3, m=mat('#ffe27a', 0.4, emit=0.5), font=BOLD, extrude=0.02)
    for x in (-2.3, 2.3):
        cyl(0.03, 2.2, (x, 1.7, 1.1), m='#c8a24a')
    box((0.6, 0.02, 0.4), (-2.0, 1.7, 2.0), m='#ffffff')
    table((0, 0.45, 0), (1.6, 0.7), 0.78, '#6a4a2a', '#4a3020')
    s = saul(loc=(0, 1.08, 0))
    life(c, s, 34)
    fd = wf(c, 'dinheiro')
    for i, x in enumerate((-0.45, -0.15)):
        ms = money_stack((x, 0.35, 0.81), 4, rot=0.2 * i)
        pop_in(ms, fd + i * 3, 8)
    fn = wf(c, 'E')
    talk(c, s, wf(c, 'entra'), fn - 4, 1.0)
    fs = wf(c, 'Sól')
    aim(s, 0, chest_pt(s, (-0.6, -0.3, 0.75)), fs); aim(s, 1, chest_pt(s, (0.6, -0.3, 0.75)), fs)
    smile(s, fs + 8, True)
    s.brows_set(fs, 0.25)
    sun(rot=(0.8, 0.1, 0.6), energy=2.6)
    point((0, -0.5, 2.4), 80, '#fff0dc', 1.0)
    cam, t = camera((0, -2.4, 1.45), (0, 0.8, 1.3), 32)
    cam_move(cam, t, c, (0, -2.5, 1.48), (0, -2.05, 1.42), (0, 0.8, 1.32), (0, 0.85, 1.32), 1, fn - 1)
    # ---- quarto do bebe (x=40)
    X = 40
    room('#f6d0dc', '#f9dfe8', '#e8d8c8', '#d8c8b8', back_y=2.2, sq=0.7, ox=X)
    crib((X + 1.45, 1.35, 0), 0)
    sk = skyler(name='sk2', loc=(X - 0.2, 0.55, 0), rot=0.2)
    b = baby(sk.chest, (0, -0.24, 0.24), (0, 0, PI / 2))
    sk.arms[0].rotation_euler = aim_rot(sk, 0, chest_pt(sk, (0.02, -0.3, 0.12)))
    sk.arms[1].rotation_euler = aim_rot(sk, 1, chest_pt(sk, (-0.02, -0.3, 0.16)))
    w = walt(name='w13', loc=(X + 0.65, 0.65, 0), rot=-0.35)
    life(c, sk, 35, 0.5); life(c, w, 36)
    sk.look(1, 0.25, 0)
    fh = wf(c, 'Róli')
    smile(sk, fn + 6); smile(w, fh - 4, True)
    w.look(fn + 4, 0.15, 0.3)
    point((X, -0.5, 2.4), 90, '#fff0e8', 1.0)
    cam2, t2 = shot_cam(fn, (X + 0.15, -2.4, 1.4), (X + 0.15, 0.6, 1.15), 32)
    cam_move(cam2, t2, c, (X + 0.15, -2.4, 1.4), (X + 0.05, -2.0, 1.35), (X + 0.15, 0.6, 1.15), (X - 0.05, 0.55, 1.2), fn, c.n)


def s14(c):
    """Jane morre; voce nao faz nada (nao grafico)"""
    night_world('#0a0e1a', 0.28)
    room('#3a3a5a', None, '#5a4a3a', '#4a3a2a', back_y=2.4, side_x=-2.4, sq=0.8, trim='#2a2a3a')
    # cama de casal
    box((1.75, 2.15, 0.35), (0, 0.9, 0.175), m='#4a3020', bevel=0.03)
    box((1.62, 2.0, 0.2), (0, 0.9, 0.45), m='#e8e4dc', bevel=0.05)
    box((1.85, 0.1, 1.1), (0, 2.0, 0.55), m='#4a3020', bevel=0.03)
    for x in (-0.4, 0.4):
        box((0.6, 0.35, 0.14), (x, 1.62, 0.6), m='#f2f0ea', bevel=0.06)
    ja = jane(loc=(0.39, 0.26, 0), dress=None, jacket='#2a2a2e', shirt='#2a2a2e', pants='#3a3a4a', sleeves='#2a2a2e')
    je = jesse(loc=(-0.39, 0.26, 0), beanie=None)
    for ch in (ja, je):
        lie(ch, 0.67)
        close_eyes(ch)
        life(c, ch, 40, 0.25, blink=False)
    box((1.64, 1.38, 0.42), (0, 0.6, 0.76), m=mat('#7a5a8a', 0.85), bevel=0.14)   # cobertor
    fm = wf(c, 'morre')
    for i, f in enumerate(range(fm, fm + 16, 4)):
        key(ja.neck, 'rotation_euler', f, (0, 0, 0.12 * (1 if i % 2 else -1)))
    key(ja.neck, 'rotation_euler', fm + 20, (0, 0, 0.18))
    w = walt(loc=(1.35, 1.25, 0), rot=-1.3)
    life(c, w, 41, 0.5)
    w.brows_set(fm, 0.5)
    fn = wf(c, 'não')
    w.look(fn, 0.25, 0.1)
    window((-2.28, 0.8, 1.5), PI / 2, 1.0, 1.0, '#3a5a9a', emit=0.8)
    area((-1.5, 0.6, 2.4), (0, 0.8, -1.2), 120, 1.5, '#7a9aff')
    lamp = point((1.0, 1.9, 1.0), 25, '#ffb070', 0.2)
    box((0.4, 0.4, 0.5), (1.15, 1.9, 0.25), m='#3a2a1a')
    cam, t = camera((-0.2, -2.6, 2.3), (0.35, 0.9, 0.9), 30)
    cam_path(cam, t, [(1, (-0.3, -2.7, 2.35), (0.3, 0.9, 0.9)), (fm, (-0.1, -2.35, 2.2), (0.35, 0.95, 0.85)),
                      (c.n, (0.3, -1.9, 2.0), (0.75, 1.0, 1.0))])


def s15(c):
    """Gus Fring, dono do Los Pollos Hermanos"""
    setup_render(sky='#fff2cc')
    checker_floor('#c0392b', '#f2ead8', size=24, scale=0.6)
    pollos_store(back_y=2.5, font=BOLD)
    g = gus(loc=(0.25, 1.32, 0), rot=-0.2)
    life(c, g, 50, 0.6)
    w = walt(loc=(-0.6, -0.15, 0), rot=2.75)
    life(c, w, 51)
    fg = wf(c, 'Gás')
    smile(g, fg + 6)
    g.look(fg + 2, 0.08, 0.0)
    g.look(fg + 14, 0.0, 0.0)
    for i, x in enumerate((-2.6, 2.6)):
        table((x, -0.3, 0), (0.8, 0.8), 0.75, '#e8e2d0', '#8a8a8a', round_=True)
    sun(rot=(0.8, 0.1, 0.6), energy=2.6)
    area((0, 0.4, 3.5), (0, 0, 0), 400, 4, '#fff6e0')
    cam, t = camera((0.0, -3.2, 1.45), (-0.1, 0.8, 1.25), 30)
    cam_move(cam, t, c, (-0.05, -3.3, 1.45), (0.1, -2.5, 1.45), (-0.1, 0.8, 1.25), (0.15, 1.0, 1.35))


def s16(c):
    """por tras do balcao: o maior distribuidor; Mike"""
    night_world('#120e0a', 0.3)
    floor('#3a342e', 60)
    box((14, 0.2, 6), (0, 2.7, 3), m='#4a423a')
    rnd = random.Random(9)
    for x in (-2.7, -2.0, 2.4, 3.1):
        for k in range(3):
            b = box((0.62, 0.62, 0.5), (x, 2.2 - (0.7 if abs(x) < 2.5 else 0), 0.25 + k * 0.5), m=mat('#c8a46a', 0.8), bevel=0.02)
    box((0.62, 0.62, 0.5), (-1.35, 1.6, 0.25), m=mat('#c8a46a', 0.8), bevel=0.02)
    crystals((-1.35, 1.6, 0.5), 18, 0.22, seed=5, s=1.4)
    g = gus(loc=(-0.25, 0.55, 0), rot=0.1)
    m_ = mike(loc=(1.25, 0.7, 0), rot=-0.3)
    life(c, g, 52, 0.5); life(c, m_, 53, 0.5)
    g.brows_set(1, -0.3, 1)
    fd = wf(c, 'distribuidor')
    g.brows_set(fd, -0.45)
    gh = hand_obj(m_, 1)
    handgun(gh, (0, 0, 0.02), (PI / 2, 0, 0))
    m_.brows_set(1, -0.35, 1)
    fm = wf(c, 'Máik')
    m_.look(fm + 2, 0.05, 0.25)
    aim(m_, 1, chest_pt(m_, (0.35, -0.25, -0.1)), wf(c, 'resolve'))
    point((-0.3, -0.6, 0.4), 35, '#ff6a3a', 0.3)
    point((-0.2, -1.2, 1.8), 50, '#ffe0c0', 0.8)
    point((-1.8, 1.0, 2.5), 60, '#ffb070', 0.5)
    point((1.3, -0.4, 2.4), 60, '#ffd8a0', 0.6)
    pc = point((-1.35, 1.2, 1.0), 25, '#3cc0ff', 0.3)
    sun(rot=(0.9, 0.1, 0.5), energy=0.6, color='#ffd8b0')
    fe = wf(c, 'E')
    cam, t = camera((-0.3, -2.4, 1.45), (-0.3, 0.6, 1.35), 32)
    cam_path(cam, t, [(1, (-0.3, -2.6, 1.45), (-0.4, 0.6, 1.35)), (fe - 6, (-0.25, -2.1, 1.45), (-0.3, 0.6, 1.38)),
                      (fm + 12, (0.9, -2.0, 1.45), (1.15, 0.7, 1.38)), (c.n, (0.95, -1.7, 1.45), (1.2, 0.7, 1.4))])


def s17(c):
    """superlaboratorio: Gale aprende rapido; Gus observa"""
    superlab(back_y=3.0)
    lab_table((0, 0.2, 0), 0, 1.8, 0.8, flasks=False)
    flask((-0.75, 0.15, 0.945), '#3cc0ff'); flask((-0.45, 0.3, 0.945), '#ffd23f', s=0.85)
    book(None, (0.45, 0.2, 0.96), (PI / 2, 0, 0.2), '#2a4a7a')
    w = walt(loc=(-0.55, 0.88, 0), coat='#f2f2ee', jacket='#f2f2ee', sleeves='#f2f2ee')
    ga = gale(loc=(0.45, 0.88, 0))
    life(c, w, 54); life(c, ga, 55)
    fa = wf(c, 'aprende')
    for i, f in enumerate(range(fa, wf(c, 'O', 2) - 4, 6)):
        aim(ga, 0, (0.28, 0.32, 1.1 + 0.04 * (i % 2)), f, 3)
        aim(ga, 1, (0.62, 0.32, 1.12 - 0.04 * (i % 2)), f + 3, 3)
    ga.arm(0, wf(c, 'O', 2) + 4, (0, -0.12, 0)); ga.arm(1, wf(c, 'O', 2) + 4, (0, 0.12, 0))
    smile(ga, fa + 10)
    w.look(wf(c, 'rápido'), 0.05, -0.4)
    w.brows_set(wf(c, 'demais'), 0.35)
    fg = wf(c, 'Gás')
    g = gus(loc=(3.3, 1.75, 0), rot=-PI / 2)
    life(c, g, 56)
    g.walk(fg - 14, fg + 10, (3.3, 1.75, 0), (1.35, 1.75, 0), 2.0)
    key(g.root, 'rotation_euler', fg + 10, (0, 0, -PI / 2)); key(g.root, 'rotation_euler', fg + 18, (0, 0, -0.55))
    g.brows_set(fg + 18, -0.3)
    w.look(fg + 14, 0.0, 0.35)
    sun(rot=(0.8, 0.1, 0.6), energy=2.2)
    area((0, 0.5, 4.2), (0, 0, 0), 600, 5, '#f4fbff')
    cam, t = camera((0, -2.6, 1.45), (0, 0.8, 1.3), 32)
    cam_path(cam, t, [(1, (0, -2.7, 1.48), (0, 0.8, 1.3)), (fg - 16, (0.05, -2.4, 1.46), (0.05, 0.8, 1.3)),
                      (fg + 12, (0.55, -2.9, 1.5), (0.6, 1.1, 1.3)), (c.n, (0.55, -2.7, 1.5), (0.65, 1.1, 1.32))])


def s18(c):
    """Walt manda Jesse matar o Gale (nao grafico)"""
    night_world('#10141e', 0.3)
    floor('#2a2a30', 160)
    box((6, 0.2, 5), (0, 1.4, 2.5), m='#2a2e3a')
    w = walt(loc=(0, 0.4, 0))
    life(c, w, 57, 0.6)
    w.brows_set(1, 0.5, 1)
    ph = hand_obj(w, 1)
    phone(ph, (0, 0, 0.02), (0, 0, 0))
    upd()
    aim(w, 1, chest_pt(w, (0.31, -0.12, 0.8)), fit=True)
    fy = wf(c, 'você')
    talk(c, w, fy, wf(c, 'Guéiol') + 12, 0.8)
    point((0.6, -0.8, 1.6), 50, '#9ab4ff', 0.4)
    point((-0.8, 0.0, 2.2), 30, '#ffb070', 0.4)
    fp = wf(c, 'pele') + 8
    hide_from(w, fp + 1)
    cam, t = camera((0, -1.7, 1.45), (0, 0.4, 1.38), 35)
    cam_move(cam, t, c, (0.05, -1.75, 1.45), (0.0, -1.45, 1.42), (0, 0.4, 1.38), (0, 0.4, 1.38), 1, fp)
    # ---- apartamento do Gale (x=40)
    X = 40
    box((10, 0.2, 5), (X, 2.2, 2.5), m='#b8865a')
    box((10, 10, 0.02), (X, 0, 0.002), m='#6a4a32')
    door((X + 1.4, 2.08, 0), 0, '#5a3a22')
    tree((X - 1.8, 1.7, 0), 0.5, seed=3)
    frame_photo((X - 0.4, 2.08, 1.8), (0, 0, 0), 0.6, 0.45, '#8a5a32', bg='#e8c87a')
    ga = gale(name='g18', loc=(X + 0.55, 1.05, 0), rot=-0.95, coat=None, jacket='#5a7a5a', shirt='#e8e0d0', sleeves='#5a7a5a')
    j = jesse(name='j18', loc=(X - 0.5, 0.35, 0), rot=2.2)
    life(c, ga, 58); life(c, j, 59)
    ga.brows_set(1, 0.55, 1); j.brows_set(1, 0.6, 1)
    aim(ga, 0, chest_pt(ga, (-0.36, -0.15, 0.95)), fp + 4); aim(ga, 1, chest_pt(ga, (0.36, -0.15, 0.95)), fp + 4)
    talk(c, ga, fp + 10, c.n, 0.6)
    gh = hand_obj(j, 0)
    handgun(gh, (0, 0, 0.02), (PI / 2, 0, 0))
    tgt = chest_pt(ga, (0, 0, 0.42))
    base = aim_rot(j, 0, tgt)
    j.arms[0].rotation_euler = base
    for i, f in enumerate(range(fp + 2, c.n + 1, 3)):
        key(j.arms[0], 'rotation_euler', f, (base[0] + 0.03 * (1 if i % 2 else -1), base[1], base[2] + 0.02 * (1 if i % 3 else -1)))
    fx = min(c.n - 3, wf(c, 'Guéiol') + 12)
    spike(fx, (X - 0.1, 0.6, 1.4), '#fff2c8', 2500, 3)
    cam2, t2 = shot_cam(fp + 1, (X - 0.05, -2.4, 1.45), (X + 0.1, 0.65, 1.3), 32)
    cam_move(cam2, t2, c, (X - 0.05, -2.4, 1.45), (X + 0.05, -2.0, 1.42), (X + 0.1, 0.65, 1.3), (X + 0.2, 0.7, 1.32), fp + 1, c.n)


def s19(c):
    """bomba na cadeira de rodas do Tio Salamanca (nao grafico)"""
    setup_render(sky='#e8e0c8')
    room('#d8d8b8', '#ccccaa', '#c8c0a8', '#b8b098', back_y=2.0, sq=0.7)
    window((-1.6, 1.88, 1.6), 0, 1.0, 0.8, '#ffe8b0', emit=0.8)
    bed((2.4, 1.0, 0), 0, '#ffffff', '#c8d8b8')
    wc = wheelchair((-0.55, 0.65, 0), PI / 2, bell=True, bell_side=-1)
    ti = tio(loc=(-0.55, 0.65, 0), rot=PI / 2)
    sit_on(ti, 0.5)
    life(c, ti, 60, 0.5)
    ti.brows_set(1, -0.35, 1)
    bomb = empty('bomb', (0, 0.05, 0.24), wc)
    box((0.26, 0.12, 0.14), (0, 0, 0), m='#3a3a32', parent=bomb, bevel=0.01)
    box((0.27, 0.04, 0.05), (0, -0.03, 0.0), m='#c0392b', parent=bomb)
    led = sphere(0.018, (-0.135, 0.0, 0.05), m=mat('#ff2020', 0.3, emit=6), parent=bomb)
    g = gus(loc=(0.75, 0.65, 0), rot=-PI / 2)
    life(c, g, 61)
    upd()
    bell_w = wc.matrix_world @ Vector((-0.27, -0.27, 0.80))
    up = aim_rot(ti, 0, bell_w + Vector((0, 0, 0.18)))
    down = aim_rot(ti, 0, bell_w)
    ti.arms[0].rotation_euler = (-0.3, -0.12, 0)
    fb = wf(c, 'bomba')
    ti.arm(0, fb - 20, up)
    f = fb - 12
    while f < wf(c, 'Salamanca') + 6:
        key(ti.arms[0], 'rotation_euler', f, down); key(ti.arms[0], 'rotation_euler', f + 4, up)
        f += 8
    pl = point((-0.55, 0.9, 0.4), 0, '#ff2020', 0.1)
    for i, ff in enumerate(range(fb - 4, c.n, 6)):
        pl.data.energy = 12 if i % 2 == 0 else 0; pl.data.keyframe_insert('energy', frame=ff)
    g.brows_set(fb + 6, 0.5)
    g.look(fb + 4, 0.25, 0.0)
    fx = wf(c, 'Salamanca') + 8
    fire = empty('fire', (-0.4, 0.6, 0.9))
    sphere(1, (0, 0, 0), (1, 1, 1), mat('#ffb02a', 0.6, emit=6), fire, seg=24)
    sphere(1, (0.4, -0.3, 0.3), (0.7, 0.7, 0.7), mat('#ff6a1a', 0.6, emit=5), fire, seg=24)
    sphere(1, (-0.4, -0.2, -0.2), (0.8, 0.8, 0.8), mat('#ffd84a', 0.6, emit=7), fire, seg=24)
    fire.scale = (0.01, 0.01, 0.01)
    key(fire, 'scale', fx - 1, (0.0, 0.0, 0.0), 'CONSTANT'); key(fire, 'scale', fx, (0.2, 0.2, 0.2))
    key(fire, 'scale', fx + 6, (2.2, 2.2, 2.2))
    for ch in (ti, g):
        hide_from(ch, fx + 4)
    spike(fx, (-0.2, -0.2, 1.2), '#ffb060', 2500, 12, 1.0)
    puffs((-0.4, 0.6, 1.2), fx + 4, c.n, '#3a3a3a', n=6, seed=8, rise=1.5, s=0.9, spread=0.8, every=2)
    sun(rot=(0.8, 0.1, 0.6), energy=2.6)
    point((0, -0.6, 2.3), 60, '#fff2dc', 1.0)
    cam, t = camera((0, -2.5, 1.3), (0, 0.65, 1.0), 32)
    cam_path(cam, t, [(1, (0.05, -2.6, 1.32), (0.05, 0.65, 1.05)), (fb - 2, (0.0, -2.3, 1.28), (0.0, 0.65, 1.0)),
                      (fx - 2, (-0.35, -1.6, 1.15), (-0.5, 0.5, 0.85)), (c.n, (-0.4, -1.75, 1.2), (-0.5, 0.5, 0.9))])


def s20(c):
    """o chefao e voce; Mike no rio (nao grafico)"""
    setup_render(sky='#ffb26a', sky_strength=0.8)
    floor('#2a2622', 40)
    box((12, 0.2, 7), (0, 2.2, 3.5), m='#1e1c1e')
    money_pile((-1.25, 1.4, 0), 1.2, 0.8, 1.0, seed=2)
    money_pile((1.3, 1.4, 0), 1.2, 0.8, 1.3, seed=3)
    meth_tray((0, 1.25, 0.0))
    crystals((0.0, 1.25, 0.07), 10, 0.2, seed=6, s=1.2)
    h = heisenberg(loc=(0, 0.35, 0))
    life(c, h, 62, 0.6)
    h.brows_set(1, -0.3, 1)
    fc = wf(c, 'chefão')
    key(h.mouth, 'scale', fc, (1.0, 1, 0.35)); key(h.mouth, 'scale', fc + 8, (1.45, 1, 0.45))
    point((0, -0.8, 0.5), 35, '#ffd8a0', 0.4)
    point((0, -1.2, 2.4), 90, '#fff0dc', 0.8)
    point((0, 1.0, 0.5), 30, '#3cc0ff', 0.3)
    point((-1.6, 0.0, 2.6), 60, '#ffb070', 0.5)
    fv = wf(c, 'Você', 2)
    cam, t = camera((0, -2.3, 1.05), (0, 0.4, 1.4), 30)
    cam_move(cam, t, c, (0.1, -2.5, 1.0), (0.0, -2.0, 1.1), (0, 0.4, 1.4), (0, 0.4, 1.42), 1, fv - 3)
    # ---- rio (x=40)
    X = 40
    box((30, 30, 0.02), (X, 0, 0.005), m=mat('#7a8a4a', 0.85))
    box((30, 4.0, 0.03), (X, 3.6, 0.012), m=mat('#3a7aa8', 0.15, spec=0.9))
    for i, (x, y, r) in enumerate(((-1.6, 1.3, 0.3), (1.7, 1.5, 0.35), (2.6, 0.6, 0.25))):
        sphere(1, (X + x, y, 0), (r, r * 0.8, r * 0.7), mat('#8a8278', 0.9))
    for i, x in enumerate((-4, -2.6, 2.8, 4.2)):
        tree((X + x, 6.5, 0), 1.2, '#5a8a3a', seed=i)
    sphere(1, (X + 0.2, 1.05, 0), (0.42, 0.36, 0.42), mat('#9a9288', 0.9))
    mk = mike(name='mk20', loc=(X + 0.2, 1.08, 0), rot=PI)
    sit_on(mk, 0.42)
    life(c, mk, 63, 0.4)
    w = heisenberg(name='h20', loc=(X - 0.65, 0.2, 0), rot=2.35, hat=None)
    life(c, w, 64, 0.5)
    gh = hand_obj(w, 0)
    handgun(gh, (0, 0, 0.02), (PI / 2, 0, 0))
    w.arms[0].rotation_euler = (0.15, -0.12, 0)
    fm = wf(c, 'mata')
    spike(fm + 4, (X - 0.3, 0.6, 1.0), '#fff2c8', 2000, 3)
    mk.look(fm + 14, 0.45, 0.0)
    w.brows_set(fm, 0.15)
    w.look(fm + 10, 0.2, 0.0)
    sun(rot=(1.25, 0.0, 0.9), energy=3.2, color='#ffc890')
    cam2, t2 = shot_cam(fv - 2, (X + 0.5, -2.5, 1.45), (X - 0.25, 0.75, 1.0), 30)
    cam_move(cam2, t2, c, (X + 0.5, -2.5, 1.45), (X + 0.45, -2.2, 1.4), (X - 0.25, 0.75, 1.0), (X - 0.2, 0.8, 0.95), fv - 2, c.n)


def s21(c):
    """tanto dinheiro que a Skyler nao consegue contar"""
    setup_render(sky='#c8ccd0')
    floor('#8a8a86', 40)
    stripes_wall('#9aa0a6', '#8a9096', w=8, h=4, n=20, loc=(0, 2.2, 0), horizontal=False)
    box((0.2, 4, 4), (-2.5, 0.4, 2), m='#9aa0a6'); box((0.2, 4, 4), (2.5, 0.4, 2), m='#9aa0a6')
    money_pile((0, 1.45, 0), 1.8, 1.0, 1.2, seed=4)
    sk = skyler(loc=(1.05, 0.35, 0), rot=-0.35)
    w = walt(loc=(-1.05, 0.35, 0), rot=0.35)
    life(c, sk, 65); life(c, w, 66)
    mh = hand_obj(sk, 0)
    ms = money_stack((0, 0, -0.05), 2, mh)
    ms.rotation_euler = (PI / 2, 0, 0)
    aim(sk, 0, chest_pt(sk, (-0.05, -0.35, 0.3)))
    for i, f in enumerate(range(8, wf(c, 'nem') - 4, 8)):
        key(sk.neck, 'rotation_euler', f, (0.12, 0, 0.05 * (1 if i % 2 else -1)))
    fn = wf(c, 'nem')
    hide_between(ms, None, fn + 2)
    aim(sk, 0, chest_pt(sk, (-0.3, -0.12, 0.88)), fn + 2); aim(sk, 1, chest_pt(sk, (0.3, -0.12, 0.88)), fn + 2)
    sk.brows_set(fn, 0.5)
    key(sk.mouth, 'scale', fn, (1, 1, 0.35)); key(sk.mouth, 'scale', fn + 6, (0.9, 1, 1.4))
    smile(w, wf(c, 'dinheiro') + 6)
    point((0, 0.2, 3.3), 120, '#fff6e0', 0.4)
    sun(rot=(0.8, 0.1, 0.6), energy=2.4)
    cam, t = camera((0, -3.4, 1.5), (0, 0.8, 1.15), 28)
    cam_move(cam, t, c, (0, -3.45, 1.52), (0.15, -2.9, 1.45), (0, 0.8, 1.15), (0.25, 0.75, 1.2))


def s22(c):
    """Hank no banheiro acha o livro: dedicatoria pra W.W."""
    setup_render(sky='#e8f4f6')
    room('#d8eef0', '#c8e4e8', '#f2f2f2', '#d8d8d8', back_y=1.7, sq=0.3, trim='#9fc8d0')
    box((0.2, 6, 5), (-1.3, 0.0, 2.5), m='#d8eef0'); box((0.2, 6, 5), (1.3, 0.0, 2.5), m='#d8eef0')
    toilet((0, 1.25, 0), 0)
    box((0.5, 0.06, 0.6), (0.8, 1.66, 1.6), m=mat('#bfe8ff', 0.05, spec=1.0, emit=0.2))
    hk = hank(loc=(0, 1.2, 0), badge=False)
    sit_on(hk, 0.435)
    life(c, hk, 67, 0.4)
    bk = book(None, (0, 0.77, 1.0), (-0.35, 0, 0), '#3a7a4a', 1.2)
    aim(hk, 0, (-0.13, 0.74, 0.98)); aim(hk, 1, (0.13, 0.74, 0.98))
    hk.look(1, 0.3, 0)
    fd = wf(c, 'dedicatória')
    hk.brows_set(wf(c, 'livro'), 0.2)
    hk.brows_set(fd - 2, 0.55)
    sun(rot=(0.8, 0.1, 0.5), energy=2.4)
    point((0, 0.0, 2.4), 80, '#ffffff', 0.6)
    cam, t = camera((0, -1.6, 1.4), (0, 1.0, 1.0), 30)
    cam_move(cam, t, c, (0, -1.7, 1.45), (0, -1.25, 1.4), (0, 1.0, 1.0), (0, 1.0, 1.05), 1, fd - 3)
    # ---- detalhe: livro aberto (x=40)
    X = 40
    box((3, 3, 0.1), (X, 0, 0.7), m='#8a5a32')
    for sx in (-1, 1):
        box((0.42, 0.56, 0.03), (X + sx * 0.215, 0, 0.77), rot=(0, -sx * 0.06, 0), m='#3a7a4a', bevel=0.005)
        box((0.4, 0.54, 0.02), (X + sx * 0.205, 0, 0.79), rot=(0, -sx * 0.06, 0), m='#f6f0dc')
    text3d('Ao meu outro\nW.W. favorito.\n\n— G.B.', (X + 0.2, 0, 0.805), (0, 0, 0), size=0.032, m=mat('#2a2a6a', 0.6), font=SERIF, extrude=0.001, bevel=0.0)
    for i in range(6):
        box((0.3, 0.004, 0.003), (X - 0.2, 0.15 - i * 0.06, 0.803), m='#8a8a8a')
    point((X, -0.2, 1.5), 60, '#fff6e0', 0.5)
    cam2, t2 = shot_cam(fd - 2, (X + 0.05, -0.45, 1.6), (X + 0.05, 0.0, 0.8), 35)
    cam_move(cam2, t2, c, (X + 0.05, -0.45, 1.6), (X + 0.18, -0.3, 1.32), (X + 0.05, 0.0, 0.8), (X + 0.2, 0.02, 0.8), fd - 2, c.n)


def s23(c):
    """Heisenberg dentro da familia"""
    setup_render(sky='#a8dcff')
    floor('#8ac46a', 160)
    house_ext((0, 6.5, 0), wall='#e8dcc0', roof='#7a5a4a', night=False)
    box((10, 0.1, 1.0), (0, 3.3, 0.5), m='#c8a87a')
    cyl(0.3, 0.6, (2.3, 1.8, 0.3), m='#2a2a2a'); cyl(0.32, 0.08, (2.3, 1.8, 0.62), m='#3a3a3a')
    w = walt(loc=(0, 0.0, 0))
    h = heisenberg(loc=(0, 0.0, 0))
    sk = skyler(loc=(0.62, 0.45, 0), rot=-0.15)
    hk = hank(loc=(-0.65, 0.45, 0), rot=0.15)
    jr = walt_jr(loc=(1.12, 0.95, 0), rot=-0.25)
    ma = marie(loc=(-1.12, 0.95, 0), rot=0.25)
    for i, ch in enumerate((w, h, sk, hk, jr, ma)):
        life(c, ch, 70 if i < 2 else 70 + i, 0.7)
    for ch in (sk, hk, jr, ma):
        smile(ch, 4)
    crutches(jr)
    fh = wf(c, 'Raisenberg')
    hide_from(w, fh); show_from(h, fh)
    h.brows_set(fh + 2, -0.4, 1)
    key(h.mouth, 'scale', fh + 10, (1.0, 1, 0.35)); key(h.mouth, 'scale', fh + 18, (1.35, 1, 0.45))
    spike(fh, (0, -0.6, 1.5), '#ff3a2a', 1500, 10)
    pr = point((0, 0.6, 2.0), 0, '#ff2a2a', 0.4)
    pr.data.keyframe_insert('energy', frame=fh); pr.data.energy = 90; pr.data.keyframe_insert('energy', frame=fh + 6)
    ff = wf(c, 'família')
    hk.look(ff, 0, -0.45)
    hk.brows_set(ff, 0.2)
    sun(rot=(0.8, 0.1, 0.6), energy=3.4)
    cam, t = camera((0, -3.4, 1.5), (0, 0.5, 1.25), 30)
    cam_path(cam, t, [(1, (0, -3.6, 1.5), (0, 0.5, 1.25)), (fh, (0, -3.2, 1.5), (0, 0.4, 1.28)), (c.n, (0, -2.2, 1.45), (0, 0.2, 1.38))])


def s24(c):
    """Hank morto pela gangue do Jack (nao grafico); Marie viuva; dinheiro roubado"""
    desert_world(sky='#ffd9a0', sand='#e2b07a', back=22, n_cactus=6, cact_y=(6, 14))
    jk = jack(loc=(-0.75, 0.35, 0), rot=1.25)
    td = todd(loc=(-0.45, 1.3, 0), rot=1.2)
    hk = hank(loc=(0.85, 0.55, 0), rot=-1.3, badge=False)
    wk = walt(loc=(0.25, 1.65, 0), rot=-0.3)
    wk.kneel()
    for i, ch in enumerate((jk, td, hk, wk)):
        life(c, ch, 80 + i)
    gh = hand_obj(jk, 1)
    handgun(gh, (0, 0, 0.02), (PI / 2, 0, 0))
    aim(jk, 1, chest_pt(hk, (0, 0, 0.45)), 4)
    jk.brows_set(1, -0.3, 1)
    hk.brows_set(1, -0.45, 1)
    talk(c, hk, wf(c, 'deserto'), wf(c, 'é') - 2, 0.8)
    wk.brows_set(1, 0.6, 1)
    aim(wk, 0, chest_pt(wk, (-0.15, -0.5, 0.6)), 6); aim(wk, 1, chest_pt(wk, (0.15, -0.5, 0.6)), 6)
    fm = wf(c, 'morto') + 6
    spike(fm, (0.0, 0.0, 1.4), '#fff2c8', 2500, 3)
    hide_from(hk, fm + 2)
    wk.look(fm + 2, 0.35, 0)
    smile(td, wf(c, 'Tódi') + 4)
    fa = wf(c, 'A')
    sun(rot=(1.0, 0.0, -0.7), energy=3.6, color='#ffe2b8')
    cam, t = camera((0, -3.2, 1.4), (0, 0.8, 1.2), 32)
    cam_move(cam, t, c, (0.05, -3.3, 1.42), (0.0, -3.0, 1.4), (0.0, 0.8, 1.2), (0.0, 0.8, 1.2), 1, fm)
    cam1b, t1b = shot_cam(fm + 2, (0.6, -1.8, 1.45), (-0.6, 0.85, 1.35), 32)
    cam_move(cam1b, t1b, c, (0.6, -1.8, 1.45), (0.45, -1.55, 1.45), (-0.6, 0.85, 1.35), (-0.6, 0.85, 1.38), fm + 2, fa - 1)
    # ---- Marie (x=40)
    X = 40
    box((10, 0.2, 5), (X, 1.8, 2.5), m='#8a6aa8')
    box((10, 10, 0.02), (X, 0, 0.002), m='#5a4a5a')
    window((X - 0.9, 1.68, 1.6), 0, 1.0, 1.0, '#6a7a9a', emit=0.5)
    frame_photo((X + 0.9, 1.68, 1.7), (0, 0, 0), 0.45, 0.55, '#c8a24a', bg='#c8a87a')
    ma = marie(name='ma24', loc=(X, 0.6, 0))
    life(c, ma, 85, 0.5)
    ma.brows_set(fa, 0.6)
    ma.look(fa + 6, 0.3, 0)
    aim(ma, 0, chest_pt(ma, (0.08, -0.3, 0.55)), fa + 8)
    for i in range(3):
        for sx in (-1, 1):
            tr = sphere(1, (sx * 0.1, -0.235, 0.03), (0.012, 0.01, 0.018), mat('#9fd8ff', 0.1, emit=0.6), ma.head, seg=10)
            f0 = fa + 10 + i * 12 + (4 if sx > 0 else 0)
            key(tr, 'location', f0, (sx * 0.1, -0.235, 0.03)); key(tr, 'location', f0 + 12, (sx * 0.12, -0.21, -0.12))
            hide_between(tr, f0, f0 + 12)
    point((X, -0.6, 2.0), 50, '#c8b8ff', 0.6)
    point((X - 0.8, 1.2, 1.8), 30, '#8a9aff', 0.5)
    fd = wf(c, 'e')
    cam2, t2 = shot_cam(fa, (X, -1.9, 1.45), (X, 0.6, 1.35), 35)
    cam_move(cam2, t2, c, (X, -1.9, 1.45), (X, -1.5, 1.45), (X, 0.6, 1.35), (X, 0.6, 1.38), fa, fd - 1)
    # ---- dinheiro roubado (x=80)
    X = 80
    box((60, 60, 0.02), (X, 0, 0.004), m=mat('#e2b07a', 0.9))
    trk = empty('truck', (X + 0.6, 2.0, 0))
    m_ = mat('#6a6a5a', 0.5)
    box((1.6, 1.8, 1.2), (1.8, 0, 1.1), m=m_, parent=trk, bevel=0.1)
    box((3.0, 1.9, 0.5), (-0.6, 0, 0.75), m=m_, parent=trk, bevel=0.05)
    for sy in (-1, 1):
        box((3.0, 0.08, 0.45), (-0.6, sy * 0.92, 1.2), m=m_, parent=trk)
        for x in (-1.3, 1.6):
            cyl(0.38, 0.25, (x, sy * 0.85, 0.38), (PI / 2, 0, 0), m='#1a1a1a', parent=trk)
    box((0.04, 1.5, 0.5), (2.62, 0, 1.35), m=mat('#1a2a3a', 0.05, spec=1.0), parent=trk)
    for i, (x, y) in enumerate(((-1.5, -0.45), (-0.9, 0.45), (-0.3, -0.45), (0.3, 0.45))):
        cyl(0.3, 0.75, (x, y, 1.38), m='#2f5a8a', parent=trk)
        cyl(0.27, 0.03, (x, y, 1.76), m='#4fae5a', parent=trk)
    fr = fd + 6
    key(trk, 'location', fr, (X + 0.6, 2.0, 0)); key(trk, 'location', c.n + 10, (X + 6.5, 2.0, 0))
    for i, (mx, mw, mh) in enumerate(((-14, 10, 5), (-2, 12, 6.5), (11, 9, 4.5))):
        box((mw, 5, mh), (X + mx, 24, mh / 2), m=mat('#c8724a', 0.85), bevel=0.4)
    cactus((X - 3.2, 6, 0), 1.1, 1); cactus((X + 3.8, 8, 0), 1.0, 2)
    puffs((X - 1.2, 2.0, 0.3), fr, c.n, '#d8c0a0', n=8, seed=9, rise=0.8, s=0.4, spread=0.3, every=3)
    w3 = walt(name='w24', loc=(X - 0.9, -0.1, 0), rot=0.2)
    w3.kneel()
    life(c, w3, 86)
    w3.brows_set(fd, 0.6)
    w3.look(fr, 0, -0.5)
    cam3, t3 = shot_cam(fd, (X - 0.5, -3.2, 1.45), (X - 0.1, 1.2, 1.0), 28)
    cam_move(cam3, t3, c, (X - 0.5, -3.2, 1.45), (X - 0.4, -3.0, 1.45), (X - 0.1, 1.2, 1.0), (X + 0.15, 1.3, 1.0), fd, c.n)


def s25(c):
    """cabana na neve; o filho quer que voce morra"""
    setup_render(sky='#c8d8e8', sky_strength=0.9)
    floor('#f4f8fc', 160)
    cabin((0.7, 3.4, 0), 0)
    for i, (x, y, s) in enumerate(((-2.4, 3.0, 1.3), (-1.6, 5.5, 1.5), (3.2, 2.6, 1.2), (2.6, 5.8, 1.6), (-3.4, 1.6, 1.0))):
        snow_pine((x, y, 0), s)
    snowfall(70, (0.0, 0.3), (3.6, 3.0), 3.2, 1, c.n, seed=2, avoid=[(-0.55, 0.55, 0.5)])
    w = walt(loc=(-0.55, 0.55, 0), rot=0.15, beard='#a8a39a', jacket='#3a3a42', sleeves='#3a3a42', pants='#2a2a30', beanie='#2a2a2e', hair_style='bald')
    life(c, w, 90, 0.6)
    w.brows_set(1, 0.35, 1)
    aim(w, 0, chest_pt(w, (-0.08, -0.26, 0.3))); aim(w, 1, chest_pt(w, (0.08, -0.26, 0.26)))
    for k in range(5):
        f0 = 12 + k * 18
        puffs((-0.55 + 0.04, 0.2, 1.3), f0, f0 + 2, '#ffffff', n=1, seed=k, rise=0.35, s=0.07, spread=0.05)
    fe = wf(c, 'E')
    sun(rot=(0.9, 0.1, 0.6), energy=2.2, color='#e8f0ff')
    point((-0.1, 1.85, 1.3), 60, '#ffb060', 0.4)
    cam, t = camera((0, -3.4, 1.6), (0.2, 1.2, 1.3), 30)
    cam_move(cam, t, c, (0.1, -3.6, 1.7), (0.0, -2.8, 1.5), (0.2, 1.3, 1.35), (0.0, 1.0, 1.3), 1, fe - 1)
    # ---- Walter Jr ao telefone (x=40)
    X = 40
    box((10, 0.2, 5), (X, 1.6, 2.5), m='#d8d0b0')
    box((10, 10, 0.02), (X, 0, 0.002), m='#8a7a6a')
    corkboard((X - 0.6, 1.48, 1.7), 1.4, 0.9)
    jr = walt_jr(name='jr25', loc=(X, 0.5, 0))
    life(c, jr, 91, 0.8)
    ph = hand_obj(jr, 1)
    phone(ph, (0, 0, 0.02))
    aim(jr, 1, chest_pt(jr, (0.3, -0.12, 0.74)), fit=True)
    crutches_side = jr.arms[0]
    jr.brows_set(fe, -0.5)
    talk(c, jr, wf(c, 'diz'), c.n, 1.5)
    point((X, -0.6, 2.0), 60, '#fff2dc', 0.8)
    cam2, t2 = shot_cam(fe, (X, -1.9, 1.35), (X, 0.5, 1.2), 35)
    cam_path(cam2, t2, [(fe, (X, -1.9, 1.35), (X, 0.5, 1.2)), (wf(c, 'quer'), (X, -1.6, 1.33), (X, 0.5, 1.22)), (c.n, (X, -1.05, 1.3), (X, 0.5, 1.25))])


def s26(c):
    """volta final: Lydia envenenada, fim da gangue, Jesse livre (nao grafico)"""
    night_world('#141a2a', 0.35)
    floor('#3a3a40', 220)
    sedan((1.6, 3.6, 0), 0, '#5a6a7a')
    for x in (-3, 3):
        cyl(0.05, 3.2, (x, 4.5, 1.6), m='#5a5a5a'); sphere(0.15, (x, 4.3, 3.2), m=mat('#ffd890', 0.3, emit=4))
    w = walt_final(loc=(0.3, 3.4, 0), rot=0)
    life(c, w, 95)
    fv = wf(c, 'última')
    w.walk(4, fv, (0.25, 3.4, 0), (0.0, 0.6, 0), 1.8)
    w.brows_set(fv, -0.35)
    point((0, -0.6, 2.0), 60, '#c8d0ff', 0.8)
    point((0.8, 4.0, 3.0), 300, '#ffd890', 1.0)
    fl = wf(c, 'Envenena')
    cam, t = camera((0, -2.5, 1.45), (0.1, 1.5, 1.35), 32)
    cam_move(cam, t, c, (0.0, -2.6, 1.45), (0.0, -2.2, 1.42), (0.1, 2.0, 1.35), (0.0, 0.6, 1.42), 1, fl - 1)
    # ---- Lydia no cafe (x=40)
    X = 40
    box((10, 0.2, 5), (X, 1.8, 2.5), m='#d8c8a8')
    box((10, 10, 0.02), (X, 0, 0.002), m='#8a6a4a')
    window((X - 0.9, 1.68, 1.7), 0, 1.2, 0.9, '#cfe8ff', emit=0.6)
    table((X, 0.3, 0), (0.7, 0.7), 0.75, '#f2f0ea', '#5a5a5a', round_=True)
    chair((X, 1.05, 0), 0, '#3a3a42')
    ly = lydia(loc=(X, 1.05, 0))
    sit_on(ly, 0.48)
    life(c, ly, 96)
    cp = hand_obj(ly, 1)
    teacup((0, 0, 0.0), 0.8, cp, '#f2f2ee')
    ly.arms[1].rotation_euler = aim_rot(ly, 1, chest_pt(ly, (0.14, -0.38, 0.32)))
    fly = wf(c, 'Lídia')
    aim(ly, 1, chest_pt(ly, (0.06, -0.36, 0.62)), fly - 6)
    aim(ly, 1, chest_pt(ly, (0.14, -0.38, 0.32)), fly + 8)
    ly.brows_set(fly + 8, 0.5)
    ly.look(fly + 10, 0.2, 0.1)
    box((0.05, 0.03, 0.01), (X + 0.12, 0.25, 0.785), m='#7ab86a')
    point((X, -0.5, 2.2), 70, '#fff2dc', 0.8)
    fg = wf(c, 'acaba')
    cam2, t2 = shot_cam(fl, (X, -1.7, 1.45), (X, 0.8, 1.05), 32)
    cam_move(cam2, t2, c, (X, -1.7, 1.45), (X, -1.45, 1.4), (X, 0.8, 1.05), (X, 0.85, 1.1), fl, fg - 1)
    # ---- complexo da gangue (x=80)
    X = 80
    box((12, 0.3, 4), (X, 3.2, 2.0), m='#6a5a4a')
    wins = []
    for i, x in enumerate((-2.0, 0.0, 2.0)):
        wins.append(window((X + x, 3.03, 1.7), 0, 1.0, 0.8, '#ffb040', emit=0.3))
    car = sedan((X + 0.3, 0.6, 0), 0, '#2a2a30')
    box((1.4, 0.1, 0.5), (X + 0.3, 2.8, 1.1), rot=(-0.6, 0, 0), m='#2a2a30')
    gun = box((0.1, 0.5, 0.1), (X + 0.3, 2.75, 0.95), m='#1a1a1a')
    fls = []
    rnd = random.Random(12)
    pin = point((X, 3.8, 1.8), 0, '#ffa040', 1.0)
    pm = point((X + 0.3, 3.3, 1.0), 0, '#ffe08a', 0.3)
    for f in range(fg, wf(c, 'liberta') - 2, 2):
        pin.data.energy = rnd.choice((0, 800, 1500)); pin.data.keyframe_insert('energy', frame=f)
        pm.data.energy = rnd.choice((0, 400)); pm.data.keyframe_insert('energy', frame=f)
    pin.data.energy = 0; pin.data.keyframe_insert('energy', frame=wf(c, 'liberta') - 2)
    pm.data.energy = 0; pm.data.keyframe_insert('energy', frame=wf(c, 'liberta') - 2)
    fj = wf(c, 'liberta')
    cam3, t3 = shot_cam(fg, (X - 2.2, -3.2, 1.6), (X + 0.2, 1.6, 1.2), 30)
    cam_move(cam3, t3, c, (X - 2.2, -3.2, 1.6), (X - 1.9, -2.8, 1.55), (X + 0.2, 1.6, 1.2), (X + 0.3, 1.8, 1.25), fg, fj - 1)
    # ---- Jesse livre (x=120)
    X = 120
    box((10, 0.2, 5), (X, 1.8, 2.5), m='#5a5a60')
    box((10, 10, 0.02), (X, 0, 0.002), m='#4a4a4e')
    for x in (-1.6, 1.6):
        lab_tank((X + x, 1.2, 0), 0.4, 1.8)
    je = jesse(name='j26', loc=(X, 0.45, 0), beanie=None, hair_style='cas', beard='#7a5a3a', jacket='#4a4a42', sleeves='#4a4a42')
    life(c, je, 97)
    je.brows_set(fj, 0.5)
    for s_ in (0, 1):
        je.arms[s_].rotation_euler = aim_rot(je, s_, chest_pt(je, ((-1 if s_ == 0 else 1) * 0.06, -0.38, 0.05)))
    upd()
    hl = je.arms[0].matrix_world @ Vector((0, 0, -0.44)); hr = je.arms[1].matrix_world @ Vector((0, 0, -0.44))
    links = []
    for i in range(5):
        u = (i + 0.5) / 5
        p = hl.lerp(hr, u) - Vector((0, 0, 0.04 * math.sin(u * PI)))
        lk = torus(0.025, 0.006, tuple(p), (0, PI / 2 if i % 2 else 0, 0), m=mat('#b8bcc4', 0.25, metal=0.9))
        links.append(lk)
    ff = fj + 8
    for i, lk in enumerate(links):
        z0 = lk.location.z
        key(lk, 'location', ff, tuple(lk.location)); key(lk, 'location', ff + 10, (lk.location.x + 0.05 * (i - 2), lk.location.y - 0.1, 0.01))
    aim(je, 0, chest_pt(je, (-0.45, -0.15, 0.95)), ff + 10); aim(je, 1, chest_pt(je, (0.45, -0.15, 0.95)), ff + 10)
    key(je.mouth, 'scale', ff + 8, (1, 1, 0.35)); key(je.mouth, 'scale', ff + 14, (1.1, 1, 1.5))
    je.look(ff + 10, -0.25, 0)
    point((X, -0.6, 2.2), 70, '#fff0dc', 0.8)
    point((X, 1.0, 2.6), 60, '#9ab4ff', 0.6)
    cam4, t4 = shot_cam(fj, (X, -2.0, 1.45), (X, 0.45, 1.3), 32)
    cam_move(cam4, t4, c, (X, -2.0, 1.45), (X, -2.3, 1.5), (X, 0.45, 1.3), (X, 0.45, 1.35), fj, c.n)


def s27(c):
    """a verdade para a Skyler"""
    setup_render(sky='#ffe8c8')
    checker_floor('#c8b8a0', '#b8a890', size=24, scale=0.6)
    kitchen(back_y=2.2, wall='#c8c0b0')
    sk = skyler(loc=(0.6, 0.45, 0), rot=-0.75, hair='#c8a060', jacket='#5a6a7a', dress='#5a6a7a')
    w = walt_final(loc=(-0.6, 0.45, 0), rot=0.75)
    life(c, sk, 98); life(c, w, 99)
    sk.brows_set(1, 0.35, 1)
    fe = wf(c, 'eu')
    talk(c, w, fe, c.n, 0.9)
    w.brows_set(fe, 0.2)
    w.look(wf(c, 'gostava'), -0.05, 0.1)
    sk.brows_set(fe + 10, 0.55)
    sk.look(wf(c, 'bom'), 0.15, 0)
    sun(rot=(0.8, 0.1, 0.6), energy=2.2)
    point((0, -0.4, 2.3), 70, '#ffe0b8', 1.0)
    cam, t = camera((0, -2.9, 1.4), (0, 0.5, 1.25), 32)
    cam_path(cam, t, [(1, (0, -2.95, 1.42), (0, 0.5, 1.25)), (fe - 6, (0.0, -2.6, 1.42), (0, 0.5, 1.28)),
                      (c.n, (-0.4, -1.55, 1.42), (-0.55, 0.45, 1.38))])


def s28(c):
    """morre no laboratorio, o unico lugar onde se sentiu vivo"""
    setup_render(sky='#2a2e36', sky_strength=0.5)
    checker_floor('#8a8a86', '#7a7a76', size=40, scale=0.9)
    for i, (x, y) in enumerate(((-2.0, 2.4), (2.0, 2.6), (-2.6, 0.2), (2.7, -0.4))):
        lab_tank((x, y, 0), 0.5, 2.0)
    lab_table((1.4, 1.2, 0), 0.3, 1.4, 0.7, flasks=True, seed=4)
    meth_tray((-1.0, -0.6, 0))
    w = walt_final(loc=(0, -0.55, 0))
    lie(w, 0.12)
    life(c, w, 100, 0.25, blink=False)
    for a in w.arms:
        a.rotation_euler = (0, a.rotation_euler[1] * 2.5, 0)
    fv = wf(c, 'vivo')
    smile(w, fv + 4)
    w.brows_set(1, 0.15, 1)
    w.blink([40, 120])
    police_lights(wf(c, 'único'), c.n, (-3.5, 3.0, 1.2), (3.5, 3.0, 1.2), 250, 9)
    area((0, -0.2, 4.0), (0, 0, 0), 300, 2.5, '#e8f0ff')
    ka = point((0, 0.6, 1.2), 40, '#fff0dc', 0.6)
    ka.data.keyframe_insert('energy', frame=fv + 30); ka.data.energy = 5; ka.data.keyframe_insert('energy', frame=c.n)
    hy = -0.55 + 1.34
    cam, t = camera((0, hy - 0.45, 1.35), (0, hy, 0.25), 35)
    cam_path(cam, t, [(1, (0.0, hy - 0.45, 1.3), (0, hy - 0.02, 0.26)), (fv - 10, (0.0, hy - 0.9, 2.6), (0, hy - 0.25, 0.25)),
                      (c.n, (0.0, hy - 2.2, 7.0), (0, hy - 0.6, 0.2))])


SHOTS = {f's{i:02d}': globals()[f's{i:02d}'] for i in range(1, 29)}
