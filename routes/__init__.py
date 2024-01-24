from flask import Blueprint, render_template

from db.queries import paginate_all_collections, paginate_all_pictures
from utils.db import get_db_connection
from utils.url import get_pagination_params

root = Blueprint('Root', __name__, template_folder='templates')


@root.route('/')
def index_route():
    params = get_pagination_params()
    connection = get_db_connection()
    page = paginate_all_pictures(params=params, connection=connection)
    collections = paginate_all_collections(params={}, connection=connection)
    return render_template('index.html', page=page, collections=collections, path='/')
