import fastapi
import pandas as pd
from pydantic import BaseModel
from typing import List
from datetime import datetime
import os

from challenge.model import ReplenishmentModel

app = fastapi.FastAPI()

# Cargar el modelo al iniciar
model = ReplenishmentModel()
model_path = "model.pkl"
if os.path.exists(model_path):
    model.load(model_path)

# Cargar productos conocidos
productos = pd.read_csv("dataset/productos.csv")
known_gtins = set(productos['gtin'].astype(str).tolist())


class ProductRequest(BaseModel):
    gtin: str
    fecha: str


class PredictRequest(BaseModel):
    products: List[ProductRequest]


class PredictResponse(BaseModel):
    predict: List[dict]


@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }


@app.post("/predict", status_code=200, response_model=PredictResponse)
async def post_predict(request: PredictRequest) -> dict:
    # Validar productos
    for product in request.products:
        if product.gtin not in known_gtins:
            raise fastapi.HTTPException(
                status_code=400,
                detail=f"Producto desconocido: {product.gtin}"
            )
        
        # Validar fecha
        try:
            datetime.strptime(product.fecha, '%Y-%m-%d')
        except ValueError:
            raise fastapi.HTTPException(
                status_code=400,
                detail=f"Fecha inválida: {product.fecha}. Formato esperado: YYYY-MM-DD"
            )
    
    # Crear DataFrame para predicción
    data = []
    for product in request.products:
        data.append({
            'gtin': product.gtin,
            'fecha': product.fecha,
            'cantidad': 0,
            'tipo_movimiento': 'S'
        })
    
    df = pd.DataFrame(data)
    
    # Preprocesar y predecir
    features = model.preprocess(data=df)
    predictions = model.predict(features=features)
    
    return {"predict": predictions}