from flask import Flask, render_template, request, redirect, url_for, jsonify
from lectorXML import carga  
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html', titulo="Invernadero", descripcion="Carga tu archivo XML")

@app.route('/ayuda')
def ayuda():
    return render_template('ayuda.html')

@app.route('/procesar_xml', methods=['POST'])
def procesar_xml():
    try:
        archivo = request.files.get('archivo')
        if archivo and archivo.filename.endswith('.xml'):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            ruta = os.path.join(app.config['UPLOAD_FOLDER'], archivo.filename)
            archivo.save(ruta)
            print("Ruta guardada:", ruta)

            cargador = carga()
            cargador.cargar_archivo(ruta)

            # construye el JSON manualmente usando la  lista
            json_texto = '{"invernaderos":['
            actual = cargador.invernaderos.primero
            Primero = True
            while actual:
                if not Primero:
                    json_texto += ','
                # Nodo almacena el objeto en "info"
                json_texto += f'"{actual.info.nombre}"'
                Primero = False
                actual = actual.siguiente
            json_texto += ']}'
            return app.response_class(response=json_texto, status=200, mimetype='application/json')
            
        return jsonify({'error': 'Archivo inválido'}), 400
    except Exception as e:
        print(f"Error en /procesar_xml: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/seleccionar_invernadero', methods=['POST'])
def seleccionar_invernadero():
    nombre = request.json.get('nombre')
    return jsonify({'mensaje': f'Escogiste este invernadero: {nombre}'})

if __name__ == '__main__':
    app.run(debug=True)