from flask import Flask, request, redirect, render_template

from models import db, connect_db, User, Book, Club, Membership, Read, Note

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///booktalk' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

### Routes ###