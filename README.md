# 🛒 E-commerce API

## 📌 Overview
This project is a RESTful API built using **Flask, SQLAlchemy, Marshmallow, and MySQL**. It simulates the backend of a simple e-commerce system, allowing users to manage **users, products, and orders**.

The API demonstrates how to design and implement relational databases, handle one-to-many and many-to-many relationships, and build CRUD operations in a real-world backend application.

---

## 🚀 Features

### 👤 Users
- Create a user
- Retrieve all users
- Retrieve a user by ID
- Update a user
- Delete a user

### 📦 Products
- Create a product
- Retrieve all products
- Retrieve a product by ID
- Update a product
- Delete a product

### 🧾 Orders
- Create an order
- Add a product to an order
- Remove a product from an order
- Get all orders for a user
- Get all products in an order

### ⭐ Bonus Features
- Delete an order
- Calculate total cost of an order

---

## 🏗️ Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- Flask-Marshmallow
- Marshmallow
- MySQL

---

## 🗄️ Database Design

This project includes three main models:

### User
- id (Primary Key)
- name
- address
- email (Unique)

### Product
- id (Primary Key)
- product_name
- price

### Order
- id (Primary Key)
- order_date
- user_id (Foreign Key)

### 🔗 Relationships
- A **User** can have many **Orders** (one-to-many)
- An **Order** can have many **Products**
- A **Product** can belong to many **Orders**

A many-to-many relationship between Orders and Products is handled using an **association table (`order_products`)**.

---

## 🔒 Data Validation

Marshmallow is used to:
- Validate user input (email format, required fields)
- Ensure product prices are valid
- Serialize data into JSON responses

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure database
Make sure MySQL is running and create a database:

```bash
CREATE DATABASE ecommerce_api;
```
Update your connection string if needed:
```bash
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://username:password@localhost/ecommerce_api'
```

### 5. Run the application
```bash
python app.py
```

---

## 📡 API Endpoints
### 👤 Users
- ```POST /users```
- ```GET /users```
- ```GET /users/<id>```
- ```PUT /users/<id>```
- ```DELETE /users/<id>```

### 📦 Products
- ```POST /products```
- ```GET /products```
- ```GET /products/<id>```
- ```PUT /products/<id>```
- ```DELETE /products/<id>```

### 🧾 Orders
- ```POST /orders```
- ```PUT /orders/<order_id>/add_product/<product_id>```
- ```DELETE /orders/<order_id>/remove_product/<product_id>```
- ```GET /orders/user/<user_id>```
- ```GET /orders/<order_id>/products```

### ⭐ Bonus
- ```DELETE /orders/<id>```
- ```GET /orders/<order_id>/total_cost```

---

## 🧪 Testing

This API can be tested using **Postman**.

Make sure to:

- Start the Flask server
- Send requests to ```http://127.0.0.1:5000/```

--- 

## 🧠 What I Learned
- Building RESTful APIs using Flask
- Designing relational databases
- Implementing one-to-many and many-to-many relationships
- Using Marshmallow for validation and serialization
- Handling real-world backend logic

--- 

## 🙌 Author

Stephana Pudjowargono
