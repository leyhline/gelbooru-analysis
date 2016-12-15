import os
import logging
import urllib.error
import sys
from urllib.request import urlretrieve

EXCEPTION_LIMIT = 10
exception_counter = 0
logging.basicConfig(filename="download.log", filemode="w", level=logging.INFO,
                    format = "%(asctime)s - %(levelname)s - %(message)s")


def retrieve_image(url, dest_path):
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
        logging.info("File already exists: {}".format(dest_path))


def download_images(url, uid, dest_folder):
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
        logging.error("{} does not exist.".format(inputpath))
        sys.exit(1)
    pathname = os.path.abspath(inputpath)
    pathname, filename = os.path.split(pathname)
    basename = os.path.splitext(filename)[0]
    dest_folder = pathname + "/" + basename
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)
    with open(inputpath) as f:
        for line in f:
            url, uid = line.split()
            download_images(url, uid, dest_folder)
