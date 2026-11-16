#!/bin/bash
# Render all frames in 4 parallel workers, then mux with audio.
set -e
cd "$(dirname "$0")"
OUT=${1:-preview.mp4}
TOTAL=$(python3 -c "import json;d=json.load(open('timeline.json'));print(int(d['total']*d['fps']))")
rm -rf frames; mkdir frames
Q=$(( (TOTAL + 3) / 4 ))
for i in 0 1 2 3; do
  node render.js frames frames $((i*Q)) $(( (i+1)*Q < TOTAL ? (i+1)*Q : TOTAL )) &
done
wait
python3 -I music2.py
AUD=music.wav
if [ -f voice.wav ]; then
  ffmpeg -loglevel error -y -i voice.wav -i music.wav -filter_complex "[1:a]volume=0.55[m];[0:a][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[a]" -map "[a]" mix.wav
  AUD=mix.wav
fi
ffmpeg -loglevel error -y -framerate 30 -i frames/f%05d.jpg -i $AUD -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
echo "done $OUT"
