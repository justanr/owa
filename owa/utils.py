"""
    openwebamp.utils
    ~~~~~~~~~~~~~~~~

    Internal utilities for OpenWebAmp
"""
from marshmallow.fields import Field
from flask import jsonify, request
from flask.ext.restful import Resource
from werkzeug.wrappers import Response as ResponseBase


def _unique(session, cls, hashfunc, queryfunc, constructor, *args, **kwargs):
    """Codifies the find_or_create behavior needed for certain lookups that
    either find an item in the database or create a new one.

    :param session: Current session
    :param cls: Model in question
    :param hashfunc: Hash function used to determine uniqueness
    :param queryfunc: Function that modifies a query used for the lookup
    :param constructor: Callable that returns a new model
    :param args: positional args to pass to the hashfunc, queryfunc and
    constructor
    :param kwargs: optional keywords to pass to the hashfunc, queryfunc and
    constructor

    Source:
    https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/UniqueObject
    """
    cache = getattr(session, '_unique_cache', {})

    if not cache:
        session._unique_cache = cache

    key = (cls, hashfunc(*args, **kwargs))

    if key in cache:
        return cache[key]
    else:
        with session.no_autoflush:
            obj = queryfunc(session.query(cls), *args, **kwargs).first()

            if not obj:
                obj = constructor(*args, **kwargs)
                session.add(obj)

        cache[key] = obj
        return obj


class UniqueMixin(object):
    """Implements the _unique function as a class mixin.
    """
    @classmethod
    def find_or_create(cls, session, *args, **kwargs):
        return _unique(session,
                       cls,
                       cls.unique_hash,
                       cls.unique_func,
                       cls,
                       *args, **kwargs)

    @classmethod
    def unique_hash(cls, *args, **kwargs):
        raise NotImplementedError("unique_hash not implemented")

    @classmethod
    def unique_func(cls, *args, **kwargs):
        raise NotImplementedError("unique_func not implemented")


class ReprMixin(object):
    '''Provides a string representible form for objects.'''
    repr_fields = ()

    def __repr__(self):
        reprs = getattr(self, 'repr_fields', ()) + ('id',)
        fields = {f: repr(getattr(self, f, '<BLANK>')) for f in reprs}
        # constructs a dictionary compatible pattern for formatting
        # {{{0}}} becomes {id} for example
        pattern = ' '.join(['{0}={{{0}}}'.format(f) for f in reprs])
        return '<{} {}>'.format(
            self.__class__.__name__,
            pattern.format(**fields))


_time_units = (
    3600,   # 1 hour
    60,     # 1 minute
    1,      # 1 second
)


def _seconds_to_human(seconds, units=_time_units):
    """Converter to transform a seconds based length into a huamn readable
    format. Smart enough to handle edge cases like exactly one minute or
    exactly three hours.

    :param seconds: A member of numbers.Number representing length
    :param units: Iterable of time units given in seconds
    """
    if not seconds:
        return '00:00'

    result = []

    for idx, unit in enumerate(_time_units, 1):
        part, seconds = seconds // unit, seconds % unit
        if part:
            result.append('{:0>2}'.format(part))
        if not seconds:
            # bail early and build the rest of the length
            result.extend(['00'] * (len(units) - idx))
            break

    if len(result) < 2:
        part.insert(0, '00')

    return ':'.join(result)


class Length(Field):
    def _serialize(self, value, attr, obj):
        return _seconds_to_human(value)


class OWAResource(Resource):
    schema = None
    schema_opts = {}
    routes = []
    route_opts = {}

    @classmethod
    def register(cls, api):
        api.add_resource(cls, *cls.routes, **cls.route_opts)

    def dispatch_request(self, *args, **kwargs):
        """OWA only deals with JSON and uses Marshmallow to do so.
        Instead of adding jsonsify(cls.scheme(data, **cls.schema_opts).data)
        to every route by hand, the behavior is simply encoded here.
        """
        # Taken from Flask and Flask-Restful
        meth = getattr(self, request.method.lower(), None)
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)
        assert meth is not None, \
            'Unimplemented method {!r}'.format(request.method)

        for decorator in self.method_decorators:
            meth = decorator(meth)

        resp = meth(*args, **kwargs)

        if isinstance(resp, ResponseBase):
            return resp

        if self.schema:
            return jsonify(self.schema.dump(resp).data)
        else:
            return jsonify(resp)
