from ..models import Tag
from ..resource import SingleResource, ListResource
from ..schemas import TagSchema


class SingleTag(SingleResource):
    schema = TagSchema()
    routes = ('/tag/<name>/',)
    model = Tag


class ListTags(ListResource):
    schema = TagSchema(many=True, only=('id', 'name'))
    routes = ('/tag/',)
    model = Tag
