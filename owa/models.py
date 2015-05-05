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
from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery
from uuid import uuid4
from pynads import List, Right, Left
from pynads.utils.decorators import annotate
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from .utils import ReprMixin, UniqueMixin
from .core import break_tag


db = SQLAlchemy()


# Really wish Flask-SQLA made it easier to replace the BaseQuery class.
class SafeQuery(BaseQuery):
    """Handles querying the database safely using pynads.Either
    """
    @annotate(type='Int -> b -> Either Model b')
    def either(self, id, error):
        model = self.get(id)
        return Right(model) if model else Left(error)

    @annotate(type='forall a. {String: a} -> Either Model String')
    def get_one_by(self, **filters):
        try:
            return Right(self.filter_by(**filters).one())
        except NoResultFound:
            return Left('not found with {!s}'.format(filters))
        except MultipleResultsFound:
            return Left('multiple results found with {!s}'.format(filters))


class BaseModel(ReprMixin):
    query_class = SafeQuery

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    id = db.Column(db.Integer, primary_key=True)


class Artist(BaseModel, db.Model, UniqueMixin):
    repr_fields = ('name',)

    name = db.Column(db.Unicode(64), unique=True)
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


class Tag(BaseModel, db.Model, UniqueMixin):
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
    @annotate(type='String -> [Tag]')
    def from_composite(cls, composite_tag):
        """Accepts a composite tag like 'death metal' and returns a list
        of Tag objects that are either pulled from the database or created
        as needed.
        """
        broken = break_tag(composite_tag)
        existing = List(*cls.query.filter(cls.name.in_(broken)).all())
        new = broken.difference(existing.fmap(lambda t: t.name)).fmap(
            lambda t: cls.find_or_create(session=db.session, name=t))
        return existing.extend(new)


class Track(BaseModel, db.Model):
    repr_fields = ('name', 'artist')

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist')
    length = db.Column(db.Integer)
    location = db.Column(db.UnicodeText, unique=True)
    name = db.Column(db.UnicodeText)
    _tracklists = db.relationship('TrackPosition', backref='track')
    tracklists = association_proxy('_tracklists', 'tracklist')
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))


class Tracklist(BaseModel, db.Model):
    repr_fields = ('name',)

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


class ArtistTag(BaseModel, db.Model):
    repr_fields = ('tag', 'artist')

    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    artist = db.relationship('Artist', backref='_tags')
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'))
    tag = db.relationship('Tag',
                          backref=db.backref('_artists', lazy='dynamic'))


class TrackPosition(BaseModel, db.Model):
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
