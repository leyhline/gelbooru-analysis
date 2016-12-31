#!/usr/bin/env bash

output_dir=/montage
tiles=100

cd data
# Create array of randomly shuffled images and count them.
images=$(find -name "*.webp*" | sort -R)
echo $images | tr " " "\n" > ${output_dir}/text/order.txt
count=$(echo $images | wc -w)
images=($images)

parallel --citation
for i in `seq 0 $tiles $(( $count - $tiles ))`; do
    isplit=${images[@]:$i:$tiles}
    echo $isplit | tr " " "\n" > ${output_dir}/text/${i}.txt
    sem -j+0 gm montage -geometry 200x200+0+0 -tile 10x10 -define webp:lossless=true $isplit ${output_dir}/${i}.webp ";" echo Montage of images $i to $(($i + $tiles)) constructed.
done
sem --wait
