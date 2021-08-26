"""Seed file to make sample data for Users db."""

from models import db, User, Club, Book, Membership, Reads, Notes
from app import app

# Create all tables
db.drop_all()
db.create_all()

# If table isn't empty, empty it
User.query.delete()

# Add Users
whiskey = User(username='Whiskey', bio="bookworm")
bowser = User(username='Bowser', bio="reads book sometimes")
spike = User(username='Spike', bio="would like to read more")

# Add new objects to session, so they'll persist
db.session.add(whiskey)
db.session.add(bowser)
db.session.add(spike)

# Commit--otherwise, this never gets saved!
db.session.commit()