# Biblioteca de modelagem procedural estilo "boneco de brinquedo" para Blender 4.2
import bpy, bmesh, math, random
from mathutils import Vector, Euler

FPS = 30
_mats = {}

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    sc = bpy.context.scene
    sc.render.fps = FPS
    return sc

def hexc(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    # sRGB -> linear
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)

def mat(color, rough=0.5, emit=0.0, metal=0.0, name=None, spec=0.4):
    key = (color, rough, emit, metal, spec)
    if key in _mats:
        return _mats[key]
    c = hexc(color) if isinstance(color, str) else color
    m = bpy.data.materials.new(name or f"m{len(_mats)}")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*c, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Specular IOR Level"].default_value = spec
    if emit > 0:
        b.inputs["Emission Color"].default_value = (*c, 1)
        b.inputs["Emission Strength"].default_value = emit
    m.diffuse_color = (*c, 1)
    m.roughness = rough
    _mats[key] = m
    return m

def _finish(o, m, parent=None, smooth=True):
    if m is not None:
        o.data.materials.clear()
        o.data.materials.append(m if not isinstance(m, str) else mat(m))
    if smooth and o.type == 'MESH':
        for p in o.data.polygons:
            p.use_smooth = True
    if parent is not None:
        o.parent = parent
    return o

def sphere(r=1, loc=(0, 0, 0), scale=(1, 1, 1), m=None, parent=None, seg=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=max(8, seg // 2), location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    return _finish(o, m, parent)

def cyl(r=1, depth=1, loc=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), m=None, parent=None, verts=32, smooth=True, bevel=0):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    if bevel > 0:
        bm = o.modifiers.new("b", 'BEVEL'); bm.width = bevel; bm.segments = 3; bm.limit_method = 'ANGLE'
    o = _finish(o, m, parent, smooth)
    if smooth:
        # evita sombreamento estranho nas tampas
        o.data.shade_smooth()
        try:
            bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
        except Exception:
            pass
    return o

def cone(r1=1, r2=0, depth=1, loc=(0, 0, 0), rot=(0, 0, 0), m=None, parent=None, verts=32):
    bpy.ops.mesh.primitive_cone_add(radius1=r1, radius2=r2, depth=depth, vertices=verts, location=loc, rotation=rot)
    o = bpy.context.object
    o = _finish(o, m, parent)
    try:
        bpy.ops.object.shade_smooth_by_angle(angle=math.radians(40))
    except Exception:
        pass
    return o

def box(size=(1, 1, 1), loc=(0, 0, 0), rot=(0, 0, 0), m=None, parent=None, bevel=0.0, seg=4):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        b = o.modifiers.new("bev", 'BEVEL'); b.width = bevel; b.segments = seg; b.limit_method = 'NONE'
        b.harden_normals = False
    _finish(o, m, parent, smooth=bevel > 0)
    return o

def torus(R=1, r=0.1, loc=(0, 0, 0), rot=(0, 0, 0), m=None, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot, major_segments=48, minor_segments=12)
    o = bpy.context.object; o.scale = scale
    return _finish(o, m, parent)

def empty(name="e", loc=(0, 0, 0), parent=None, rot=(0, 0, 0)):
    o = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    if parent is not None:
        o.parent = parent
    return o

def text3d(s, loc=(0, 0, 0), rot=(math.pi / 2, 0, 0), size=0.3, m='#ffffff', parent=None, extrude=0.02, align='CENTER', font=None, bevel=0.005):
    bpy.ops.object.text_add(location=loc, rotation=rot)
    o = bpy.context.object
    o.data.body = s
    o.data.size = size
    o.data.extrude = extrude
    o.data.bevel_depth = bevel
    o.data.align_x = align
    o.data.align_y = 'CENTER'
    if font:
        o.data.font = bpy.data.fonts.load(font, check_existing=True)
    o.data.materials.append(mat(m) if isinstance(m, str) else m)
    if parent is not None:
        o.parent = parent
    return o

def curve_path(points, bevel=0.02, m='#000000', parent=None, closed=False, res=12):
    cu = bpy.data.curves.new("c", 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(points) - 1)
    for p, c in zip(sp.bezier_points, points):
        p.co = c; p.handle_left_type = p.handle_right_type = 'AUTO'
    sp.use_cyclic_u = closed
    cu.bevel_depth = bevel; cu.bevel_resolution = 4; cu.resolution_u = res
    cu.use_fill_caps = True
    o = bpy.data.objects.new("curve", cu)
    bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(mat(m) if isinstance(m, str) else m)
    if parent is not None:
        o.parent = parent
    return o

# ------------------------------------------------------------------ keyframes
def key(o, path, frame, value=None, interp='BEZIER'):
    if value is not None:
        setattr(o, path, value)
    o.keyframe_insert(data_path=path, frame=frame)
    ad = o.animation_data
    if ad and ad.action:
        for fc in ad.action.fcurves:
            if fc.data_path == path:
                for kp in fc.keyframe_points:
                    if abs(kp.co[0] - frame) < 0.01:
                        kp.interpolation = interp
                        kp.easing = 'EASE_IN_OUT'

def keys(o, path, pairs, interp='BEZIER'):
    for f, v in pairs:
        key(o, path, f, v, interp)

def set_linear(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'LINEAR'

def hide_between(o, f_show=None, f_hide=None):
    """visivel de f_show ate f_hide (escala 0 fora)"""
    s = tuple(o.scale)
    if f_show is not None:
        key(o, 'scale', f_show - 1, (0, 0, 0), 'CONSTANT')
        key(o, 'scale', f_show, s, 'CONSTANT')
    if f_hide is not None:
        key(o, 'scale', f_hide - 1, s, 'CONSTANT')
        key(o, 'scale', f_hide, (0, 0, 0), 'CONSTANT')

def pop_in(o, f, dur=8, overshoot=1.15):
    s = Vector(o.scale)
    key(o, 'scale', f - 1, (0, 0, 0), 'CONSTANT')
    key(o, 'scale', f, s * 0.01)
    key(o, 'scale', f + int(dur * 0.6), s * overshoot)
    key(o, 'scale', f + dur, s)

# ------------------------------------------------------------------ personagem
SKIN = '#f7c29c'

def _hair_cap(R, parent, m, off=(0, 0.04, 0.07), sc=(1.06, 1.06, 1.0), name='hair'):
    """casco de cabelo = esfera deslocada; a intersecao com a cabeca da uma linha de cabelo suave"""
    o = sphere(R, off, sc, m, parent, seg=48)
    o.name = name
    return o

class Char:
    """Boneco com cabeca grande. Pivos: root (pes), hips, chest, head, armL/R, legL/R."""
    def __init__(self, name="c", skin=SKIN, hair='#d9a441', hair_style='wavy', eyes='#4a8fd6',
                 jacket='#4b4f5c', vest='#5b5f6b', shirt='#f4f4f0', pants=None, shoes='#3a2a20',
                 tie=None, female=False, beard=None, mustache=None, hat=None, height=1.0,
                 loc=(0, 0, 0), rot=0.0, brows=None, glasses=False, dress=None, badge=False,
                 lapels=True, body_w=1.0, skirt=None, sleeves=None, collar=True,
                 coat=None, eye_mode=None, fangs=False, pointy_ears=False, stubble=None, emit_body=0.0, hands=None):
        self.name = name
        pants = pants or jacket
        sleeves = sleeves or jacket
        R = 0.27
        self.R = R
        self.root = empty(name + "_root", loc, rot=(0, 0, rot))
        leg_len = 0.52 * height
        self.leg_len = leg_len
        hips = empty(name + "_hips", (0, 0, leg_len), self.root)
        self.hips = hips
        tw = 0.21 * body_w
        # pernas
        self.legs = []
        for sx in (-1, 1):
            lp = empty(name + "_leg", (sx * 0.085 * body_w, 0, 0), hips)
            if skirt is None and dress is None:
                sphere(1, (0, 0, -leg_len * 0.5), (0.075, 0.08, leg_len * 0.55), pants, lp)
            else:
                sphere(1, (0, 0, -leg_len * 0.55), (0.05, 0.05, leg_len * 0.5), skin, lp)
            sphere(1, (0, -0.04, -leg_len + 0.03), (0.075, 0.12, 0.05), shoes, lp)
            self.legs.append(lp)
        # tronco
        chest = empty(name + "_chest", (0, 0, 0), hips)
        self.chest = chest
        th = 0.56 * height
        body_m = dress or jacket
        torso = box((tw * 2, 0.24, th), (0, 0, th / 2 + 0.01), m=body_m, parent=chest, bevel=0.1, seg=6)
        self.torso = torso
        if skirt:
            cone(0.24, 0.17, 0.3, (0, 0, -0.08), m=skirt, parent=chest)
        if dress:
            cone(0.3, 0.17, 0.42, (0, 0, -0.12), m=dress, parent=chest)
        front = -0.12
        if dress is None:
            # camisa em V + colete
            if collar:
                bpy.ops.mesh.primitive_cone_add(vertices=3, radius1=0.085, depth=0.01, location=(0, front - 0.002, th * 0.82), rotation=(math.pi / 2, math.pi, 0))
                v = bpy.context.object; v.scale = (1, 1.9, 1); _finish(v, mat(shirt), chest, smooth=False)
                if tie:
                    box((0.035, 0.012, th * 0.42), (0, front - 0.012, th * 0.68), m=tie, parent=chest, bevel=0.01)
                if vest:
                    for sx in (-1, 1):
                        box((0.05, 0.012, th * 0.62), (sx * 0.055, front - 0.004, th * 0.5), rot=(0, sx * 0.25, 0), m=vest, parent=chest, bevel=0.008)
        if badge:
            sphere(1, (-0.11, front - 0.01, th * 0.7), (0.028, 0.01, 0.032), mat('#e8c34a', 0.25, metal=0.8), chest)
        if coat:
            cone(0.25 * body_w, 0.2 * body_w, 0.42, (0, 0.0, -0.14), m=coat, parent=chest, verts=32)
        # bracos
        self.arms = []
        for sx in (-1, 1):
            ap = empty(name + "_arm", (sx * (tw + 0.03), 0, th * 0.86), chest)
            sphere(1, (0, 0, -0.2), (0.06, 0.065, 0.24), sleeves, ap)
            sphere(0.055, (0, 0, -0.44), m=hands or skin, parent=ap)
            ap.rotation_euler = (0, sx * 0.12, 0)
            self.arms.append(ap)
        # cabeca
        neck = empty(name + "_neck", (0, 0, th + 0.02), chest)
        sphere(1, (0, 0, 0.02), (0.07, 0.07, 0.06), skin, neck)
        head = empty(name + "_head", (0, 0, R * 0.92), neck)
        self.neck, self.head = neck, head
        sphere(R, (0, 0, 0), (1, 0.94, 1.02), skin, head)
        # orelhas
        for sx in (-1, 1):
            sphere(1, (sx * R * 0.97, 0.01, -0.01), (0.04, 0.03, 0.06), skin, head)
        # olhos
        self.eyes = []
        for sx in (-1, 1):
            ex, ez = sx * 0.088, 0.035
            ey = -math.sqrt(max(0.0, (R * 0.94) ** 2 - ex ** 2 - ez ** 2)) + 0.02
            ep = empty(name + "_eye", (ex, ey, ez), head)
            if eye_mode == 'black':      # demonio: olho todo preto
                sphere(0.052, (0, 0, 0), (1, 0.6, 1.08), mat('#080808', 0.15), ep)
            elif eye_mode == 'yellow':   # Azazel
                sphere(0.052, (0, 0, 0), (1, 0.6, 1.08), mat('#f2d21a', 0.2, emit=1.2), ep)
                sphere(0.012, (0, -0.042, -0.002), (0.6, 0.4, 1.6), '#111111', ep)
            elif eye_mode == 'red':      # brilho vermelho
                sphere(0.052, (0, 0, 0), (1, 0.6, 1.08), '#ffffff', ep)
                sphere(0.032, (0, -0.03, -0.002), (1, 0.4, 1), mat('#ff2020', 0.2, emit=4), ep)
                sphere(0.016, (0, -0.042, -0.002), (1, 0.4, 1), '#300000', ep)
            elif eye_mode == 'white':    # anjo/luz
                sphere(0.052, (0, 0, 0), (1, 0.6, 1.08), mat('#e8f6ff', 0.2, emit=5), ep)
            else:
                sphere(0.052, (0, 0, 0), (1, 0.6, 1.08), '#ffffff', ep)
                sphere(0.032, (0, -0.03, -0.002), (1, 0.4, 1), eyes, ep)
                sphere(0.018, (0, -0.042, -0.002), (1, 0.4, 1), '#111111', ep)
            sphere(0.008, (0.01, -0.05, 0.012), (1, 0.5, 1), mat('#ffffff', emit=1.5), ep)
            self.eyes.append(ep)
        # sobrancelhas
        bc = brows or hair
        if hair_style == 'bald':
            bc = brows or '#6a5a4a'
        self.brows = []
        for sx in (-1, 1):
            bp = empty(name + "_brow", (sx * 0.09, -R * 0.84, 0.115), head)
            box((0.085, 0.02, 0.022), (0, 0, 0), rot=(0, sx * -0.12, 0), m=bc, parent=bp, bevel=0.009)
            bp.rotation_euler = (0.25, 0, 0)
            self.brows.append(bp)
        # nariz
        sphere(1, (0, -R * 0.95, -0.03), (0.026, 0.024, 0.03), skin, head)
        # boca
        mp = empty(name + "_mouth", (0, -R * 0.86, -0.11), head)
        mp.rotation_euler = (0.3, 0, 0)
        sphere(1, (0, 0, 0), (0.045, 0.02, 0.024), '#4a1414', mp)
        sphere(1, (0, -0.006, -0.012), (0.026, 0.012, 0.009), '#c85a5a', mp)
        self.mouth = mp
        mp.scale = (1, 1, 0.35)
        if fangs:
            for sx in (-1, 1):
                cone(0.012, 0, 0.04, (sx * 0.022, -0.016, -0.03), (math.pi, 0, 0), m='#ffffff', parent=mp)
        if pointy_ears:
            for sx in (-1, 1):
                cone(0.05, 0, 0.14, (sx * R * 0.9, 0.0, R * 0.55), (0, sx * -0.5, 0), m=hair, parent=head)
        if stubble:
            sphere(1, (0, -R * 0.42, -0.14), (0.205, 0.17, 0.11), mat(stubble, 0.9), head)
        if beard:
            sphere(1, (0, -R * 0.5, -0.2), (0.17, 0.13, 0.085), beard, head)
            for sx in (-1, 1):
                sphere(1, (sx * 0.16, -R * 0.45, -0.1), (0.05, 0.08, 0.09), beard, head)
        if mustache:
            for sx in (-1, 1):
                sphere(1, (sx * 0.03, -R * 0.9, -0.075), (0.045, 0.02, 0.018), mustache, head, rot=(0, sx * 0.3, 0))
        if glasses:
            for sx in (-1, 1):
                torus(0.045, 0.006, (sx * 0.088, -R * 0.92, 0.035), (math.pi / 2, 0, 0), m='#222222', parent=head)
        # cabelo
        hm = mat(hair, 0.65)
        if hair_style == 'wavy':      # Jane: loiro ondulado
            _hair_cap(R, head, hm, off=(0, 0.07, 0.105), sc=(1.05, 1.05, 1.0))
            rnd = random.Random(7)
            for i in range(26):
                a = rnd.uniform(-math.pi * 0.95, math.pi * 0.95)
                el = rnd.uniform(0.25, 0.95)
                x = math.sin(a) * math.cos(el) * R * 1.02
                y = -math.cos(a) * math.cos(el) * R * 1.02
                z = math.sin(el) * R * 1.05
                if abs(a) < 1.2 and el < 0.8:
                    continue
                sphere(rnd.uniform(0.045, 0.065), (x, y + 0.03, z + 0.03), m=hm, parent=head, seg=16)
            # topete
            sphere(1, (0.07, -R * 0.62, R * 0.74), (0.16, 0.085, 0.07), hm, head, rot=(0.5, 0, -0.35))
            sphere(1, (-0.09, -R * 0.6, R * 0.76), (0.12, 0.08, 0.065), hm, head, rot=(0.5, 0, 0.4))
        elif hair_style == 'dean':      # curto, espetado
            _hair_cap(R, head, hm, off=(0, 0.06, 0.11), sc=(1.03, 1.04, 0.95))
            sphere(1, (0.0, -R * 0.5, R * 0.86), (0.16, 0.1, 0.075), hm, head, rot=(0.55, 0, 0))   # topete curto
            rnd = random.Random(11)
            for i in range(9):
                x = rnd.uniform(-0.12, 0.12)
                cone(0.035, 0, 0.07, (x, -R * 0.45 + rnd.uniform(-0.03, 0.05), R * 0.98), (rnd.uniform(-0.6, -0.2), x * 2, 0), m=hm, parent=head, verts=8)
        elif hair_style == 'sam':       # comprido ate o queixo, repartido
            _hair_cap(R, head, hm, off=(0, 0.07, 0.115), sc=(1.07, 1.07, 1.0))
            sphere(1, (-0.07, -R * 0.62, R * 0.75), (0.15, 0.07, 0.06), hm, head, rot=(0.5, 0, 0.45))
            sphere(1, (0, 0.1, -0.06), (0.29, 0.17, 0.25), hm, head)
            for sx in (-1, 1):
                sphere(1, (sx * 0.235, -0.02, -0.06), (0.07, 0.13, 0.2), hm, head)
        elif hair_style == 'cas':       # escuro, baguncado
            _hair_cap(R, head, hm, off=(0, 0.05, 0.1), sc=(1.04, 1.05, 0.97))
            rnd = random.Random(23)
            for i in range(16):
                a = rnd.uniform(-math.pi, math.pi); el = rnd.uniform(0.35, 1.0)
                sphere(rnd.uniform(0.04, 0.06), (math.sin(a) * math.cos(el) * R, -math.cos(a) * math.cos(el) * R + 0.03, math.sin(el) * R + 0.04), m=hm, parent=head, seg=12)
        elif hair_style == 'curly_long':
            _hair_cap(R, head, hm, off=(0, 0.04, 0.08), sc=(1.08, 1.08, 1.02))
            rnd = random.Random(31)
            for i in range(22):
                a = rnd.uniform(-2.2, 2.2); z = rnd.uniform(-0.3, 0.15)
                sphere(rnd.uniform(0.06, 0.08), (math.sin(a) * 0.27, math.cos(a) * 0.12 + 0.07, z), m=hm, parent=head, seg=14)
        elif hair_style == 'short':
            _hair_cap(R, head, hm, off=(0, 0.07, 0.125), sc=(1.03, 1.04, 0.95))
        elif hair_style == 'buzz':
            _hair_cap(R, head, hm, off=(0, 0.06, 0.11), sc=(1.02, 1.03, 0.95))
        elif hair_style in ('long', 'long_red'):
            _hair_cap(R, head, hm, off=(0, 0.06, 0.1), sc=(1.06, 1.06, 1.0))
            sphere(1, (0, 0.1, -0.12), (0.3, 0.17, 0.36), hm, head)
            for sx in (-1, 1):
                sphere(1, (sx * 0.23, 0.0, -0.13), (0.07, 0.12, 0.28), hm, head)
            # franja lateral
            sphere(1, (-0.08, -R * 0.66, R * 0.7), (0.16, 0.075, 0.07), hm, head, rot=(0.5, 0, 0.35))
        elif hair_style == 'bun':
            _hair_cap(R, head, hm, off=(0, 0.06, 0.1), sc=(1.05, 1.05, 1.0))
            sphere(0.1, (0, 0.18, 0.2), m=hm, parent=head)
        elif hair_style == 'gray':
            _hair_cap(R, head, hm, off=(0, 0.06, 0.115), sc=(1.03, 1.04, 0.95))
        elif hair_style == 'child':
            _hair_cap(R, head, hm, off=(0, 0.06, 0.1), sc=(1.05, 1.05, 1.0))
            for sx in (-1, 1):
                sphere(0.075, (sx * 0.27, 0.05, 0.05), m=hm, parent=head)
        if hat == 'sheriff':
            cyl(0.42, 0.025, (0, 0, R * 0.78), m='#c9a46a', parent=head, scale=(1, 0.9, 1))
            sphere(1, (0, 0, R * 0.92), (0.24, 0.23, 0.17), '#c9a46a', head)
            cyl(0.245, 0.04, (0, 0, R * 0.84), m='#6b4a2a', parent=head)
        elif hat == 'veil':
            torus(0.2, 0.03, (0, 0.02, R * 0.85), (0.3, 0, 0), m='#ffffff', parent=head)
            sphere(1, (0, 0.22, -0.05), (0.28, 0.08, 0.42), mat('#ffffff', 0.6), head)
        elif hat == 'straw':
            cyl(0.45, 0.02, (0, 0, R * 0.8), m='#e3c27a', parent=head)
            sphere(1, (0, 0, R * 0.9), (0.25, 0.25, 0.17), '#e3c27a', head)
            cyl(0.255, 0.04, (0, 0, R * 0.86), m='#8a4a2a', parent=head)
        elif hat == 'cap':
            sphere(1, (0, 0.01, R * 0.5), (0.285, 0.29, 0.25), '#7a2a22', head)
            box((0.26, 0.2, 0.02), (0, -0.3, R * 0.48), rot=(0.12, 0, 0), m='#7a2a22', parent=head, bevel=0.01)

    # -------------------- animacao
    def blink(self, frames):
        for f in frames:
            for e in self.eyes:
                key(e, 'scale', f - 2, (1, 1, 1)); key(e, 'scale', f, (1, 1, 0.1)); key(e, 'scale', f + 3, (1, 1, 1))

    def auto_blink(self, f0, f1, seed=0):
        rnd = random.Random(seed)
        f = f0 + rnd.randint(15, 50)
        fr = []
        while f < f1 - 4:
            fr.append(f); f += rnd.randint(55, 110)
        self.blink(fr)

    def idle(self, f0, f1, amp=1.0, seed=0):
        rnd = random.Random(seed)
        ph = rnd.uniform(0, 6)
        for f in range(f0, f1 + 1, 6):
            t = f / FPS
            self.chest.rotation_euler = (0.015 * amp * math.sin(t * 1.7 + ph), 0.02 * amp * math.sin(t * 1.1 + ph), 0)
            self.chest.keyframe_insert('rotation_euler', frame=f)
            self.head.rotation_euler = (0.03 * amp * math.sin(t * 1.3 + ph), 0.04 * amp * math.sin(t * 0.9 + ph * 2), 0.06 * amp * math.sin(t * 0.7 + ph))
            self.head.keyframe_insert('rotation_euler', frame=f)

    def talk(self, env, f0, f1, gain=1.0):
        """env: lista de amplitude (0..1) por frame global; aplica na boca."""
        for f in range(f0, f1 + 1, 2):
            a = env[f] if 0 <= f < len(env) else 0
            self.mouth.scale = (1 - 0.15 * a, 1, 0.35 + 1.9 * min(1, a * gain))
            self.mouth.keyframe_insert('scale', frame=f)

    def walk(self, f0, f1, p0, p1, steps_per_sec=2.0, bob=0.03):
        n = f1 - f0
        for i, f in enumerate(range(f0, f1 + 1, 2)):
            u = (f - f0) / max(1, n)
            pos = Vector(p0).lerp(Vector(p1), u)
            ph = (f - f0) / FPS * steps_per_sec * math.pi
            self.root.location = pos
            self.root.keyframe_insert('location', frame=f)
            self.hips.location = (0, 0, self.leg_len + abs(math.sin(ph)) * bob)
            self.hips.keyframe_insert('location', frame=f)
            for k, l in enumerate(self.legs):
                s = 1 if k == 0 else -1
                l.rotation_euler = (s * 0.5 * math.sin(ph), 0, 0)
                l.keyframe_insert('rotation_euler', frame=f)
            for k, a in enumerate(self.arms):
                s = -1 if k == 0 else 1
                a.rotation_euler = (s * 0.45 * math.sin(ph), a.rotation_euler[1], 0)
                a.keyframe_insert('rotation_euler', frame=f)
        # pose neutra no fim
        for l in self.legs:
            key(l, 'rotation_euler', f1 + 4, (0, 0, 0))
        for k, a in enumerate(self.arms):
            key(a, 'rotation_euler', f1 + 4, (0, (-1 if k == 0 else 1) * 0.12, 0))

    def arm(self, side, f, rot, hold=None, ease=8):
        """side 0=esquerda(da tela: direita do boneco -x), 1=+x. rot = euler (x,y,z)"""
        a = self.arms[side]
        key(a, 'rotation_euler', f - ease, tuple(a.rotation_euler))
        key(a, 'rotation_euler', f, rot)
        a.rotation_euler = rot

    def look(self, f, rx=0, rz=0, ease=8):
        h = self.neck
        key(h, 'rotation_euler', f - ease, tuple(h.rotation_euler))
        key(h, 'rotation_euler', f, (rx, 0, rz))

    def brows_set(self, f, angle_in=0.0, ease=6):
        for k, b in enumerate(self.brows):
            s = -1 if k == 0 else 1
            key(b, 'rotation_euler', f - ease, tuple(b.rotation_euler))
            key(b, 'rotation_euler', f, (0.25, s * angle_in, 0))

    def kneel(self):
        for l in self.legs:
            l.rotation_euler = (math.radians(88), 0, 0)
        self.hips.location = (0, 0, 0.1)

    def sit(self):
        """pose sentada (pernas para frente)"""
        for l in self.legs:
            l.rotation_euler = (math.radians(-85), 0, 0)
        self.hips.location = (0, 0, self.leg_len * 0.55)


# ---------------------------------------------------------- presets de personagens
def jane(**kw):
    d = dict(name='jane', hair='#d8a640', hair_style='wavy', eyes='#3f8ed8', jacket='#545a66', vest='#464b55',
             shirt='#f5f3ea', pants='#545a66', shoes='#3b2b22', brows='#b8862e')
    d.update(kw); return Char(**d)

def lisbon(**kw):
    d = dict(name='lisbon', hair='#3a2418', hair_style='long', eyes='#3c8a4a', jacket='#2c2f3a', vest=None,
             shirt='#cfd8e6', pants='#2c2f3a', shoes='#1b1b1b', female=True, badge=True, body_w=0.9, height=0.95)
    d.update(kw); return Char(**d)

def cho(**kw):
    d = dict(name='cho', skin='#e6c09a', hair='#141414', hair_style='buzz', eyes='#3a2a1a', jacket='#1f2229', vest=None,
             shirt='#ffffff', tie='#2a3550', pants='#1f2229')
    d.update(kw); return Char(**d)

def rigsby(**kw):
    d = dict(name='rigsby', hair='#6b4a2e', hair_style='short', eyes='#5a7a4a', jacket='#3d4a3a', vest=None,
             shirt='#dfe8f2', tie='#7a2a2a', pants='#3d4a3a', height=1.12)
    d.update(kw); return Char(**d)

def vanpelt(**kw):
    d = dict(name='vanpelt', hair='#c0471f', hair_style='long_red', eyes='#4a7ab0', jacket='#4a3a5a', vest=None,
             shirt='#f0e6f0', pants='#2a2a35', female=True, body_w=0.9, height=0.97, shoes='#222222')
    d.update(kw); return Char(**d)

def sheriff(**kw):
    d = dict(name='sheriff', hair='#9a9a9a', hair_style='gray', eyes='#4a5a6a', jacket='#b89a64', vest=None,
             shirt='#b89a64', pants='#5a4a32', mustache='#8a8a8a', hat='sheriff', badge=True, lapels=False,
             tie='#3a2a1a', brows='#7a7a7a', body_w=1.08)
    d.update(kw); return Char(**d)


# ------------------------------------------------------------------ render / camera / luz
def setup_render(engine='EEVEE', res=(1080, 1920), samples=8, sky='#8fd3ff', sky_strength=1.0):
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'Standard'
    sc.view_settings.look = 'None'
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    # luz ambiente neutra-quente; a cor de fundo visivel (camera) = sky
    nt = w.node_tree
    lp = nt.nodes.new('ShaderNodeLightPath'); mix = nt.nodes.new('ShaderNodeMixShader')
    bg2 = nt.nodes.new('ShaderNodeBackground')
    bg.inputs[0].default_value = (*hexc('#fff3e6'), 1); bg.inputs[1].default_value = 0.55 * sky_strength
    bg2.inputs[0].default_value = (*hexc(sky), 1); bg2.inputs[1].default_value = 1.0
    out = nt.nodes["World Output"]
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
    nt.links.new(bg.outputs[0], mix.inputs[1]); nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    if engine == 'EEVEE':
        sc.render.engine = 'BLENDER_EEVEE_NEXT'
        e = sc.eevee
        e.taa_render_samples = samples
        e.use_shadows = True
        e.shadow_ray_count = 1
        e.shadow_step_count = 2
        e.use_gtao = True
        e.gtao_distance = 0.6
        try:
            e.use_raytracing = False
        except Exception:
            pass
    elif engine == 'CYCLES':
        sc.render.engine = 'CYCLES'
        sc.cycles.samples = samples; sc.cycles.use_denoising = True
        sc.cycles.max_bounces = 3
    else:
        sc.render.engine = 'BLENDER_WORKBENCH'
        sh = sc.display.shading
        sh.light = 'STUDIO'; sh.color_type = 'MATERIAL'
        sh.show_shadows = True; sh.shadow_intensity = 0.35
        sh.show_cavity = True; sh.cavity_type = 'BOTH'
        sh.show_specular_highlight = True
        sc.display.render_aa = '8'
    return sc

def camera(loc, target, lens=35, name='cam'):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.sensor_fit = 'AUTO'
    cd.clip_start = 0.05; cd.clip_end = 200
    c = bpy.data.objects.new(name, cd); bpy.context.scene.collection.objects.link(c)
    c.location = loc
    t = empty(name + "_tgt", target)
    con = c.constraints.new('TRACK_TO'); con.target = t; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'
    bpy.context.scene.camera = c
    return c, t

def sun(rot=(0.75, 0.15, 0.6), energy=4.0, color='#fff1dc', angle=5):
    ld = bpy.data.lights.new("sun", 'SUN'); ld.energy = energy; ld.color = hexc(color); ld.angle = math.radians(angle)
    o = bpy.data.objects.new("sun", ld); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = rot
    return o

def point(loc, energy=200, color='#ffffff', radius=0.15):
    ld = bpy.data.lights.new("pt", 'POINT'); ld.energy = energy; ld.color = hexc(color); ld.shadow_soft_size = radius
    o = bpy.data.objects.new("pt", ld); bpy.context.scene.collection.objects.link(o)
    o.location = loc
    return o

def area(loc, rot, energy=300, size=3, color='#ffffff'):
    ld = bpy.data.lights.new("ar", 'AREA'); ld.energy = energy; ld.size = size; ld.color = hexc(color)
    o = bpy.data.objects.new("ar", ld); bpy.context.scene.collection.objects.link(o)
    o.location = loc; o.rotation_euler = rot
    return o

def checker_floor(c1='#f4b63a', c2='#ffd56b', size=40, scale=6.0, loc=(0, 0, 0), name='floor'):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    ch = nt.nodes.new('ShaderNodeTexChecker'); ch.inputs['Scale'].default_value = size / scale
    ch.inputs['Color1'].default_value = (*hexc(c1), 1); ch.inputs['Color2'].default_value = (*hexc(c2), 1)
    tc = nt.nodes.new('ShaderNodeTexCoord')
    nt.links.new(tc.outputs['UV'], ch.inputs['Vector']); nt.links.new(ch.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.45
    m.diffuse_color = (*hexc(c1), 1)
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    o = bpy.context.object; o.data.materials.append(m)
    return o

def floor(color='#f4b63a', size=60, loc=(0, 0, 0), rough=0.6):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    o = bpy.context.object; o.data.materials.append(mat(color, rough))
    return o

def stripes_wall(c1, c2, w=12, h=6, n=12, loc=(0, 3, 0), horizontal=True, depth=0.1):
    p = empty("wall", loc)
    for i in range(n):
        c = c1 if i % 2 == 0 else c2
        if horizontal:
            box((w, depth, h / n), (0, 0, h / n * (i + 0.5)), m=c, parent=p)
        else:
            box((w / n, depth, h), (-w / 2 + w / n * (i + 0.5), 0, h / 2), m=c, parent=p)
    return p

def tri_bg(colors, loc=(0, 6, 0), n=6, w=14, h=10):
    """faixas diagonais (sunburst simples) de fundo"""
    p = empty("tri", loc)
    for i in range(n):
        c = colors[i % len(colors)]
        box((w / n * 1.02, 0.05, h * 1.6), (-w / 2 + w / n * (i + 0.5), 0, h / 2), rot=(0, 0.35, 0), m=c, parent=p)
    return p

def env_amplitude(wav, fps=30, total=150.0):
    import struct, wave
    wf = wave.open(wav, 'rb'); sr = wf.getframerate(); n = wf.getnframes(); sw = wf.getsampwidth()
    raw = wf.readframes(n); wf.close()
    if sw == 2:
        import array
        a = array.array('h', raw)
        vals = [abs(x) / 32768 for x in a]
    else:
        vals = [0] * n
    hop = sr // fps
    env = []
    for i in range(int(total * fps) + 2):
        seg = vals[i * hop:(i + 1) * hop]
        env.append(min(1.0, (sum(seg) / len(seg)) * 9) if seg else 0)
    # suavizar
    out = []
    for i in range(len(env)):
        out.append(max(env[i], 0.6 * (env[i - 1] if i else 0)))
    return out


# ---------------------------------------------------------- Supernatural
def dean(**kw):
    d = dict(name='dean', hair='#7a5a38', hair_style='dean', eyes='#3f9a5a', jacket='#5a3a24', vest=None,
             shirt='#3d4a3a', pants='#2f3f5a', shoes='#3a2a1a', brows='#6a4a2e')
    d.update(kw); return Char(**d)

def sam(**kw):
    d = dict(name='sam', hair='#5a3a22', hair_style='sam', eyes='#6a8a4a', jacket='#8a3a2a', vest=None,
             shirt='#3a4a62', pants='#34445e', shoes='#3a2a1a', height=1.12, brows='#4a2e1a')
    d.update(kw); return Char(**d)

def john(**kw):
    d = dict(name='john', hair='#2e2218', hair_style='short', eyes='#5a4a3a', jacket='#4a3020', vest=None,
             shirt='#5a5a4a', pants='#2f3a4a', shoes='#2a1e14', beard='#3a2c20', height=1.05, brows='#2e2218')
    d.update(kw); return Char(**d)

def mary(**kw):
    d = dict(name='mary', hair='#e8c66a', hair_style='long', eyes='#4a8ad0', jacket='#f4f1ea', vest=None,
             dress='#f4f1ea', female=True, collar=False, body_w=0.9, shoes='#f4f1ea')
    d.update(kw); return Char(**d)

def castiel(**kw):
    d = dict(name='cas', hair='#2a2018', hair_style='cas', eyes='#2f7fff', jacket='#c9a97a', vest=None,
             shirt='#f4f4f0', tie='#2a4a9a', pants='#2a2a33', shoes='#1a1a1a', coat='#c9a97a', brows='#2a2018',
             )
    d.update(kw); return Char(**d)

def bobby(**kw):
    d = dict(name='bobby', hair='#7a6a5a', hair_style='short', eyes='#4a6a8a', jacket='#6a4a32', vest='#4a4a32',
             shirt='#8a6a4a', pants='#3a3a32', shoes='#2a1e14', beard='#7a6a5a', hat='cap', body_w=1.12, brows='#6a5a4a')
    d.update(kw); return Char(**d)


# ---------------------------------------------------------- Dexter
def dexter(**kw):
    d = dict(name='dexter', hair='#3a2418', hair_style='short', eyes='#5a7a4a', jacket='#3f6a9a', vest=None,
             shirt='#e8e0d0', pants='#a08a6a', shoes='#3a2a1a', brows='#2e1c12', height=1.02)
    d.update(kw); return Char(**d)

def dexter_kill(**kw):
    d = dict(name='dexterk', hair='#3a2418', hair_style='short', eyes='#5a7a4a', jacket='#4a5232', vest=None,
             shirt='#4a5232', pants='#3a3a32', shoes='#2a2a22', brows='#2e1c12', height=1.02, collar=False, hands='#2a2a2a')
    d.update(kw); return Char(**d)

def dexter_lumber(**kw):
    d = dict(name='dexterl', hair='#3a2418', hair_style='short', eyes='#5a7a4a', jacket='#8a2a22', vest=None,
             shirt='#2a2a2a', pants='#3a4a5a', shoes='#4a3220', brows='#2e1c12', height=1.02, beard='#3a2418')
    d.update(kw); return Char(**d)

def debra(**kw):
    d = dict(name='debra', hair='#3a2418', hair_style='long', eyes='#4a6a3a', jacket='#3a3a42', vest=None,
             shirt='#8a9aaa', pants='#2f3f5a', shoes='#1a1a1a', female=True, badge=True, body_w=0.9, height=0.97)
    d.update(kw); return Char(**d)

def harry(**kw):
    d = dict(name='harry', hair='#8a8478', hair_style='gray', eyes='#4a6a8a', jacket='#6a5a42', vest=None,
             shirt='#d8ccb0', tie='#3a3a5a', pants='#5a4e3a', shoes='#2a1e14', height=1.05, brows='#6a6458', badge=True)
    d.update(kw); return Char(**d)

def rita(**kw):
    d = dict(name='rita', hair='#e8cf8a', hair_style='short', eyes='#4a8ad0', jacket='#e88aa0', vest=None,
             dress='#e88aa0', female=True, collar=False, body_w=0.9, shoes='#c96a7a')
    d.update(kw); return Char(**d)

def doakes(**kw):
    d = dict(name='doakes', skin='#6a4430', hair='#1a1a1a', hair_style='bald', eyes='#2a1a10', jacket='#3a4a3a', vest=None,
             shirt='#3a4a3a', pants='#2a2a30', shoes='#1a1a1a', brows='#1a1a1a', height=1.06, body_w=1.1, collar=False, badge=True)
    d.update(kw); return Char(**d)

def trinity(**kw):
    d = dict(name='trinity', hair='#a8a49a', hair_style='gray', eyes='#3a4a5a', jacket='#5a4e40', vest=None,
             shirt='#c9c0a8', pants='#4a4238', shoes='#2a1e14', height=1.14, brows='#8a8478')
    d.update(kw); return Char(**d)

def brian(**kw):
    d = dict(name='brian', hair='#6a5a46', hair_style='short', eyes='#6aa8e8', jacket='#e8e8f0', vest=None,
             shirt='#c9d8e8', pants='#3a3a42', shoes='#1a1a1a', brows='#4a3e30')
    d.update(kw); return Char(**d)

def hannah(**kw):
    d = dict(name='hannah', hair='#f0d27a', hair_style='long', eyes='#4a8ad0', jacket='#ffffff', vest=None,
             dress='#7ab0e0', female=True, collar=False, body_w=0.9)
    d.update(kw); return Char(**d)

def kid(name='kid', age_h=0.55, **kw):
    d = dict(name=name, hair='#3a2418', hair_style='short', eyes='#5a7a4a', jacket='#e8d070', vest=None,
             shirt='#e8d070', pants='#4a6a9a', shoes='#d8d8e8', collar=False, height=age_h, body_w=0.74, brows='#2e1c12')
    d.update(kw); return Char(**d)
