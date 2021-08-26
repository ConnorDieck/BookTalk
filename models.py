from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

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
    image = db.Column(db.Text, default="")
    bio = db.Column(db.Text)

    # You can see which clubs a user is a part of, and which users are in which clubs
    clubs = db.relationship('Club', secondary="memberships", backref="users")

    @classmethod
    def register(cls, username, pwd):
        """Register user w/hashed password & return user."""
        pwd_hashed = bcrypt.generate_password_hash(pwd)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = pwd_hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return cls(username=username, password=hashed_utf8)

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
    publish_date = db.Column(db.Date, nullable=False)

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

class Notes(db.Model):
    """Connects users with books, allows for multiple users to add notes to multiple books"""

    __tablename__ = "notes"

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    text = db.Column(db.Text)
    discussion_date = db.Column(db.Date)

class Reads(db.Model):
    """Maps clubs to books and marks as current or past"""

    __tablename__ = "reads"

    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'), primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), primary_key=True)

    current = db.Column(db.Boolean)
    discussion_date = db.Column(db.Date)