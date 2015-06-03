from marshmallow import Schema, post_dump
from marshmallow.fields import List, Nested, String
from flask.ext.marshmallow.fields import AbsoluteUrlFor as URL, Hyperlinks
from .utils import Length, Polymorphic

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


class ArtistSchema(BaseSchema):
    tags = List(Nested('TagSchema', only=('id', 'name', 'links')))
    links = Hyperlinks({
        'self': URL('singleartist', id='<id>'),
        'collection': URL('listartists')
    })
    albums = List(Nested('AlbumSchema', only=('id', 'name', 'links')))


class TagSchema(BaseSchema):
    artists = List(Nested('ArtistSchema', only=('id', 'name', 'links')))
    links = Hyperlinks({
        'self': URL('singletag', name='<name>'),
        'collection': URL('listtags')
    })


class TrackSchema(BaseSchema):
    artist = Nested('ArtistSchema', only=('id', 'name', 'links'))
    tracklists = List(Polymorphic(
        schemas={'Album': 'AlbumSchema', 'Playlist': 'PlaylistSchema'},
        default_schema='BaseSchema',
        nested_kwargs={'only': ('id', 'links', 'name')}
    ))
    length = Length()
    uuid = String()
    links = Hyperlinks({
        'self': URL('singletrack', id='<id>'),
        'collection': URL('listtracks'),
        'stream': URL('stream.stream', stream='<uuid>')
    })


class PlaylistSchema(BaseSchema):
    tracks = List(Nested('TrackSchema', only=('id', 'name', 'artist', 'links')))
    links = Hyperlinks({
        'self': URL('singleplaylist', id='<id>'),
        'collection': URL('listplaylists')
    })


class AlbumSchema(BaseSchema):
    artist = Nested('ArtistSchema', only=('id', 'name', 'links'))
    tracks = List(Nested('TrackSchema', only=('id', 'name', 'links')))
    links = Hyperlinks({
        'self': URL('singlealbum', id='<id>'),
        'collection': URL('listalbums')
    })
