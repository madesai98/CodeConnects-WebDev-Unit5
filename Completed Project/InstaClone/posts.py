# Each component will be explained as it's used
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory
)

# Items created in this project
from InstaClone.auth import login_required
from InstaClone.db import get_db

# Will use for file names
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

# Use for saving file on the server
import os

# Creates a Blueprint named post
# Routes /, /upload, /user/<username> will be defined here
bp = Blueprint('posts', __name__)

# Creates the / route which will simply handle a GET request
@bp.route('/')
@login_required
def index():
    db = get_db()
    users = db.execute('SELECT id, username FROM user').fetchall()
    return render_template('posts/index.html', users=users)

# Creates the /upload route which will have two distinct methods within it: GET and POST
@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':

        # Get required form data
        caption = request.form['caption']
        img = request.files['img']

        error = None

        # Error checking
        if not caption:
            error = 'A caption is required.'

        if not img:
            error = 'An image is required.'

        if img and not allowed_file(img.filename):
            error = 'Only JPG and PNG are accepted.'

        if error is not None:
            flash(error)
        else:
            # Generate a random filename based on the user's ID and the current time
            # This makes it almost impossible for the same name to be generated twice
            filename = secure_filename(generate_password_hash('%s %s' % (g.user['id'], datetime.now())))

            # Save the image on the server's storage at the designated path in the config
            img.save(os.path.join(os.path.dirname(os.path.realpath(__file__)), current_app.config['UPLOAD_FOLDER'], filename))

            # Insert the proper values into the database
            db = get_db()
            db.execute(
                'INSERT INTO post (author_id, img_path, caption)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], filename, caption)
            )
            db.commit()
            return redirect(url_for('index'))

    return render_template('posts/upload.html')

# Creates the /user/<username> route which will present a user's profile based on <username>
@bp.route('/user/<username>')
@login_required
def user(username):
    db = get_db()
    posts = db.execute(
        'SELECT p.id, img_path, caption, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id WHERE u.username = ?'
        ' ORDER BY created DESC',
        (username,)
    ).fetchall()
    print(posts)
    return render_template('posts/user.html', posts=posts, username=username)

# Short function to determine if a file has the correct file extension for uploading
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

# Make a route to access uploaded files
@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(os.path.dirname(os.path.realpath(__file__)), current_app.config['UPLOAD_FOLDER']), filename)