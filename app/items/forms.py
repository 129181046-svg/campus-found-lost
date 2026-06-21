from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, RadioField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

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
        ('SOC', 'SOC'),
        ('VV Block', 'VV Block'),
        ('SOME (Mech)', 'SOME (Mech)'),
        ('SASHE', ' SASHE'),
        ('TDC', ' TDC'),
        ('LTC', 'LTC'),
        ('auditorium', 'Auditorium'),
        ('LIBRARY', 'Library'),
        ('JVC', 'JVC'),
        ('NMV', 'NMV'),
        ('CHANAKYA', 'CHANAKYA'),
        ('MANISHA', 'MANISHA'),
        ('CHITH VIHAR', 'CHITH VIHAR'),
        ('AROGYASALA [GURUNATH]', 'AROGYASALA (GURUNATH)'),
        ('VANIVIHAR', 'VANIVIHAR'),
        ('GNANA VIHAR', 'GNANA VIHAR'),
        ('VIDHYA VIHAR', 'VIDHYA VIHAR'),
        ('KRISHNA CANTEEN', 'KRISHNA CANTEEN'),
        ('SHANMUGA CANTEEN', 'SHANMUGA CANTEEN'),
        ('SOUTHERN CANTEEN', 'SOUTHERN CANTEEN'),
        ('VELA CAFE', 'NORTH CANTEEN'),
        ('ARUNDATI HOSTEL', 'ARUNDATI HOSTEL'),
        ('AHALYA HOSTEL', 'AHALYA HOSTEL'),
        ('ANASUYA HOSTEL', 'ANASUYA HOSTEL'),
        ('SV NEW', 'SV NEW'),
        ('SV OLD', 'SV OLD'),
        ('VB-1', 'VB-1'),
        ('VB-2', 'VB-2'),
        ('VB-3', 'VB-3'),
        ('SPS', 'SPS'),
        ('RLV', 'RLV'),
        ('KAMADENU', 'KAMADENU'),
        ('PV', 'PV'),
        ('VASHISTA', 'VASHISTA'),
        ('TEMPLE', 'TEMPLE'),
        ('SAC', 'SAC')
    ], validators=[DataRequired()])

    # NEW — optional floor/classroom detail
    room_number = StringField(
        'Floor / Room No. (optional)',
        validators=[Optional(), Length(max=50)]
    )

    date_occurred = DateField('Date Lost/Found', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired(), Length(10, 500)])
    tags = StringField('Tags (comma-separated, e.g. blue, nike, airpods)')
    photo = FileField('Photo', validators=[
        FileAllowed(['png', 'jpg', 'jpeg', 'webp'], 'Images only.')
    ])
    submit = SubmitField('Submit Report')