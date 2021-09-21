"""User Views tests."""

# run these tests like:
#
#    python -m unittest test_user_views.py


import os
from unittest import TestCase
from requests.sessions import session
from sqlalchemy.exc import IntegrityError

from models import Club, db, User, Note, Membership, Favorite

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

# os.environ['DATABASE_URL'] = "postgresql:///booktalk_test"


# Now we can import app

from app import CURR_USER_KEY, app
import pdb

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///booktalk_test"
app.config['SQLALCHEMY_ECHO'] = False

# For tests of forms to work, need to disable CSRF checking in tests
app.config['WTF_CSRF_ENABLED'] = False

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class UserViewsTestCase(TestCase):
    """Test functionality of each User view"""

    def setUp(self):
        """Create test client, add sample data"""

        User.query.delete()
        Note.query.delete()
        Membership.query.delete()
        Favorite.query.delete()
        Club.query.delete()

        self.client = app.test_client()

        self.testuser = User.register(
            username="testuser",
            email="test@test.com",
            pwd="password",
            image=User.image.default.arg,
            bio="nothing",
            first="Mr.",
            last="Test")

        self.testuser_id = 9999
        self.testuser.id = self.testuser_id

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_register_form(self):
        """Register form loads upon request"""

        with self.client as c:
            resp = c.get("/register")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<form action="" method="post"', html)

    def test_register_user(self):
        """Can register through register view function"""


        with self.client as c:
            # with c.session_transaction() as sess:
                
            resp = c.post("/register", data={
                "username": "testuser2",
                "password": "password",
                "email": "email@email.com",
                "image": User.image.default.arg,
                "first_name": "Register",
                "last_name": "Test",
                "bio": "testbio"
            }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)

            user = User.query.filter(User.username == "testuser2").first()

            # Ensure user exists
            self.assertEqual(user.username, "testuser2")
        
    
    def test_show_login(self):
        """Show User login"""

        with self.client as c:
            resp = c.get("/login")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Log In to BookTalk</h1>', html)

    def test_login(self):
        """Test User login"""

        with self.client as c:
            data = {"username": "testuser", "password": "password"}
            resp = c.post("/login", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Welcome", html)

    def test_delete_user(self):
        """Delete user"""

        ## Since we need to change the session to mimic logging in,
        ## we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(f"/users/{self.testuser.id}/delete", follow_redirects=True)

            user = User.query.one_or_none()
            # pdb.set_trace()

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(user, None)
    
    def test_show_users(self):
        """Test show users route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get("/users")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h5 class="card-title">{self.testuser.username}</h5>', html)

    def test_show_user(self):
        """Test show user route"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<li>Username: { self.testuser.username }</li>', html)

    def test_show_user_edit_form(self):
        """Successfully load user edit form"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(f"/users/{self.testuser.id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1 class="display-1">Edit Your Profile</h1>', html)

    def test_user_edit(self):
        """Edit user profile"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            data = {
                "username": "EditedUser",
                "password": "password",
                "email": "email@email.com",
                "image": User.image.default.arg,
                "first_name": "Edit",
                "last_name": "Edit",
                "bio": "editedbio"
            }
            resp = c.post(f"/users/{self.testuser.id}/edit", data=data, follow_redirects = True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("EditedUser", html)


    ################################################################################
    # Test Membership routes

    # Create clubs
    def setup_club(self):
        """Used to add clubs to db"""

        c1 = Club(name="Club 1")

        db.session.add(c1)
        db.session.commit()

    def test_join_club(self):
        """User can join club"""

        self.setup_club()
        club = Club.query.first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/clubs/{club.id}/join")
            self.assertEqual(resp.status_code, 302)

            membership = Membership.query.one_or_none()

            self.assertEqual(membership.user_id, self.testuser.id)

            # REVIEW ERROR and "lazy loading"
            # sqlalchemy.orm.exc.DetachedInstanceError: Parent instance <User at 0x10e487590> is not bound to a Session; lazy load operation of attribute 'memberships' cannot proceed (Background on this error at: https://sqlalche.me/e/14/bhk3)
            # self.assertEqual(len(self.testuser.memberships), 1)
    
    # Create membership
    def setup_membership(self):
        """Used to add membership to db"""

        c = Club(name="Test Club")
        db.session.add(c)
        db.session.commit()

        club = Club.query.first()

        m = Membership(club_id=club.id, user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()


    def test_leave_club(self):
        """Test that user can leave club"""

        self.setup_membership()
        club = Club.query.first()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.post(f"/clubs/{club.id}/leave")
            self.assertEqual(resp.status_code, 302)

            membership = Membership.query.one_or_none()

            self.assertEqual(membership, None)

