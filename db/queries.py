import sqlite3
import json
from flask import g
from . import DATABASE

INSERT_COLLECTION = """
INSERT INTO collections (path, name)
SELECT :path, :name
WHERE NOT EXISTS (
  SELECT 1 FROM collections WHERE pictures.path = :path
)
"""

INSERT_PICTURE = """
INSERT INTO pictures (path, name, collection)
SELECT :path, :name, :collection
WHERE NOT EXISTS (
  SELECT 1 FROM pictures WHERE pictures.path = :path
)
"""

SELECT_ALL_COLLECTIONS = """
SELECT * FROM collections
ORDER BY collections.name DESC
"""

PAGINATE_ALL_COLLECTIONS = """
SELECT json_object(
    'data', (
        SELECT json_group_array(json_object(
            'name', collections.name,
            'path', collections.path
        ))
        FROM (
            SELECT *
            FROM collections
            ORDER BY collections.name DESC
            LIMIT :limit
            OFFSET :offset
        )
        AS collections
    ),
    'meta', (
        SELECT json_object(
            'page_size', :limit,
            'pages', cast(round(count(*) / :limit + 0.5, 0) as INTEGER),
            'page', cast(round((:offset + 1) / :limit + 0.5, 0) as INTEGER),
            'entries', count(*)
        )
        FROM collections
    )
)
AS result
"""

SELECT_ALL_PICTURES = """
SELECT pictures.name, pictures.path, collections.json AS collection
FROM pictures
JOIN (
    SELECT json_object('name', name, 'path', path) AS json, path
    FROM collections
) collections on pictures.collection = collections.path
ORDER BY pictures.collection DESC
"""

PAGINATE_ALL_PICTURES = """
SELECT json_object(
    'data', (
        SELECT json_group_array(json_object(
            'name', pictures.name, 
            'path', pictures.path, 
            'collection', collections.json
        ))
        FROM (
            SELECT *
            FROM pictures
            ORDER BY pictures.collection DESC
            LIMIT :limit
            OFFSET :offset
        )
        AS pictures
        JOIN (
            SELECT json_object('name', name, 'path', path)
            AS json, path
            FROM collections
        ) collections on pictures.collection = collections.path
    ),
    'meta', (
        SELECT json_object(
            'page_size', :limit,
            'pages', cast(round(count(*) / :limit + 0.5, 0) as INTEGER),
            'page', cast(round((:offset + 1) / :limit + 0.5, 0) as INTEGER),
            'entries', count(*)
        )
        FROM pictures
    )
)
AS result
"""


class Query:
    def __init__(self, query, connection: sqlite3.Connection | None = None):
        self.connection = connection or sqlite3.connect(DATABASE)
        self.connection.row_factory = sqlite3.Row
        self.q = query

    def execute(self, params: dict[str, str | int] | list[dict[str, str | int]] = {}):
        cursor = self.connection.cursor()
        if isinstance(params, list):
            cursor.executemany(self.q, params)
        else:
            cursor.execute(self.q, params)

        result = cursor.fetchall()
        result = list(map(lambda row: dict(row), result))

        self.connection.commit()

        return result


def create_collection(params: dict[str, str], connection: sqlite3.Connection | None = None):
    query = Query(INSERT_COLLECTION, connection)
    return query.execute(params)


def create_picture(params: dict[str, str], connection: sqlite3.Connection | None = None):
    query = Query(INSERT_PICTURE, connection)
    return query.execute(params)


def paginate_all_collections(params: dict[str, int], connection: sqlite3.Connection | None = None):
    query = Query(PAGINATE_ALL_COLLECTIONS, connection)
    rows = query.execute({'limit': 25, 'offset': 0, **params})
    return json.loads(rows[0]['result'])


def paginate_all_pictures(params: dict[str, int], connection: sqlite3.Connection | None = None):
    query = Query(PAGINATE_ALL_PICTURES, connection)
    rows = query.execute({'limit': 25, 'offset': 0, **params})
    return json.loads(rows[0]['result'])


def select_all_collections(connection: sqlite3.Connection | None = None):
    query = Query(SELECT_ALL_COLLECTIONS, connection)
    return query.execute()


def select_all_pictures(connection: sqlite3.Connection | None = None):
    query = Query(SELECT_ALL_PICTURES, connection)
    return query.execute()
