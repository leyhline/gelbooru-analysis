#!/usr/bin/env bash
# Count images and check for corruptions using GraphicsMagick.
# Usage: verify_download FOLDER
#	 where FOLDER is the folder containing the images.
# Furthermore there should be a textfile containing the download links.

path=$1
source_file=${path}.txt

current_count=$(ls $path | wc -w)
target_count=$(cat $source_file | wc -l)
echo Current number of images: $current_count
echo Total number of images:   $target_count
echo Checking for corrupted images...
for file in $(ls $path); do
	gm identify ${path}/${file} > /dev/null
done
