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
from itertools import chain
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from uuid import uuid4
from .core import break_tag
from .exts import SQLAlchemy
from .utils.model import BaseModel, UniqueMixin

db = SQLAlchemy(model=BaseModel)


class Artist(db.Model, UniqueMixin):
    repr_fields = ('name',)

    name = db.Column(db.UnicodeText, unique=True)
    tags = association_proxy('_tags', 'tag',
                             creator=lambda tag: ArtistTag(tag=tag))

    def __init__(self, name, tags=None):
        self.name = name
        if tags:
            self.tags.extend(tags)

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return hash(name)

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)

    def apply_tags(self, tags):
        tags = chain.from_iterable([Tag.from_composite(tag) for tag in tags])
        self.tags.extend(set(tags) - set(self.tags))


class Tag(db.Model, UniqueMixin):
    repr_fields = ('name',)

    name = db.Column(db.Unicode(16), unique=True)
    artists = association_proxy('_artists', 'artist',
                                creator=lambda artist: ArtistTag(artist=artist))

    def __init__(self, name, artists=None):
        self.name = name
        if artists:
            self.artists.extend(artists)

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return hash(name)

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)

    @classmethod
    def from_composite(cls, composite_tag):
        """Accepts a composite tag like 'death metal' and returns a list
        of Tag objects that are either pulled from the database or created
        as needed.
        """
        broken = break_tag(composite_tag)
        existing = cls.query.filter(cls.name.in_(broken)).all()
        new = [cls(name=t) for t in broken - {t.name for t in existing}]
        return existing + new


class Track(db.Model):
    repr_fields = ('name', 'artist')

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist')
    length = db.Column(db.Integer)
    location = db.Column(db.UnicodeText, unique=True)
    name = db.Column(db.UnicodeText)
    _tracklists = db.relationship('TrackPosition', backref='track')
    tracklists = association_proxy('_tracklists', 'tracklist')
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))

    def __init__(self, name, artist, length, location):
        self.name = name
        self.artist = artist
        self.length = length
        self.location = location


class Tracklist(db.Model):
    repr_fields = ('name',)

    type = db.Column(db.String(16))
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

    __mapper_args__ = {
        'polymorphic_on': type,
        'with_polymorphic': '*'
    }


class Album(Tracklist, UniqueMixin):
    """System defined tracklist
    """
    repr_fields = ('name', 'artist')

    id = db.Column(db.Integer, db.ForeignKey('tracklists.id'), primary_key=True)
    name = db.Column(db.Unicode(128))
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist', backref='albums')

    def __init__(self, artist, **kwargs):
        self.artist = artist
        super(Album, self).__init__(**kwargs)

    @classmethod
    def unique_hash(cls, name, artist, **kwargs):
        return hash((name, artist.name))

    @classmethod
    def unique_func(cls, query, name, artist, **kwargs):
        return query.filter(cls.name == name, cls.artist_id == artist.id)

    __table_args__ = (
        db.Constraint('name', 'artist_id'),
    )

    __mapper_args__ = {
        'polymorphic_identity': 'album',
        'inherit_condition': (id == Tracklist.id)
    }


class Playlist(Tracklist, UniqueMixin):
    """User defined tracklist
    """
    id = db.Column(db.Integer, db.ForeignKey('tracklists.id'), primary_key=True)
    name = db.Column(db.Unicode(128), unique=True)

    def __init__(self, **kwargs):
        super(Playlist, self).__init__(**kwargs)

    @classmethod
    def unique_hash(cls, name, **kwargs):
        return hash(name)

    @classmethod
    def unique_func(cls, query, name, **kwargs):
        return query.filter(cls.name == name)

    __mapper_args__ = {
        'polymorphic_identity': 'playlist',
        'inherit_condition': (id == Tracklist.id)
    }


class ArtistTag(db.Model):
    repr_fields = ('tag', 'artist')

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist', backref='_tags')
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship('Tag',
                          backref=db.backref('_artists', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('artist_id', 'tag_id'),
    )


class TrackPosition(db.Model):
    repr_fields = ('tracklist', 'track', 'position')

    position = db.Column(db.Integer)
    track_id = db.Column(db.Integer, db.ForeignKey('tracks.id'))
    tracklist_id = db.Column(db.Integer, db.ForeignKey('tracklists.id'))

    __table_args__ = (
        # ensure a track only appears once in a given location on a given list
        db.UniqueConstraint('position', 'track_id', 'tracklist_id'),
        # ensure a track can't appear in an invalid position on a given list
        db.CheckConstraint('position > -1')
    )
