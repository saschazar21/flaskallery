import hashlib
import os
from PIL import Image

PICTURES_ROOT = os.environ.get(
    'PICTURES_ROOT') or os.path.abspath(os.path.expanduser('~/Downloads'))

THUMBNAIL_ROOT = os.environ.get(
    'THUMBNAIL_ROOT') or os.path.abspath('./.cache')


class Collection:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.hash = str(self.__hash__())

    def __str__(self):
        return f"Collection(name={self.name}, path={self.path})"

    def __hash__(self):
        h = hashlib.sha1(self.path.encode('utf-8'), usedforsecurity=False)
        return int(h.hexdigest(), 16)

    def asdict(self):
        return {
            'name': self.name,
            'path': self.path
        }


class Thumbnail(Collection):
    size = (320, 320)

    def __init__(self, path, hash, height, width):
        super().__init__(path=path, name=hash)
        self.hash = hash
        self.height = height
        self.width = width

    def __str__(self):
        return f"Thumbnail(hash={self.hash}, path={self.path}, dimensions=({self.width}*{self.height}))"

    def asdict(self):
        return {
            'hash': self.hash,
            'path': self.path,
            'height': self.height,
            'width': self.width
        }


class Picture(Collection):

    def __init__(self, path, name, collection, width=0, height=0):
        super().__init__(path=path, name=name)
        self.collection = collection
        self.width = width
        self.height = height

    def __str__(self):
        return f"Picture(name={self.name}, path={self.path}, dimension=({self.height}*{self.width}), collection={self.collection})"

    def asdict(self):
        return {
            **super().asdict(),
            'hash': self.hash,
            'collection': self.collection.path,
            'height': self.height,
            'width': self.width
        }

    def get_thumbnail_name(self):
        return f"thumb_{self.hash}.jpg"

    def create_thumbnail(self):
        path = os.path.join(PICTURES_ROOT, self.path)
        im = Image.open(path)
        self.height, self.width = (im.height, im.width)
        im.thumbnail(Thumbnail.size)
        self.thumbnail = Thumbnail(
            path=self.get_thumbnail_name(),
            hash=self.hash,
            height=im.height,
            width=im.width
        )
        im.save(os.path.join(THUMBNAIL_ROOT, self.thumbnail.path))
