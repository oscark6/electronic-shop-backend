#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, jsonify
from flask_restful import Resource
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime

# Local imports
from config import app, db, api
from models import User, Customer, Seller, Product, Cart, Order, OrderHistory, Category

# Initialize app components
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Views go here!

@app.route('/')
def index():
    return '<h1>Project Server</h1>'

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify(access_token=access_token), 200

# User registration
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    if not username or not password or not role:
        return jsonify({"message": "Missing required fields"}), 400

    if role not in ['customer', 'seller']:
        return jsonify({"message": "Invalid role specified"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Username already exists!"}), 400

    new_user = User(username=username, role=role)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    if role == 'customer':
        if not all(field in data for field in ['name', 'email', 'address', 'phone_no']):
            return jsonify({"message": "Missing customer details"}), 400
        
        new_customer = Customer(
            user_id=new_user.id,
            name=data.get('name'),
            email=data.get('email'),
            address=data.get('address'),
            phone_no=data.get('phone_no')
        )
        db.session.add(new_customer)

    elif role == 'seller':
        if not all(field in data for field in ['business_name', 'business_email', 'business_address']):
            return jsonify({"message": "Missing seller details"}), 400
        
        if Seller.query.filter_by(business_email=data.get('business_email')).first():
            return jsonify({"message": "Business email already exists!"}), 400

        new_seller = Seller(
            user_id=new_user.id,
            business_name=data.get('business_name'),
            business_email=data.get('business_email'),
            business_address=data.get('business_address')
        )
        db.session.add(new_seller)

    db.session.commit()

    return jsonify({"message": "User registered successfully!"}), 201

@app.route('/categories/products', methods=['GET'])
def get_all_categories_with_products():
    categories = Category.query.all()
    response = []

    for category in categories:
        category_data = {
            'id': category.id,
            'name': category.name,

            # Add any other fields from the Category model that you need
        }
        category_data['products'] = []

        for product in category.products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'image_url': product.image_url,
                # Add any other fields from the Product model that you need
            }
            category_data['products'].append(product_data)

        response.append(category_data)

    return jsonify(response), 200



@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories]), 200

# Route to get products by category id
@app.route('/categories/<int:category_id>/products', methods=['GET'])
def get_products_by_category(category_id):
    products = Product.query.filter_by(category_id=category_id).all()
    return jsonify([product.to_dict() for product in products]), 200

# @app.route('/products')
# def get_products():
#     category = request.args.get('category')
#     if category:
#         products = Product.query.filter_by(category=category).all()
#     else:
#         products = Product.query.all()
#     return jsonify([product.to_dict() for product in products])



@app.route('/seller/products', methods=['GET'])
@jwt_required()
def get_seller_products():
    current_user = get_jwt_identity()
    products = Product.query.filter_by(seller_id=current_user['id']).all()

    product_list = [
        {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "stock": product.stock,
            "image": product.image,
            "category_id": product.category_id
        }
        for product in products
    ]

    return jsonify(product_list), 200

@app.route('/seller/products', methods=['POST'])
@jwt_required()
def add_product():
    data = request.get_json()
    current_user = get_jwt_identity()

    new_product = Product(
        seller_id=current_user['id'],
        name=data['name'],
        description=data['description'],
        price=data['price'],
        stock=data['stock'],
        image=data['image'],
        category_id=data['category_id']
    )
    db.session.add(new_product)
    db.session.commit()

    return jsonify({"message": "Product added successfully", "product_id": new_product.id}), 201

@app.route('/seller/products/<int:id>', methods=['GET'])
@jwt_required()
def seller_product(id):
    product = Product.query.get_or_404(id)
    return jsonify({"id": product.id, "name": product.name, "description": product.description,
                    "price": product.price, "stock": product.stock, "image": product.image,
                    "category_id": product.category_id, "seller_id": product.seller_id}), 200

@app.route('/seller/buyers', methods=['GET'])
@jwt_required()
def seller_buyers():
    current_user = get_jwt_identity()
    seller = Seller.query.filter_by(user_id=current_user['id']).first()
    if not seller:
        return jsonify({'message': 'Seller not found'}), 404

    customers = Customer.query.all()
    customer_list = [{"id": c.id, "name": c.name, "email": c.email, "address": c.address, "phone_no": c.phone_no}
                     for c in customers]

    return jsonify({"buyers": customer_list}), 200

@app.route('/buyers/orders', methods=['GET'])
@jwt_required()
def buyers_orders():
    current_user = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=current_user['id']).first()
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404

    orders = Order.query.filter_by(customer_id=customer.id).all()
    order_list = [
        {
            "id": o.id,
            "product_id": o.product_id,
            "quantity": o.quantity,
            "status": o.status
        }
        for o in orders
    ]
    return jsonify({"orders": order_list}), 200

@app.route('/admin/seller', methods=['GET'])
@jwt_required()
def admin_seller():
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403

    sellers = Seller.query.all()
    seller_list = [
        {
            "id": s.id,
            "business_name": s.business_name,
            "business_email": s.business_email,
            "business_address": s.business_address
        }
        for s in sellers
    ]
    return jsonify({"sellers": seller_list}), 200

@app.route('/admin/seller/<int:id>/decline', methods=['PUT'])
@jwt_required()
def admin_seller_decline(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403

    seller = Seller.query.get_or_404(id)
    db.session.delete(seller)
    db.session.commit()
    return jsonify({'message': 'Seller registration declined'}), 200

@app.route('/admin/seller/<int:id>/approve', methods=['PUT'])
@jwt_required()
def admin_seller_approve(id):
    current_user = get_jwt_identity()
    if current_user['role'] != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 4037

    seller = Seller.query.get_or_404(id)
    seller.status = True  # Assuming status is a boolean field for approval
    db.session.commit()

    return jsonify({'message': 'Seller registration approved'}), 200







# Add a product to the cart
# @app.route('/cart', methods=['POST'])
# @jwt_required()
# def add_to_cart():
#     user_identity = get_jwt_identity()
#     customer = Customer.query.filter_by(user_id=user_identity['id']).first()
#     if not customer:
#         return jsonify({'msg': 'Customer not found'}), 404

#     data = request.get_json()
#     product_id = data.get('productId')
#     quantity = data.get('quantity', 1)

#     product = Product.query.get_or_404(product_id)

#     cart_item = Cart.query.filter_by(customer_id=customer.id, product_id=product.id).first()
#     if cart_item:
#         cart_item.quantity += quantity
#     else:
#         cart_item = Cart(customer_id=customer.id, product_id=product.id, quantity=quantity)
#         db.session.add(cart_item)

#     db.session.commit()

#     return jsonify({'msg': 'Product added to cart', 'cart_item_id': cart_item.id}), 201

@app.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    user_identity = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=user_identity['id']).first()
    if not customer:
        return jsonify({'msg': 'Customer not found'}), 404

    data = request.get_json()
    product_id = data.get('productId')
    quantity = data.get('quantity', 1)  # Default to 1 if not provided

    if not product_id or not quantity:
        return jsonify({'msg': 'Missing productId or quantity'}), 400

    product = Product.query.get_or_404(product_id)

    cart_item = Cart.query.filter_by(customer_id=customer.id, product_id=product.id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = Cart(customer_id=customer.id, product_id=product.id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()

    return jsonify({'msg': 'Product added to cart', 'cart_item_id': cart_item.id}), 201


# Get the current user's cart items
@app.route('/cart/get', methods=['GET'])
@jwt_required()
def get_cart_items():
    user_identity = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=user_identity['id']).first()
    if not customer:
        return jsonify({'msg': 'Customer not found'}), 404

    cart_items = Cart.query.filter_by(customer_id=customer.id).all()
    items = [
        {
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'quantity': item.quantity,
            'price': item.product.price,
            'total': item.quantity * item.product.price,
        }
        for item in cart_items
    ]

    return jsonify({'cart_items': items}), 200

# Remove a product from the cart
@app.route('/cart/<int:id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(id):
    user_identity = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=user_identity['id']).first()
    if not customer:
        return jsonify({'msg': 'Customer not found'}), 404

    cart_item = Cart.query.filter_by(id=id, customer_id=customer.id).first()
    if not cart_item:
        return jsonify({'msg': 'Cart item not found'}), 404

    db.session.delete(cart_item)
    db.session.commit()

    return jsonify({'msg': 'Product removed from cart'}), 200










@app.route('/orders', methods=['POST'])
@jwt_required()
def place_order():
    user_identity = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=user_identity['id']).first()
    if not customer:
        return jsonify({'msg': 'Customer not found'}), 404

    cart_items = Cart.query.filter_by(customer_id=customer.id).all()
    if not cart_items:
        return jsonify({'msg': 'No items in cart'}), 400

    for item in cart_items:
        order = Order(
            customer_id=customer.id,
            product_id=item.product_id,
            quantity=item.quantity,
            status='pending'
        )
        db.session.add(order)
        db.session.delete(item)

    db.session.commit()

    return jsonify({'msg': 'Order placed successfully'}), 201

@app.route('/orders/get', methods=['GET'])
@jwt_required()
def view_orders():
    user_identity = get_jwt_identity()
    customer = Customer.query.filter_by(user_id=user_identity['id']).first()
    if not customer:
        return jsonify({'msg': 'Customer not found'}), 404

    orders = Order.query.filter_by(customer_id=customer.id).all()
    order_list = [
        {
            'order_id': order.id,
            'product_id': order.product_id,
            'quantity': order.quantity,
            'status': order.status
        }
        for order in orders
    ]

    return jsonify({'orders': order_list}), 200

if __name__ == '__main__':
    app.run(port=5555, debug=True)
