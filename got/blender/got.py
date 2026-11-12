# Game of Thrones: personagens + cenarios (estilo boneco de brinquedo).
# Convencao: frente = -Y (como os personagens com rot=0).
import bpy, math, random
from mathutils import Vector
from lib import *
from props import flames, flicker, puffs, snow_pine, pine, snowfall, toilet, wheelchair, candle, table, bed, sea, waves, cloud

PI = math.pi
GOLD = '#e0b43a'
STEEL = '#a8b0ba'


def _mesh(name, verts, faces, m, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), smooth=False):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces); me.update()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    o.data.materials.append(m if not isinstance(m, str) else mat(m))
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    if parent is not None:
        o.parent = parent
    return o


def _dims(ch):
    bpy.context.view_layer.update()
    h = ch.leg_len / 0.52
    th = 0.56 * h
    tw = ch.torso.dimensions.x / 2
    return h, th, tw


# ------------------------------------------------------------------ acessorios de personagem
def cape(ch, color='#2a2a2e', length=None, tilt=0.1, width=1.0):
    h, th, tw = _dims(ch)
    L = length or (th + ch.leg_len * 0.82)
    p = empty(ch.name + '_cape', (0, 0.135, th - 0.02), ch.chest, rot=(tilt, 0, 0))
    box(((2 * tw + 0.1) * width, 0.025, L), (0, 0, -L / 2), m=mat(color, 0.85), parent=p, bevel=0.012)
    return p


def fur(ch, color='#8a8078', s=1.0):
    h, th, tw = _dims(ch)
    torus(max(0.15, tw * 0.82), 0.065 * s, (0, 0.02, th - 0.01), m=mat(color, 0.95), parent=ch.chest, scale=(1, 0.85, 1))


def crown(ch, color=GOLD, r=0.255, z=0.23, n=7, spike=0.11, emit=0.0, bald=False):
    """coroa de pontas no topo da cabeca"""
    if bald:
        r, z = 0.215, 0.18
    m = mat(color, 0.25, metal=0.85, emit=emit)
    p = empty(ch.name + '_crown', (0, 0.01, z), ch.head)
    cyl(r, 0.07, (0, 0, 0), m=m, parent=p, verts=24)
    for i in range(n):
        a = 2 * PI * i / n
        cone(0.035, 0, spike, (math.sin(a) * r * 0.97, -math.cos(a) * r * 0.97, 0.035 + spike / 2), m=m, parent=p, verts=8)
    return p


def ice_crown(ch):
    m = mat('#cfeeff', 0.15, emit=0.6)
    p = empty(ch.name + '_icecrown', (0, 0.02, 0.0), ch.head)
    for i in range(9):
        a = -PI * 0.75 + 1.5 * PI * i / 8
        x, y = math.sin(a) * 0.2, -math.cos(a) * 0.2 + 0.02
        cone(0.035, 0, 0.15, (x, y, 0.24), rot=(math.cos(a) * 0.35, -math.sin(a) * 0.35, 0), m=m, parent=p, verts=6)
    return p


def sword(parent, loc=(0, 0, -0.47), rot=(0, 0, 0), L=0.75, blade=STEEL, hilt='#3a2a1e', guard='#8a8a92', s=1.0):
    """lamina ao longo de -Z local a partir do punho"""
    p = empty('sword', loc, parent, rot)
    bm = mat(blade, 0.2, metal=0.9)
    box((0.06 * s, 0.014 * s, L * s), (0, 0, -L * s / 2 - 0.05 * s), m=bm, parent=p, bevel=0.004)
    cone(0.042 * s, 0, 0.08 * s, (0, 0, -L * s - 0.09 * s), (PI, 0, 0), m=bm, parent=p, verts=4)
    box((0.22 * s, 0.04 * s, 0.035 * s), (0, 0, -0.04 * s), m=mat(guard, 0.3, metal=0.7), parent=p, bevel=0.008)
    cyl(0.022 * s, 0.16 * s, (0, 0, 0.04 * s), m=hilt, parent=p, verts=12)
    sphere(0.035 * s, (0, 0, 0.13 * s), m=mat(guard, 0.3, metal=0.7), parent=p, seg=12)
    return p


def dagger(parent, loc=(0, 0, -0.47), rot=(0, 0, 0), color=STEEL):
    return sword(parent, loc, rot, L=0.22, blade=color, s=0.8)


def goblet(parent=None, loc=(0, 0, 0), color=GOLD, wine='#6a0a1e'):
    p = empty('goblet', loc, parent)
    m = mat(color, 0.25, metal=0.85)
    cyl(0.045, 0.012, (0, 0, 0.006), m=m, parent=p, verts=16)
    cyl(0.01, 0.07, (0, 0, 0.045), m=m, parent=p, verts=8)
    cone(0.02, 0.05, 0.08, (0, 0, 0.12), m=m, parent=p, verts=16)
    cyl(0.044, 0.005, (0, 0, 0.152), m=mat(wine, 0.2), parent=p, verts=16)
    return p


def hand_pin(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0):
    """broche da Mao do Rei"""
    p = empty('pin', loc, parent, rot)
    m = mat(GOLD, 0.2, metal=0.9)
    box((0.09 * s, 0.015 * s, 0.08 * s), (0, 0, 0), m=m, parent=p, bevel=0.01)
    for i in range(4):
        box((0.018 * s, 0.015 * s, 0.07 * s), (-0.03 * s + i * 0.02 * s, 0, 0.07 * s), m=m, parent=p, bevel=0.006)
    box((0.018 * s, 0.015 * s, 0.05 * s), (-0.055 * s, 0, 0.02 * s), rot=(0, 0.7, 0), m=m, parent=p, bevel=0.006)
    return p


def braid(ch, color, n=6, z0=-0.05, step=0.075):
    """tranca descendo pelas costas (Drogo/Daenerys)"""
    m = mat(color, 0.65)
    for i in range(n):
        sphere(0.055 - i * 0.003, (0, 0.27 + i * 0.012, z0 - i * step), m=m, parent=ch.head, seg=12)


def scar(ch, color='#c87a6a', side=-1):
    sphere(1, (side * 0.13, -0.19, 0.0), (0.1, 0.06, 0.13), mat(color, 0.95), ch.head)


# ------------------------------------------------------------------ personagens
def _c(defaults, kw):
    d = dict(defaults); d.update(kw); return d


def ned(cape_=True, **kw):
    ch = Char(**_c(dict(name='ned', skin='#e8b48e', hair='#3a2a1e', hair_style='sam', eyes='#5a4a3a', jacket='#5a4636',
                        vest=None, shirt='#5a4636', pants='#3a3028', shoes='#2a1e16', collar=False, beard='#3a2a1e',
                        mustache='#3a2a1e', brows='#2e2016', body_w=1.05), kw))
    fur(ch, '#8a8078')
    if cape_:
        cape(ch, '#3a3a40')
    return ch


def catelyn(**kw):
    return Char(**_c(dict(name='cat', skin='#f0c4a4', hair='#9a3a1e', hair_style='long_red', eyes='#4a7aa6', dress='#3e4e6e',
                          jacket='#3e4e6e', female=True, brows='#7a2e18', body_w=0.92), kw))


def robb(cape_=True, crown_=False, **kw):
    ch = Char(**_c(dict(name='robb', skin='#f0bea0', hair='#6a3a20', hair_style='cas', eyes='#4a7aa6', jacket='#4a3a2e', vest=None,
                        shirt='#4a3a2e', pants='#3a3028', shoes='#2a1e16', collar=False, stubble='#6a3a20', brows='#5a3018'), kw))
    fur(ch, '#7a7068')
    if cape_:
        cape(ch, '#2e3a46')
    if crown_:
        crown(ch, '#a8783a', spike=0.13)
    return ch


def sansa(**kw):
    return Char(**_c(dict(name='sansa', skin='#f6cdb2', hair='#c0461e', hair_style='long_red', eyes='#4a7aa6', dress='#7aa6d8',
                          jacket='#7aa6d8', female=True, brows='#9a3418', body_w=0.86, height=0.9), kw))


def arya(**kw):
    return Char(**_c(dict(name='arya', skin='#f0c0a0', hair='#4a3220', hair_style='bun', eyes='#5a4a3a', jacket='#6a5a48', vest=None,
                          shirt='#6a5a48', pants='#4a3e32', shoes='#3a2a1e', collar=False, brows='#3a2618', body_w=0.8, height=0.78), kw))


def bran(**kw):
    return Char(**_c(dict(name='bran', skin='#f0c4a6', hair='#5a3a22', hair_style='short', eyes='#4a6a8a', jacket='#5a6a7a', vest=None,
                          shirt='#5a6a7a', pants='#3e3a34', shoes='#2a1e16', collar=False, brows='#4a2e18', body_w=0.76, height=0.68), kw))


def rickon(**kw):
    return Char(**_c(dict(name='rickon', skin='#f4caae', hair='#8a4a24', hair_style='cas', eyes='#4a6a8a', jacket='#7a6a52', vest=None,
                          shirt='#7a6a52', pants='#4a3e32', shoes='#2a1e16', collar=False, brows='#6a3a1a', body_w=0.7, height=0.52), kw))


def jon(cape_=True, **kw):
    ch = Char(**_c(dict(name='jon', skin='#ecb898', hair='#161214', hair_style='curly_long', eyes='#3a2a1e', jacket='#1c1c22', vest=None,
                        shirt='#1c1c22', pants='#1e1c1c', shoes='#141010', collar=False, mustache='#241c1a', brows='#141010'), kw))
    fur(ch, '#2a2624')
    if cape_:
        cape(ch, '#141418')
    return ch


def robert(**kw):
    ch = Char(**_c(dict(name='robert', skin='#eab08a', hair='#2a2018', hair_style='short', eyes='#4a6a8a', jacket='#3a2e1e', vest=None,
                        shirt='#3a2e1e', pants='#2a2218', shoes='#1e1610', collar=False, beard='#2a2018', mustache='#2a2018',
                        brows='#221a12', body_w=1.18, belly=True), kw))
    box((0.46, 0.01, 0.08), (0, -0.25, 0.3), m=mat(GOLD, 0.3, metal=0.8), parent=ch.chest)   # cinto dourado
    crown(ch, GOLD, spike=0.13)
    return ch


def cersei(crown_=False, **kw):
    ch = Char(**_c(dict(name='cersei', skin='#f6d0b4', hair='#e8c66a', hair_style='long', eyes='#3a8a5a', dress='#a8141e',
                        jacket='#a8141e', female=True, brows='#b8964a', body_w=0.9), kw))
    sphere(1, (0, -0.125, 0.5), (0.06, 0.01, 0.04), mat(GOLD, 0.3, metal=0.8), ch.chest)
    if crown_:
        crown(ch, GOLD, spike=0.1, n=9)
    return ch


def jaime(cape_=True, **kw):
    ch = Char(**_c(dict(name='jaime', skin='#f0c4a0', hair='#e0b860', hair_style='short', eyes='#3a8a5a', jacket='#d4a838',
                        vest=None, shirt='#d4a838', pants='#8a1e1e', shoes='#3a2a1e', collar=False, brows='#b8944a'), kw))
    if cape_:
        cape(ch, '#a8141e')
    return ch


def dany(**kw):
    ch = Char(**_c(dict(name='dany', skin='#f8dcc8', hair='#eeeef4', hair_style='long', eyes='#7a6ab8', dress='#c8d8ea',
                        jacket='#c8d8ea', female=True, brows='#d8d8e0', body_w=0.86, height=0.92), kw))
    braid(ch, '#eeeef4', 5, z0=-0.02)
    return ch


def drogo(**kw):
    ch = Char(**_c(dict(name='drogo', skin='#a8744e', hair='#141010', hair_style='buzz', eyes='#2a1a10', jacket='#a8744e', vest=None,
                        shirt='#a8744e', pants='#3a2a1e', shoes='#2a1e16', collar=False, beard='#141010', mustache='#141010',
                        brows='#141010', body_w=1.16, height=1.08), kw))
    braid(ch, '#141010', 9, z0=0.0, step=0.085)
    box((0.48, 0.26, 0.09), (0, 0, 0.05), m=mat('#5a3a22', 0.8), parent=ch.chest, bevel=0.03)   # cinto
    for sx in (-1, 1):
        sphere(1, (sx * 0.12, -0.12, 0.42), (0.08, 0.02, 0.06), mat('#c88a5e', 0.8), ch.chest)  # tinta/peito
    return ch


def joffrey(crown_=True, **kw):
    ch = Char(**_c(dict(name='joff', skin='#f6d0b4', hair='#e8c66a', hair_style='short', eyes='#3a8a5a', jacket='#b8141e', vest=None,
                        shirt='#b8141e', pants='#5a0e14', shoes='#2a1e16', collar=False, brows='#c8a050', body_w=0.86, height=0.88), kw))
    box((0.36, 0.01, 0.06), (0, -0.125, 0.4), m=mat(GOLD, 0.3, metal=0.8), parent=ch.chest)
    if crown_:
        crown(ch, GOLD, spike=0.1)
    return ch


def littlefinger(**kw):
    ch = Char(**_c(dict(name='lf', skin='#ecbc9a', hair='#3a2e28', hair_style='short', eyes='#5a6a4a', jacket='#2a3a2e', vest=None,
                        shirt='#2a3a2e', pants='#1e2420', shoes='#141210', collar=False, goatee='#4a3e38', brows='#2e241e'), kw))
    sphere(1, (0.1, -0.125, 0.48), (0.03, 0.01, 0.03), mat('#c0c0c8', 0.3, metal=0.8), ch.chest)   # broche tordo
    return ch


def executioner(**kw):
    return Char(**_c(dict(name='exe', skin='#d8a88a', hair='#6a5a4a', hair_style='bald', eyes='#3a2a1a', jacket='#4a4038', vest=None,
                          shirt='#4a4038', pants='#2a2420', shoes='#1a1410', collar=False, brows='#3a2a1a', body_w=1.12, height=1.05), kw))


def sam(**kw):
    ch = Char(**_c(dict(name='sam', skin='#f4c8a8', hair='#5a3e28', hair_style='short', eyes='#5a6a7a', jacket='#1e1e22', vest=None,
                        shirt='#1e1e22', pants='#1a1a1a', shoes='#141010', collar=False, brows='#4a2e18', body_w=1.25, belly=True), kw))
    fur(ch, '#2a2624', 0.9)
    return ch


def tyrion(cape_=False, **kw):
    ch = Char(**_c(dict(name='tyrion', skin='#f0c0a0', hair='#a8844a', hair_style='sam', eyes='#5a7a5a', jacket='#7a2a1e', vest=None,
                        shirt='#7a2a1e', pants='#3a2a22', shoes='#2a1e16', collar=False, stubble='#8a6a3a', brows='#8a6a3a',
                        body_w=0.95, height=0.6), kw))
    if cape_:
        cape(ch, '#5a1a14')
    return ch


def stannis(**kw):
    ch = Char(**_c(dict(name='stannis', skin='#e8b898', hair='#3a3634', hair_style='buzz', eyes='#4a6a8a', jacket='#5a5e66', vest=None,
                        shirt='#5a5e66', pants='#2a2a2e', shoes='#1a1a1a', collar=False, beard='#3a3634', brows='#2a2624'), kw))
    cape(ch, '#e0b43a')
    return ch


def walder(**kw):
    ch = Char(**_c(dict(name='walder', skin='#ecc0a6', hair='#d8d4cc', hair_style='gray', eyes='#4a4a4a', jacket='#5a5a50', vest=None,
                        shirt='#5a5a50', pants='#3a3a34', shoes='#1a1a1a', collar=False, stubble='#d8d4cc', brows='#d8d4cc',
                        body_w=0.85, height=0.88), kw))
    sphere(1, (0, 0.0, 0.2), (0.27, 0.27, 0.12), mat('#1e1e22', 0.7), ch.head)   # gorro
    return ch


def tywin(**kw):
    ch = Char(**_c(dict(name='tywin', skin='#ecbea0', hair='#d0c8b8', hair_style='buzz', eyes='#3a8a5a', jacket='#8a1e1e', vest=None,
                        shirt='#8a1e1e', pants='#3a1414', shoes='#1a1a1a', collar=False, brows='#c0b8a8', body_w=1.02), kw))
    for sx in (-1, 1):
        sphere(1, (sx * 0.23, -0.07, -0.08), (0.06, 0.08, 0.13), mat('#d0c8b8', 0.8), ch.head)   # costeletas
    return ch


def hound(**kw):
    ch = Char(**_c(dict(name='hound', skin='#e0aa88', hair='#2a2018', hair_style='sam', eyes='#3a2a1a', jacket='#3a3a3e', vest=None,
                        shirt='#3a3a3e', pants='#2a2a2a', shoes='#1a1a1a', collar=False, stubble='#2a2018', brows='#221a12',
                        body_w=1.2, height=1.12), kw))
    scar(ch, '#c86a5a', side=1)
    return ch


def ramsay(**kw):
    ch = Char(**_c(dict(name='ramsay', skin='#f0c4a8', hair='#2a1e18', hair_style='short', eyes='#6a8ab8', jacket='#2a1a1a', vest=None,
                        shirt='#2a1a1a', pants='#1e1414', shoes='#141010', collar=False, brows='#221812'), kw))
    cape(ch, '#6a1e24')
    return ch


def melisandre(**kw):
    ch = Char(**_c(dict(name='mel', skin='#f6d6c0', hair='#b8241e', hair_style='long_red', eyes='#c8241e', dress='#a8141e',
                        jacket='#a8141e', female=True, brows='#8a1a14', body_w=0.88), kw))
    sphere(0.045, (0, -0.13, 0.5), m=mat('#ff1a2a', 0.15, emit=3), parent=ch.chest)   # rubi
    return ch


def night_king(**kw):
    ch = Char(**_c(dict(name='nk', skin='#a8cce0', hair='#a8cce0', hair_style='bald', eyes='#38b8ff', eye_mode='blue', jacket='#2a3a4a',
                        vest=None, shirt='#2a3a4a', pants='#1e2a36', shoes='#1a2430', collar=False, brows='#7aa6c0', body_w=1.05,
                        height=1.06), kw))
    ice_crown(ch)
    return ch


def wight(seed=0, **kw):
    rnd = random.Random(seed)
    return Char(**_c(dict(name=f'wight{seed}', skin=rnd.choice(['#9aa6a8', '#8a9698', '#a0aaa6']), hair='#4a4a48',
                          hair_style=rnd.choice(['bald', 'short', 'cas']), eyes='#38b8ff', eye_mode='blue',
                          jacket=rnd.choice(['#4a4238', '#3a3a36', '#5a5046']), vest=None, shirt='#3a3a36', pants='#2a2824',
                          shoes='#1a1a1a', collar=False, brows='#5a5a58', height=rnd.uniform(0.95, 1.05)), kw))


def soldier(seed=0, color='#5a4a3a', helmet=STEEL, **kw):
    rnd = random.Random(seed)
    ch = Char(**_c(dict(name=f'sold{seed}', skin=rnd.choice(['#f0c4a6', '#e0a97f', '#c68a5e', '#8d5a3b']), hair='#3a2a1a',
                        hair_style='short', eyes='#3a2a1a', jacket=color, vest=None, shirt=color, pants='#2a2420', shoes='#1a1410',
                        collar=False, brows='#2a1a10', height=rnd.uniform(0.96, 1.04)), kw))
    if helmet:
        sphere(1, (0, 0.01, 0.07), (0.29, 0.29, 0.27), mat(helmet, 0.3, metal=0.8), ch.head)
    return ch


def unsullied(seed=0, **kw):
    ch = soldier(seed, '#4a3a2a', helmet=None, skin='#8d5a3b', **kw)
    cone(0.3, 0.02, 0.24, (0, 0.0, 0.3), m=mat('#6a5a3a', 0.4, metal=0.6), parent=ch.head, verts=24)   # capacete conico
    return ch


def crowd_person(seed, loc=(0, 0, 0), rot=0, **kw):
    rnd = random.Random(seed)
    tones = ['#6a5a48', '#7a6a52', '#5a4a3a', '#8a6a4a', '#4a5a5a', '#7a4a3a', '#a89a7a']
    female = rnd.random() < 0.4
    d = dict(name=f'cp{seed}', skin=rnd.choice(['#f0c4a6', '#e0a97f', '#c68a5e', '#f6d0b4']), hair=rnd.choice(['#2a1a10', '#5a3a1a', '#8a5a2a', '#1a1a1a', '#7a7a7a']),
             hair_style=rnd.choice(['long', 'bun']) if female else rnd.choice(['short', 'buzz', 'cas']), eyes='#3a2a1a',
             jacket=rnd.choice(tones), vest=None, shirt='#d8ccb0', pants='#3a3028', collar=False, female=female,
             dress=rnd.choice(tones) if female else None, body_w=0.92 if female else 1.0, height=rnd.uniform(0.92, 1.04), loc=loc, rot=rot)
    d.update(kw)
    return Char(**d)


# ------------------------------------------------------------------ animais / criaturas
def dragon(loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, body='#2e2628', belly='#9a2a1e', wing='#7a2622', eye='#ffcc2a', parent=None):
    """dragao: frente = -Y. retorna dict(root, wings, head, jaw, mouth)"""
    p = empty('dragon', loc, parent, rot)
    p.scale = (s, s, s)
    bm = mat(body, 0.55); blm = mat(belly, 0.7); wm = mat(wing, 0.8)
    sphere(1, (0, 0, 0), (0.36, 0.95, 0.36), bm, p)
    sphere(1, (0, -0.1, -0.1), (0.3, 0.8, 0.27), blm, p)
    # espinhos nas costas
    for i in range(7):
        cone(0.06, 0, 0.16, (0, 0.55 - i * 0.18, 0.4 - abs(i - 3) * 0.02), (-0.3, 0, 0), m=blm, parent=p, verts=6)
    # pescoco + cabeca
    neck = empty('dneck', (0, -0.8, 0.15), p, rot=(0.75, 0, 0))
    for i in range(6):
        sphere(0.17 - i * 0.012, (0, -i * 0.15, 0), m=bm, parent=neck, seg=16)
        cone(0.04, 0, 0.1, (0, -i * 0.15, 0.15 - i * 0.01), m=blm, parent=neck, verts=6)
    head = empty('dhead', (0, -0.9, 0.0), neck, rot=(-0.75, 0, 0))
    sphere(1, (0, -0.05, 0), (0.2, 0.28, 0.18), bm, head)
    sphere(1, (0, -0.32, -0.03), (0.13, 0.24, 0.1), bm, head)
    jaw = empty('djaw', (0, -0.1, -0.08), head)
    sphere(1, (0, -0.22, -0.03), (0.11, 0.24, 0.045), blm, jaw)
    for sx in (-1, 1):
        cone(0.05, 0, 0.3, (sx * 0.12, 0.17, 0.16), (-1.1, sx * 0.4, 0), m=mat('#d8c8a8', 0.5), parent=head, verts=8)
        sphere(0.045, (sx * 0.12, -0.17, 0.08), m=mat(eye, 0.2, emit=3), parent=head, seg=12)
        sphere(0.02, (sx * 0.135, -0.2, 0.085), m='#111111', parent=head, seg=8)
        cone(0.02, 0, 0.06, (sx * 0.05, -0.34, -0.09), (PI, 0, 0), m='#f2f2e8', parent=head, verts=6)   # dentes
    mouth = empty('dmouth', (0, -0.52, -0.06), head)
    # cauda
    for i in range(7):
        sphere(0.2 - i * 0.026, (0, 0.75 + i * 0.2, -0.05 - i * 0.03), m=bm, parent=p, seg=14)
    cone(0.12, 0, 0.22, (0, 2.2, -0.26), (-PI / 2 - 0.15, 0, 0), m=blm, parent=p, verts=4)
    # patas
    for sx in (-1, 1):
        for y in (-0.4, 0.4):
            sphere(1, (sx * 0.3, y, -0.38), (0.1, 0.12, 0.16), bm, p, seg=12)
    # asas
    wings = []
    for sx in (-1, 1):
        wp = empty('dwing', (sx * 0.3, -0.25, 0.3), p)
        v = [(0, 0, 0), (sx * 1.3, -0.2, 0.3), (sx * 2.5, 0.3, 0.12), (sx * 2.0, 0.95, -0.05), (sx * 1.2, 1.2, -0.05), (sx * 0.45, 1.0, -0.05), (0, 0.7, 0)]
        _mesh('membrane', v, [list(range(len(v)))], wm, wp)
        bpy.ops.object.select_all(action='DESELECT')
        # osso da borda
        for a, b in ((v[0], v[1]), (v[1], v[2])):
            A, B = Vector(a), Vector(b)
            d = B - A
            o = cyl(0.04, d.length, tuple((A + B) / 2), m=bm, parent=wp, verts=10)
            o.rotation_euler = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
        cone(0.04, 0, 0.12, (sx * 1.3, -0.25, 0.36), m='#d8c8a8', parent=wp, verts=6)
        for k in (3, 4, 5):
            A, B = Vector(v[1]), Vector(v[k]); dd = B - A
            o = cyl(0.018, dd.length, tuple((A + B) / 2), m=bm, parent=wp, verts=8)
            o.rotation_euler = Vector((0, 0, 1)).rotation_difference(dd.normalized()).to_euler()
        # face dupla visivel dos dois lados
        wings.append(wp)
    for o in p.children_recursive:
        if o.type == 'MESH' and o.name.startswith('membrane'):
            o.data.polygons[0].use_smooth = False
    return dict(root=p, wings=wings, head=head, jaw=jaw, mouth=mouth, neck=neck)


def dragon_flap(d, f0, f1, speed=10, amp=0.7, phase=0.0):
    for f in range(f0, f1 + 1, 2):
        a = math.sin((f + phase) / speed * PI) * amp - 0.3
        for k, w in enumerate(d['wings']):
            sx = -1 if k == 0 else 1
            w.rotation_euler = (0, -sx * a, 0)
            w.keyframe_insert('rotation_euler', frame=f)


def fire_breath(d, f0, f1, L=3.5, every=2, seed=0, s=1.0):
    """jato de fogo saindo da boca (particulas emissivas presas a cabeca), abre a mandibula"""
    rnd = random.Random(seed)
    key(d['jaw'], 'rotation_euler', f0 - 4, (0, 0, 0)); key(d['jaw'], 'rotation_euler', f0, (0.55, 0, 0))
    key(d['jaw'], 'rotation_euler', f1, (0.55, 0, 0)); key(d['jaw'], 'rotation_euler', f1 + 5, (0, 0, 0))
    cols = [mat('#ffd84a', 0.6, emit=9), mat('#ff8a1a', 0.6, emit=8), mat('#ff4a1a', 0.6, emit=6)]
    for k, fa in enumerate(x for x in range(f0, f1) for _ in range(2)):
        o = sphere(1, (0, 0, 0), (0.01, 0.01, 0.01), cols[k % 3], d['mouth'], seg=14)
        life_ = 12 + (k % 2) * 2
        ex, ez = rnd.uniform(-0.25, 0.25), rnd.uniform(-0.3, 0.15)
        key(o, 'location', fa, (0, 0, 0), 'LINEAR'); key(o, 'scale', fa, (0.05, 0.05, 0.05))
        key(o, 'location', fa + life_, (ex * L * 0.4, -L, ez * L * 0.4 - L * 0.25), 'LINEAR')
        sc = rnd.uniform(0.22, 0.4) * s
        key(o, 'scale', fa + life_ - 2, (sc, sc, sc)); key(o, 'scale', fa + life_, (0.0, 0.0, 0.0))
        key(o, 'scale', fa - 1, (0.0, 0.0, 0.0), 'CONSTANT')


def baby_dragon(parent=None, loc=(0, 0, 0), rot=(0, 0, 0), body='#2a2226', belly='#8a1e1e', s=0.22):
    d = dragon((0, 0, 0), (0, 0, 0), 1.0, body, belly, body, parent=None)
    p = empty('bdr', loc, parent, rot)
    d['root'].parent = p
    p.scale = (s, s, s)
    return p, d


def boar(loc, rot=0):
    p = empty('boar', loc, rot=(0, 0, rot))
    m = mat('#4a3a30', 0.85)
    sphere(1, (0, 0, 0.42), (0.32, 0.6, 0.32), m, p)
    sphere(1, (0, -0.58, 0.45), (0.22, 0.25, 0.22), m, p)
    cyl(0.1, 0.1, (0, -0.83, 0.42), (PI / 2, 0, 0), m='#c89a8a', parent=p)
    for sx in (-1, 1):
        cone(0.03, 0, 0.16, (sx * 0.11, -0.78, 0.4), (-0.6, sx * 0.2, 0), m='#f2eee0', parent=p, verts=8)
        sphere(0.03, (sx * 0.11, -0.72, 0.55), m='#ff3a1a', parent=p, seg=8)
        cone(0.06, 0, 0.12, (sx * 0.12, -0.5, 0.67), m=m, parent=p, verts=8)
        for y in (-0.35, 0.35):
            cyl(0.06, 0.26, (sx * 0.18, y, 0.13), m=m, parent=p, verts=10)
    for i in range(6):
        cone(0.04, 0, 0.14, (0, -0.35 + i * 0.13, 0.75), m='#2a201a', parent=p, verts=6)
    return p


def crows(f0, center, n=10, seed=0, spread=2.0, rise=3.0, f1=None):
    """revoada de corvos pretos saindo de center"""
    rnd = random.Random(seed)
    m = mat('#141418', 0.6)
    out = []
    for i in range(n):
        p = empty('crow', center)
        sphere(1, (0, 0, 0), (0.07, 0.14, 0.06), m, p, seg=12)
        sphere(0.05, (0, -0.13, 0.03), m=m, parent=p, seg=10)
        cone(0.02, 0, 0.06, (0, -0.19, 0.03), (PI / 2, 0, 0), m='#3a3a3a', parent=p, verts=6)
        ws = []
        for sx in (-1, 1):
            wp = empty('cw', (sx * 0.05, 0, 0.02), p)
            sphere(1, (sx * 0.12, 0.02, 0), (0.13, 0.06, 0.012), m, wp, seg=10)
            ws.append(wp)
        fa = f0 + rnd.randint(0, 6)
        d = Vector((rnd.uniform(-1, 1) * spread, rnd.uniform(-0.3, 1.0) * spread * 0.5, rise * rnd.uniform(0.7, 1.2)))
        p.rotation_euler = (0, 0, math.atan2(-d.x, d.y) + PI)
        hide_between(p, fa, None)
        key(p, 'location', fa, center, 'LINEAR')
        key(p, 'location', fa + 45, tuple(Vector(center) + d), 'LINEAR')
        p.scale = (1.3, 1.3, 1.3)
        for f in range(fa, (f1 or fa + 60), 2):
            a = math.sin(f / 2.2 * PI) * 0.9
            for k, w in enumerate(ws):
                w.rotation_euler = (0, (1 if k == 0 else -1) * a, 0); w.keyframe_insert('rotation_euler', frame=f)
        out.append(p)
    return out


# ------------------------------------------------------------------ arquitetura
STONE = '#8a8a86'
STONE2 = '#7a7a76'


def stone_wall(x0, x1, y, h=3.5, color=STONE, thick=0.6, cren=True, rot=0.0, z=0.0, parent=None):
    p = empty('swall', ((x0 + x1) / 2, y, z), parent, rot=(0, 0, rot))
    w = x1 - x0
    m = mat(color, 0.9); m2 = mat(STONE2, 0.9)
    box((w, thick, h), (0, 0, h / 2), m=m, parent=p)
    # fiadas de pedra (linhas mais escuras)
    for k in range(1, int(h / 0.5)):
        box((w, 0.02, 0.035), (0, -thick / 2 - 0.005, k * 0.5), m=m2, parent=p)
    if cren:
        n = max(2, int(w / 0.6))
        for i in range(n):
            if i % 2 == 0:
                box((w / n, thick, 0.35), (-w / 2 + w / n * (i + 0.5), 0, h + 0.175), m=m, parent=p)
    return p


def tower(loc, r=1.0, h=6.0, color=STONE, roof='#3a4a5a', window_z=None, cren=False):
    p = empty('tower', loc)
    m = mat(color, 0.9)
    cyl(r, h, (0, 0, h / 2), m=m, parent=p, verts=32)
    for k in range(1, int(h / 0.6)):
        cyl(r + 0.005, 0.03, (0, 0, k * 0.6), m=mat(STONE2, 0.9), parent=p, verts=32)
    if roof:
        cone(r * 1.2, 0, r * 1.6, (0, 0, h + r * 0.8), m=mat(roof, 0.7), parent=p, verts=32)
    if cren:
        for i in range(12):
            if i % 2 == 0:
                a = 2 * PI * i / 12
                box((0.35, 0.3, 0.35), (math.sin(a) * r * 0.95, -math.cos(a) * r * 0.95, h + 0.17), rot=(0, 0, a), m=m, parent=p)
    if window_z:
        box((0.5, 0.2, 0.8), (0, -r + 0.05, window_z), m=mat('#1a1410', 0.9), parent=p)
    return p


def banner(loc, color='#f2f0ea', sigil='wolf', w=0.9, h=1.7, rot=0.0, sig_col=None, parent=None):
    """estandarte pendurado (frente -Y) com brasao simples"""
    p = empty('banner', loc, parent, rot=(0, 0, rot))
    box((w + 0.1, 0.05, 0.05), (0, 0, 0), m=mat('#5a4030', 0.7), parent=p)
    box((w, 0.03, h), (0, 0, -h / 2), m=mat(color, 0.85), parent=p)
    cone(w * 0.5, 0, 0.3, (0, 0, -h - 0.15), (PI, 0, PI / 4), m=mat(color, 0.85), parent=p, verts=4).scale = (1, 0.06, 1)
    sg = empty('sigil', (0, -0.03, -h * 0.5), p)
    sc = w / 0.9
    sg.scale = (sc, sc, sc)
    if sigil == 'wolf':
        m = mat(sig_col or '#6a6a70', 0.8)
        sphere(1, (0, 0, 0), (0.2, 0.03, 0.2), m, sg)
        sphere(1, (0, -0.005, -0.17), (0.09, 0.03, 0.12), m, sg)
        for sx in (-1, 1):
            cone(0.08, 0, 0.2, (sx * 0.13, 0, 0.22), (PI / 2, 0, sx * -0.35), m=m, parent=sg, verts=3)
    elif sigil == 'lion':
        m = mat(sig_col or GOLD, 0.4, metal=0.5)
        cyl(0.26, 0.03, (0, 0, 0), (PI / 2, 0, 0), m=m, parent=sg, verts=12)
        sphere(1, (0, -0.02, -0.02), (0.14, 0.03, 0.16), mat('#c8902a', 0.5), sg)
    elif sigil == 'stag':
        m = mat(sig_col or '#141414', 0.7)
        sphere(1, (0, 0, -0.08), (0.12, 0.03, 0.16), m, sg)
        for sx in (-1, 1):
            box((0.04, 0.03, 0.3), (sx * 0.12, 0, 0.18), rot=(0, sx * 0.5, 0), m=m, parent=sg)
            box((0.035, 0.03, 0.14), (sx * 0.22, 0, 0.22), rot=(0, sx * -0.4, 0), m=m, parent=sg)
            box((0.035, 0.03, 0.14), (sx * 0.06, 0, 0.3), rot=(0, sx * -0.2, 0), m=m, parent=sg)
    elif sigil == 'dragon':
        m = mat(sig_col or '#c0141e', 0.6)
        sphere(1, (0, 0, -0.05), (0.12, 0.03, 0.2), m, sg)
        sphere(1, (0, 0, 0.2), (0.08, 0.03, 0.08), m, sg)
        for sx in (-1, 1):
            cone(0.2, 0, 0.42, (sx * 0.2, 0, 0.08), (PI / 2, 0, sx * 1.2), m=m, parent=sg, verts=3)
    elif sigil == 'flayed':
        m = mat(sig_col or '#e88a9a', 0.7)
        sphere(0.08, (0, 0, 0.22), m=m, parent=sg)
        box((0.1, 0.03, 0.3), (0, 0, 0.0), m=m, parent=sg)
        for sx in (-1, 1):
            box((0.05, 0.03, 0.3), (sx * 0.14, 0, 0.12), rot=(0, sx * 1.0, 0), m=m, parent=sg)
            box((0.05, 0.03, 0.3), (sx * 0.09, 0, -0.26), rot=(0, sx * -0.4, 0), m=m, parent=sg)
    elif sigil == 'trout':
        m = mat(sig_col or '#4a6a9a', 0.6)
        sphere(1, (0, 0, 0), (0.24, 0.03, 0.1), m, sg)
        cone(0.1, 0, 0.14, (0.28, 0, 0), (PI / 2, 0, PI / 2), m=m, parent=sg, verts=3)
    elif sigil == 'towers':
        m = mat(sig_col or '#2a3a5a', 0.7)
        for sx in (-1, 1):
            box((0.12, 0.03, 0.4), (sx * 0.12, 0, 0), m=m, parent=sg)
        box((0.36, 0.03, 0.06), (0, 0, -0.05), m=m, parent=sg)
    return p


def house(loc, w=1.4, d=1.2, h=1.3, wall='#e8d8b8', roof='#b8462a', rot=0.0, parent=None):
    p = empty('house', loc, parent, rot=(0, 0, rot))
    box((w, d, h), (0, 0, h / 2), m=mat(wall, 0.85), parent=p)
    r = cone(max(w, d) * 0.78, 0, h * 0.6, (0, 0, h + h * 0.3), (0, 0, PI / 4), m=mat(roof, 0.7), parent=p, verts=4)
    r.scale = (w / max(w, d), d / max(w, d), 1)
    box((0.22, 0.02, 0.28), (w * 0.2, -d / 2 - 0.005, h * 0.6), m=mat('#4a3a2a', 0.8), parent=p)
    return p


def kings_landing(center=(0, 8, 0), seed=3, n=40, R=7.0, burning=None, f0=1, f1=200, keep=True, sea_y=None):
    """cidade de casas de telhado vermelho subindo um morro + Fortaleza Vermelha"""
    rnd = random.Random(seed)
    cx, cy, cz = center
    out = []
    for i in range(n):
        x = cx + rnd.uniform(-R, R); y = cy + rnd.uniform(-R * 0.4, R * 0.5)
        hill = max(0, 1.6 - (abs(x - cx) / R) * 1.6) + (y - cy) * 0.12
        o = house((x, y, cz + hill * 0.6), rnd.uniform(0.9, 1.6), rnd.uniform(0.8, 1.3), rnd.uniform(0.9, 1.6),
                  rnd.choice(['#e8d8b8', '#e0ccaa', '#f0e2c4', '#d8c4a0']), rnd.choice(['#b8462a', '#c0562e', '#a83e26']), rot=rnd.uniform(-0.2, 0.2))
        out.append(o)
    # morro
    sphere(1, (cx, cy + 1.5, cz - 2.0), (R * 1.2, R * 0.8, 3.0), mat('#9a8a6a', 0.9), seg=48)
    if keep:
        kp = empty('keep', (cx + 0.5, cy + R * 0.55, cz + 1.0))
        rm = mat('#b8564a', 0.85)
        box((4.0, 2.5, 2.8), (0, 0, 1.4), m=rm, parent=kp)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl(0.55, 4.2, (sx * 2.0, sy * 1.25, 2.1), m=rm, parent=kp, verts=24)
                cone(0.65, 0, 0.9, (sx * 2.0, sy * 1.25, 4.65), m=mat('#7a2a22', 0.8), parent=kp, verts=24)
        cyl(0.8, 5.5, (0, 0, 2.75), m=rm, parent=kp, verts=24)
        cone(0.95, 0, 1.2, (0, 0, 6.1), m=mat('#7a2a22', 0.8), parent=kp, verts=24)
        out.append(kp)
    if burning:
        for i, o in enumerate(out[:burning]):
            fo, fl = flames(tuple(Vector(o.location) + Vector((0, 0, 1.0))), 5, 0.5, 0.9, seed=i)
            fs = f0 + rnd.randint(0, max(1, (f1 - f0) // 2))
            fo.scale = (0, 0, 0)
            key(fo, 'scale', fs - 1, (0, 0, 0), 'CONSTANT'); key(fo, 'scale', fs + 6, (1.4, 1.4, 1.4))
            flicker(fl, f0, f1, seed=i)
    return out


def sept(loc, s=1.0, color='#e8e0d0', dome='#d8c8a0'):
    p = empty('sept', loc); p.scale = (s, s, s)
    m = mat(color, 0.8)
    box((6, 5, 3), (0, 0, 1.5), m=m, parent=p)
    cyl(2.2, 1.2, (0, 0, 3.6), m=m, parent=p, verts=7)
    sphere(1, (0, 0, 4.2), (2.2, 2.2, 1.9), mat(dome, 0.6), p, seg=48)
    cone(0.25, 0, 1.2, (0, 0, 6.6), m=mat(GOLD, 0.3, metal=0.8), parent=p, verts=12)
    for i in range(7):
        a = 2 * PI * i / 7
        cyl(0.35, 3.8, (math.sin(a) * 3.2, -math.cos(a) * 2.7, 1.9), m=m, parent=p, verts=16)
        cone(0.45, 0, 0.9, (math.sin(a) * 3.2, -math.cos(a) * 2.7, 4.25), m=mat(dome, 0.6), parent=p, verts=16)
    # escadaria
    for k in range(5):
        box((6.5 - k * 0.3, 0.35, 0.18), (0, -2.65 - (4 - k) * 0.35, 0.09 + k * 0.18), m=mat('#d8d0c0', 0.8), parent=p)
    return p


def iron_throne(loc, rot=0.0, s=1.0, seed=5):
    """Trono de Ferro: assento z=0.55*s; sentado olha para -Y local"""
    rnd = random.Random(seed)
    p = empty('throne', loc, rot=(0, 0, rot)); p.scale = (s, s, s)
    m = mat('#4a4a52', 0.35, metal=0.85)
    m2 = mat('#6a6a74', 0.3, metal=0.9)
    # degraus
    for k in range(3):
        box((2.4 - k * 0.4, 1.8 - k * 0.3, 0.12), (0, 0.1 + k * 0.08, 0.06 + k * 0.12), m=mat('#5a5048', 0.8), parent=p)
    seat_z = 0.55
    box((0.8, 0.65, 0.2), (0, 0.15, seat_z - 0.1 - 0.2), m=m, parent=p, bevel=0.03)
    box((0.8, 0.65, 0.12), (0, 0.15, seat_z - 0.06), m=mat('#3a3a40', 0.6), parent=p, bevel=0.03)
    box((0.8, 0.12, 1.1), (0, 0.48, seat_z + 0.5), m=m, parent=p, bevel=0.02)
    # bracos com espadas
    for sx in (-1, 1):
        box((0.12, 0.6, 0.3), (sx * 0.46, 0.15, seat_z + 0.1), m=m, parent=p, bevel=0.02)
        for k in range(4):
            box((0.04, 0.5 + k * 0.08, 0.012), (sx * (0.48 + k * 0.025), 0.05, seat_z + 0.26 + k * 0.02), rot=(0, 0, rnd.uniform(-0.15, 0.15)), m=m2, parent=p)
    # leque de espadas atras
    for i in range(46):
        a = rnd.uniform(-0.85, 0.85)
        L = rnd.uniform(1.0, 2.2) * (1.15 - abs(a) * 0.5)
        x = math.sin(a) * 0.3; z = seat_z + 0.5
        o = box((0.05, 0.012, L), (x + math.sin(a) * L / 2, 0.58 + rnd.uniform(0, 0.25), z + math.cos(a) * L / 2), rot=(0, a, 0), m=m2, parent=p)
        cone(0.035, 0, 0.08, (x + math.sin(a) * (L + 0.04), 0.58, z + math.cos(a) * (L + 0.04)), (0, a, 0), m=m2, parent=p, verts=4)
    return p


def ice_wall(y=12, h=14, w=80, x=0):
    m = mat('#d4ecf6', 0.15, emit=0.1)
    box((w, 3, h), (x, y, h / 2), m=m)
    box((w, 0.2, 0.25), (x, y - 1.6, h - 0.15), m=mat('#f4fbff', 0.3, emit=0.2))
    m2 = mat('#c0dcea', 0.2, emit=0.08)
    rnd = random.Random(2)
    for i in range(40):
        box((rnd.uniform(0.6, 2.5), 0.2, rnd.uniform(1.5, 6)), (x + rnd.uniform(-w / 2, w / 2), y - 1.55, rnd.uniform(1, h - 2)), m=m2)


def pyre(loc, seed=0):
    rnd = random.Random(seed)
    p = empty('pyre', loc)
    m = mat('#6a4a2e', 0.9)
    for k in range(4):
        for i in range(5):
            if k % 2 == 0:
                cyl(0.07, 1.6, (-0.6 + i * 0.3, 0, 0.07 + k * 0.13), (PI / 2, 0, 0), m=m, parent=p, verts=10)
            else:
                cyl(0.07, 1.6, (0, -0.6 + i * 0.3, 0.07 + k * 0.13), (0, PI / 2, 0), m=m, parent=p, verts=10)
    return p


def egg(loc, color, parent=None, s=1.0):
    o = sphere(1, loc, (0.09 * s, 0.09 * s, 0.13 * s), mat(color, 0.35, metal=0.3), parent, seg=24)
    return o


def ship(loc, rot=0.0, sail='#e0b43a', hull='#5a3a24', s=1.0, sigil=None):
    p = empty('ship', loc, rot=(0, 0, rot)); p.scale = (s, s, s)
    hm = mat(hull, 0.8)
    box((1.4, 4.2, 0.7), (0, 0, 0.25), m=hm, parent=p, bevel=0.25)
    cone(0.7, 0, 1.0, (0, -2.4, 0.35), (PI / 2, 0, 0), m=hm, parent=p, verts=4).scale = (1, 1, 0.5)
    cyl(0.07, 3.6, (0, 0.1, 2.2), m=mat('#4a3020', 0.8), parent=p)
    box((2.2, 0.05, 1.8), (0, 0.1, 2.4), m=mat(sail, 0.85), parent=p)
    if sigil:
        banner((0, 0.05, 3.25), sail, sigil, 1.0, 1.6, parent=p)
    return p


def long_table(loc, L=4.0, w=0.9, h=0.78, color='#6a4a2e', rot=0.0):
    p = empty('ltable', loc, rot=(0, 0, rot))
    m = mat(color, 0.7)
    box((L, w, 0.08), (0, 0, h - 0.04), m=m, parent=p, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            box((0.1, 0.1, h - 0.08), (sx * (L / 2 - 0.2), sy * (w / 2 - 0.1), (h - 0.08) / 2), m=m, parent=p)
    box((L * 0.98, w * 0.6, 0.01), (0, 0, h + 0.005), m=mat('#c8b890', 0.9), parent=p)
    return p


def bench(loc, L=3.0, rot=0.0, h=0.45, color='#5a3e26'):
    p = empty('bench', loc, rot=(0, 0, rot))
    m = mat(color, 0.8)
    box((L, 0.4, 0.07), (0, 0, h - 0.035), m=m, parent=p)
    for sx in (-1, 1):
        box((0.08, 0.36, h - 0.07), (sx * (L / 2 - 0.15), 0, (h - 0.07) / 2), m=m, parent=p)
    return p


def torch(loc, f0=1, f1=200, seed=0, wall=True):
    p = empty('torch', loc)
    cyl(0.035, 0.45, (0, 0, 0), m=mat('#4a3020', 0.8), parent=p, verts=10)
    fo, fl = flames((0, 0, 0.22), 3, 0.06, 0.28, seed=seed, parent=p)
    flicker(fl, f0, f1, seed=seed)
    l = point((loc[0], loc[1] - 0.2, loc[2] + 0.4), 40, '#ffa040', 0.2)
    return p


def weirwood(loc, s=1.0, seed=1):
    """arvore-coracao: tronco branco, folhas vermelhas, rosto"""
    rnd = random.Random(seed)
    p = empty('weirwood', loc); p.scale = (s, s, s)
    wm = mat('#efe8dc', 0.8)
    cyl(0.4, 3.0, (0, 0, 1.5), m=wm, parent=p, verts=16)
    for i in range(5):
        a = rnd.uniform(0, 2 * PI)
        cyl(0.15, 1.5, (math.sin(a) * 0.5, math.cos(a) * 0.5, 2.9), (math.cos(a) * 0.7, -math.sin(a) * 0.7, 0), m=wm, parent=p, verts=10)
    lm = mat('#b8141e', 0.8); lm2 = mat('#d8341e', 0.8)
    for i in range(16):
        sphere(rnd.uniform(0.5, 0.8), (rnd.uniform(-1.4, 1.4), rnd.uniform(-1.0, 1.0), rnd.uniform(3.0, 4.2)), m=lm if i % 2 else lm2, parent=p, seg=16)
    # rosto entalhado
    for sx in (-1, 1):
        sphere(1, (sx * 0.12, -0.38, 1.9), (0.07, 0.03, 0.04), mat('#8a0a14', 0.6), p)
    sphere(1, (0, -0.38, 1.65), (0.1, 0.03, 0.05), mat('#8a0a14', 0.6), p)
    return p


def crossbow(parent, loc=(0, 0, -0.47), rot=(0, 0, 0)):
    p = empty('xbow', loc, parent, rot)
    m = mat('#5a3a22', 0.7)
    box((0.04, 0.4, 0.05), (0, -0.12, 0), m=m, parent=p)
    box((0.42, 0.03, 0.03), (0, -0.3, 0), m=mat('#3a3a3a', 0.5, metal=0.6), parent=p)
    return p


def snow_ground(ox=0, size=60, color='#eef4f8'):
    box((size, size, 0.02), (ox, 0, -0.009), m=mat(color, 0.6))


def grass_ground(ox=0, size=60, color='#7a9a4a'):
    box((size, size, 0.02), (ox, 0, -0.009), m=mat(color, 0.9))


def mud_ground(ox=0, size=60, color='#6a5a44'):
    box((size, size, 0.02), (ox, 0, -0.009), m=mat(color, 0.95))


def stone_floor(ox=0, c1='#8a8478', c2='#7a7468', size=30, scale=1.0, y=0):
    checker_floor(c1, c2, size=size, scale=scale, loc=(ox, y, 0))


def tent(loc, r=2.0, h=2.4, color='#c89a5a', rot=0.0):
    p = empty('tent', loc, rot=(0, 0, rot))
    cone(r, 0.1, h, (0, 0, h / 2), m=mat(color, 0.85), parent=p, verts=12)
    box((0.7, 0.05, 1.2), (0, -r * 0.62, 0.6), rot=(0.35, 0, 0), m=mat('#3a2418', 0.9), parent=p)
    return p
