from flask import Blueprint, render_template, request
from models import Category, ShopItems

public_bp = Blueprint('public', __name__)


@public_bp.route("/")
def home():
    """Home page route"""
    categories = Category.query.all()
    category_items = {} # Dictionary to store the image name of the first item in each category
    for category in categories:
        first_item = ShopItems.query.filter_by(category_id=category.id).first() # Get the first item in the category
        if first_item:
            category_items[category.id] = first_item.image_name # Get the image name of the first item
        else:
            category_items[category.id] = 'default.jpg'
    return render_template("public/index.html", categories=categories, category_items=category_items)



@public_bp.route("/store", methods=['GET'])
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
    return render_template('public/product.html', product=product)


@public_bp.route("/cart")
def cart():
    return render_template("public/cart.html")


@public_bp.route("/about")
def about():
    return render_template("public/about.html")


@public_bp.route("/contact")
def contact():
    return render_template("public/contact.html")