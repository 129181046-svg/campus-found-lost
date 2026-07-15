# app/auth/forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, ValidationError
)
from flask import current_app

# -------------------------------------------------------------------------
# ALLOWED DEPARTMENTS
# -------------------------------------------------------------------------
DEPARTMENTS = [
    ("", "-- Select Department --"),
    ("ARS",  "Aerospace Engineering"),
    ("BIE",  "Bio Engineering"),
    ("BIOINFO",  "Bioinformatics"),
    ("BIO",  "Biotechnology"),
    ("CHEM",  "Chemical Engineering"),
    ("CIV",  "Civil Engineering"),
    ("CSE",  "Computer Science & Engineering"),
    ("CSE",  "Computer Science & Engineering (AI&DS)"),
    ("CSE",  "Computer Science & Engineering (Cyber Security & Blockchain)"),
    ("CSE",  "Computer Science & Engineering (IOT & AUTOMATION)"),
    ("CSE",  "Computer Science & Engineering (Networks)"),    
    ("ECE",  "Electronics & Communication"),
    ("EEE",  "Electrical & Electronics"),
    ("EIE",  "Electronics & Instrumentation Engineering"),
    ("RAI",  "Robotics & Artificial Intelligence"),
    ("ECOME",  "Electronics & Computer Engineering"),
    ("MECH", "Mechanical Engineering"),
    ("IEM",  "Industrial Engineering & Management"),
    ("Mechatronics",  "Mechatronics Engineering"),
    ("IT",   "Information Technology"),
    ("MedNano",  "Medical Nanotechnology"),
    ("B.A.LLB",  "B.A.LLB"),
    ("B.COM.LLB",  "B.COM.LLB"),
    ("B.B.A.LLB",  "B.B.A.LLB"),
    ("SASHE",  "School of ARTS & SCIENCE, HUMANITIES & EDUCATION")
]

# -------------------------------------------------------------------------
# REGISTRATION FORM
# -------------------------------------------------------------------------
class RegistrationForm(FlaskForm):

    name = StringField("Full Name", validators=[
        DataRequired(message="Name is required."),
        Length(min=3, max=80, message="Name must be between 3 and 80 characters."),
    ])

    roll_no = StringField("Register Number", validators=[
        DataRequired(message="Register number is required."),
        Length(min=5, max=20, message="Enter a valid register number."),
    ])

    department = SelectField("Department", choices=DEPARTMENTS, validators=[
        DataRequired(message="Please select your department."),
    ])

    email = StringField("SASTRA Email", validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address."),
        Length(max=120),
    ])

    phone = StringField("Phone Number", validators=[
        DataRequired(message="Phone number is required."),
        Length(min=10, max=15, message="Enter a valid phone number."),
    ])

    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
        Length(min=8, message="Password must be at least 8 characters."),
    ])

    confirm_password = PasswordField("Confirm Password", validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo("password", message="Passwords do not match."),
    ])

    submit = SubmitField("Create Account")

    def validate_email(self, email):
        if not email.data.lower().endswith('@sastra.ac.in'):
            raise ValidationError('Only SASTRA University email addresses (@sastra.ac.in) are allowed.')
        try:
            existing = current_app.db.users.find_one({'email': email.data.lower()})
            if existing:
                raise ValidationError('This email is already registered.')
        except ValidationError:
            raise
        except Exception:
            pass

    def validate_roll_no(self, roll_no):
        try:
            existing = current_app.db.users.find_one(
                {"roll_no": roll_no.data.strip().upper()}
            )
            if existing:
                raise ValidationError(
                    "This register number is already registered."
                )
        except ValidationError:
            raise
        except Exception:
            pass

    def validate_phone(self, phone):
        if not phone.data.isdigit():
            raise ValidationError("Phone number must contain digits only.")


# -------------------------------------------------------------------------
# LOGIN FORM
# -------------------------------------------------------------------------
class LoginForm(FlaskForm):

    email = StringField("SASTRA Email", validators=[
        DataRequired(message="Email is required."),
        Email(message="Enter a valid email address."),
    ])

    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required."),
    ])

    submit = SubmitField("Log In")