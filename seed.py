"""Seed file to make sample data for Users db."""

from models import db, User, Club, Book, Membership, Read, Note
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

# Add new objects to session, so they'll persist
db.session.add(whiskey)
db.session.add(bowser)
db.session.add(spike)

# Commit--otherwise, this never gets saved!
db.session.commit()


#### Clubs ####
potter_fans = Club(name="Potter Fan Club")
lotr_nerds = Club(name="The Hobbits")

db.session.add(potter_fans)
db.session.add(lotr_nerds)

db.session.commit()


#### Books ####

# In the full app, will need to send request to openlibrary's API to fetch model information
azkaban = Book(title="Harry Potter and the Prisoner of Azkaban", author="JK Rowling", image="/static/images/azkaban.jpeg", num_pages=317, publish_date="8 July 1999")
goblet = Book(title="Harry Potter and the Goblet of Fire", author="JK Rowling", image="/static/images/goblet.png", num_pages=636, publish_date="8 July 2000")
fellowship = Book(title="The Fellowship of the Ring", author="JRR Tolkien", image="/static/images/fellowship.jpeg", num_pages=423, publish_date="29 July 1954")

db.session.add_all([azkaban, goblet, fellowship])

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


### Memberships ###

u1.clubs.append(c1)
u1.clubs.append(c2)
u2.clubs.append(c1)
u3.clubs.append(c1)
u3.clubs.append(c2)

### Notes ###

n1 = Note(user_id=u1.id, book_id=b1.id, text="This is my favorite Harry Potter book. I love Sirius and Harry's relationship.", discussion_date="26 Aug 2021")
n2 = Note(user_id=u2.id, book_id=b1.id, text="I bet Dementors would be a good defense against Mario....", discussion_date="26 Aug 2021")
n3 = Note(user_id=u3.id, book_id=b3.id, text="My favorite member of the Fellowship is Gimli because he's short like me", discussion_date="28 August 2021")

db.session.add_all([n1, n2, n3])

db.session.commit()

### Reads ###

r1 = Read(club_id=c1.id, book_id=b1.id, current=False)
r2 = Read(club_id=c1.id, book_id=b2.id, current=True)
r3 = Read(club_id=c2.id, book_id=b3.id, current=True)

db.session.add_all([r1, r2, r3])

db.session.commit()