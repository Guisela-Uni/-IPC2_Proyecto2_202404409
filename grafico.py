from Invernadero_Clases import planRiego as PlanRiego
from simulacion_drones import simular_recorrido, buscar_dron_en_lista, iterar_lista
from ListaSimple import ListaSimple
import os

class NodoTiempo:
    #almacena tiempo y estado
    def __init__(self, tiempo, estado_str):
        self.tiempo = tiempo
        self.estado_str = estado_str

#funcion que genera un grafo DOT con el estado de los drones, por segundo
def generar_dot_estados(invernadero, plan:PlanRiego, tiempo_analisis, nombre_archivo):

    if tiempo_analisis <= 0:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write('digraph Error {\n')
            f.write('  "Número inválido" [shape=box, style=filled, color=red, fontsize=16];\n')
            f.write('}\n')
        return

    # Simular recorrido
    try:
        eventos = simular_recorrido(invernadero, plan)
    except Exception as e:
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write('digraph Error {\n')
            f.write('  "Error en simulación" [shape=box, style=filled, color=red, fontsize=16];\n')
            f.write('}\n')
        return

    if eventos.estaVacia():
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write('digraph Error {\n')
            f.write('  "No hay eventos" [shape=box, style=filled, color=orange, fontsize=16];\n')
            f.write('}\n')
        return

    # Obtener lista de drones únicos
    drones = ListaSimple()
    actual_evento = eventos.primero
    while actual_evento:
        id_dron = actual_evento.info.id_dron
        if not buscar_dron_en_lista(drones, id_dron):
            drones.insertar(id_dron)
        actual_evento = actual_evento.siguiente

    # Construir tabla de eventos por tiempo, [tiempo,acciones]
    tabla_tiempos = ListaSimple()
    actual_evento = eventos.primero
    while actual_evento:
        evento = actual_evento.info
        # Buscar si ya existe el tiempo
        nodo_tiempo = tabla_tiempos.primero
        tiempo_info = None
        while nodo_tiempo:
            if nodo_tiempo.info['tiempo'] == evento.tiempo:
                tiempo_info = nodo_tiempo.info
                break
            nodo_tiempo = nodo_tiempo.siguiente
        if tiempo_info is None:
            nuevo_tiempo = {'tiempo': evento.tiempo, 'acciones': ListaSimple()}
            nuevo_tiempo['acciones'].insertar((evento.id_dron, evento.accion))
            tabla_tiempos.insertar(nuevo_tiempo)
        else:
            tiempo_info['acciones'].insertar((evento.id_dron, evento.accion))
        actual_evento = actual_evento.siguiente

    # Encontrar tiempo optimo
    tiempo_max = 0
    nodo_tiempo = tabla_tiempos.primero
    while nodo_tiempo:
        if nodo_tiempo.info['tiempo'] > tiempo_max:
            tiempo_max = nodo_tiempo.info['tiempo']
        nodo_tiempo = nodo_tiempo.siguiente

    # Ajustar al tiempo maximo si se pasa de segundos ingresados
    tiempo_limite = tiempo_analisis
    if tiempo_analisis > tiempo_max:
        tiempo_limite = tiempo_max

    # Crear lista de estados por tiempo lista de nodo
    estados_lista = ListaSimple()
    t = 1
    while t <= tiempo_limite:
        estado_lineas = ListaSimple()
        estado_lineas.insertar(f"t={t}")

        # Verificar drones terminados antes de este tiempo
        drones_terminados = ListaSimple()
        actual_ev = eventos.primero
        while actual_ev:
            ev = actual_ev.info
            if ev.accion == "FIN" and ev.tiempo < t:
                if not buscar_dron_en_lista(drones_terminados, ev.id_dron):
                    drones_terminados.insertar(ev.id_dron)
            actual_ev = actual_ev.siguiente

        # construye el estado de cada dron
        for dron_id in iterar_lista(drones):
            if buscar_dron_en_lista(drones_terminados, dron_id):
                accion_str = ""
            else:
                # Buscar acción en este tiempo
                accion = ""
                nodo_tiempo = tabla_tiempos.primero
                while nodo_tiempo:
                    if nodo_tiempo.info['tiempo'] == t:
                        nodo_accion = nodo_tiempo.info['acciones'].primero
                        while nodo_accion:
                            if nodo_accion.info[0] == dron_id:
                                accion = nodo_accion.info[1]
                                break
                            nodo_accion = nodo_accion.siguiente
                        break
                    nodo_tiempo = nodo_tiempo.siguiente
                if accion == "":
                    accion_str = "Espera"
                else:
                    accion_str = accion
            if accion_str != "":
                estado_lineas.insertar(f"DR{str(dron_id).zfill(2)}: {accion_str}")

        # Convierte la lista a una cadena
        estado_str = ""
        nodo_linea = estado_lineas.primero
        while nodo_linea:
            if estado_str == "":
                estado_str = nodo_linea.info
            else:
                estado_str += "\\n" + nodo_linea.info
            nodo_linea = nodo_linea.siguiente

        estados_lista.insertar(NodoTiempo(t, estado_str))
        t += 1

    # Genera el archivo DOT
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("digraph EstadosDrones {\n")
        f.write('  label="Estados de Drones por Segundo";\n')
        f.write('  labelloc="t";\n')
        f.write('  fontsize=20;\n')
        f.write('  node [shape=box, style=filled, color=lightcyan];\n')
        f.write('  rankdir=LR;\n')

        # Escribir nodos
        nodo_estado = estados_lista.primero
        while nodo_estado:
            nt = nodo_estado.info
            f.write(f'  "t={nt.tiempo}" [label="{nt.estado_str}"];\n')
            nodo_estado = nodo_estado.siguiente

        # Escribir flechas con lista de tiempos
        tiempos_secuencia = ListaSimple()
        nodo_estado = estados_lista.primero
        while nodo_estado:
            tiempos_secuencia.insertar(nodo_estado.info.tiempo)
            nodo_estado = nodo_estado.siguiente

        # Generar flechas entre tiempos consecutivos
        nodo_actual = tiempos_secuencia.primero
        while nodo_actual and nodo_actual.siguiente:
            f.write(f'  "t={nodo_actual.info}" -> "t={nodo_actual.siguiente.info}";\n')
            nodo_actual = nodo_actual.siguiente

        f.write("}\n")

#genera png del dot
def generar_imagen_dot(nombre_dot, nombre_png):
    os.system(f'dot -Tpng "{nombre_dot}" -o "{nombre_png}"')