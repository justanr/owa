from flask.ext.marshmallow import Marshmallow
from .utils import Length


ma = Marshmallow()
common = ('id', 'name')


class BaseSchema(ma.Schema):
    class Meta:
        additional = common
