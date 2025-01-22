import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
import numpy as np
from pymongo import MongoClient
from datetime import datetime
import random
import pickle

# MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["my_database"]
    products_collection = db["products"]
    orders_collection = db["orders"]
    print("Connected to MongoDB successfully!")
    
    # Load products data
    print("Loading products data...")
    products_data = pd.DataFrame(list(products_collection.find(
        {},
        {
            'Product ID': 1,
            'Name': 1, 
            'Description': 1,
            'Category': 1,
            'Price (tax excluded)': 1,
            'product_rating': 1,
            'image': 1,
            '_id': 0
        }
    )))
    
    # Load orders data
    print("Loading orders data...")
    orders_data = pd.DataFrame(list(orders_collection.find(
        {},
        {
            'Order ID': 1,
            'Customer ID': 1,
            'Product ID': 1,
            'Total Products': 1,
            'Order Date': 1,
            '_id': 0
        }
    )))
    
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

def calculate_popularity_score(products_data, orders_data):
    # Convert Order Date to datetime
    orders_data['Order Date'] = pd.to_datetime(orders_data['Order Date'])
    
    # Calculate days since order
    current_date = datetime.now()
    orders_data['days_since_order'] = (current_date - orders_data['Order Date']).dt.days
    
    # Calculate time decay factor (exponential decay)
    orders_data['time_weight'] = np.exp(-0.001 * orders_data['days_since_order'])
    
    # Calculate product popularity metrics
    popularity_metrics = orders_data.groupby('Product ID').agg({
        'Order ID': 'count',  # Number of orders
        'Total Products': 'sum',  # Total quantity sold
        'time_weight': 'mean'  # Average time weight
    }).reset_index()
    
    # Normalize metrics
    for column in ['Order ID', 'Total Products']:
        popularity_metrics[f'{column}_normalized'] = popularity_metrics[column] / popularity_metrics[column].max()
    
    # Calculate final popularity score
    popularity_metrics['popularity_score'] = (
        0.4 * popularity_metrics['Order ID_normalized'] +
        0.4 * popularity_metrics['Total Products_normalized'] +
        0.2 * popularity_metrics['time_weight']
    )
    
    return popularity_metrics[['Product ID', 'popularity_score']]

# Calculate popularity metrics
print("Calculating popularity scores...")
popularity_metrics = calculate_popularity_score(products_data, orders_data)

# Prepare data for recommendation system
product_details_df = products_data.copy()
data = products_data.copy()
data.rename(columns={
    'Name': 'product_name',
    'product_rating': 'rating'
}, inplace=True)

# Drop rows with missing ratings
data = data.dropna(subset=['rating'])

# Encode product names
product_encoder = LabelEncoder()
data['product_id'] = product_encoder.fit_transform(data['product_name'])

# Create user-item interaction matrix
print("Creating user-item interaction matrix...")
user_item_data = orders_data.groupby(['Customer ID', 'Product ID']).agg({
    'Total Products': 'sum',
    'Order Date': 'max'
}).reset_index()

# Create interaction matrix
interaction_matrix = user_item_data.pivot(
    index='Customer ID',
    columns='Product ID',
    values='Total Products'
).fillna(0)

# Asignar valores aleatorios entre 0 y 1 a los valores faltantes
interaction_matrix = interaction_matrix.applymap(lambda x: random.randint(0, 1) if x == 0 else x)
interaction_matrix = interaction_matrix.astype(int)

# Create train-test split
print("Splitting data for evaluation...")
interaction_sparse = interaction_matrix.values

# Apply SVD
print("Training recommendation model...")
n_components = min(500, min(interaction_sparse.shape) - 1)
svd = TruncatedSVD(n_components=n_components, random_state=42)
user_factors = svd.fit_transform(interaction_sparse)
item_factors = svd.components_.T

# Get predictions
predictions = np.dot(user_factors, item_factors.T)

# Compute item similarity
item_similarity = cosine_similarity(item_factors)

# Save model data for API usage
print("Saving model data...")
with open("interaction_matrix.pkl", "wb") as f:
    pickle.dump(interaction_sparse, f)
with open("user_factors.pkl", "wb") as f:
    pickle.dump(user_factors, f)
with open("item_factors.pkl", "wb") as f:
    pickle.dump(item_factors, f)
with open("item_similarity.pkl", "wb") as f:
    pickle.dump(item_similarity, f)

popularity_metrics.to_pickle("popularity_metrics.pkl")
product_details_df.to_pickle("product_details_df.pkl")

print("Model data saved successfully!")

# Close MongoDB connection
client.close()
