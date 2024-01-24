from flask import request


def get_pagination_params():
    limit = request.args.get('size', default=25, type=int)
    offset = (request.args.get('page', default=1, type=int) - 1) * limit

    return {
        'limit': limit,
        'offset': offset
    }
