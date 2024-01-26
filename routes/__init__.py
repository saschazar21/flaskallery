from flask import Blueprint, redirect, render_template, request, send_from_directory

from db.queries import paginate_all_collections, paginate_all_pictures, select_collection_by_path, select_picture_by_path
from utils.db import get_db_connection
from utils.pictures import PICTURES_ROOT, THUMBNAIL_ROOT
from utils.url import DEFAULT_PAGE_SIZE, get_pagination_params

root = Blueprint('Root', __name__, template_folder='templates')


@root.errorhandler(404)
def page_not_found(_e):
    return render_template('404.html'), 404


@root.errorhandler(500)
def internal_server_error(_e):
    return render_template('500.html'), 500


@root.route('/')
def index_route():
    size = request.args.get('size', default=DEFAULT_PAGE_SIZE, type=int)
    params = get_pagination_params()
    connection = get_db_connection()
    page = paginate_all_pictures(params=params, connection=connection)
    collections = paginate_all_collections(params={}, connection=connection)
    return render_template('index.html', page=page, collections=collections, path='/', size=size)


@root.route('/collections')
def collections_index():
    size = request.args.get('size', default=DEFAULT_PAGE_SIZE, type=int)
    params = get_pagination_params()
    connection = get_db_connection()
    page = paginate_all_collections(params=params, connection=connection)
    return render_template('collections.html', page=page, path='/collections', size=size)


@root.route('/collections/<path:path>')
def collection_by_path(path):
    params = path
    connection = get_db_connection()

    try:
        collection = select_collection_by_path(params, connection)
        return render_template('collection.html', collection=collection)
    except:
        return page_not_found(None)


@root.route('/pictures')
def pictures_index():
    return redirect('/', code=301)


@root.route('/pictures/<path:path>')
def picture_by_path(path):
    params = path
    connection = get_db_connection()

    try:
        picture = select_picture_by_path(params, connection)
        collection = select_collection_by_path(
            picture.collection.path, connection)
        return render_template('picture.html', picture=picture, collection=collection)
    except:
        return page_not_found(None)


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
