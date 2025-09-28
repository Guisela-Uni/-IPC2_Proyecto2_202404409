from flask import Flask, render_template, request, redirect, url_for, jsonify
from lectorXML import carga
from sistema_optimizacion import SistemaOptimizacion
from simulacion_drones import simular_recorrido, generar_tabla_eventos
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
    resumen, tiempo_total = sistema.simular_riego_por_dron()
    tabla_html = sistema.generar_tabla(resumen, cargador.drones)
    
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
                            seleccion_actual={
                                'invernadero': invernadero_nombre,
                                'riego': plan_nombre,
                                'fertilizante': request.form.get('fertilizante'),
                                'tiempo_dron': tiempo_dron
                            })

#ruta para generar los reportes
@app.route('/generar_reportes', methods=['POST'])
def generar_reportes():
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

if __name__ == '__main__':
    app.run(debug=True)