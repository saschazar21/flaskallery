from sqlite3 import Connection
from flask import Blueprint, g, jsonify, request
from db.queries import paginate_all_collections, paginate_all_pictures, select_collection_by_path, select_picture_by_path
from utils.db import get_db_connection
from utils.url import get_pagination_params

api = Blueprint('API', __name__, template_folder='templates')


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
