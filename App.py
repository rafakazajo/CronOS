from flask import Flask, render_template, request, jsonify, abort
from werkzeug.utils import secure_filename
import threading
import os
import time
import Cerebro
import Boca

app = Flask(__name__)

ruta_env = os.path.join(os.path.dirname(__file__), '.env')
ips_cargadas = set(['127.0.0.1'])

if os.path.exists(ruta_env):
    with open(ruta_env, 'r') as f:
        for linea in f:
            if linea.startswith('IPS_PERMITIDAS='):
                ips_str = linea.strip().split('=', 1)[1]
                ips_cargadas.update([ip.strip() for ip in ips_str.split(',')])

IPS_PERMITIDAS = ips_cargadas
DIRECTORIO_SEGURO = os.path.expanduser("~/CronOS_Obsidian/Cerebro_CronOS")
os.makedirs(DIRECTORIO_SEGURO, exist_ok=True)

def realizar_limpieza_automatica():
    while True:
        ahora = time.time()
        limite_antiguedad = 30 * 24 * 3600
        try:
            carpetas_volatiles = ["Documentos", "Imagenes", "Proyectos"]
            for carpeta in carpetas_volatiles:
                ruta_carpeta = os.path.join(DIRECTORIO_SEGURO, carpeta)
                if os.path.exists(ruta_carpeta):
                    for nombre_archivo in os.listdir(ruta_carpeta):
                        ruta_completa = os.path.join(ruta_carpeta, nombre_archivo)
                        if os.path.isfile(ruta_completa):
                            if ahora - os.path.getmtime(ruta_completa) > limite_antiguedad:
                                os.remove(ruta_completa)
        except Exception: pass
        time.sleep(3600)

threading.Thread(target=realizar_limpieza_automatica, daemon=True).start()

@app.before_request
def limitar_acceso():
    if request.path.startswith('/static'): return
    if request.remote_addr not in IPS_PERMITIDAS: abort(403)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estado_boca', methods=['GET'])
def estado_boca():
    return jsonify({"hablando": Boca.esta_hablando})

@app.route('/esperar_boca', methods=['GET'])
def esperar_boca():
    while Boca.esta_hablando:
        time.sleep(0.5)
    return jsonify({"hablando": False})

@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    datos = request.json
    mensaje_usuario = datos.get('mensaje')
    modo_seleccionado = datos.get('modo', 'normal')
    modo_silencio = datos.get('silencio', False)
    
    respuesta, accion = Cerebro.pensar(mensaje_usuario, modo_seleccionado)
    
    if not modo_silencio:
        threading.Thread(target=Boca.hablar, args=(respuesta,)).start()
        
    return jsonify({"respuesta": respuesta, "accion": accion})

@app.route('/subir_archivo', methods=['POST'])
def subir_archivo():
    if 'archivo' not in request.files: return jsonify({"error": "No hay archivo"}), 400
    archivo = request.files['archivo']
    if archivo:
        nombre_seguro = secure_filename(archivo.filename)
        extension = nombre_seguro.rsplit('.', 1)[1].lower() if '.' in nombre_seguro else ''
        
        if extension in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            carpeta_destino = os.path.join(DIRECTORIO_SEGURO, "Imagenes")
        else:
            carpeta_destino = os.path.join(DIRECTORIO_SEGURO, "Documentos")
            
        os.makedirs(carpeta_destino, exist_ok=True)
        archivo.save(os.path.join(carpeta_destino, nombre_seguro))
        return jsonify({"mensaje": "Listo"}), 200

@app.route('/silenciar_boca', methods=['POST'])
def silenciar_boca():
    Boca.callar()
    return jsonify({"mensaje": "Silenciado"})

@app.route('/limpiar_chat', methods=['POST'])
def limpiar_chat():
    Cerebro.limpiar_historial()
    return jsonify({"mensaje": "Historial borrado"})

if __name__ == '__main__':
    from waitress import serve
    print("[SISTEMA EN LÍNEA] Iniciando Núcleo CronOS en modo Producción (Waitress)...")
    print("Escuchando en el puerto 5000 para múltiples dispositivos.")
    serve(app, host='0.0.0.0', port=5000)