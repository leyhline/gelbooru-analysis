import sqlite3
import scraper

STANDARD_DB_PATH = "../data/gelbooru.db"


class BooruDB:
    """Class for accesing a SQLite database. Use per "with" statement."""

    def __init__(self, db_path=STANDARD_DB_PATH):
        """Constructor: Set db_path=":memory:" for temporary in memory database."""
        self.db_path = db_path

    def __enter__(self):
        """Method for using "with" statement."""
        self._con = sqlite3.connect(self.db_path)
        self._cur = self._con.cursor()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Method for using "with" statement. Closes connection."""
        self._cur.close()
        self._con.close()

    def insert_view(self, booru_view):
        """Extracts data from BooruView object and writes it into database."""
        val_view = (booru_view.uid, booru_view.posted.isoformat(), booru_view.rating,
                    booru_view.url, booru_view.xsize, booru_view.ysize)
        self._cur.execute("INSERT OR REPLACE INTO view VALUES (?,?,?,?,?,?)", val_view)
        val_tag = ((tag,) for tag in booru_view.tags)
        self._cur.executemany("INSERT OR IGNORE INTO tag(name) VALUES (?)", val_tag)
        val_tagged = ((booru_view.uid, tag) for tag in booru_view.tags)
        self._cur.executemany("INSERT OR IGNORE INTO tagged_with " +
                              "SELECT ?, id FROM tag WHERE name = ?", val_tagged)
        self._con.commit()
