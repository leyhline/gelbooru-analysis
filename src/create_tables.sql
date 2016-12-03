CREATE TABLE view(
    id INTEGER PRIMARY KEY,
    posted TEXT,
    score INTEGER,
    xsize INTEGER,
    ysize INTEGER,
    url TEXT
) WITHOUT ROWID;

CREATE TABLE tag(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE rating(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE tag_type(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE poster(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE tags(
    view INTEGER REFERENCES view(id),
    tag INTEGER REFERENCES tag(id),
    PRIMARY KEY (view, tag)
);

CREATE TABLE categorizes(
    tag INTEGER REFERENCES tag(id),
    tag_type INTEGER REFERENCES tag_type(id),
    PRIMARY KEY (tag, tag_type)
);

CREATE TABLE posts(
    poster INTEGER REFERENCES poster(id),
    view INTEGER REFERENCES view(id),
    PRIMARY KEY (poster, view)
);

CREATE TABLE rates(
    view INTEGER REFERENCES view(id),
    rating INTEGER REFERENCES rating(id),
    PRIMARY KEY (view, rating)
);
