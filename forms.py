from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SubmitField
from wtforms.validators import DataRequired


class UpdateMovieForm(FlaskForm):
    rating = FloatField("Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField("Your Review")
    submit = SubmitField("Done")


class AddMovieForm(FlaskForm):
    name = StringField("Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")
