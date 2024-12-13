from flask_wtf import FlaskForm
from wtforms import SubmitField


class MailconfigurationForm(FlaskForm):
    submit = SubmitField("Save mailconfiguration")
