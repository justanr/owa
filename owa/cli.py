from __future__ import print_function
import os
import sys
from time import time
from mutagenx import File
from sqlalchemy.exc import IntegrityError
from . import shell
from .models import db, Artist, Track, Album


valid_file_exts = ('m4a', 'flac', 'mp3', 'ogg', 'oga')


def filter_files(basedir, valid_exts=valid_file_exts):
    """Use os.walk to step through a directory structure and gathering
    files that have the appropriate extension and yields groups of
    file paths based on location.

    .. code-block:: python
        >>> found = find_files('~/Music/Gorguts/') # call with defaults
        >>> next(found)

        ['/home/.../Music/Gorguts/From Wisdom to Hate/01 Inverted.mp3',
         '/home/.../Music/Gorguts/From Wisdom to Hate/02 Behave Through Mythos.mp3',
         ...]

        >>> next(found)

        ['/home/.../Music/Gorguts/Obscura/01 Obscura.mp3',
         '/home/.../Music/Gorguts/Obscura/02 Earthly Love.mp3',
         ...]

    And so on.

    :param basedir: Absolute or relative path to directory to walk.
    :param valid_exts: Iterable of extensions to match against
    :yields [AbsolutePath]:
    """
    for current, _, files in os.walk(basedir):
        files = sorted(files)
        matched = [f for f in files if f.endswith(valid_exts)]
        full_paths = [os.path.join(current, f) for f in matched]

        if files:
            yield full_paths


def adaptor(track):
    """Adapts a Mutagen/MutagenX file object to a dictionary for easier
    handling. Extracts and manipulates specific information.
    """

    artist = track['artist'][0]

    if 'feat' in artist:
        artist = artist.split('feat')[0].strip()

    try:
        tags = track['genre']
    except KeyError:
        tags = []

    return dict(
        album=track['album'][0],
        length=int(track.info.length),
        location=track.filename,
        name=track['title'][0],
        artist=artist,
        tags=tags)


def shove_into_models(data):
    """Take a dictionary and convert it to models.
    """
    info = {k: v for k, v in data.items()}
    artist = Artist.find_or_create(db.session, name=info['artist'])
    album = Album.find_or_create(db.session, name=info.pop('album'),
                                 artist=artist)

    tags, success = shell.apply_tags_to_artist(info, artist)
    if not success:
        tags = []
    del info['tags']

    info['artist'] = artist
    track = Track(**info)

    db.session.add_all([artist, album, track])
    db.session.add_all(tags)
    return artist, album, track, tags


def store_directory(basedir, valid_exts=valid_file_exts, adaptor=adaptor):
    total_time = time()
    total_count = 0
    print('Begining walk of {}'.format(basedir))
    for group in filter_files(basedir, valid_exts):
        start = time()
        art, alb, trk, tags = [False] * 4
        for filepath in group:

            track = File(filepath, easy=True)

            try:
                info = adaptor(track)
            except KeyError as e:
                print('Error processing: {}'.format(track.filename),
                      'Error {0!s}: {1!s}'.format(e.__class__.__name__, e),
                      sep='\n', file=sys.stderr)
                continue

            if Track.query.filter_by(location=info['location']).first():
                print('{} previously processed, skipping'.format(info['name']))
                continue

            art, alb, trk, tags = shove_into_models(info)
            tag_str = ', '.join([t.name for t in tags])
            print(
                '* Processed: {0.name} - {1.name} - {2.name}'
                '\n    With Tags: {3}'.format(art, alb, trk, tag_str),
                sep='\n', file=sys.stdout)
        try:
            db.session.commit()
            total_count += len(group)
        except IntegrityError as e:
            db.session.rollback()
            print('***Error encountered: {!s}'.format(e),
                  '  Artist: {}'.format(art.name),
                  '  Album: {}'.format(alb.name),
                  '  Track: {}'.format(trk.name),
                  sep='\n', file=sys.stderr)
        else:
            if all([art, alb, trk]):
                end = int(time() - start)
                print('\n**Storing: {0.name} - {1.name}'
                      '\n  **Stored {2} files'
                      '\n  **Took {3} seconds'
                      '\n**Current Progress:'
                      '\n  Total Tracks: {4}'
                      '\n  Time: {5}\n'
                      ''.format(art, alb, len(group), end,
                                total_count, (time() - total_time)))
    print('Finished!')
