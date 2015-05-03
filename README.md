#OpenWebAmp 2: Electric Boogaloo

So, OpenWebAmp got a little wild for me. Instead of trying to fix all the 
mistakes in it, I'm going to through the first one away and start from scratch.
Something about how the first one is always garbage anyways and throw one away.

Iunno. I made bad choices, the project gained debt that wasn't unmanagable
but made it incredibly unfun to hack on in my limited free time. May as well
try again with hindsight.

##Major Changes

* No user system. I always envisioned OWA being more of a WinAmp or RhythmBox
style app that happens to provide a web frontend than something as massive as
like Spotify. Keeping in tune with that, the half-realized user system is gone.
Good riddens. This actually simplifies a lot of things, like whatever
`MemberTaggedArtist` grew into (a many-to-many-to-many relationship from hell).
* Smarter use of Flask-Restful and Marshmallow.
* Soon: Actually posting things to the application! My god, what a miracle.

## The Song Remains the Same

* Still uses Flask. You'll pry it from my cold, dead fingers. Django, Pyramid,
et. al. are cool and all but the simplicity and extensiblity Flask offers is
just too alluring.
* Still planning on using Ngnix as my main server. Sorry Apache folks. ):
* There's still better options for music streaming as well. This is meant
to be a toy project kept on a RasPi for use at parties and what not.
