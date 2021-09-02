"""Seed file to make sample data for Users db."""

from models import Meeting, db, User, Club, Book, Membership, Read, Note, Favorite
from app import app

# Create all tables
db.drop_all()
db.create_all()

#### Users ####

# If table isn't empty, empty it
User.query.delete()

# Add Users
whiskey = User.register(username='Whiskey', bio="loves cocktail books", pwd="oldfashioned", first="Jack", last="Daniels", image="/static/images/jack_daniels.jpeg", email="whiskey@test.com")
bowser = User.register(username='Bowser', bio="reads Princess Peach catalogues", pwd="ihatemario", first="Bowser", last="Koopa", image="/static/images/bowser.png", email="bowser@test.com")
spike = User.register(username='Spike', bio="would like to read more", pwd="ouch", first="Spikey", last="Spike", image="/static/images/spike.png", email="spike@test.com")
mario = User.register(username='Mario', bio="mama mía", pwd="superstar", first="Mario", last="Mario", image="/static/images/mario.png", email="jumpman@test.com")
luigi = User.register(username='Luigi', bio="m-m-m-maaariooo??", pwd="daisy", first="Luigi", last="Mario", image="/static/images/luigi.png", email="imscared@test.com")

# Add new objects to session, so they'll persist
db.session.add(whiskey)
db.session.add(bowser)
db.session.add(spike)
db.session.add(mario)
db.session.add(luigi)

# Commit--otherwise, this never gets saved!
db.session.commit()


#### Clubs ####
potter_fans = Club(name="Potter Fan Club")
lotr_nerds = Club(name="The Hobbits")
empty1 = Club(name="Empty Club 1")
empty2 = Club(name="Empty Club 2")
empty3 = Club(name="Empty Club 3")
empty4 = Club(name="Empty Club 4")

db.session.add_all([potter_fans, lotr_nerds, empty1, empty2, empty3, empty4])

db.session.commit()


#### Books ####

# In the full app, will need to send request to openlibrary's API to fetch model information
azkaban = Book(title="Harry Potter and the Prisoner of Azkaban", author="JK Rowling", image="/static/images/azkaban.jpeg", num_pages=317, publish_date="8 July 1999")
goblet = Book(title="Harry Potter and the Goblet of Fire", author="JK Rowling", image="/static/images/goblet.png", num_pages=636, publish_date="8 July 2000")
phoenix = Book(title="Harry Potter and the Order of the Phoenix", author="JK Rowling", image="/static/images/phoenix.jpeg", num_pages=766, publish_date="21 June 2003")
fellowship = Book(title="The Fellowship of the Ring", author="JRR Tolkien", image="/static/images/fellowship.jpeg", num_pages=423, publish_date="29 July 1954")
hobbit = Book(title="The Hobbit", author="JRR Tolkien", image="/static/images/hobbit.jpeg", num_pages=310, publish_date="21 September 1937")

db.session.add_all([azkaban, goblet, fellowship, phoenix, hobbit])

db.session.commit()


#### Relationships ####

u1 = User.query.filter_by(username="Whiskey").first()
u2 = User.query.filter_by(username="Bowser").first()
u3 = User.query.filter_by(username="Spike").first()

c1 = Club.query.filter_by(name="Potter Fan Club").first()
c2 = Club.query.filter_by(name="The Hobbits").first()

b1 = Book.query.filter_by(title="Harry Potter and the Prisoner of Azkaban").first()
b2 = Book.query.filter_by(title="Harry Potter and the Goblet of Fire").first()
b3 = Book.query.filter_by(title="The Fellowship of the Ring").first()
b4 = Book.query.filter_by(title="Harry Potter and the Order of the Phoenix").first()
b5 = Book.query.filter_by(title="The Hobbit").first()


### Memberships ###

u1.clubs.append(c1)
u1.clubs.append(c2)
u2.clubs.append(c1)
u3.clubs.append(c1)
u3.clubs.append(c2)

### Meetings ###

meeting1 = Meeting(date="9/20/21", club_id=c1.id)
meeting2 = Meeting(date="9/30/21", club_id=c1.id)
meeting3 = Meeting(date="9/20/21", club_id=c2.id)
meeting4 = Meeting(date="9/30/21", club_id=c2.id)

db.session.add_all([meeting1, meeting2, meeting3, meeting4])
db.session.commit()

m1 = db.session.query(Meeting).filter( Meeting.date == "9/20/21", Meeting.club_id == c1.id).first()
m2 = db.session.query(Meeting).filter( Meeting.date == "9/30/21", Meeting.club_id == c1.id).first()
m3 = db.session.query(Meeting).filter( Meeting.date == "9/20/21", Meeting.club_id == c2.id).first()
m4 = db.session.query(Meeting).filter( Meeting.date == "9/30/21", Meeting.club_id == c2.id).first()

## Notes ###

# The first note will be associated with a meeting from the outset. The rest will be added via append later
n1 = Note(user_id=u1.id, book_id=b1.id, text="This is my favorite Harry Potter book. I love Sirius and Harry's relationship.", meeting_id=m1.id)
n2 = Note(user_id=u2.id, book_id=b1.id, text="I bet Dementors would be a good defense against Mario....")
n3 = Note(user_id=u3.id, book_id=b3.id, text="My favorite member of the Fellowship is Gimli because he's short like me")

db.session.add_all([n1, n2, n3])
db.session.commit()

### Reads ###

# Harry Potter
r1 = Read(club_id=c1.id, book_id=b1.id, current=False, complete=True)
r2 = Read(club_id=c1.id, book_id=b2.id, current=True, complete=False)
r3 = Read(club_id=c1.id, book_id=b4.id, current=False, complete=False)

# Lord of the Rings
r4 = Read(club_id=c2.id, book_id=b3.id, current=True, complete=False)
r5 = Read(club_id=c2.id, book_id=b5.id, current=False, complete=True)

db.session.add_all([r1, r2, r3, r4, r5])
db.session.commit()


### Add remaining notes to meetings ###

m1.notes.append(n2)
m3.notes.append(n3)


### Add favorites ###

f1 = Favorite(user_id=u1.id, book_id=b1.id)
f2 = Favorite(user_id=u2.id, book_id=b2.id)
u3.favorites.append(b3)

db.session.add_all([f1, f2])
db.session.commit()