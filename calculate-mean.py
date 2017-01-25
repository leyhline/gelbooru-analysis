#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for calculating the BGR mean over the whole trainingset.

Created on Wed Jan 25 22:47:18 2017

@copyright: 2017 Thomas Leyh
@licence: GPLv3
"""

import sys
import os
import cv2
import numpy as np


# Training on the first 3000 files of given dir.
TRAINING_CUT = (0, 3000)
# Default path if no arguments are given.
PATH = "data/montage"


def calculate_mean(images):
    """Calculate mean of all given images."""
    mean = np.zeros(3, dtype=np.float64)
    nb_images = TRAINING_CUT[1] - TRAINING_CUT[0]
    for img in images:
        mean += img.mean(axis=(0,1)) / nb_images
    return mean


if __name__ == "__main__":
    if len(sys.argv) != 2:
        path = PATH
    else:
        path = sys.argv[1]
    files = list(os.walk(path))[0][2]
    files = sorted(files, key=lambda x: int(os.path.splitext(x)[0]))
    # Not all images are used for training.
    files = files[TRAINING_CUT[0]:TRAINING_CUT[1]]
    files = [path + "/" + file for file in files]
    images = (cv2.imread(file) for file in files)
    mean = calculate_mean(images)
    print(mean)