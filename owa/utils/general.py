"""
    owa.utils.flask?
    ````````````````
    Helpers used throughout OWA
"""

from flask import request
from functools import partial
from ..compat import wraps, filter

__all__ = ('get_page_and_limit', 'seconds_to_human', 'kwargs_decorator',
           'multifilter')

_time_units = (
    3600,   # one hour
    60,     # one minute
    1       # one second
)


def seconds_to_human(seconds, units=_time_units):
    """Convert a seconds based time stamp to a human readable format
    """

    if not seconds:
        return '00:00'

    result = []

    for idx, unit in enumerate(_time_units, 1):
        part, seconds = seconds // unit, seconds % unit
        if part:
            result.append('{:0>2}'.format(part))
        if not seconds:
            # bail early and build rest of the length
            # handles edge cases like exactly one hour
            # or exactly three minutes
            result.extend(['00'] * (len(units) - idx))
            break

    if len(result) < 2:
        result.insert(0, '00')

    return ':'.join(result)


def get_page_and_limit(request=request):
    """Helper to avoid a little bit of boiler plate when extracting page and
    limit URL query parameters.
    """
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    return page, limit


def kwargs_decorator(deco):
    """Allows creating decorators that take keyword arguments (either optional
    or required).

    .. code-block python ::
        @kwargs_decorator
        def debugly(func, prefix='DEBUG:'):
            @wraps(func)
            def wrapper(*a, **k):
                print(prefix, func, a, k, sep=' ')
                return func(*a, **k)
            return wrapper

        @debugly(prefix='***DEBUG***')
        def adder(a, b):
            return a+b

        >>> adder(1,2)
        '***DEBUG*** <function adder at 0xd34db33f> (1,2) {}'
        ... 3

        @debugly # note: no parens needed when not passing any keywords
        def subber(a, b):
            return a - b

        >>> subber(2, 1)
        'DEBUG <function subber at 0x7f86180c8a60> (2, 1) {}'
        ... 1
    """
    @wraps(deco)
    def wrapper(func=None, **kwargs):
        if func is None:
            return partial(wrapper, **kwargs)
        return deco(func, **kwargs)
    return wrapper


def multifilter(source, *filters):
    """Applies many filters to a single source.

    .. code-block python ::
        >>> filters = [str.isupper, lambda s: s.endswith('WORLD')]
        >>> entries = ['hello world', 'HELLO WORLD', 'HELLO EARTH']
        >>> list(multifilter(entries, *filters))
        ... ['HELLO WORLD']

    """
    for filt in filters:
        source = filter(filt, source)
    return source
