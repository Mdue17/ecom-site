import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager
from werkzeug.utils import secure_filename
from routes.admin import admin_bp
from routes.public import public_bp
from models import db, Category, ShopItems, User

app = Flask(__name__)

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'placeholder'


db.init_app(app)

#init flask-login
login_manager  = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "public.login"

#load user for session manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)


with app.app_context():
    db.create_all()  # Create all tables in the correct order

    # Add initial data
    if not Category.query.first():
        db.session.add(Category(name='Combos', description='Perfectly Paired. Effortlessly Stylish.'))
        db.session.add(Category(name='Merch', description='Streetwear That Speaks.'))
        db.session.add(Category(name='Pants', description='Perfect Paired. Effortlessly Stylish.'))
        db.session.commit()





if __name__ == "__main__":
    app.run(debug=True)
