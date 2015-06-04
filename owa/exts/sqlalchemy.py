"""
    owa.exts.sqlalchemy
    ```````````````````
    Monkey patching the Flask-SQLAlchemy extension
"""

import flask_sqlalchemy as fsqla
import sqlalchemy
import sqlalchemy.orm
from ..compat import wraps


def _set_default_query_class(d, cls=fsqla.BaseQuery):
    d.setdefault('query_class', cls)


def _wrap_with_default_query_class(fn, cls=fsqla.BaseQuery):
    @wraps(fn)
    def newfn(*args, **kwargs):
        _set_default_query_class(kwargs, cls)
        if 'backref' in kwargs:
            backref = kwargs['backref']
            if isinstance(backref, fsqla.string_types):
                backref = (backref, {})
            _set_default_query_class(backref[1], cls)
        return fn(*args, **kwargs)
    return newfn


def _include_sqlalchemy(obj, cls=fsqla.BaseQuery):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))

    # Note: obj.Table does not attempt to be a SQLAlchemy Table class.
    obj.Table = fsqla._make_table(obj)
    obj.relationship = _wrap_with_default_query_class(obj.relationship, cls)
    obj.relation = _wrap_with_default_query_class(obj.relation, cls)
    obj.dynamic_loader = _wrap_with_default_query_class(obj.relation, cls)
    obj.event = fsqla.event


class SQLAlchemy(fsqla.SQLAlchemy):
    def __init__(self, app=None, use_native_unicode=True, session_options=None,
                 metadata=None, model=fsqla.Model, query_cls=fsqla.BaseQuery):

        if session_options is None:
            session_options = {}

        session_options.setdefault('scopefunc', fsqla.connection_stack.__ident_func__)
        self.use_native_unicode = use_native_unicode
        self.session = self.create_scoped_session(session_options)
        self.Model = self.make_declarative_base(cls=model, metadata=metadata)
        self.Query = query_cls
        self._engine_lock = fsqla.Lock()
        self.app = app
        _include_sqlalchemy(self, query_cls)

        if app is not None:
            self.init_app(app)

    def make_declarative_base(self, cls, metadata=None):
        base = fsqla.declarative_base(cls=cls, name='Model', metadata=metadata,
                                      metaclass=fsqla._BoundDeclarativeMeta)
        base.query = fsqla._QueryProperty(self)
        return base
