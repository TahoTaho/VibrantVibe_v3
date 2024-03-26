from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from website.credential import username, password
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

server = 'databasev1.database.windows.net'
database = 'VibrantVibe_Database'
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

from website import routes