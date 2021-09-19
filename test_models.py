"""Model tests."""

# run these tests like:
#
#    python -m unittest test_models.py


import os
from unittest import TestCase
from sqlalchemy.exc import IntegrityError

from models import db, User, Book, Club, Meeting, Note, Read, Membership, Favorite

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///booktalk-test"


# Now we can import app

from app import app
import pdb

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserModelTestCase(TestCase):
    """Test User model functionality"""

    def setUp(self):
        """Add sample data"""

        db.drop_all()
        db.create_all()

        