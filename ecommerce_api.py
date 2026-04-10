from __future__ import annotations
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import Integer, Table, Column, String, Float, ForeignKey, DateTime, func, select
from marshmallow import ValidationError, fields, validate
from typing import List
from datetime import datetime
import os

# Initialize Flask app
app = Flask(__name__)

# Configure MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:<password>@localhost/ecommerce_api'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Creating Base Model
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy(model_class=Base)
db.init_app(app)
ma = Marshmallow(app)

# Create assocation table for many-to-many relationship between Orders and Products
order_products = Table('order_products', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)

# Create User model with relationships
class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    orders: Mapped[List[Order]] = relationship(back_populates='user', cascade='all, delete-orphan')
    
# Create Product model with relationships
class Product(Base):
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    orders: Mapped[List[Order]] = relationship(secondary='order_products', back_populates='products')

# Create Order model with relationships
class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    
    user: Mapped[User] = relationship(back_populates='orders')
    products: Mapped[List[Product]] = relationship(secondary='order_products', back_populates='orders')
    
# Create User, PRoduct and Order schema for serialization
class UserSchema(ma.SQLAlchemyAutoSchema):
    # Adding validation to the fields in the UserSchema
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    address = fields.String(required=True, validate=validate.Length(min=1, max=200))
    email = fields.Email(required=True, validate=validate.Length(max=100))
    
    class Meta:
        model = User
        load_instance = False # Set to False to return a dictionary instead of a User instance when deserializing
        
class ProductSchema(ma.SQLAlchemyAutoSchema):
    # Adding validation to the fields in the ProductSchema
    product_name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    
    class Meta:
        model = Product
        load_instance = False
    
class OrderSchema(ma.SQLAlchemyAutoSchema):
    user_id = fields.Integer(required=True, validate=validate.Range(min=1))
    order_date = fields.DateTime(required=False) # Optional field, will default to current date and time if not provided
    
    class Meta:
        model = Order
        include_fk = True # Include foreign key fields in the schema
        load_instance = False 
        
# Initialize schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True) # Can be used to serialize mulitple users

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

## Create API endpoints for CRUD operations on Users, Products and Orders ##

## User Endpoints ##

# Create a new user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_user = User(
        name=user_data['name'],
        address=user_data['address'],
        email=user_data['email']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return user_schema.jsonify(new_user), 201

# Get all users
@app.route('/users', methods=['GET'])
def get_users():
    query = select(User)
    users = db.session.execute(query).scalars().all()
    
    return users_schema.jsonify(users), 200

# Get a user by ID
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return user_schema.jsonify(user), 200

# Update a user by ID
@app.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'Invalid user ID'}), 404
    
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    user.name = user_data['name']
    user.address = user_data['address']
    user.email = user_data['email']
    
    db.session.commit()
    return user_schema.jsonify(user), 200

# Delete a user by ID
@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = db.session.get(User, id)
    if not user:
        return jsonify({'message': 'Invalid user ID'}), 404
    
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': f'User with ID {id} has been successfully deleted'}), 200

## Product Endpoints ## 

# Create a new product
@app.route('/products', methods=['POST'])
def create_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(
        product_name=product_data['product_name'],
        price=product_data['price']
    )
    
    db.session.add(new_product)
    db.session.commit()
    
    return product_schema.jsonify(new_product), 201

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    products = db.session.execute(query).scalars().all()
    
    return products_schema.jsonify(products), 200

# Get a product by ID
@app.route('/products/<int:id>', methods=['GET'])
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Product not found'}), 404
    
    return product_schema.jsonify(product), 200

# Update a product by ID
@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Invalid product ID'}), 404
    
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    product.product_name = product_data['product_name']
    product.price = product_data['price']
    
    db.session.commit()
    return product_schema.jsonify(product), 200

# Delete a product by ID
@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({'message': 'Invalid product ID'}), 404
    
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': f'Product with ID: {id} has been successfully deleted'}), 200

## Order Endpoints ##

# Create a new order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    user = db.session.get(User, order_data['user_id'])
    if not user:
        return jsonify({'message': 'Invalid user ID'}), 404
    
    new_order = Order(
        user_id=order_data['user_id'],
        order_date=order_data.get('order_date', datetime.now())
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    return order_schema.jsonify(new_order), 201

# Add products to an order 
@app.route('/orders/<int:order_id>/add_product/<int:product_id>', methods=['PUT'])
def add_product_to_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Invalid order ID'}), 404
    
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Invalid product ID'}), 404
    
    if product in order.products:
        return jsonify({'message': f'{product.product_name} with ID: {product_id} is already in order: {order_id}'}), 400
    
    order.products.append(product)
    db.session.commit()
    return jsonify({'message': f'{product.product_name} with ID: {product_id} has been added to order: {order_id}'}), 200

# Get all orders for a user
@app.route('/orders/user/<int:user_id>', methods=['GET'])
def get_user_orders(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'Invalid user ID'}), 404
    
    orders = user.orders
    return orders_schema.jsonify(orders), 200

# Get all products in an order
@app.route('/orders/<int:order_id>/products', methods=['GET'])
def get_order_products(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Invalid order ID'}), 404

    products = order.products
    return products_schema.jsonify(products), 200

# Remove a product from an order
@app.route('/orders/<int:order_id>/remove_product/<int:product_id>', methods=['DELETE'])
def remove_product_from_order(order_id, product_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Invalid order ID'}), 404
    
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({'message': 'Invalid product ID'}), 404
    
    if product not in order.products:
        return jsonify({'message': f'{product.product_name} with ID: {product_id} is not in order: {order_id}'}), 404
    
    order.products.remove(product)
    db.session.commit()
    return jsonify({'message': f'{product.product_name} with ID: {product_id} has been removed from order: {order_id}'}), 200

## BONUS ## 
# Delete an order by ID
@app.route('/orders/<int:id>', methods=['DELETE'])
def delete_entire_order(id):
    order = db.session.get(Order, id)
    if not order:
        return jsonify({'message': 'Invalid order ID'}), 404
    
    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': f'Order: {id} has been successfully deleted'}), 200

# Get total cost of an order
@app.route('/orders/<int:order_id>/total_cost', methods=['GET'])
def get_order_total_cost(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({'message': 'Invalid order ID'}), 404
    
    total_cost = sum(product.price for product in order.products)
    return jsonify({'order_id': order_id, 'total_cost': total_cost}), 200


# Run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create tables in the database
        
    app.run(debug=True)
