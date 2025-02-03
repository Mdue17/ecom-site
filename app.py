import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'placeholder'
db = SQLAlchemy(app)


# might move this to a separate file
class ShopItems(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)
    subtitle = db.Column(db.String(120), nullable=False)  # Removed unique=True
    category = db.Column(db.String(100), nullable=False, default='other')
    sizes = db.Column(db.String(10), nullable=False)
    image_name = db.Column(db.String(100), nullable=False, default='default.jpg')


# with app.app_context():
#     db.drop_all()
#     db.create_all()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/store", methods=['GET', 'POST'])
def store():
    items = ShopItems.query.all()
    return render_template("store.html", products=items)


@app.route('/product/<int:product_id>')
def product(product_id):
    product = ShopItems.query.get(product_id)
    return render_template('product.html', product=product)


@app.route('/store/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        title = request.form['title']
        subtitle = request.form['subtitle']
        category = request.form['category']
        sizes = request.form['sizes']
        image_file = request.files['image_name']

        if image_file and image_file.filename:
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            item = ShopItems(title=title, subtitle=subtitle, category=category, sizes=sizes, image_name=filename)
            db.session.add(item)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('store'))
    else:
        return render_template('add.html')

@app.route('/store/delete/<int:product_id>')
def delete(product_id):
    product = ShopItems.query.get(product_id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('store'))


@app.route('/store/edit/<int:product_id>', methods=['GET', 'POST'])
def edit(product_id):
    product = ShopItems.query.get(product_id)
    if request.method == 'POST':
        product.title = request.form['title']
        product.subtitle = request.form['subtitle']
        product.category = request.form['category']
        product.sizes = request.form['sizes']
        product.image_name = request.form['image_name']
        db.session.commit()
        return redirect(url_for('store'))
    else:
        return render_template('edit.html', product=product)


@app.route("/cart")
def cart():
    return render_template("cart.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
