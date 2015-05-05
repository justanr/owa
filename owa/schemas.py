from marshmallow import Schema, post_dump
from marshmallow.fields import List, Nested, String
from flask.ext.marshmallow.fields import AbsoluteUrlFor as URL, Hyperlinks
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
    tags = List(Nested('TagSchema', only=('id', 'name', 'links')))
    links = Hyperlinks({
        'self': URL('singleartist', id='<id>'),
        'collection': URL('listartists')
    })


class TagSchema(BaseSchema):
    # artists = List(String)
    artists = List(Nested('ArtistSchema', only=('id', 'name', 'links')))
    links = Hyperlinks({
        'self': URL('singletag', name='<name>'),
        'collection': URL('listtags')
    })


class TrackSchema(BaseSchema):
    artist = Nested('ArtistSchema', only=('id', 'name', 'links'))
    tracklists = List(Nested('TracklistSchema', only=('id', 'name', 'links')))
    length = Length()
    uuid = String()
    links = Hyperlinks({
        'self': URL('singletrack', id='<id>'),
        'collection': URL('listtracks')
    })


class TracklistSchema(BaseSchema):
    tracks = List(Nested('TrackSchema', only=('id', 'name', 'artist', 'links')))
    links = Hyperlinks({
        'self': URL('singletracklist', id='<id>'),
        'collection': URL('listtracklists')
    })
