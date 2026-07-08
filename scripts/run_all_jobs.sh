#!/bin/bash
# Runs on H100: bg image + fast mosaic + 10 gallery compressions, then reports.
set -u
cd /mnt/data0/LX_Bench/CS/hyperframes
R=/mnt/data0/LX_Bench/CS/hyperframes/paper2video.github.io

python3 "$R/scripts/gen_page_bg.py" "$R/images/page_bg.png" > "$R/images/page_bg.log" 2>&1 &
BG=$!

python3 "$R/scripts/make_hero_mosaic.py" \
  --input-manifest "$R/assets/hero/selected_videos.json" \
  --output "$R/assets/hero/hero_mosaic.mp4" \
  --title-output "$R/assets/hero/hero_mosaic_title.mp4" \
  --speed 1.35 > "$R/assets/hero/render.log" 2>&1 &
MOSAIC=$!

for i in 01 04 06 09 12 16 23 24 27 29; do
  ffmpeg -y -loglevel error \
    -i "dataset/paper_to_video/skill_v2_batch_30/paper_$i/final/video.mp4" \
    -vf scale=1280:720 -c:v libx264 -crf 26 -preset veryfast \
    -c:a aac -b:a 96k -movflags +faststart \
    "$R/videos/n$i.mp4" 2>> "$R/videos/compress.log" &
done

wait
echo "=== bg image ==="; tail -2 "$R/images/page_bg.log"
echo "=== mosaic ==="; grep -vE '^\+ ' "$R/assets/hero/render.log" | tail -3
echo "=== gallery ==="; ls -la "$R"/videos/n*.mp4 2>/dev/null | wc -l; du -sh "$R"/videos/n*.mp4 2>/dev/null | tail -3
echo ALL-DONE
