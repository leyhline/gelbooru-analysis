import sqlite3
import os.path
import logging
import logging.config
import yaml

SOURCE_PATH = os.path.dirname(__file__)
STANDARD_DB_PATH = SOURCE_PATH + "/../data/gelbooru.db"
# Load and configure logging.
with open(SOURCE_PATH + "/logging.yaml") as f:
    logging_config = yaml.load(f)
logging.config.dictConfig(logging_config)

class BooruDB:
    """Class for accesing a SQLite database. Use per "with" statement."""

    def __init__(self, db_path=STANDARD_DB_PATH):
        """Constructor: Set db_path=":memory:" for temporary in memory database."""
        self.db_path = db_path

    def __enter__(self):
        """Method for using "with" statement."""
        self._con = sqlite3.connect(self.db_path)
        self._cur = self._con.cursor()
        # Activate foreign key support.
        foreign_key_support = self._foreign_key_support()
        try:
            assert foreign_key_support == True
        except AssertionError:
            logging.warning("Your run-time SQLite library does not support foreign keys. " + 
                            "Proceed with caution. (Version {})".format(sqlite3.sqlite_version))
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Method for using "with" statement. Closes connection."""
        self._cur.close()
        self._con.close()

    def _foreign_key_support(self):
        """Activate and test foreign key support. Return True if supported."""
        self._cur.execute("PRAGMA foreign_keys = ON")
        self._cur.execute("PRAGMA foreign_keys")
        supported = self._cur.fetchone()
        if supported and supported[0] == 1:
            return True
        else:
            return False

    def insert_view(self, booru_view):
        """Extracts data from BooruView object and writes it into database."""
        try:
            # ENTITIES #
            # Table for views and some specific statistics.
            val_view = (booru_view.uid, booru_view.posted, booru_view.score,
                        booru_view.xsize, booru_view.ysize, booru_view.url)
            self._cur.execute("INSERT OR REPLACE INTO view VALUES (?,?,?,?,?,?)", val_view)
            tags, tag_types = zip(*booru_view.tagtuple)
            # Table for listing all tags.
            val_tag = ((tag,) for tag in tags)
            self._cur.executemany("INSERT OR IGNORE INTO tag(name) VALUES (?)", val_tag)
            # Table for listing all type of tags (like general, copyright, artist...).
            val_tag_type = ((tag_type,) for tag_type in tag_types)
            self._cur.executemany("INSERT OR IGNORE INTO tag_type(name) VALUES (?)", val_tag_type)
            # Table for listing rating types (safe, questionable, explicit).
            val_rating = (booru_view.rating,)
            self._cur.execute("INSERT OR IGNORE INTO rating(name) VALUES (?)", val_rating)
            # Table for listing all the people who posted pictures.
            val_poster = (booru_view.poster,)
            self._cur.execute("INSERT OR IGNORE INTO poster(name) VALUES (?)", val_poster)
            # RELATIONSHIPS #
            # Table for assigning tags to different views.
            val_tags = ((booru_view.uid, tag) for tag in tags)
            self._cur.executemany("INSERT OR IGNORE INTO tags " +
                                  "SELECT ?, id FROM tag WHERE name = ?", val_tags)
            # Table for assigning categories to tags.
            val_categorizes = booru_view.tagtuple
            self._cur.executemany("INSERT OR IGNORE INTO categorizes " +
                                  "SELECT tag.id, tag_type.id FROM tag, tag_type " +
                                  "WHERE tag.name = ? and tag_type.name = ?", val_categorizes)
            # Table for assigning a poster to his/her view.
            val_posts = (booru_view.uid, booru_view.poster)
            self._cur.execute("INSERT OR IGNORE INTO posts " +
                              "SELECT id, ? FROM poster WHERE name = ?", val_posts)
            # Table for assigning a rating to a view.
            val_rates = (booru_view.uid, booru_view.rating)
            self._cur.execute("INSERT OR IGNORE INTO rates " +
                              "SELECT ?, id FROM rating WHERE name = ?", val_rates)
            # Commit changes! (almost forgot this one)
            self._con.commit()
        except sqlite3.IntegrityError as err:
            logging.error("Database insertion failed: " + str(err))
            return
        except Exception as err:
            logging.critical("Aborting because of unhandled exception: " +
                              str(err) + " " + str(type(err)))
            raise err
        finally:
            logging.info("Inserting view {} into database.".format(booru_view.uid))
