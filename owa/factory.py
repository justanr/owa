"""
    openwebamp.factory
    ~~~~~~~~~~~~~~~~~~
    Factory module for OpenWebAmp instances
"""
from flask import Flask


def create_app(import_name, config=None, bps=None, exts=None,
               maker=Flask, **options):
    """Factory function for creating Flask or Flask-like objects.

    :param import_name: The same as the first parameter to the Flask class,
    see its documentation for more details about it.
    :param config: Configuration object for the instance created
    :param bps: Iterable of Blueprints to register on the appliation
    :param exts: Iterable of Extensions to initialize with the application
    :param maker: Callable that recieves the import_name and options kwargs
    and returns a Flask or Flask-like object, defaults to flask.Flask
    :param options: Keyword arguments to pass directly to the instance maker
    """

    application = maker(import_name, **options)

    if config:
        application.config.from_object(config)

    if bps:
        for bp in bps:
            application.register(bp)

    if exts:
        for ext in exts:
            ext.init_app(application)

    return application
