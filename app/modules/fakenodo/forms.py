from flask_wtf import FlaskForm
from wtforms import SubmitField


class FakeNodoForm(FlaskForm):
    submit = SubmitField('Simulate FakeNodo Action')