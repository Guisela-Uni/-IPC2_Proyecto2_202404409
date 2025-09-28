from sistema_optimizacion import SistemaOptimizacion
from simulacion_drones import simular_recorrido, generar_tabla_eventos

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
            html += "<h3>Consumo por dron</h3>"
            html += tabla_consumo

            # tabla simulacion de drones
            eventos = simular_recorrido(invernadero, plan)
            tabla_eventos = generar_tabla_eventos(eventos)
            html += "<h3>Simulación paso a paso</h3>"
            html += tabla_eventos

            html += "<hr>"
            actual_inv = actual_inv.siguiente

        html += "</body></html>"

        # Guardar archivo
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(html)
