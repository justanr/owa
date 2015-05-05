from os import path, environ


basedir = path.abspath(path.dirname(__file__))


class BaseConfig(object):
    SQLALCHEMY_RECORD_QUERIES = False


class DevConfig(BaseConfig):
    SQLALCHEMY_RECORD_QUERIES = True
    SQLALCHEMY_DATABASE_URI = environ.get('OWA_DEV_DB', 'sqlite:///owa_dev.db')

config = {'dev': DevConfig, 'default': DevConfig}
