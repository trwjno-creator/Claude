# uso: blender -b --python render_shot.py -- <shot_id> <out_dir> <modo: preview|full> [res_w res_h samples]
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy
import lib
from lib import reset, env_amplitude
import shots

argv = sys.argv[sys.argv.index('--') + 1:]
sid, out, mode = argv[0], argv[1], argv[2]
W, H, S = (int(argv[3]), int(argv[4]), int(argv[5])) if len(argv) > 5 else (720, 1280, 6)

ROOT = os.path.dirname(HERE)
tl = json.load(open(os.path.join(ROOT, 'audio', 'timeline.json')))
sh = [s for s in tl['shots'] if s['id'] == sid][0]
env = env_amplitude(os.path.join(ROOT, 'audio', 'narration.wav'), 30, tl['total'])

reset()
c = shots.Ctx(sh['nframes'], sh['f0'], env)   # frame local 1 -> frame global f0
shots.SHOTS[sid](c)
_mk = bpy.context.scene.timeline_markers
if len(_mk) and not any(m.frame <= 1 for m in _mk):      # camera principal ate o 1o corte
    _m = _mk.new('c1', frame=1); _m.camera = bpy.data.objects['cam']
sc = bpy.context.scene
sc.render.resolution_x, sc.render.resolution_y = W, H
if sc.render.engine == 'BLENDER_EEVEE_NEXT':
    sc.eevee.taa_render_samples = S
    sc.eevee.shadow_resolution_scale = 0.5
sc.frame_start, sc.frame_end = 1, sh['nframes']
os.makedirs(out, exist_ok=True)
if mode == 'preview' or mode.startswith('frames:'):
    n = sh['nframes']
    fl = [int(x) for x in mode[7:].split(',')] if mode.startswith('frames:') else [1, n // 3, (2 * n) // 3, n]
    for f in sorted(set(fl)):
        sc.frame_set(f)
        sc.render.filepath = os.path.join(out, f"{sid}_{f:04d}.png")
        bpy.ops.render.render(write_still=True)
else:
    sc.render.filepath = os.path.join(out, "")
    sc.render.use_overwrite = False   # permite retomar
    bpy.ops.render.render(animation=True)
print("DONE", sid)
