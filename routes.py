"""
API: Rutas de FastAPI
=======================
Endpoints REST que el frontend React consume.
Cada endpoint delega inmediatamente al ExplorerService.
Esta capa es DELGADA: solo valida la entrada y formatea la salida.
"""

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from explorer_service import ExplorerService

router = APIRouter()

# Instancia única del servicio (se comparte entre todas las peticiones)
service = ExplorerService()


# ── Modelos de Request ───────────────────────────────────────────────

class RutaRequest(BaseModel):
    origen: str
    destino: str
    modo: str = "tiempo"   # "tiempo" o "costo"

class CercanosRequest(BaseModel):
    latitud: float
    longitud: float
    radio_km: float = 5.0


# ── Endpoints ────────────────────────────────────────────────────────

@router.get("/atracciones")
def get_atracciones():
    """Devuelve todas las atracciones. Usado para poblar dropdowns."""
    return service.todas_las_atracciones()


@router.get("/autocomplete")
def get_autocomplete(prefix: str = Query(..., min_length=1)):
    """
    Autocompletado de nombres usando el Trie.
    Ejemplo: GET /autocomplete?prefix=Cha → ["Chapultepec"]
    Complejidad: O(m) donde m = len(prefix)
    """
    resultados = service.autocompletar(prefix)
    return {"prefix": prefix, "resultados": resultados}


@router.post("/shortest-path")
def get_shortest_path(body: RutaRequest):
    """
    Ruta más corta entre dos atracciones con Dijkstra.
    Modo "tiempo": minimiza minutos de trayecto.
    Modo "costo":  minimiza pesos MXN.
    Complejidad: O((V + E) log V)
    """
    if body.modo not in ("tiempo", "costo"):
        raise HTTPException(status_code=400,
                            detail="modo debe ser 'tiempo' o 'costo'")
    resultado = service.ruta_mas_corta(body.origen, body.destino, body.modo)
    if not resultado.get("encontrado"):
        raise HTTPException(status_code=404, detail=resultado.get("mensaje"))
    return resultado


@router.get("/mst")
def get_mst(modo: str = Query("tiempo")):
    """
    Árbol de Expansión Mínima con Prim.
    Devuelve la red que conecta todas las atracciones con menor costo total.
    Complejidad: O(E log V)
    """
    if modo not in ("tiempo", "costo"):
        raise HTTPException(status_code=400,
                            detail="modo debe ser 'tiempo' o 'costo'")
    return service.red_minima(modo)


@router.post("/nearby")
def get_nearby(body: CercanosRequest):
    """
    Atracciones dentro de un radio dado usando KD-Tree.
    Complejidad: O(√N + k) vs O(N) de búsqueda lineal.
    """
    if body.radio_km <= 0:
        raise HTTPException(status_code=400, detail="radio_km debe ser > 0")
    return service.lugares_cercanos(body.latitud, body.longitud, body.radio_km)
