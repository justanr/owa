from flask import request
from ..models import Artist, db
from . import SingleResource, ListResource
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
        artist = Artist.query.get(id)
        result, success = apply_tags_to_artist(request.get_json(), artist)

        if success:
            db.session.commit()
            return (TagSchema(many=True, only=('id', 'name', 'links'))
                    .dump(result)
                    .data)
        else:
            db.session.rollback()
            return result


class ListArtists(ListResource):
    schema = ArtistSchema(many=True, only=('id', 'name'))
    routes = ('/', '/artist/')
    model = Artist
