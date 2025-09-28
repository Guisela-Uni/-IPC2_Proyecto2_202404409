from xml.dom.minidom import parse
from ListaSimple import ListaSimple
from Invernadero_Clases import Dron, AsignacionDrones as AsignacionDron, plantas as Planta, planRiego as PlanRiego, Invernadero

class carga:
    def __init__(self):
        self.drones = ListaSimple() # Lista de drones 
        self.invernaderos = ListaSimple()# Lista de invernaderos

    def cargar_archivo(self, ruta):
        try:
            dom = parse(ruta)

            # Drones, carga la lista de drones
            ListaDrones = dom.getElementsByTagName('listaDrones')
            if ListaDrones:
                lista_drones = ListaDrones[0]
                for dron_xml in lista_drones.getElementsByTagName('dron'):
                    #try except para evitar errores si el id no es un entero
                    try:
                        id_dron = int(dron_xml.getAttribute('id'))
                    except Exception:
                        # salta si el id no es válido
                        continue
                    nombre_dron = dron_xml.getAttribute('nombre')
                    self.drones.insertar(Dron(id_dron, nombre_dron))

            # Invernaderos
            ListaInvernaderos = dom.getElementsByTagName('listaInvernaderos')
            if not ListaInvernaderos:
                print("Advertencia: no se encontró el nodo <listaInvernaderos>")
                return
            lista_invernaderos = ListaInvernaderos[0]
            for inv_xml in lista_invernaderos.getElementsByTagName('invernadero'):
                nombre = inv_xml.getAttribute('nombre')
                hileras = int(inv_xml.getElementsByTagName('numeroHileras')[0].firstChild.data.strip())
                plantasXhilera = int(inv_xml.getElementsByTagName('plantasXhilera')[0].firstChild.data.strip())
                invernadero = Invernadero(nombre, hileras, plantasXhilera)
                print("Invernaderos encontrados:", len(dom.getElementsByTagName('invernadero')))

                # Plantas
                ListaPlantas = inv_xml.getElementsByTagName('listaPlantas')
                if ListaPlantas:
                    lista_plantas = ListaPlantas[0]
                    for planta_xml in lista_plantas.getElementsByTagName('planta'):
                        #try except para evitar errores, si faltan atributos o no son enteros, saltar esta planta
                        try:
                            hilera = int(planta_xml.getAttribute('hilera'))
                            posicion = int(planta_xml.getAttribute('posicion'))
                            litros = int(planta_xml.getAttribute('litrosAgua'))
                            gramos = int(planta_xml.getAttribute('gramosFertilizante'))
                        except Exception:
                            continue
                        tipo = planta_xml.firstChild.data.strip() if planta_xml.firstChild else ""
                        invernadero.plantas.insertar(Planta(hilera, posicion, litros, gramos, tipo))

                # Asignacione de drones
                AsignacionesDrones = inv_xml.getElementsByTagName('asignacionDrones')
                if AsignacionesDrones:
                    asignaciones = AsignacionesDrones[0]
                    for asignacion_xml in asignaciones.getElementsByTagName('dron'):
                        try:
                            id_dron = int(asignacion_xml.getAttribute('id'))
                            hilera = int(asignacion_xml.getAttribute('hilera'))
                        except Exception:
                            continue
                        invernadero.asignaciones.insertar(AsignacionDron(id_dron, hilera))

                # Planes de riego
                planes_nodes = inv_xml.getElementsByTagName('planesRiego')
                if planes_nodes:
                    planes = planes_nodes[0]
                    for plan_xml in planes.getElementsByTagName('plan'):
                        nombre_plan = plan_xml.getAttribute('nombre')
                        acciones = plan_xml.firstChild.data.strip() if plan_xml.firstChild else ""
                        invernadero.planes.insertar(PlanRiego(nombre_plan, acciones))

                self.invernaderos.insertar(invernadero)
                print("Invernadero insertado:", invernadero.nombre)

        #error general al cargar el archivo
        except Exception as e:
            print("Error al cargar archivo:", e)
    
    def buscar_invernadero(self, nombre):
        actual = self.invernaderos.primero
        while actual:
            if actual.info.nombre == nombre:
                return actual.info
            actual = actual.siguiente
        return None
    
    def buscar_plan(self, invernadero, nombre_plan):
        actual = invernadero.planes.primero
        while actual:
            if actual.info.nombre == nombre_plan:
                return actual.info
            actual = actual.siguiente
        return None