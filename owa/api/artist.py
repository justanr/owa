from flask import request
from operator import attrgetter
from ..models import Artist
from ..resource import OWAResource
from ..schemas import ArtistSchema, TagSchema
from ..shell import (apply_tags_to_artist,
                     get_paginated)
from ..utils import get_page_and_limit


class SingleArtist(OWAResource):
    schema = ArtistSchema()
    routes = ('/artist/<int:id>/',)

    def get(self, id):
        """Returns a single artist or error message.
        """
        return Artist.either(id, 'no artist found')

    def post(self, id):
        """Allows applying multiple tags to an artist.

        i.e. posting this to /artist/1/
        .. code-block:: raw
            {"tags": [
                "progressive death metal",
                "ambient death metal",
                "avant-garde metal"
            ]}

        Would apply the tags 'progressive', 'death', 'metal', 'ambient' and
        'avant-garde' to that artist.
        """
        return (apply_tags_to_artist(request, id),
                TagSchema(many=True, only=('id', 'name')))


class ListArtists(OWAResource):
    schema = ArtistSchema(many=True, only=('id', 'name'))
    routes = ('/', '/artist/', '/artists')

    def get(self):
        page, limit = get_page_and_limit(request)
        return get_paginated(Artist, page, limit)


class ListArtistTags(SingleArtist):
    schema = TagSchema(many=True, exclude=('artists',))
    routes = ('/artist/<int:id>/tags/',)

    def get(self, id):
        return Artist.either(id, 'no artist found').fmap(attrgetter('tags'))
