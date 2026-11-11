#!/bin/bash
# Gera o video final: compoe os quadros + mixa audio + normaliza loudness.
set -e
cd "$(dirname "$0")"
T=/tmp/supernatural_parts; mkdir -p $T; rm -f $T/*
B=(0 1125 2250 3375 4500)
for i in 0 1 2 3; do python3 post/compose.py frames $T/p$i.mp4 ${B[$i]}:${B[$((i+1))]} > $T/log$i.txt 2>&1 & done
wait
for i in 0 1 2 3; do echo "file '$T/p$i.mp4'"; done > $T/list.txt
python3 audio/music.py   # depois da composicao (usa sfx_events.json gerado por ela)
ffmpeg -v error -y -f concat -safe 0 -i $T/list.txt -c copy /tmp/supernatural_video.mp4
ffmpeg -v error -y -i /tmp/supernatural_video.mp4 -i audio/final_mix.wav \
  -map 0:v -map 1:a -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -profile:v high -r 30 -af "loudnorm=I=-14:TP=-1.0:LRA=9" -ar 48000 -c:a aac -b:a 192k \
  -movflags +faststart -t 150 Supernatural_2m30_9x16.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of default=nw=1 Supernatural_2m30_9x16.mp4
