"""
    openwebamp.utils
    ~~~~~~~~~~~~~~~~

    Internal utilities for OpenWebAmp
"""
from flask import request
from marshmallow.fields import Field
from marshmallow.class_registry import get_class as get_schema


def get_page_and_limit(request=request):
    page = request.args.get('page', default=1, type=int)
    limit = request.args.get('limit', default=10, type=int)
    return page, limit


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
    cache = getattr(session, '_unique_cache', None)

    if cache is None:
        session._unique_cache = cache = {}

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


class Polymorphic(Field):
    def __init__(self, mapping, default_schema, nested_kwargs=None, **kwargs):
        self.mapping = mapping
        self.default_schema = default_schema
        self.nested_kwargs = nested_kwargs or {}
        super(Polymorphic, self).__init__(**kwargs)

    def _serialize(self, nested, attr, obj):
        if nested is None:
            return None

        nested_type = nested.__class__.__name__
        schema = self.mapping.get(nested_type, self.default_schema)

        if isinstance(schema, basestring):
            schema = get_schema(schema)

        return schema(**self.nested_kwargs).dump(nested).data


class Length(Field):
    def _serialize(self, value, attr, obj):
        return _seconds_to_human(value)
