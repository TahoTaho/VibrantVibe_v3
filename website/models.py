from flask_login import UserMixin
from website import db, login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'UserAccount'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpeg')
    password = db.Column(db.String(60), nullable=False)
    #recipes = db.relationship('Recipe', backref='creator', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cuisine = db.Column(db.String(50), nullable=False)
    meal_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    ingredient = db.Column(db.Text, nullable=False)
    instruction = db.Column(db.Text, nullable=False)
    time = db.Column(db.Integer, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpeg')
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Recipe('{self.name}', '{self.image_file}', '{self.date_posted}', '{self.cuisine}')"