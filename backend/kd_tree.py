"""
ESTRUCTURA: KD-Tree 2D
========================
Implementación adaptada del código de clase, manteniendo la compatibilidad
con el resto del proyecto para cálculo de distancias reales (Haversine).
"""

import math
from dataclasses import dataclass

def _distancia_haversine(lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
    R = 6371  # Radio de la Tierra en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


@dataclass
class PuntoKD:
    """Un punto en el espacio 2D con metadatos de la atracción."""
    lat: float
    lon: float
    atraccion_id: int
    nombre: str

    # Permite que la instancia se comporte como una lista (punto[0], punto[1], len(punto))
    # tal como el código de clase lo espera.
    def __len__(self):
        return 2

    def __getitem__(self, index):
        if index == 0:
            return self.lat
        elif index == 1:
            return self.lon
        raise IndexError("Índice fuera de rango")

    def __iter__(self):
        yield self.lat
        yield self.lon


class nodo:
    def __init__(self, punto):
        self.punto = punto
        self.izq = None
        self.der = None

    def __str__(self):
        return str(self.punto)


class kdtree:
    def __init__(self):
        self.raiz = None

    def _crear(self, lista, profundidad=0):
        if len(lista) == 0:
            return None
        eje = profundidad % len(lista[0])
        lista.sort(key=lambda x: x[eje])
        mitad = len(lista) // 2
        n = nodo(lista[mitad])
        n.izq = self._crear(lista[:mitad], profundidad + 1)
        n.der = self._crear(lista[mitad + 1:], profundidad + 1)
        return n

    def crear(self, lista):
        self.raiz = self._crear(lista)

    # Alias para compatibilidad con explorer_service.py
    def construir(self, puntos):
        self.crear(puntos)

    def buscar_mas_cercano(self, punto):
        if self.raiz is None:
            return None
        return self.mas_cercano(self.raiz, punto, self.raiz.punto, None)

    def mas_cercano(self, nodo_actual, punto, mejor_punto, mejor_distancia, profundidad=0):
        if nodo_actual is None:
            return mejor_punto, mejor_distancia

        distancia = self.distancia(nodo_actual.punto, punto)
        if mejor_distancia is None or distancia < mejor_distancia:
            mejor_punto = nodo_actual.punto
            mejor_distancia = distancia

        eje = profundidad % len(punto)
        if punto[eje] < nodo_actual.punto[eje]:
            primero, segundo = nodo_actual.izq, nodo_actual.der
        else:
            primero, segundo = nodo_actual.der, nodo_actual.izq

        mejor_punto, mejor_distancia = self.mas_cercano(primero, punto, mejor_punto, mejor_distancia, profundidad + 1)

        distancia_plano = abs(punto[eje] - nodo_actual.punto[eje])
        if distancia_plano ** 2 < mejor_distancia:
            mejor_punto, mejor_distancia = self.mas_cercano(segundo, punto, mejor_punto, mejor_distancia, profundidad + 1)

        return mejor_punto, mejor_distancia

    def distancia(self, punto1, punto2):
        # Distancia Euclidiana (como en clase)
        return sum((a - b) ** 2 for a, b in zip(punto1, punto2))

    # --- Método adicional para compatibilidad con el frontend (búsqueda geoespacial) ---
    def buscar_por_radio(self, lat: float, lon: float, radio_km: float) -> list[dict]:
        resultado = []
        self._buscar_radio(self.raiz, lat, lon, radio_km, resultado, 0)
        resultado.sort(key=lambda x: x["distancia_km"])
        return resultado

    def _buscar_radio(self, nodo_actual, lat: float, lon: float, radio_km: float, resultado: list, profundidad: int):
        if nodo_actual is None:
            return

        # Calculamos distancia real en kilómetros
        dist = _distancia_haversine(lat, lon, nodo_actual.punto.lat, nodo_actual.punto.lon)
        if dist <= radio_km:
            resultado.append({
                "id": nodo_actual.punto.atraccion_id,
                "nombre": nodo_actual.punto.nombre,
                "distancia_km": round(dist, 3)
            })

        eje = profundidad % 2
        val_nodo = nodo_actual.punto[eje]
        val_query = lat if eje == 0 else lon
        
        # Poda
        dist_plano = abs(val_query - val_nodo)
        radio_grados = radio_km / 111.0 # 1 grado ~ 111km aproximado

        if val_query < val_nodo:
            self._buscar_radio(nodo_actual.izq, lat, lon, radio_km, resultado, profundidad + 1)
            if dist_plano <= radio_grados:
                self._buscar_radio(nodo_actual.der, lat, lon, radio_km, resultado, profundidad + 1)
        else:
            self._buscar_radio(nodo_actual.der, lat, lon, radio_km, resultado, profundidad + 1)
            if dist_plano <= radio_grados:
                self._buscar_radio(nodo_actual.izq, lat, lon, radio_km, resultado, profundidad + 1)

# Alias para que explorer_service.py pueda instanciarlo sin cambios
KDTree = kdtree
