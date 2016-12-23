#!/usr/bin/env bash

# Randomly select 100 images.
images=$(ls $1 | sort -R | head -n100)
# Append absolute path.
for image in $images; do
	images_a+="`pwd`/${1}/${image} "
done
gm montage -geometry 200x200+0+0 -tile 10x10 $images_a montage.png
