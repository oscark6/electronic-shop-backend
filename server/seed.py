#!/usr/bin/env python3

from app import app
from models import db, User, Customer, Seller, Product, Order, Category
import random
from faker import Faker

from datetime import datetime

fake = Faker()

# Updated product details with electronic devices
product_names = [
    "iPhone 13", "Samsung Galaxy S21", "MacBook Pro", "Dell XPS 13", "Apple Watch Series 7",
    "iPad Pro", "Surface Laptop 4", "Sony WH-1000XM4", "Bose QC35 II", "Canon EOS R5",
    "Samsung QLED TV", "HP Envy 6055 Printer", "Asus ROG Gaming Laptop", "Amazon Echo Dot", 
    "Google Nest Hub", "Razer DeathAdder Mouse", "Logitech MX Master 3", "Anker PowerCore 20100", 
    "WD My Passport SSD", "Tile Pro Bluetooth Tracker"
]

product_descriptions = [
    "Latest model with A15 Bionic chip and advanced dual-camera system.",
    "High-end Android smartphone with dynamic AMOLED display.",
    "High-performance laptop with M1 chip and Retina display.",
    "Ultra-thin laptop with 11th Gen Intel Core processor.",
    "Smartwatch with fitness tracking and cellular connectivity.",
    "High-resolution tablet with Liquid Retina display.",
    "Sleek laptop with AMD Ryzen processor and touch display.",
    "Industry-leading noise-canceling headphones with superior sound.",
    "Wireless headphones with top-notch noise cancellation.",
    "Mirrorless camera with 45MP full-frame sensor.",
    "4K QLED TV with vibrant colors and smart features.",
    "All-in-one printer with wireless printing and scanning.",
    "Powerful gaming laptop with NVIDIA RTX graphics.",
    "Smart speaker with Alexa and improved sound quality.",
    "Smart display with Google Assistant and home control.",
    "Ergonomic gaming mouse with customizable buttons.",
    "Advanced wireless mouse with precision and comfort.",
    "High-capacity power bank with fast charging.",
    "Portable SSD with high-speed data transfer.",
    "Bluetooth tracker with long-range and loud ring."
]

image_paths = [
    "https://media.wired.com/photos/61439ca1ea5305148f36968a/1:1/w_1211,h_1211,c_limit/Gear-iphone13_sierra_blue__2bovafkl4yaa_large_2x.jpg",
      "https://phonesstorekenya.com/wp-content/uploads/2021/03/Samsung-S21-FE-5G-b.jpg", 
      "https://www.apple.com/newsroom/images/product/mac/standard/Apple-MacBook-Pro-M2-Pro-and-M2-Max-hero-230117_Full-Bleed-Image.jpg.large.jpg", 
    "https://cdn.vox-cdn.com/thumbor/JDumhAK18Dujmv5JwB13N7EGa1I=/0x0:2040x1360/2000x1333/filters:focal(1020x680:1021x681)/cdn.vox-cdn.com/uploads/chorus_asset/file/24432609/236524_Dell_XPS_13_AKrales_0016.jpg", 
    "https://www.apple.com/newsroom/images/product/watch/standard/Apple_watch-series7_hero_09142021_big.jpg.slideshow-xlarge_2x.jpg",
      "https://www.phoneplacekenya.com/wp-content/uploads/2024/07/Apple-iPad-Pro-11-2024-b.jpg", 
    "https://assets2.razerzone.com/images/pnx.assets/6173ae46054c0c98f5bbf4480679b006/deathadder-essential-available-in-mobile.jpg", 
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRBnsudept4CMwnvbmQynw5q3L8mxHTXifkfA&s",
      "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQTrGQPr2KwTVhPV1efWWwrXCfs_2FzU0nU1Q&s",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQlVLfXpyBua_8xYW8Gje_z7YJ6choso4RteA&s",
      "https://melcom.com/media/catalog/product/cache/d0e1b0d5c74d14bfa9f7dd43ec52d082/1/1/113300_1.jpg", 
      "https://www.hp.com/gb-en/shop/Html/Merch/Images/c07035233_1750x1285.jpg",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQK5AE71Ll3Scp7W1uQ-5uZbESd2yy2b_tHrg&s",
      "https://le.co.ke/wp-content/uploads/2022/04/amazon_echo_dot_3rd_gen_template_255bd639-3cf6-4915-9b8f-a1bef6dcdeb1_1500x.jpg",
        "https://storage.googleapis.com/support-kms-prod/cvw0X96zBdApRadBDbYYf1OC8oQBqq5E8oBl",
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6BYftWjO21l-lEErc52PjLmOLoyWD-DsaNg&s",
      "https://i.rtings.com/assets/products/25W0iOu9/logitech-mx-master-2s/design-medium.jpg?format=auto",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ8uhkHEN1ZUk8jVpsVM-hGDNrNjSs_aiVwBA&s",
    "https://5.imimg.com/data5/ANDROID/Default/2023/1/SZ/UD/ZA/126788677/product-jpeg-500x500.jpg", 
    "https://m.media-amazon.com/images/I/51XdMjYkzLL.jpg"
]

def add_user(username, password, role):
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"User with username {username} already exists. Skipping.")
        return existing_user
    else:
        user = User(username=username, role=role)
        user.set_password(password)  # Ensure this uses a valid hash method
        db.session.add(user)
        db.session.commit()
        print(f"User {username} added successfully.")
        return user

if __name__ == '__main__':
    with app.app_context():
        print("Starting seed...")

        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        print("All tables dropped successfully.")

        # Recreate all tables
        print("Creating tables...")
        db.create_all()
        print("Tables created successfully.")

        # Add Admin User
        try:
            admin_username = 'admin'
            admin_password = 'admin_password'  # Use a strong password in production
            add_user(admin_username, admin_password, 'admin')
        except Exception as e:
            print(f"Error adding admin user: {e}")
            db.session.rollback()

        # Add Regular Users (both customers and sellers)
        try:    
            for i in range(5):
                # Add Customers
                username = fake.user_name()
                password = fake.password()
                user = add_user(username, password, 'customer')
                
                existing_customer = Customer.query.filter_by(user_id=user.id).first()
                if existing_customer:
                    print(f"Customer record for user {username} already exists. Skipping.")
                    continue
                
                customer = Customer(
                    user_id=user.id,
                    name=fake.name(),
                    email=fake.email(),
                    address=fake.address(),
                    phone_no=fake.phone_number()
                )
                db.session.add(customer)

            for i in range(5):
                # Add Sellers
                username = fake.user_name()
                password = fake.password()
                user = add_user(username, password, 'seller')

                existing_seller = Seller.query.filter_by(user_id=user.id).first()
                if existing_seller:
                    print(f"Seller record for user {username} already exists. Skipping.")
                    continue

                seller = Seller(
                    user_id=user.id,
                    business_name=fake.company(),
                    business_email=fake.company_email(),
                    business_address=fake.address(),
                )
                db.session.add(seller)

            db.session.commit()
            print("Users, customers, and sellers added successfully.")
        except Exception as e:
            print(f"Error adding users: {e}")
            db.session.rollback()

        # Add Categories
        try:
            categories = ['Electronics', 'Home Appliances', 'Smart Devices', 'Wearable Tech', 'Computers & Accessories']
            category_objects = []
            for category in categories:
                new_category = Category(name=category)
                db.session.add(new_category)
                category_objects.append(new_category)
            db.session.commit()
            print("Categories added successfully.")
        except Exception as e:
            print(f"Error adding categories: {e}")
            db.session.rollback()

        # Add Products
        try:
            sellers = Seller.query.all()
            for i in range(len(product_names)):
                seller = random.choice(sellers)
                category = random.choice(category_objects)
                name = product_names[i]
                description = product_descriptions[i]
                price = round(random.uniform(10.0, 1000.0), 2)
                stock = random.randint(1, 100)
                image_url = image_paths[i]

                product = Product(
                    seller_id=seller.id, 
                    name=name, 
                    description=description, 
                    price=price, 
                    stock=stock, 
                    image_url=image_url,
                    category_id=category.id
                )
                db.session.add(product)

            db.session.commit()
            print("Products added successfully.")
        except Exception as e:
            print(f"Error adding products: {e}")
            db.session.rollback()

        # Add Orders
        try:
            customers = Customer.query.all()
            products = Product.query.all()
            for i in range(30):
                customer = random.choice(customers)
                product = random.choice(products)
                quantity = random.randint(1, 5)
                total_price = round(product.price * quantity, 2)
                order_date = datetime.now()

                order = Order(
                    customer_id=customer.id, 
                    product_id=product.id, 
                    quantity=quantity, 
                    total_price=total_price, 
                    order_date=order_date
                )
                db.session.add(order)

            db.session.commit()
            print("Orders added successfully.")
        except Exception as e:
            print(f"Error adding orders: {e}")
            db.session.rollback()
