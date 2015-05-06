#!/usr/bin/env python

import sys
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from owa import (
    # extensions
    db,

    # configuration
    config,

    # modules
    schemas, models, utils, core, shell,

    # helpers
    create_app, after_request
)

from owa.api import api
from owa.stream import Stream
from owa.cli import store_directory

import pynads

app = create_app('owa',
                 config=config.DevConfig,
                 exts=[db, api],
                 bps=[Stream],
                 after=after_request)
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.option('-d', '--d', dest='basedir')
def addfiles(basedir):
    try:
        store_directory(basedir)
    except (KeyboardInterrupt, EOFError):
        db.session.rollback()
        sys.exit(1)
    else:
        sys.exit(0)


@manager.shell
def _shell_context():
    return dict(app=app, db=db, models=models,
                utils=utils, core=core, pynads=pynads,
                schemas=schemas, shell=shell, api=api)

if __name__ == '__main__':
    manager.run()
