# So we can use SQLite
import sqlite3

# Used for defining commands that can be run from the command-line
import click

# g is a special object that references the request itself and holds data pertaining to it
# current_app is a special object that points to the Flask instance that g came from
from flask import g, current_app

# with_appcontext is a decorator used when defining commands so that when run, it will run with the app in context
from flask.cli import with_appcontext

# Returns the connection instance of the database
def get_db():

    # If the connection instance is not already in the request, create it
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # Tells the connection how to return rows; in this case, you can access columns by their names
        g.db.row_factory = sqlite3.Row

    return g.db

# Destroys the database instance
def close_db(e=None):

    # First, remove the connection instance from the request
    db = g.pop('db', None)

    # Then make sure the connection is closed
    if db is not None:
        db.close()

# Initializes and sets up the database according to the scheme.sql file
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# Creates a command that can initialize the database
@click.command('init-db')
@with_appcontext
def init_db_command():

    # Description used in the help menu when running 'flask --help'
    """Clears and creates new database."""
    
    init_db()
    click.echo('Initialized the database.')

# Used to make sure the database is properly integrated with the application
def init_app(app):
    
    # Calls the close_db() function after returning a response
    app.teardown_appcontext(close_db)

    # Registers the command so it can be used in the command-line as 'flask init-db'
    app.cli.add_command(init_db_command)