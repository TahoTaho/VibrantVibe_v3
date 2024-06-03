import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from website.credential import username, password
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

server = 'vibrantvibeserver.database.windows.net'
database = 'DB_VibrantVibe'
connection_string = f'mssql+pymssql://{username}:{password}@{server}/{database}?charset=utf8'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'SSSAAAA'
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = credential.email
app.config['MAIL_PASSWORD'] = credential.email_pass
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@yourdomain.com'
mail = Mail(app)

from website import routes