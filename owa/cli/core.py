'''
    owa.cli.core
    ````````````
    Core functionality for the OWA cli submodule. Handles things like filtering
    files, adapting track objects to dictionaries, etc.
'''

from os import path

valid_file_exts = ('m4a', 'flac', 'mp3', 'ogg', 'oga')


def filter_files(filenames, valid_exts=valid_file_exts):
    """Filter files base on file extensions
    """
    return [f for f in filenames if f.endswith(valid_exts)]


def make_full_paths(basedir, filenames):
    """Returns a full qualified path for a collection of filenames
    """
    return [path.join(basedir, f) for f in filenames]


def adapt_track_to_dict(track):
    """Designed to adapt a MutagenX file object to a dictionary for easier
    handling. Extracts and potentially manipulates:
        * artist name, stripping featured artists (sorry folks)
        * album name
        * track name, length, file location
        * genre tags attached to the track (or an empty list if not present)
    """

    artist = track['artist'][0]

    if 'feat' in artist:
        artist = artist.split('feat')[0].strip()

    tags = track.get('genre', [])

    return {'album': track['album'][0],
            'length': int(track.info.length),
            'location': track.filename,
            'name': track['title'][0],
            'artist': artist,
            'tags': tags}


def shove_into(data, **makers):
    """Converts a dictionary into their respective object forms
    """
    missing = {'artist', 'album', 'track'} - set(makers)

    if missing:
        raise KeyError('Makers for {} missing'
                       ''.format(', '.join([m for m in missing])))

    # unpack to make actual calls more pleasant looking
    Artist, Album, Track = makers['artist'], makers['album'], makers['track']

    # don't modify passed data
    info = data.copy()

    artist = info['artist'] = Artist(name=info['artist'])
    album = Album(name=info.pop('album'), artist=artist)

    if 'tags' in data:
        artist.apply_tags(info.pop('tags'))

    track = Track(**info)
    album.tracks.append(track)

    return artist, album, track
