from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.associationproxy import association_proxy

from config import db

# Models go here!

# models.py
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# User model
class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'customer' or 'seller'

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def repr(self):
        return f"<User {self.username}>"

# Customer model
class Customer(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    phone_no = db.Column(db.Integer)
    #phone = db.Column(db

    user = db.relationship('User', backref=db.backref('customer', uselist=False))

    def repr(self):
        return f"<Customer {self.name}>"

# Seller model
class Seller(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    business_name = db.Column(db.String(100), nullable=False)
    business_email = db.Column(db.String(120), unique=True, nullable=False)
    business_address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), default='pending')
    # phone_no = db.Column(db.Integer)

    user = db.relationship('User', backref=db.backref('seller', uselist=False))

    def repr(self):
        return f"<Seller {self.business_name}>"
    
# Category model
class Category(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Only define the relationship here
    products = db.relationship('Product', backref='category', lazy=True)

    def repr(self):
        return f"<Category {self.name}>"

# Product model
class Product(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('seller.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    seller = db.relationship('Seller', backref=db.backref('products', lazy=True))
    # Remove the duplicate backref here
    # category = db.relationship('Category', backref=db.backref('products', lazy=True))

    def repr(self):
        return f"<Product {self.name}>"


# Order model
class Order(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    order_date = db.Column(db.DateTime, nullable=False)

    customer = db.relationship('Customer', backref=db.backref('orders', lazy=True))
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))

    def repr(self):
        return f"<Order {self.id} - {self.quantity} x {self.product.name}>"
    
# Cart model
class Cart(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    
    customer = db.relationship('Customer', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))

    def repr(self):
        return f"<Cart {self.customer_id} - {self.product_id} ({self.quantity})>"
    

class OrderHistory(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=True)
    total_price = db.Column(db.Float, nullable=True)

    order = db.relationship('Order', backref=db.backref('order_history', lazy=True))
    product = db.relationship('Product', backref=db.backref('order_history', lazy=True))

    def repr(self):
        return f"<OrderHistory {self.order_id} - {self.product_id} ({self.quantity})>"