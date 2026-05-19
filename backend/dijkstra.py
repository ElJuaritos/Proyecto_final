"""
ALGORITMO: Dijkstra — Ruta Más Corta: Encuentra el camino de menor costo entre dos nodos en un grafo ponderado.

Complejidad: O((V + E) log V)
- V operaciones de extracción del heap: cada una cuesta O(log V)
- E operaciones de inserción al heap: cada una cuesta O(log V)
- Total: O((V + E) log V)
"""

import heapq
from graph import GrafoTuristico
import numpy as np

def dijkstra(grafo: GrafoTuristico, origen_id: int, destino_id: int,
             modo: str = "tiempo") -> dict:
    """
    Encuentra la ruta más corta entre origen y destino.
    
    @param    grafo:      El grafo de atracciones.
    @param    origen_id:  ID de la atracción de inicio.
    @param    destino_id: ID de la atracción objetivo.
    @param    modo:       "tiempo" (minutos) o "costo" (pesos mexicanos).
    
    Retorna un dict con:
        - camino:      lista de nombres de atracciones en orden
        - ids:         lista de IDs en orden
        - total_tiempo: minutos totales del recorrido
        - total_costo:  costo total en pesos
        - encontrado:  bool
    """

    pi = {} # Nodo anterior en la ruta
    llave = {} # Costo acumulado desde el origen hasta cada nodo
    tiempos_acum = {}
    costos_acum = {}
    
    for v in grafo.todos_los_ids():
        pi[v] = None
        llave[v] = np.inf
        tiempos_acum[v] = 0
        costos_acum[v] = 0
    
    llave[origen_id] = 0
    Q = []
    for v in grafo.todos_los_ids():
        # Agrega todos los nodos al heap con su llave inicial
        heapq.heappush(Q, (llave[v], v)) 

    # Ciclo principal
    while Q:
        # Extrae el nodo con menor llave
        _, u = heapq.heappop(Q)

        # Si el nodo extraído es el destino, se detiene
        if u == destino_id:
            break

        for conexion in grafo.vecinos(u):
            # Elegimos el tipo de peso según el modo
            if modo == "tiempo":
                peso_arista = conexion.tiempo_min
            else:
                peso_arista = conexion.costo_pesos

            # Si se encontró un camino más corto, se actualiza la llave y el nodo anterior
            if llave[u] + peso_arista < llave[conexion.destino_id]:
                llave[conexion.destino_id] = llave[u] + peso_arista
                pi[conexion.destino_id] = u

                # Acumulamos tiempo y costo por separado
                tiempos_acum[conexion.destino_id] = (tiempos_acum[u]
                                                      + conexion.tiempo_min)
                costos_acum[conexion.destino_id] = (costos_acum[u]
                                                     + conexion.costo_pesos)
                # Se actualiza la posición del nodo en el heap
                heapq.heappush(Q, (llave[conexion.destino_id], conexion.destino_id))

    # Si llave sigue siendo infinita, no hay ruta
    if llave[destino_id] == np.inf:
        return {
            "encontrado": False,
            "mensaje": "No existe ruta entre estas atracciones"
        }

    # Seguimos los punteros de pi de atrás hacia adelante
    camino_ids = []
    nodo = destino_id
    while nodo is not None:
        camino_ids.append(nodo)
        nodo = pi[nodo]
    camino_ids.reverse()   # Revertimos el camino para obtner el orden correcto

    # Convertimos IDs a nombres legibles
    camino_nombres = [
        grafo.get_atraccion(id).nombre for id in camino_ids
    ]

    return {
        "encontrado": True,
        "camino": camino_nombres,
        "ids": camino_ids,
        "total_tiempo_min": tiempos_acum[destino_id],
        "total_costo_pesos": costos_acum[destino_id],
        "modo": modo
    }
