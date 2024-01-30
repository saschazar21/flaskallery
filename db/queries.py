import sqlite3
import json

from . import DATABASE
from utils.url import DEFAULT_PAGE_SIZE

INSERT_COLLECTION = """
INSERT INTO collections (path, name)
SELECT :path, :name
WHERE NOT EXISTS (
    SELECT 1 FROM collections WHERE collections.path = :path
)
"""

INSERT_PICTURE = """
INSERT INTO pictures (path, name, hash, collection, height, width)
SELECT :path, :name, :hash, :collection, :height, :width
WHERE NOT EXISTS (
    SELECT 1 FROM pictures WHERE pictures.path = :path
)
"""

INSERT_THUMBNAIL = """
INSERT INTO thumbnails (path, hash, height, width)
SELECT :path, :hash, :height, :width
WHERE NOT EXISTS (
    SELECT 1 FROM thumbnails where thumbnails.hash = :hash
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
            'path', collections.path,
            'pictures', (
                SELECT json_group_array(
                    json_object(
                        'name', pictures.name,
                        'path', pictures.path,
                        'hash', pictures.hash,
                        'height', pictures.height,
                        'width', pictures.width,
                        'thumbnail', thumbnails.json
                    )
                )
                FROM (
                    SELECT *
                    FROM pictures
                    WHERE pictures.collection = collections.path
                    ORDER BY pictures.name ASC
                ) AS pictures
                JOIN (
                    SELECT json_object(
                        'path', thumbnails.path,
                        'height', thumbnails.height,
                        'width', thumbnails.width
                    )
                    AS json, thumbnails.hash
                    FROM thumbnails
                ) thumbnails on pictures.hash = thumbnails.hash
            )
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

SELECT_COLLECTION_BY_PATH = """
SELECT json_object(
    'name', collections.name,
    'path', collections.path,
    'pictures', json_group_array(pictures.json)
)
AS result
FROM (
    SELECT *
    FROM collections
    WHERE collections.path = :path
)
AS collections
JOIN (
    SELECT json_object(
        'path', pictures.path,
        'name', pictures.name,
        'height', pictures.height,
        'width', pictures.width,
        'thumbnail', thumbnails.json
    )
    AS json, pictures.collection
    FROM (
        SELECT *
        FROM pictures
        ORDER BY pictures.name ASC
    )
    AS pictures
    JOIN (
        SELECT json_object(
            'path', thumbnails.path,
            'height', thumbnails.height,
            'width', thumbnails.width
        )
        AS json, thumbnails.hash
        FROM thumbnails
    ) thumbnails on pictures.hash = thumbnails.hash
) pictures on collections.path = pictures.collection
GROUP BY collections.path
"""

SELECT_ALL_PICTURES = """
SELECT pictures.name, pictures.path, pictures.hash, collections.json AS collection
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
            'hash', pictures.hash,
            'height', pictures.height,
            'width', pictures.width,
            'collection', collections.json,
            'thumbnail', thumbnails.json
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
        JOIN (
            SELECT json_object('path', path, 'height', height, 'width', width)
            AS json, hash
            FROM thumbnails
        ) thumbnails on pictures.hash = thumbnails.hash
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

SELECT_PICTURE_BY_PATH = """
SELECT json_object(
    'name', pictures.name,
    'path', pictures.path,
    'hash', pictures.hash,
    'height', pictures.height,
    'width', pictures.width,
    'collection', collections.json,
    'thumbnail', thumbnails.json
)
AS result
FROM (
    SELECT *
    FROM pictures
    WHERE pictures.path = :path
)
AS pictures
JOIN (
    SELECT json_object(
        'path', collections.path,
        'name', collections.name
    )
    AS json, path
    FROM collections
) collections on pictures.collection = collections.path
JOIN (
    SELECT json_object(
        'path', thumbnails.path,
        'height', thumbnails.height,
        'width', thumbnails.width
    )
    AS json, hash
    FROM thumbnails
) thumbnails on pictures.hash = thumbnails.hash
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


def create_collection(params: dict[str, str] | list[dict[str, str]], connection: sqlite3.Connection | None = None):
    query = Query(INSERT_COLLECTION, connection)
    return query.execute(params)


def create_picture(params: dict[str, str | int] | list[dict[str, str | int]], connection: sqlite3.Connection | None = None):
    query = Query(INSERT_PICTURE, connection)
    return query.execute(params)


def create_thumbnail(params: dict[str, str | int] | list[dict[str, str | int]], connection: sqlite3.Connection | None = None):
    query = Query(INSERT_THUMBNAIL, connection)
    return query.execute(params)


def paginate_all_collections(params: dict[str, int], connection: sqlite3.Connection | None = None):
    query = Query(PAGINATE_ALL_COLLECTIONS, connection)
    rows = query.execute({'limit': DEFAULT_PAGE_SIZE, 'offset': 0, **params})
    return json.loads(rows[0]['result'])


def paginate_all_pictures(params: dict[str, int], connection: sqlite3.Connection | None = None):
    query = Query(PAGINATE_ALL_PICTURES, connection)
    rows = query.execute({'limit': DEFAULT_PAGE_SIZE, 'offset': 0, **params})
    return json.loads(rows[0]['result'])


def select_all_collections(connection: sqlite3.Connection | None = None):
    query = Query(SELECT_ALL_COLLECTIONS, connection)
    return query.execute()


def select_collection_by_path(path: str, connection: sqlite3.Connection | None = None):
    query = Query(SELECT_COLLECTION_BY_PATH, connection)
    rows = query.execute({'path': path})
    return json.loads(rows[0]['result'])


def select_all_pictures(connection: sqlite3.Connection | None = None):
    query = Query(SELECT_ALL_PICTURES, connection)
    return query.execute()


def select_picture_by_path(path: str, connection: sqlite3.Connection | None = None):
    query = Query(SELECT_PICTURE_BY_PATH, connection)
    rows = query.execute({'path': path})
    return json.loads(rows[0]['result'])
