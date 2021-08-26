from flask_wtf import FlaskForm
from flask_wtf.recaptcha import validators
from wtforms import StringField, FloatField
from wtforms.validators import Email, InputRequired

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])