"""
    openwebamp.models
    ~~~~~~~~~~~~~~~~~
    SQLAlchemy models for openwebamp

    The main models are:
    - Artist
    - Tag
    - Track
    - Tracklist

    Helper Models:
    - ArtistTag
    - TrackPosition
"""
from uuid import uuid4
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from .utils import ReprMixin, UniqueMixin

db = SQLAlchemy()


class Artist(db.Model, ReprMixin, UniqueMixin):
    __tablename__ = 'artists'
    repr_fields = ('name',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64), unique=True)
    tags = association_proxy('_tags', 'tag', creator=lambda t:
                             ArtistTag(tag=Tag(name=t)))

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return name

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)


class Tag(db.Model, ReprMixin, UniqueMixin):
    __tablename__ = 'tags'
    repr_fields = ('name',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(16), unique=True)
    artists = association_proxy('_artists', 'artist')

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return name

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)


class Track(db.Model, ReprMixin):
    __tablename__ = 'tracks'
    repr_fields = ('name', 'artist')

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist')
    length = db.Column(db.Integer)
    location = db.Column(db.UnicodeText, unique=True)
    name = db.Column(db.UnicodeText)
    _tracklists = db.relationship('TrackPosition', backref='track')
    tracklists = association_proxy('_tracklists', 'tracklist')
    uuid = db.Column(db.String(36), unique=True, default=uuid4().__str__)


class Tracklist(db.Model, ReprMixin):
    __tablename__ = 'tracklists'
    repr_fields = ('name',)

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(128))
    _tracks = db.relationship('TrackPosition', backref='tracklist',
                              order_by='TrackPosition.position',
                              collection_class=ordering_list('position'))
    tracks = association_proxy('_tracks', 'track',
                               creator=lambda track: TrackPosition(track=track))

    def __init__(self, name, tracks=None):
        self.name = name

        if tracks:
            self.tracks.extend(tracks)

    @hybrid_property
    def length(self):
        return sum(t.length for t in self.tracks)

    @hybrid_property
    def total_tracks(self):
        return len(self.tracks)


class ArtistTag(db.Model, ReprMixin):
    __tablename__ = 'artisttags'
    repr_fields = ('tag', 'artist')

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist', backref='_tags')
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship('Tag', backref='_artists')


class TrackPosition(db.Model, ReprMixin):
    __tablename__ = 'trackpositions'
    repr_fields = ('tracklist', 'track', 'position')

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'))
    tracklist_id = db.Column(db.Integer, db.ForeignKey('tracklists.id'))

    __table_args__ = (
        # ensure a track only appears once in a given location on a given list
        db.UniqueConstraint('position', 'track_id', 'tracklist_id'),
        # ensure a track can't appear in an invalid position on a given list
        db.CheckConstraint('position > -1')
    )
