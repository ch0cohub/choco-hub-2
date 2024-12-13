from flask_wtf import FlaskForm
from wtforms import SubmitField


class PasswordForm(FlaskForm):
    submit = SubmitField("Save password")
