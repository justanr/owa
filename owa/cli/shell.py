'''
    owa.cli.shell
    `````````````
    Handles mapping IO interaction with CLI core functionality.
'''
from __future__ import print_function
import os
from functools import partial
from mutagenx import File
from sqlalchemy.exc import IntegrityError
from sys import stderr
from time import time
from .core import (filter_files, make_full_paths, shove_into,
                   adapt_track_to_dict, valid_file_exts)
from ..models import db, Artist, Track, Album
from ..utils.schema import _seconds_to_human


def shove_into_models(data):
    """Converts a track dictionary into fully formed models and adds them to
    the current session.
    """
    makers = {'artist': partial(Artist.find_or_create, db.session),
              'album': partial(Album.find_or_create, db.session),
              'track': Track}

    artist, album, track = shove_into(data, **makers)

    db.session.add_all([artist, album, track])
    return artist, album, track


def already_processed(filepath):
    """Boolean check to avoid needlessly reprocessing files.
    """
    return Track.query.filter_by(location=filepath).first() is not None


def store_directory(basedir, valid_exts=valid_file_exts,
                    adaptor=adapt_track_to_dict):
    running_time = time()
    running_count = 0
    print('Beginning walk of {}'.format(basedir))

    for current, _, files in os.walk(basedir):
        local_start = time()
        sorted_files = sorted(filter_files(files, valid_exts))
        filepaths = make_full_paths(current, sorted_files)

        for fp in filepaths:
            art, alb, trk = [None] * 3
            if already_processed(fp):
                print('{} previously processed, skipping'.format(fp))
                continue

            try:
                info = adaptor(File(fp, easy=True))
            # should be the extent of errors at this level
            except KeyError as e:
                print('Error processing file: {0}\n{1!r}\n'.format(fp, e),
                      file=stderr)
                continue
            else:
                art, alb, trk = shove_into_models(info)
                print('* Processed: {0.name} - {1.name} - {2.name}'
                      ''.format(art, alb, trk))

        if filepaths and all([art, alb, trk]):
            try:
                db.session.commit()
                running_count += len(filepaths)
            except IntegrityError as e:
                db.session.rollback()
                print('**Error Encountered: {0!r}\n'
                      '  Artist: {1.name}\n'
                      '  Album:  {2.name}\n'
                      '  Track:  {3.name}\n'
                      ''.format(e, art, alb, trk),
                      file=stderr)
            else:
                now = time()
                local_end = _seconds_to_human(int(now - local_start))
                global_time = _seconds_to_human(int(now - running_time))
                print('\n**Stored: {0.name} - {1.name}\n'
                      '  Files: {2}\n'
                      '  Time:  {3}\n'
                      '**Current Progress:\n'
                      '  Total Files: {4}\n'
                      '  Total Time:  {5}\n'
                      ''.format(art, alb, len(filepaths), local_end,
                                running_count, global_time))
        else:
            print('No tracks found in {}'.format(current))
