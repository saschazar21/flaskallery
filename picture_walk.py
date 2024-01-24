import os
from db.queries import Query, INSERT_COLLECTION, INSERT_PICTURE

PICTURES_ROOT = os.environ.get(
    'PICTURES_ROOT') or os.path.abspath('~/Downloads')


class Collection:
    def __init__(self, path, name):
        self.path = path
        self.name = name

    def __str__(self):
        return f"Collection(name={self.name}, path={self.path})"


class Picture:
    def __init__(self, path, name, collection):
        self.path = path
        self.name = name
        self.collection = collection

    def __str__(self):
        return f"Picture(name={self.name}, path={self.path}, collection={self.collection})"


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
                pictures.append(picture)

    return pictures


def update_db():
    pictures = []
    collections = []
    for picture in picture_walk():
        collections.append({
            "name": picture.collection.name,
            "path": picture.collection.path
        })
        pictures.append({
            "name": picture.name,
            "path": picture.path,
            "collection": picture.collection.path
        })

    collections = Query(INSERT_COLLECTION).execute(collections)
    pictures = Query(INSERT_PICTURE).execute(pictures)

    return (collections, pictures)


if __name__ == '__main__':
    update_db()
