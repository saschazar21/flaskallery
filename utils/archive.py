import os
from shutil import make_archive, move
from tempfile import NamedTemporaryFile, gettempdir
from utils.pictures import PICTURES_ROOT

TEMP_ROOT = os.environ.get('TEMP_ROOT') or gettempdir()


def create_archive(path: str, name: str):
    collection_url = os.path.join(PICTURES_ROOT, path)
    archive_url = os.path.join(TEMP_ROOT, f"{name}.zip")

    if not os.path.exists(archive_url):
        with NamedTemporaryFile() as temp:
            print(collection_url, temp.name)
            make_archive(temp.name, format='zip', root_dir=collection_url)

            move(f"{temp.name}.zip", archive_url)

    return os.path.relpath(archive_url, TEMP_ROOT)
