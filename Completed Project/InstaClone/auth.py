# Useful high-level functions and tools
import functools

# Each component will be explained as it's used
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

# Password hashing functions
from werkzeug.security import check_password_hash, generate_password_hash

# The database file made in this project
from InstaClone.db import get_db

# Creates a Blueprint named auth under the parent route /auth
# Routes /login, /logout, and /register will be put in here for organizational purposes
# Since there is a url_prefix, these routes will be accessed using /auth/login, /auth/logout, and /auth/register
bp = Blueprint('auth', __name__, url_prefix='/auth')

# Creates the /login route which will have two distinct methods within it: GET and POST
@bp.route('/login', methods=('GET', 'POST'))
def login():

    # The POST method is a request to the /register route from a form post (user sends data)
    if request.method == 'POST':

        # The values the user submitted through the form
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        # Tries to get the user from the database with the given username
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        # Check for errors
        if user is None:
            error = 'That user does not exist'
        elif not check_password_hash(user['password'], password):
            error = 'Your password is incorrect'

        # If there are no errors, log the user in using a session and redirect to the homepage
        # Sessions locally store authentication data for a temporary amount of time
        if error is None:

            # Clear any previous session data just in-case
            session.clear()

            # Set a session variable called user_id and set it to the user's id retrieved from the database, then redirect to the homepage
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        # If there was an error, show the error message on the current page
        # flash() stores the message so it can be displayed however you want from the HTML file
        flash(error)

    # Renders the register.html file to the page when it is a GET request (user receives data)
    return render_template('auth/login.html')

# Creates the /logout route which will simply clear the session and redirect to the homepage
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# Creates the /register route which will have two distinct methods within it: GET and POST
@bp.route('/register', methods=('GET', 'POST'))
def register():

    # The POST method is a request to the /register route from a form post (user sends data)
    if request.method == 'POST':

        # The values the user submitted through the form
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        conf_password = request.form['conf_password']

        db = get_db()
        error = None

        # Check for errors
        if (not username) or (not email) or (not password) or (not conf_password):
            error = 'All fields are required'
        elif db.execute(
            'SELECT id FROM user WHERE username = ?', (username,)
        ).fetchone() is not None:
            error = 'The username \'{}\' is already in use'.format(username)
        elif db.execute(
            'SELECT id FROM user WHERE email = ?', (email,)
        ).fetchone() is not None:
            error = 'The email \'{}\' is already in use'.format(username)
        elif password != conf_password:
            error = 'Your passwords do not match'

        # If there are no errors, insert the user into the database and redirect to the login page
        if error is None:
            db.execute(
                'INSERT INTO user (username, email, password) VALUES (?, ?, ?)',
                (username, email, generate_password_hash(password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        # If there was an error, show the error message on the current page
        # flash() stores the message so it can be displayed however you want from the HTML file
        flash(error)

    # Renders the register.html file to the page when it is a GET request (user receives data)
    return render_template('auth/register.html')

# Decorator makes the following function be called before any view is loaded
# Sets a global variable with the user's information if they are logged in
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

# Makes a view into one that requires the user to be logged in
# This will be used as a decorator when defining routes
def login_required(view):

    # This decorator returns a new view function that wraps the original view it’s applied to
    # The new function checks if a user is loaded and redirects to the login page otherwise 
    # If a user is loaded the original view is called and continues normally
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view