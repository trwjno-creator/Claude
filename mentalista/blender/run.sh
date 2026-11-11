#!/bin/bash
# uso: run.sh <shot> <out> <mode> [w h samples]
export LD_LIBRARY_PATH=/opt/egl/root/usr/lib/x86_64-linux-gnu
export __EGL_VENDOR_LIBRARY_DIRS=/opt/egl/root/usr/share/glvnd/egl_vendor.d
export GBM_BACKENDS_PATH=/opt/egl/root/usr/lib/x86_64-linux-gnu/gbm
HERE=$(cd "$(dirname "$0")" && pwd)
xvfb-run -a -s "-screen 0 1280x1024x24" /opt/blender/blender-4.2.3-linux-x64/blender -b --python "$HERE/render_shot.py" -- "$@"
