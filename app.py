from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from lectorXML import carga
from sistema_optimizacion import SistemaOptimizacion
from simulacion_drones import simular_recorrido, generar_tabla_eventos
from grafico import generar_dot_estados, generar_imagen_dot
from reporte_html import ReporteHTML
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ayuda')
def ayuda():
    return render_template('ayuda.html')

#ruta que recauda los datos ingresados al formulario
@app.route('/formulario', methods=['POST'])
def formulario():
    archivo = request.files.get('archivo')
    if not archivo or not archivo.filename.endswith('.xml'):
        return render_template('index.html', titulo="Invernadero", descripcion="Archivo inválido")

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
    archivo.save(ruta)

    cargador = carga()
    cargador.cargar_archivo(ruta)

    invernaderos = []
    planes = []
    actual = cargador.invernaderos.primero
    while actual:
        invernaderos.append(actual.info.nombre)
        if not planes and actual.info.planes.primero:
            nodo_plan = actual.info.planes.primero
            while nodo_plan:
                planes.append(nodo_plan.info.nombre)
                nodo_plan = nodo_plan.siguiente
        actual = actual.siguiente

    return render_template('index.html',
                            titulo="Invernadero",
                            descripcion="Archivo cargado correctamente",
                            invernaderos=invernaderos,
                            planes=planes,
                            uploaded_filename=archivo.filename)

#ruta para procesar la info enviada en el formulario
@app.route('/procesar_seleccion', methods=['POST'])
def procesar_seleccion():
    invernadero_nombre = request.form.get('invernadero')
    plan_nombre = request.form.get('riego')
    aplicar_fertilizante = request.form.get('fertilizante') == 'Sí'
    tiempo_dron = int(request.form.get('tiempo_dron'))
    filename = request.form.get('archivo_nombre')

    ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cargador = carga()
    cargador.cargar_archivo(ruta)

    # validacion para que invernadero exista
    invernadero = cargador.buscar_invernadero(invernadero_nombre)
    if not invernadero:
        return render_template('index.html',
                                titulo="Error",
                                descripcion=f"Invernadero '{invernadero_nombre}' no encontrado.",
                                error=True)

    # validacion para que plan exista
    plan = cargador.buscar_plan(invernadero, plan_nombre)
    if not plan:
        return render_template('index.html',
                                titulo="Error",
                                descripcion=f"Plan '{plan_nombre}' no encontrado en el invernadero '{invernadero_nombre}'.",
                                error=True)

    sistema = SistemaOptimizacion(invernadero, plan, aplicar_fertilizante)
    # para mandar a la tabla
    resumen, tiempo_total, total_litros, total_gramos = sistema.simular_riego_por_dron()
    tabla_html = sistema.generar_tabla(resumen, cargador.drones, total_litros, total_gramos)
    
    # reconstruir selects: invernaderos y planes 
    invernaderos = []
    actual = cargador.invernaderos.primero
    while actual:
        invernaderos.append(actual.info.nombre)
        actual = actual.siguiente

    planes = []
    nodo_plan = invernadero.planes.primero
    while nodo_plan:
        planes.append(nodo_plan.info.nombre)
        nodo_plan = nodo_plan.siguiente

    return render_template('index.html',
                            titulo="Invernadero",
                            descripcion="Selección procesada",
                            invernaderos=invernaderos,
                            planes=planes,
                            uploaded_filename=filename,
                            tabla=tabla_html,
                            tiempo_total=tiempo_total,
                            # Opcional: si quieres mostrar los totales también fuera de la tabla
                            total_litros=total_litros,
                            total_gramos=total_gramos,
                            seleccion_actual={
                                'invernadero': invernadero_nombre,
                                'riego': plan_nombre,
                                'fertilizante': request.form.get('fertilizante'),
                                'tiempo_dron': tiempo_dron
                            })

#ruta para generar los reportes
@app.route('/generar_simulacion', methods=['POST'])
def generar_simulacion():
    invernadero_nombre = request.form.get('invernadero')
    plan_nombre = request.form.get('riego')
    aplicar_fertilizante = request.form.get('fertilizante') == 'Sí'
    tiempo_dron = int(request.form.get('tiempo_dron'))
    filename = request.form.get('archivo_nombre')

    ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cargador = carga()
    cargador.cargar_archivo(ruta)

    # valida invernadero
    invernadero = cargador.buscar_invernadero(invernadero_nombre)
    if not invernadero:
        return render_template('index.html',
                                titulo="Error",
                                descripcion=f"Invernadero '{invernadero_nombre}' no encontrado.",
                                error=True)

    # valida planes
    plan = cargador.buscar_plan(invernadero, plan_nombre)
    if not plan:
        return render_template('index.html',
                                titulo="Error",
                                descripcion=f"Plan '{plan_nombre}' no encontrado en el invernadero '{invernadero_nombre}'.",
                                error=True)

    #simulacion
    eventos = simular_recorrido(invernadero, plan)
    tabla_eventos = generar_tabla_eventos(eventos)

    # reconstruye los selects de invernaderos y planes 
    invernaderos = []
    actual = cargador.invernaderos.primero
    while actual:
        invernaderos.append(actual.info.nombre)
        actual = actual.siguiente

    planes = []
    nodo_plan = invernadero.planes.primero
    while nodo_plan:
        planes.append(nodo_plan.info.nombre)
        nodo_plan = nodo_plan.siguiente

    return render_template('index.html',
                            titulo="Invernadero",
                            descripcion="Reporte paso a paso generado",
                            invernaderos=invernaderos,
                            planes=planes,
                            uploaded_filename=filename,
                            tabla_eventos=tabla_eventos,
                            seleccion_actual={
                                'invernadero': invernadero_nombre,
                                'riego': plan_nombre,
                                'fertilizante': request.form.get('fertilizante'),
                                'tiempo_dron': tiempo_dron
                            })


#ruta para imprimir el grafico
@app.route('/descargar_grafico', methods=['POST'])
def descargar_grafico():
    try:
        invernadero_nombre = request.form.get('invernadero')
        plan_nombre = request.form.get('riego')
        aplicar_fertilizante = request.form.get('fertilizante') == 'Sí'
        tiempo_dron = int(request.form.get('tiempo_dron'))
        filename = request.form.get('archivo_nombre')

        # Validación de filename
        if not filename:
            return render_template('index.html',
                                    titulo="Error",
                                    descripcion="No se recibió el nombre del archivo. Por favor, suba un archivo primero.",
                                    error=True)

        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        cargador = carga()
        cargador.cargar_archivo(ruta)

        # Validar invernadero
        invernadero = cargador.buscar_invernadero(invernadero_nombre)
        if not invernadero:
            return render_template('index.html',
                                    titulo="Error",
                                    descripcion=f"Invernadero '{invernadero_nombre}' no encontrado.",
                                    error=True)

        # Validar plan
        plan = cargador.buscar_plan(invernadero, plan_nombre)
        if not plan:
            return render_template('index.html',
                                    titulo="Error",
                                    descripcion=f"Plan '{plan_nombre}' no encontrado en el invernadero '{invernadero_nombre}'.",
                                    error=True)

        # Generar gráfico
        try:
            nombre_base = os.path.splitext(filename)[0]
        except Exception:
            nombre_base = "grafico"

        ruta_dot = os.path.join(app.config['UPLOAD_FOLDER'], f"{nombre_base}_estados.dot")
        ruta_png = os.path.join(app.config['UPLOAD_FOLDER'], f"{nombre_base}_estados.png")

        generar_dot_estados(invernadero, plan, tiempo_dron, ruta_dot)
        generar_imagen_dot(ruta_dot, ruta_png)

        # Descargar PNG si existe
        if os.path.exists(ruta_png):
            return send_file(ruta_png, as_attachment=True, download_name=f"grafico_estados_{nombre_base}.png")
        else:
            return render_template('index.html',
                                    titulo="Error",
                                    descripcion="No se pudo generar el gráfico. Verifique que Graphviz esté instalado.",
                                    error=True)

    except Exception as e:
        # Capturar cualquier error inesperado
        return render_template('index.html',
                                titulo="Error Inesperado",
                                descripcion=f"Ocurrió un error: {str(e)}",
                                error=True)


#funcion para generar el reporte hmtl
@app.route('/generar_reporte_html', methods=['POST'])
def generar_reporte_html():
    filename = request.form.get('archivo_nombre')
    if not filename:
        return render_template('index.html',
                                titulo="Error",
                                descripcion="No se cargó ningún archivo XML.",
                                error=True)

    ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    cargador = carga()
    cargador.cargar_archivo(ruta)

    # Generar reporte HTML
    from reporte_html import ReporteHTML
    generador = ReporteHTML()
    ruta_salida = os.path.join(app.config['UPLOAD_FOLDER'], "reportes_invernaderos.html")
    generador.generar_reporte(cargador, ruta_salida)

    # Descargar con nombre correcto y tipo MIME
    return send_file(
        ruta_salida,
        as_attachment=True,
        download_name="reportes_invernaderos.html",
        mimetype='text/html'
    )


    
#pone el debug en "on" para actualizar pagina    
if __name__ == '__main__':
    app.run(debug=True)