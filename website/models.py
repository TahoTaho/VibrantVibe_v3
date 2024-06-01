from flask_login import UserMixin
from website import db, login_manager, app
from datetime import datetime
from itsdangerous import URLSafeTimedSerializer as Serializer

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'ACCOUNTS'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpeg')
    password = db.Column(db.String(60), nullable=False)
    recipes = db.relationship('Recipe', backref='creator', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}, salt='reset_token')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Recipe(db.Model):
    __tablename__ = 'RECIPES'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(50), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    dish_type = db.Column(db.String(50), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    date_posted = db.Column(db.Date, nullable=False, default=datetime.utcnow().date())
    user_id = db.Column(db.Integer, db.ForeignKey('ACCOUNTS.id'), nullable=False)

    def __repr__(self):
        return f"Recipe('{self.name}', '{self.image_file}', '{self.date_posted}', '{self.cuisine}')"


