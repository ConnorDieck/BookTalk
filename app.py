from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Book, Club, Membership, Read, Note

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///booktalk' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_ECHO'] = True

app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)

### Routes ###

@app.route("/")
def show_home():
    """Shows home page"""

    return render_template("home.html")