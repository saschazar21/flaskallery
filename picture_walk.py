import os
import sqlite3
from db import DATABASE, SCHEMA
from db.queries import create_collection, create_picture, create_thumbnail
from utils.pictures import PICTURES_ROOT, THUMBNAIL_ROOT, Collection, Picture


def init_db():
    db = sqlite3.connect(DATABASE)
    with open(SCHEMA, mode='r') as schema:
        db.cursor().executescript(schema.read())

    db.close()


def extract_collection_name(root):
    root, part = os.path.split(root)
    if part != 'bearb':
        return part
    else:
        return extract_collection_name(root)


def picture_walk():
    pictures = []
    for root, _dirs, files in os.walk(PICTURES_ROOT):
        for file in files:
            if file.endswith('.jpeg') or file.endswith('.jpg'):
                root, name = os.path.split(
                    os.path.join(root, file))
                relative_root = os.path.relpath(root, PICTURES_ROOT)
                collection_name = extract_collection_name(root)
                collection = Collection(relative_root, collection_name)
                picture = Picture(os.path.join(
                    relative_root, name), name, collection)
                picture.create_thumbnail()
                pictures.append(picture)

    return pictures


def update_db():
    collections = []
    pictures = []
    thumbnails = []
    for picture in picture_walk():
        collections.append(picture.collection.asdict())
        pictures.append(picture.asdict())
        thumbnails.append(picture.thumbnail.asdict())

    create_thumbnail(thumbnails)
    create_collection(collections)
    create_picture(pictures)

    return (collections, pictures, thumbnails)


if __name__ == '__main__':
    os.makedirs(THUMBNAIL_ROOT, exist_ok=True)
    init_db()
    update_db()
