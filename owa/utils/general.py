"""
    owa.utils.flask?
    ````````````````
    Helpers used throughout OWA
"""

from flask import request


__all__ = ('get_page_and_limit',)


def get_page_and_limit(request=request):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    return page, limit
