"""Seed file to make sample data for Heroku db."""

from models import Meeting, db, User, Club, Book, Membership, Read, Note, Favorite
from app import app

# Create all tables
db.drop_all()
db.create_all()