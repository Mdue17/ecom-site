from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Category, ShopItems
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)

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
            # Save the image file
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(admin_bp.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            item = ShopItems(title=title, subtitle=subtitle, category=category, sizes=sizes, price=price, image_name=filename)
            db.session.add(item)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('public.store'))
    else:
        return render_template('admin/add.html', categories=Category.query.all())


@admin_bp.route('/store/delete/<int:product_id>')
def delete(product_id):
    """Delete a product from the store"""
    product = ShopItems.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('public.store'))


@admin_bp.route('/store/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    """Edit a product in the store"""
    product = ShopItems.query.get(product_id)
    if request.method == 'POST':
        product.title = request.form['title']
        product.subtitle = request.form['subtitle']
        product.category = request.form['category']
        product.sizes = request.form['sizes']
        product.image_name = request.form['image_name']
        db.session.commit()
        return redirect(url_for('public.store'))
    else:
        return render_template('admin/edit.html', product=product)

