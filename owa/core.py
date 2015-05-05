import re
from operator import attrgetter
from pynads import List, Maybe
from pynads.utils.decorators import annotate

TAG_BREAKERS = re.compile('|'.join(('\\\\', '/', '&', ',', ' ',  '\\\.')))


@annotate(type="String -> [String]")
def break_tag(tag):
    """Splits a composite tag (like "death metal") into individual tags
    (like "death" and "metal") based on arbitrary punctuation. The smaller
    tags are striped of white space and placed into a set, which is transformed
    into a pynads.List

    :param tag: A string representing a tag.
    """
    return List(*set(t.strip() for t in re.split(TAG_BREAKERS, tag) if t))


@annotate(type="{k: v} -> a -> (v -> b) -> Maybe b")
def process_from_dict(dct, look_for, processor):
    """Accepts a potentially empty mapping and attempts to process a certain
    key monadically.

    :param dct: Potentially empty mapping
    :param look_for: Key to extract from dictionary if present
    :param processor: Callback for processing contents of key
    :returns Maybe a:
    """
    return (Maybe(dct, checker=bool)
            .bind(lambda d: Maybe(d.get(look_for)))
            .fmap(processor))


@annotate(type="{k: [v]} -> ([v] -> [Tag]) -> b -> Either [Tag] b")
def process_tags_from_dict(dct, processor, error):
    return (process_from_dict(dct, look_for='tags', processor=processor)
            .fmap(lambda tags: List.mconcat(*tags))
            .fmap(List.distinct)
            ).to_either(error)


@annotate(type="(Artist -> ([Tag] -> [Tag]) [Tag])")
def extend_artist_tags(artist):
    """Callback for extending and Artist's tags.
    """
    def extender(tags):
        artist.tags.extend(tags)
        return tags
    return extender


@annotate(type="(Artist -> ([Tag] -> [Tag]) -> [Tag]")
def remove_duplicate_tags(artist):
    """Callback for filter tags that exist on artist from a list of
    new tags.
    """
    def remover(new_tags):
        return List.difference(new_tags, artist.tags)
    return remover


@annotate(type="[Tag] -> [String]")
def extract_tag_names(tags):
    return List.fmap(tags, attrgetter('name'))


@annotate(type="Either Artist b -> Either [Tag] b -> Either Artist b")
def combine_tags(artist, tags):
    """Accepts an artist and a list of tag objects both wrapped in Either
    and combines the tags on the artist with the new tags, ensuring no
    duplicates existing.
    """
    # looks like Python and Lisp's bastard child
    # should I feel bad because I don't.

    return (artist
            .fmap(extend_artist_tags)
            .apply(artist
                   .fmap(remove_duplicate_tags)
                   .apply(tags)
                   )
            )
