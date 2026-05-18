"""
PUNTO DE ENTRADA: CityExplorer Backend
========================================
Servidor FastAPI con CORS habilitado para el frontend React.

Para correr:
    pip install fastapi uvicorn pandas
    uvicorn main:app --reload --port 8000

La API quedará disponible en:
    http://localhost:8000
    http://localhost:8000/docs  ← Swagger UI automático (¡úsalo en la expo!)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(
    title="CityExplorer API",
    description="API de turismo inteligente con Dijkstra, Prim, KD-Tree y Trie",
    version="1.0.0"
)

# CORS: permite al frontend (localhost:3000) llamar al backend (localhost:8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {
        "mensaje": "CityExplorer API funcionando 🗺️",
        "docs": "/docs",
        "endpoints": ["/api/atracciones", "/api/autocomplete",
                      "/api/shortest-path", "/api/mst", "/api/nearby"]
    }
