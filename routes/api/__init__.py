import os
from flask import Blueprint, jsonify
from db.queries import paginate_all_collections, paginate_all_pictures, select_collection_by_path, select_picture_by_path
from utils.archive import create_archive
from utils.db import get_db_connection
from utils.pictures import Collection
from utils.url import get_pagination_params

api = Blueprint('API', __name__, template_folder='templates')


@api.errorhandler(404)
def page_not_found(_e):
    return jsonify({'error': 'Not Found'}), 404


@api.errorhandler(500)
def internal_server_error(_e):
    return jsonify({'error': 'Internal Server Error'}), 500


@api.route('/collections')
def all_collections():
    params = get_pagination_params()

    connection = get_db_connection()
    result = paginate_all_collections(params, connection)
    return jsonify(result)


@api.route('/collections/<path:path>')
def collection_by_path(path):
    params = path

    connection = get_db_connection()
    result = select_collection_by_path(params, connection)
    return jsonify(result)


@api.route('/collections/<path:path>/zip')
def zip_collection_by_path(path):
    params = path
    try:
        collection = select_collection_by_path(params)
        collection = Collection(
            path=collection['path'], name=collection['name'])

        archive_url = create_archive(
            path=collection.path, name=str(collection.hash))
        archive_url = os.path.join('/z', archive_url)

        return jsonify({'data': archive_url})
    except:
        return page_not_found(None)


@api.route('/pictures')
def all_pictures():
    params = get_pagination_params()

    connection = get_db_connection()
    result = paginate_all_pictures(params, connection)
    return jsonify(result)


@api.route('/pictures/<path:path>')
def pictures_by_path(path):
    params = path

    connection = get_db_connection()
    result = select_picture_by_path(params, connection)
    return jsonify(result)
