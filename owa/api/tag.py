from flask import request
from ..models import Tag
from ..resource import OWAResource
from ..schemas import TagSchema, ArtistSchema
from ..shell import get_paginated, get_artists_by_tag
from ..utils import get_page_and_limit


class SingleTag(OWAResource):
    schema = TagSchema()
    routes = ('/tag/<name>/',)

    def get(self, name):
        return Tag.get_one_by({'name': name})


class ListTags(OWAResource):
    schema = TagSchema(many=True, only=('id', 'name'))
    routes = ('/tag/', '/tags')

    def get(self):
        page, limit = get_page_and_limit(request)
        return get_paginated(Tag, page, limit)


class ListArtistsByTag(SingleTag):
    schema = ArtistSchema(many=True, exclude=('tags',))
    routes = ('/tag/<tag>/artists',)

    def get(self, tag):
        page, limit = get_page_and_limit(request)
        return get_artists_by_tag(tag, page, limit)
