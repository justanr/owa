from flask import request
from ..models import Tag
from ..resource import SingleResource, ListResource, OWAResource
from ..schemas import TagSchema, ArtistSchema
from ..shell import get_artists_by_tag
from ..utils import get_page_and_limit


class SingleTag(SingleResource):
    schema = TagSchema()
    routes = ('/tag/<name>/',)
    model = Tag

    def post(self, name):
        # get tag
        # find provided artists that don't have the tag
        # add tag to remaining artists
        # return artist list
        pass


class ListTags(ListResource):
    schema = TagSchema(many=True, only=('id', 'name'))
    routes = ('/tag/', '/tags')
    model = Tag


class ListArtistsByTags(OWAResource):
    schema = ArtistSchema(many=True, exclude=('tags',))
    routes = ('/tag/<tag>/artists',)

    def get(self, tag):
        page, limit = get_page_and_limit(request)
        return get_artists_by_tag(tag, page, limit)
