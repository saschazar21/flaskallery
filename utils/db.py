from flask import g
from sqlite3 import Connection


def get_db_connection() -> Connection:
    return getattr(g, '_database', None)
