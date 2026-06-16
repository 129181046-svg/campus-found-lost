from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length

class ItemReportForm(FlaskForm):
    item_type = SelectField('Item Type', choices=[
        ('', '-- Select --'),
        ('lost', 'Lost'),
        ('found', 'Found'),
    ], validators=[DataRequired()])
    item_name = StringField('Item Name', validators=[DataRequired(), Length(3, 100)])
    category = SelectField('Category', choices=[
        ('', '-- Select Category --'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books & Stationery'),
        ('accessories', 'Accessories'),
        ('documents', 'Documents / ID Cards'),
        ('keys', 'Keys'),
        ('bags', 'Bags'),
        ('sports', 'Sports Equipment'),
        ('other', 'Other'),
    ], validators=[DataRequired()])
    location = SelectField('Location', choices=[
        ('', '-- Select Location --'),
        ('library', 'Library'),
        ('canteen', 'Canteen'),
        ('main_block', 'Main Block'),
        ('hostel', 'Hostel'),
        ('sports_complex', 'Sports Complex'),
        ('lab_block', 'Lab Block'),
        ('auditorium', 'Auditorium'),
        ('other', 'Other'),
    ], validators=[DataRequired()])
    date_occurred = DateField('Date Lost/Found', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(10, 500)])
    tags = StringField('Tags (comma-separated, e.g. blue, nike, airpods)')
    photo = FileField('Photo', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'webp'], 'Images only.')
    ])
    submit = SubmitField('Submit Report')