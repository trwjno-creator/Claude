#!/bin/bash
set -e
cd "$(dirname "$0")"
OUT=${1:-out.mp4}
python3 -I sfx.py && python3 -I mixref.py
TOTAL=$(python3 -c "import json;d=json.load(open('timeline.json'));print(int(d['total']*d['fps']))")
rm -rf frames; mkdir frames; Q=$(( (TOTAL + 3) / 4 ))
for i in 0 1 2 3; do node render.js frames frames $((i*Q)) $(( (i+1)*Q < TOTAL ? (i+1)*Q : TOTAL )) & done; wait
ffmpeg -loglevel error -y -framerate 30 -i frames/f%05d.jpg -i mix_refmusic.wav -af "volume=0.89,alimiter=limit=0.85:level=false" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
echo "done $OUT"
