from flask import Blueprint, send_file, abort
from .models import Track

Stream = Blueprint('stream', __name__, url_prefix='/stream')


@Stream.route('/<stream>')
def stream(stream):
    track = Track.query.filter(Track.uuid == stream).first()
    if not track:
        abort(404)

    return send_file(track.location)
