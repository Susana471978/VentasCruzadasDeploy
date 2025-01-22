from pymongo import MongoClient
from faker import Faker
import random
import pandas as pd

# Conexión a MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]  # Cambia el nombre de la base de datos
customers_table = db["customers"]  # Colección de clientes
products_table = db["products"]  # Colección de productos
categories_table = db["categories"]  # Colección de categorías
orders_table = db["orders"]  # Colección de órdenes

# Instancia de Faker
fake = Faker()

# Crear categorías generales
def create_general_categories():
    general_categories = [
        {"Category ID": idx + 1, "Name": name, "Description": description}
        for idx, (name, description) in enumerate([
            ("Ropa y Moda", "Clothing, fashion, and accessories"),
            ("Parafarmacia y Salud", "Health products and pharmacy"),
            ("Cosmética y Perfumería", "Cosmetics and perfumes"),
            ("Electrónica", "Electronic gadgets and devices"),
            ("Hogar", "Home goods and essentials"),
            ("Jardín y Bricolaje", "Garden tools and DIY products"),
            ("Juguetes", "Toys for children and adults"),
            ("Libros", "Books and reading materials"),
            ("Deportes y Aire Libre", "Sports and outdoor activities"),
            ("Oficina y Papelería", "Office supplies and stationery"),
            ("Joyería", "Jewelry and accessories"),
            ("Alimentación y Bebidas", "Food and beverages"),
            ("Coche y Moto", "Automotive and motorcycle products"),
        ])
    ]
    categories_table.insert_many(general_categories)
    return {category["Name"]: category["Category ID"] for category in general_categories}

# Procesar dataset externo de productos y asignar categorías generales
def process_external_products_with_categories(file_path, general_categories_map):
    data = pd.read_csv(file_path)

    def assign_general_category(category_name):
        mapping = {
            "Ropa y Moda": ["Clothing", "Footwear", "Watches", "Jewelry"],
            "Parafarmacia y Salud": ["Health", "Pharmacy", "Supplements"],
            "Cosmética y Perfumería": ["Cosmetics", "Perfumes", "Beauty"],
            "Electrónica": ["Mobiles", "Laptops", "Tablets", "Cameras", "Headphones"],
            "Hogar": ["Furniture", "Home Decor", "Kitchen", "Bedding"],
            "Jardín y Bricolaje": ["Garden", "Tools", "DIY"],
            "Juguetes": ["Toys", "Games", "Play"],
            "Libros": ["Books", "Novels", "Magazines"],
            "Deportes y Aire Libre": ["Sports", "Fitness", "Outdoor Gear"],
            "Oficina y Papelería": ["Office Supplies", "Stationery", "Desk"],
            "Joyería": ["Jewelry", "Accessories", "Watches"],
            "Alimentación y Bebidas": ["Food", "Beverages", "Snacks"],
            "Coche y Moto": ["Automotive", "Motorcycle", "Car Accessories"],
        }
        for general_category, specific_categories in mapping.items():
            if any(specific in category_name for specific in specific_categories):
                return general_categories_map[general_category]
        return general_categories_map.get("Otros", "Unknown")

    data["Product ID"] = range(1, len(data) + 1)  # IDs secuenciales
    data["Active"] = 1
    data["Name"] = data["product_name"]
    
    def extract_category(category_tree):
        if pd.notna(category_tree) and ">>" in category_tree:
            categories = category_tree.split(">>")
            return categories[1].strip() if len(categories) > 1 else categories[0].strip()
        return "Unknown"

    data["Category"] = data["product_category_tree"].apply(extract_category)
    data["General Category ID"] = data["Category"].apply(assign_general_category)
    data["Price (tax excluded)"] = data["retail_price"]
    data["Tax rules ID"] = [random.randint(1, 5) for _ in range(len(data))]
    data["Wholesale price"] = data["retail_price"] * random.uniform(0.5, 0.8)
    data["On sale"] = data.apply(
        lambda row: 1 if row["retail_price"] > row["discounted_price"] else 0, axis=1
    )
    data["Discount amount"] = data["retail_price"] - data["discounted_price"]
    data["Discount percent"] = (data["Discount amount"] / data["retail_price"]) * 100
    data["Quantity"] = [random.randint(1, 100) for _ in range(len(data))]
    data["Description"] = data["description"]

    # Add random ratings for products (assuming a scale from 1 to 5)
    data["product_rating"] = [random.randint(1, 5) for _ in range(len(data))]

    mapped_products = data[[
        "Product ID", "Active", "Name", "Category", "General Category ID", 
        "Price (tax excluded)", "Tax rules ID", "Wholesale price", 
        "On sale", "Discount amount", "Discount percent", "Quantity", 
        "Description", "product_rating", "image"  # Added image column here
    ]]
    return mapped_products.to_dict(orient="records")

# Generar datos ficticios para clientes
def generate_customers(n):
    customers = []
    for customer_id in range(1, n + 1):  # IDs secuenciales
        title_id = random.choice([1, 2, 0])
        first_name = fake.first_name_male() if title_id == 1 else fake.first_name_female()
        last_name = fake.last_name()
        email = fake.email()
        password = fake.password()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d")
        newsletter = random.choice([0, 1])
        opt_in = random.choice([0, 1])
        registration_date = fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d")
        groups = random.choice(["Customer", "Customer, Carribean", "VIP"])
        default_group_id = random.randint(1, 5)

        customer = {
            "Customer ID": customer_id,
            "Active": 1,
            "Title ID": title_id,
            "Email": email,
            "Password": password,
            "Birthday": birthday,
            "Last Name": last_name,
            "First Name": first_name,
            "Newsletter": newsletter,
            "Opt-in": opt_in,
            "Registration Date": registration_date,
            "Groups": groups,
            "Default Group ID": default_group_id,
        }
        customers.append(customer)
    return customers

# Generar datos ficticios para órdenes
def generate_orders(n, customer_ids, product_ids):
    orders = []
    for _ in range(n):
        order = {
            "Order ID": fake.uuid4(),
            "Customer ID": random.choice(customer_ids),
            "Product ID": random.choice(product_ids),
            "ID Carrier": random.randint(1, 10),
            "ID Lang": random.randint(1, 5),
            "ID Currency": random.randint(1, 3),
            "Total Paid": round(random.uniform(20, 500), 2),
            "Total Products": random.randint(1, 5),
            "Total Shipping": round(random.uniform(5, 50), 2),
            "Payment Method": random.choice(["Credit Card", "PayPal", "Bank Transfer"]),
            "Order Date": fake.date_between(start_date="-5y", end_date="today").strftime("%Y-%m-%d"),
        }
        orders.append(order)
    return orders

# Archivo externo de productos
products_file_path = "/home/reboot-student/code/python/Proyecto-ventas-cruzadas/flipkart_com-ecommerce_sample.csv"

# Crear categorías generales e insertar en la base de datos
general_categories_map = create_general_categories()

# Procesar y cargar productos con categorías generales
processed_products = process_external_products_with_categories(products_file_path, general_categories_map)
products_table.insert_many(processed_products)

# Generar clientes ficticios
num_customers = 100
fake_customers = generate_customers(num_customers)
customers_table.insert_many(fake_customers)

# Generar órdenes ficticias
customer_ids = [customer["Customer ID"] for customer in fake_customers]
product_ids = [product["Product ID"] for product in processed_products]
num_orders = 500
fake_orders = generate_orders(num_orders, customer_ids, product_ids)
orders_table.insert_many(fake_orders)

print(f"Se han insertado {num_customers} clientes ficticios en la colección 'customers'.")
print(f"Se han insertado {len(processed_products)} productos con categorías generales en la colección 'products'.")
print(f"Se han insertado {num_orders} órdenes ficticias en la colección 'orders'.")
print(f"Se han creado 6 categorías generales en la colección 'categories'.")