CREATE TABLE view(
    id INTEGER PRIMARY KEY,
    posted TEXT,
    rating TEXT,
    url TEXT,
    xsize INTEGER,
    ysize INTEGER
);

CREATE TABLE tag(
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE
);

CREATE TABLE  tagged_with(
    view INTEGER,
    tag INTEGER,
    FOREIGN KEY(view) REFERENCES view(id),
    FOREIGN KEY(tag) REFERENCES tag(id),
    PRIMARY KEY (view, tag)    
);
