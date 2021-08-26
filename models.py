from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.orm import backref

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    first_name = db.Column(db.String(), nullable=False)
    last_name = db.Column(db.String(), nullable=False)
    image = db.Column(db.Text, default="")
    bio = db.Column(db.Text)

    # Map to clubs through membership. You can see which clubs a user is a part of, and which users are in which clubs
    clubs = db.relationship('Club', secondary="memberships", backref="users")
    # Map directly to memberships (important to view join date)
    membership = db.relationship('Membership', backref="users")

    # Map directly to notes so you can see the notes a user has made on each book
    notes = db.relationship('Note', backref="users")

    @classmethod
    def register(cls, username, pwd, first, last, image, bio, email):
        """Register user w/hashed password & return user."""
        pwd_hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = pwd_hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8, first_name=first, last_name=last, image=image, bio=bio, email=email)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct.

        Return user if valide; else return False"""

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, pwd):
            # return user instance
            return u
        else:
            return False


class Book(db.Model):
    """Book model"""

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(), nullable=False)
    image = db.Column(db.Text)
    num_pages = db.Column(db.Integer, nullable=False)
    publish_date = db.Column(db.Text, nullable=False)

    # Map to clubs through reads
    clubs = db.relationship('Club', secondary="reads", backref="books")
    # Map directly to reads (important for finding whether this is the current book or not)
    reads = db.relationship('Read', backref="books")

    # Map directly to notes so you can see the notes a on each book
    notes = db.relationship('Note', backref="books")

class Club(db.Model):
    """Club model"""

    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False, unique=True) 

class Membership(db.Model):
    """Membership model, maps users to clubs"""

    __tablename__ = "memberships"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), primary_key=True)

    join_date = db.Column(db.Date)

class Note(db.Model):
    """Connects users with books, allows for multiple users to add notes to multiple books"""

    __tablename__ = "notes"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    text = db.Column(db.Text)
    discussion_date = db.Column(db.Text)



class Read(db.Model):
    """Maps clubs to books and marks as current or past"""

    __tablename__ = "reads"

    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    current = db.Column(db.Boolean)