# app/extensions.py
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_talisman import Talisman


bcrypt = Bcrypt()
mail   = Mail()
talisman = Talisman()