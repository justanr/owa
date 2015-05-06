import re
from functools import partial
from itertools import chain

_breaker_puncs = ('\\\\', '/', '&', ',', ' ', '\.', '_', '-')
TAG_BREAKER = re.compile('|'.join(_breaker_puncs))


def break_tag(tag):
    """Splits a composite tag (like "death metal") into individual tags
    (like "death" and "metal") based on arbitrary punctuation. The smaller
    tags are striped of white space and placed into a set.

    :param tag: A string representing a tag.
    """
    return set(t.strip() for t in re.split(TAG_BREAKER, tag.lower()) if t)


def process_from_dict(dct, look_for, processor, or_=()):
    """Accepts a potentially empty mapping and attempts to process a certain
    key.

    :param dct: Potentially empty mapping
    :param look_for: Key to extract from dictionary if present
    :param processor: Callback for processing contents of key
    :returns processed item from dictionary or None:
    """
    if dct and look_for in dct:
        return processor(dct[look_for])
    else:
        return or_


def process_tags(dct, processor):
    data = process_from_dict(dct, look_for='tags', processor=processor, or_=[])
    return set(chain.from_iterable(data))


def process_track_pos_pairs(dct, track_builder):
    data = process_from_dict(dct, look_for='tracks',
                             processor=partial(build_track_positions,
                                               track_builder=track_builder),
                             or_=[])
    return [(track, pos) for track, pos in data if track]


def build_track_positions(track_pos_pairs, track_builder):
    for pair in track_pos_pairs:
        if isinstance(pair, (list, tuple)):
            try:
                track, pos = pair
            except ValueError:  # bad unpack
                track, pos = pair, None
        else:
            track, pos = pair, None
        yield track_builder(track), pos


def remove_duplicate_tags(artist, tags):
    if artist:
        return set(tags) - set(artist.tags)
    else:
        return set()


def combine_tags(artist, tags, return_tags=True):
    if artist:
        tags = remove_duplicate_tags(artist, tags)
        artist.tags.extend(tags)
        return tags if return_tags else artist
    else:
        return None


def insert_tracks(tl, track_pos_pairs):
    for track, pos in track_pos_pairs:
        if pos is not None:
            tl.tracks.insert(pos, track)
        else:
            tl.tracks.append(track)
    return track_pos_pairs
