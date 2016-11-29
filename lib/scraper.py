import re
from datetime import datetime
from bs4 import BeautifulSoup

class BooruView:
    """Class for parsing a view and mining useful data."""

    def __init__(self, soup):
        """Contructor: Takes a BeautifulSoup object for further parsing."""
        self.soup = soup
        self.tags = self._parse_tags()
        self.url = self._parse_url()
        stats = self._parse_stats()
        self.uid = self.__maybeIndex("Id", stats)
        self.posted = self.__maybeIndex("Posted", stats)
        self.rating = self.__maybeIndex("Rating", stats)
        sizes = self.__maybeIndex("Size", stats)
        if sizes is not None:
            self.xsize = sizes[0]
            self.ysize = sizes[1]


    def __str__(self):
        signature = ""
        for tag in self.tags:
            signature += tag + " "
        signature += "- Image View -  | " + self.uid + " | Gelbooru"
        return signature


    def _parse_tags(self):
        """Return all tags of the view."""
        tags = self.soup.select("li.tag-type-general > a")
        tags = filter(lambda tag: tag != "?", (tag.contents[0] for tag in tags))
        return list(tags)


    def _parse_stats(self):
        """Return the statistics of the view."""
        stats = self.soup.select("div.sidebar3 > div#stats > ul > li")
        stats = (line.contents for line in stats)
        # Flatten stats. (list of list of strings -> list of strings)
        stats = (item for sublist in stats for item in sublist)
        stats = filter(lambda item: isinstance(item, str), stats)
        regex = re.compile(r"""\w+(?=:)""")  # Check if "BLAH:", match only BLAH
        # Match fitting lines in statistics element.
        matches = ((regex.match(entry), entry) for entry in stats if entry)
        matches = ((match[0].group(), match[1]) for match in matches if match[0] is not None)
        # Write relevant statistics into a new dictionary which is to be returned at the end.
        statdict = dict()
        for entry in matches:
            key = entry[0]
            value = entry[1]
            if key == "Id":
                statdict[key] = value[4:]
            elif key == "Posted":
                re_datetime = re.compile(r"""[\- :]""")  # Get date and time.
                param_datetime = map(int, re_datetime.split(value[8:]))
                obj_datetime = datetime(*param_datetime)
                statdict[key] = obj_datetime
            elif key == "Size":
                sizes = value[6:].split("x")
                statdict[key] = (sizes[0], sizes[1])
            elif key == "Rating":
                statdict[key] = value[8:]
        return statdict


    def _parse_url(self):
        """Return the URL of the original image."""
        urls = self.soup.select("div.sidebar3 > div > ul > li > a")
        # Get tag containing the URL of the original image.
        url = filter(lambda url: url.contents[0] == "Original image", urls)
        url = list(url)[0]
        return url.attrs["href"]
    
    def __maybeIndex(self, key, dictionary):
        if key in dictionary:
            return dictionary[key]
        else:
            return None
