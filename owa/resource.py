from flask.ext.restful import Resource
from inspect import isclass
from .compat import filter
from .schemas import BaseSchema
from .utils import get_page_and_limit


class OWAResource(Resource):
    routes = []
    route_opts = {}

    @classmethod
    def register(cls, api):
        """Helper method to make registering resources on multiple endpoints
        less painful.
        """
        api.add_resource(cls, *cls.routes, **cls.route_opts)


class SingleResource(OWAResource):
    schema = BaseSchema()
    model = None

    def get(self, **filters):
        if self.model:
            item = self.model.query.filter_by(**filters).first()
            if item:
                return self.schema.dump(item).data
            return {'error': 'no results found'}
        return {'error': 'no model found'}


class ListResource(OWAResource):
    schema = BaseSchema(many=True)
    model = None

    def get(self):
        if self.model:
            page, limit = get_page_and_limit()
            items = self.model.query.paginate(page, limit, error_out=False).items
            return self.schema.dump(items).data
        else:
            return {'error': 'no model found'}


def register_all_resources(module, api):
    classes = filter(isclass, module.__dict__.values())
    resources = filter(lambda x: issubclass(x, OWAResource), classes)
    for resource in resources:
        if resource is OWAResource:
            continue
        resource.register(api)
