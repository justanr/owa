from flask import request
from ..models import Artist
from ..resource import SingleResource, ListResource
from ..schemas import ArtistSchema, TagSchema
from ..shell import apply_tags_to_artist


class SingleArtist(SingleResource):
    schema = ArtistSchema()
    routes = ('/artist/<int:id>/',)
    model = Artist

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
        result, success = apply_tags_to_artist(request, id)

        if success:
            return (TagSchema(many=True, only=('id', 'name', 'links'))
                    .dump(result)
                    .data)
        else:
            return result


class ListArtists(ListResource):
    schema = ArtistSchema(many=True, only=('id', 'name'))
    routes = ('/', '/artist/', '/artists')
    model = Artist
