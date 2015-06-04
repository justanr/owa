from flask.ext.restful import Api
from ..utils.resource import register_all_resources, SingleResource, ListResource
from . import artist, tag, track, playlist, album

api = Api()


for module in (artist, tag, track, playlist, album):
    register_all_resources(module, api)
