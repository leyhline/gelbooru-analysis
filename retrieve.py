"""
Search for images with specific tags on Gelbooru and
write their metadata to a database.

USAGE:
    retrieve.py [ options ... ] tags ...
    
DESCRIPTION
    Query for specified tags, visit every page and look at every image view
    to get its metadata.

    Saved data:
        - Image Id,
        - Date and time when image was posted,
        - Safety rating (can be 'Save', 'Questionable', 'Explicit'),
        - URL of original image for direct access,
        - Size of image on X axis (horizontal),
        - Size of image on Y axis (vertical).

    Because you can not list more than 20,000 results per query it is better
    to run several successive queries where you only select range of Id's
    but always with the same tags.
    
    Example: You search for "school uniform" rating:safe "silver hair"
        and the program internally searches for:
        "school uniform" rating:safe "silver hair" id:>=0     id:<20000
        "school uniform" rating:safe "silver hair" id:>=20000 id:<40000
        "school uniform" rating:safe "silver hair" id:>=40000 id:<60000
        ...
        "school uniform" rating:safe "silver hair" id:>=2980000 id:<3000000

    You can specifiy the step size (here: 10,000) with -s
    and the maximum (here: 3,000,000) with -mx.

OPTIONS
    TODO atm configuration is only possible per retrieve.yaml config file.
"""

import yaml
import src.scraper
import src.database
import sys
import time

# Default values for splitting queries into ranges of id's.
MINIMUM = 0
MAXIMUM = 3000000
STEPSIZE = 20000
# Default file for loading configurations from.
CONFIG_FILE = "retrieve.yaml"


def range_of_ids(start=MINIMUM, stop=MAXIMUM, step=STEPSIZE):
    greater_than = range(start, stop - step + 1, step)
    lesser_than  = range(start + step, stop + 1, step)
    ranges = list(zip(greater_than, lesser_than))
    offset = (stop - start) % step
    # Make sure to really stop where you specified without an offset.
    if offset:
        ranges.append((stop - offset, stop))
    return ranges


def file_config(filename=CONFIG_FILE):
    with open(filename) as f:
        config = yaml.load(f)
    return config


def print_status(uid, counter, last_printed, program_start_time=0, seconds_until_flush=1):
    if time.monotonic() - last_printed >= seconds_until_flush:
        message = "Last inserted view: {} - Total operations: {}".format(uid, counter)
        if program_start_time:
            message += " - Running since {} seconds.".format(int(time.monotonic() -
                                                                 program_start_time))
        sys.stdout.write(message)
        sys.stdout.flush()
        sys.stdout.write("\r")
        return time.monotonic()
    else:
        return last_printed


if __name__ == "__main__":
    config = file_config()
    tags = config["tags"]
    id_ranges = range_of_ids(config["minimum"], config["maximum"], config["stepsize"])
    counter = 0
    last_printed = 0
    start_time = time.monotonic()
    with src.database.BooruDB() as db:  # Open database connection.
        print("Opened database connection: " + db.db_path)
        for idr in id_ranges:
            range_tags = ["id:>=" + str(idr[0]), "id:<" + str(idr[1])]
            range_tags.extend(tags)
            # Query gelbooru with respective tags for id range specified in idr.
            bquery = src.scraper.BooruQuery(range_tags)
            bviews = bquery.generate_views()
            for bview in bviews:  # Insert every resulting view into database.
                db.insert_view(bview)
                counter += 1
                last_printed = print_status(bview.uid, counter, last_printed, start_time)
    sys.stdout.write("\n")
    print("Database connection properly closed. {} views retrieved.".format(counter))
    total_time = int(time.monotonic() - start_time)
    print("Total time: {} hours, {} seconds".format(total_time // 60, total_time % 60))
    
