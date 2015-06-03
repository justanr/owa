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
)

from owa.api import api
from owa.stream import Stream
from owa.commands import store_directory
from owa.utils import create_app

import pynads

app = create_app('owa',
                 config=config.DevConfig,
                 exts=[db, api],
                 bps=[Stream])
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
