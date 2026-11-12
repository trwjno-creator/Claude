#!/bin/bash
# Gera o vídeo final: renderiza os quadros, sintetiza o áudio e junta tudo.
set -e
cd "$(dirname "$0")"
F=${FRAMES:-/tmp/cade_frames}
[ -n "$SKIP_RENDER" ] || { rm -rf "$F"; node render.js "$F" 30 4; }
[ -n "$NEW_VOICE" ] && python3 audio/gen_narration.py   # precisa de internet (edge-tts)
python3 audio/audio.py
ffmpeg -v error -y -framerate 30 -i "$F/f%05d.jpg" -i audio/mix.wav \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -profile:v high -r 30 \
  -af "loudnorm=I=-14:TP=-1.0:LRA=9" -ar 48000 -c:a aac -b:a 192k -movflags +faststart -t 40 \
  CadeMeuPar_40s_9x16.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of default=nw=1 CadeMeuPar_40s_9x16.mp4
