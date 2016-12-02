import re
import logging
import logging.config
import yaml
import urllib.error
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlencode
from functools import reduce

BOORU_URL = "http://gelbooru.com/"
# Load and configure logging.
with open("logging.yaml") as f:
    logging_config = yaml.load(f)
logging.config.dictConfig(logging_config)
log_headline = logging.getLogger("headline")

class BooruView:
    """Class for parsing a view and mining useful data."""

    def __init__(self, soup, uid=None):
        """
        Contructor: Takes a BeautifulSoup object for further parsing.
        If uid is given, assert if parsed id is equal.
        """
        self.soup = soup
        self.tagtuple = self._parse_tags()
        self.tags = list(zip(*self.tagtuple))[0]
        self.url = self._parse_url()
        stats = self._parse_stats()
        self.uid = self.__maybeIndex("Id", stats)
        if uid:  # Safety check if you are parsing the correct view.
            try:
                assert uid == self.uid
            except AssertionError:
                logging.warning("Assertion of Id failed. " +
                                "View {} might be corrupted".format(self.uid))
        try:
            assert len(stats) == 4
        except AssertionError:
            logging.error("Invalid view {}. Missing statistics. Set to None.".format(self.uid))
        self.posted = self.__maybeIndex("Posted", stats)
        self.rating = self.__maybeIndex("Rating", stats)
        sizes = self.__maybeIndex("Size", stats)
        if sizes is not None:
            self.xsize = sizes[0]
            self.ysize = sizes[1]
        else:
            self.xsize = 0
            self.ysize = 0
        logging.info("View {} constructed.".format(self.uid))

    def __str__(self):
        """Return a string that looks the same as the title of the original site."""
        return self.soup.title.contents[0]

    def _parse_tags(self):
        """Return a tuple (tag, type) for all tags and their corresponding type."""
        tag_soup = self.soup.select("ul#tag-sidebar > li")
        types = (tag.get("class")[0][9:] for tag in tag_soup)
        tags = (tag.select("a")[1].contents[0] for tag in tag_soup)
        return list(zip(tags, types))

    def _parse_stats(self):
        """Return the statistics of the view."""
        stats = self.soup.select("div.sidebar3 > div#stats > ul > li")
        stats = (line.contents for line in stats)
        # Flatten stats. (list of list of strings -> list of strings)
        stats = (item for sublist in stats for item in sublist if isinstance(item, str))
        regex = re.compile(r"""\w+(?=:)""")  # Check if "BLAH:", match only BLAH
        # Match fitting lines in statistics element.
        matches = ((regex.match(entry), entry) for entry in stats if entry)
        matches = ((match[0].group(), match[1]) for match in matches if match[0] is not None)
        # Write relevant statistics into a new dictionary which is to be returned at the end.
        statdict = dict((self.__create_dict_entry(match) for match in matches
                         if self.__create_dict_entry(match)))
        return statdict

    def _parse_url(self):
        """Return the URL of the original image."""
        urls = self.soup.select("div.sidebar3 > div > ul > li > a")
        # Get tag containing the URL of the original image.
        return [url.attrs["href"] for url in urls if url.contents[0] == "Original image"][0]

    def __maybeIndex(self, key, dictionary):
        if key in dictionary:
            return dictionary[key]
        else:
            return None

    def __create_dict_entry(self, entry):
        key, value = entry
        if key == "Id":
            dict_entry = (key, int(value[4:]))
        elif key == "Posted":
            re_datetime = re.compile(r"""[\- :]""")  # Get date and time.
            param_datetime = map(int, re_datetime.split(value[8:]))
            obj_datetime = datetime(*param_datetime)
            dict_entry = (key, obj_datetime)
        elif key == "Size":
            sizes = value[6:].split("x")
            dict_entry = (key, (sizes[0], sizes[1]))
        elif key == "Rating":
            dict_entry = (key, value[8:])
        else:
            dict_entry = None
        return dict_entry


class BooruList:
    """
    Class for parsing one page of the listed results when querying the Booru.
    You should be able to iterate over the object to get BooruView objects.
    At the moment these should be at most 42.
    """

    def __init__(self, soup):
        """Constructor: Takes a soup object of the results page."""
        self.soup = soup
        parsed_views = self._parse_links()
        uids, urls = zip(*parsed_views)  # Unzip for better readability (Haha...)
        soups = zip((BeautifulSoup(urlopen(BOORU_URL + url), "html.parser") for url in urls), uids)
        # Create a list with views; soup[1] contains id for asserting correctness.
        self._views = (BooruView(soup[0], soup[1]) for soup in soups)
        logging.info("List constructed.")

    def __iter__(self):
        """For iterating through the BooruView objects."""
        return self._views.__iter__()

    def __next__(self):
        """For iterating through the BooruView objects."""
        print("1+1=2")
        try:
            view = self._views.__next__()
        except urllib.error.HTTPError as err:
            logging.error("Retrieving view failed. " + str(err))
            return None
        return view

    def __str__(self):
        return self.soup.title.contents[0]

    def _parse_links(self):
        """Returns a list of tumples (id, url) of all views of the page."""
        links = self.soup.select("div#post-list > div.content > div > span.yup > span > a")
        # Only includes objects with id attribute.
        links = [(int(url.get("id")[1:]), url.get("href")) for url in links
                 if url.get("id") is not None]
        return links


class BooruQuery:
    """
    A class for getting all the pages of a query.
    You should be able to iterate over the object to get the BooruList objects.
    """

    def __init__(self, tags):
        """Constructor: Takes a list of all the tags you want to query for."""
        self.tags = tags
        self.base_url = self._create_url()
        log_headline.info("Query constructed with tags: " + str(self))

    def __iter__(self):
        self.last_page = 0
        self.last_soup = None
        return self

    def __next__(self):
        try:
            if self.last_page == 0:
                self.last_soup = BeautifulSoup(urlopen(self.base_url), "html.parser")
            else:
                self.last_soup = BeautifulSoup(urlopen(next(self._get_next_soup())), "html.parser")
        except urllib.error.HTTPError as err:
            logging.error("Retrieving page {} failed. ".format(self.last_page + 1) + str(err))
            self.last_page += 1
            return None
        self.last_page += 1
        return BooruList(self.last_soup)
        
    def __str__(self):
        """Return a string that looks the same as the title of the original site."""
        return reduce(lambda s1, s2: s1 + ", " + s2, self.tags)

    def _create_url(self):
        get_args = {"page": "post", "s": "list"}
        tags = (tag.replace(" ", "_") for tag in self.tags)
        # Reduce the list to a single string and add to argument dictionary.
        get_args["tags"] = reduce(lambda s, t: s + " " + t, tags)
        url = BOORU_URL + "?" + urlencode(get_args)
        return url

    def _get_next_soup(self):
        pages = self.last_soup.select("div#paginator > div.pagination > a")
        # Get URL for next page (as generator).
        next_pages = (BOORU_URL + page.get("href") for page in pages
                      if not(page.get("alt")) and int(page.contents[0]) > self.last_page)
        return next_pages

    def generate_views(self):
        """Return a generator for all views resulting from the query."""
        return (view for list in self if list for view in list if view)
