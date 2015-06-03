from __future__ import print_function
import os
import sys
from time import time
from mutagenx import File
from sqlalchemy.exc import IntegrityError
from . import shell
from .models import db, Artist, Track, Album


valid_file_exts = ('m4a', 'flac', 'mp3', 'ogg', 'oga')


def filter_files(filenames, valid_exts=valid_file_exts):
    """Accepts an iterable of file names and returns ai sorted list of those
    names that have a valid file extension. Cheaper, faster and easier than
    mimetype matching. Plus, if it's *our* files and not user submitted content
    it's okay.

    :param files: Iterable of filenames
    :param valid_exts: Iterable of valid file extensions
    :returns: Sorted list valid files
    """
    return [f for f in sorted(filenames) if f.endswith(valid_exts)]


def make_full_paths(basedir, filenames):
    """Accepts a target directory and a list of filenames and uses os.path.join
    to create a full path.

    :param basedir string: Target directory path
    :param filenames: Iterable of filenames
    """
    return [os.path.join(basedir, fn) for fn in filenames]


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

    if track not in album.tracks:
        album.tracks.append(track)

    db.session.add_all([artist, album, track])
    db.session.add_all(tags)
    return artist, album, track, tags


def store_directory(basedir, valid_exts=valid_file_exts, adaptor=adaptor):
    total_time = time()
    total_count = 0
    print('Begining walk of {}'.format(basedir))

    for current, _, files in os.walk(basedir):
        # start time for this group
        start = time()
        filepaths = make_full_paths(current, filter_files(files))

        # initialize these to false
        # XXX: Why?
        art, alb, trk, tags = False, False, False, []
        track, info = False, False
        for filepath in filepaths:

            track = File(filepath, easy=True)

            try:
                info = adaptor(track)
            # this *should* be the extent of the errors at this level.
            except KeyError as e:
                print('Error processing: {0}\n'
                      'Error {1!s}: {2!s}\n'
                      ''.format(track.filename, e.__class__.__name__, e),
                      file=sys.stderr)
                continue

            # TODO: A better way? This is faster than actually constructing
            # each object, but still.
            already_processed = Track.query.filter_by(location=info['location']).count()  # noqa

            if already_processed:
                print('{} previously processed, skipping'.format(info['location']))  # noqa
                continue

            art, alb, trk, tags = shove_into_models(info)
            tag_str = ', '.join([t.name for t in tags])
            print(
                '* Processed: {0.name} - {1.name} - {2.name}\n'
                '  Found Tags: {3}'.format(art, alb, trk, tag_str),
                file=sys.stdout)
        try:
            db.session.commit()
            total_count += len(filepaths)
        except IntegrityError as e:
            db.session.rollback()
            print('**Error encountered: {!s}'.format(e),
                  '  Artist: {}'.format(art.name),
                  '  Album:  {}'.format(alb.name),
                  '  Track:  {}'.format(trk.name),
                  sep='\n', file=sys.stderr)
        else:
            # TODO: We got this far, why do we need to check now?
            if all([art, alb, trk]):
                end = int(time() - start)
                print('\n** Storing: {0.name} - {1.name}'
                      '\n     Files: {2}'
                      '\n     Time:  {3}'
                      '\n** Current Progress:'
                      '\n     Total Files: {4}'
                      '\n     Total Time:  {5}\n'
                      ''.format(art, alb, len(filepaths), end,
                                total_count, (time() - total_time)))
        finally:
            # clean up so we don't leave dangling objects around.
            del art, alb, trk, tags, track, info
            art, alb, trk, tags, track, info = False, False, False, False, False, []  # noqa
    print('Finished!')
