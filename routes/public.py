import random

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask import session
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, SignupForm
from models import Category, ShopItems, db, User
from flask_bcrypt import Bcrypt

public_bp = Blueprint('public', __name__)



@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    bcrypt = Bcrypt()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next') #if theres a nxt page
            return redirect(next_page) if next_page else redirect(url_for('public.home'))
        else:
            flash ('Invalid email or password, try again',"error")
    return render_template('public/login.html', form=form)


@public_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    bcrypt = Bcrypt()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()
        flash('Registratired successfully!', 'success')
        return redirect(url_for('public.login'))
    return render_template('public/signup.html', form=form)

@public_bp.route("/logout")
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('public.login'))


@public_bp.route("/")
# @login_required
def home():
    """Home page route"""
    categories = Category.query.all()
    products = ShopItems.query.all()
    random.shuffle(products)
    category_items = {}  # Dictionary to store the image name of the first item in each category
    recent_items = []
    latest_updated_category = Category.query.order_by(Category.last_updated.desc()).all()  # Get the latest updated categories

    for category in latest_updated_category:
        first = ShopItems.query.filter_by(category_id=category.id).first()  # Get the first item in the category
        if first:
            recent_items.append(first)


    for category in categories:
        first_item = ShopItems.query.filter_by(category_id=category.id).first()  # Get the first item in the category
        if first_item:
            category_items[category.id] = first_item.image_name  # Get the image name of the first item
        else:
            category_items[category.id] = 'default.jpg'
    return render_template("public/index.html", categories=categories, category_items=category_items, products=products, recent_items=recent_items)


@public_bp.route("/store", methods=['GET'])
# @login_required
def store():
    """Store page route"""
    category_names = request.args.getlist('category') # Get the category names from the query string
    if category_names:
        categories = Category.query.filter(Category.name.in_(category_names)).all() # Get the category objects
        items = ShopItems.query.filter(ShopItems.category_id.in_([category.id for category in categories])).all() # Get the items in the categories
    else:
        items = ShopItems.query.all()
    categories = Category.query.all()
    return render_template("public/store.html", products=items, categories=categories)


@public_bp.route('/product/<int:product_id>')
def product(product_id):
    product = ShopItems.query.get(product_id)
    category = Category.query.get(product.category_id)
    return render_template('public/product.html', product=product, category=category)


@public_bp.route("/cart")
@login_required
def cart():
    return render_template("public/cart.html")


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")