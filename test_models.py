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

app.config['SQLALCHEMY_ECHO'] = False

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

        u1 = User.register("testuser1", "password", "User1", "User1", "/static/images/placeholder.png", "test bio 1", "email1@email.com")
        uid1 = 1111
        u1.id = uid1

        u2 = User.register("testuser2", "password", "User2", "User2", "/static/images/placeholder.png", "test bio 2", "email2@email.com")
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does the basic model work?"""

        u = User(
            username="testuser",
            password="pswd_hash",
            email="test@test.com",
            first_name="test",
            last_name="test"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no favorites, no notes, and no memberships
        self.assertEqual(len(u.favorites), 0)
        self.assertEqual(len(u.notes), 0)
        self.assertEqual(len(u.memberships), 0)

    ######################################################
    # User.register tests

    def test_user_register_valid(self):
        """Does User.register successfully create a new user given valid credentials?"""

        u = User.register(
            username="testuser",
            email="test@test.com",
            pwd="pswd_hash",
            image=User.image.default.arg,
            bio="testbio",
            first="test",
            last="test"
        )

        db.session.commit()

        u.id = 9999

        user = User.query.get(u.id)
        username = user.username

        self.assertEqual(username, "testuser")

    def test_user_register_invalid(self):
        """Does User.register return an error with invalid credentials?"""

        invalid_user = User.register(
            username=None,
            email="test@test.com",
            pwd="password",
            image=User.image.default.arg,
            bio=None,
            first="test",
            last="test"
        )
        uid = 9999
        invalid_user.id = uid

        with self.assertRaises(IntegrityError) as cm:
            db.session.commit()

    
    ######################################################
    # User.authenticate tests 

    def test_user_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid name and password?"""

        user = User.authenticate("testuser1", "password")

        self.assertEqual(user.username, "testuser1")
        self.assertIn("$2b$", user.password)

    def test_user_authenticate_invalid_username(self):
        """Does User.authenticate successfully return False when given an invalid username?"""

        user = User.authenticate("wrong_username", "password")

        self.assertEqual(user, False)

    def test_user_authenticate_invalid_password(self):
        """Does User.authenticate successfully return False when given an invalid password?"""

        user = User.authenticate("test1", "wrong_password")

        self.assertEqual(user, False)