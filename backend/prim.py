"""
ALGORITMO: Prim — Árbol de Expansión Mínima (MST): Construye la red de menor costo total que conecta TODAS las atracciones.

Complejidad: O(E log V)
- E inserciones al heap: O(log V) cada una
- V extracciones del heap: O(log V) cada una
"""

import heapq
from graph import GrafoTuristico
import numpy as np

def prim(grafo: GrafoTuristico, modo: str = "tiempo") -> dict:
    """
    Genera el Árbol de Expansión Mínima con el algoritmo de Prim.
    
    
    @param    grafo: El grafo de atracciones.
    @param    modo:  "tiempo" o "costo" — define qué peso minimizar.
    
    Retorna:
        - aristas:      lista de conexiones seleccionadas para el MST
        - total_tiempo: suma de tiempos de todas las aristas del MST
        - total_costo:  suma de costos de todas las aristas del MST
        - nodos_conectados: número de nodos en el MST
    """
    ids = grafo.todos_los_ids()
    if not ids:
        return {"aristas": [], "total_tiempo": 0, "total_costo": 0}

    pi: dict[int, int | None] = {} # Nodo anterior en el MST
    llave: dict[int, float] = {} # Costo mínimo para conectar cada nodo al MST
    tiempos_arista: dict[int, int] = {}
    costos_arista: dict[int, int] = {}
    en_mst: set[int] = set() # Nodos ya incluidos en el árbol
    aristas_mst = [] # Aristas seleccionadas

    total_tiempo = 0
    total_costo  = 0

    for v in ids:
        pi[v] = None
        llave[v] = np.inf
        tiempos_arista[v] = 0
        costos_arista[v] = 0

    nodo_inicial = ids[0]
    llave[nodo_inicial] = 0

    # El heap guarda tuplas: (llave, nodo_id)
    Q = []
    for v in ids:
        heapq.heappush(Q, (llave[v], v))

    # Ciclo principal
    while Q and len(en_mst) < len(ids):
        llave_actual, u = heapq.heappop(Q)

        if u in en_mst:
            continue

        if llave_actual == np.inf:
            break

        en_mst.add(u)

        if pi[u] is not None:
            origen = pi[u]
            destino = u
            total_tiempo += tiempos_arista[u]
            total_costo += costos_arista[u]
            aristas_mst.append({
                "de":        grafo.get_atraccion(origen).nombre,
                "hacia":     grafo.get_atraccion(destino).nombre,
                "de_id":     origen,
                "hacia_id":  destino,
                "tiempo_min": tiempos_arista[u],
                "costo_pesos": costos_arista[u]
            })

        for conexion in grafo.vecinos(u):
            v = conexion.destino_id
            if v in en_mst:
                continue

            peso_arista = (conexion.tiempo_min if modo == "tiempo"
                           else conexion.costo_pesos)

            if peso_arista < llave[v]:
                llave[v] = peso_arista
                pi[v] = u
                tiempos_arista[v] = conexion.tiempo_min
                costos_arista[v] = conexion.costo_pesos
                heapq.heappush(Q, (llave[v], v))

    return {
        "aristas": aristas_mst,
        "total_tiempo_min": total_tiempo,
        "total_costo_pesos": total_costo,
        "nodos_conectados": len(en_mst),
        "total_nodos": len(ids),
        "modo": modo,
        # Pues, si nodos_conectados < total_nodos, el grafo es desconectado
        "es_conexo": len(en_mst) == len(ids)
    }
