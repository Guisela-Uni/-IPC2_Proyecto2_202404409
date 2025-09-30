from estructuras.Matriz import Matriz
from estructuras.Cola import Cola
from ListaSimple import ListaSimple
from Invernadero_Clases import Evento

# estado de un dron
class EstadoDronSim:
    def __init__(self, id_dron, hilera, posicion_inicial=0):
        self.id_dron = id_dron
        self.hilera = hilera
        self.posicion_actual = posicion_inicial
        self.cola_posiciones = Cola()  # Cola de posiciones pendientes

# mapeo hilera-dron
class MapeoHileraDron:
    def __init__(self, hilera, id_dron):
        self.hilera = hilera
        self.id_dron = id_dron

# Construye la matriz de hileras, posiciones
def matriz_plantas(invernadero):
    matriz = Matriz(invernadero.numeroHileras, invernadero.plantasXhilera)
    actual = invernadero.plantas.primero
    while actual:
        planta = actual.info
        matriz.asignar(planta.hilera - 1, planta.posicion - 1, planta)
        actual = actual.siguiente
    return matriz

# Buscar dron por hilera en la lista de mapeo
def buscar_dron_por_hilera(lista_mapeo, hilera):
    actual = lista_mapeo.primero
    while actual:
        mapeo = actual.info
        if mapeo.hilera == hilera:
            return mapeo.id_dron
        actual = actual.siguiente
    return None

# Buscar estado de dron por id
def buscar_estado_dron(lista_estados, id_dron):
    actual = lista_estados.primero
    while actual:
        estado = actual.info
        if estado.id_dron == id_dron:
            return estado
        actual = actual.siguiente
    return None

# Simulación del recorrido de los drones
def simular_recorrido(invernadero, plan):
    if not plan or not hasattr(plan, 'secuencia') or not isinstance(plan.secuencia, str):
        eventos = Cola()
        eventos.Push(Evento(0, "Sistema", "Plan inválido"))
        return eventos

    # Parsear el plan en una Cola de acciones (hilera, posicion)
    cola_acciones_plan = Cola()
    acciones = plan.secuencia.split(',')
    for paso in acciones:
        paso = paso.strip().upper()
        if '-' not in paso:
            continue
        try:
            partes = paso.split('-', 1)
            hilera_txt = partes[0].replace('H', '', 1)
            posicion_txt = partes[1].replace('P', '', 1)
            hilera = int(hilera_txt)
            posicion = int(posicion_txt)
            accion = ListaSimple()
            accion.insertar(hilera)
            accion.insertar(posicion)
            cola_acciones_plan.Push(accion)
        except:
            continue

    if cola_acciones_plan.estaVacia():
        eventos = Cola()
        eventos.Push(Evento(0, "Sistema", "Plan vacío"))
        return eventos

    # Crear el mapeo hilera -> dron
    mapeo_hilera_dron = ListaSimple()
    actual_asignacion = invernadero.asignaciones.primero
    while actual_asignacion:
        asignacion = actual_asignacion.info
        mapeo_hilera_dron.insertar(MapeoHileraDron(asignacion.hilera, asignacion.id_dron))
        actual_asignacion = actual_asignacion.siguiente

    # Inicializar estado de drones
    estados_drones = ListaSimple()
    temp_acciones = Cola()
    
    # recolectar todos los drones involucrados y crear sus estados
    while not cola_acciones_plan.estaVacia():
        accion = cola_acciones_plan.Pop()
        temp_acciones.Push(accion)
        hilera = accion.primero.info
        id_dron = buscar_dron_por_hilera(mapeo_hilera_dron, hilera)
        if id_dron is not None:
            estado_existente = buscar_estado_dron(estados_drones, id_dron)
            if estado_existente is None:
                # Encontrar la hilera asignada al dron
                hilera_dron = None
                actual_mapeo = mapeo_hilera_dron.primero
                while actual_mapeo:
                    mapeo = actual_mapeo.info
                    if mapeo.id_dron == id_dron:
                        hilera_dron = mapeo.hilera
                        break
                    actual_mapeo = actual_mapeo.siguiente
                estados_drones.insertar(EstadoDronSim(id_dron, hilera_dron))

    
    acciones_plan = ListaSimple()
    while not temp_acciones.estaVacia():
        accion = temp_acciones.Pop()
        cola_acciones_plan.Push(accion)
        acciones_plan.insertar(accion)

   
    actual_accion = acciones_plan.primero
    while actual_accion:
        accion = actual_accion.info
        hilera = accion.primero.info
        posicion = accion.primero.siguiente.info
        id_dron = buscar_dron_por_hilera(mapeo_hilera_dron, hilera)
        if id_dron is not None:
            estado = buscar_estado_dron(estados_drones, id_dron)
            if estado:
                estado.cola_posiciones.Push(posicion)
        actual_accion = actual_accion.siguiente

   
    eventos = Cola()
    tiempo = 0

   
    total_acciones = 0
    nodo = acciones_plan.primero
    while nodo:
        total_acciones += 1
        nodo = nodo.siguiente

    acciones_completadas = 0

    while acciones_completadas < total_acciones:
        tiempo += 1

        actual_estado = estados_drones.primero
        while actual_estado:
            estado = actual_estado.info
            if not estado.cola_posiciones.estaVacia():
                # Ver la próxima posición sin sacarla
                temp_cola = Cola()
                prox_pos = None
                while not estado.cola_posiciones.estaVacia():
                    item = estado.cola_posiciones.Pop()
                    if prox_pos is None:
                        prox_pos = item
                    temp_cola.Push(item)
                # Restaurar la cola
                while not temp_cola.estaVacia():
                    estado.cola_posiciones.Push(temp_cola.Pop())

                if prox_pos is not None:
                    if estado.posicion_actual < prox_pos:
                        estado.posicion_actual += 1
                        eventos.Push(Evento(tiempo, estado.id_dron, f"Adelante (H{estado.hilera}P{estado.posicion_actual})"))
                    elif estado.posicion_actual > prox_pos:
                        estado.posicion_actual -= 1
                        eventos.Push(Evento(tiempo, estado.id_dron, f"Atrás (H{estado.hilera}P{estado.posicion_actual})"))
            actual_estado = actual_estado.siguiente

        actual_estado = estados_drones.primero
        while actual_estado:
            estado = actual_estado.info
            if not estado.cola_posiciones.estaVacia():
                # Ver la próxima posición
                temp_cola = Cola()
                prox_pos = None
                while not estado.cola_posiciones.estaVacia():
                    item = estado.cola_posiciones.Pop()
                    if prox_pos is None:
                        prox_pos = item
                    temp_cola.Push(item)
                while not temp_cola.estaVacia():
                    estado.cola_posiciones.Push(temp_cola.Pop())

                if prox_pos is not None and estado.posicion_actual == prox_pos:
                    # ¡Regar!
                    estado.cola_posiciones.Pop()  # Eliminar la posición regada
                    eventos.Push(Evento(tiempo, estado.id_dron, "Regar"))
                    acciones_completadas += 1
            actual_estado = actual_estado.siguiente

    actual_estado = estados_drones.primero
    while actual_estado:
        estado = actual_estado.info
        tiempo += 1
        eventos.Push(Evento(tiempo, estado.id_dron, "FIN"))
        actual_estado = actual_estado.siguiente

    return eventos


# TABLA HTML

def buscar_tiempo(tabla, tiempo):
    actual = tabla.primero
    while actual:
        if actual.info['tiempo'] == tiempo:
            return actual.info
        actual = actual.siguiente
    return None

def buscar_dron_en_lista(lista, id_dron):
    actual = lista.primero
    while actual:
        if actual.info == id_dron:
            return True
        actual = actual.siguiente
    return False

def obtener_accion_en_tiempo(lista_acciones, id_dron):
    actual = lista_acciones.primero
    while actual:
        if actual.info[0] == id_dron:
            return actual.info[1]
        actual = actual.siguiente
    return ""

def iterar_lista(lista_simple):
    actual = lista_simple.primero
    while actual:
        yield actual.info
        actual = actual.siguiente

def generar_tabla_eventos(eventos):
    if eventos.estaVacia():
        return "<p>No hay eventos para mostrar.</p>"

    tabla = ListaSimple()
    drones = ListaSimple()
    fin_drones = ListaSimple()  # (id_dron, tiempo_fin)

    actual = eventos.primero
    while actual:
        evento = actual.info
        if not buscar_dron_en_lista(drones, evento.id_dron):
            drones.insertar(evento.id_dron)
        if evento.accion == "FIN":
            fin_drones.insertar((evento.id_dron, evento.tiempo))
        tiempo_actual = buscar_tiempo(tabla, evento.tiempo)
        if not tiempo_actual:
            nuevo_tiempo = {'tiempo': evento.tiempo, 'acciones': ListaSimple()}
            nuevo_tiempo['acciones'].insertar((evento.id_dron, evento.accion))
            tabla.insertar(nuevo_tiempo)
        else:
            tiempo_actual['acciones'].insertar((evento.id_dron, evento.accion))
        actual = actual.siguiente

    html = "<table border='1'><tr><th>Tiempo</th>"
    actual_dron = drones.primero
    while actual_dron:
        html += f"<th>DR{str(actual_dron.info).zfill(2)}</th>"
        actual_dron = actual_dron.siguiente
    html += "</tr>"

    actual_tiempo = tabla.primero
    while actual_tiempo:
        tiempo = actual_tiempo.info['tiempo']
        html += f"<tr><td>{tiempo} segundos</td>"
        for d in iterar_lista(drones):
            accion = obtener_accion_en_tiempo(actual_tiempo.info['acciones'], d)
            
            # Verificar si el dron ya terminó antes de este tiempo
            ya_termino_antes = False
            actual_fin = fin_drones.primero
            while actual_fin:
                fin_info = actual_fin.info
                if fin_info[0] == d and fin_info[1] < tiempo:
                    ya_termino_antes = True
                    break
                actual_fin = actual_fin.siguiente

            if ya_termino_antes:
                html += "<td></td>"
            elif accion == "":
                html += "<td>Espera</td>"
            else:
                html += f"<td>{accion}</td>"
        html += "</tr>"
        actual_tiempo = actual_tiempo.siguiente

    html += "</table>"
    return html
