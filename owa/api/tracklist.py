from flask import request
from ..models import Playlist
from ..resource import SingleResource, ListResource
from ..schemas import TracklistSchema, TrackSchema
from ..shell import extend_tracklist, new_playlist


class SingleTracklist(SingleResource):
    schema = TracklistSchema()
    routes = ('/tracklist/<int:id>/',)
    model = Playlist

    def post(self, id):
        result, success = extend_tracklist(request.get_json(), id)
        if success:
            data = (TrackSchema(many=True, only=('id', 'links', 'name', 'artist'))
                    .dump(result)
                    .data)
            return data
        else:
            return result


class ListTracklists(ListResource):
    schema = TracklistSchema(many=True)
    routes = ('/tracklists/', '/tracklist/')
    model = Playlist

    def post(self):
        result, success = new_playlist(request.get_json())
        if success:
            return (TracklistSchema(only=('id', 'name', 'tracks'))
                    .dump(result)
                    .data)
        else:
            return result
