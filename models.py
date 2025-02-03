from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    """Model for the categories table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(200), nullable=True)
    items = db.relationship('ShopItems', backref='category', lazy=True)

class ShopItems(db.Model):
    """Model for the shop_items table"""
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(20), nullable=False)
    subtitle = db.Column(db.String(120), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    sizes = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    image_name = db.Column(db.String(100), nullable=False, default='default.jpg')
