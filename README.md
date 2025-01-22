# VentasCruzadasDeploy

# Recommendation System Project

## Overview
This project implements a recommendation system using FastAPI as the API framework, MongoDB for database management, and Singular Value Decomposition (SVD) for generating personalized recommendations. It includes functionality to preprocess data, generate synthetic datasets, and provide recommendations based on a combination of collaborative filtering and product popularity metrics.

## Key Features
1. **Data Handling**: Connects to a MongoDB database and retrieves collections for products and orders.
2. **Popularity Metrics**: Calculates product popularity scores based on sales, order frequency, and time decay.
3. **Recommendation Model**: Uses SVD for collaborative filtering and combines it with popularity metrics for final recommendations.
4. **Synthetic Data Generation**: Generates synthetic datasets for customers, products, and orders using the Faker library.
5. **API Endpoint**: Provides an API endpoint to serve product recommendations.

---

## Installation

### Prerequisites
- Python 3.9+
- MongoDB installed and running locally

### Dependencies
Install required packages using the following command:

```bash
pip install -r requirements.txt
```

Ensure the following Python libraries are included in your `requirements.txt` file:

```
pandas
scikit-learn
numpy
pymongo
fastapi
faker
uvicorn
pydantic
```

---

## Project Structure

- **Database Connection**: Connects to a local MongoDB instance and retrieves collections for `products` and `orders`.
- **Popularity Metrics Calculation**: Calculates product popularity based on order data, including time decay factors for recent orders.
- **Data Preparation**:
  - Retrieves and preprocesses product and order data from MongoDB.
  - Encodes product IDs and customer interactions into a user-item interaction matrix.
- **Recommendation Engine**:
  - Uses SVD to decompose the interaction matrix.
  - Computes item similarity using cosine similarity.
  - Combines collaborative filtering with popularity scores to generate recommendations.
- **Synthetic Data Generation**:
  - Generates categories, products, customers, and orders.
  - Assigns realistic attributes using the Faker library.
- **FastAPI Endpoint**: Implements a POST endpoint for generating recommendations based on user ID.

---

## Usage

### 1. Setup MongoDB
1. Start MongoDB server:
   ```bash
   mongod --config /etc/mongod.conf
   ```
2. Ensure the following collections exist in the database `my_database`:
   - `products`
   - `orders`
   - `customers`
   - `categories`

### 2. Run the FastAPI Server
1. Launch the server using Uvicorn:
   ```bash
   uvicorn main:app --reload
   ```
2. Open the API documentation at:
   ```
   http://127.0.0.1:8000/docs
   ```

### 3. API Endpoint
#### **POST /recommendations/**
Request Body:
```json
{
    "user_id": 1,
    "n": 5,
    "max_per_category": 2
}
```
Response:
```json
{
    "user_id": 1,
    "recommendations": [101, 202, 303]
}
```

Parameters:
- `user_id`: ID of the user for whom recommendations are generated.
- `n`: Number of recommendations (default: 5).
- `max_per_category`: Maximum recommendations per category (default: 2).

### 4. Synthetic Data Generation
- Synthetic data is generated and inserted into MongoDB collections (`products`, `orders`, `customers`, and `categories`) using predefined functions in the code.
- The `process_external_products_with_categories` function processes an external CSV file containing product data.

---

## Files
- **main.py**: Contains the implementation of the FastAPI server and recommendation logic.
- **interaction_matrix.pkl**: Stores the user-item interaction matrix.
- **user_factors.pkl**: Contains the user factor matrix from SVD.
- **item_factors.pkl**: Contains the item factor matrix from SVD.
- **item_similarity.pkl**: Stores the item similarity matrix.
- **popularity_metrics.pkl**: Stores calculated product popularity metrics.
- **product_details_df.pkl**: Contains detailed product information.

---

## Key Functions

### Data Handling
- **`calculate_popularity_score`**: Computes product popularity based on time decay and order frequency.
- **`create_general_categories`**: Generates predefined categories and inserts them into MongoDB.
- **`process_external_products_with_categories`**: Processes an external product dataset and maps products to general categories.
- **`generate_customers`**: Generates synthetic customer data.
- **`generate_orders`**: Generates synthetic order data.

### Recommendation System
- **`get_recommendations`**: Combines collaborative filtering and popularity scores to recommend products.
- **`train_svd`**: Trains the recommendation model using SVD.

---

## Notes
- Modify the database name and collection names as per your requirements.
- Ensure the MongoDB server is running and accessible.
- Customize the `process_external_products_with_categories` function to fit your dataset.
- The project assumes a specific CSV format for external product data.

---

## Future Enhancements
- Add user authentication for personalized recommendations.
- Implement advanced filtering options in the API.
- Extend the recommendation engine to support hybrid filtering.
- Deploy the API to a cloud platform (e.g., AWS, Azure, or GCP).

---

## Author
Developed by [Your Name].

## License
This project is licensed under the MIT License. See the LICENSE file for details.

