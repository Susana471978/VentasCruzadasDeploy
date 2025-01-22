from fastapi import FastAPI, HTTPException
import numpy as np
import pandas as pd
import pickle
from pydantic import BaseModel

# Carga de datos preentrenados
with open("interaction_matrix.pkl", "rb") as f:
    interaction_matrix = pickle.load(f)

with open("user_factors.pkl", "rb") as f:
    user_factors = pickle.load(f)

with open("item_factors.pkl", "rb") as f:
    item_factors = pickle.load(f)

with open("item_similarity.pkl", "rb") as f:
    item_similarity = pickle.load(f)

popularity_metrics = pd.read_pickle("popularity_metrics.pkl")
product_details_df = pd.read_pickle("product_details_df.pkl")

# Inicializa la aplicación FastAPI
app = FastAPI()

# Modelo de entrada
class RecommendationRequest(BaseModel):
    user_id: int
    n: int = 5  # Número de recomendaciones
    max_per_category: int = 2  # Máximo por categoría

# Función de recomendación
def get_recommendations(user_id, n=5, max_per_category=2):
    if user_id >= interaction_matrix.shape[0]:
        raise ValueError(f"El ID de usuario {user_id} no existe.")

    user_ratings = interaction_matrix[user_id]
    base_scores = item_similarity.dot(user_ratings)
    
    # Puntajes de popularidad
    popularity_scores = popularity_metrics['popularity_score'].values
    
    # Combinación de puntuaciones
    final_scores = 0.7 * base_scores + 0.3 * popularity_scores
    
    # Generar recomendaciones
    recommendations = [(i, score) for i, score in enumerate(final_scores)]
    
    # Filtrar y ordenar por puntaje
    potential_recommendations = []
    for product_idx, score in recommendations:
        product_details = product_details_df.iloc[product_idx].to_dict()
        product_details['recommendation_score'] = float(score)
        potential_recommendations.append(product_details)
    
    # Ordenar por calificación y puntuación
    potential_recommendations.sort(key=lambda x: (x['product_rating'], x['recommendation_score']), reverse=True)
    
    # Diversidad por categoría
    detailed_recommendations = []
    category_count = {}
    
    for product in potential_recommendations:
        if len(detailed_recommendations) >= n:
            break
            
        category = product['Category']
        if category_count.get(category, 0) >= max_per_category:
            continue
            
        category_count[category] = category_count.get(category, 0) + 1
        detailed_recommendations.append(product)
    
    return [product['Product ID'] for product in detailed_recommendations]

# Endpoint de recomendaciones
@app.post("/recommendations/")
async def recommend_products(request: RecommendationRequest):
    try:
        recommendations = get_recommendations(request.user_id, request.n, request.max_per_category)
        return {"user_id": request.user_id, "recommendations": recommendations}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

