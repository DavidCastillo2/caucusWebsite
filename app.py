###########################################################################################################################################
#                                                                                                                                         #
#                                                           App Setup                                                                     #
#                                                                                                                                         #
###########################################################################################################################################

from flask import Flask, render_template, url_for, g, redirect, request, flash, session, Blueprint, send_from_directory
from werkzeug.utils import secure_filename
import time as time
from cand import Candidate
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# import toastr as toastr
app = Flask(__name__)

# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

# jinja2 setup
import jinja2 as ninja
import os
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja2_env = ninja.Environment(loader=ninja.FileSystemLoader(template_dir))

# SQLite database setup
app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.path.join(app.instance_path, "myData.sqlite"),
    STATICFILES_DIRS=(
        os.path.join(BASE_DIR, 'static'),
    ),
    STATIC_URL='/static/',
    STATIC_ROOT=os.path.join(BASE_DIR, 'staticfiles'),
)

from db import init_app, get_db, insert, remove, init_app
from dataVisualBuilder import createGraph
init_app(app)  # initialize the database

# App setup
init_app(app)


###########################################################################################################################################
#                                                                                                                                         #
#                                                           Login Features                                                                #
#                                                                                                                                         #
###########################################################################################################################################

import login
from login import login_required
app.register_blueprint(login.bp)


###########################################################################################################################################
#                                                                                                                                         #
#                                                           Routing                                                                       #
#                                                                                                                                         #
###########################################################################################################################################

# Home Page
@app.route('/')
def home():

    return render_template('home.html')


# Settings Page
@app.route('/settings', methods=("GET", "POST"))
@login_required
def settings():
    # Add Candidate Form
    if request.method == "POST":
        if "insert" in request.form:
            name = request.form["candName"]
            bio = request.form["candBio"]
            tempimage = request.files["filename"]  # special object from Flask
            if tempimage.filename == '':
                return render_template('index.html', alert="settings")

            # check that name isnt any injection attack
            filename = secure_filename(tempimage.filename)

            # save this image

            filename = app.config["STATIC_ROOT"] + str(time.time()) + filename
            tempimage.save(filename)
            print(filename)
            error = None

            if not name or not bio:
                error = "Missing Information"

            if error is not None:
                flash(error)
            else:
                insert("candidate", ["name", "bio", "img"], [name, bio, filename])
                return render_template('index.html', alert="insert")

        # Remove a Candidate Form
        elif "delete" in request.form:
            candName = request.form["candName"]
            remove("candidate", "name", candName)
            return render_template('index.html', alert="delete")

        # Seetings Form
        elif "settings" in request.form:
            db = get_db()
            realign = request.form["realign"]
            numPeople = request.form["people"]
            error = None

            if not numPeople:
                error = "Missing Information"

            if error is not None:
                flash(error)
            else:
                insert("settings", ["realign", "numPeople"], [realign, numPeople])
                return render_template('index.html', alert="settings")

    # Main Page
    return render_template('index.html')


# Count Page
@app.route('/count', methods=("GET", "POST"))
def count():
    global Candidates
    Candidates = []
    # get candidate names
    db = get_db()
    cursor = db.cursor()

    # get data from candidates table
    names = []
    bios = []
    images = []
    for row in cursor.execute('SELECT * FROM candidate'):
        canName = row['name']
        canImage = row['img']
        canBio = row['bio']
        names.append(canName)
        images.append(canImage)
        bios.append(canBio)

    for i in range(0, len(names)):
        # imageURL = "https://i.imgur.com/yXvE8B1.png"
        # imageURL = url_for('static', filename=(images[i]))
        imageURL = images[i]# [40:]
        # imageURL = imageURL.replace("\\", "/")
        cand = Candidate(names[i], bios[i], imageURL)
        Candidates.append(cand)

    if request.method == "POST":
        db = get_db()
        numOfVotes = request.form['numVotes']
        name = request.form['Candname']
        db.execute(
                "UPDATE candidate WHERE name=(?) SET numVotes=(?)", (name, numOfVotes),
            )
    return render_template('votes.html', Candidates=Candidates)


# Data Page
@app.route('/data')
@login_required
def data():
    global Candidates
    Candidates = []
    # get candidate names
    db = get_db()
    cursor = db.cursor()

    # get data from candidates table
    names = []
    bios = []
    images = []
    for row in cursor.execute('SELECT * FROM candidate'):
        canName = row['name']
        canImage = row['img']
        canBio = row['bio']
        names.append(canName)
        images.append(canImage)
        bios.append(canBio)

    for i in range(0, len(names)):
        imageURL = images[i]  # [40:]
        cand = Candidate(names[i], bios[i], imageURL)
        Candidates.append(cand)

    # graph
    for filename in os.listdir('static/images'):
        if filename.startswith('graph'):
            os.remove('static/images/' + filename)
    filename = createGraph()
    return render_template('data.html', graphPath=filename, Candidates=Candidates)


local = True
if __name__ == '__main__':
    if local:
        import os
        HOST = os.environ.get('SERVER_HOST', 'localhost')
        try:
            PORT = int(os.environ.get('SERVER_PORT', '5555'))
        except ValueError:
            PORT = 5555
        app.run(HOST, PORT)
    else:
        app.run(debug=True)
