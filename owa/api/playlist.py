from flask import request
from ..models import Playlist, db
from . import SingleResource, ListResource
from ..schemas import PlaylistSchema, TrackSchema
from ..shell import extend_tracklist, new_playlist
from ..utils import marshal_with


class SinglePlaylist(SingleResource):
    schema = PlaylistSchema()
    routes = ('/playlist/<int:id>/',)
    model = Playlist

    @marshal_with(PlaylistSchema)
    def get(self, id):
        pl = Playlist.query.get(id)
        return pl or {'error': 'playlist not found'}

    @marshal_with(TrackSchema, many=True, only=('id', 'links', 'name', 'artist')) # noqa
    def post(self, id):
        playlist = Playlist.query.get(id)
        result, success = extend_tracklist(request.get_json(), playlist)
        if success:
            db.session.commit()
        else:
            db.session.rollback()
            return result


class ListPlaylists(ListResource):
    schema = PlaylistSchema(many=True)
    routes = ('/playlist/', '/tracklist/')
    model = Playlist

    def post(self):
        result, success = new_playlist(request.get_json())
        if success:
            db.session.commit()
            return (PlaylistSchema(only=('id', 'name', 'tracks'))
                    .dump(result)
                    .data)
        else:
            db.session.rollback()
            return result
