# Game of Thrones - definicao de cada shot (cenario + personagens + animacao + camera)
# Convencao: personagem com rot=θ olha para (sin θ, -cos θ). θ=0 -> camera (-Y); θ=+π/2 -> +X; θ=-π/2 -> -X.
# Cadeiras/cadeira de rodas/vaso usam o mesmo rot de quem senta. Eventos sincronizados com as palavras (wf).
import bpy, math, random, json, os, re
from mathutils import Vector, Matrix
from lib import *
from props import *
from got import *

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
    key(ch.mouth, 'scale', f - 6, val_at(ch.mouth, 'scale', f - 6)); key(ch.mouth, 'scale', f, (1.6 if big else 1.4, 1, 0.55))

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

def _snapshot():
    out = []
    for o in bpy.data.objects:
        if o.animation_data and o.animation_data.action:
            out.append((o, tuple(o.location), tuple(o.rotation_euler), tuple(o.scale)))
    return out

def _restore(snap):
    for o, l, r, s_ in snap:
        o.location, o.rotation_euler, o.scale = l, r, s_

def aim_rot(ch, side, target, frame=None):
    """rotacao do braco para a mao apontar para target (mundo). Se o boneco estiver escondido (escala 0),
    avalia num frame em que esta visivel e depois restaura os valores (sem mexer nas chaves)."""
    upd()
    a = ch.arms[side]
    pm = a.parent.matrix_world.copy()
    if abs(pm.to_3x3().determinant()) < 1e-12:
        sc = bpy.context.scene; cur = sc.frame_current
        snap = _snapshot()
        for k in range(1, 2000, 3):
            sc.frame_set(k); pm = a.parent.matrix_world.copy()
            if abs(pm.to_3x3().determinant()) > 1e-12:
                break
        sc.frame_current = cur
        _restore(snap); upd()
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



# ----------------------------------------------------------------- helpers GOT
def kneel_at(ch, z=0.0):
    ch.kneel()
    ch.root.location.z = z

def fall_back(ch, f0, dur=10, z=0.13, tilt=0.1):
    """cai de costas (cabeca para +Y local do mundo apos rot)"""
    r = val_at(ch.root, 'rotation_euler', f0); l = val_at(ch.root, 'location', f0)
    key(ch.root, 'rotation_euler', f0, r); key(ch.root, 'location', f0, l)
    key(ch.root, 'rotation_euler', f0 + dur, (-(PI / 2 - tilt), r[1], r[2]))
    key(ch.root, 'location', f0 + dur, (l[0], l[1], z))

def fall_fwd(ch, f0, dur=10, z=0.13, tilt=0.1):
    r = val_at(ch.root, 'rotation_euler', f0); l = val_at(ch.root, 'location', f0)
    key(ch.root, 'rotation_euler', f0, r); key(ch.root, 'location', f0, l)
    key(ch.root, 'rotation_euler', f0 + dur, ((PI / 2 - tilt), r[1], r[2]))
    key(ch.root, 'location', f0 + dur, (l[0], l[1], z))

def arms_down(ch, f, ease=6):
    ch.arm(0, f, (0, -0.12, 0), ease=ease); ch.arm(1, f, (0, 0.12, 0), ease=ease)

def front(ch, d=0.5, z=1.0, side=0.0):
    """ponto a frente do personagem (mundo)"""
    th = ch.root.rotation_euler[2]
    p = ch.root.location
    return (p.x + math.sin(th) * d + math.cos(th) * side, p.y - math.cos(th) * d + math.sin(th) * side, p.z + z)

def walk_to(ch, f0, f1, p1, sps=2.0, turn=6):
    """vira para a direcao do movimento e anda ate p1"""
    p0 = val_at(ch.root, 'location', f0)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    th = math.atan2(dx, -dy)
    r0 = val_at(ch.root, 'rotation_euler', f0)
    while th - r0[2] > PI: th -= 2 * PI
    while th - r0[2] < -PI: th += 2 * PI
    face(ch, f0 + turn, th, turn)
    ch.walk(f0, f1, p0, p1, sps)

def turn_to(ch, f, target, ease=8):
    """vira o corpo para olhar o ponto target (x, y)"""
    p = val_at(ch.root, 'location', f)
    th = math.atan2(target[0] - p[0], -(target[1] - p[1]))
    r0 = val_at(ch.root, 'rotation_euler', f - ease)
    while th - r0[2] > PI: th -= 2 * PI
    while th - r0[2] < -PI: th += 2 * PI
    face(ch, f, th, ease)

def face(ch, f, rot, ease=8):
    r0 = val_at(ch.root, 'rotation_euler', f - ease)
    key(ch.root, 'rotation_euler', f - ease, r0)
    key(ch.root, 'rotation_euler', f, (r0[0], r0[1], rot))

def shocked(ch, f):
    ch.brows_set(f, 0.45)
    key(ch.mouth, 'scale', f - 4, val_at(ch.mouth, 'scale', f - 4)); key(ch.mouth, 'scale', f, (0.8, 1, 1.5))
    for e in ch.eyes:
        key(e, 'scale', f - 4, (1, 1, 1)); key(e, 'scale', f, (1.2, 1.2, 1.2))

def evil_smile(ch, f):
    ch.brows_set(f, -0.35)
    key(ch.mouth, 'scale', f - 6, val_at(ch.mouth, 'scale', f - 6)); key(ch.mouth, 'scale', f, (1.5, 1, 0.45))

def sad(ch, f):
    ch.brows_set(f, 0.4)
    key(ch.mouth, 'scale', f - 6, val_at(ch.mouth, 'scale', f - 6)); key(ch.mouth, 'scale', f, (0.75, 1, 0.3))

def winterfell(ox=0.0, back=5.0, snow=True, bolton=False, f1=400, flakes=60):
    """patio de Winterfell: chao de neve, muralha, torres, estandartes"""
    if snow:
        snow_ground(ox, 60, '#e8eef2')
    else:
        mud_ground(ox)
    stone_wall(ox - 9, ox + 9, back, 4.2)
    tower((ox - 4.6, back + 1.0, 0), 1.3, 7.5, roof='#4a5a6a', window_z=5.5)
    tower((ox + 4.8, back + 1.2, 0), 1.1, 6.5, roof='#4a5a6a', window_z=4.6)
    tower((ox + 0.3, back + 4.0, 0), 1.6, 9.5, roof='#4a5a6a', window_z=7.0)
    for i, x in enumerate((-2.6, -0.9, 0.9, 2.6)):
        if bolton:
            banner((ox + x, back - 0.33, 3.8), '#1e1414', 'flayed', 1.0, 2.0)
        else:
            banner((ox + x, back - 0.33, 3.8), '#f2f0ea', 'wolf', 1.0, 2.0)
    box((2.2, 0.4, 2.6), (ox, back - 0.22, 1.3), m=mat('#3a2a1e', 0.9))       # portao
    for x in (-6.5, 6.8):
        snow_pine((ox + x, back - 1.5, 0), 0.9)
    if flakes:
        snowfall(flakes, (ox, 0.5, 0), (7, 5), 4.0, 1, f1, seed=int(ox) + 3, r=0.022)

def red_room(ox=0.0, back=2.2, color='#8a2a24', color2='#7a221e'):
    """sala Lannister (vermelha) com estandartes de leao"""
    stone_floor(ox, '#8a7a6a', '#7a6a5a', 30, 1.2)
    stripes_wall(color, color2, w=14, h=6, n=16, loc=(ox, back, 0), horizontal=False)
    for x in (-1.9, 1.9):
        banner((ox + x, back - 0.1, 3.0), '#a8141e', 'lion', 0.9, 1.8)

def throne_room(ox=0.0, back=4.0, throne=True, dark=False, cols=True):
    stone_floor(ox, '#6a6460', '#5a5450', 30, 1.0)
    box((18, 0.4, 8), (ox, back + 0.4, 4), m=mat('#5a524c' if not dark else '#3a3430', 0.9))
    for x in ((-3.4, -1.8, 1.8, 3.4) if cols else ()):
        cyl(0.3, 7.0, (ox + x, back - 1.2, 3.5), m=mat('#6a625a', 0.85), verts=16)
    for x in (-2.6, 2.6):
        banner((ox + x, back + 0.15, 5.2), '#a8141e', 'lion', 1.1, 2.6)
    box((1.8, 6.0, 0.02), (ox, back - 3.5, 0.01), m=mat('#8a1e1e', 0.9))     # tapete
    if throne:
        return iron_throne((ox, back - 1.0, 0), 0.0)

def godswood(ox=0.0, night=True):
    snow_ground(ox, 60, '#c8d4e0' if night else '#e8eef2')
    weirwood((ox, 3.9, 0), 1.0)
    for i, (x, y) in enumerate(((-3.5, 4), (3.6, 4.5), (-5.5, 7), (5.2, 7.5), (-2, 9), (2.5, 9.5), (0, 11))):
        snow_pine((ox + x, y, 0), 1.0 + (i % 3) * 0.15)


# ============================================================================ SHOTS
def s01(c):
    """GANCHO: Ned ajoelhado no cadafalso, o carrasco ergue a espada -> corte seco, corvos; Joffrey sorri"""
    setup_render(sky='#d8c8b0', sky_strength=0.9)
    stone_floor(0, '#b8ac98', '#a89c88', 30, 1.0)
    sept((0, 9.0, 0), 0.9)
    for i, x in enumerate((-5.5, 5.8)):
        house((x, 5.0, 0), 2.4, 2.0, 2.6, '#e0ccaa', '#b8462a')
    box((2.8, 1.8, 0.6), (0, 1.0, 0.3), m=mat('#6a4a2e', 0.85))               # cadafalso
    for x in (-1.2, 1.2):
        banner((x, 1.95, 2.9), '#a8141e', 'lion', 0.8, 1.6)
        cyl(0.05, 3.0, (x, 1.95, 1.5), m=mat('#4a3020', 0.8))
    n = ned(cape_=False, loc=(0, 0.9, 0.6), rot=0)
    kneel_at(n, 0.6)
    life(c, n, 1, 0.6)
    sad(n, 6)
    n.look(30, -0.12, 0.0)
    e = executioner(loc=(0.72, 1.2, 0.6), rot=-0.3)
    life(c, e, 2, 0.4)
    e.brows_set(1, -0.3, 1)
    hd = hand_obj(e, 1)
    sword(hd, (0, 0, 0), (0, 0, 0), L=1.0, s=1.6, blade='#c8d0da')
    upd()
    sh = e.arms[1].matrix_world.translation
    e.arms[1].rotation_euler = aim_rot(e, 1, (sh.x + 0.25, sh.y + 0.1, sh.z - 0.6))
    fc = wf(c, 'cabeça')
    e.arm(1, 34, aim_rot(e, 1, (sh.x + 0.05, sh.y + 0.25, sh.z + 0.8)), ease=14)
    e.arm(1, fc - 3, aim_rot(e, 1, (sh.x + 0.1, sh.y + 0.35, sh.z + 0.9)), ease=6)
    e.arm(1, fc + 1, aim_rot(e, 1, (sh.x + 0.5, sh.y - 0.4, sh.z - 0.2)), ease=4)
    # plateia de costas (primeiro plano)
    for i, (x, y) in enumerate(((-1.25, -0.45), (-0.95, -1.05), (1.0, -0.95), (1.3, -0.4), (-1.9, 0.05), (1.95, 0.0))):
        p = crowd_person(10 + i, (x, y, 0), PI + (0.15 if x < 0 else -0.15))
        life(c, p, 10 + i, 0.4, blink=False)
    sun(rot=(0.9, 0.1, 0.5), energy=3.0, color='#ffe2c0')
    point((0, -1.2, 2.6), 80, '#ffe6c8', 1.0)
    cam, t = camera((0, -3.6, 1.6), (0, 1.0, 1.25), 32)
    cam_path(cam, t, [(1, (0.15, -3.6, 1.7), (0.3, 1.0, 1.45)), (fc - 2, (0.2, -1.6, 1.62), (0.3, 1.0, 1.5))])
    # corte: corvos sobre o septo
    cam2, t2 = shot_cam(fc + 1, (0.0, -4.5, 1.2), (0.0, 6, 4.2), 30)
    cam_move(cam2, t2, c, (0.0, -4.5, 1.2), (0.0, -3.8, 1.4), (0.0, 6, 4.2), (0.0, 6, 5.0), fc + 1, wf(c, 'Literalmente') - 6)
    crows(fc + 1, (0, 2.0, 2.6), 14, seed=3, spread=3.0, rise=4.0)
    # Joffrey sorrindo no balcao (x=40)
    X = 40
    stone_floor(X, '#b8ac98', '#a89c88', 30, 1.0)
    stone_wall(X - 6, X + 6, 2.2, 5.0, cren=False)
    banner((X - 1.1, 1.85, 3.6), '#a8141e', 'lion', 0.9, 1.8); banner((X + 1.1, 1.85, 3.6), GOLD, 'stag', 0.9, 1.8)
    box((3.0, 0.25, 1.0), (X, 0.25, 0.5), m=mat('#a89c88', 0.85))           # parapeito
    j = joffrey(loc=(X, 0.8, 0), rot=0)
    life(c, j, 5, 0.5)
    fl = wf(c, 'Literalmente')
    evil_smile(j, fl + 4)
    cam3, t3 = shot_cam(fl - 4, (X, -1.6, 1.45), (X, 0.8, 1.3), 34)
    cam_move(cam3, t3, c, (X, -1.6, 1.45), (X, -1.15, 1.42), (X, 0.8, 1.32), (X, 0.8, 1.36), fl - 4, c.n)


def s02(c):
    """o final odiado: dragao queimando a cidade ao entardecer"""
    setup_render(sky='#e8784a', sky_strength=0.7)
    mud_ground(0, 80, '#7a6a52')
    kings_landing((0, 9, 0), seed=3, n=46, R=9.0, burning=22, f0=8, f1=c.n)
    sea(200, '#2a4a6a', z=-0.3)
    d = dragon((-9, 3.5, 6.5), (0.1, 0, -PI / 2 + 0.25), 1.6)
    dragon_flap(d, 1, c.n, speed=9)
    key(d['root'], 'location', 1, (-9, 3.5, 6.8), 'LINEAR'); key(d['root'], 'location', c.n, (8, 5.5, 5.6), 'LINEAR')
    fire_breath(d, 14, 70, L=5.0, s=1.6)
    fire_breath(d, 86, 118, L=5.0, s=1.6, seed=2)
    sun(rot=(1.25, 0.0, -0.9), energy=2.4, color='#ffb070')
    point((0, 4, 3), 900, '#ff7a2a', 6.0)
    cam, t = camera((0, -9, 3.0), (0, 4, 4.0), 26)
    cam_move(cam, t, c, (-1.0, -9.5, 2.8), (1.0, -8.0, 3.2), (-2.0, 4, 4.6), (2.0, 4, 4.2))


def s03(c):
    """POV: voce e o Ned Stark, Winterfell, o inverno esta chegando"""
    setup_render(sky='#b8c8d8', sky_strength=0.9)
    winterfell(0, 5.0, f1=c.n, flakes=70)
    n = ned(loc=(0, 0.6, 0), rot=0)
    life(c, n, 3, 0.7)
    sword(n.hips, (-0.27, 0.02, 0.05), (0.25, 0, 0), L=0.85)                   # espada na cintura
    fi = wf(c, 'inverno')
    n.look(fi, 0.25, 0.1, 10)
    n.brows_set(fi, 0.15)
    # neve forte no "inverno"
    snowfall(110, (0, -0.5, 0), (5, 3), 3.5, fi - 4, c.n, seed=9, r=0.02)
    for s_, (x, y) in enumerate(((-2.4, 2.4), (2.6, 2.6))):
        sd = soldier(30 + s_, '#5a5a62', loc=(x, y, 0), rot=0)
        sword(hand_obj(sd, 1), (0, 0, 0), (0, 0, 0), L=0.7)
        life(c, sd, 30 + s_, 0.4)
    sun(rot=(0.9, 0.15, 0.5), energy=2.2, color='#e8f0ff')
    point((0, -1.2, 2.5), 70, '#f0f4ff', 1.0)
    cam, t = camera((0, -2.0, 1.45), (0, 0.6, 1.4), 32)
    fu = wf(c, 'Uínterfél')
    cam_path(cam, t, [(1, (0, -2.1, 1.42), (0, 0.6, 1.38)), (fu - 10, (0, -2.6, 1.5), (0, 0.6, 1.5)),
                      (fu + 25, (0.2, -6.6, 2.7), (0.1, 2.5, 3.0)), (fi - 4, (0.1, -5.4, 2.3), (0, 1.5, 2.2)),
                      (c.n, (0, -2.6, 1.6), (0, 0.6, 1.45))])


def s04(c):
    """a familia: Catelyn, Robb, Sansa, Arya, Bran, Rickon ... e o bastardo Jon Snow"""
    setup_render(sky='#b8c8d8', sky_strength=0.9)
    winterfell(0, 5.0, f1=c.n, flakes=50)
    n = ned(loc=(-2.4, 0.7, 0), rot=0.15)
    fam = [(catelyn, 'Kétlin', (-1.72, 0.7), 0.15), (robb, 'Róbi', (-0.98, 0.65), 0.05), (sansa, 'Sânsa', (-0.3, 0.55), 0.0),
           (arya, 'Ária', (0.3, 0.45), -0.05), (bran, 'Brân', (0.85, 0.42), -0.1), (rickon, 'Ríkon', (1.32, 0.4), -0.15)]
    life(c, n, 1, 0.6)
    chars = []
    for i, (fn, w, (x, y), r) in enumerate(fam):
        ch = fn(loc=(x, y, 0), rot=r)
        life(c, ch, 40 + i, 0.6)
        pop_in(ch.root, wf(c, w), 9)
        smile(ch, wf(c, w) + 10)
        chars.append(ch)
    smile(n, wf(c, 'Kétlin') + 6)
    j = jon(loc=(2.75, 0.85, 0), rot=-0.25)
    life(c, j, 50, 0.6)
    fj = wf(c, 'Djón')
    pop_in(j.root, fj, 9)
    sad(j, fj + 12)
    j.look(fj + 14, 0.25, 0, 10)
    cat = chars[0]
    fb = wf(c, 'bastardo')
    face(cat, fb + 2, -0.55, 10)
    cat.brows_set(fb + 6, -0.4)
    sun(rot=(0.9, 0.15, 0.5), energy=2.2, color='#e8f0ff')
    point((0, -1.5, 2.5), 80, '#f0f4ff', 1.5)
    cam, t = camera((-2.0, -2.9, 1.35), (-2.0, 0.6, 1.1), 30)
    pts = [(1, -2.05), (wf(c, 'Kétlin') + 4, -1.95), (wf(c, 'Róbi') - 6, -1.45), (wf(c, 'Sânsa'), -0.9), (wf(c, 'Ária'), -0.25),
           (wf(c, 'Brân'), 0.35), (wf(c, 'Ríkon') + 4, 0.75), (fj - 10, 1.0), (fj + 6, 2.25), (c.n, 2.35)]
    cam_path(cam, t, [(f, (x, -2.9, 1.3), (x, 0.6, 1.0)) for f, x in pts])


def s05(c):
    """o rei Robert chega e chama o Ned para ser a Mao do Rei"""
    setup_render(sky='#b8c8d8', sky_strength=0.9)
    winterfell(0, 5.0, f1=c.n, flakes=40)
    for x in (-3.3, 3.3):
        banner((x, 4.67, 3.8), GOLD, 'stag', 1.0, 2.0)
    n = ned(loc=(-0.55, 0.6, 0), rot=0.6)
    life(c, n, 4, 0.6)
    r = robert(loc=(3.0, 0.9, 0), rot=-PI / 2)
    life(c, r, 5, 0.6)
    r.walk(4, 52, (3.0, 0.9, 0), (0.55, 0.65, 0), 1.8)
    face(r, 60, -0.75, 10)
    smile(r, 58, big=True); smile(n, 62)
    for i, (x, y) in enumerate(((2.2, 2.0), (3.0, 2.3))):
        sd = soldier(60 + i, '#3a2e1e', GOLD, loc=(x + 1.5, y, 0), rot=-PI / 2)
        sd.walk(4, 52, (x + 1.5, y, 0), (x, y, 0), 1.8)
        face(sd, 60, -0.4, 10)
    fm = wf(c, 'Mão')
    hp = hand_obj(r, 1)
    pin = hand_pin(hp, (0, -0.02, -0.03), (PI / 2, 0, 0), 1.6)
    pop_in(pin, fm - 14, 8)
    upd()
    mid = ((n.root.location.x + r.root.location.x) / 2, 0.42, 1.0)
    aim(r, 1, mid, fm - 16, 10)
    aim(n, 1, (mid[0] - 0.05, mid[1] - 0.02, mid[2] - 0.04), fm - 4, 10)
    n.brows_set(fm, 0.2)
    sun(rot=(0.9, 0.15, 0.5), energy=2.2, color='#e8f0ff')
    point((0, -1.5, 2.5), 80, '#f0f4ff', 1.5)
    cam, t = camera((0.6, -3.2, 1.5), (0.8, 0.7, 1.2), 32)
    cam_path(cam, t, [(1, (1.1, -3.4, 1.5), (1.4, 0.7, 1.2)), (52, (0.1, -2.9, 1.45), (0.05, 0.6, 1.2)),
                      (c.n, (0.05, -2.3, 1.35), (0.0, 0.6, 1.15))])


def s06(c):
    """Cersei e o irmao gemeo Jaime"""
    setup_render(sky='#3a1a14', sky_strength=0.75)
    red_room(0, 2.2)
    candle((-1.2, 1.6, 0.0), 0.0)
    ce = cersei(loc=(-0.36, 0.55, 0), rot=1.05)
    ja = jaime(loc=(0.36, 0.55, 0), rot=-1.05)
    life(c, ce, 6, 0.6); life(c, ja, 7, 0.6)
    fc = wf(c, 'caso')
    aim(ce, 0, (0.0, 0.35, 0.82), fc - 6, 10)
    aim(ja, 1, (0.02, 0.35, 0.84), fc - 4, 10)
    smile(ce, fc + 4); smile(ja, fc + 8)
    evil_smile(ce, wf(c, 'Djáime') + 6)
    ce.look(fc, -0.08, 0.15); ja.look(fc, -0.08, -0.15)
    sun(rot=(0.9, 0.15, 0.5), energy=1.2, color='#ffd8b0')
    point((0, -1.0, 2.2), 120, '#ffc890', 1.2)
    point((-1.2, 1.3, 1.6), 30, '#ffa040', 0.2)
    cam, t = camera((0, -2.6, 1.45), (0, 0.55, 1.3), 32)
    cam_move(cam, t, c, (0.0, -2.7, 1.45), (0.0, -1.85, 1.4), (0, 0.55, 1.32), (0, 0.55, 1.36))


def s07(c):
    """Bran ve os dois pela janela da torre; Jaime empurra (nao grafico)"""
    setup_render(sky='#9fc8e8')
    stone_floor(0, '#8a8478', '#7a7468', 20, 1.0)
    m = mat(STONE, 0.9)
    Y = 1.2
    box((5.0, 0.2, 4.0), (-3.0, Y, 2.0), m=m); box((5.0, 0.2, 4.0), (3.0, Y, 2.0), m=m)
    box((1.0, 0.2, 1.0), (0, Y, 0.5), m=m); box((1.0, 0.2, 2.0), (0, Y, 3.0), m=m)
    box((7, 0.2, 4.0), (-4.0, -1.0, 2.0), rot=(0, 0, PI / 2), m=m)
    # paisagem la fora (embaixo)
    box((40, 40, 0.02), (0, 22, -8.0), m=mat('#7a9a5a', 0.9))
    for i in range(4):
        cloud((-6 + i * 4, 18, 3 + (i % 2)), 1.2, seed=i)
    ce = cersei(loc=(0.45, 0.1, 0), rot=PI / 2 - 0.4)
    ja = jaime(loc=(1.15, 0.1, 0), rot=-PI / 2 + 0.4)
    life(c, ce, 6, 0.5); life(c, ja, 7, 0.5)
    b = bran(loc=(0.0, 1.47, 0.5), rot=0)
    life(c, b, 8, 0.5)
    fv = wf(c, 'vê')
    for k, sx in enumerate((-1, 1)):
        aim(b, k, (sx * 0.24, 1.28, 1.02))
    pop_in(b.root, 2, 6)
    shocked(b, fv + 6)
    turn_to(ce, fv + 6, (0, 1.2), 10); turn_to(ja, fv + 4, (0, 1.2), 10)
    shocked(ce, fv + 10)
    ja.brows_set(fv + 12, -0.4)
    fe = wf(c, 'empurra')
    walk_to(ja, fe - 24, fe - 4, (0.1, 0.86, 0), 2.2)
    face(ja, fe - 2, PI, 5)
    aim(ja, 1, (0.02, 1.36, 1.25), fe + 2, 6)
    # Bran cai para tras e some
    key(b.root, 'location', fe + 2, (0.0, 1.47, 0.5)); key(b.root, 'rotation_euler', fe + 2, (0, 0, 0))
    key(b.root, 'location', fe + 16, (0.0, 2.4, -2.6)); key(b.root, 'rotation_euler', fe + 16, (-1.3, 0, 0))
    hide_from(b, fe + 17)
    sun(rot=(0.7, 0.1, 0.4), energy=2.6)
    point((0, -0.5, 2.6), 90, '#fff2dc', 1.0)
    cam, t = camera((-1.2, -2.6, 1.5), (0.35, 0.8, 1.3), 30)
    cam_move(cam, t, c, (-1.25, -2.7, 1.5), (-1.0, -2.2, 1.45), (0.4, 0.8, 1.3), (0.15, 0.9, 1.3), 1, c.n)


def s08(c):
    """do outro lado do mar: Daenerys obrigada a casar com Khal Drogo"""
    setup_render(sky='#ffc890', sky_strength=1.0)
    grass_ground(0, 80, '#c8a85a')
    sea(200, '#3a8ab8', z=-0.02)
    box((80, 30, 0.04), (0, -3.0, 0.0), m=mat('#c8a85a', 0.9))
    for i, (x, y) in enumerate(((-3.5, 5.5), (3.8, 6.2), (-6.5, 8.0), (6.8, 9.0), (0.5, 9.5))):
        tent((x, y, 0), 1.6 + (i % 2) * 0.4, 2.2, ['#c89a5a', '#a87a4a', '#d8b070'][i % 3])
    dn = dany(loc=(-0.45, 0.55, 0), rot=0.25)
    life(c, dn, 8, 0.6)
    sad(dn, wf(c, 'obrigada'))
    dr = drogo(loc=(3.0, 0.75, 0), rot=-PI / 2)
    life(c, dr, 9, 0.5)
    fo = wf(c, 'obrigada')
    dr.walk(fo - 4, fo + 34, (3.0, 0.75, 0), (0.45, 0.6, 0), 1.6)
    face(dr, fo + 40, -0.6, 10)
    dr.brows_set(fo + 30, -0.3)
    dn.look(fo + 36, -0.15, 0.3, 10)
    sun(rot=(1.1, 0.1, -0.7), energy=3.0, color='#ffd8a0')
    point((0, -1.2, 2.4), 70, '#ffe6c8', 1.0)
    cam, t = camera((0, -4.5, 2.4), (0, 3, 1.5), 30)
    fd = wf(c, 'Dainéris')
    cam_path(cam, t, [(1, (0.6, -6.0, 3.8), (0.6, 8, 1.5)), (fd - 4, (0.0, -3.4, 1.6), (0.0, 0.6, 1.25)),
                      (c.n, (0.15, -2.75, 1.5), (0.1, 0.6, 1.3))])


def s09(c):
    """o segredo: os filhos da rainha (loiros) nao sao do rei -> sao do Jaime"""
    setup_render(sky='#2a1e18', sky_strength=0.7)
    stone_floor(0, '#7a6a5a', '#6a5a4a', 30, 1.0)
    box((14, 0.3, 5), (0, 2.0, 2.5), m=mat('#6a5a4a', 0.9))
    for x in (-2.0, 2.0):                                               # estantes
        sh = empty('shelf', (x, 1.65, 0))
        box((1.5, 0.4, 2.6), (0, 0, 1.3), m=mat('#5a3a22', 0.8), parent=sh)
        rnd = random.Random(int(x * 10))
        for k in range(4):
            for i in range(9):
                box((0.12, 0.3, rnd.uniform(0.25, 0.4)), (-0.6 + i * 0.15, -0.06, 0.25 + k * 0.6 + 0.18), m=mat(rnd.choice(['#8a2a22', '#2a4a6a', '#3a5a2a', '#7a6a2a']), 0.7), parent=sh)
    table((0, 0.0, 0), (1.3, 0.7), 0.8, '#6a4a2e', '#4a3020')
    bk = empty('bigbook', (0.0, -0.05, 0.83))
    box((0.6, 0.42, 0.06), (0, 0, 0.03), m=mat('#5a2a1e', 0.7), parent=bk, bevel=0.01)
    box((0.56, 0.4, 0.02), (0, 0, 0.07), m=mat('#f2e8cc', 0.9), parent=bk)
    candle((0.48, 0.1, 0.8), 0.25)
    n = ned(cape_=False, loc=(0, 0.6, 0), rot=0)
    life(c, n, 9, 0.5)
    n.look(1, 0.35, 0)
    aim(n, 0, (-0.2, 0.05, 0.92)); aim(n, 1, (0.2, 0.05, 0.92))
    fs = wf(c, 'segredo')
    shocked(n, fs + 4)
    n.look(fs + 2, -0.05, 0, 6)
    point((0.48, 0.0, 1.3), 60, '#ffb060', 0.3)
    point((0, -1.0, 2.2), 50, '#ffd8a8', 1.0)
    cam, t = camera((0, -2.4, 1.6), (0, 0.4, 1.2), 32)
    cam_move(cam, t, c, (0, -2.5, 1.65), (0, -1.9, 1.5), (0, 0.4, 1.2), (0, 0.5, 1.3), 1, fs + 10)
    # filhos loiros + Jaime (x=40)
    X = 40
    red_room(X, 2.2)
    kids = [joffrey(name='jk', crown_=False, loc=(X - 0.62, 0.45, 0), rot=0.1),
            kid(name='myrc', age_h=0.62, hair='#ecc870', hair_style='long', jacket='#e8b8c8', shirt='#e8b8c8', pants='#e8b8c8',
                female=True, dress='#e8b8c8', loc=(X + 0.2, 0.35, 0), rot=0.0),
            kid(name='tommen', age_h=0.5, hair='#ecc870', hair_style='short', jacket='#c8a040', shirt='#c8a040', pants='#5a3a22',
                loc=(X + 0.72, 0.3, 0), rot=-0.1)]
    ff = wf(c, 'filhos')
    for i, k in enumerate(kids):
        life(c, k, 90 + i, 0.5)
        pop_in(k.root, ff + i * 4, 8)
    ja = jaime(loc=(X - 0.25, 1.0, 0), rot=0)
    life(c, ja, 95, 0.5)
    fn_ = wf(c, 'não')
    pop_in(ja.root, fn_, 9)
    smile(ja, fn_ + 10)
    aim(ja, 0, (X - 0.52, 0.55, 0.98), fn_ + 8, 8)
    point((X, -1.0, 2.4), 110, '#ffd8b0', 1.2)
    cam2, t2 = shot_cam(ff - 4, (X, -2.9, 1.35), (X, 0.6, 1.0), 32)
    cam_move(cam2, t2, c, (X, -2.9, 1.35), (X, -2.6, 1.5), (X, 0.6, 1.0), (X, 0.7, 1.25), ff - 4, c.n)



def s10(c):
    """o rei morre numa cacada (javali) -> Joffrey assume o Trono de Ferro"""
    setup_render(sky='#bfe0c8', sky_strength=0.9)
    grass_ground(0, 60, '#5a7a3a')
    for i, (x, y) in enumerate(((-3.0, 3.5), (-1.2, 5.0), (1.5, 4.2), (3.4, 3.0), (-4.5, 6.5), (4.6, 6.8), (0.2, 7.5), (-2.4, 8.5), (2.8, 9.0))):
        pine((x, y, 0), 1.2 + (i % 3) * 0.2, '#2a5a3a')
    r = robert(loc=(-0.45, 0.6, 0), rot=0.9)
    life(c, r, 10, 0.6)
    hp = hand_obj(r, 1)
    sp = empty('spear', (0, 0, 0), hp)
    cyl(0.025, 2.0, (0, 0, -0.6), m=mat('#6a4a2e', 0.8), parent=sp, verts=10)
    cone(0.05, 0, 0.2, (0, 0, -1.68), (PI, 0, 0), m=mat(STEEL, 0.3, metal=0.8), parent=sp, verts=4)
    aim(r, 1, front(r, 0.6, 0.85))
    bo = boar((3.2, 0.9, 0), PI / 2 + 0.25)
    fm = wf(c, 'morre')
    key(bo, 'location', 1, (3.2, 0.9, 0), 'LINEAR'); key(bo, 'location', fm + 6, (0.35, 0.55, 0))
    for f in range(1, fm + 7, 3):                                     # galope
        bo.rotation_euler = (0.08 * math.sin(f * 1.3), 0, PI / 2 + 0.25); bo.keyframe_insert('rotation_euler', frame=f)
    shocked(r, fm - 4)
    fall_back(r, fm + 6, 9)
    sun(rot=(0.9, 0.15, 0.6), energy=2.8)
    point((0, -1.2, 2.4), 60, '#fff2dc', 1.0)
    cam, t = camera((0.6, -3.2, 1.5), (0.6, 0.7, 0.9), 32)
    cam_move(cam, t, c, (0.8, -3.4, 1.5), (0.3, -2.8, 1.35), (0.8, 0.7, 0.9), (0.2, 0.7, 0.8), 1, fm + 20)
    # Joffrey no trono (x=40)
    X = 40
    throne_room(X, 4.0)
    j = joffrey(loc=(X, 3.15, 0), rot=0)
    sit_on(j, 0.55)
    life(c, j, 11, 0.5)
    fj = wf(c, 'Djófri')
    evil_smile(j, fj + 8)
    for i, x in enumerate((-1.6, 1.6)):
        sd = soldier(70 + i, '#a8141e', GOLD, loc=(X + x, 2.2, 0), rot=0)
        sword(hand_obj(sd, 1), (0, 0, 0), (0, 0, 0), L=0.7)
        life(c, sd, 70 + i, 0.3)
    sun(rot=(0.9, 0.1, 0.5), energy=1.8, color='#ffe2c0')
    point((X, 1.0, 3.0), 150, '#ffd8a8', 2.0)
    cam2, t2 = shot_cam(fj - 10, (X, -2.6, 1.7), (X, 3.1, 1.5), 32)
    cam_move(cam2, t2, c, (X, -2.6, 1.7), (X, 0.6, 1.45), (X, 3.1, 1.5), (X, 3.1, 1.32), fj - 10, c.n)


def s11(c):
    """o Mindinho trai o Ned; Joffrey manda cortar a cabeca"""
    setup_render(sky='#3a3030', sky_strength=0.75)
    throne_room(0, 4.0)
    n = ned(loc=(-0.15, 0.4, 0), rot=0.15)
    lf = littlefinger(loc=(0.42, 0.8, 0), rot=-0.6)
    life(c, n, 12, 0.5); life(c, lf, 13, 0.5)
    ft = wf(c, 'trai')
    dg = dagger(hand_obj(lf, 0), (0, 0, 0), (0, 0, 0))
    pop_in(dg, ft - 4, 6)
    upd()
    lf.walk(ft - 14, ft - 2, (0.42, 0.8, 0), (0.25, 0.68, 0), 2.0)
    aim(lf, 0, (0.02, 0.48, 1.08), ft, 8)
    evil_smile(lf, ft + 2)
    shocked(n, ft + 4)
    n.look(ft + 6, 0, -0.5, 8)
    for i, x in enumerate((-1.3, 1.5)):
        sd = soldier(75 + i, '#a8141e', GOLD, loc=(x, 1.6, 0), rot=0)
        life(c, sd, 75 + i, 0.3)
    sun(rot=(0.9, 0.1, 0.5), energy=1.6, color='#ffe2c0')
    point((0, -1.0, 2.5), 90, '#ffd8a8', 1.5)
    cam, t = camera((0.2, -2.6, 1.5), (0.1, 0.6, 1.25), 32)
    cam_move(cam, t, c, (0.2, -2.7, 1.5), (0.15, -2.1, 1.45), (0.1, 0.6, 1.25), (0.15, 0.6, 1.3), 1, wf(c, 'e'))
    # Joffrey aponta (x=40) -> carrasco + corvos (x=80)
    X = 40
    stone_floor(X, '#b8ac98', '#a89c88', 30, 1.0)
    stone_wall(X - 6, X + 6, 2.2, 5.0, cren=False)
    banner((X - 1.1, 1.85, 3.6), '#a8141e', 'lion', 0.9, 1.8); banner((X + 1.1, 1.85, 3.6), GOLD, 'stag', 0.9, 1.8)
    box((3.0, 0.25, 1.0), (X, 0.25, 0.5), m=mat('#a89c88', 0.85))
    j = joffrey(loc=(X, 0.8, 0), rot=0)
    life(c, j, 14, 0.5)
    fe = wf(c, 'e')
    fm = wf(c, 'manda')
    aim(j, 1, (X + 0.15, -0.6, 1.45), fm, 8)
    evil_smile(j, fm + 4)
    talk(c, j, fm, fm + 22, 0.6)
    point((X, -1.0, 2.5), 90, '#ffd8a8', 1.5)
    cam2, t2 = shot_cam(fe - 2, (X, -1.7, 1.45), (X, 0.8, 1.32), 34)
    cam_move(cam2, t2, c, (X, -1.7, 1.45), (X, -1.3, 1.42), (X, 0.8, 1.32), (X, 0.8, 1.35), fe - 2, wf(c, 'cortar'))
    X2 = 80
    stone_floor(X2, '#b8ac98', '#a89c88', 30, 1.0)
    sept((X2, 9.0, 0), 0.9)
    box((2.8, 1.8, 0.6), (X2, 1.0, 0.3), m=mat('#6a4a2e', 0.85))
    e = executioner(loc=(X2 + 0.3, 1.0, 0.6), rot=-0.2)
    life(c, e, 15, 0.4)
    e.brows_set(1, -0.3, 1)
    sword(hand_obj(e, 1), (0, 0, 0), (0, 0, 0), L=1.0, s=1.6, blade='#c8d0da')
    upd()
    sh = e.arms[1].matrix_world.translation
    fcort = wf(c, 'cortar'); fcab = wf(c, 'cabeça')
    e.arms[1].rotation_euler = aim_rot(e, 1, (sh.x + 0.1, sh.y + 0.25, sh.z + 0.85))
    e.arm(1, fcab - 1, aim_rot(e, 1, (sh.x + 0.1, sh.y + 0.35, sh.z + 0.9)), ease=6)
    e.arm(1, fcab + 3, aim_rot(e, 1, (sh.x + 0.5, sh.y - 0.4, sh.z - 0.2)), ease=3)
    crows(fcab + 3, (X2, 2.0, 2.6), 14, seed=5, spread=3.0, rise=4.0)
    sun(rot=(0.9, 0.1, 0.5), energy=2.6, color='#ffe2c0')
    cam3, t3 = shot_cam(fcort - 3, (X2 + 0.2, -1.6, 0.9), (X2 + 0.3, 1.0, 2.2), 28)
    cam_move(cam3, t3, c, (X2 + 0.2, -1.6, 0.9), (X2 + 0.1, -2.6, 1.0), (X2 + 0.3, 1.0, 2.2), (X2 + 0.1, 3.0, 3.6), fcort - 3, c.n)


def s12(c):
    """voce morreu, mas a guerra comecou -> Daenerys sai viva da fogueira com 3 dragoes"""
    setup_render(sky='#c8b8a0', sky_strength=0.85)
    mud_ground(0, 60, '#7a6a52')
    # dois exercitos: lobo x leao
    for i in range(5):
        for k in range(2):
            a_ = soldier(100 + i * 2 + k, '#5a5a62', STEEL, loc=(-1.0 - k * 0.7, 2.0 + i * 0.75 - k * 0.3, 0), rot=PI / 2 - 0.3)
            sword(hand_obj(a_, 1), (0, 0, 0), (0, 0, 0), L=0.7)
            b_ = soldier(140 + i * 2 + k, '#a8141e', GOLD, loc=(1.0 + k * 0.7, 2.0 + i * 0.75 - k * 0.3, 0), rot=-PI / 2 + 0.3)
            sword(hand_obj(b_, 1), (0, 0, 0), (0, 0, 0), L=0.7)
            fg = wf(c, 'guerra') + (i + k) % 3 * 2
            for ch in (a_, b_):
                aim(ch, 1, front(ch, 0.25, 1.95, 0.15), fg, 6)
                ch.brows_set(fg, -0.35)
    banner((-2.6, 5.5, 3.0), '#f2f0ea', 'wolf', 1.0, 2.0); banner((2.6, 5.5, 3.0), '#a8141e', 'lion', 1.0, 2.0)
    for x in (-2.6, 2.6):
        cyl(0.05, 3.2, (x, 5.55, 1.6), m=mat('#4a3020', 0.8))
    sun(rot=(0.9, 0.15, 0.5), energy=2.4)
    cam, t = camera((0, -4.5, 2.3), (0, 3.0, 1.2), 30)
    fd = wf(c, 'Dainéris')
    cam_move(cam, t, c, (0, -4.8, 2.2), (0, -3.6, 2.6), (0, 3.0, 1.2), (0, 3.0, 1.2), 1, fd)
    # fogueira noturna (x=40)
    X = 40
    mud_ground(X, 60, '#3a3228')
    py = pyre((X, 1.2, 0))
    fo, fl = flames((X, 1.2, 0.5), 16, 0.8, 1.6, seed=4)
    flicker(fl, 1, c.n, 4, 0.3)
    fe_ = wf(c, 'entra'); fs = wf(c, 'sai')
    key(fo, 'scale', fe_ + 10, (1, 1, 1)); key(fo, 'scale', fe_ + 24, (1.4, 1.4, 1.6)); key(fo, 'scale', fs - 2, (1.4, 1.4, 1.6))
    key(fo, 'scale', fs + 10, (0.02, 0.02, 0.02))
    dn = dany(loc=(X - 0.2, -0.4, 0), rot=PI - 0.2)
    life(c, dn, 16, 0.5)
    walk_to(dn, fe_, fe_ + 22, (X, 0.75, 0.0), 1.6)
    face(dn, fs + 2, 0.0, 10)
    # depois: em pe nas cinzas, 3 dragoes bebes
    key(dn.root, 'location', fs + 2, (X, 0.75, 0.0)); key(dn.root, 'location', fs + 10, (X, 0.75, 0.52))
    puffs((X, 1.2, 0.6), fs, c.n, '#5a5450', n=8, seed=3, rise=2.0, s=0.5, spread=0.6, every=3)
    upd()
    fdr = wf(c, 'dragões')
    for k, (pos, col, rr) in enumerate((((-0.3, 0.02, 0.6), '#2e2628', 0.6), ((0.3, 0.02, 0.6), '#2e6a3a', -0.6), ((0.0, -0.18, 0.3), '#e0c070', 0.0))):
        p, d = baby_dragon(dn.chest, pos, (0, 0, rr), col, '#9a2a1e', s=0.19)
        dragon_flap(d, fdr, c.n, speed=5, amp=0.6, phase=k * 3)
        pop_in(p, wf(c, 'três') + k * 5, 8)
    smile(dn, fdr)
    point((X, 0.5, 1.4), 600, '#ff9a3a', 2.0)
    point((X, -1.5, 2.2), 30, '#ffd8a8', 1.0)
    cam2, t2 = shot_cam(fd - 2, (X, -2.6, 1.4), (X, 0.8, 1.2), 30)
    cam_path(cam2, t2, [(fd - 2, (X, -2.6, 1.4), (X, 0.8, 1.2)), (fs, (X - 0.3, -2.9, 1.5), (X, 0.8, 1.35)),
                        (c.n, (X, -1.75, 1.6), (X, 0.75, 1.55))])


def s13(c):
    """Jon e Sam na Patrulha da Noite, a Muralha de gelo, os Caminhantes Brancos"""
    setup_render(sky='#6a7e96', sky_strength=0.9)
    snow_ground(0, 80, '#e8eef4')
    ice_wall(14, 16, 80)
    for i, (x, y) in enumerate(((-3.5, 6), (3.8, 6.5), (-6.0, 9), (6.2, 9.5))):
        box((2.2, 1.8, 1.8), (x, y, 0.9), m=mat('#5a4030', 0.85))
        cone(1.6, 0, 0.9, (x, y, 2.25), (0, 0, PI / 4), m=mat('#3a2a1e', 0.8), verts=4)
    snowfall(70, (0, 0.5, 0), (6, 4), 4.0, 1, c.n, seed=13)
    j = jon(loc=(-0.38, 0.6, 0), rot=0.1)
    sm = sam(loc=(0.42, 0.65, 0), rot=-0.15)
    life(c, j, 17, 0.6); life(c, sm, 18, 0.6)
    sword(j.hips, (-0.27, 0.02, 0.05), (0.25, 0, 0), L=0.85)
    fs = wf(c, 'Sam')
    smile(sm, fs + 4, True)
    aim(sm, 1, front(sm, 0.15, 1.75, 0.35), fs + 2, 8)
    sm.arm(1, fs + 30, (0, 0.12, 0), ease=10)
    sm.look(fs + 2, 0, 0.35, 8); j.look(fs + 6, 0, -0.3, 8)
    fm = wf(c, 'Muralha')
    for g, i in ((j, 0), (sm, 1)):
        g.look(fm, 0.45, 0, 10)
    for i, x in enumerate((-2.2, 2.4)):
        b = soldier(80 + i, '#1c1c22', None, loc=(x, 2.4, 0), rot=0.0)
        cape(b, '#141418'); life(c, b, 80 + i, 0.4)
    sun(rot=(0.85, 0.15, 0.5), energy=2.2, color='#e8f0ff')
    point((0, -1.5, 2.5), 80, '#f0f4ff', 1.2)
    cam, t = camera((0, -2.8, 1.45), (0, 0.6, 1.3), 30)
    fc = wf(c, 'Caminhantes')
    cam_path(cam, t, [(1, (0, -2.8, 1.45), (0, 0.6, 1.3)), (fm - 8, (0, -3.2, 1.5), (0, 0.6, 1.4)),
                      (fm + 14, (0, -4.8, 1.2), (0, 6, 8.5)), (fc, (0, -4.8, 1.2), (0, 6, 9.5))])
    # alem da Muralha: Caminhante Branco (x=40)
    X = 40
    setup_dummy = None
    snow_ground(X, 80, '#c8d8e8')
    for i, (x, y) in enumerate(((-2.8, 3.5), (3.0, 4.5), (-4.5, 7), (4.0, 8), (0.5, 9))):
        snow_pine((X + x, y, 0), 1.2)
    ww = night_king(name='walker', loc=(X, 1.2, 0), rot=0)
    for o in ww.head.children:
        if o.name.startswith('walker_icecrown'):
            o.scale = (0.7, 0.7, 0.6)
    life(c, ww, 19, 0.4)
    ww.walk(fc, c.n, (X, 1.6, 0), (X, 0.6, 0), 1.4)
    ww.brows_set(fc, -0.3, 1)
    snowfall(120, (X, 0.0, 0), (5, 4), 4.0, fc - 5, c.n, seed=31)
    point((X, -0.6, 1.6), 60, '#7ac8ff', 1.0)
    cam2, t2 = shot_cam(fc, (X, -1.9, 1.45), (X, 0.9, 1.38), 34)
    cam_move(cam2, t2, c, (X, -1.9, 1.45), (X, -1.6, 1.42), (X, 0.9, 1.38), (X, 0.8, 1.38), fc, c.n)


def s14(c):
    """Robb Rei do Norte; Tyrion salva a capital do Stannis com fogo verde"""
    setup_render(sky='#b8c8d8', sky_strength=0.9)
    snow_ground(0, 60, '#dde6ee')
    for i, (x, y) in enumerate(((-4, 5), (4.2, 5.5), (-6.5, 8), (6.5, 8.5))):
        tent((x, y, 0), 1.6, 2.2, '#8a7a6a')
    banner((0, 3.8, 3.4), '#f2f0ea', 'wolf', 1.2, 2.4)
    cyl(0.06, 3.6, (0, 3.85, 1.8), m=mat('#4a3020', 0.8))
    r = robb(crown_=True, loc=(0, 1.3, 0), rot=0)
    life(c, r, 20, 0.5)
    crw = [o for o in r.head.children if o.name.startswith('robb_crown')][0]
    fr = wf(c, 'Rei')
    pop_in(crw, fr, 8)
    sword(hand_obj(r, 1), (0, 0, 0), (0, 0, 0), L=0.85)
    aim(r, 1, front(r, 0.2, 2.1, 0.25), fr, 8)
    smile(r, fr + 6)
    for i in range(6):
        x = (-1.5, -0.9, 0.9, 1.5, -2.1, 2.1)[i]; y = (0.2, -0.5, -0.5, 0.2, 1.0, 1.0)[i]
        sd = soldier(150 + i, '#5a5a62', STEEL, loc=(x, y, 0), rot=PI + (0.5 if x < 0 else -0.5) * 0.6)
        sword(hand_obj(sd, 1), (0, 0, 0), (0, 0, 0), L=0.7)
        aim(sd, 1, front(sd, 0.25, 1.95, 0.1), fr + 4 + i % 3 * 2, 6)
        life(c, sd, 150 + i, 0.4)
    snowfall(50, (0, 0.5, 0), (6, 4), 4.0, 1, c.n, seed=14)
    sun(rot=(0.85, 0.15, 0.5), energy=2.2, color='#e8f0ff')
    point((0, -1.0, 2.6), 90, '#f0f4ff', 1.5)
    cam, t = camera((0, -3.4, 1.4), (0, 1.3, 1.6), 30)
    ft = wf(c, 'Tírion')
    cam_move(cam, t, c, (0, -3.6, 1.3), (0, -2.6, 1.3), (0, 1.3, 1.7), (0, 1.3, 1.75), 1, ft)
    # Tyrion na muralha a noite (x=40)
    X = 40
    setup = None
    box((12, 3, 3.0), (X, 1.8, 1.5), m=mat(STONE, 0.9))
    stone_floor(X, '#6a6460', '#5a5450', 30, 1.0)
    for i in range(8):
        if i % 2 == 0:
            box((0.6, 0.4, 0.5), (X - 2.1 + i * 0.6, 0.45, 3.25), m=mat(STONE, 0.9))
    box((12, 0.4, 0.3), (X, 0.45, 3.15), m=mat(STONE, 0.9))
    box((12, 2.0, 0.1), (X, 1.5, 3.0), m=mat('#6a6460', 0.9))
    ty = tyrion(cape_=True, loc=(X - 0.25, 1.0, 3.05), rot=0.2)
    ce = cersei(loc=(X + 0.45, 1.25, 3.05), rot=-0.3)
    life(c, ty, 21, 0.5); life(c, ce, 22, 0.5)
    fcs = wf(c, 'Cérsei')
    pop_in(ce.root, fcs, 8)
    ce.look(fcs + 10, 0.2, 0.3, 8)
    ty.brows_set(ft + 6, -0.2)
    torch((X - 1.4, 0.6, 3.6), 1, c.n, 2); torch((X + 1.4, 0.6, 3.6), 1, c.n, 3)
    point((X, -1.0, 4.2), 120, '#ffc890', 1.5)
    cam2, t2 = shot_cam(ft - 2, (X, -1.6, 4.35), (X, 1.0, 4.2), 30)
    cam_move(cam2, t2, c, (X, -1.6, 4.35), (X + 0.1, -1.3, 4.3), (X, 1.0, 4.2), (X + 0.05, 1.0, 4.25), ft - 2, wf(c, 'salva'))
    # navios do Stannis + fogo verde (x=80)
    X2 = 80
    sea(200, '#1e3048', z=0.0)
    for i, (x, y, r_) in enumerate(((-2.0, 6.0, 0.3), (2.5, 7.5, -0.2), (-0.5, 10.0, 0.1), (4.5, 11.5, -0.3), (-4.5, 10.5, 0.4))):
        ship((X2 + x, y, 0), r_, GOLD, s=0.9, sigil='stag' if i < 2 else None)
    st = stannis(loc=(X2 - 2.0, 5.2, 0.6), rot=0.3)
    life(c, st, 23, 0.4)
    st.brows_set(1, -0.3, 1)
    fv = wf(c, 'verde')
    gf = empty('wildfire', (X2 + 0.5, 8.5, 0.5))
    for k, (dx, dy, dz, sc) in enumerate(((0, 0, 0, 2.2), (-1.5, -0.8, 0.2, 1.6), (1.6, 0.6, 0.1, 1.8), (0.3, 1.5, 0.6, 1.4))):
        sphere(sc, (dx, dy, dz), m=mat(['#4aff5a', '#2adf3a', '#8aff6a', '#3aef4a'][k], 0.5, emit=7), parent=gf, seg=24)
    key(gf, 'scale', fv - 5, (0, 0, 0), 'CONSTANT'); key(gf, 'scale', fv - 4, (0.05, 0.05, 0.05)); key(gf, 'scale', fv + 6, (1.3, 1.3, 1.1))
    key(gf, 'scale', c.n, (1.5, 1.5, 1.3))
    spike(fv - 3, (X2 + 0.5, 6.5, 2.0), '#4aff5a', 6000, 14, 2.0)
    setup_render_sky = None
    point((X2, 2.0, 3.0), 120, '#a8b8ff', 2.0)
    cam3, t3 = shot_cam(wf(c, 'salva') - 2, (X2 - 0.5, -2.0, 2.2), (X2 - 1.5, 5.5, 1.6), 30)
    cam_move(cam3, t3, c, (X2 - 0.5, -2.0, 2.2), (X2, -3.5, 3.0), (X2 - 1.6, 5.5, 1.7), (X2 + 0.3, 7.0, 2.0), wf(c, 'salva') - 2, c.n)


def s15(c):
    """Casamento Vermelho (nao grafico): luzes vermelhas, besteiros, Walder Frey"""
    setup_render(sky='#2a1a14', sky_strength=0.7)
    stone_floor(0, '#7a6a5a', '#6a5a4a', 30, 1.0)
    box((14, 0.3, 6), (0, 2.6, 3), m=mat('#6a5a4a', 0.9))
    for x in (-1.5, 1.5):
        banner((x, 2.4, 3.6), '#c8c8c8', 'towers', 1.0, 2.0)
    long_table((0, 0.35, 0), 3.6, 0.9, 0.78)
    for i, x in enumerate((-1.2, -0.3, 0.6, 1.4)):
        goblet(None, (x, 0.25, 0.79))
        candle((x + 0.35, 0.45, 0.79), 0.18)
    bench((0, 1.05, 0), 3.4)
    r = robb(cape_=False, crown_=True, loc=(-0.35, 1.05, 0), rot=0)
    ca = catelyn(loc=(0.4, 1.05, 0), rot=0)
    for ch in (r, ca):
        sit_on(ch, 0.45)
    life(c, r, 24, 0.4); life(c, ca, 25, 0.4)
    smile(r, 10); smile(ca, 12)
    fv = wf(c, 'Vermelho'); fm = wf(c, 'mortos')
    shocked(ca, fv + 6); shocked(r, fv + 10)
    ca.look(fv + 8, 0.3, 0.3, 8); r.look(fv + 10, 0.3, -0.2, 8)
    # besteiros na galeria
    box((14, 1.0, 0.15), (0, 2.1, 2.6), m=mat('#4a3a2a', 0.8))
    for i, x in enumerate((-1.8, -0.6, 0.6, 1.8)):
        b = soldier(200 + i, '#3a3a3e', '#4a4a50', loc=(x, 2.1, 2.68), rot=0)
        crossbow(hand_obj(b, 1), (0, 0, 0), (0, 0, 0))
        aim(b, 1, front(b, 0.6, 1.2, 0.1))
        pop_in(b.root, fv + 4 + i * 3, 8)
        life(c, b, 200 + i, 0.3)
    warm = point((0, -0.8, 2.4), 110, '#ffc890', 1.5)
    red = point((0, -0.5, 2.6), 0, '#ff1a1a', 1.5)
    key(warm.data, 'energy', fv, 110); key(warm.data, 'energy', fv + 10, 10)
    key(red.data, 'energy', fv, 0); key(red.data, 'energy', fv + 10, 260)
    spike(fm, (0, -0.5, 1.6), '#ff2020', 2500, 10, 1.0)
    cam, t = camera((0, -2.8, 1.6), (0, 1.0, 1.4), 30)
    fw = wf(c, 'Uólder')
    cam_move(cam, t, c, (0, -2.8, 1.6), (0, -2.0, 1.55), (0, 1.0, 1.4), (0, 1.0, 1.4), 1, fw)
    # Walder Frey (x=40)
    X = 40
    stone_floor(X, '#7a6a5a', '#6a5a4a', 30, 1.0)
    box((14, 0.3, 6), (X, 2.0, 3), m=mat('#6a5a4a', 0.9))
    banner((X, 1.8, 3.4), '#c8c8c8', 'towers', 1.0, 2.0)
    chair_ = empty('chr', (X, 0.9, 0))
    box((0.7, 0.6, 0.08), (0, 0, 0.44), m=mat('#4a3020', 0.8), parent=chair_)
    box((0.7, 0.1, 1.2), (0, 0.28, 0.9), m=mat('#4a3020', 0.8), parent=chair_)
    w = walder(loc=(X, 0.85, 0), rot=0)
    sit_on(w, 0.48)
    life(c, w, 26, 0.4)
    gb = goblet(hand_obj(w, 1), (0, -0.03, -0.02))
    gb.rotation_euler = (PI, 0, 0)
    aim(w, 1, (X + 0.25, 0.4, 1.15), fw + 4, 8)
    evil_smile(w, fw + 4)
    point((X, -0.8, 2.4), 0, '#ff2a2a', 1.5).data.energy = 200
    cam2, t2 = shot_cam(fw - 3, (X, -1.5, 1.2), (X, 0.85, 1.05), 34)
    cam_move(cam2, t2, c, (X, -1.5, 1.2), (X, -1.2, 1.18), (X, 0.85, 1.05), (X, 0.85, 1.08), fw - 3, c.n)


def s16(c):
    """Casamento roxo: Joffrey envenenado"""
    setup_render(sky='#bfe6c8', sky_strength=1.0)
    grass_ground(0, 60, '#6a9a4a')
    for i, (x, y) in enumerate(((-3.5, 4.0), (3.6, 4.5), (-5.0, 7.0), (5.5, 7.5))):
        tree((x, y, 0), 1.3, '#4aa05a', seed=i)
    long_table((0, 1.9, 0), 4.0, 0.9, 0.78)
    for i, x in enumerate((-1.4, -0.4, 0.6, 1.5)):
        goblet(None, (x, 1.75, 0.79))
    cake = empty('cake', (0.0, 1.95, 0.8))
    cyl(0.3, 0.2, (0, 0, 0.1), m=mat('#f2e8d8', 0.6), parent=cake); cyl(0.2, 0.18, (0, 0, 0.29), m=mat('#f2e8d8', 0.6), parent=cake)
    j = joffrey(loc=(0.15, 0.9, 0), rot=0.2)
    jp = joffrey(name='joffp', skin='#9a7ab8', loc=(0.15, 0.9, 0), rot=0.2)
    life(c, j, 27, 0.5); life(c, jp, 27, 0.5)
    ce = cersei(loc=(-1.2, 1.2, 0), rot=0.5)
    life(c, ce, 28, 0.5)
    gb = goblet(hand_obj(j, 1), (0, -0.03, -0.02)); gb.rotation_euler = (PI, 0, 0)
    fm = wf(c, 'morre'); fe = wf(c, 'envenenado')
    aim(j, 1, front(j, 0.45, 1.2, 0.18), 1)
    aim(j, 1, front(j, 0.12, 1.42, 0.02), wf(c, 'Djófri') + 6, 10)
    smile(j, 8)
    hide_from(j, fm); show_from(jp, fm)
    for k, sx in ((0, -1), (1, 1)):
        aim(jp, k, front(jp, 0.16, 1.15, sx * 0.05))
    shocked(jp, fm + 2)
    fall_back(jp, fe + 4, 12)
    shocked(ce, fm + 6)
    walk_to(ce, fe + 2, fe + 30, (-0.45, 0.55, 0), 2.2)
    turn_to(ce, fe + 36, (0.15, 1.6), 6)
    sun(rot=(0.85, 0.15, 0.5), energy=3.0)
    point((0, -1.0, 2.5), 70, '#fff2dc', 1.2)
    cam, t = camera((0.2, -2.5, 1.5), (0.1, 0.9, 1.25), 32)
    cam_move(cam, t, c, (0.2, -2.5, 1.5), (0.0, -2.9, 1.9), (0.1, 0.9, 1.3), (-0.1, 1.2, 0.7), 1, c.n)


def s17(c):
    """Tyrion acusado; mata o pai Tywin (no vaso) com a besta; foge"""
    setup_render(sky='#3a3030', sky_strength=0.75)
    throne_room(0, 4.0, throne=True)
    ty = tyrion(loc=(0.0, 0.5, 0), rot=0.0)
    ce = cersei(loc=(-0.9, 1.3, 0), rot=0.6)
    life(c, ty, 29, 0.5); life(c, ce, 30, 0.5)
    fa = wf(c, 'acusado')
    aim(ce, 1, (0.0, 0.5, 1.0), fa - 2, 8)
    evil_smile(ce, fa)
    sad(ty, fa + 4)
    for i, x in enumerate((-0.95, 0.95)):
        g = soldier(210 + i, '#a8141e', GOLD, loc=(x, 1.0, 0), rot=0.0)
        life(c, g, 210 + i, 0.3)
    point((0, -1.0, 2.4), 100, '#ffd8a8', 1.5)
    cam, t = camera((0, -2.4, 1.3), (-0.2, 0.8, 1.0), 32)
    fmt = wf(c, 'mata')
    cam_move(cam, t, c, (0, -2.4, 1.3), (-0.1, -2.0, 1.25), (-0.2, 0.8, 1.0), (-0.1, 0.8, 1.0), 1, fmt)
    # vaso: Tywin (x=40)
    X = 40
    stone_floor(X, '#6a6460', '#5a5450', 30, 1.0)
    box((10, 0.3, 5), (X, 1.6, 2.5), m=mat('#5a524c', 0.9))
    toilet((X + 0.55, 1.0, 0), 0)
    box((0.5, 0.3, 0.45), (X + 0.55, 1.3, 0.22), m=mat('#4a3a2a', 0.8))
    tw = tywin(loc=(X + 0.55, 0.95, 0), rot=0)
    sit_on(tw, 0.43)
    life(c, tw, 31, 0.4)
    ty2 = tyrion(name='ty2', cape_=True, loc=(X - 0.75, 0.1, 0), rot=PI / 2 - 0.35)
    life(c, ty2, 32, 0.4)
    xb = crossbow(hand_obj(ty2, 1), (0, 0, 0), (0, 0, 0))
    upd()
    aim(ty2, 1, (X + 0.55, 0.95, 0.95), fmt + 4, 8)
    aim(ty2, 0, (X + 0.2, 0.5, 0.75), fmt + 6, 8)
    shocked(tw, fmt + 8)
    tw.brows_set(fmt + 10, 0.3)
    fT = wf(c, 'Táiuen')
    spike(fT + 8, (X, 0.4, 1.2), '#ffffff', 800, 4)
    for e in tw.eyes:
        key(e, 'scale', fT + 10, (1, 1, 1)); key(e, 'scale', fT + 14, (1, 1, 0.1))
    key(tw.neck, 'rotation_euler', fT + 10, (0, 0, 0)); key(tw.neck, 'rotation_euler', fT + 18, (0.45, 0, 0.2))
    ff = wf(c, 'foge')
    arms_down(ty2, ff - 4)
    walk_to(ty2, ff - 2, c.n, (X - 2.2, -1.0, 0), 2.2)
    point((X, -0.8, 2.2), 80, '#ffd8a8', 1.2)
    cam2, t2 = shot_cam(fmt - 2, (X - 0.1, -2.5, 1.25), (X, 0.6, 0.9), 30)
    cam_move(cam2, t2, c, (X - 0.1, -2.5, 1.25), (X - 0.4, -2.6, 1.3), (X, 0.6, 0.9), (X - 0.6, 0.3, 0.85), fmt - 2, c.n)


def s18(c):
    """Arya foge com o Cao de Caca e vira assassina; Sansa nas maos do Ramsay Bolton"""
    setup_render(sky='#c8d8c0', sky_strength=0.95)
    grass_ground(0, 60, '#7a8a4a')
    box((1.4, 40, 0.02), (0, 8, 0.002), m=mat('#a8946a', 0.95))
    for i, (x, y) in enumerate(((-2.4, 3), (2.6, 4), (-3.0, 7), (3.2, 8), (-2.0, 11), (2.4, 12))):
        tree((x, y, 0), 1.2, '#5a8a3a', seed=i + 3)
    a = arya(loc=(-0.3, 1.8, 0), rot=0)
    h = hound(loc=(0.35, 2.1, 0), rot=0)
    life(c, a, 33, 0.5); life(c, h, 34, 0.5)
    sword(hand_obj(a, 1), (0, 0, 0), (0, 0, 0), L=0.45, s=0.7)
    a.walk(1, wf(c, 'vira') - 6, (-0.3, 1.8, 0), (-0.3, 0.4, 0), 2.2)
    h.walk(1, wf(c, 'vira') - 6, (0.35, 2.1, 0), (0.35, 0.7, 0), 1.7)
    h.brows_set(1, -0.35, 1); a.brows_set(1, -0.2, 1)
    sun(rot=(0.85, 0.15, 0.5), energy=2.8)
    cam, t = camera((0, -2.8, 1.4), (0, 1.0, 1.0), 30)
    fv = wf(c, 'vira')
    cam_move(cam, t, c, (0.1, -2.6, 1.4), (0.0, -2.9, 1.45), (0.0, 1.2, 1.0), (0.0, 0.5, 1.0), 1, fv)
    # Arya assassina (x=40): sala escura com mascaras
    X = 40
    stone_floor(X, '#3a3634', '#2e2a28', 30, 1.0)
    box((10, 0.3, 5), (X, 1.6, 2.5), m=mat('#2a2624', 0.9))
    rnd = random.Random(4)
    for i in range(14):
        sphere(1, (X - 2.2 + (i % 7) * 0.72, 1.42, 1.5 + (i // 7) * 0.8), (0.16, 0.06, 0.2), mat(rnd.choice(['#e8d8c8', '#d8c0a8', '#c8a888']), 0.7))
    a2 = arya(name='arya2', jacket='#2a2a2e', shirt='#2a2a2e', pants='#1e1e22', height=0.9, loc=(X, 0.5, 0), rot=0)
    life(c, a2, 35, 0.4)
    dagger(hand_obj(a2, 1), (0, 0, 0), (0, 0, 0))
    aim(a2, 1, front(a2, 0.4, 1.0, 0.15), fv + 4, 6)
    a2.brows_set(fv + 4, -0.4)
    point((X, -0.6, 2.0), 40, '#8ab8ff', 1.0)
    point((X + 1.5, 0.5, 1.5), 30, '#ffb060', 0.5)
    cam2, t2 = shot_cam(fv - 2, (X, -1.9, 1.3), (X, 0.5, 1.05), 32)
    cam_move(cam2, t2, c, (X, -1.9, 1.3), (X, -1.3, 1.2), (X, 0.5, 1.05), (X, 0.5, 1.15), fv - 2, wf(c, 'Sânsa'))
    # Sansa + Ramsay em Winterfell (x=80)
    X2 = 80
    winterfell(X2, 5.0, bolton=True, f1=c.n, flakes=40)
    s = sansa(dress='#3a3a4a', jacket='#3a3a4a', loc=(X2 - 0.3, 0.6, 0), rot=0.25)
    rm = ramsay(loc=(X2 + 0.75, 0.95, 0), rot=-0.6)
    life(c, s, 36, 0.4); life(c, rm, 37, 0.4)
    sad(s, wf(c, 'cai'))
    s.look(wf(c, 'cai') + 4, 0.15, 0.25, 8)
    fr = wf(c, 'Rãmzei')
    walk_to(rm, fr - 20, fr - 2, (X2 + 0.42, 0.7, 0), 1.8)
    turn_to(rm, fr + 4, (X2 - 0.3, 0.6), 6)
    evil_smile(rm, fr)
    aim(rm, 0, (X2 - 0.1, 0.62, 1.05), fr + 6, 8)
    sun(rot=(0.85, 0.15, 0.5), energy=1.8, color='#d8e0ec')
    point((X2, -1.0, 2.4), 60, '#e8eef8', 1.2)
    cam3, t3 = shot_cam(wf(c, 'Sânsa') - 2, (X2 + 0.1, -2.4, 1.45), (X2 + 0.1, 0.7, 1.25), 32)
    cam_move(cam3, t3, c, (X2 + 0.1, -2.4, 1.45), (X2 + 0.2, -1.9, 1.4), (X2 + 0.1, 0.7, 1.25), (X2 + 0.15, 0.7, 1.3), wf(c, 'Sânsa') - 2, c.n)


def s19(c):
    """Jon traido pela Patrulha (nao grafico) -> Melisandre o traz de volta"""
    setup_render(sky='#141c2e', sky_strength=0.6)
    snow_ground(0, 60, '#9aa8b8')
    box((12, 0.4, 4), (0, 3.0, 2), m=mat('#4a3a2a', 0.85))
    j = jon(loc=(0, 0.9, 0), rot=0)
    life(c, j, 38, 0.5)
    ft = wf(c, 'traído')
    bros = []
    for i, (x, y, r_) in enumerate(((-0.75, 0.55, 0.9), (0.75, 0.55, -0.9), (-0.55, 1.5, 2.3), (0.6, 1.45, -2.3))):
        b = soldier(220 + i, '#1c1c22', None, loc=(x * 1.6, y + (0.5 if y > 1 else -0.5), 0), rot=r_)
        cape(b, '#141418'); life(c, b, 220 + i, 0.4)
        dagger(hand_obj(b, 1), (0, 0, 0), (0, 0, 0))
        walk_to(b, ft - 10, ft + 8, (x, y, 0), 1.8)
        turn_to(b, ft + 12, (0, 0.9), 4)
        b.brows_set(ft, -0.4)
        bros.append(b)
    shocked(j, ft + 6)
    spike(ft + 14, (0, 0.2, 1.6), '#ff3030', 900, 5)
    fall_back(j, ft + 16, 12)
    torch((-1.6, 2.7, 1.8), 1, c.n, 5); torch((1.6, 2.7, 1.8), 1, c.n, 6)
    snowfall(40, (0, 0.5, 0), (5, 4), 4.0, 1, c.n, seed=19)
    point((0, -1.0, 2.5), 50, '#a8b8e8', 1.5)
    cam, t = camera((0, -2.6, 1.6), (0, 0.9, 1.1), 30)
    fmel = wf(c, 'Melisândre')
    cam_move(cam, t, c, (0, -2.6, 1.6), (0, -2.1, 1.8), (0, 0.9, 1.1), (0, 0.9, 0.8), 1, fmel)
    # ressurreicao (x=40)
    X = 40
    stone_floor(X, '#4a4440', '#3e3a36', 30, 1.0)
    box((10, 0.3, 5), (X, 2.0, 2.5), m=mat('#3a342e', 0.9))
    table((X, 0.9, 0), (0.75, 2.0), 0.7, '#5a3e26', '#3e2a1a')
    j2 = jon(name='jon2', cape_=False, loc=(X, -0.02, 0.84), rot=0)
    lie(j2, 0.84, 0.0, 0)
    close_eyes(j2)
    fv = wf(c, 'vida')
    for e in j2.eyes:
        key(e, 'scale', fv - 1, (1, 1, 0.1)); key(e, 'scale', fv + 3, (1.2, 1.2, 1.2))
    key(j2.mouth, 'scale', fv - 1, (1, 1, 0.35)); key(j2.mouth, 'scale', fv + 3, (0.9, 1, 1.6))
    me = melisandre(loc=(X + 0.7, 0.85, 0), rot=-PI / 2 + 0.3)
    life(c, me, 39, 0.4)
    for k in (0, 1):
        aim(me, k, (X + 0.25, 0.75 + k * 0.2, 1.05), wf(c, 'traz'), 10)
    talk(c, me, wf(c, 'traz'), fv - 4, 0.5)
    for i, (x, y) in enumerate(((-0.6, 1.6), (0.6, 1.7), (-1.2, 1.4), (1.3, 1.5), (0, 1.75))):
        candle((X + x, y, 0), 0.3)
    glow = point((X, 0.6, 1.6), 0, '#ff6a3a', 1.0)
    key(glow.data, 'energy', wf(c, 'traz'), 20); key(glow.data, 'energy', fv, 400); key(glow.data, 'energy', fv + 10, 60)
    point((X, -1.0, 2.2), 50, '#ffb080', 1.2)
    cam2, t2 = shot_cam(fmel - 2, (X - 1.3, 0.6, 2.0), (X + 0.1, 1.0, 0.95), 30)
    cam_move(cam2, t2, c, (X - 1.3, 0.6, 2.0), (X - 0.9, 0.8, 1.75), (X + 0.1, 1.0, 0.95), (X, 1.15, 0.9), fmel - 2, c.n)


def heart(loc, s=0.2, parent=None, color='#ff3a5a'):
    p = empty('heart', loc, parent)
    m = mat(color, 0.4, emit=1.5)
    for sx in (-1, 1):
        sphere(0.5 * s, (sx * 0.32 * s, 0, 0.2 * s), m=m, parent=p, seg=20)
    cone(0.78 * s, 0, 0.95 * s, (0, 0, -0.32 * s), (PI, 0, 0), m=m, parent=p, verts=24).scale = (1, 0.62, 1)
    return p

def bran_adult(**kw):
    d = dict(name='brana', height=0.88, body_w=0.85, jacket='#4a4a52', shirt='#4a4a52', pants='#3a3a3e')
    d.update(kw)
    return bran(**d)

def lap_hands(ch):
    p = ch.root.location
    for k, sx in ((0, -1), (1, 1)):
        aim(ch, k, (p.x + sx * 0.1, p.y - 0.22, p.z + 0.62 + 0.05))

def white_eyes(ch, f=None):
    for e in ch.eyes:
        sphere(0.054, (0, -0.002, 0), (1, 0.62, 1.1), mat('#f4f8ff', 0.2, emit=1.6), e)


def s20(c):
    """Batalha dos Bastardos: Jon sozinho contra a cavalaria -> soco no Ramsay -> Rei do Norte"""
    setup_render(sky='#9aa0a8', sky_strength=0.85)
    mud_ground(0, 80, '#5a4a3a')
    j = jon(loc=(0, 0.4, 0), rot=PI)
    life(c, j, 40, 0.5)
    sword(hand_obj(j, 1), (0, 0, 0), (0, 0, 0), L=0.85)
    aim(j, 1, front(j, 0.5, 0.9, 0.25))
    fb = wf(c, 'Batalha')
    aim(j, 1, front(j, 0.3, 1.9, 0.2), fb + 10, 8)
    for i in range(14):
        x = -3.2 + (i % 7) * 1.05 + (0.5 if i >= 7 else 0); y0 = 9.0 + (i // 7) * 1.4
        sd = soldier(300 + i, '#2a1e1e', '#6a5a5a', loc=(x, y0, 0), rot=PI if False else 0.0)
        sword(hand_obj(sd, 1), (0, 0, 0), (0, 0, 0), L=0.7)
        aim(sd, 1, front(sd, 0.3, 1.9, 0.15))
        sd.walk(1, 56, (x, y0, 0), (x * 0.8, y0 - 5.5, 0), 3.2, 0.06)
    for x in (-2.0, 2.2):
        banner((x, 11.5, 3.0), '#1e1414', 'flayed', 1.0, 2.0)
        cyl(0.05, 3.2, (x, 11.55, 1.6), m=mat('#4a3020', 0.8))
    sun(rot=(0.85, 0.15, 0.5), energy=2.0, color='#dde4ee')
    cam, t = camera((0.4, -2.2, 1.0), (0.2, 6, 1.6), 30)
    fv = wf(c, 'vence')
    cam_move(cam, t, c, (0.4, -2.2, 1.0), (0.3, -1.6, 1.1), (0.2, 6, 1.6), (0.1, 6, 1.5), 1, fv - 10)
    # soco no Ramsay (x=40)
    X = 40
    mud_ground(X, 60, '#5a4a3a')
    for i, (x, y) in enumerate(((-3, 4), (3.2, 4.6), (-5.0, 7), (5.5, 7.5))):
        sd = soldier(320 + i, '#5a5a62', STEEL, loc=(X + x, y, 0), rot=0.4 if x > 0 else -0.4)
    j2 = jon(name='jon2', loc=(X - 0.45, 0.5, 0), rot=PI / 2)
    rm = ramsay(loc=(X + 0.32, 0.5, 0), rot=-PI / 2)
    life(c, j2, 41, 0.5); life(c, rm, 42, 0.5)
    j2.brows_set(fv, -0.45, 1)
    evil_smile(rm, fv - 6)
    fp = fv + 4
    aim(j2, 1, (X + 0.0, 0.48, 1.25), fp - 6, 4)
    aim(j2, 1, (X + 0.32, 0.5, 1.38), fp, 3)
    j2.arm(1, fp + 10, (0, 0.12, 0), ease=8)
    shocked(rm, fp)
    fall_back(rm, fp + 1, 9)
    face(rm, fp + 1, -PI / 2, 1)
    sun(rot=(0.85, 0.15, 0.5), energy=2.0, color='#dde4ee')
    point((X, -1.0, 2.4), 60, '#f0f4ff', 1.2)
    cam2, t2 = shot_cam(fv - 6, (X - 0.1, -2.0, 1.35), (X - 0.05, 0.5, 1.15), 32)
    cam_move(cam2, t2, c, (X - 0.1, -2.0, 1.35), (X, -1.7, 1.3), (X - 0.05, 0.5, 1.15), (X + 0.05, 0.5, 1.1), fv - 6, wf(c, 'vira'))
    # Rei do Norte (x=80)
    X2 = 80
    stone_floor(X2, '#6a5a4a', '#5a4a3a', 30, 1.0)
    box((14, 0.3, 6), (X2, 2.6, 3), m=mat('#5a4a3a', 0.9))
    for x in (-1.6, 1.6):
        banner((X2 + x, 2.4, 3.8), '#f2f0ea', 'wolf', 1.0, 2.0)
    j3 = jon(name='jon3', loc=(X2, 1.4, 0), rot=0)
    life(c, j3, 43, 0.4)
    fr = wf(c, 'Rei')
    smile(j3, fr + 6)
    for i, (x, y) in enumerate(((-1.4, 0.6), (-0.8, 0.0), (0.8, 0.0), (1.4, 0.6), (-1.9, 1.4), (1.9, 1.4))):
        lord = soldier(340 + i, ['#4a3a2e', '#5a4a3a', '#3a3a3e'][i % 3], None, loc=(X2 + x, y, 0), rot=math.atan2(-x, -(1.4 - y)) if False else (0.6 if x < 0 else -0.6) + PI)
        turn_to(lord, 2, (X2, 1.4), 1)
        sword(hand_obj(lord, 1), (0, 0, 0), (0, 0, 0), L=0.7)
        aim(lord, 1, front(lord, 0.2, 1.95, 0.1), fr + 2 + i % 3 * 2, 6)
        life(c, lord, 340 + i, 0.4)
    torch((X2 - 2.6, 2.3, 2.0), 1, c.n, 7); torch((X2 + 2.6, 2.3, 2.0), 1, c.n, 8)
    point((X2, -1.0, 2.5), 90, '#ffd8a8', 1.5)
    cam3, t3 = shot_cam(wf(c, 'vira') - 2, (X2, -2.4, 1.6), (X2, 1.2, 1.35), 30)
    cam_move(cam3, t3, c, (X2, -2.6, 1.6), (X2, -3.4, 1.85), (X2, 1.2, 1.35), (X2, 1.0, 1.4), wf(c, 'vira') - 2, c.n)


def s21(c):
    """Cersei explode o Septo com fogo verde e vira rainha"""
    setup_render(sky='#c8b8a8', sky_strength=0.85)
    red_room(0, 2.0)
    window((0.55, 1.88, 1.6), 0, 1.0, 1.2, '#cfe8ff', emit=1.0)
    ce = cersei(dress='#1e1a1e', jacket='#1e1a1e', loc=(-0.3, 0.7, 0), rot=0.35)
    life(c, ce, 44, 0.4)
    gb = goblet(hand_obj(ce, 1), (0, -0.03, -0.02)); gb.rotation_euler = (PI, 0, 0)
    aim(ce, 1, front(ce, 0.3, 1.15, 0.2))
    evil_smile(ce, 8)
    point((0, -1.0, 2.4), 90, '#ffd8b0', 1.2)
    fe = wf(c, 'explode')
    cam, t = camera((-0.1, -1.8, 1.45), (-0.25, 0.7, 1.35), 32)
    cam_move(cam, t, c, (-0.1, -1.9, 1.45), (-0.15, -1.6, 1.42), (-0.25, 0.7, 1.35), (-0.25, 0.7, 1.38), 1, fe)
    # explosao verde (x=40)
    X = 40
    mud_ground(X, 80, '#8a7a5a')
    for i in range(14):
        rnd = random.Random(i)
        house((X + rnd.uniform(-7, 7), rnd.uniform(2, 5) * (1 if i % 2 else 1.6), 0), rnd.uniform(1, 1.6), 1, rnd.uniform(1, 1.5), '#e0ccaa', '#b8462a')
    sp_ = sept((X, 11, 0), 1.0)
    gf = empty('gboom', (X, 11, 3.5))
    for k, (dx, dz, sc) in enumerate(((0, 0, 4.2), (-2.5, -1.0, 3.0), (2.6, -0.8, 3.2), (0, 2.5, 3.0))):
        sphere(sc, (dx, 0, dz), m=mat(['#4aff5a', '#2adf3a', '#8aff6a', '#3aef4a'][k], 0.5, emit=8), parent=gf, seg=32)
    key(gf, 'scale', fe - 1, (0, 0, 0), 'CONSTANT'); key(gf, 'scale', fe, (0.1, 0.1, 0.1)); key(gf, 'scale', fe + 8, (1.1, 1.1, 1.1))
    key(gf, 'scale', fe + 40, (1.35, 1.35, 1.35))
    hide_between(sp_, None, fe + 4)
    puffs((X, 11, 6), fe + 6, wf(c, 'vira'), '#3a5a3a', n=10, seed=21, rise=5, s=2.0, spread=3, every=3)
    spike(fe, (X, 6, 4), '#4aff5a', 9000, 14, 3.0)
    sun(rot=(0.85, 0.15, 0.5), energy=2.4)
    cam2, t2 = shot_cam(fe, (X, -6.0, 2.2), (X, 10, 4.0), 28)
    cam_move(cam2, t2, c, (X, -6.0, 2.2), (X, -7.5, 2.4), (X, 10, 4.0), (X, 10, 4.6), fe, wf(c, 'vira'))
    # rainha no trono (x=80)
    X2 = 80
    throne_room(X2, 4.0)
    ce2 = cersei(name='cersei2', crown_=True, dress='#1e1a1e', jacket='#1e1a1e', loc=(X2, 3.15, 0), rot=0)
    sit_on(ce2, 0.55)
    life(c, ce2, 45, 0.4)
    fr = wf(c, 'rainha')
    evil_smile(ce2, fr + 4)
    point((X2, 1.0, 3.0), 150, '#ffd8a8', 2.0)
    cam3, t3 = shot_cam(wf(c, 'vira') - 2, (X2, -1.4, 1.65), (X2, 3.1, 1.4), 32)
    cam_move(cam3, t3, c, (X2, -1.4, 1.65), (X2, 0.9, 1.45), (X2, 3.1, 1.4), (X2, 3.1, 1.38), wf(c, 'vira') - 2, c.n)


def s22(c):
    """Daenerys chega com dragoes, exercito (Imaculados) e Tyrion como conselheiro"""
    setup_render(sky='#a8c8e8', sky_strength=0.95)
    sea(200, '#2a6a9a', z=-0.02)
    box((80, 14, 0.04), (0, -3.0, 0.0), m=mat('#c8b890', 0.9))
    for i, (x, y, r_) in enumerate(((-4, 9, 0.2), (3.5, 11, -0.2), (-0.5, 14, 0.1), (7, 13, -0.3), (-7.5, 12.5, 0.3))):
        ship((x, y, 0), r_, '#1a1a1a', '#3a2a1e', 1.0, 'dragon' if i < 2 else None)
    dn = dany(dress='#e8e8ec', jacket='#e8e8ec', loc=(-0.25, 1.8, 0), rot=0)
    cape(dn, '#c8c8d0', tilt=0.15)
    ty = tyrion(cape_=True, loc=(0.42, 2.0, 0), rot=0)
    for ch, s_ in ((dn, 46), (ty, 47)):
        life(c, ch, s_, 0.4)
    dn.walk(1, 70, (-0.25, 1.8, 0), (-0.25, 0.3, 0), 1.7)
    ty.walk(1, 70, (0.42, 2.0, 0), (0.42, 0.5, 0), 2.4)
    for i in range(10):
        u = unsullied(400 + i, loc=(-1.6 + (i % 5) * 0.8, 3.0 + (i // 5) * 0.8, 0), rot=0)
        sp = empty('spear', (0, 0, 0), hand_obj(u, 1))
        cyl(0.02, 1.9, (0, 0, -0.2), m=mat('#6a4a2e', 0.8), parent=sp, verts=8)
        u.walk(1, 70, (-1.6 + (i % 5) * 0.8, 3.0 + (i // 5) * 0.8, 0), (-1.6 + (i % 5) * 0.8, 1.6 + (i // 5) * 0.8, 0), 1.7)
    fd = wf(c, 'dragões')
    d = dragon((-7, 6, 5), (0.1, 0, -PI / 2 + 0.3), 1.2)
    dragon_flap(d, 1, c.n, speed=9)
    key(d['root'], 'location', fd - 10, (-8, 7, 5.5), 'LINEAR'); key(d['root'], 'location', fd + 50, (8, 9, 4.8), 'LINEAR')
    smile(dn, fd + 4)
    ft = wf(c, 'Tírion')
    smile(ty, ft + 4)
    ty.look(ft + 2, -0.15, 0.4, 8)
    sun(rot=(0.85, 0.15, 0.5), energy=3.0)
    cam, t = camera((0, -2.8, 1.5), (0, 1.2, 1.6), 30)
    cam_path(cam, t, [(1, (0.1, -3.4, 1.4), (0, 1.5, 1.9)), (fd + 20, (0.1, -2.9, 1.4), (-0.2, 1.0, 2.2)),
                      (ft - 4, (0.15, -2.4, 1.35), (0.1, 0.5, 1.15)), (c.n, (0.35, -1.9, 1.2), (0.3, 0.5, 1.0))])


def s23(c):
    """Jon e Daenerys se apaixonam... ela e tia dele"""
    setup_render(sky='#2a2430', sky_strength=0.7)
    stone_floor(0, '#4a4440', '#3e3a36', 30, 1.0)
    sphere(1, (0, 2.5, 1.0), (5.0, 1.5, 3.5), mat('#3a3430', 0.95), seg=32)
    fo, fl = flames((-0.9, 1.2, 0), 5, 0.2, 0.5, seed=7)
    flicker(fl, 1, c.n, 7)
    j = jon(loc=(0.36, 0.55, 0), rot=-PI / 2 + 0.45)
    dn = dany(dress='#e8e8ec', jacket='#e8e8ec', loc=(-0.36, 0.55, 0), rot=PI / 2 - 0.45)
    life(c, j, 48, 0.5); life(c, dn, 49, 0.5)
    fa = wf(c, 'apaixonam')
    smile(j, fa); smile(dn, fa + 2)
    aim(j, 0, (0.0, 0.42, 0.85), fa - 4, 10); aim(dn, 1, (0.0, 0.42, 0.85), fa - 2, 10)
    for k, (x, z) in enumerate(((-0.15, 2.05), (0.18, 2.2), (0.0, 2.45))):
        hp = heart((x, 0.5, z), 0.14 + k * 0.03)
        pop_in(hp, fa + k * 5, 8)
        hide_between(hp, None, wf(c, 'problema'))
    ft = wf(c, 'tia')
    arms_down(j, ft - 4); arms_down(dn, ft - 2)
    shocked(j, ft + 2)
    j.look(ft + 2, 0, 0.3, 6)
    point((-0.9, 1.0, 1.0), 120, '#ff9a4a', 0.5)
    point((0, -1.0, 2.2), 40, '#ffd8b0', 1.2)
    cam, t = camera((0, -2.4, 1.45), (0, 0.55, 1.35), 32)
    cam_path(cam, t, [(1, (0, -2.4, 1.45), (0, 0.55, 1.35)), (ft - 6, (0, -2.0, 1.45), (0, 0.55, 1.38)),
                      (ft + 4, (0.35, -0.8, 1.45), (0.36, 0.55, 1.38)), (c.n, (0.35, -0.65, 1.45), (0.36, 0.55, 1.38))])


def s24(c):
    """Bran revela: Jon e um Targaryen, com mais direito ao trono"""
    setup_render(sky='#b8c8d8', sky_strength=0.9)
    godswood(0, night=False)
    b = bran_adult(loc=(0, 1.2, 0), rot=0)
    wc = wheelchair((0, 1.2, 0), 0, bell=False)
    sit_on(b, 0.5)
    lap_hands(b)
    life(c, b, 50, 0.3)
    white_eyes(b)
    snowfall(40, (0, 0.5, 0), (5, 4), 4.0, 1, c.n, seed=24)
    sun(rot=(0.85, 0.15, 0.5), energy=2.2, color='#e8f0ff')
    cam, t = camera((0, -2.0, 1.3), (0, 1.2, 1.1), 32)
    fdj = wf(c, 'Djón')
    cam_move(cam, t, c, (0, -2.1, 1.3), (0, -1.7, 1.25), (0, 1.2, 1.12), (0, 1.2, 1.12), 1, fdj)
    # Jon: lobo -> dragao (x=40)
    X = 40
    stone_floor(X, '#6a6460', '#5a5450', 30, 1.0)
    box((12, 0.3, 6), (X, 2.4, 3), m=mat('#5a524c', 0.9))
    bw = banner((X, 2.2, 3.6), '#f2f0ea', 'wolf', 1.4, 2.8)
    bd = banner((X, 2.15, 3.6), '#141414', 'dragon', 1.4, 2.8)
    ft = wf(c, 'Targárien')
    hide_between(bw, None, ft)
    pop_in(bd, ft, 8)
    j = jon(loc=(X, 0.7, 0), rot=0)
    life(c, j, 51, 0.4)
    shocked(j, ft + 4)
    j.brows_set(ft + 30, 0.0)
    fd = wf(c, 'direito')
    th = iron_throne((X + 1.6, 1.6, 0), -0.4, 0.5)
    pop_in(th, fd, 8)
    point((X, -1.0, 2.5), 100, '#ffd8a8', 1.5)
    spike(ft, (X, 0.5, 2.5), '#ff5a3a', 500, 6)
    cam2, t2 = shot_cam(fdj - 2, (X, -2.4, 1.55), (X, 0.9, 1.6), 30)
    cam_move(cam2, t2, c, (X, -2.4, 1.55), (X + 0.2, -2.8, 1.6), (X, 0.9, 1.6), (X + 0.3, 0.9, 1.4), fdj - 2, wf(c, 'que'))
    # Daenerys com ciume (x=80)
    X2 = 80
    stone_floor(X2, '#6a6460', '#5a5450', 30, 1.0)
    box((12, 0.3, 6), (X2, 2.0, 3), m=mat('#3a3434', 0.9))
    banner((X2, 1.8, 3.6), '#141414', 'dragon', 1.2, 2.4)
    dn = dany(dress='#2a1e22', jacket='#2a1e22', loc=(X2, 0.7, 0), rot=0)
    life(c, dn, 52, 0.4)
    dn.brows_set(wf(c, 'que') + 4, -0.45)
    key(dn.mouth, 'scale', wf(c, 'que') + 4, (0.7, 1, 0.3))
    point((X2, -1.0, 2.4), 80, '#ffd8b0', 1.2)
    cam3, t3 = shot_cam(wf(c, 'que') - 2, (X2, -1.5, 1.4), (X2, 0.7, 1.3), 34)
    cam_move(cam3, t3, c, (X2, -1.5, 1.4), (X2, -1.15, 1.38), (X2, 0.7, 1.3), (X2, 0.7, 1.32), wf(c, 'que') - 2, c.n)


def s25(c):
    """Rei da Noite ataca; Arya salta do nada e o destroi com uma facada"""
    setup_render(sky='#141c2e', sky_strength=0.65)
    godswood(0, night=True)
    b = bran_adult(loc=(0, 2.1, 0), rot=0)
    wheelchair((0, 2.1, 0), 0, bell=False)
    sit_on(b, 0.5)
    lap_hands(b)
    life(c, b, 53, 0.3)
    white_eyes(b)
    nk = night_king(loc=(0.6, -0.6, 0), rot=PI)
    life(c, nk, 54, 0.3)
    nk.walk(4, 80, (0.6, -0.6, 0), (0.15, 1.15, 0), 1.2)
    face(nk, 6, PI - 0.25, 4)
    wights = []
    for i, (x, y) in enumerate(((-2.0, -1.2), (-2.7, -0.4), (-1.7, 0.2), (2.1, -1.0), (2.8, -0.2), (1.9, 0.4), (-2.4, 1.0))):
        w = wight(500 + i, loc=(x, y - 1.0, 0), rot=PI + (0.35 if x < 0 else -0.35))
        life(c, w, 500 + i, 0.5)
        aim(w, 0, front(w, 0.5, 1.1, -0.1)); aim(w, 1, front(w, 0.5, 1.1, 0.1))
        w.walk(4, 90, (x, y - 1.0, 0), (x * 0.92, y, 0), 1.2)
        wights.append(w)
    fs = wf(c, 'salta'); fm = wf(c, 'mata')
    # Arya: salto em arco por tras dele
    a = arya(jacket='#2a2a2e', shirt='#2a2a2e', pants='#1e1e22', height=0.9, loc=(-1.3, 2.7, 0), rot=PI / 2 + 0.5)
    life(c, a, 55, 0.4)
    dg = dagger(hand_obj(a, 1), (0, 0, 0), (0, 0, 0), color='#3a3a44')
    hide_between(a.root, fs - 6, None)
    key(a.root, 'location', fs - 2, (-1.3, 2.7, 0.0))
    key(a.root, 'location', fs + 8, (-0.8, 1.9, 1.3))
    key(a.root, 'location', fm - 2, (-0.25, 1.05, 0.25))
    key(a.root, 'location', fm + 2, (-0.18, 1.05, 0.0))
    for l in a.legs:
        key(l, 'rotation_euler', fs - 2, (0, 0, 0)); key(l, 'rotation_euler', fs + 6, (-0.9, 0, 0)); key(l, 'rotation_euler', fm, (0, 0, 0))
    aim(a, 1, (0.15, 1.1, 1.2), fs + 4, 6)
    a.brows_set(fs, -0.45, 2)
    shocked(nk, fm - 2)
    turn_to(nk, fs + 10, (-0.8, 1.9), 6)
    # estilhacos de gelo
    shards = empty('shards', (0.15, 1.15, 1.1))
    rnd = random.Random(25)
    for k in range(26):
        d = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-0.2, 1))).normalized() * rnd.uniform(0.8, 1.8)
        o = cone(0.05, 0, 0.16, (0, 0, 0), (rnd.uniform(0, 3), rnd.uniform(0, 3), 0), m=mat('#bfeaff', 0.1, emit=2.5), parent=shards, verts=5)
        key(o, 'location', fm + 1, (0, 0, 0), 'LINEAR'); key(o, 'location', fm + 22, tuple(d))
    hide_between(shards, fm + 1, fm + 26)
    hide_from(nk, fm + 2)
    spike(fm + 1, (0.15, 0.6, 1.5), '#9adfff', 500, 10, 1.0)
    for i, w in enumerate(wights):
        fall_back(w, fm + 4 + i % 3 * 2, 10)
    point((0, -1.0, 2.6), 40, '#8ab8ff', 1.5)
    point((0.6, 0.2, 1.5), 25, '#7ac8ff', 0.6)
    cam, t = camera((0.4, -3.4, 1.7), (0.2, 1.2, 1.15), 30)
    cam_path(cam, t, [(1, (0.4, -3.4, 1.8), (0.25, 1.0, 1.15)), (fs - 6, (0.3, -2.2, 1.6), (0.15, 1.2, 1.15)),
                      (fm + 2, (0.2, -1.4, 1.5), (0.0, 1.2, 1.05)), (c.n, (0.2, -1.8, 1.55), (0.0, 1.3, 1.0))])


def s26(c):
    """Daenerys perde a cabeca: queima a capital montada no dragao; Cersei e Jaime nos escombros"""
    setup_render(sky='#e8784a', sky_strength=0.7)
    mud_ground(0, 80, '#7a6a52')
    kings_landing((0, 9, 0), seed=8, n=46, R=9.0, burning=30, f0=wf(c, 'queima'), f1=c.n)
    d = dragon((-1.2, -0.2, 2.2), (0.1, 0, -0.35), 1.0)
    dragon_flap(d, 1, c.n, speed=9)
    dn = dany(dress='#2a1e22', jacket='#2a1e22', loc=(0, 0.15, 0.32), rot=0)
    dn.root.parent = d['root']; dn.root.location = (0, 0.12, 0.3)
    sit_on(dn, 0.3)
    dn.root.location.y = 0.12
    dn.legs[0].rotation_euler = (-0.5, 1.0, 0); dn.legs[1].rotation_euler = (-0.5, -1.0, 0)
    life(c, dn, 56, 0.4)
    fp = wf(c, 'perde')
    dn.brows_set(fp, -0.5)
    key(dn.mouth, 'scale', fp, (1.2, 1, 0.3))
    fq = wf(c, 'queima')
    key(d['root'], 'location', 1, (-1.2, -0.2, 2.2)); key(d['root'], 'location', fq - 6, (-1.0, 0.0, 2.3))
    key(d['root'], 'location', fq + 40, (2.5, 3.5, 3.2), 'LINEAR')
    fire_breath(d, fq, fq + 40, L=4.5, s=1.2)
    sun(rot=(1.2, 0.0, -0.9), energy=2.4, color='#ffb070')
    point((0, 4, 3), 900, '#ff7a2a', 6.0)
    point((-1.2, -1.5, 2.6), 80, '#ffd8b0', 1.0)
    cam, t = camera((-1.0, -1.9, 3.6), (-1.15, -0.05, 2.9), 32)
    cam_path(cam, t, [(1, (-1.05, -1.95, 3.55), (-1.18, -0.08, 2.92)), (fq - 8, (-0.9, -2.2, 3.6), (-1.0, 0.0, 2.95)),
                      (fq + 6, (0.0, -5.5, 2.6), (0.5, 4.0, 3.0)), (wf(c, 'Cérsei'), (0.5, -7.0, 2.8), (1.0, 6.0, 3.2))])
    # Cersei e Jaime nos escombros (x=40)
    X = 40
    stone_floor(X, '#4a4440', '#3e3a36', 30, 1.0)
    box((10, 0.3, 5), (X, 1.6, 2.5), m=mat('#3a3430', 0.9))
    ce = cersei(dress='#1e1a1e', jacket='#1e1a1e', loc=(X - 0.25, 0.5, 0), rot=PI / 2 - 0.5)
    ja = jaime(loc=(X + 0.25, 0.5, 0), rot=-PI / 2 + 0.5)
    life(c, ce, 57, 0.4); life(c, ja, 58, 0.4)
    fc = wf(c, 'Cérsei')
    aim(ce, 0, (X + 0.05, 0.4, 1.2), fc, 8); aim(ja, 1, (X - 0.05, 0.4, 1.2), fc + 2, 8)
    sad(ce, fc + 4); sad(ja, fc + 6)
    fmr = wf(c, 'morrem')
    rnd = random.Random(26)
    for k in range(34):
        x = X + rnd.uniform(-1.6, 1.6); y = rnd.uniform(-0.2, 1.4); f0 = fmr - 14 + rnd.randint(0, 30)
        o = box((rnd.uniform(0.25, 0.5), rnd.uniform(0.25, 0.45), rnd.uniform(0.2, 0.35)), (x, y, 4.0), (rnd.uniform(0, 1), rnd.uniform(0, 1), 0), m=mat(rnd.choice(['#6a625a', '#5a524a', '#7a7268']), 0.9))
        zf = 0.15 + (k % 5) * 0.22 if abs(x - X) < 0.6 else 0.15
        key(o, 'location', f0, (x, y, 4.0), 'LINEAR'); key(o, 'location', f0 + 10, (x, y, zf), 'CONSTANT')
        hide_between(o, f0, None)
    puffs((X, 0.7, 0.3), fmr + 6, c.n, '#7a7068', n=6, seed=26, rise=1.0, s=0.35, spread=1.0, every=4)
    point((X, -1.0, 2.2), 60, '#ffb080', 1.2)
    cam2, t2 = shot_cam(fc - 3, (X, -2.0, 1.5), (X, 0.5, 1.3), 32)
    cam_move(cam2, t2, c, (X, -2.0, 1.5), (X, -2.4, 1.6), (X, 0.5, 1.3), (X, 0.5, 1.1), fc - 3, c.n)


def s27(c):
    """Jon mata a mulher que ama (abraco, nao grafico); o dragao derrete o Trono de Ferro"""
    setup_render(sky='#5a5450', sky_strength=0.7)
    th = throne_room(0, 4.0, dark=True, cols=False)
    rnd_ = random.Random(27)
    am = mat('#8a8480', 0.9)
    for k in range(60):                                   # cinzas caindo
        x, y = rnd_.uniform(-2.5, 2.5), rnd_.uniform(0.2, 3.5)
        z0 = rnd_.uniform(0.5, 4.0)
        o = sphere(0.018, (x, y, z0), m=am, seg=6)
        key(o, 'location', 1, (x, y, z0), 'LINEAR'); key(o, 'location', c.n, (x + 0.3, y, z0 - c.n * 0.012), 'LINEAR')
    for o in [o for o in bpy.data.objects if o.name.startswith('snow') or o.type == 'MESH' and o.data.materials and o.data.materials[0].name.startswith('m') and False]:
        pass
    j = jon(loc=(0.3, 0.6, 0), rot=-PI / 2 + 0.35)
    dn = dany(dress='#2a1e22', jacket='#2a1e22', loc=(-0.24, 0.6, 0), rot=PI / 2 - 0.35)
    life(c, j, 59, 0.4); life(c, dn, 60, 0.4)
    fm = wf(c, 'mata')
    aim(j, 0, (0.0, 0.55, 1.15), fm - 6, 8); aim(j, 1, (-0.05, 0.75, 1.0), fm - 4, 8)
    aim(dn, 0, (0.05, 0.75, 1.15), fm - 6, 8); aim(dn, 1, (0.08, 0.5, 1.0), fm - 4, 8)
    sad(j, fm + 2)
    shocked(dn, fm + 8)
    for e in dn.eyes:
        key(e, 'scale', fm + 24, (1.2, 1.2, 1.2)); key(e, 'scale', fm + 30, (1, 1, 0.1))
    fall_back(dn, fm + 34, 14)
    face(dn, fm + 34, PI / 2 - 0.35, 2)
    fd = wf(c, 'dragão'); fdr = wf(c, 'derrete')
    d = dragon((2.3, 2.5, 1.9), (0.1, 0, -1.45), 0.7)
    dragon_flap(d, fd - 8, c.n, speed=10, amp=0.35)
    pop_in(d['root'], fd - 6, 10)
    fire_breath(d, fdr - 6, fdr + 26, L=3.5, s=1.2)
    # trono derrete: fica laranja e afunda
    hot = mat('#ff7a1a', 0.4, emit=4.0)
    for o in th.children_recursive:
        pass
    key(th, 'scale', fdr + 4, (1, 1, 1)); key(th, 'scale', c.n - 4, (1.15, 1.1, 0.12))
    glow = point((0, 3.0, 1.0), 0, '#ff7a1a', 1.2)
    key(glow.data, 'energy', fdr, 0); key(glow.data, 'energy', fdr + 10, 900)
    point((0, -1.0, 2.6), 80, '#d8d0c8', 1.5)
    cam, t = camera((0.05, -2.1, 1.5), (0.05, 0.6, 1.35), 32)
    cam_path(cam, t, [(1, (0.05, -2.1, 1.5), (0.05, 0.6, 1.35)), (fd - 10, (0.05, -1.8, 1.45), (0.05, 0.6, 1.3)),
                      (fd - 4, (0.6, -3.8, 1.7), (0.8, 2.8, 1.5)), (c.n, (0.5, -3.4, 1.6), (0.7, 2.8, 1.3))])


def s28(c):
    """quem vira rei? Bran. Voce concorda com esse final?"""
    setup_render(sky='#c8d8e8', sky_strength=0.95)
    stone_floor(0, '#a89c88', '#988c78', 40, 1.2)
    box((30, 0.6, 3.0), (0, 6.0, 1.5), m=mat('#8a7e6c', 0.9))
    b = bran_adult(loc=(0, 1.6, 0), rot=0)
    wheelchair((0, 1.6, 0), 0, bell=False)
    sit_on(b, 0.5)
    lap_hands(b)
    life(c, b, 61, 0.3)
    fb = wf(c, 'Brân')
    cr = crown(b, GOLD, spike=0.1)
    pop_in(cr, fb + 4, 8)
    smile(b, fb + 10)
    seats = [(sansa, dict(dress='#3a4a6a', jacket='#3a4a6a'), (-1.7, 0.6), 0.9), (arya, {}, (-1.15, 1.2), 0.6),
             (tyrion, dict(cape_=True), (1.0, 1.25), -0.6), (sam, {}, (1.65, 0.6), -0.9)]
    for i, (fn, kw, (x, y), r_) in enumerate(seats):
        ch = fn(loc=(x, y, 0), rot=r_, **kw)
        life(c, ch, 62 + i, 0.4)
        ch.look(fb + 2, 0, (-0.3 if x > 0 else 0.3), 8)
    ty = [o for o in bpy.data.objects if o.name == 'tyrion_root'][0]
    pin = hand_pin(None, (1.0 - 0.1, 1.25 - 0.13, 0.55), (0, 0, -0.6), 1.0)
    pin.parent = [o for o in bpy.data.objects if o.name == 'tyrion_chest'][0]
    pin.location = (-0.1, -0.125, 0.25); pin.rotation_euler = (0, 0, 0)
    for i in range(10):
        x = -4.5 + i * 1.0
        if abs(x) < 2.3:
            continue
        p = crowd_person(600 + i, (x, 3.6 + abs(x) * 0.2, 0), 0.0 if x == 0 else (0.25 if x < 0 else -0.25))
        life(c, p, 600 + i, 0.4)
    for x in (-3.0, 3.0):
        banner((x, 5.65, 2.8), '#f2f0ea', 'wolf', 1.0, 2.0)
    sun(rot=(0.85, 0.15, 0.5), energy=2.6)
    point((0, -1.0, 2.6), 70, '#fff2dc', 1.5)
    cam, t = camera((0, -3.0, 1.5), (0, 1.6, 1.2), 30)
    fe = wf(c, 'E', 2)
    cam_path(cam, t, [(1, (0, -3.6, 1.7), (0, 1.6, 1.2)), (fb + 4, (0, -1.6, 1.35), (0, 1.6, 1.2)),
                      (fe - 4, (0, -1.3, 1.32), (0, 1.6, 1.22)), (fe + 40, (0, -5.0, 3.2), (0, 1.6, 0.9)), (c.n, (0, -5.6, 3.5), (0, 1.6, 0.9))])

SHOTS = {k: v for k, v in globals().items() if re.fullmatch(r's\d\d', k)}
