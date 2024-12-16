from flask_wtf import FlaskForm
from wtforms import SubmitField


class SignupvalidationForm(FlaskForm):
    submit = SubmitField("Save signupvalidation")
