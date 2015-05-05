from flask.ext.restful import Api
from ..resource import register_all_resources
from . import artist, tag, track, tracklist

api = Api()


for module in (artist, tag, track, tracklist):
    register_all_resources(module, api)
