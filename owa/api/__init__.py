from flask.ext.restful import Api
from ..resource import register_all_resources
from . import artist, tag

api = Api()

register_all_resources(artist, api)
register_all_resources(tag, api)
