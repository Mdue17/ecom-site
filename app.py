from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

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


@app.route("/store")
def store():
    return render_template("store.html")


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
