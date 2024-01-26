from flask import request

DEFAULT_PAGE_SIZE = 24


def get_pagination_params():
    limit = request.args.get('size', default=DEFAULT_PAGE_SIZE, type=int)
    offset = (request.args.get('page', default=1, type=int) - 1) * limit

    return {
        'limit': limit,
        'offset': offset
    }
