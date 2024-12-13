from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length


class CommunityForm(FlaskForm):

    name = StringField("Name", validators=[DataRequired(), Length(max=256)])
    description = TextAreaField("Description", validators=[DataRequired()])
    submit = SubmitField("Save community")
