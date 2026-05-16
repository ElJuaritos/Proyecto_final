"""
ESTRUCTURA: KD-Tree 2D
========================
Árbol binario espacial para búsqueda eficiente de atracciones cercanas.

Usamos latitud y longitud como las 2 dimensiones del árbol.

¿Por qué KD-Tree y no búsqueda lineal?
- Búsqueda lineal: O(N) por consulta — recorre TODAS las atracciones
- KD-Tree:         O(log N) promedio por consulta — poda ramas del espacio

Para N=10 la diferencia es mínima, pero con N=10,000 atracciones
el KD-Tree haría ~14 comparaciones vs 10,000 de la búsqueda lineal.

Complejidad:
- Construcción: O(N log N)
- Búsqueda KNN: O(log N) promedio, O(N) peor caso
- Búsqueda por radio: O(√N + k) promedio donde k = resultados
"""

import math
from dataclasses import dataclass
from typing import Optional


@dataclass
class PuntoKD:
    """Un punto en el espacio 2D con metadatos de la atracción."""
    lat: float
    lon: float
    atraccion_id: int
    nombre: str


class NodoKD:
    """Nodo del KD-Tree: guarda un punto y sus hijos izquierdo/derecho."""
    def __init__(self, punto: PuntoKD, izquierdo=None, derecho=None):
        self.punto = punto
        self.izquierdo: Optional["NodoKD"] = izquierdo
        self.derecho: Optional["NodoKD"] = derecho


def _distancia_haversine(lat1: float, lon1: float,
                          lat2: float, lon2: float) -> float:
    """
    Calcula distancia real entre dos coordenadas (en km).
    Fórmula Haversine — tiene en cuenta la curvatura de la Tierra.
    Para distancias cortas (<100km) podríamos usar Euclidiana,
    pero Haversine es más correcta geográficamente.
    """
    R = 6371  # Radio de la Tierra en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class KDTree:
    """
    KD-Tree 2D para búsqueda geoespacial de atracciones.
    
    Cada nivel del árbol alterna entre dividir por latitud (eje 0)
    y por longitud (eje 1). Esto garantiza particiones balanceadas
    del espacio geográfico.
    """

    def __init__(self):
        self.raiz: Optional[NodoKD] = None

    def construir(self, puntos: list[PuntoKD]):
        """
        Construye el KD-Tree desde una lista de puntos.
        Usa la mediana para balancear el árbol.
        Complejidad: O(N log N)
        """
        self.raiz = self._construir_recursivo(puntos, profundidad=0)

    def _construir_recursivo(self, puntos: list[PuntoKD],
                              profundidad: int) -> Optional[NodoKD]:
        if not puntos:
            return None

        # Alternamos el eje de división: 0=latitud, 1=longitud
        eje = profundidad % 2

        # Ordenamos por el eje actual y tomamos la mediana
        # Esto mantiene el árbol balanceado
        puntos_ordenados = sorted(
            puntos,
            key=lambda p: p.lat if eje == 0 else p.lon
        )
        medio = len(puntos_ordenados) // 2
        punto_mediana = puntos_ordenados[medio]

        # Construimos recursivamente los subárboles
        return NodoKD(
            punto=punto_mediana,
            izquierdo=self._construir_recursivo(
                puntos_ordenados[:medio], profundidad + 1
            ),
            derecho=self._construir_recursivo(
                puntos_ordenados[medio + 1:], profundidad + 1
            )
        )

    def buscar_cercanos(self, lat: float, lon: float,
                        k: int = 3) -> list[dict]:
        """
        Encuentra los k vecinos más cercanos a (lat, lon).
        Usa un heap para mantener los k mejores candidatos.
        Complejidad: O(log N) promedio.
        
        Retorna lista de dicts con id, nombre y distancia.
        """
        # heap = lista de (-distancia, punto) — negamos para simular max-heap
        heap = []
        self._buscar_knn(self.raiz, lat, lon, k, heap, profundidad=0)

        # Ordenamos por distancia ascendente antes de retornar
        resultado = []
        for neg_dist, punto in sorted(heap, key=lambda x: -x[0]):
            resultado.append({
                "id": punto.atraccion_id,
                "nombre": punto.nombre,
                "distancia_km": round(-neg_dist, 3)
            })
        return resultado

    def _buscar_knn(self, nodo: Optional[NodoKD], lat: float, lon: float,
                    k: int, heap: list, profundidad: int):
        """
        Búsqueda KNN recursiva con poda de ramas.
        
        La magia del KD-Tree está aquí: si la distancia al hiperplano
        divisor es mayor que la peor distancia en nuestro heap,
        podamos esa rama completa — no necesitamos explorarla.
        """
        if nodo is None:
            return

        dist = _distancia_haversine(lat, lon,
                                     nodo.punto.lat, nodo.punto.lon)

        # Insertamos en el heap si tiene espacio o mejora al peor
        if len(heap) < k:
            heap.append((-dist, nodo.punto))
        elif dist < -heap[0][0]:
            heap[0] = (-dist, nodo.punto)
            # Reordenamos manualmente (heap pequeño, no vale importar heapq)
            heap.sort(key=lambda x: x[0])

        # Determinamos qué subárbol explorar primero
        eje = profundidad % 2
        val_nodo = nodo.punto.lat if eje == 0 else nodo.punto.lon
        val_query = lat if eje == 0 else lon

        # Vamos primero al lado más prometedor
        if val_query < val_nodo:
            primero, segundo = nodo.izquierdo, nodo.derecho
        else:
            primero, segundo = nodo.derecho, nodo.izquierdo

        self._buscar_knn(primero, lat, lon, k, heap, profundidad + 1)

        # ¿Vale la pena explorar el otro lado?
        # Solo si la distancia al plano divisor es menor que nuestro peor resultado
        dist_plano = abs(val_query - val_nodo)
        peor_en_heap = -heap[0][0] if heap else float("inf")

        if dist_plano < peor_en_heap or len(heap) < k:
            self._buscar_knn(segundo, lat, lon, k, heap, profundidad + 1)

    def buscar_por_radio(self, lat: float, lon: float,
                          radio_km: float) -> list[dict]:
        """
        Encuentra todas las atracciones dentro de `radio_km` kilómetros.
        Complejidad: O(√N + k) promedio donde k = resultados encontrados.
        """
        resultado = []
        self._buscar_radio(self.raiz, lat, lon, radio_km, resultado, 0)
        resultado.sort(key=lambda x: x["distancia_km"])
        return resultado

    def _buscar_radio(self, nodo: Optional[NodoKD], lat: float, lon: float,
                       radio_km: float, resultado: list, profundidad: int):
        if nodo is None:
            return

        dist = _distancia_haversine(lat, lon,
                                     nodo.punto.lat, nodo.punto.lon)
        if dist <= radio_km:
            resultado.append({
                "id": nodo.punto.atraccion_id,
                "nombre": nodo.punto.nombre,
                "distancia_km": round(dist, 3)
            })

        # Poda: si la distancia al plano divisor > radio, no exploramos ese lado
        eje = profundidad % 2
        val_nodo = nodo.punto.lat if eje == 0 else nodo.punto.lon
        val_query = lat if eje == 0 else lon
        dist_plano = abs(val_query - val_nodo)

        if val_query < val_nodo:
            self._buscar_radio(nodo.izquierdo, lat, lon, radio_km,
                                resultado, profundidad + 1)
            if dist_plano <= radio_km:
                self._buscar_radio(nodo.derecho, lat, lon, radio_km,
                                    resultado, profundidad + 1)
        else:
            self._buscar_radio(nodo.derecho, lat, lon, radio_km,
                                resultado, profundidad + 1)
            if dist_plano <= radio_km:
                self._buscar_radio(nodo.izquierdo, lat, lon, radio_km,
                                    resultado, profundidad + 1)
