from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    """Model for Users in db"""
    id = db.Column(db.Interger, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def chech_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    """Model for the categories table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    items = db.relationship('ShopItems', backref='category', lazy=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ShopItems(db.Model):
    """Model for the shop_items table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)
    subtitle = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    sizes = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    image_name = db.Column(db.String(100), nullable=False, default='default.jpg')
