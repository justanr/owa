#OpenWebAmp 2: Electric Boogaloo
So, OpenWebAmp got a little wild for me. Instead of trying to fix all the 
mistakes in it, I'm going to through the first one away and start from scratch.
Something about how the first one is always garbage anyways and throw one away.

Iunno. I made bad choices, the project gained debt that wasn't unmanagable
but made it incredibly unfun to hack on in my limited free time. May as well
try again with hindsight.

##Endpoints
OWA has several endpoints:

* `/album/` A paginated list of all albums in the database
* `/album/` Returns a single album including artist, name, id, tracks, and
links
* `/`, `/artist/`: A paginated list of all artists in the database
* `/artist/<int:id>`:
    * **GET**: Returns a single artist, including name, id, links,
    tags, and albums attached to the artist
    * **POST**: Allows applying tags to an artist and returns the tags applied,
    any tags not currently found in the database are created.
* `/playlist/`:
    * **GET**: A paginated list of all user created playlists
    * **POST**: Allows creation of a new playlist, potentially with tracks
* `/playlist/<int:id>/`:
    * **GET**: Returns information about a single user created playlist
    including tracks in order, id, links
    * **POST**: Allows adding tracks to a user created playlist
* `/stream/<stream_id>/` Allows streaming a track by providing its UUID
* `/tag/`: Paginated list of all tags in database
* `/tag/<tagname>/`: List of artists attached to this tag
* `/track/`: Paginated list of all tracks in database
* `/track/<int:id>/`: Reports information on a specific track, including:
its name, id, artist, which playlists and albums it appears on


##Adding Data
###Adding Tags to Artist

`POST /artist/<int:id>/` looks for the `tags` key in the JSON request,
which should be a list of tags to apply to an artist. OWA makes the choice
to explode composite tags into smaller ones. So something like "death metal"
actually becomes two tags: "death" and "metal". It'll also lowercase tags as
well, so "METAL" and "metal" and "Metal" all refer to the same tag.

Let's tag the first artist in the database with rock.

``bash
curl localhost/artist/1/ \
-H 'Accept: application/json' \
-H 'Content-Type: application/json' \
-X POST --data '{"tags": ["rock"]}'
``

And you should get back something like this:

```
{
    tags: [
        {
            "id": 149,
            "links": {
                "self": "localhost/tag/rock/",
                "collection": "localhost/tag/"
                }
            "name": "rock"
        }
    ]
}
```

If the artist had already been tagged with rock, tags will be empty, signifying
no new tags were applied. There's also two errors this end point will produce:

* `{"error": "no artist found"}` meaning we tried tagging an artist that doesn't
exist.
* `{"error": "no tags found"}` meaning the endpoint didn't find "tags" in the
top level object.

Currently, they both report `200 OK` when really it should be `400 BAD REQUEST`.

###Creating a new Playlist

`POST /playlist/` looks for a `name` key in the JSON request and optionally a
`tracks` key. `name` signifies the name of the new playlist, which must be
unique in the application and `tracks` is either:

* `track_id` and `position` pairs, signifying which tracks and where to put them
* just `track_id` which simply means "Add this track to the end of the list"

The request is simple:

####Just a new playlist
```bash
curl localhost/playlist/ \
-H 'Accept: application/json' -H 'Content-Type: application/json' -X POST \
--data '{"name": "My First Playlist"}'
```

And you'll either get back the playlist object or an error saying the playlist
exists already.

####New Playlist with Tracks
```bash
curl ... \
--data '{"name": "Awesome Playlist", "tracks": [1,2,3]}'
```

Again, either the playlist object or an error. The tracks value could have also
been specified as a list of lists: `[[1, 0], [2, 0], [3, 0]]` to build the
playlist backwards. Or a combination of the two.

###Adding to an existing Playlist
`POST /playlist/<int:id>/` only looks for a `tracks` key in the JSON. And
returns either the tracks that were added to the playlist or an error
message if the tracklist wasn't found.


###CLI
Aside from posting data to few endpoints that accept them, OWA features a
directory crawler that will look for files that end in certain extensions
(quicker than mimetype checking, plus its our own files, not user submitted)
open them up, yank out information and shove it into the database.

Navigate to where you've cloned OWA and run:

```bash
./manager.py addfiles -d /abs/path/to/music
```

And watch the processing fly by on your screen. Seriously, it handles
about 21000 tracks in around five minutes on my laptop.


##Major Changes
* No user system. I always envisioned OWA being more of a WinAmp or RhythmBox
style app that happens to provide a web frontend than something as massive as
like Spotify. Keeping in tune with that, the half-realized user system is gone.
Good riddens. This actually simplifies a lot of things, like whatever
`MemberTaggedArtist` grew into (a many-to-many-to-many relationship from hell).
* Smarter use of Flask-Restful and Marshmallow.

## The Song Remains the Same
* Still uses Flask. You'll pry it from my cold, dead fingers. Django, Pyramid,
et. al. are cool and all but the simplicity and extensiblity Flask offers is
just too alluring.
* Still planning on using Ngnix as my main server. Sorry Apache folks. ):
* There's still better options for music streaming as well. This is meant
to be a toy project kept on a RasPi for use at parties and what not.
