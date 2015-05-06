from .core import (process_tags, combine_tags,
                   process_track_pos_pairs, insert_tracks)
from .models import Artist, Tag, Track, Tracklist, db
from functools import partial


def apply_tags_to_artist(request, id):
    artist = Artist.query.get(id)
    tags = process_tags(request.get_json(),
                        processor=partial(map, Tag.from_composite))

    if tags and artist:
        result = combine_tags(artist, tags)
        db.session.commit()
        #      result, success
        return result, True
    else:
        db.session.rollback()
        if not artist:
            error = {'error': 'no artist found'}
        elif not tags:
            error = {'error': 'no tags found'}
        else:
            error = {'error': 'Internal error'}
        return error, False


def extend_tracklist(request, id):
    tracklist = Tracklist.query.get(id)
    tracks = process_track_pos_pairs(request.get_json(),
                                     track_builder=Track.query.get)

    if tracklist and tracks:
        db.session.commit()
        return [track for track, _ in insert_tracks(tracklist, tracks)], True
    else:
        db.session.rollback()
        if not tracklist:
            error = {'error': 'Tracklist not found'}
        elif not tracks:
            error = {'error': 'Tracks not found'}
        else:
            error = {'error': 'Internal error'}
        return error, False


def new_tracklist(request):
    json = request.get_json()
    if not json or 'name' not in json:
        return {'error': 'json not submitted or malformed'}, False

    name = json['name']

    # sanity check
    free_name = Tracklist.query.filter_by(name=name).first() is None

    if free_name:
        tracklist = Tracklist(name=name)

        if 'tracks' in json:
            tracks = process_track_pos_pairs(json,
                                             track_builder=Track.query.get)
            insert_tracks(tracklist, tracks)
        db.session.commit()
        return tracklist, True
    else:
        return {'error': '{} already exists'.format(name)}, False
