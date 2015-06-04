"""
    owa.utils.schema
    ````````````````
    Custom fields and schema operations for OWA
"""
from collections import Mapping
from functools import partial
from flask_restful import unpack
from marshmallow import Schema
from marshmallow.base import SchemaABC
from marshmallow.fields import Field
from marshmallow.class_registry import get_class as get_schema
from marshmallow.compat import basestring
from werkzeug.wrappers import BaseResponse
from ..compat import wraps
from .general import seconds_to_human


__all__ = ('Polymorphic', 'Length', 'marshal_with')


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
        @wraps(fn)
        def wrapper(*args, **kwargs):
            res = fn(*args, **kwargs)

            # result is a fully realized response
            # pass it through
            if isinstance(res, BaseResponse):
                return res

            data, code, headers = unpack(res)

            # if a mapping is handed back, it's
            # been serialized already so we don't bother
            # trying to re-serialize it
            if not isinstance(data, Mapping):
                data = dumper(data).data

            return data, code, headers

        return wrapper
    return deco

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
    as strings, classes or instances of a schema.
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

        nested_type = type(nested)
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
                             .format(type(schema)))

        # allow errors to propagate from dump
        return schema.dump(nested).data


class Length(Field):
    """Field to serialize second based length to a human readable form.
    """
    def _serialize(self, value, attr, obj):
        return seconds_to_human(value)
