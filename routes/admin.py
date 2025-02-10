from functools import wraps

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, abort
from flask_bcrypt import Bcrypt
from flask_login import  login_required, logout_user, current_user, LoginManager

from forms import AddProductForm, AddCategoryForm, SignupForm, AddRoleForm
from models import db, Category, ShopItems, User, Activity, Role
import os
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__)


def admin_only(func):
    """Restrict access to admin users only"""
    @wraps(func) # Preserve the original function's parameter metadata
    def wrapper(*args, **kwargs):

        if current_user.role_id != 1 and current_user.id != 1:
            flash('Access denied! Admins only.', 'danger')
            return redirect(url_for('public.login'))
        return func(*args, **kwargs) # Call the original function
    return wrapper



@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@admin_only
def dashboard():

    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    pending_requests = 0  # Adjust based on actual business logic
    recent_activities = Activity.query.order_by(Activity.date.desc()).limit(10).all()
    roles = Role.query.all()
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        active_users=active_users,
        pending_requests=pending_requests,
        recent_activities=recent_activities,
        users= User.query.all(),
        form = SignupForm(),
        role_form = AddRoleForm(),
        roles = reversed(roles),
        user = current_user
    )

@admin_bp.route('/update_role', methods=['POST'])
@login_required
@admin_only
def update_role():
    user_id = request.form.get('user_id')
    new_role_id = request.form.get('role')

    user = User.query.get(user_id)
    new_role = Role.query.get(new_role_id)

    if user and new_role:
        user.role_id = new_role.id  # Correctly update the role_id
        db.session.commit()
        flash(f'Role updated to {new_role.name} for {user.username}', 'success')
    else:
        flash('User or Role not found', 'danger')

    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/add_user', methods=['POST', 'GET'])
@login_required
@admin_only
def add_user():
    bcrypt = Bcrypt()
    form = SignupForm()
    email = form.email.data

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=email,
            password_hash=bcrypt.generate_password_hash(form.password.data).decode(
                "utf-8"
            ),
        )
        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'danger')
            return redirect(url_for('admin.dashboard', form=form))
        db_processing(user)
        log_activity(user, 'User added')
    flash('New user added successfully!', 'success')

    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_only
def delete_user(user_id):
    user = User.query.get(user_id)
    db_processing(user, False)
    flash('User deleted successfully!', 'success')
    log_activity(current_user, f"User {user.username} deleted")
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/add_role', methods=['GET', 'POST'])
@login_required
@admin_only
def add_role():
    form = AddRoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data, description=form.description.data)
        db_processing(role)
        flash('Role added successfully!', 'success')
        log_activity(current_user, f"Role {role.name} added")
    return render_template('admin/add_role.html', role_form=form)

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
            return redirect(url_for('admin.add', form=form, categories=category))

    return render_template('admin/add.html', form=form, categories=Category.query.all(), user=current_user)

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



@admin_bp.route('/store/delete', methods=['GET', 'POST'])
@login_required
@admin_only
def delete():
    search_query = request.args.get('search_query')
    columns = User.__table__.columns.keys()
    product = None

    if search_query:
        product = ShopItems.query.filter_by(title=search_query).first()
        if product:
            db_processing(product, False)
            flash('Product removed successfully!', 'success')
            log_activity(current_user, f"Product {product.title} removed")

        else:
            flash("Product not found", "danger")

    return render_template('admin/delete.html', product=product, categories=Category.query.all(), columns=columns, products=ShopItems.query.all(), user=current_user)





@admin_bp.route('/store/delete/<int:product_id>', methods=['POST', 'GET'])
@login_required
@admin_only
def delete1(product_id):
    """Delete a product from the store"""
    product = ShopItems.query.get(product_id)
    db_processing(product, False)
    flash('Product deleted successfully!', 'success')
    log_activity(current_user, f"Product {product.title} deleted")
    return redirect(url_for('public.store'))





@admin_bp.route('/store/edit', methods=['GET', 'POST'])
@login_required
@admin_only
def edit():
    search_query = request.args.get('search_query')
    form = AddProductForm()
    product = None

    if search_query:
        product = ShopItems.query.filter_by(title=search_query).first()
        if product:
            form.title.data = product.title
            form.subtitle.data = product.subtitle
            form.category.data = product.category
            form.sizes.data = product.sizes
            form.price.data = product.price
        else:
            flash("Product not found", "danger")

    return render_template('admin/edit.html', form=form, product=product, categories=Category.query.all(), user=current_user, roles=Role.query.all())

@admin_bp.route('/admin/update/<int:product_id>', methods=['POST', 'GET'])
def update(product_id):
    form = AddProductForm()
    product = ShopItems.query.get_or_404(product_id)
    category_name = form.category.data
    category = Category.query.filter_by(name=category_name).first()

    product.title = form.title.data
    product.subtitle = form.subtitle.data
    product.category = category
    product.sizes = form.sizes.data
    product.price = form.price.data
    if form.image_name.data:
        product.image_name = data_saver(form.image_name.data)
    db.session.commit()
    flash("Product updated successfully!", "success")
    log_activity(current_user, f"Product {product.title} updated")
    return redirect(url_for('admin.edit'))


def log_activity(user, action):
    activity = Activity(user_id=user.id, action=action)
    db.session.add(activity)
    db.session.commit()


