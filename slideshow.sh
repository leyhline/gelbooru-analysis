#!/usr/bin/env bash
# Randomized slideshow using feh.
# Usage: slideshow [DELAY] FOLDER
#	 where FOLDER is the folder containing the images
# 	 and DELAY is the slideshow delay in seconds.
# Also includes subfolders.

if [ $# -eq 1 ]; then
	folder=$1
elif [ $# -eq 2 ]; then
	delay="--slideshow-delay ${1}"
	folder=$2
else
	echo Wrong number of command line arguments.
	exit 1
fi

options="--draw-filename \
	 --fullscreen \
	 --hide-pointer \
	 --randomize \
	 --recursive"

feh $options $delay $folder
