#!/usr/bin/env bash

# Copyright (C) 2017 Thomas Leyh
# Licenced under GPLv3

# Takes all webp images from the data directory and below and
# creates for all of these 10x10 tiled montages. The images are in random order.
# Also saves textfiles with the names of the individual tiles
# to make identifying them later possible.
 
# Uses sem from GNU parallel for speedup which is a really cool software.
# If you ever write about this project (haha...) don't forget to cite them.

output_dir=montage
tiles=100

cd data/cuts
# Create array of randomly shuffled images and count them.
images=$(find -name "*.webp*" | sort -R)
echo $images | tr " " "\n" > ${output_dir}/text/order.txt
count=$(echo $images | wc -w)
images=($images)

parallel --citation
for i in `seq 0 $tiles $(( $count - $tiles ))`; do
    isplit=${images[@]:$i:$tiles}
    echo $isplit | tr " " "\n" > ${output_dir}/text/${i}.txt
    sem -j+0 gm montage -geometry 200x200+0+0 -tile 10x10 -define webp:lossless=false,webp:image-hint=picture $isplit ${output_dir}/${i}.webp ";" echo Montage of images $i to $(($i + $tiles)) constructed.
done
sem --wait
