#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script for batch cropping and scaling images.
At the end all images should be quadratic and of the same size.
Save images as lossless WebP (or whatever other format specified in OUTPUT_FORMAT).

@author: Thomas Leyh
"""

import sys
import os
import concurrent.futures
import cv2
import numpy as np

TARGET_SIZE = 200
OUTPUT_FORMAT = ".webp"
FEATURE_DETECTOR = cv2.AKAZE_create()
MAX_WORKERS = 4


def crop(img):
    """
    Crop image to make it quadratic using a feature detector for finding a nice center.
    """
    kp = FEATURE_DETECTOR.detect(img)
    ysize, xsize = img.shape[:2]
    smallest = min(xsize, ysize)
    if not kp:
        print("No keypoints. Crop image in the center.")
        if xsize > ysize:
            dst = img[:, xsize // 2 - smallest // 2:xsize // 2 + smallest // 2]
        else:
            dst = img[xsize // 2 - smallest // 2:xsize // 2 + smallest // 2,:]
        return dst
    kp_sum = np.zeros(abs(xsize - ysize))
    if xsize > ysize:
        x_or_y = 0
    else:
        x_or_y = 1
    for i in range(kp_sum.size):
        for k in kp:
            if k.pt[x_or_y] - i < smallest:
                kp_sum[i] += k.response
    imax = kp_sum.argmax()
    if x_or_y:
        dst = img[imax:imax+smallest,:]
    else:
        dst = img[:,imax:imax+smallest]
    return dst


def process_file(file, output_path):
    filename, img = file
    ysize, xsize = img.shape[:2]
    if xsize < TARGET_SIZE or ysize < TARGET_SIZE:
        print("Image size too small: {} x {}".format(xsize, ysize))
        return
    # Resize image.
    if xsize > ysize:
        xsize = round(xsize / ysize * TARGET_SIZE)
        ysize = TARGET_SIZE
    elif xsize < ysize:
        ysize = round(ysize / xsize * TARGET_SIZE)
        xsize = TARGET_SIZE
    else:
        xsize = ysize = TARGET_SIZE
    dst = cv2.resize(img, (xsize, ysize), interpolation=cv2.INTER_AREA)
    # Crop image if it is not already quadratic.
    if not xsize == ysize:
        dst = crop(dst)
    base, ext = os.path.splitext(filename)
    cv2.imwrite(output_path + "/" + base + OUTPUT_FORMAT, dst)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments.")
        sys.exit(1)
    path = sys.argv[1]
    files = list(os.walk(path))[0][2]
    output_path = path + "/" + "output"
    os.makedirs(output_path, exist_ok=True)
    images = ((file, cv2.imread(path + "/" + file)) for file in files
              if cv2.imread(path + "/" + file) is not None)
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as e:
        for file in images:
            e.submit(process_file, file, output_path)
