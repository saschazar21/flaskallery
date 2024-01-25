CREATE TABLE IF NOT EXISTS collections (
    path TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS thumbnails (
    hash TEXT PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    height INTEGER NOT NULL,
    width INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS pictures (
    path TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    height INTEGER NOT NULL,
    width INTEGER NOT NULL,
    collection VARCHAR(255) NOT NULL,
    hash TEXT NOT NULL,
    FOREIGN KEY (hash) REFERENCES thumbnails(hash),
    FOREIGN KEY (collection) REFERENCES collections(name)
);