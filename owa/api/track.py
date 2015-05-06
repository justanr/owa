from ..models import Track
from ..resource import SingleResource, ListResource
from ..schemas import TrackSchema


class SingleTrack(SingleResource):
    schema = TrackSchema()
    routes = ('/track/<int:id>/',)
    model = Track


class ListTracks(ListResource):
    schema = TrackSchema(many=True, only=('id', 'name', 'artist'))
    routes = ('/track/',)
    model = Track
