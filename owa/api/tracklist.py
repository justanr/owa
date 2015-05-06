from flask import request
from ..models import Tracklist
from ..resource import SingleResource, ListResource
from ..schemas import TracklistSchema, TrackSchema
from ..shell import extend_tracklist, new_tracklist


class SingleTracklist(SingleResource):
    schema = TracklistSchema()
    routes = ('/tracklist/<int:id>/',)
    model = Tracklist

    def post(self, id):
        result, success = extend_tracklist(request, id)
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
    model = Tracklist

    def post(self):
        result, success = new_tracklist(request)
        if success:
            return (TracklistSchema(only=('id', 'name', 'tracks'))
                    .dump(result)
                    .data)
        else:
            return result
