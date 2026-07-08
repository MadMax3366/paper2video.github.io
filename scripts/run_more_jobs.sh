#!/bin/bash
# H100: compress 10 more gallery videos (batch 2 of 2).
set -u
cd /mnt/data0/LX_Bench/CS/hyperframes
R=/mnt/data0/LX_Bench/CS/hyperframes/paper2video.github.io
for i in 02 05 08 10 13 15 21 22 26 30; do
  ffmpeg -y -loglevel error \
    -i "dataset/paper_to_video/skill_v2_batch_30/paper_$i/final/video.mp4" \
    -vf scale=1280:720 -c:v libx264 -crf 26 -preset veryfast \
    -c:a aac -b:a 96k -movflags +faststart \
    "$R/videos/n$i.mp4" 2>> "$R/videos/compress2.log" &
done
wait
ls "$R"/videos/n*.mp4 | wc -l
echo MORE-DONE
