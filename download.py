#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrieve images (multithreaded) from gelbooru.

Usage:
You call the script with giving it a name of the file containing
the urls and the ids (for naming the files with their id) seperated by linebreak.

The script then tries to retrieve all these files and puts them into a new folder
with the basename of the file in the same path.

Unfortunately the implementation is really error prone if the server does not respond.
(Meaning: the exception handling does not work.)

@copyright: 2017 Thomas Leyh
@licence: GPLv3
"""

import os
import logging
import urllib.error
import sys
import concurrent.futures
from urllib.request import urlretrieve

EXCEPTION_LIMIT = 10
MAX_WORKERS = 4
exception_counter = 0
logging.basicConfig(filename="download.log", filemode="a", level=logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s")


def retrieve_image(url, dest_path):
    """Retrieves the image at url and downloads it to dest_path."""
    if not os.path.exists(dest_path):
        try:
            urlretrieve(url, dest_path)
        except urllib.error.URLError as err:
            if hasattr(err, "reason"):
                logging.error("Failed to reach server: " + str(err.reason))
            elif hasattr(err, "code"):
                logging.error("Server could not fulfill request: " + str(err.code))
            global exception_counter
            exception_counter += 1
            if exception_counter > EXCEPTION_LIMIT:
                logging.critical("Retrieving images failed more than {} times. Aborting.".format(EXCEPTION_LIMIT))
                raise(err)
            else:
                return
    else:
        logging.warning("File already exists: {}".format(dest_path))


def download_images(list_entry, dest_folder):
    """This function just gets some arguments ready for retrieve_image
       which is the function which really does all the work."""
    url, uid = list_entry.split()
    dest_file = str(uid) + os.path.splitext(url)[1]
    dest_path = dest_folder + "/" + dest_file
    logging.info("Retrieving image {} from {}".format(uid, url))
    retrieve_image(url, dest_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("No argument given. Usage: {} FILENAME".format(sys.argv[0]))
        sys.exit(1)
    inputpath = sys.argv[1]
    if not os.path.exists(inputpath):
        print("{} does not exist.".format(inputpath))
        sys.exit(1)
    pathname = os.path.abspath(inputpath)
    pathname, filename = os.path.split(pathname)
    basename = os.path.splitext(filename)[0]
    dest_folder = pathname + "/" + basename
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
    # Read file contents to list.
    url_list = []
    with open(inputpath) as f:
        for line in f:
            url_list.append(line)
    # Calling download_images() with multiple threads.
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as e:
        for i in range(len(url_list)):
            e.submit(download_images, url_list[i], dest_folder)
