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
"""

# Default values for splitting queries into ranges of id's.
MINIMUM = 0
MAXIMUM = 3000000
STEPSIZE = 20000


def range_of_ids(start=MINIMUM, stop=MAXIMUM, step=STEPSIZE):
    greater_than = range(start, stop - step + 1, step)
    lesser_than  = range(start + step, stop + 1, step)
    return zip(greater_than, lesser_than)


if __name__ == "__main__":
    for tup in range_of_ids():
        print(tup)
