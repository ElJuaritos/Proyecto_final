
class nodoTrie:
    def __init__(self):
        self.hijos = {}
        self.fin = False
        self.cont = 0  # cuántas veces se agregó esta palabra
        
        # Atributos adicionales para el proyecto
        self.atraccion_id = None
        self.nombre_completo = None


class Trie:
    def __init__(self):
        self.raiz = nodoTrie()
        self.cant = 0
  
  
    def agregar(self, palabra):
        actual = self.raiz

        palabra_norm = palabra.lower()
        for simbolo in palabra_norm:
            if simbolo not in actual.hijos:
                actual.hijos[simbolo] = nodoTrie()
            actual = actual.hijos[simbolo]
            
        if not actual.fin:
            actual.fin = True
            self.cant += 1

        actual.cont += 1  
       
    def buscar(self, palabra):
        existe = True
        actual = self.raiz
        palabra_norm = palabra.lower()
        for simbolo in palabra_norm:
            if simbolo not in actual.hijos:
                existe = False
            else:
                actual = actual.hijos[simbolo]
        if actual.fin == False:
            existe = False
        return existe
    
    def buscaR(self, palabra, actual):
        if actual is None:
            return False
        if len(palabra) == 0:
            return actual.fin
        if palabra[0].lower() not in actual.hijos:
            return False
        return self.buscaR(palabra[1:], actual.hijos[palabra[0].lower()])
    
    def agregada_max(self, nodo, prefijo_actual):
        mejor_palabra = ""
        mejor_cont = 0

        if nodo.fin:
            mejor_palabra = prefijo_actual
            mejor_cont = nodo.cont

        for letra, hijo in nodo.hijos.items():
            palabra_candidata, cont_candidato = self.agregada_max(hijo, prefijo_actual + letra)
            if cont_candidato > mejor_cont:
                mejor_cont = cont_candidato
                mejor_palabra = palabra_candidata

        return mejor_palabra, mejor_cont

    def completar_palabra(self, prefijo):
        actual = self.raiz
        prefijo_norm = prefijo.lower()
        for simbolo in prefijo_norm:
            if simbolo not in actual.hijos:
                return None  
            actual = actual.hijos[simbolo]

        palabra, cont = self.agregada_max(actual, prefijo_norm)
        return palabra

    
    def insertar(self, nombre: str, atraccion_id: int):

        self.agregar(nombre)
        
        actual = self.raiz
        for simbolo in nombre.lower():
            actual = actual.hijos[simbolo]
            
        actual.atraccion_id = atraccion_id
        actual.nombre_completo = nombre

    def _recolectar_palabras_dict(self, nodo: nodoTrie, resultado: list):

        if nodo.fin and nodo.atraccion_id is not None:
            resultado.append({
                "id": nodo.atraccion_id,
                "nombre": nodo.nombre_completo
            })
        for hijo in nodo.hijos.values():
            self._recolectar_palabras_dict(hijo, resultado)

    def autocomplete(self, prefijo: str) -> list[dict]:

        actual = self.raiz
        prefijo_norm = prefijo.lower()
        for simbolo in prefijo_norm:
            if simbolo not in actual.hijos:
                return []  # No hay coincidencias
            actual = actual.hijos[simbolo]

        resultado = []
        self._recolectar_palabras_dict(actual, resultado)
        return resultado
