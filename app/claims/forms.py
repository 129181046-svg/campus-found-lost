# app/claims/forms.py

from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ClaimForm(FlaskForm):
    color        = StringField('Color / Colour',
                               validators=[DataRequired(), Length(2, 100)])
    brand        = StringField('Brand / Make',
                               validators=[DataRequired(), Length(2, 100)])
    unique_marks = StringField('Unique Marks or Stickers',
                               validators=[DataRequired(), Length(2, 200)])
    extra_info   = TextAreaField('Any other identifying details',
                                 validators=[DataRequired(), Length(10, 500)])
    submit       = SubmitField('Submit Claim')