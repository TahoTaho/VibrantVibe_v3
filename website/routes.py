from datetime import date
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from website import app, db, bcrypt, mail
from website.forms import RegistrationForm, LoginForm, UpdateAccountForm, UploadForm, ResetPasswordForm, RequestResetForm
from website.models import User, Recipe
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc
from flask_mail import Message


@app.route("/")
@app.route('/home')
def home():
    recipes = Recipe.query.order_by(desc(Recipe.date_posted)).limit(2).all()
    return render_template('home.html', recipes=recipes)

@app.route('/recipes/all')
def recipes():
    recipes = Recipe.query.order_by(desc(Recipe.date_posted)).all()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipes/meal-typle/breakfast')
def recipes_breakfast():
    recipes = Recipe.query.filter_by(meal_type='breakfast').order_by(desc(Recipe.date_posted)).all()
    return render_template('recipe_filter.html', recipes=recipes, title="Breakfast")

@app.route('/recipes/meal-typle/lunch')
def recipes_lunch():
    recipes = Recipe.query.filter_by(meal_type='lunch').order_by(desc(Recipe.date_posted)).all()
    return render_template('recipe_filter.html', recipes=recipes, title="Lunch")

@app.route('/recipes/meal-typle/merienda')
def recipes_merienda():
    recipes = Recipe.query.filter_by(meal_type='merienda').order_by(desc(Recipe.date_posted)).all()
    return render_template('recipe_filter.html', recipes=recipes, title="Merienda")

@app.route('/recipes/meal-typle/dinner')
def recipes_dinner():
    recipes = Recipe.query.filter_by(meal_type='dinner').order_by(desc(Recipe.date_posted)).all()
    return render_template('recipe_filter.html', recipes=recipes, title="Dinner")

@app.route('/recipes/meal-typle/beverages')
def recipes_beverages():
    recipes = Recipe.query.filter_by(meal_type='beverages').order_by(desc(Recipe.date_posted)).all()
    return render_template('recipe_filter.html', recipes=recipes, title="Beverages")

@app.route('/recipes/cuisine/american')
def recipes_american():
    recipes = Recipe.query.filter_by(cuisine='american').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes, title="American Cuisine")

@app.route('/recipes/cuisine/filipino')
def recipes_filipino():
    recipes = Recipe.query.filter_by(cuisine='filipino').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes, title="Filipino Cuisine")

@app.route('/recipes/cuisine/indian')
def recipes_indian():
    recipes = Recipe.query.filter_by(cuisine='indian').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes, title="Indian Cuisine")

@app.route('/recipes/cuisine/japanese')
def recipes_japanese():
    recipes = Recipe.query.filter_by(cuisine='japanese').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes, title="Japanese Cuisine")

@app.route('/recipes/cuisine/korean')
def recipes_korean():
    recipes = Recipe.query.filter_by(cuisine='korean').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes, title="Korean Cuisine")

@app.route('/recipes/user-type/casual')
def recipes_casual():
    recipes = Recipe.query.filter_by(user_type='casual').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes)

@app.route('/recipes/user-type/bodybuilding')
def recipes_bodybuilding():
    recipes = Recipe.query.filter_by(user_type='bodybuilding').order_by(desc(Recipe.date_posted)).all()
    return render_template('user_type.html', recipes=recipes)

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
    output_sie = (1000,1000)
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
        current_user.username = form.username.data.strip()
        current_user.email = form.email.data.strip()
        db.session.commit()
        flash('Account has been updated', 'success')
        return redirect(url_for('account'))

    elif request.method == 'GET':
        form.username.data = current_user.username.strip()
        form.email.data = current_user.email.strip()
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)

    recipes = Recipe.query.filter_by(creator=current_user) \
        .order_by(desc(Recipe.date_posted))
    return render_template('account.html',
                           title='Account', image_file=image_file, form=form, recipes=recipes)

@app.route("/recipe/new", methods=['GET','POST'])
@login_required
def new_recipe():
    form = UploadForm()
    if form.validate_on_submit():
        picture_file = saved_picture(request.files['food-photo'], 'recipe_pics')
        recipe = Recipe(name=form.name.data,
                        cuisine=request.form['cuisine'],
                        meal_type=request.form['meal-type'],
                        dish_type=request.form['dish-type'],
                        user_type=request.form['user-type'],
                        protein=request.form.get('protein'),  # This can be None
                        calories=request.form.get('calories'),  # This can be None
                        affordability=request.form.get('affordability'),  # This can be None
                        difficulty=request.form.get('difficulty'), # This can be None
                        ingredients=form.ingredient.data,
                        instructions=form.instruction.data,
                        image_file=picture_file,
                        date_posted=date.today(),
                        creator=current_user)
        db.session.add(recipe)
        db.session.commit()
        flash('Your recipe has been uploaded!', 'success')
        return redirect(url_for('recipes'))
    else:
        print("Form not validated")  # Debug statement
        print(form.errors)  # Debug statement to print form errors
    return render_template('create_recipe.html', title='New Recipe', form=form)

@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe_detail.html', title=recipe.name, recipe=recipe)

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
        recipe.ingredients = form.ingredient.data
        recipe.instructions = form.instruction.data
        recipe.image_file = picture_file
        db.session.commit()
        flash('Your recipe has been update', 'success')
        return redirect(url_for('recipe', recipe_id=recipe.id))

    elif request.method == 'GET':
        form.name.data = recipe.name
        form.cuisine.data = recipe.cuisine
        form.dish_type.data = recipe.dish_type
        form.ingredient.data = recipe.ingredients
        form.instruction.data = recipe.instructions
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

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='noreplydemo.com', recipients=[user.email])
    msg.body = f'''
    To reset your password, visit the following link 
{url_for('reset_token', token=token, _external=True)}
    If you did not make this request then ignore this email
    '''
    mail.send(msg)


@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET','POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)