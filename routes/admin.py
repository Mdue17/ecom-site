from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_login import  login_required, logout_user, current_user, LoginManager

from forms import AddProductForm, AddCategoryForm
from models import db, Category, ShopItems, User
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


@admin_bp.route('/store/add', methods=['GET', 'POST'])
@login_required
@admin_only
def add():
    form = AddProductForm()
    if form.validate_on_submit():

        category_name = form.category.data
        category = Category.query.filter_by(name=category_name).first()

        if category:
            product = ShopItems(
                title=form.title.data,
                subtitle=form.subtitle.data,
                category=category,
                sizes=form.sizes.data,
                price=form.price.data,
                image_name=data_saver(form.image_name.data)
            )
            db_processing(product)
        flash('Product added successfully!', 'success')
        return redirect(url_for('admin.add_product'))

    return render_template('admin/add.html', form=form)

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

@admin_bp.route('/store/add_category', methods=['POST', 'GET'])
@login_required
@admin_only
def add_category():
    """Add a new category to the database"""
    form = AddCategoryForm()

    if form.validate_on_submit():
        if Category.query.filter_by(name=form.name.data).first():
            flash('Category already exists!', 'danger')
            return render_template('admin/add_category.html')
        category = Category(name=form.name.data, description=form.description.data)
        db_processing(category)
        flash('Category added successfully!', 'success')
    return render_template('admin/add_category.html', form=form)


@admin_bp.route('/store/delete/<int:product_id>')
@login_required
@admin_only
def delete(product_id):
    """Delete a product from the store"""
    product = ShopItems.query.get(product_id)
    db_processing(product, False)
    return redirect(url_for('public.store'))





@admin_bp.route('/store/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_only
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

