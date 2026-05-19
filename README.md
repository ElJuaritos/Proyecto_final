# Documentación del Backend: City Explorer

Esta documentación explica paso a paso el propósito y funcionamiento de cada uno de los archivos que componen el backend en Python.

---

## 1. `main.py`
**Propósito:** Es el punto de entrada de la aplicación. Aquí se levanta el servidor web usando el framework **FastAPI**.

**Paso a paso:**
1. Importa `FastAPI` y el enrutador (`router`) de `routes.py`.
2. Crea la instancia principal de la aplicación `app = FastAPI(...)` con metadatos como el título y descripción.
3. Configura el **CORS (Cross-Origin Resource Sharing)**. Esto es crucial porque el frontend (React en el puerto 3000 o 5173) y el backend (FastAPI en el puerto 8000) corren en puertos distintos. Sin CORS, el navegador bloquearía las peticiones.
4. Incluye las rutas definidas en `routes.py` bajo el prefijo `/api`.
5. Define un endpoint raíz `/` que simplemente devuelve un mensaje de bienvenida y los endpoints disponibles.

---

## 2. `routes.py`
**Propósito:** Define las URLs (endpoints) a las que el frontend puede hacer peticiones HTTP (GET, POST). Es una capa muy delgada que solo recibe datos y se los pasa al servicio principal.

**Paso a paso:**
1. Crea una instancia única de `ExplorerService` (el "cerebro" del backend).
2. Define modelos de datos con `Pydantic` (`RutaRequest`, `CercanosRequest`) para validar automáticamente que el frontend envíe los datos correctos (ej. que la latitud sea un número).
3. **`/atracciones`**: Devuelve la lista completa de lugares.
4. **`/autocomplete`**: Llama al método de autocompletado del servicio pasando el prefijo que escribió el usuario.
5. **`/shortest-path`**: Recibe un origen, destino y modo (tiempo/costo). Llama a la función de Dijkstra a través del servicio.
6. **`/mst`**: Llama a la función de Prim para obtener la red mínima.
7. **`/nearby`**: Llama al KD-Tree a través del servicio para buscar puntos cercanos a una latitud/longitud en un radio específico.

---

## 3. `explorer_service.py`
**Propósito:** Actúa como el "Director de Orquesta". Une la lectura de datos con los algoritmos. Mantiene la lógica de negocio separada de FastAPI.

**Paso a paso:**
1. **Inicialización:** Al crear la instancia, crea un `GrafoTuristico`, un `KDTree` y un `Trie`.
2. **Carga de Datos (`_cargar_datos`):** 
   - Lee `lugares.csv`, `horarios.csv` y `conexiones.csv` usando la librería `pandas`.
   - Por cada lugar, crea un objeto `Atraccion`, lo inserta en el grafo, lo inserta en el Trie (para autocompletado) y guarda sus coordenadas para el KD-Tree.
   - Construye las aristas del grafo y finalmente invoca `kd_tree.construir()`.
3. **Métodos de Consulta:** Expone funciones limpias (`ruta_mas_corta`, `red_minima`, `lugares_cercanos`, `autocompletar`) que `routes.py` puede llamar fácilmente.

---

## 4. `graph.py`
**Propósito:** Define las estructuras de datos fundamentales para representar el mapa de la ciudad como un grafo matemático.

**Paso a paso:**
1. Define la clase `Atraccion` usando `@dataclass` (una forma elegante en Python de crear clases para guardar datos). Guarda id, nombre, coordenadas, rating, etc.
2. Define la clase `Conexion` (la arista del grafo) que guarda hacia dónde va y cuánto cuesta en tiempo y dinero.
3. Define `GrafoTuristico`. Utiliza una **Lista de Adyacencia** (dos diccionarios: uno para nodos y otro para las listas de aristas de cada nodo). Esto es mucho más eficiente en memoria que una matriz, ya que no todos los lugares están conectados con todos.
4. Incluye funciones para agregar nodos y aristas (bidireccionales, porque las calles se pueden transitar de ida y vuelta).

---

## 5. `trie.py` (Árbol de Prefijos)
**Propósito:** Permite buscar palabras rápidamente letra por letra. Se usa para el autocompletado de la barra de búsqueda en el frontend.

**Paso a paso:**
1. Define `NodoTrie`, donde cada nodo representa una letra, guarda sus hijos en un diccionario y tiene una bandera (`es_fin`) para indicar si ahí termina el nombre de una atracción.
2. **Insertar:** Toma un nombre (ej. "Zócalo"), lo pasa a minúsculas y navega nodo por nodo creando las letras que no existen. Al final, guarda el ID de la atracción.
3. **Autocompletar (`autocomplete`):** 
   - Primero navega hasta la última letra del prefijo escrito por el usuario (ej. "Zo").
   - A partir de ahí, usa una búsqueda en profundidad (DFS) en `_recolectar_palabras` para explorar todas las ramas que cuelgan de ese nodo y devolver las palabras completas que encontró.

---

## 6. `dijkstra.py` (Ruta más corta)
**Propósito:** Encuentra el camino más barato (en tiempo o dinero) entre dos atracciones específicas.

**Paso a paso:**
1. **Inicialización:** Crea un diccionario de distancias asumiendo que todas son infinito, excepto el origen que es 0. Crea un diccionario de `anteriores` para poder rastrear los pasos de regreso.
2. **Priority Queue (Heap):** Utiliza `heapq` para llevar el control de qué nodo visitar a continuación. El heap garantiza que siempre sacaremos el nodo con el costo acumulado más bajo.
3. **Ciclo Principal:**
   - Extrae el nodo más barato del heap. Si es el destino, termina.
   - Si no, revisa todos sus vecinos.
   - **Relajación:** Si llegar a un vecino a través del nodo actual es más barato que la ruta que conocíamos antes, actualizamos su costo, anotamos de dónde venimos y lo metemos al heap.
4. **Reconstrucción:** Una vez alcanzado el destino, retrocede usando el diccionario `anteriores` para construir la lista de lugares visitados y la devuelve.

---

## 7. `prim.py` (Árbol de Expansión Mínima - MST)
**Propósito:** Encuentra cómo conectar todos los lugares del mapa sin formar ciclos, gastando lo mínimo indispensable (como si quisieras tender líneas de metro nuevas).

**Paso a paso:**
1. Selecciona un nodo inicial cualquiera (el primero de la lista) y lo marca como parte del árbol.
2. Mete todas las conexiones (aristas) de ese nodo a una cola de prioridad (Heap).
3. **Ciclo Voraz (Greedy):** 
   - Mientras haya aristas en el heap y falten nodos por conectar, saca la arista más barata.
   - Revisa el destino de esa arista. Si ya está en el árbol, la descarta (para evitar ciclos).
   - Si es un nodo nuevo, lo agrega al árbol, suma el costo total y mete todas las conexiones de este nuevo nodo al heap.
4. Devuelve la lista de aristas seleccionadas y el costo total.

---

## 8. `kd_tree.py` (Búsqueda Espacial / Vecinos Cercanos)
**Propósito:** Busca qué lugares están cerca de unas coordenadas de manera eficiente (sin tener que calcular la distancia con los 10,000 puntos del mapa).

**Paso a paso:**
1. Define las clases `nodo` y `kdtree` tal como las viste en tus clases universitarias.
2. **Construcción (`_crear`):** 
   - Toma una lista de puntos y un eje (alternando latitud `0` y longitud `1` dependiendo de la profundidad).
   - Ordena los puntos por ese eje y escoge el de en medio (la mediana) como raíz.
   - Parte la lista a la mitad y manda la mitad izquierda al hijo izquierdo y la derecha al hijo derecho recursivamente.
3. **Búsqueda por Radio (`_buscar_radio`):**
   - Calcula la distancia real (usando la fórmula de curvatura terrestre *Haversine*) entre el punto buscado y el nodo actual. Si está dentro del radio, lo guarda.
   - Calcula la distancia "en el plano" (en 1D) hacia el eje de división.
   - **Poda (La magia del KD-Tree):** Entra primero a la rama donde es más probable que esté el punto. Luego, revisa si la distancia hacia el plano divisor es menor que el radio de búsqueda; si no lo es, descarta toda la otra mitad del árbol, ahorrando miles de cálculos.
