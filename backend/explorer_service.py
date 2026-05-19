"""
SERVICIO: ExplorerService
===========================
Capa de negocio que une todos los módulos:
- Carga los CSVs con pandas y construye el grafo
- Inicializa KD-Tree y Trie con los datos cargados
- Expone métodos limpios que la API llama directamente

Esta separación (service vs api) mantiene la lógica de negocio
independiente del framework web (FastAPI). Es más fácil testear
y más claro en una presentación.
"""

from pathlib import Path
import pandas as pd

from graph   import GrafoTuristico, Atraccion
from kd_tree import KDTree, PuntoKD
from trie    import Trie
from dijkstra import dijkstra
from prim     import prim


# Ruta a los datos — relativa a este archivo
DATA_DIR = Path(__file__).parent.parent / "datos"


class ExplorerService:
    """
    Servicio principal de CityExplorer.
    Se instancia UNA sola vez al arrancar el servidor (patrón Singleton ligero).
    """

    def __init__(self):
        self.grafo   = GrafoTuristico()
        self.kd_tree = KDTree()
        self.trie    = Trie()
        self._cargar_datos()

    # Se cargan los datos
    def _cargar_datos(self):
        """
        Lee los tres CSVs con pandas y puebla las estructuras de datos.
        Pandas simplifica el parsing; la lógica algorítmica es 100% manual.
        """
        # ── lugares.csv → nodos del grafo ───────────────────────────
        df_lugares = pd.read_csv(DATA_DIR / "lugares.csv")
        df_horarios = pd.read_csv(DATA_DIR / "horarios.csv")

        # Hacemos un merge para añadir horarios a quienes los tienen
        df = df_lugares.merge(df_horarios, left_on="id",
                               right_on="id_lugar", how="left")

        puntos_kd = []  # Para construir el KD-Tree al final

        for _, fila in df.iterrows():
            atraccion = Atraccion(
                id=int(fila["id"]),
                nombre=fila["nombre"],
                tipo=fila["tipo"],
                latitud=float(fila["latitud"]),
                longitud=float(fila["longitud"]),
                rating=float(fila["rating"]),
                tiempo_visita_min=int(fila["tiempo_visita_min"]),
                abre=fila.get("abre") if pd.notna(fila.get("abre")) else None,
                cierra=fila.get("cierra") if pd.notna(fila.get("cierra")) else None,
                dias_cerrado=(fila.get("dias_cerrado")
                              if pd.notna(fila.get("dias_cerrado")) else None),
            )
            self.grafo.agregar_nodo(atraccion)
            self.trie.insertar(atraccion.nombre, atraccion.id)
            puntos_kd.append(PuntoKD(atraccion.latitud, atraccion.longitud,
                                      atraccion.id, atraccion.nombre))

        df_conexiones = pd.read_csv(DATA_DIR / "conexiones.csv")
        for _, fila in df_conexiones.iterrows():
            self.grafo.agregar_arista(
                int(fila["origen"]),
                int(fila["destino"]),
                int(fila["tiempo_min"]),
                int(fila["costo_pesos"])
            )

        self.kd_tree.construir(puntos_kd)

        print(f"✓ {self.grafo} cargado")
        print(f"✓ KD-Tree construido con {len(puntos_kd)} puntos")
        print(f"✓ Trie cargado con {len(puntos_kd)} atracciones")

    def ruta_mas_corta(self, origen_nombre: str, destino_nombre: str,
                       modo: str = "tiempo") -> dict:
        """Encuentra la ruta óptima entre dos atracciones por nombre."""
        origen  = self._nombre_a_id(origen_nombre)
        destino = self._nombre_a_id(destino_nombre)

        if origen is None:
            return {"encontrado": False,
                    "mensaje": f"Atracción no encontrada: '{origen_nombre}'"}
        if destino is None:
            return {"encontrado": False,
                    "mensaje": f"Atracción no encontrada: '{destino_nombre}'"}

        return dijkstra(self.grafo, origen, destino, modo)

    def red_minima(self, modo: str = "tiempo") -> dict:
        """Genera el Árbol de Expansión Mínima con Prim."""
        return prim(self.grafo, modo)

    def lugares_cercanos(self, lat: float, lon: float,
                          radio_km: float = 5.0) -> dict:
        """Encuentra atracciones dentro de un radio dado."""
        resultados = self.kd_tree.buscar_por_radio(lat, lon, radio_km)
        # Enriquecemos con datos de la atracción
        enriquecidos = []
        for r in resultados:
            atrac = self.grafo.get_atraccion(r["id"])
            if atrac:
                enriquecidos.append({
                    **r,
                    "tipo": atrac.tipo,
                    "rating": atrac.rating,
                    "tiempo_visita_min": atrac.tiempo_visita_min
                })
        return {"radio_km": radio_km, "resultados": enriquecidos,
                "total": len(enriquecidos)}

    def autocompletar(self, prefijo: str) -> list[dict]:
        """Autocompletado de nombres de atracciones con el Trie."""
        return self.trie.autocomplete(prefijo)

    def todas_las_atracciones(self) -> list[dict]:
        """Devuelve todas las atracciones (para poblar dropdowns)."""
        return [
            {
                "id": a.id,
                "nombre": a.nombre,
                "tipo": a.tipo,
                "rating": a.rating,
                "latitud": a.latitud,
                "longitud": a.longitud,
                "tiempo_visita_min": a.tiempo_visita_min,
                "abre": a.abre,
                "cierra": a.cierra,
                "dias_cerrado": a.dias_cerrado,
            }
            for a in self.grafo.nodos.values()
        ]

    def _nombre_a_id(self, nombre: str) -> int | None:
        """Busca el ID de una atracción por nombre (case-insensitive)."""
        nombre_lower = nombre.lower().strip()
        for nid, atrac in self.grafo.nodos.items():
            if atrac.nombre.lower() == nombre_lower:
                return nid
        return None
