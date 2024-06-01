from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import InputRequired,  Length, Email, EqualTo, ValidationError
from website.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[InputRequired(), Email(check_deliverability=True)])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=2,max=20)])
    email = StringField('Email', validators=[InputRequired(), Email(check_deliverability=True)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data.strip() != current_user.username.strip():
            print(username.data != current_user.username)
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one')

    def validate_email(self, email):
        if email.data.strip() != current_user.email.strip():
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one')

class UploadForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    cuisine = RadioField('Cuisine', choices=["Italian", "Indian", "Mexican", "Japanese"], validators=[InputRequired()])
    meal_type = RadioField('Meal Type', choices=["Snack", "Breakfast", "Lunch", "Dinner"], validators=[InputRequired()])
    dish_type = RadioField('Dish Type', choices=["Pasta", "Salad", "Curry", "Dessert"], validators=[InputRequired()])
    ingredient = TextAreaField('Ingredients', validators=[InputRequired()])
    instruction = TextAreaField('Instructions', validators=[InputRequired()])
    picture = FileField('Dish Image', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Upload Recipe')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('This email doesnt exist. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')