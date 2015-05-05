from flask import request, jsonify
from flask.ext.restful import Resource
from inspect import isclass
from werkzeug.wrappers import Response as ResponseBase
from .compat import filter
from .schemas import ErrorSchema, BaseSchema


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


def register_all_resources(module, api):
    classes = filter(isclass, module.__dict__.values())
    resources = filter(lambda x: issubclass(x, OWAResource), classes)
    for resource in resources:
        if resource is OWAResource:
            continue
        resource.register(api)
