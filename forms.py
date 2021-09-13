from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, SelectField, PasswordField, TextAreaField, IntegerField
from wtforms.validators import Email, InputRequired
from wtforms.fields.html5 import EmailField

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    image = StringField("Image URL", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    bio = TextAreaField("Bio", validators=[InputRequired()])

class EditUserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired(), Email()])
    image = StringField("Image URL", validators=[InputRequired()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])
    bio = TextAreaField("Bio", validators=[InputRequired()])

class ClubForm(FlaskForm):
    name = StringField("Club Name", validators =[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class NotesForm(FlaskForm):
    book = SelectField("Which book is this note for?", validators=[InputRequired()])
    text = StringField("Note Text", validators=[InputRequired()])
    discussion_date = StringField("Discussion Date", validators=[InputRequired()])

class MeetingForm(FlaskForm):
    date = StringField("Date", validators=[InputRequired()])
    # Topic will be selected from club's books
    topic = SelectField("Topic", validators=[InputRequired()])
    url = StringField("URL")

    # Club ID will be added automatically

class DeleteForm(FlaskForm):
    """Form used to send POST requests in delete pathways"""