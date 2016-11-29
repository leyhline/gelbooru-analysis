import re
from datetime import datetime
from bs4 import BeautifulSoup

class BooruView:
    """Class for parsing a view and mining useful data."""

    def __init__(self, soup):
        """Contructor: Takes a BeautifulSoup object for further parsing."""
        self.soup = soup

    def parse_tags(self):
        """Return all tags of the view."""
        tags = self.soup.select("li.tag-type-general > a")
        tags = filter(lambda tag: tag != "?", (tag.contents[0] for tag in tags))
        return list(tags)


    def parse_stats(self):
        """Return the statistics of the view."""
        stats = self.soup.select("div.sidebar3 > div#stats > ul > li")
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
                id_pair = (key, int(entry[4:]))
                statlist.append(id_pair)
            elif key == "Posted":
                re_datetime = re.compile(r"""[\- :]""")  # Get date and time.
                param_datetime = map(int, re_datetime.split(entry[8:]))
                obj_datetime = datetime(*param_datetime)
                date_pair = (key, obj_datetime)
                statlist.append(date_pair)
            elif key == "Size":
                sizes = entry[6:].split("x")
                size_triple = (key, sizes[0], sizes[1])
                statlist.append(size_triple)
            elif key == "Rating":
                rating_pair = (key, entry[8:])
                statlist.append(rating_pair)
        return statlist


    def parse_url(self):
        """Return the URL of the original image."""
        urls = self.soup.select("div.sidebar3 > div > ul > li > a")
        # Get tag containing the URL of the original image.
        url = filter(lambda url: url.contents[0] == "Original image", urls)
        url = list(url)[0]
        return url.attrs["href"]
