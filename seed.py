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

# If table isn't empty, empty it
Club.query.delete()

potter_fans = Club(name="Potter Fan Club")
lotr_nerds = Club(name="The Hobbits")
radiants = Club(name="The Radiants")
mystery_fans = Club(name="Mystery Fans")
nonfiction = Club(name="Nonfiction Nerds")

db.session.add_all([potter_fans, lotr_nerds, radiants, mystery_fans, nonfiction])

db.session.commit()


#### Books ####

# If table isn't empty, empty it
Book.query.delete()

# In the full app, will need to send request to openlibrary's API to fetch model information
azkaban = Book(title="Harry Potter and the Prisoner of Azkaban", author="JK Rowling", image="/static/images/azkaban.jpeg", num_pages=317, publish_date="8 July 1999")
goblet = Book(title="Harry Potter and the Goblet of Fire", author="JK Rowling", image="/static/images/goblet.png", num_pages=636, publish_date="8 July 2000")
phoenix = Book(title="Harry Potter and the Order of the Phoenix", author="JK Rowling", image="/static/images/phoenix.jpeg", num_pages=766, publish_date="21 June 2003")
fellowship = Book(title="The Fellowship of the Ring", author="JRR Tolkien", image="/static/images/fellowship.jpeg", num_pages=423, publish_date="29 July 1954")
hobbit = Book(title="The Hobbit", author="JRR Tolkien", image="/static/images/hobbit.jpeg", num_pages=310, publish_date="21 September 1937")
kings = Book(title="The Way of Kings", author="Brandon Sanderson", image="/static/images/kings.png", num_pages=1007, publish_date="31 August 2010")
radiance = Book(title="Words of Radiance", author="Brandon Sanderson", image="/static/images/radiance.png", num_pages=1087, publish_date="4 March 2014")
meaning = Book(title="Man's Search for Meaning", author="Viktor E. Frankl", image="/static/images/meaning.jpeg", num_pages=200, publish_date="1946")
patient = Book(title="The Silent Patient", author="Alex Michaelides", image="/static/images/patient.png", num_pages=336, publish_date="5 February 2019")

db.session.add_all([azkaban, goblet, fellowship, phoenix, hobbit, kings, radiance, meaning, patient])
db.session.commit()


#### Relationships ####

u1 = User.query.filter_by(username="Whiskey").first()
u2 = User.query.filter_by(username="Bowser").first()
u3 = User.query.filter_by(username="Spike").first()
u4 = User.query.filter_by(username="Mario").first()
u5 = User.query.filter_by(username="Luigi").first()

c1 = Club.query.filter_by(name="Potter Fan Club").first()
c2 = Club.query.filter_by(name="The Hobbits").first()
c3 = Club.query.filter_by(name="The Radiants").first()
c4 = Club.query.filter_by(name="Mystery Fans").first()
c5 = Club.query.filter_by(name="Nonfiction Nerds").first()

b1 = Book.query.filter_by(title="Harry Potter and the Prisoner of Azkaban").first()
b2 = Book.query.filter_by(title="Harry Potter and the Goblet of Fire").first()
b3 = Book.query.filter_by(title="The Fellowship of the Ring").first()
b4 = Book.query.filter_by(title="Harry Potter and the Order of the Phoenix").first()
b5 = Book.query.filter_by(title="The Hobbit").first()
b6 = Book.query.filter_by(title="The Way of Kings").first()
b7 = Book.query.filter_by(title="Words of Radiance").first()
b8 = Book.query.filter_by(title="Man's Search for Meaning").first()
b9 = Book.query.filter_by(title="The Silent Patient").first()


### Memberships ###

# If table isn't empty, empty it
Membership.query.delete()

u1.clubs.append(c1)
u1.clubs.append(c2)
u1.clubs.append(c5)

u2.clubs.append(c1)
u2.clubs.append(c4)

u3.clubs.append(c1)
u3.clubs.append(c2)

u4.clubs.append(c3)
u4.clubs.append(c4)
u4.clubs.append(c5)

u5.clubs.append(c3)
u5.clubs.append(c4)

### Meetings ###

# If table isn't empty, empty it
Meeting.query.delete()

meeting1 = Meeting(date="9/20/21", club_id=c1.id)
meeting2 = Meeting(date="9/30/21", club_id=c1.id)
meeting3 = Meeting(date="9/20/21", club_id=c2.id)
meeting4 = Meeting(date="9/30/21", club_id=c2.id)
meeting5 = Meeting(date="9/21/21", club_id=c3.id)
meeting6 = Meeting(date="9/21/21", club_id=c4.id)
meeting7 = Meeting(date="9/30/21", club_id=c5.id)

db.session.add_all([meeting1, meeting2, meeting3, meeting4, meeting5, meeting6, meeting7])
db.session.commit()

m1 = db.session.query(Meeting).filter( Meeting.date == "9/20/21", Meeting.club_id == c1.id).first()
m2 = db.session.query(Meeting).filter( Meeting.date == "9/30/21", Meeting.club_id == c1.id).first()
m3 = db.session.query(Meeting).filter( Meeting.date == "9/20/21", Meeting.club_id == c2.id).first()
m4 = db.session.query(Meeting).filter( Meeting.date == "9/30/21", Meeting.club_id == c2.id).first()
m5 = db.session.query(Meeting).filter( Meeting.date == "9/21/21", Meeting.club_id == c3.id).first()
m6 = db.session.query(Meeting).filter( Meeting.date == "9/21/21", Meeting.club_id == c4.id).first()
m7 = db.session.query(Meeting).filter( Meeting.date == "9/30/21", Meeting.club_id == c5.id).first()

## Notes ###

# If table isn't empty, empty it
Note.query.delete()

# The first note will be associated with a meeting from the outset. The rest will be added via append later
n1 = Note(user_id=u1.id, book_id=b1.id, text="This is my favorite Harry Potter book. I love Sirius and Harry's relationship.", meeting_id=m1.id)
n2 = Note(user_id=u2.id, book_id=b1.id, text="I bet Dementors would be a good defense against Mario....")
n3 = Note(user_id=u3.id, book_id=b3.id, text="My favorite member of the Fellowship is Gimli because he's short like me")
n4 = Note(user_id=u4.id, book_id=b4.id, text="Mama mía pizza pia!")

db.session.add_all([n1, n2, n3, n4])
db.session.commit()

### Reads ###

# If table isn't empty, empty it
Read.query.delete()

# Harry Potter
r1 = Read(club_id=c1.id, book_id=b1.id, current=False, complete=True)
r2 = Read(club_id=c1.id, book_id=b2.id, current=True, complete=False)
r3 = Read(club_id=c1.id, book_id=b4.id, current=False, complete=False)

# Lord of the Rings
r4 = Read(club_id=c2.id, book_id=b3.id, current=True, complete=False)
r5 = Read(club_id=c2.id, book_id=b5.id, current=False, complete=True)

# Stormlight Archive
r6 = Read(club_id=c3.id, book_id=b6.id, current=False, complete=True)
r7 = Read(club_id=c3.id, book_id=b7.id, current=True, complete=False)

# Mystery
r8 = Read(club_id=c4.id, book_id=b9.id, current=True, complete=False)

# Nonfiction
r9 = Read(club_id=c5.id, book_id=b8.id, current=True, complete=False)

db.session.add_all([r1, r2, r3, r4, r5, r6, r7, r8, r9])
db.session.commit()


### Add remaining notes to meetings ###

m1.notes.append(n2)
m3.notes.append(n3)
m5.notes.append(n4)


### Add favorites ###

# If table isn't empty, empty it
Favorite.query.delete()

f1 = Favorite(user_id=u1.id, book_id=b1.id)
f2 = Favorite(user_id=u2.id, book_id=b2.id)
u3.favorites.append(b3)
u4.favorites.append(b4)

db.session.add_all([f1, f2])
db.session.commit()