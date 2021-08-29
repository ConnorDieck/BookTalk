from flask import Flask, request, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, Book, Club, Membership, Read, Note
from forms import LoginForm, RegisterForm, NotesForm, DeleteForm

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

    # If no user is signed in, redirect to log-in page
    if 'username' not in session:
        
        return redirect("/login")

    return render_template("home.html")

##### Login / registration page #####

@app.route("/register", methods=["GET", "POST"])
def register():
    """Generates and handles registration submission"""

    if 'username' in session:
        flash("You'll need to log out to view that page.", "text-danger")
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        u = User.register(username, password, email, first_name, last_name)

        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Sorry, this username is already taken. Please choose another')
            return render_template('register.html', form=form)

        session['username'] = u.username
        flash('Your account has been created. Welcome to BookTalk!', "text-success")
        return redirect (f"/users/{u.username}")
    
    return render_template('register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Generates and handles login form submission"""
    if 'username' in session:
        flash("You'll need to log out to view that page.", "text-danger")
        return redirect(f"/users/{session['username']}")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.first_name}!", "text-primary")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('login.html', form=form)


##### Routes for clubs #####


@app.route("/clubs")
def show_clubs():
    """Shows list of active clubs"""

    clubs = Club.query.all()

    return render_template("clubs.html", clubs=clubs)

