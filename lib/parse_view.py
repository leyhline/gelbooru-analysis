import re
from datetime import datetime
from bs4 import BeautifulSoup


def parse_tags(view):
    """Return all tags of the given view."""
    tags = view.select("li.tag-type-general > a")
    tags = filter(lambda tag: tag != "?", (tag.contents[0] for tag in tags))
    return list(tags)


def parse_stats(view):
    """Return the statistics of the given view."""
    stats = view.select("div.sidebar3 > div#stats > ul > li")
    stats = (line.contents for line in stats)
    # Flatten stats. (list of list of strings -> list of strings)
    stats = (item for sublist in stats for item in sublist)
    stats = filter(lambda item: isinstance(item, str), stats)
    regex = re.compile(r"""\w+(?=:)""")  # Check if "BLAH:", match only BLAH
    statlist = []
    for entry in stats:
        key = regex.match(entry)
        if not key:
            break
        key = key.group()
        if key == "Id":
            statlist.append(key)
            statlist.append(int(entry[4:]))
        elif key == "Posted":
            statlist.append(key)
            re_datetime = re.compile(r"""[\- :]""")  # Get date and time.
            param_datetime = map(int, re_datetime.split(entry[8:]))
            obj_datetime = datetime(*param_datetime)
            statlist.append(obj_datetime)
        elif key == "Size":
            statlist.append(key)
            sizes = entry[6:].split("x")
            statlist.extend(sizes)
        elif key == "Rating":
            statlist.append(key)
            statlist.append(entry[8:])
    return statlist


def parse_url(view):
    """Return the URL of the original image."""
    urls = view.select("div.sidebar3 > div > ul > li > a")
    # Get tag containing the URL of the original image.
    url = filter(lambda url: url.contents[0] == "Original image", urls)
    url = list(url)[0]
    return url.attrs["href"]
