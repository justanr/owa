import re
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


def gather_tags(dct, processor):
    data = process_from_dict(dct, look_for='tags', processor=processor, or_=[])
    return set(chain.from_iterable(data))


def gather_tracks(dct, track_builder):
    data = process_from_dict(dct, look_for='tracks',
                             processor=track_builder, or_=[])
    return [track for track in data if track]


def remove_duplicate_tags(artist, tags):
    if artist:
        return set(tags) - set(artist.tags)
    return set()


def combine_tags(artist, tags):
    tags = remove_duplicate_tags(artist, tags)
    artist.tags.extend(tags)
    return artist, tags


def reorder_tracklist(tracks, new_order):
    return [tracks[n] for n in new_order]


