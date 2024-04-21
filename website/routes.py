from datetime import date
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from website import app, db, bcrypt
from website.forms import RegistrationForm, LoginForm, UpdateAccountForm, UploadForm
from website.models import User, Recipe
from flask_login import login_user, current_user ,logout_user, login_required
from sqlalchemy import desc


@app.route("/")
@app.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.order_by(desc(Recipe.date_posted)).paginate(page=page, per_page=5)
    return render_template('home.html', recipes=recipes)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check your username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account has been successfully created', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def saved_picture(form_picture, folder_name):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/' + folder_name, picture_fn)
    output_sie = (125,125)
    resized_image = Image.open(form_picture)
    resized_image.thumbnail(output_sie)
    resized_image.save(picture_path)

    return picture_fn


@app.route('/account', methods=['GET','POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = saved_picture(form.picture.data, 'profile_pics')
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Account has been updated', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html',
                           title='Account', image_file=image_file, form=form)

@app.route("/recipe/new", methods=['GET','POST'])
@login_required
def new_recipe():
    form = UploadForm()
    if form.validate_on_submit():
        picture_file = saved_picture(form.picture.data, 'recipe_pics')
        recipe = Recipe(name=form.name.data,
                        cuisine=form.cuisine.data,
                        meal_type=form.meal_type.data,
                        dish_type=form.dish_type.data,
                        ingredient=form.ingredient.data,
                        instruction=form.instruction.data,
                        image_file=picture_file,
                        date_posted=date.today(),
                        creator=current_user)
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been uploaded!', 'success')
        return redirect(url_for('home'))
    return render_template('create_recipe.html', title='New Recipe', form=form, legend='New Recipe')

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', title=recipe.name, recipe=recipe)

@app.route("/recipe/<int:recipe_id>/update", methods=['GET','POST'])
@login_required
def update_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.creator != current_user:
        abort(403)

    form = UploadForm()
    if form.validate_on_submit():
        picture_file = saved_picture(form.picture.data, 'recipe_pics')
        recipe.name = form.name.data
        recipe.cuisine = form.cuisine.data
        recipe.dish_type = form.dish_type.data
        recipe.ingredient = form.ingredient.data
        recipe.instruction = form.instruction.data
        recipe.image_file = picture_file
        db.session.commit()
        flash('Your recipe has been update', 'success')
        return redirect(url_for('recipe', recipe_id=recipe.id))

    elif request.method == 'GET':
        form.name.data = recipe.name
        form.cuisine.data = recipe.cuisine
        form.dish_type.data = recipe.dish_type
        form.ingredient.data = recipe.ingredient
        form.instruction.data = recipe.instruction
    return render_template('create_recipe.html', title='Update Recipe', form=form, legend='Update Recipe')

@app.route("/recipe/<int:recipe_id>/delete", methods=['POST'])
@login_required
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    if recipe.creator != current_user:
        abort(403)
    db.session.delete(recipe)
    db.session.commit()
    flash('Your recipe has been deleted', 'success')
    return redirect(url_for('home'))

@app.route('/user/<string:username>')
def user_recipes(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    recipes = Recipe.query.filter_by(creator=user)\
        .order_by(desc(Recipe.date_posted))\
        .paginate(page=page, per_page=5)
    return render_template('user_recipes.html', recipes=recipes, user=user)

@app.route('/user/uploaded_recipes')
def uploaded_recipes():
    page = request.args.get('page', 1, type=int)
    recipes = Recipe.query.filter_by(creator=current_user) \
        .order_by(desc(Recipe.date_posted)) \
        .paginate(page=page, per_page=5)
    return render_template('user_recipes.html', recipes=recipes, user=current_user)