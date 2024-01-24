CREATE TABLE IF NOT EXISTS collections (
    path TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS pictures (
    path TEXT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    collection VARCHAR(255),
    FOREIGN KEY (collection) REFERENCES collections(name)
);