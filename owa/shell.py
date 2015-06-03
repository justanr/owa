from .core import gather_tags, combine_tags, gather_tracks
from .models import Tag, Track, Playlist, db
from functools import partial


def apply_tags_to_artist(json, artist):
    tags = gather_tags(json, processor=partial(map, Tag.from_composite))

    if tags and artist:
        _, result = combine_tags(artist, tags)
        #      result, success
        return result, True
    else:
        if not artist:
            error = {'error': 'no artist found'}
        elif not tags:
            error = {'error': 'no tags found'}
        else:
            error = {'error': 'Internal error'}
        return error, False


def extend_tracklist(json, tracklist):
    tracks = gather_tracks(json, track_builder=partial(map, Track.query.get))

    if tracklist and tracks:
        tracklist.tracks.extend(tracks)
        return tracks, True
    else:
        if not tracklist:
            error = {'error': 'Tracklist not found'}
        elif not tracks:
            error = {'error': 'Tracks not found'}
        else:
            error = {'error': 'Internal error'}
        return error, False


def new_playlist(json):
    if not json or 'name' not in json:
        return {'error': 'json not submitted or malformed'}, False

    name = json['name']

    # sanity check
    free_name = Playlist.query.filter_by(name=name).first() is None

    if free_name:
        tracklist = Playlist(name=name)
        db.session.add(tracklist)

        if 'tracks' in json:
            extend_tracklist(json, tracklist)

        return tracklist, True
    else:
        return {'error': '{} already exists'.format(name)}, False
