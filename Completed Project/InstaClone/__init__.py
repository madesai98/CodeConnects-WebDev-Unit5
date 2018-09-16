# Import os so we can manipulate the filesystem
import os

# Import the main Flask instance from the flask package
from flask import Flask

# Create Flask instance through function to avoid scaling issues
def create_app(test_config=None):

    # Make app variable the Flask instance
    # instance_relative_config makes configuration relative to the InstaClone folder instead of the project root
    app = Flask(__name__, instance_relative_config=True)

    # Sets default configuration information about the application
    # Secret key is used by Flask and extensions for keeping data safe; change to random value for production settings
    # Database is the path to the SQLite file for the database
    # Upload folder is where we will upload the images that users post
    # Allowed extensions is what file extensions are able to be uploaded
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'InstaClone.sqlite'),
        UPLOAD_FOLDER='./uploads',
        ALLOWED_EXTENSIONS=set(['png', 'jpg', 'jpeg'])
    )

    # Checks if a parameter was passed into the create_app() function when called
    # If it was, add those config values to the config mapping (DEVELOPMENT ENVIRONMENT)
    # If it wasn't, load the config values from the config.py file (PRODUCTION ENVIRONMENT)
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Create the instance folder because the SQLite file will be created there
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Hooks the db.py code into the main application
    from . import db
    db.init_app(app)

    # Hooks the auth.py code into the main application
    from . import auth
    app.register_blueprint(auth.bp)

     # Hooks the auth.py code into the main application
    from . import posts
    app.register_blueprint(posts.bp)

    # Since / is defined in the posts blueprint, it would
    # be referenced as posts.index, however, we want it to
    # be referenced just as index, so this line overrides that
    app.add_url_rule('/', endpoint='index')

    return app
