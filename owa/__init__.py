from . import config
from .factory import create_app
from .models import db

def after_request(resp):
    db.session.commit()
    db.session.remove()
    return resp
