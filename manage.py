#!/usr/bin/env python

from flask_script import Manager, Server, Option, prompt_bool
from flask_script.commands import Clean, ShowUrls
from flask_alembic import ManageMigrations, FlaskAlembicConfig
from alembic import command

from peopleflow import app
from peopleflow import models
from peopleflow.models import db


manager = Manager(app)
database = Manager(usage="Perform database operations")


class InitedServer(Server):
    def get_options(self):
        return super(InitedServer, self).get_options() + (
            Option('-e', dest='env', default='dev', help="run server for this environment [default 'dev']"),
        )

    def handle(self, *args, **kwargs):
        super(InitedServer, self).handle(*args, **kwargs)


class InitedMigrations(ManageMigrations):
    def run(self, args):
        super(InitedMigrations, self).run(args[1:])


@manager.shell
def _make_context():
    return dict(app=app, db=db, models=models)


@database.option('-e', '--env', default='dev', help="runtime environment [default 'dev']")
def drop(env):
    "Drops database tables"
    if prompt_bool("Are you sure you want to lose all your data?"):
        db.drop_all()

@database.option('-e', '--env', default='dev', help="runtime environment [default 'dev']")
def create(env):
    "Creates database tables from sqlalchemy models"
    db.create_all()
    config = FlaskAlembicConfig("alembic.ini")
    command.stamp(config, "head")

@database.option('-e', '--env', default='dev', help="runtime environment [default 'dev']")
def setversion(env):
    '''
    Manually set the alembic version of the
    database to the provided value.
    '''
    config = FlaskAlembicConfig("alembic.ini")
    version = raw_input("Enter the alembic version to be set:")
    command.stamp(config, version)


manager.add_command("db", database)
manager.add_command("runserver", InitedServer())
manager.add_command("clean", Clean())
manager.add_command("showurls", ShowUrls())
manager.add_command("migrate", InitedMigrations())


if __name__ == "__main__":
    manager.run()