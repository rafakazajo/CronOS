from flask import Flask, render_template, request, jsonify
import threading
import Cerebro
import Boca

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    datos = request.json
    mensaje_usuario = datos.get('mensaje')
    
    respuesta_cronos = Cerebro.pensar(mensaje_usuario)
    
    threading.Thread(target=Boca.hablar, args=(respuesta_cronos,)).start()

    return jsonify({"respuesta": respuesta_cronos})

if __name__ == '__main__':
    print("Iniciando Interfaz de CronOS...")
    app.run(host='0.0.0.0', port=5000, debug=True)