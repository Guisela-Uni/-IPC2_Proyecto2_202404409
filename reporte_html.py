from sistema_optimizacion import SistemaOptimizacion
from simulacion_drones import simular_recorrido, generar_tabla_eventos
import xml.etree.ElementTree as ET

class ReporteHTML:

    def generar_reporte(self, cargador, ruta_salida):
        html = """
        <!DOCTYPE html>
        <html lang='es'>
        <head>
            <meta charset='UTF-8'>
            <meta name='viewport' content='width=device-width, initial-scale=1.0'>
            <title>Reporte de Invernaderos</title>
            <style>
                table {border-collapse: collapse; width: 100%; margin-bottom: 30px;}
                h2 {margin-top: 50px; color: #2ab792}
                h3 {color: #6ae943;margin-top: 20px;margin-bottom: 5px;}
                hr {margin: 50px 0;}
                h1 {text-align: center;margin-bottom: 10px; color: #43e97b}
                th, td {border: 1px solid #ccc;padding: 8px;text-align: left;}
                th {background-color: #43e97b;}
            </style>
        </head>
        <body>
        <h1>Reporte Completo de Invernaderos</h1>
        """

        actual_inv = cargador.invernaderos.primero
        while actual_inv:
            invernadero = actual_inv.info
            html += f"<h2>{invernadero.nombre}</h2>"

            # Toma el primer plan de riego
            plan = invernadero.planes.primero.info if invernadero.planes.primero else None
            if not plan:
                html += "<p>No hay planes de riego definidos.</p><hr>"
                actual_inv = actual_inv.siguiente
                continue

            # Simulación de optimización
            sistema = SistemaOptimizacion(invernadero, plan, aplicar_fertilizante=True)
            resumen, tiempo_total, total_litros, total_gramos = sistema.simular_riego_por_dron()
            tabla_consumo = sistema.generar_tabla(resumen, cargador.drones, total_litros, total_gramos)
            html += "<h3>Informacion drones</h3>"
            html += tabla_consumo

            # tabla simulacion de drones
            eventos = simular_recorrido(invernadero, plan)
            tabla_eventos = generar_tabla_eventos(eventos)
            html += "<h3>Riego optimizado</h3>"
            html += tabla_eventos

            html += "<hr>"
            actual_inv = actual_inv.siguiente

        html += "</body></html>"

        # Guardar archivo
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(html)


class Archivo_Salida:

    def generar_salida(self, cargador, ruta_salida):
        # Raíz del XML
        datos_salida = ET.Element("datosSalida")
        lista_invernaderos = ET.SubElement(datos_salida, "listaInvernaderos")

        actual_inv = cargador.invernaderos.primero
        while actual_inv:
            invernadero = actual_inv.info
            inv_elem = ET.SubElement(lista_invernaderos, "invernadero", nombre=invernadero.nombre)

            lista_planes = ET.SubElement(inv_elem, "listaPlanes")
            plan_nodo = invernadero.planes.primero

            while plan_nodo:
                plan = plan_nodo.info
                plan_elem = ET.SubElement(lista_planes, "plan", nombre=plan.nombre)

                # Simulación de optimización
                sistema = SistemaOptimizacion(invernadero, plan, aplicar_fertilizante=True)
                resumen, tiempo_total, total_litros, total_gramos = sistema.simular_riego_por_dron()

                # Tiempo óptimo, agua y fertilizante
                ET.SubElement(plan_elem, "tiempoOptimoSegundos").text = str(int(tiempo_total))
                ET.SubElement(plan_elem, "aguaRequeridaLitros").text = str(int(total_litros))
                ET.SubElement(plan_elem, "fertilizanteRequeridoGramos").text = str(int(total_gramos))

                # Eficiencia por dron
                eficiencia_drones = ET.SubElement(plan_elem, "eficienciaDronesRegadores")
                # 'resumen' es una ListaSimple con nodos cuyo .info es un dict
                nodo_res = resumen.primero
                while nodo_res:
                    datos = nodo_res.info
                    # usar id_dron como nombre (si tiene nombre real, se puede mapear fuera)
                    dron_nombre = str(datos.get('id_dron'))
                    litros_val = int(datos.get('litros', 0))
                    gramos_val = int(datos.get('gramos', 0))
                    dron_elem = ET.SubElement(
                        eficiencia_drones,
                        "dron",
                        nombre=dron_nombre,
                        litrosAgua=str(litros_val),
                        gramosFertilizante=str(gramos_val)
                    )
                    nodo_res = nodo_res.siguiente

                # Instrucciones por segundo
                instrucciones_elem = ET.SubElement(plan_elem, "instrucciones")
                eventos = simular_recorrido(invernadero, plan)

                # Agrupar eventos por segundo
                eventos_por_tiempo = {}
                actual_ev = eventos.primero
                while actual_ev:
                    ev = actual_ev.info  # Evento object
                    try:
                        t = int(ev.tiempo)
                    except Exception:
                        t = 0
                    if t not in eventos_por_tiempo:
                        eventos_por_tiempo[t] = []
                    eventos_por_tiempo[t].append({'dron': str(ev.id_dron), 'accion': ev.accion})
                    actual_ev = actual_ev.siguiente

                # Generar nodos <tiempo>
                for segundo in sorted(eventos_por_tiempo.keys()):
                    tiempo_elem = ET.SubElement(instrucciones_elem, "tiempo", segundos=str(int(segundo)))
                    for ev in eventos_por_tiempo[segundo]:
                        ET.SubElement(
                            tiempo_elem,
                            "dron",
                            nombre=ev['dron'],
                            accion=ev['accion']
                        )

                plan_nodo = plan_nodo.siguiente

            actual_inv = actual_inv.siguiente

        # Escribir XML a archivo
        tree = ET.ElementTree(datos_salida)
        # Añadir declaración XML y formatear
        with open(ruta_salida, "wb") as f:
            f.write(b'<?xml version="1.0"?>\n')
            tree.write(f, encoding="utf-8", xml_declaration=False)