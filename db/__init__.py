import sqlite3
from flask import g

DATABASE = 'db.sqlite3'
SCHEMA = 'schema.sql'


def init_db():
    db = get_db()
    with open(SCHEMA, mode='r') as f:
        db.cursor().executescript(f.read())

    db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)

    return db
