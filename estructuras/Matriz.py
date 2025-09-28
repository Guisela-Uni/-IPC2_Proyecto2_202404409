from ListaSimple import ListaSimple

class Matriz:
    def __init__(self, filas, columnas):
        self.filas = filas
        self.columnas = columnas
        self.datos = ListaSimple()  # Lista de filas

        for _ in range(filas):
            fila = ListaSimple()
            for _ in range(columnas):
                fila.insertar(0)  
            self.datos.insertar(fila)

    def obtener(self, fila, columna):
        if fila < 0 or fila >= self.filas or columna < 0 or columna >= self.columnas:
            return None
        fila_actual = self.datos.obtener(fila)
        return fila_actual.obtener(columna)

    def asignar(self, fila, columna, valor):
        if fila < 0 or fila >= self.filas or columna < 0 or columna >= self.columnas:
            return False
        fila_actual = self.datos.obtener(fila)
        nodo = fila_actual.primero
        for _ in range(columna):
            nodo = nodo.siguiente
        nodo.info = valor
        return True

    def mostrar(self):
        actual_fila = self.datos.primero
        while actual_fila:
            actual_columna = actual_fila.info.primero
            fila_str = ""
            while actual_columna:
                fila_str += f"{actual_columna.info} "
                actual_columna = actual_columna.siguiente
            print(fila_str.strip())
            actual_fila = actual_fila.siguiente

    