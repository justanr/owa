from flask import request
from ..models import Playlist, db
from ..resource import SingleResource, ListResource
from ..schemas import PlaylistSchema, TrackSchema
from ..shell import extend_tracklist, new_playlist


class SinglePlaylist(SingleResource):
    schema = PlaylistSchema()
    routes = ('/playlist/<int:id>/',)
    model = Playlist

    def post(self, id):
        result, success = extend_tracklist(request.get_json(), id, model=Playlist)
        if success:
            data = (TrackSchema(many=True, only=('id', 'links', 'name', 'artist'))
                    .dump(result)
                    .data)
            return data
        else:
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
