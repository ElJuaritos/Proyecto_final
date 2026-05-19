from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Atraccion:
    id: int
    nombre: str
    tipo: str
    latitud: float
    longitud: float
    rating: float
    tiempo_visita_min: int
    abre: Optional[str] = None
    cierra: Optional[str] = None
    dias_cerrado: Optional[str] = None


@dataclass
class Conexion:
    destino_id: int
    tiempo_min: int    
    costo_pesos: int    


class GrafoTuristico:

    def __init__(self):
        self.nodos: dict[int, Atraccion] = {}
        self.aristas: dict[int, list[Conexion]] = {}

    def agregar_nodo(self, atraccion: Atraccion):
        self.nodos[atraccion.id] = atraccion
        if atraccion.id not in self.aristas:
            self.aristas[atraccion.id] = []

    def agregar_arista(self, origen_id: int, destino_id: int,
                       tiempo_min: int, costo_pesos: int):

        self.aristas[origen_id].append(
            Conexion(destino_id, tiempo_min, costo_pesos)
        )
        self.aristas[destino_id].append(
            Conexion(origen_id, tiempo_min, costo_pesos)
        )

    def vecinos(self, nodo_id: int) -> list[Conexion]:
        return self.aristas.get(nodo_id, [])

    def get_atraccion(self, nodo_id: int) -> Optional[Atraccion]:
        return self.nodos.get(nodo_id)

    def todos_los_ids(self) -> list[int]:
        return list(self.nodos.keys())

    def __repr__(self):
        return (f"GrafoTuristico("
                f"{len(self.nodos)} nodos, "
                f"{sum(len(v) for v in self.aristas.values()) // 2} aristas)")
