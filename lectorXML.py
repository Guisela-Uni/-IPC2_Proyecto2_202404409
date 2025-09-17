from ListaSimple import ListaSimple
from Invernadero_Clases import Dron, AsignacionDrones as AsignacionDron, plantas as Planta, planesRiego as PlanRiego, Invernadero
from xml.dom.minidom import parse

class carga:
    def __init__(self):
        self.drones = ListaSimple()
        self.invernaderos = ListaSimple()

    def cargar_archivo(self, ruta):
        try:
            dom = parse(ruta)
            print("📂 Cargando archivo XML...")

            # Drones
            drones_xml = dom.getElementsByTagName('dron') #se obtienen todos los nodos <dron> y getElementsByTagName recorre cada nodo
            for dron_xml in drones_xml:
                id_dron = int(dron_xml.getAttribute('id'))
                nombre_dron = dron_xml.getAttribute('nombre')
                dron = Dron(id_dron, nombre_dron) #se encapsula en un objeto Dron
                self.drones.insertar(dron)
                print(f"Dron registrado: {id_dron} - {nombre_dron}")

            # Invernaderos
            invernaderos_xml = dom.getElementsByTagName('invernadero')
            for inv_xml in invernaderos_xml:
                nombre = inv_xml.getAttribute('nombre')
                hileras = int(inv_xml.getElementsByTagName('numeroHileras')[0].firstChild.data.strip())
                plantasXhilera = int(inv_xml.getElementsByTagName('plantasXhilera')[0].firstChild.data.strip())
                invernadero = Invernadero(nombre, hileras, plantasXhilera)
                print(f" Invernadero cargado: {nombre}")

                # Plantas
                plantas_xml = inv_xml.getElementsByTagName('planta')
                for planta_xml in plantas_xml:
                    hilera = int(planta_xml.getAttribute('hilera'))
                    posicion = int(planta_xml.getAttribute('posicion'))
                    litros = int(planta_xml.getAttribute('litrosAgua'))
                    gramos = int(planta_xml.getAttribute('gramosFertilizante'))
                    tipo = planta_xml.firstChild.data.strip()
                    planta = Planta(hilera, posicion, litros, gramos, tipo)
                    invernadero.plantas.insertar(planta)

                print(f" 🌱 Plantas registradas: {plantas_xml.length}")

                # Asignaciones de drones
                asignaciones_xml = inv_xml.getElementsByTagName('dron')
                for asignacion_xml in asignaciones_xml:
                    id_dron = int(asignacion_xml.getAttribute('id'))
                    hilera = int(asignacion_xml.getAttribute('hilera'))
                    asignacion = AsignacionDron(id_dron, hilera)
                    invernadero.asignaciones.insertar(asignacion)

                print(f" Asignaciones de drones: {asignaciones_xml.length}")

                # Planes de riego
                planes_xml = inv_xml.getElementsByTagName('plan')
                for plan_xml in planes_xml:
                    nombre_plan = plan_xml.getAttribute('nombre')
                    acciones = plan_xml.firstChild.data.strip()
                    plan = PlanRiego(nombre_plan, acciones)
                    invernadero.planes.insertar(plan)

                print(f" 💧 Planes de riego cargados: {planes_xml.length}")

                self.invernaderos.insertar(invernadero)

            print("✅ Archivo cargado exitosamente ¡Super!")

        except Exception as e:
            print(f"❌ Error al cargar archivo: {e}")