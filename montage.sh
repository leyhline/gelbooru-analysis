#!/usr/bin/env bash

if [ $# -eq 1 ]; then
	images=$1
	dest=montage.png
elif [ $# -eq 2 ]; then
	images=$1
	dest=$2
else
	echo Wrong number of command line arguments.
	exit 1
fi

# Randomly select 100 images.
images=$(ls $1 | sort -R | head -n100)
# Append absolute path.
for image in $images; do
	images_a+="`pwd`/${1}/${image} "
done
gm montage -geometry 200x200+0+0 -tile 10x10 $images_a $dest
