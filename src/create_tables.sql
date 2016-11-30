CREATE TABLE view(
    id INTEGER PRIMARY KEY,
    posted TEXT,
    rating TEXT,
    url TEXT,
    xsize INTEGER,
    ysize INTEGER
);

CREATE TABLE tag(
    name TEXT PRIMARY KEY
);

CREATE TABLE  tagged(
    view INTEGER,
    tag TEXT,
    FOREIGN KEY(view) REFERENCES view(id),
    FOREIGN KEY(tag) REFERENCES tag(name),
    PRIMARY KEY (view, tag)    
);
