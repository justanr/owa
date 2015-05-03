#!/usr/bin/env python

from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from owa import (
    # extensions
    db,

    # configuration
    config,

    # modules
    models,

    # helpers
    create_app,
)

app = create_app('owa', config=config.DevConfig, exts=[db])
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)


@manager.shell
def _shell_context():
    return dict(app=app, db=db, models=models)

if __name__ == '__main__':
    manager.run()
