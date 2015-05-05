from ..models import Tracklist
from ..resource import SingleResource, ListResource
from ..schemas import TracklistSchema


class SingleTracklist(SingleResource):
    schema = TracklistSchema()
    routes = ('/tracklist/<int:id>/',)
    model = Tracklist

    def post(self, id):
        # if tracklist is album: Left('Can not modify album.')
        # parse json looking for
        # track, position pairs
        # insert tracks at desired spots
        pass

class ListTracklists(ListResource):
    schema = TracklistSchema(many=True)
    routes = ('/tracklists/', '/tracklist/')
    model = Tracklist

    def post(self):
        # parse json to
        #   - tracklist name
        #   - any possible tracks
        # create tracklist
        pass
