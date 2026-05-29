from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import threading
import os
import psutil
import time
import json
from Boca import ciclo_voz
from Estado import estado_global

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/estado_sistema', methods=['GET'])
def estado_sistema():
    def generar():
        while True:
            cpu = psutil.cpu_percent(interval=0.1)
            ram = psutil.virtual_memory()
            disco = psutil.disk_usage(os.path.expanduser('~'))
            data = {
                "cpu": cpu,
                "ram": round(ram.used / (1024**3), 1),
                "disco": round(disco.free / (1024**3), 1),
                "estado": estado_global.get("estado", "reposo"),
                "log": estado_global.get("log", "")
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.8)
    return Response(stream_with_context(generar()), mimetype='text/event-stream')

@app.route('/activar_escucha', methods=['POST'])
def activar_escucha():
    if estado_global.get("ocupado"):
        return jsonify({"ok": False, "razon": "ocupado"})
    estado_global["ocupado"] = True
    threading.Thread(target=ciclo_voz, daemon=True).start()
    return jsonify({"ok": True})

@app.route('/cancelar_escucha', methods=['POST'])
def cancelar_escucha():
    estado_global["cancelar"] = True
    estado_global["ocupado"] = False
    estado_global["estado"] = "reposo"
    estado_global["log"] = "[MIC] Escucha cancelada por el usuario."
    return jsonify({"ok": True})

if __name__ == '__main__':
    from waitress import serve
    print("[CronOS] Núcleo en línea. Escuchando en puerto 5000.")
    serve(app, host='0.0.0.0', port=5000)