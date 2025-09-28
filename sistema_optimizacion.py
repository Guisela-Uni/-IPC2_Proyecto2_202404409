from ListaSimple import ListaSimple
from simulacion_drones import simular_recorrido  

class SistemaOptimizacion:
    def __init__(self, invernadero, plan, aplicar_fertilizante):
        self.invernadero = invernadero
        self.plan = plan
        self.aplicar_fertilizante = aplicar_fertilizante

    def calcular_consumo_por_dron(self):
        #Calcula el consumo total por dron desde la sumulacion
        resumen = ListaSimple()
        nodo_asignacion = self.invernadero.asignaciones.primero

        while nodo_asignacion:
            asignacion = nodo_asignacion.info
            total_litros = 0
            total_gramos = 0

            nodo_planta = self.invernadero.plantas.primero
            while nodo_planta:
                planta = nodo_planta.info
                if planta.hilera == asignacion.hilera and self.hilera_en_plan(planta.hilera):
                    total_litros += planta.litrosAgua
                    if self.aplicar_fertilizante:
                        total_gramos += planta.gramosFertilizante
                nodo_planta = nodo_planta.siguiente

            resumen.insertar({
                'id_dron': asignacion.id_dron,
                'hilera': asignacion.hilera,
                'litros': total_litros,
                'gramos': total_gramos,
                'acciones': 0  
            })
            nodo_asignacion = nodo_asignacion.siguiente

        return resumen

    def hilera_en_plan(self, hilera):
        #Verifica si una hilera aparece en la secuencia del plan.
        if not self.plan or not self.plan.secuencia:
            return False
        secuencia = self.plan.secuencia.split(',')
        for accion in secuencia:
            accion = accion.strip().upper()
            if accion.startswith(f"H{hilera}-"):
                return True
        return False

    #simula el riego paso a paso, devuelve tiempo total y acciones del dron
    def simular_riego_por_dron(self):
        resumen = ListaSimple()
        total_litros_global = 0
        total_gramos_global = 0

        # Inicializar resumen por dron
        nodo_asignacion = self.invernadero.asignaciones.primero
        while nodo_asignacion:
            asignacion = nodo_asignacion.info
            resumen.insertar({
                'id_dron': asignacion.id_dron,
                'hilera': asignacion.hilera,
                'litros': 0,
                'gramos': 0,
                'acciones': 0
            })
            nodo_asignacion = nodo_asignacion.siguiente

        # Validar plan
        if not self.plan or not self.plan.secuencia:
            return resumen, 0, total_litros_global, total_gramos_global

        # Procesar cada acción del plan para calcular consumo
        acciones = self.plan.secuencia.split(',')
        for paso in acciones:
            paso = paso.strip().upper()
            if '-' not in paso:
                continue

            try:
                hilera_txt, posicion_txt = paso.split('-', 1)
                hilera = int(hilera_txt.replace('H', '', 1))
                posicion = int(posicion_txt.replace('P', '', 1))
            except (ValueError, AttributeError):
                continue

            # Buscar planta
            planta_obj = None
            nodo_planta = self.invernadero.plantas.primero
            while nodo_planta:
                planta = nodo_planta.info
                if planta.hilera == hilera and planta.posicion == posicion:
                    planta_obj = planta
                    break
                nodo_planta = nodo_planta.siguiente

            if not planta_obj:
                continue

            # Actualizar dron asignado a esta hilera
            nodo_dron = resumen.primero
            while nodo_dron:
                dron_info = nodo_dron.info
                if dron_info['hilera'] == hilera:
                    dron_info['litros'] += planta_obj.litrosAgua
                    dron_info['acciones'] += 1
                    total_litros_global += planta_obj.litrosAgua
                    if self.aplicar_fertilizante:
                        dron_info['gramos'] += planta_obj.gramosFertilizante
                        total_gramos_global += planta_obj.gramosFertilizante
                    break
                nodo_dron = nodo_dron.siguiente

        # obtiene tiempo real de drones
        try:
            eventos = simular_recorrido(self.invernadero, self.plan)
            # tiempo total = tiempo ultimo evento
            tiempo_total = 0
            actual = eventos.primero
            while actual:
                if actual.info.tiempo > tiempo_total:
                    tiempo_total = actual.info.tiempo
                actual = actual.siguiente
        except Exception as e:
            print(f"Error en simulación para tiempo óptimo: {e}")
            tiempo_total = 0

        return resumen, tiempo_total, total_litros_global, total_gramos_global

    @staticmethod
    def generar_tabla(lista_drones, lista_drones_info, total_litros, total_gramos):
        #Genera una tabla HTML con el resumen del consumo por dron y totales.
        def obtener_nombre_dron(id_dron):
            actual = lista_drones_info.primero
            while actual:
                dron = actual.info
                if dron.id == id_dron:
                    return dron.nombre
                actual = actual.siguiente
            return f"DR{id_dron:02d}"

        html = "<table border='1'>"
        html += "<tr><th>Nombre del Dron</th><th>Hilera</th><th>Litros de Agua</th><th>Gramos de Fertilizante</th><th>Acciones</th></tr>"

        # Variables para totales
        litros_totales = 0
        gramos_totales = 0

        actual = lista_drones.primero
        while actual:
            info = actual.info
            nombre_dron = obtener_nombre_dron(info['id_dron'])
            html += (
                f"<tr>"
                f"<td>{nombre_dron}</td>"
                f"<td>{info['hilera']}</td>"
                f"<td>{info['litros']}</td>"
                f"<td>{info['gramos']}</td>"
                f"<td>{info.get('acciones', 0)}</td>"
                f"</tr>"
            )
            litros_totales += info['litros']
            gramos_totales += info['gramos']
            actual = actual.siguiente

        #Fila con los totales
        html += (
            f"<tr style='font-weight:bold;'>"
            f"<td colspan='2'>TOTAL</td>"
            f"<td>{total_litros}</td>"
            f"<td>{total_gramos}</td>"
            f"<td></td>"
            f"</tr>"
        )

        html += "</table>"
        return html
    