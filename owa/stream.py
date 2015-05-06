from flask import Blueprint, send_file, abort
from .models import Track

Stream = Blueprint('stream', __name__, url_prefix='/stream')


@Stream.route('/<stream_id>')
def stream(stream_id):
    track = Track.query.filter(Track.uuid == stream_id).first()
    if not track:
        abort(404)

    return send_file(track.location)
