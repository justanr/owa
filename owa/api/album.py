from ..models import Album
from ..resource import SingleResource, ListResource
from ..schemas import AlbumSchema


class SingleAlbum(SingleResource):
    schema = AlbumSchema()
    routes = ('/album/<int:id>/',)
    model = Album


class ListAlbums(ListResource):
    schema = AlbumSchema(many=True)
    routes = ('/album/', '/tracklist/')
    model = Album
