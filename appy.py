from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    titulo = "Sistema de riego para un Invernadero"
    descripcion = "Optimizador de un sistema de riego y aplicación de fertilizante robótico."
    return render_template('index.html', titulo=titulo, descripcion=descripcion)

@app.route('/ayuda')
def ayuda():
    return render_template('ayuda.html')

if __name__ == '__main__':
    app.run(debug=True)