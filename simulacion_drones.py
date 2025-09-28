from estructuras.Matriz import Matriz
from estructuras.Cola import Cola
from ListaSimple import ListaSimple
from Invernadero_Clases import Evento

# Clase auxiliar para el estado de un dron
class EstadoDronSim:
    def __init__(self, id_dron, hilera, posicion_inicial=0):
        self.id_dron = id_dron
        self.hilera = hilera
        self.posicion_actual = posicion_inicial
        self.cola_posiciones = Cola()  # Cola de posiciones pendientes

# Clase auxiliar para mapeo hilera-dron
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

# Simulación de el recorrido de los drones
def simular_recorrido(invernadero, plan):
    if not plan or not hasattr(plan, 'secuencia') or not isinstance(plan.secuencia, str):
        eventos = Cola()
        eventos.Push(Evento(0, "Sistema", "Plan inválido"))
        return eventos

    # se parsea el plan en una Cola de acciones (hilera, posicion)
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

    #  Crea el  mapeo hilera, dron
    mapeo_hilera_dron = ListaSimple()
    actual_asignacion = invernadero.asignaciones.primero
    while actual_asignacion:
        asignacion = actual_asignacion.info
        mapeo_hilera_dron.insertar(MapeoHileraDron(asignacion.hilera, asignacion.id_dron))
        actual_asignacion = actual_asignacion.siguiente

    # inicializar estado de drones y sus rutas
    estados_drones = ListaSimple()
    # Primero, crear entrada para cada dron que aparece en el plan
    temp_acciones = Cola()
    while not cola_acciones_plan.estaVacia():
        accion = cola_acciones_plan.Pop()
        temp_acciones.Push(accion)
        hilera = accion.primero.info
        id_dron = buscar_dron_por_hilera(mapeo_hilera_dron, hilera)
        if id_dron is not None:
            # Verifica si ya existe el estado
            estado_existente = buscar_estado_dron(estados_drones, id_dron)
            if estado_existente is None:
                # Encontrar hilera del dron
                hilera_dron = None
                actual_mapeo = mapeo_hilera_dron.primero
                while actual_mapeo:
                    mapeo = actual_mapeo.info
                    if mapeo.id_dron == id_dron:
                        hilera_dron = mapeo.hilera
                        break
                    actual_mapeo = actual_mapeo.siguiente
                estados_drones.insertar(EstadoDronSim(id_dron, hilera_dron))

    # Restaurar cola_acciones_plan
    while not temp_acciones.estaVacia():
        cola_acciones_plan.Push(temp_acciones.Pop())

    # asignar las posiciones a las colas de cada dron
    temp_acciones2 = Cola()
    while not cola_acciones_plan.estaVacia():
        accion = cola_acciones_plan.Pop()
        temp_acciones2.Push(accion)
        hilera = accion.primero.info
        posicion = accion.primero.siguiente.info
        id_dron = buscar_dron_por_hilera(mapeo_hilera_dron, hilera)
        if id_dron is not None:
            estado = buscar_estado_dron(estados_drones, id_dron)
            if estado:
                estado.cola_posiciones.Push(posicion)

    acciones_plan = ListaSimple()  # Lista de ListaSimple([hilera, posicion])
    while not temp_acciones2.estaVacia():
        accion = temp_acciones2.Pop()
        acciones_plan.insertar(accion)

    # Simulación de drones en el campo
    eventos = Cola()
    tiempo = 0
    contador_accion = 0  # contador para acciones

    # contador del total de acciones
    total_acciones = 0
    actual_accion = acciones_plan.primero
    while actual_accion:
        total_acciones += 1
        actual_accion = actual_accion.siguiente

    while contador_accion < total_acciones:
        tiempo += 1
        # Obtener la acción actual (hilera, posicion)
        actual_accion = acciones_plan.primero
        contador = 0
        while actual_accion and contador < contador_accion:
            actual_accion = actual_accion.siguiente
            contador += 1
        if not actual_accion:
            break
        hilera_obj = actual_accion.info.primero.info
        posicion_obj = actual_accion.info.primero.siguiente.info

        # Todos los drones se mueven 1 paso hacia su proxima posicion
        actual_estado = estados_drones.primero
        while actual_estado:
            estado = actual_estado.info
            if not estado.cola_posiciones.estaVacia():

                # Ver la próxima posición sin sacarla
                pos_temp = Cola()
                proxima_pos = None
                while not estado.cola_posiciones.estaVacia():
                    item = estado.cola_posiciones.Pop()
                    if proxima_pos is None:
                        proxima_pos = item
                    pos_temp.Push(item)
                # Restaurar cola
                while not pos_temp.estaVacia():
                    estado.cola_posiciones.Push(pos_temp.Pop())
                pos_temp = None

                if proxima_pos is not None:
                    if estado.posicion_actual < proxima_pos:
                        estado.posicion_actual += 1
                        eventos.Push(Evento(tiempo, estado.id_dron, f"Adelante (H{estado.hilera}P{estado.posicion_actual})"))
                    elif estado.posicion_actual > proxima_pos:
                        estado.posicion_actual -= 1
                        eventos.Push(Evento(tiempo, estado.id_dron, f"Atrás (H{estado.hilera}P{estado.posicion_actual})"))
            actual_estado = actual_estado.siguiente

        # Verifica si el dron de la acción actual puede regar
        id_dron_obj = buscar_dron_por_hilera(mapeo_hilera_dron, hilera_obj)
        if id_dron_obj is not None:
            estado_obj = buscar_estado_dron(estados_drones, id_dron_obj)
            if estado_obj and estado_obj.posicion_actual == posicion_obj:
                # Verifica que la próxima posición en su cola 
                if not estado_obj.cola_posiciones.estaVacia():
                    primera_pos = estado_obj.cola_posiciones.Pop()  # Sacar la posición
                    if primera_pos == posicion_obj:
                        eventos.Push(Evento(tiempo, id_dron_obj, "Regar"))
                        contador_accion += 1  # Avanzar en el plan
                    else:
                        # Volver a meter la posición 
                        estado_obj.cola_posiciones.Push(primera_pos) # Si no se riega, los drones se siguen boviendo

    # Eventos de finalización
    actual_estado = estados_drones.primero
    while actual_estado:
        estado = actual_estado.info
        tiempo += 1
        eventos.Push(Evento(tiempo, estado.id_dron, "FIN"))
        actual_estado = actual_estado.siguiente

    return eventos

# funciones para la creacion de la tabla html

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
            
            # Verificar si el dron ya terminó ANTES de este tiempo
            ya_termino_antes = False
            actual_fin = fin_drones.primero
            while actual_fin:
                fin_info = actual_fin.info
                if fin_info[0] == d and fin_info[1] < tiempo:  #si terminó ANTES
                    ya_termino_antes = True
                    break
                actual_fin = actual_fin.siguiente

            if ya_termino_antes:
                html += "<td></td>"  # Celda vacía si ya terminó en un tiempo anterior
            elif accion == "":
                html += "<td>Espera</td>"
            else:
                html += f"<td>{accion}</td>"  # "FIN" en si ya termino
        html += "</tr>"
        actual_tiempo = actual_tiempo.siguiente

    html += "</table>"
    return html