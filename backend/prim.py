"""
ALGORITMO: Prim — Árbol de Expansión Mínima (MST)
===================================================
Construye la red de menor costo total que conecta TODAS las atracciones.

Caso de uso turístico: "¿Cuál es la red mínima de rutas de transporte
que conecta todos los puntos de interés con el menor costo posible?"

Intuición: Empezamos con un nodo cualquiera y crecemos el árbol
agregando siempre la arista más barata que conecta un nodo NUEVO.
Es voraz (greedy): en cada paso tomamos la mejor decisión local.

Diferencia con Dijkstra:
- Dijkstra: minimiza distancia desde UN origen a todos los demás
- Prim:     minimiza el PESO TOTAL del árbol que conecta TODOS los nodos

Complejidad: O(E log V)
- E inserciones al heap: O(log V) cada una
- V extracciones del heap: O(log V) cada una
"""

import heapq
from graph import GrafoTuristico


def prim(grafo: GrafoTuristico, modo: str = "tiempo") -> dict:
    """
    Genera el Árbol de Expansión Mínima con el algoritmo de Prim.
    
    Parámetros:
        grafo: El grafo de atracciones.
        modo:  "tiempo" o "costo" — define qué peso minimizar.
    
    Retorna:
        - aristas:      lista de conexiones seleccionadas para el MST
        - total_tiempo: suma de tiempos de todas las aristas del MST
        - total_costo:  suma de costos de todas las aristas del MST
        - nodos_conectados: número de nodos en el MST
    """
    ids = grafo.todos_los_ids()
    if not ids:
        return {"aristas": [], "total_tiempo": 0, "total_costo": 0}

    # ── Inicialización ───────────────────────────────────────────────
    en_mst: set[int] = set()         # Nodos ya incluidos en el árbol
    aristas_mst = []                  # Aristas seleccionadas

    total_tiempo = 0
    total_costo  = 0

    # Empezamos desde el primer nodo
    nodo_inicial = ids[0]
    en_mst.add(nodo_inicial)

    # ── Priority Queue ───────────────────────────────────────────────
    # Heap de candidatos: (peso, origen_id, destino_id, tiempo, costo)
    heap = []
    for conexion in grafo.vecinos(nodo_inicial):
        peso = (conexion.tiempo_min if modo == "tiempo"
                else conexion.costo_pesos)
        heapq.heappush(heap, (peso, nodo_inicial,
                               conexion.destino_id,
                               conexion.tiempo_min,
                               conexion.costo_pesos))

    # ── Ciclo Principal ──────────────────────────────────────────────
    # Repetimos hasta incluir todos los nodos
    while heap and len(en_mst) < len(ids):
        # Extraemos la arista más barata disponible
        peso, origen, destino, tiempo, costo = heapq.heappop(heap)

        # Si el destino ya está en el MST, esta arista crearía un ciclo → saltamos
        if destino in en_mst:
            continue

        # ¡Agregamos este nodo al árbol!
        en_mst.add(destino)
        total_tiempo += tiempo
        total_costo  += costo

        # Guardamos la arista seleccionada con nombres legibles
        aristas_mst.append({
            "de":        grafo.get_atraccion(origen).nombre,
            "hacia":     grafo.get_atraccion(destino).nombre,
            "de_id":     origen,
            "hacia_id":  destino,
            "tiempo_min": tiempo,
            "costo_pesos": costo
        })

        # Exploramos las aristas del nuevo nodo añadido
        for conexion in grafo.vecinos(destino):
            if conexion.destino_id not in en_mst:
                p = (conexion.tiempo_min if modo == "tiempo"
                     else conexion.costo_pesos)
                heapq.heappush(heap, (p, destino,
                                       conexion.destino_id,
                                       conexion.tiempo_min,
                                       conexion.costo_pesos))

    return {
        "aristas": aristas_mst,
        "total_tiempo_min": total_tiempo,
        "total_costo_pesos": total_costo,
        "nodos_conectados": len(en_mst),
        "total_nodos": len(ids),
        "modo": modo,
        # Nota: si nodos_conectados < total_nodos, el grafo es desconectado
        "es_conexo": len(en_mst) == len(ids)
    }
