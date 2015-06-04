from flask.ext.restful import Resource
from inspect import isclass
from operator import attrgetter
from ..schemas import BaseSchema
from .general import get_page_and_limit, multifilter


__all__ = ('OWAResource', 'SingleResource', 'ListResource',
           'register_all_resources')


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
    filters = [isclass, lambda r: issubclass(r, OWAResource),
               attrgetter('routes')]

    for resource in multifilter(module.__dict__.values(), *filters):
        resource.register(api)
