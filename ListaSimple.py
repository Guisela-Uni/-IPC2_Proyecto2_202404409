class Nodo: 
    def __init__(self,info):
        self.info = info
        self.siguiente = None


class ListaSimple: 
    def __init__(self):
        self.primero = None
        self.longitud = 0

    def insertar(self, info):
        nodo = Nodo(info)
        if self.primero is None:
            self.primero = nodo
        else:
            actual = self.primero
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nodo
        self.longitud += 1

    def obtener(self, indice):
        if indice < 0 or indice >= self.longitud:
            return None
        actual = self.primero
        for i in range(indice):
            actual = actual.siguiente
        return actual.info

    def buscar(self, id_buscar): 
        # Busca el índice de un elemento por su id
        actual = self.primero
        indice = 0
        while actual:
            #valida si el dato actual tiene el atributo ID, para devolver el buscado
            if hasattr(actual.info, 'id') and actual.info.id == id_buscar: 
                return indice
            actual = actual.siguiente
            indice += 1
        return -1