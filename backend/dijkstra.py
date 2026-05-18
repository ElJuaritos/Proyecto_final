"""
ALGORITMO: Dijkstra — Ruta Más Corta
======================================
Encuentra el camino de menor costo entre dos nodos en un grafo ponderado.

Intuición: "Siempre expande el nodo más barato que aún no has visitado."
Es como un BFS, pero en lugar de una cola FIFO usamos una PRIORITY QUEUE
que siempre nos da el nodo de menor distancia acumulada.

Complejidad: O((V + E) log V)
- V operaciones de extracción del heap: cada una cuesta O(log V)
- E operaciones de inserción al heap: cada una cuesta O(log V)
- Total: O((V + E) log V)

¿Por qué NO funciona con pesos negativos?
Dijkstra asume que agregar una arista nunca puede reducir el costo
ya acumulado. Con pesos negativos esa suposición se rompe.
(Para eso existe Bellman-Ford, pero no lo necesitamos aquí.)
"""

import heapq
from graph import GrafoTuristico


def dijkstra(grafo: GrafoTuristico, origen_id: int, destino_id: int,
             modo: str = "tiempo") -> dict:
    """
    Encuentra la ruta más corta entre origen y destino.
    
    Parámetros:
        grafo:      El grafo de atracciones.
        origen_id:  ID de la atracción de inicio.
        destino_id: ID de la atracción objetivo.
        modo:       "tiempo" (minutos) o "costo" (pesos MXN).
    
    Retorna un dict con:
        - camino:      lista de nombres de atracciones en orden
        - ids:         lista de IDs en orden
        - total_tiempo: minutos totales del recorrido
        - total_costo:  costo total en pesos
        - encontrado:  bool
    """

    # ── Inicialización ──────────────────────────────────────────────
    # distancias[id] = menor costo conocido desde origen hasta id
    distancias = {nid: float("inf") for nid in grafo.todos_los_ids()}
    distancias[origen_id] = 0

    # anteriores[id] = nodo desde el que llegamos (para reconstruir ruta)
    anteriores: dict[int, int | None] = {nid: None for nid in grafo.todos_los_ids()}

    # Guardamos tiempos y costos por separado para reportarlos ambos
    tiempos_acum = {nid: 0 for nid in grafo.todos_los_ids()}
    costos_acum  = {nid: 0 for nid in grafo.todos_los_ids()}

    # ── Priority Queue ───────────────────────────────────────────────
    # El heap guarda tuplas: (peso_acumulado, nodo_id)
    # heapq en Python es un min-heap: el más pequeño sale primero
    heap = [(0, origen_id)]

    visitados: set[int] = set()

    # ── Ciclo Principal ──────────────────────────────────────────────
    while heap:
        # Extraemos el nodo con menor costo acumulado — O(log V)
        peso_actual, nodo_actual = heapq.heappop(heap)

        # Si ya lo visitamos, ignoramos (puede haber duplicados en el heap)
        if nodo_actual in visitados:
            continue
        visitados.add(nodo_actual)

        # ¡Llegamos al destino! Podemos parar temprano.
        if nodo_actual == destino_id:
            break

        # ── Relajación de aristas ────────────────────────────────────
        for conexion in grafo.vecinos(nodo_actual):
            if conexion.destino_id in visitados:
                continue

            # Elegimos el peso según el modo solicitado
            peso_arista = (conexion.tiempo_min if modo == "tiempo"
                           else conexion.costo_pesos)
            nuevo_peso = distancias[nodo_actual] + peso_arista

            # ¿Encontramos un camino más corto? → Actualizamos
            if nuevo_peso < distancias[conexion.destino_id]:
                distancias[conexion.destino_id] = nuevo_peso
                anteriores[conexion.destino_id] = nodo_actual

                # Acumulamos tiempo y costo por separado
                tiempos_acum[conexion.destino_id] = (tiempos_acum[nodo_actual]
                                                      + conexion.tiempo_min)
                costos_acum[conexion.destino_id]  = (costos_acum[nodo_actual]
                                                      + conexion.costo_pesos)
                # Insertamos al heap — O(log V)
                heapq.heappush(heap, (nuevo_peso, conexion.destino_id))

    # ── Reconstrucción del camino ────────────────────────────────────
    # Si distancia sigue siendo infinita, no hay ruta
    if distancias[destino_id] == float("inf"):
        return {
            "encontrado": False,
            "mensaje": "No existe ruta entre estas atracciones"
        }

    # Seguimos los punteros `anteriores` de atrás hacia adelante
    camino_ids = []
    nodo = destino_id
    while nodo is not None:
        camino_ids.append(nodo)
        nodo = anteriores[nodo]
    camino_ids.reverse()   # Estaba al revés (destino → origen)

    # Convertimos IDs a nombres legibles
    camino_nombres = [
        grafo.get_atraccion(nid).nombre for nid in camino_ids
    ]

    return {
        "encontrado": True,
        "camino": camino_nombres,
        "ids": camino_ids,
        "total_tiempo_min": tiempos_acum[destino_id],
        "total_costo_pesos": costos_acum[destino_id],
        "modo": modo
    }
