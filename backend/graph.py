"""
MODELO: Grafo con Lista de Adyacencia
======================================
Representamos la red de atracciones turísticas como un grafo dirigido/no-dirigido.

¿Por qué lista de adyacencia y no matriz?
- Nuestra red es DISPERSA: 10 nodos pero solo 17 aristas (máximo posible: 90)
- Matriz gastaría O(V²) = 100 celdas; lista usa O(V + E) = 27 entradas
- Iterar vecinos es O(grado del nodo), más eficiente para Dijkstra y Prim
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Atraccion:
    """Nodo del grafo: una atracción turística."""
    id: int
    nombre: str
    tipo: str
    latitud: float
    longitud: float
    rating: float
    tiempo_visita_min: int
    # Horario (opcional, solo algunos lugares lo tienen)
    abre: Optional[str] = None
    cierra: Optional[str] = None
    dias_cerrado: Optional[str] = None


@dataclass
class Conexion:
    """Arista del grafo: conexión entre dos atracciones."""
    destino_id: int
    tiempo_min: int      # Peso principal para Dijkstra (modo tiempo)
    costo_pesos: int     # Peso alternativo para Dijkstra (modo costo)


class GrafoTuristico:
    """
    Grafo no-dirigido representado con lista de adyacencia.
    
    Estructura interna:
        nodos:   dict[id -> Atraccion]
        aristas: dict[id -> list[Conexion]]
    
    Complejidad espacial: O(V + E)
    """

    def __init__(self):
        self.nodos: dict[int, Atraccion] = {}
        # Lista de adyacencia: cada nodo apunta a su lista de conexiones
        self.aristas: dict[int, list[Conexion]] = {}

    def agregar_nodo(self, atraccion: Atraccion):
        self.nodos[atraccion.id] = atraccion
        if atraccion.id not in self.aristas:
            self.aristas[atraccion.id] = []

    def agregar_arista(self, origen_id: int, destino_id: int,
                       tiempo_min: int, costo_pesos: int):
        """
        Agrega arista bidireccional (no-dirigido).
        Ambos nodos se "ven" mutuamente como vecinos.
        """
        self.aristas[origen_id].append(
            Conexion(destino_id, tiempo_min, costo_pesos)
        )
        self.aristas[destino_id].append(
            Conexion(origen_id, tiempo_min, costo_pesos)
        )

    def vecinos(self, nodo_id: int) -> list[Conexion]:
        """Devuelve las conexiones salientes de un nodo. O(1)."""
        return self.aristas.get(nodo_id, [])

    def get_atraccion(self, nodo_id: int) -> Optional[Atraccion]:
        return self.nodos.get(nodo_id)

    def todos_los_ids(self) -> list[int]:
        return list(self.nodos.keys())

    def __repr__(self):
        return (f"GrafoTuristico("
                f"{len(self.nodos)} nodos, "
                f"{sum(len(v) for v in self.aristas.values()) // 2} aristas)")
