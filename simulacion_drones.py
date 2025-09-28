from estructuras.Matriz import Matriz
from estructuras.Cola import Cola
from ListaSimple import ListaSimple
from Invernadero_Clases import EstadoDron, Evento, AccionesDron

#construye la matriz de hileras, posiciones
def matriz_plantas(invernadero):
    matriz = Matriz(invernadero.numeroHileras, invernadero.plantasXhilera)
    actual = invernadero.plantas.primero
    while actual:
        planta = actual.info
        matriz.asignar(planta.hilera - 1, planta.posicion - 1, planta)
        actual = actual.siguiente
    return matriz

#crea el recorrido de la matriz plantas
def simular_recorrido(invernadero, plan):
    matriz = matriz_plantas(invernadero)
    tiempo = 0
    eventos = Cola()

    posiciones_dron = ListaSimple()
    estado_drones = ListaSimple()

    # Inicializar los estados del dron
    actual_asignacion = invernadero.asignaciones.primero
    while actual_asignacion:
        asignacion = actual_asignacion.info
        posiciones_dron.insertar(EstadoDron(asignacion.id_dron, 0))
        estado_drones.insertar(AccionesDron(asignacion.id_dron))
        actual_asignacion = actual_asignacion.siguiente

    # Cargar acciones por dron
    acciones = plan.secuencia.split(',')
    for paso in acciones:
        paso = paso.strip().upper()
        if '-' not in paso:
            continue
        hilera_txt, posicion_txt = paso.split('-')
        hilera = int(hilera_txt.replace('H', ''))
        posicion = int(posicion_txt.replace('P', ''))

        actual_asignacion = invernadero.asignaciones.primero
        while actual_asignacion:
            asignacion = actual_asignacion.info
            if asignacion.hilera == hilera:
                acciones_dron = obtener_acciones_dron(estado_drones, asignacion.id_dron)
                if acciones_dron:
                    acciones_dron.Push((hilera - 1, posicion - 1))
                break
            actual_asignacion = actual_asignacion.siguiente

    # Cola de drones activos
    cola_drones = Cola()
    actual_estado = estado_drones.primero
    while actual_estado:
        cola_drones.Push(actual_estado.info.id_dron)
        actual_estado = actual_estado.siguiente

    while not cola_drones.estaVacia():
        dron_id = cola_drones.Pop()
        acciones_dron = obtener_acciones_dron(estado_drones, dron_id)
        estado_dron = obtener_estado_dron(posiciones_dron, dron_id)

        if acciones_dron.estaVacia():
            eventos.Push(Evento(tiempo, dron_id, "FIN"))
            continue

        hilera, posicion = acciones_dron.Pop()
        distancia = valor_absoluto(posicion - estado_dron.posicion_actual)

        for _ in range(distancia):
            tiempo += 1
            eventos.Push(Evento(tiempo, dron_id, f"Adelante (H{hilera+1}P{estado_dron.posicion_actual+1})"))
            estado_dron.posicion_actual += 1

        tiempo += 1
        eventos.Push(Evento(tiempo, dron_id, "Regar"))

        if not acciones_dron.estaVacia():
            cola_drones.Push(dron_id)

    return eventos


# FUNCIONES para simular mi recorrido
def obtener_estado_dron(lista, id_dron):
    actual = lista.primero
    while actual:
        estado = actual.info
        if estado.id_dron == id_dron:
            return estado
        actual = actual.siguiente
    return None

def obtener_acciones_dron(lista, id_dron):
    actual = lista.primero
    while actual:
        acciones = actual.info
        if acciones.id_dron == id_dron:
            return acciones.acciones
        actual = actual.siguiente
    return None

def buscar_tiempo(tabla, tiempo):
    actual = tabla.primero
    while actual:
        if actual.info['tiempo'] == tiempo:
            return actual.info
        actual = actual.siguiente
    return None

def buscar_dron(lista, id_dron):
    actual = lista.primero
    while actual:
        if actual.info == id_dron:
            return True
        actual = actual.siguiente
    return False

def buscar_accion(lista_acciones, id_dron):
    actual = lista_acciones.primero
    while actual:
        if actual.info[0] == id_dron:
            return actual.info[1]
        actual = actual.siguiente
    return ""

def valor_absoluto(n):
    if n < 0:
        return -n
    return n

def iterar_lista(lista_simple):
    actual = lista_simple.primero
    while actual:
        yield actual.info
        actual = actual.siguiente

# funcion para generar mi tabla        
def generar_tabla_eventos(eventos):
    tiempos = ListaSimple()
    tabla = ListaSimple()

    actual = eventos.primero
    while actual:
        evento = actual.info
        tiempo_actual = buscar_tiempo(tabla, evento.tiempo)
        if not tiempo_actual:
            nuevo_tiempo = {'tiempo': evento.tiempo, 'acciones': ListaSimple()}
            nuevo_tiempo['acciones'].insertar((evento.id_dron, evento.accion))
            tabla.insertar(nuevo_tiempo)
            tiempos.insertar(evento.tiempo)
        else:
            tiempo_actual['acciones'].insertar((evento.id_dron, evento.accion))
        actual = actual.siguiente

    # Obtener lista de drones únicos
    drones = ListaSimple()
    actual_evento = eventos.primero
    while actual_evento:
        id_dron = actual_evento.info.id_dron
        if not buscar_dron(drones, id_dron):
            drones.insertar(id_dron)
        actual_evento = actual_evento.siguiente

    # Construir HTML
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
            accion = buscar_accion(actual_tiempo.info['acciones'], d)
            html += f"<td>{accion}</td>"
        html += "</tr>"
        actual_tiempo = actual_tiempo.siguiente

    html += "</table>"
    return html