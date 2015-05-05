from marshmallow import Schema, post_dump
from marshmallow.fields import List, Nested, String
from .utils import Length

# sane defaults
common = ('name', 'id')


class BaseSchema(Schema):
    class Meta:
        additional = common

    @post_dump(raw=True)
    def add_root_if_many(self, data, many=False):
        if not many:
            return data
        else:
            ns = self.__class__.__name__.lower().split('schema')[0] + 's'
            return {ns: data}


class ErrorSchema(Schema):
    class Meta:
        additional = ('v',)

    @post_dump(raw=True)
    def v_to_error(self, data, many=False):
        return {'error': data['v']}


class ArtistSchema(BaseSchema):
    # tags = List(String)
    tags = List(Nested('TagSchema', only=common))


class TagSchema(BaseSchema):
    # artists = List(String)
    artists = List(Nested('ArtistSchema', only=common))


class TrackSchema(BaseSchema):
    artist = Nested('ArtistSchema', only=common)
    tracklists = List(Nested('TracklistSchema', only=common))
    length = Length()
    uuid = String()


class TracklistSchema(BaseSchema):
    tracks = List(Nested('TrackSchema', only=common))
