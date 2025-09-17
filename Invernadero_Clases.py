from ListaSimple import ListaSimple

class Dron: #objetos Dron, para usar en la lista de drones
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre

class AsignacionDrones: #lista de los drones asignados a cada 
    def __init__(self, id_dron, hilera):
        self.id_dron = id_dron
        self.hilera = hilera

class plantas:
    def __init__(self,hilera, posicion, litrosAgua, gramosFertilizante, tipo):
        self.hilera = hilera
        self.posicion = posicion
        self.litrosAgua = litrosAgua
        self.gramosFertilizante = gramosFertilizante
        self.tipo = tipo


class planRiego:
    def __init__(self, secuencia, nombre):
        self.nombre= nombre
        self.secuencia = secuencia

class Invernadero: #objeto Invernadero, contiene listas de plantas, asignaciones y planes
    def __init__(self, nombre, numeroHileras, plantasXhilera):
        self.nombre = nombre #nombre del invernadero
        self.numeroHileras = numeroHileras
        self.plantasXhilera = plantasXhilera
        self.plantas = ListaSimple()  # Lista de plantas en el invernadero
        self.asignaciones = ListaSimple()  # Lista de asignaciones de drones
        self.planes = ListaSimple()  # Lista de planes de riego

    def agregar_planta(self, planta):
        self.plantas.append(planta)

    def agregar_asignacion(self, asignacion):
        self.asignaciones.append(asignacion)

    def agregar_plan(self, plan):
        self.planes.append(plan)