from ListaSimple import ListaSimple

class SistemaOptimizacion:
    def __init__(self, invernadero, plan, aplicar_fertilizante):
        self.invernadero = invernadero
        self.plan = plan
        self.aplicar_fertilizante = aplicar_fertilizante

    def calcular_consumo_por_dron(self):
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
                'gramos': total_gramos
            })
            nodo_asignacion = nodo_asignacion.siguiente

        return resumen

    def hilera_en_plan(self, hilera):
        secuencia = self.plan.secuencia.split(',')
        for accion in secuencia:
            accion = accion.strip().upper()
            if accion.startswith(f"H{hilera}-"):
                return True
        return False

    def simular_riego_por_dron(self):
        resumen = ListaSimple()
        tiempo_total = 0

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

        # Recorrer el plan paso por paso
        acciones = self.plan.secuencia.split(',')
        for paso in acciones:
            paso = paso.strip().upper()
            if '-' not in paso:
                continue

            hilera_txt, posicion_txt = paso.split('-')
            try:
                hilera = int(hilera_txt.replace('H', ''))
                posicion = int(posicion_txt.replace('P', ''))
            except:
                continue

            # Buscar planta
            nodo_planta = self.invernadero.plantas.primero
            planta_obj = None
            while nodo_planta:
                planta = nodo_planta.info
                if planta.hilera == hilera and planta.posicion == posicion:
                    planta_obj = planta
                    break
                nodo_planta = nodo_planta.siguiente
            if not planta_obj:
                continue

            # Buscar dron asignado
            nodo_dron = resumen.primero
            while nodo_dron:
                dron_info = nodo_dron.info
                if dron_info['hilera'] == hilera:
                    dron_info['litros'] += planta_obj.litrosAgua
                    if self.aplicar_fertilizante:
                        dron_info['gramos'] += planta_obj.gramosFertilizante
                    dron_info['acciones'] += 1
                    tiempo_total += 1
                    break
                nodo_dron = nodo_dron.siguiente

        return resumen, tiempo_total

    @staticmethod
    def generar_tabla(lista_drones, lista_drones_info):
        html = "<table border='1'>"
        html += "<tr><th>Nombre del Dron</th><th>Hilera</th><th>Litros de Agua</th><th>Gramos de Fertilizante</th><th>Acciones</th></tr>"

        def obtener_nombre_dron(lista_drones_info, id_dron):
            actual = lista_drones_info.primero
            while actual:
                dron = actual.info
                if dron.id == id_dron:
                    return dron.nombre
                actual = actual.siguiente
            return f"DR{str(id_dron).zfill(2)}"

        actual = lista_drones.primero
        while actual:
            info = actual.info
            nombre_dron = obtener_nombre_dron(lista_drones_info, info['id_dron'])
            html += f"<tr><td>{nombre_dron}</td><td>{info['hilera']}</td><td>{info['litros']}</td><td>{info['gramos']}</td><td>{info.get('acciones', 0)}</td></tr>"
            actual = actual.siguiente

        return html
            
    