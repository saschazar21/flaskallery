from flask import Blueprint, redirect, render_template, send_from_directory

from db.queries import paginate_all_collections, paginate_all_pictures, select_collection_by_path, select_picture_by_path
from utils.db import get_db_connection
from utils.pictures import PICTURES_ROOT, THUMBNAIL_ROOT
from utils.url import get_pagination_params

root = Blueprint('Root', __name__, template_folder='templates')


@root.route('/')
def index_route():
    params = get_pagination_params()
    connection = get_db_connection()
    page = paginate_all_pictures(params=params, connection=connection)
    collections = paginate_all_collections(params={}, connection=connection)
    return render_template('index.html', page=page, collections=collections, path='/')


@root.route('/collections')
def collections_index():
    params = get_pagination_params()
    connection = get_db_connection()
    page = paginate_all_collections(params=params, connection=connection)
    return render_template('collections.html', page=page, path='/collections')


@root.route('/collections/<path:path>')
def collection_by_path(path):
    params = path
    connection = get_db_connection()
    collection = select_collection_by_path(params, connection)
    return render_template('collection.html', collection=collection)


@root.route('/pictures')
def pictures_index():
    return redirect('/', code=301)


@root.route('/pictures/<path:path>')
def picture_by_path(path):
    params = path
    connection = get_db_connection()
    picture = select_picture_by_path(params, connection)
    return render_template('picture.html', picture=picture)


#
# Ideally the routes below are handled by a dedicated server like nginx, Apache, etc...
# with an adequate caching strategy for faster serving
#
# For development, they serve as a fallback route
#

@root.route('/p/<path:path>')
def send_picture(path):
    return send_from_directory(PICTURES_ROOT, path)


@root.route('/t/<path:path>')
def send_thumbnail(path):
    return send_from_directory(THUMBNAIL_ROOT, path)
