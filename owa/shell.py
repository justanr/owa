from functools import partial
from operator import attrgetter
from pynads import Right
from pynads.utils.decorators import annotate
from .core import process_tags_from_dict, combine_tags
from .models import Artist, Tag, ArtistTag, db


@annotate(type='Request -> Int -> Either Artist String')
def apply_tags_to_artist(request, id):
    artist = Artist.query.get_one_by(id=id)
    tags = process_tags_from_dict(request.get_json(),
                                  processor=partial(map, Tag.from_composite),
                                  error={'error': 'no tags found'})

    result = combine_tags(artist, tags)

    if result:
        db.session.commit()
    else:
        # purge potentially half-constructed tags
        db.session.rollback()
    return result


def get_paginated(model, page, limit, order_by=None):
    if order_by and hasattr(model, order_by):
        order_by = getattr(model, order_by)
    else:
        order_by = model.name
    q = model.query.order_by(order_by).paginate(page, limit, False)
    return Right(q.items)


@annotate(type='String -> Int -> Int -> [Artist]')
def get_artists_by_tag(name, page, limit):
    return (Tag.query.get_one_by(name=name)
            .fmap(attrgetter('_artists'))
            .fmap(lambda q: q.join(Artist, Artist.id == ArtistTag.artist_id))
            .fmap(lambda q: q.with_entities(Artist))
            .fmap(lambda q: q.paginate(page, limit, False))
            .fmap(attrgetter('items')))
