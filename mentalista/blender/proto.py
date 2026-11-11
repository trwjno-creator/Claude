import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
from lib import *
eng = sys.argv[-2]; out = sys.argv[-1]
reset()
setup_render(eng, (720, 1280), samples=6, sky='#7fd0ff')
checker_floor('#f6b33c', '#ffd36a', size=30, scale=0.7)
stripes_wall('#ff6fa8', '#ff9cc4', w=14, h=6, n=8, loc=(0, 3, 0), horizontal=False)
box((14, 0.2, 0.4), (0, 2.85, 0.2), m='#ffffff')
cs = [jane(loc=(-0.9, 0, 0)), lisbon(loc=(-0.3, 0.3, 0)), cho(loc=(0.3, 0.3, 0)), rigsby(loc=(0.9, 0.3, 0)), vanpelt(loc=(1.5, 0.3, 0)), sheriff(loc=(-1.6, 0.3, 0))]
cs[0].mouth.scale = (1, 1, 1.4)
sun(); 
cam, t = camera((0, -4.6, 1.9), (0, 0, 0.9), lens=30)
bpy.context.scene.render.filepath = out + '_wide.png'
bpy.ops.render.render(write_still=True)
cam.location = (-0.75, -1.3, 1.45); t.location = (-0.9, 0, 1.38); cam.data.lens = 50
bpy.context.scene.render.filepath = out + '_close.png'
bpy.ops.render.render(write_still=True)
