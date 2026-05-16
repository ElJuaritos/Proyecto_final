"""
ESTRUCTURA: Trie (Árbol de Prefijos)
======================================
Usamos un Trie para implementar autocompletado de nombres de atracciones.

¿Por qué Trie y no simplemente filtrar con str.startswith()?
- startswith() recorre TODA la lista cada vez: O(N * m)
  donde N = número de atracciones, m = longitud del prefijo
- Trie responde en O(m) sin importar cuántas atracciones hay
- Los prefijos se comparten en memoria (eficiente)

Complejidad:
- Inserción:     O(m)  donde m = longitud de la palabra
- Búsqueda:      O(m)
- Autocompletado: O(m + k) donde k = número de resultados
"""


class NodoTrie:
    """Un nodo del Trie: guarda un carácter y sus hijos."""
    def __init__(self):
        # Mapa de carácter -> hijo NodoTrie
        self.hijos: dict[str, "NodoTrie"] = {}
        # ¿Termina aquí una palabra completa?
        self.es_fin: bool = False
        # Si es fin, guardamos el id de la atracción
        self.atraccion_id: int | None = None
        # Nombre completo original (para devolver al usuario)
        self.nombre_completo: str | None = None


class Trie:
    """
    Árbol de prefijos para búsqueda y autocompletado de atracciones.
    
    Normalizamos a minúsculas para búsquedas case-insensitive.
    """

    def __init__(self):
        self.raiz = NodoTrie()

    def insertar(self, nombre: str, atraccion_id: int):
        """
        Inserta un nombre en el Trie.
        Complejidad: O(m) donde m = len(nombre)
        """
        nodo = self.raiz
        # Normalizamos a minúsculas para búsqueda insensible a mayúsculas
        for caracter in nombre.lower():
            if caracter not in nodo.hijos:
                nodo.hijos[caracter] = NodoTrie()
            nodo = nodo.hijos[caracter]
        # Marcamos el final y guardamos metadatos
        nodo.es_fin = True
        nodo.atraccion_id = atraccion_id
        nodo.nombre_completo = nombre

    def _navegar_hasta_prefijo(self, prefijo: str) -> NodoTrie | None:
        """
        Navega el Trie hasta el nodo que corresponde al prefijo.
        Retorna None si el prefijo no existe.
        Complejidad: O(m)
        """
        nodo = self.raiz
        for caracter in prefijo.lower():
            if caracter not in nodo.hijos:
                return None   # Prefijo no encontrado
            nodo = nodo.hijos[caracter]
        return nodo

    def _recolectar_palabras(self, nodo: NodoTrie, resultado: list):
        """
        DFS desde un nodo: recoge todas las palabras que cuelgan de él.
        Esto nos da todos los autocompletados posibles.
        """
        if nodo.es_fin:
            resultado.append({
                "id": nodo.atraccion_id,
                "nombre": nodo.nombre_completo
            })
        for hijo in nodo.hijos.values():
            self._recolectar_palabras(hijo, resultado)

    def autocomplete(self, prefijo: str) -> list[dict]:
        """
        Devuelve todas las atracciones cuyo nombre empieza con `prefijo`.
        Complejidad: O(m + k) donde k = número de resultados.
        
        Ejemplo: autocomplete("cha") -> [{"id": 3, "nombre": "Chapultepec"}]
        """
        nodo = self._navegar_hasta_prefijo(prefijo)
        if nodo is None:
            return []   # Ninguna atracción tiene ese prefijo
        resultado = []
        self._recolectar_palabras(nodo, resultado)
        return resultado

    def buscar_exacto(self, nombre: str) -> bool:
        """
        Verifica si un nombre exacto existe en el Trie.
        Complejidad: O(m)
        """
        nodo = self._navegar_hasta_prefijo(nombre)
        return nodo is not None and nodo.es_fin
