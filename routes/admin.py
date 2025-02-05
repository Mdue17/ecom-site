from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from models import db, Category, ShopItems
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)


def admin_only(func):
    """Restrict access to admin users only"""
    @wraps(func) # Preserve the original function's parameter metadata
    def wrapper(*args, **kwargs):
        if current_user.id != 1: # Admin user id placeholder
            return abort(403)
        return func(*args, **kwargs) # Call the original function
    return wrapper

@admin_only
@login_required
@admin_bp.route('/store/add', methods=['GET', 'POST'])
def add():
    """Add a new product to the store"""
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        category_name = request.form['category']
        sizes = request.form['sizes']
        price = request.form['price']
        image_file = request.files['image_name']


        category = Category.query.filter_by(name=category_name).first() # Get the category object

        if category is None:
            flash('Category does not exist.', 'error')
            return redirect(url_for('admin.add'))

        if image_file and image_file.filename:
            item = ShopItems(title=title, subtitle=subtitle, category=category, sizes=sizes, price=price, image_name=data_saver(image_file))
            db_processing(item)
            flash('Product added successfully!', 'success')
            return redirect(url_for('public.store'))
    else:
        return render_template('admin/add.html', categories=Category.query.all())


def db_processing(item, save_bool=True):
    """Add or delete an item from the database"""
    if save_bool:
        db.session.add(item)
    else:
        db.session.delete(item)
    db.session.commit()

def data_saver(image_file):
    """Save the image file to the server"""
    filename = secure_filename(image_file.filename)
    image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    image_file.save(image_path)
    return filename



def add_category(name, description):
    """Add a new category to the database"""
    category = Category(name=name, description=description)
    db_processing(category)

@admin_only
@login_required
@admin_bp.route('/store/delete/<int:product_id>')
def delete(product_id):
    """Delete a product from the store"""
    product = ShopItems.query.get(product_id)
    db_processing(product, False)
    return redirect(url_for('public.store'))




@admin_only
@login_required
@admin_bp.route('/store/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    """Edit a product in the store"""
    product = ShopItems.query.get(product_id)
    if request.method == 'POST':
        product.title = request.form['title']
        product.subtitle = request.form['subtitle']
        product.category = Category.query.filter_by(name=request.form['category']).first()
        product.sizes = request.form['sizes']
        product.price = request.form['price']
        image_file = request.files['image_name']

        if image_file and image_file.filename:
            product.image_name = data_saver(image_file)

        db_processing(product)
        flash('Product updated successfully!', 'success')
        return redirect(url_for('public.store'))
    else:
        return render_template('admin/edit.html', product=product, categories=Category.query.all())

