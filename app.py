from flask import Flask, request, redirect, render_template, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from datetime import date

from models import db, connect_db, User, Book, Club, Membership, Read, Note, Meeting, Favorite
from forms import LoginForm, RegisterForm, NewNoteForm, EditNoteForm, DeleteForm, EditUserForm, ClubForm, MeetingForm, BookSearchForm
from transforms import transform_book_res

import requests
import pdb

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///booktalk' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_ECHO'] = True

app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


########################################################################
# User register/login/logout


@app.before_request
def load_user():
    """If logged in, load curr user."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route("/register", methods=["GET", "POST"])
def register():
    """Generate and handles registration submission"""

    if g.user:
        flash("You're already registered", "text-danger")
        return redirect(f"/")

    form = RegisterForm()
    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        image = form.image.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        bio = form.bio.data

        user = User.register(username=username, pwd=password, email=email, first=first_name, last=last_name, bio=bio, image=image)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Sorry, this username is already taken. Please choose another')
            return render_template('users/register.html', form=form)

        do_login(user)

        flash(f'Your account has been created. Welcome to BookTalk, {user.username}!', "text-success")
        first = True

        return redirect ("/", first=first)
    
    else:
        return render_template('users/register.html', form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Generates and handles login form submission"""
    if g.user:
        flash("You're already logged in.", "text-danger")
        return redirect("/")

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            # flash(f"Welcome Back, {user.first_name}!", "text-primary")
            do_login(user)
            return redirect('/')
        else:
            form.username.errors = ['Invalid username/password.']

    return render_template('users/login.html', form=form)

@app.route("/logout")
def logout():
    """Logs out current user"""

    do_logout()

    return redirect("/login")



############################################################################
# User routes


@app.route("/users")
def show_users():
    """Shows a list of users in the app if logged in"""

    if not g.user:
        flash("You need to be logged in with a registered account to view that page.", "text-danger")
        return redirect("/")

    users = User.query.all()

    return render_template("users/list.html", users=users)

@app.route("/users/<int:user_id>")
def user_details(user_id):
    """Shows user profile if logged in."""

    if not g.user:
        flash("You need to be logged in with a registered account to view that page.", "text-danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)

    return render_template("users/details.html", user=user)

@app.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
def edit_user(user_id):
    """Generates and handles submission of user edit form"""

    if not g.user:
        flash("In order to edit a profile, you must sign into that profile.", "text-danger")
        return redirect("/")

    form = EditUserForm()

    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)
        if user:

            user.username = form.username.data
            user.email = form.email.data
            user.image = form.image.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.bio = form.bio.data

            try:
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                form.username.errors.append('Sorry, this username is already taken. Please choose another')
                return render_template('users/edit.html', form=form)
            
            flash("Successfully updated user information.", "text-success")
            return redirect (f"/users/{user.id}")
        else:
            flash("The password you entered was not correct.", "text-danger")
            return redirect ("/")
    
    else:
        return render_template('users/edit.html', form=form)

@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete user."""

    user = User.query.get_or_404(user_id)

    if not g.user or user is not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/register")



###########################################################################
# Home page


@app.route("/")
def show_home():
    """Show home page."""

    # If no user is signed in, redirect to log-in page
    if g.user:
        
        return render_template("home.html", user=g.user)

    else:
        return redirect("/login")


############################################################################
# Club routes


@app.route("/clubs")
def show_clubs():
    """Shows list of active clubs"""

    if not g.user:
        flash("You need to be logged in with a registered account to view that page.", "text-danger")
        return redirect("/")

    clubs = Club.query.all()

    return render_template("clubs/list.html", clubs=clubs)

@app.route("/clubs/<int:club_id>")
def show_club_page(club_id):
    """Shows page with club details"""

    if not g.user:
        flash("You need to be logged in with a registered account to view that page.", "text-danger")
        return redirect("/")
    
    club = Club.query.get_or_404(club_id)

    # If user is in the club, they will see a more detailed club page
    if g.user in club.users:
        ########################
        # Build shelves

        # Create list of club's books
        reads = []
        for book in club.books:
            for read in book.reads:
                reads.append(read)

        # Create list of reads that are not current
        shelved = []
        for read in reads:
            if not read.current:
                shelved.append(read)

        # From shelved books, separate books that have been finished
        finished_ids = []
        unfinished_ids = []

        for read in shelved:
            if read.complete:
                finished_ids.append(read.book_id)
            else:
                unfinished_ids.append(read.book_id)

        finished = Book.query.filter(Book.id.in_(finished_ids)).all()
        unfinished = Book.query.filter(Book.id.in_(unfinished_ids)).all()

        ########################
        # Designate admins and moderators

        admin = Membership.query.filter(Membership.admin == True, Membership.club_id == club.id).first()
        mod_memberships = Membership.query.filter(Membership.moderator == True, Membership.club_id == club.id).all()
        mm_ids = []
        for membership in mod_memberships:
            mm_ids.append(membership.user_id)
        mods = User.query.filter(User.id.in_(mm_ids)).all()

        return render_template("clubs/member-details.html", club=club, unfinished=unfinished, finished=finished, admin=admin, mods=mods)

    else:
        return render_template("clubs/general-details.html", club=club)

@app.route("/clubs/create", methods=["GET", "POST"])
def create_club():
    """Generates and handles submission of new club form"""

    if not g.user:
        flash("In order to edit a profile, you must sign into that profile.", "text-danger")
        return redirect("/")

    form = ClubForm()
    if form.validate_on_submit():

        name = form.name.data
        club = Club(name=name)

        # Try to create the club, return error if name is taken
        try:
            db.session.add(club)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            form.name.errors.append('Sorry, this club name is already taken. Please choose another')
            return render_template('clubs/new.html', form=form)
        
        c = Club.query.filter(Club.name==name).first()

        # Capture the date for the join_date
        today = date.today()
        join_date = today.strftime("%m/%d/%y")
        # Give club creator admin privileges
        membership = Membership(user_id=g.user.id, club_id=c.id, join_date=join_date, admin=True, moderator=False)
        db.session.add(membership)
        db.session.commit()

        return redirect (f"/clubs/{c.id}")
    
    else:
        return render_template('clubs/new.html', form=form)

@app.route("/clubs/<int:club_id>/delete", methods=["POST"])
def delete_club(club_id):
    """Deletes a member to delete a club he or she is a part of"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")
        

    club = db.session.query(Club).get_or_404(club_id)

    membership = db.session.query(Membership).filter(Membership.club_id == club_id, Membership.user_id == g.user.id).first()

    if membership.admin:
        db.session.delete(club)
        db.session.commit()

        return redirect("/clubs")
    else:
        flash("Permission reserved for admin.", "text-danger")
        return redirect("/clubs")


############################################################################
# Membership routes (clubs subroutes)
    

@app.route("/clubs/<int:club_id>/join", methods=["POST"])
def join_club(club_id):
    """Join a club"""

    if not g.user:
        flash("In order to edit a profile, you must sign into that profile.", "text-danger")
        return redirect("/")

    club = db.session.query(Club).get_or_404(club_id)

    if g.user in club.users:
        flash("You're already part of this club.'", "text-danger")
        return redirect(f"/clubs/{club_id}")
    
    # If the club is empty, the user joining automatically becomes the moderator
    if len(club.users) == 0:
        m = Membership(user_id=g.user.id, club_id=club_id, admin=True)
        db.session.add(m)
        db.session.commit()
    else:
        m = Membership(user_id=g.user.id, club_id=club_id)
        db.session.add(m)
        db.session.commit()

    return redirect(f"/clubs/{club_id}")


@app.route("/clubs/<int:club_id>/leave", methods=["POST"])
def leave_club(club_id):
    """Leave a club"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    club = db.session.query(Club).get_or_404(club_id)

    if g.user not in club.users:
        flash("You're not a member of this club.'", "text-danger")
        return redirect(f"/clubs/{club_id}")

    g.user.clubs.remove(club)
    db.session.commit()

    return redirect(f"/clubs/{club_id}")


@app.route("/clubs/<int:club_id>/<int:user_id>/toggle_moderator", methods=["POST"])
def add_moderator(club_id, user_id):
    """Allow club admin to add a moderator"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")
        
    admin = Membership.query.filter(Membership.user_id == g.user.id, Membership.club_id == club_id).first()
    is_admin = admin.admin

    if is_admin:
        membership = Membership.query.filter(Membership.user_id == user_id, Membership.club_id == club_id).first()
        user = User.query.filter(User.id == user_id).first()

        if membership.moderator == False:
            membership.moderator = True
            db.session.commit()
            flash(f"Promoted {user.username} to Moderator!", "text-success")
            return redirect(f"/clubs/{club_id}")
        
        else:
            membership.moderator = False
            db.session.commit()
            flash(f"Demoted { user.username } from Moderator.", "text-success")
            return redirect(f"/clubs/{club_id}")

    else:
        flash(f"Admin status required.", "text-danger")
        return redirect(f"/clubs/{club_id}")



############################################################################
# Reads routes (clubs subroutes)


@app.route("/clubs/<int:club_id>/<int:book_id>/toggle_current", methods=["POST"])
def toggle_current(club_id, book_id):
    """Marks a current book as not current and a not current book as current"""

    # TO DO: Revise this function so that only the creator of the club can alter the current book

    club = db.session.query(Club).get_or_404(club_id)

    if not g.user or g.user not in club.users:
        flash("You must be signed in as a member of that club in order to view that page.", "text-danger")
        return redirect("/")

    try:
        read = db.session.query(Read).filter(Read.book_id == book_id, Read.club_id == club_id).first()
    except:
        flash(f"This club is not reading the selected book.")
        return redirect("/")

    # Find the club's read which matches the requested book id. If current, mark not; if not current, mark as current and mark the other current book as not current.
    if read.current:
        read.current = False
        db.session.commit()

        flash(f"Marked as not current", "text-success")
        return redirect(f"/clubs/{club_id}")

    else: 
        for curr_read in club.reads:
            if curr_read.current:
                curr_read.current = False

        read.current = True
        db.session.commit()
        
        flash(f"Marked as current", "text-success")
        return redirect(f"/clubs/{club_id}")


@app.route("/clubs/<int:club_id>/<int:book_id>/toggle_complete", methods=["POST"])
def toggle_complete(club_id, book_id):
    """Marks an incomplete book as complete or reset a completed book to read again"""

    club = db.session.query(Club).get_or_404(club_id)

    # TO DO: Revise this function so that only the creator of the club can alter the completed book

    if not g.user or g.user not in club.users:
        flash("You must be signed in as a member of that club in order to view that page.", "text-danger")
        return redirect("/")

    try:
        read = db.session.query(Read).filter(Read.book_id == book_id, Read.club_id == club_id).first()
    except:
        flash(f"This club is not reading the selected book.")
        return redirect("/")
    
    if read.complete:
        read.complete = False
        db.session.commit()

        flash(f"Marked as not completed", "text-success")
        return redirect(f"/clubs/{club_id}")
    
    else:
        read.complete = True
        read.current = False 
        db.session.commit()

        flash(f"Marked as finished!", "text-success")
        return redirect(f"/clubs/{club_id}")




############################################################################
# Meetings routes (clubs subroutes)

@app.route("/clubs/<int:club_id>/meetings/<int:m_id>")
def show_meetings(club_id, m_id):
    """Generate page with all of club's meetings"""

    club = db.session.query(Club).get_or_404(club_id)

    if not g.user or g.user not in club.users:
        flash("You must be signed in as a member of that club in order to view that page.", "text-danger")
        return redirect("/")
    
    meeting = Meeting.query.get_or_404(m_id)

    ########################
    # Designate admins and moderators

    admin = Membership.query.filter(Membership.admin == True, Membership.club_id == club.id).first()
    mod_memberships = Membership.query.filter(Membership.moderator == True, Membership.club_id == club.id).all()
    mm_ids = []
    for membership in mod_memberships:
        mm_ids.append(membership.user_id)
    mods = User.query.filter(User.id.in_(mm_ids)).all()


    return render_template("clubs/meetings/details.html", club=club, meeting=meeting, admin=admin, mods=mods)

@app.route("/clubs/<int:club_id>/meetings/new", methods=["GET", "POST"])
def create_meeting(club_id):
    """Generate and handle submission of new meeting form"""

    club = db.session.query(Club).get_or_404(club_id)

    membership = db.session.query(Membership).filter(Membership.club_id == club_id, Membership.user_id == g.user.id).first()

    if membership.admin or membership.moderator:
        permission = True
    else:
        permission = False

    if not g.user or g.user not in club.users or not permission:
        flash("You must have be an admin or moderator of that club in order to view that page.", "text-danger")
        return redirect("/")

    form = MeetingForm()

    # get list of club's book titles
    titles = [book.title for book in club.books]

    # dynamically set topic choices
    form.topic.choices = titles

    if form.validate_on_submit():
        meeting = Meeting(date = form.date.data, topic = form.topic.data, url = form.url.data, club_id = club.id)
        db.session.add(meeting)
        db.session.commit()
        flash("New meeting added!")
        return redirect(f"/clubs/{club_id}")

    else:
        return render_template("clubs/meetings/add.html", form=form)



############################################################################
# Notes routes 



@app.route("/meetings/<int:m_id>/notes/add", methods=["GET", "POST"])
def add_note(m_id):
    """Generate and handle submission of new note form"""

    meeting = db.session.query(Meeting).get_or_404(m_id)
    club = db.session.query(Club).get_or_404(meeting.club_id)

    if not g.user or g.user not in club.users:
        flash("You must be signed in as a member of that club in order to view that page.", "text-danger")
        return redirect("/")

    form = NewNoteForm()

    # get list of club's book titles
    # titles = [(book.title, book.id) for book in club.books]
    titles = [book.title for book in club.books]
    book_ids = [book.id for book in club.books]

    # pdb.set_trace()

    # dynamically set topic choices
    form.book.choices = titles

    if form.validate_on_submit():
        title = form.book.data
        id_ind = titles.index(title)
        book_id = book_ids[id_ind]
        
        book = db.session.query(Book).filter(Book.id == book_id).first()

        text = form.text.data

        note = Note(text=text, user_id=g.user.id, book_id=book.id, meeting_id=m_id)

        db.session.add(note)
        db.session.commit()
        flash("Note added!")
        return redirect(f"/clubs/{club.id}/meetings/{m_id}")

    else:
        return render_template("notes/add.html", form=form, meeting=meeting, club=club)

    
@app.route("/meetings/<int:m_id>/notes/<int:note_id>/edit", methods=["GET", "POST"])
def edit_note(m_id, note_id):
    """Generate and handle submission of new note form"""

    meeting = db.session.query(Meeting).get_or_404(m_id)
    club = db.session.query(Club).get_or_404(meeting.club_id)

    if not g.user or g.user not in club.users:
        flash("You must be signed in as a member of that club in order to view that page.", "text-danger")
        return redirect("/")

    note = Note.query.filter(Note.id == note_id).first()

    form = EditNoteForm()

    if form.validate_on_submit():
        text = form.text.data

        note.text = text

        db.session.commit()
        flash("Note edited!")
        return redirect(f"/clubs/{club.id}/meetings/{m_id}")

    else:
        return render_template("notes/edit.html", form=form, meeting=meeting, club=club)

@app.route("/meetings/<int:m_id>/notes/<int:note_id>/delete", methods=["POST"])
def delete_note(m_id, note_id):
    """Delete a note."""

    meeting = db.session.query(Meeting).get_or_404(m_id)
    club = db.session.query(Club).get_or_404(meeting.club_id)

    if not g.user or g.user not in club.users:
        flash("You must be signed in as a member of that club in order to view that page.", "text-danger")
        return redirect("/")
    
    note = Note.query.filter(Note.id == note_id).first()

    if note.user_id != g.user.id:
        flash("Only a note's creator may delete it.", "text-danger")
        return redirect(f"/clubs/{club.id}/meetings/{m_id}")

    else:
        db.session.delete(note)
        db.session.commit()

        flash("Note deleted!", "text-success")
        return redirect(f"/clubs/{club.id}/meetings/{m_id}")


############################################################################
# Book routes

OPEN_LIB_URL = 'https://openlibrary.org';

@app.route("/books")
def show_books():
    """Shows list of books in BookTalk's database."""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    books = Book.query.all()

    all_books = True

    return render_template("books/list.html", books=books, all_books=all_books)

@app.route("/books/my_books")
def show_my_books():
    """Shows list of books in BookTalk's database."""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    # CODE REVIEW QUESTION: Is there a cleaner way to do the following query? In SQL, we're running 4 JOINs:
    # SELECT books.id FROM books                                           
    # JOIN reads                                                                      
    # ON books.id = reads.book_id                                                     
    # JOIN clubs                                                                      
    # ON reads.club_id = clubs.id                                                     
    # JOIN memberships                                                                
    # ON clubs.id = memberships.club_id
    # JOIN users
    # ON memberships.user_id = users.id
    # WHERE users.id = 2;

    # Get books that are read by clubs which the user is a member of
    user_memberships = db.session.query(Membership).filter_by(user_id=g.user.id).all()
    user_club_ids = [membership.club_id for membership in user_memberships]
    user_club_reads = db.session.query(Read).filter(Read.club_id.in_(user_club_ids)).all()
    user_book_ids = [read.book_id for read in user_club_reads]
    books = Book.query.filter(Book.id.in_(user_book_ids)).all()

    return render_template("books/list.html", books=books)

@app.route("/books/<int:book_id>")
def book_details(book_id):
    """Shows details for a given book"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    # TO DO: Build transform function in order to pull this information from the API
    book = Book.query.get_or_404(book_id)

    return render_template("books/details.html", book=book)

@app.route("/books/<int:book_id>/favorite", methods=["POST"])
def add_favorite(book_id):
    """Add book to user.favorites"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    # TO DO: Build transform function in order to pull this information from the API
    book = Book.query.get_or_404(book_id)

    if book in g.user.favorites:
        flash("That book is already in your favorites.", "text-danger")
        return redirect("/books")

    else:
        g.user.favorites.append(book)
        db.session.commit()

        flash(f"Added {book.title} to your favorite books!", "text-success")
        return redirect("/books")

@app.route("/books/<int:book_id>/remove_favorite", methods=["POST"])
def remove_favorite(book_id):
    """Remove book from user.favorites"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    # TO DO: Build transform function in order to pull this information from the API
    book = Book.query.get_or_404(book_id)

    if book not in g.user.favorites:
        flash("That book isn't in your favorites.", "text-danger")
        return redirect("/")

    else:
        g.user.favorites.remove(book)
        db.session.commit()

        flash(f"Removed {book.title} from your favorite books.", "text-success")
        return redirect("/")

@app.route("/books/search", methods=["GET", "POST"])
def search_book():
    """Generate and handle submission of search book form"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    return render_template("/books/search.html")

@app.route("/books/<book_id>/transform", methods=["POST"])
def show_book(book_id):
    """Send a request to the OpenLibrary API using the bookID sent from the client, then transform response into BookTalk object. Pass this object to the rendered template."""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    # bookID = request.json['bookID']
    print("*********************************************")
    # print(f"BookID: {bookID}")
    print(f"BookID: {book_id}")

    # In order to get usable data, OpenLibrary requres two requests: the first to get the ISBN, which is then used for the second request which can be transformed into usable data

    res = requests.get(f"{OPEN_LIB_URL}/books/{book_id}.json")

    print(res.json())
    try:
        ISBN = res.json()['isbn_13'][0]
    except KeyError:
        flash(f"Our database doesn't include an ISBN number for the book you selected. Try choosing another.", "text-danger")
        return redirect("/books/search")

    ISBNres = requests.get(f"{OPEN_LIB_URL}/api/books?bibkeys=ISBN:{ISBN}&format=json&jscmd=data")

    bookData = ISBNres.json()[f"ISBN:{ISBN}"]
    book = transform_book_res(bookData)
    print(f"Book Object: {book}")

    session['book'] = book
    # pdb.set_trace()

    return redirect("/books/show")

@app.route("/books/show")  
def display_book():
    """Receives book data from transform route, and then uses to render template"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/")

    return render_template("/books/show.html")

@app.route("/books/add", methods=["POST"])
def add_book_to_db():
    """Takes book from session and adds it to BookTalk DB"""

    if not g.user:
        flash("You must be signed in in order to view that page.", "text-danger")
        return redirect("/") 
    
    book = session['book']


    # Check that book is not already in DB
    books = db.session.query(Book).all()
    titles = [book.title for book in books]

    if book['title'] not in titles:
        new_book = Book(title=book['title'], author=book['author'], image=book['image'], num_pages=book['num_pages'], publish_date=book['publish_date'])
        db.session.add(new_book)
        db.session.commit()

        flash(f"Added {book['title']} to BookTalk!", "text-success")
        return redirect("/books")

    else:
        flash(f"{book['title']} is already in BookTalk's Library.", "text-danger")
        return redirect("/books")
