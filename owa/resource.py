from flask import request, jsonify
from flask.ext.restful import Resource
from inspect import isclass
from pynads import Left, Right
from werkzeug.wrappers import Response as ResponseBase
from .compat import filter
from .schemas import ErrorSchema, BaseSchema
from .shell import get_paginated
from .utils import get_page_and_limit


class OWAResource(Resource):
    schema = BaseSchema
    routes = []
    route_opts = {}

    @classmethod
    def register(cls, api):
        """Helper method to make registering resources on multiple endpoints
        less painful.
        """
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

        # Convention is to return one of:
        # * Fully realized response
        # * Right(object)
        # * Left(error)
        # optionally a serializer can be returned with
        # the Right/Left option

        schema = self.schema

        resp = meth(*args, **kwargs)

        if isinstance(resp, tuple):
            resp, schema = resp

        if isinstance(resp, ResponseBase):
            return resp

        data = (resp.fmap(schema.dump)
                .get_or_call(ErrorSchema().dump, resp)).data
        return jsonify(data)


class SingleResource(OWAResource):
    model = None

    def get(self, **filters):
        model = Right(self.model) if self.model else Left('no model')
        return model.bind(lambda m: m.query.get_one_by(**filters))


class ListResource(OWAResource):
    model = None

    def get(self):
        model = Right(self.model) if self.model else Left('no model')
        page, limit = get_page_and_limit()
        return model.bind(lambda m: get_paginated(m, page, limit))


def register_all_resources(module, api):
    classes = filter(isclass, module.__dict__.values())
    resources = filter(lambda x: issubclass(x, OWAResource), classes)
    for resource in resources:
        if resource is OWAResource:
            continue
        resource.register(api)
