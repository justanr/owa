"""
    owa.utils.schema
    ````````````````
    Custom fields and schema operations for OWA
"""
from collections import Mapping
from functools import partial
from marshmallow import Schema
from marshmallow.base import SchemaABC
from marshmallow.fields import Field
from marshmallow.class_registry import get_class as get_schema
from marshmallow.compat import basestring
from werkzeug.wrappers import BaseResponse


__all__ = ('Polymorphic', 'Length', 'marshal_with')

_time_units = (
    3600,   # 1 hour
    60,     # 1 minute
    1,      # 1 second
)


def marshal_with(schema, **kwargs):
    """A spin of Flask-Restful's marshal_with decorator to work with
    Marshmallow serializers.
    """
    if isinstance(schema, basestring):
        schema = get_schema(schema)

    if not isinstance(schema, Schema):
        dumper = schema(**kwargs).dump
    else:
        dumper = partial(schema.dump, **kwargs)

    def deco(fn):
        def wrapper(*args, **kwargs):
            res = fn(*args, **kwargs)
            # result is a fully realized response
            # or a mapping already
            # pass it through
            if isinstance(res, (BaseResponse, Mapping)):
                return res
            else:
                return dumper(res).data
        return wrapper
    return deco


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
    """Allows polymorphic serialization of a field by nesting several potential
    schemas into one field. Can be used stand-alone or within a List field if
    the items should be handled differently.

    .. code-block python::
        class SomeSchema(Schema):
            some_field = Polymorphic(
                                mapping={
                                    'Frob': 'FrobSchema',
                                    'Thing': 'ThingSchema'},
                                default_schema='BaseSchema')

    :param mapping dict: Mapping of class names to schemas. Schemas may be given
    as strings or actual classes.
    :param default_schema: Default schema to fallback on if a suitable match
    isn't found.
    :param nested_kwargs dict: Keyword arguments to pass along to the nested
    schema, e.g. only, many, etc.

    Modified from example by `Steven Loria <https://github.com/marshmallow-code/marshmallow/issues/42#issuecomment-54719736>`
    """
    def __init__(self, schemas, default_schema, nested_kwargs=None, **kwargs):
        self.schemas = schemas
        self.default_schema = default_schema
        self.nested_kwargs = nested_kwargs or {}
        super(Polymorphic, self).__init__(**kwargs)

    def _serialize(self, nested, attr, obj):
        if nested is None:
            return None

        nested_type = nested.__class__.__name__
        schema = self.schemas.get(nested_type, self.default_schema)

        if isinstance(schema, basestring):
            schema = get_schema(schema)(**self.nested_kwargs)
            self.schemas[nested_type] = schema

        # already a schema instance
        # here for completion's sake though
        elif isinstance(schema, SchemaABC):
            pass

        elif isinstance(schema, type) and issubclass(schema, SchemaABC):
            schema = schema(**self.nested_kwargs)
            self.schemas[nested_type] = schema

        else:
            raise ValueError("Nested fields must be passed a Schema, not {0}"
                             .format(schema.__class__.__name__))

        # allow errors to propagate from dump
        return schema.dump(nested).data


class Length(Field):
    """Field to serialize second based length to a human readable form.
    """
    def _serialize(self, value, attr, obj):
        return _seconds_to_human(value)
