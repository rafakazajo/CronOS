import ollama
from ddgs import DDGS
import os
import re
import json
import time
import base64
import subprocess
import datetime
import requests
import pytz
import recurring_ical_events
import urllib.parse
import webbrowser
import psutil
import threading

historial_conversacion = []
MAX_MENSAJES = 10
DIRECTORIO_SEGURO = os.path.expanduser("~/CronOS_Obsidian/Cerebro_CronOS")
ARCHIVO_MEMORIA = os.path.join(DIRECTORIO_SEGURO, "Memoria_CronOS.md")
ARCHIVO_HISTORIAL = os.path.join(DIRECTORIO_SEGURO, "historial_sesion.json")

_cache_obsidian = ""
_cache_timestamps = {}

def cargar_historial_guardado():
    global historial_conversacion
    if os.path.exists(ARCHIVO_HISTORIAL):
        try:
            with open(ARCHIVO_HISTORIAL, 'r', encoding='utf-8') as f:
                historial_conversacion = json.load(f)
        except Exception as e:
            print(f"[ERROR cargar_historial_guardado]: {e}")
            historial_conversacion = []

def guardar_historial():
    try:
        with open(ARCHIVO_HISTORIAL, 'w', encoding='utf-8') as f:
            json.dump(historial_conversacion, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[ERROR guardar_historial]: {e}")

def limpiar_historial():
    global historial_conversacion
    historial_conversacion = []
    if os.path.exists(ARCHIVO_HISTORIAL):
        try:
            os.remove(ARCHIVO_HISTORIAL)
        except Exception as e:
            print(f"[ERROR limpiar_historial]: {e}")

cargar_historial_guardado()

def buscar_en_la_red(consulta):
    try:
        resultados = DDGS().text(consulta, region='es-es', max_results=3)
        contexto = ""
        for res in resultados:
            contexto += f"- {res['body']}\n"
        if not contexto:
            return "SISTEMA: La búsqueda no devolvió resultados. Informa al usuario."
        return contexto
    except Exception as e:
        print(f"[ERROR buscar_en_la_red]: {e}")
        return "SISTEMA: Fallo de conexión o librería. Informa al usuario."

def verificar_ruta_segura(ruta):
    nombre_archivo = os.path.basename(ruta)
    return os.path.join(DIRECTORIO_SEGURO, nombre_archivo)

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        try:
            with open(ARCHIVO_MEMORIA, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                return [linea.strip('- \n') for linea in lineas if linea.startswith('-')]
        except Exception as e:
            print(f"[ERROR cargar_memoria]: {e}")
    return []

def guardar_memoria(dato):
    try:
        memoria = cargar_memoria()
        if dato not in memoria:
            memoria.append(dato)
            if len(memoria) > 20:
                memoria = memoria[-20:]
            with open(ARCHIVO_MEMORIA, 'w', encoding='utf-8') as f:
                for m in memoria:
                    f.write(f"- {m}\n")
    except Exception as e:
        print(f"[ERROR guardar_memoria]: {e}")

def leer_secreto(clave):
    ruta_secrets = os.path.join(DIRECTORIO_SEGURO, "Secreto.txt")
    if os.path.exists(ruta_secrets):
        try:
            with open(ruta_secrets, 'r') as f:
                for linea in f:
                    if linea.startswith(f"{clave}="):
                        return linea.strip().split("=", 1)[1]
        except Exception as e:
            print(f"[ERROR leer_secreto]: {e}")
    return None

def leer_cerebro_obsidian():
    global _cache_obsidian, _cache_timestamps
    archivos_criticos = ["Personalidad_CronOS.md", "Perfil_Rafael.md", "Memoria_CronOS.md"]
    cambios_detectados = False
    rutas_a_leer = []

    try:
        for archivo in archivos_criticos:
            ruta = os.path.join(DIRECTORIO_SEGURO, archivo)
            if os.path.exists(ruta): rutas_a_leer.append((ruta, True))
            
        for archivo in os.listdir(DIRECTORIO_SEGURO):
            if archivo.lower().endswith(".md") and archivo not in archivos_criticos:
                ruta = os.path.join(DIRECTORIO_SEGURO, archivo)
                rutas_a_leer.append((ruta, False))
    except Exception as e:
        print(f"[ERROR leer_cerebro_obsidian]: {e}")

    timestamps_actuales = {}
    for ruta, _ in rutas_a_leer:
        try:
            ts = os.path.getmtime(ruta)
            timestamps_actuales[ruta] = ts
            if _cache_timestamps.get(ruta) != ts:
                cambios_detectados = True
        except Exception as e:
            print(f"[ERROR timestamps]: {e}")

    if not cambios_detectados and _cache_obsidian:
        return _cache_obsidian

    conocimiento_base = ""
    conocimiento_extra = ""
    for ruta, es_critico in rutas_a_leer:
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                if es_critico:
                    conocimiento_base += f"\n[DOCUMENTO CRÍTICO: {os.path.basename(ruta)}]\n{f.read()}\n"
                else:
                    conocimiento_extra += f"\n[DOCUMENTO: {os.path.basename(ruta)}]\n{f.read()}\n"
        except Exception as e:
            print(f"[ERROR leer_archivos]: {e}")

    espacio_restante = 8000 - len(conocimiento_base)
    if espacio_restante > 0:
        conocimiento_final = conocimiento_base + conocimiento_extra[:espacio_restante]
    else:
        conocimiento_final = conocimiento_base

    _cache_obsidian = conocimiento_final
    _cache_timestamps = timestamps_actuales
    return conocimiento_final

def procesar_lectura(texto):
    patron_leer = r'\[LEER_ARCHIVO\s*\|\s*(.*?)\]'
    coincidencias = re.findall(patron_leer, texto)
    contenido_total = ""
    for ruta in coincidencias:
        try:
            ruta_segura = verificar_ruta_segura(ruta.strip())
            if os.path.exists(ruta_segura):
                with open(ruta_segura, 'r', encoding='utf-8') as f:
                    contenido_total += f"\nContenido de {os.path.basename(ruta_segura)}:\n{f.read()}\n"
        except Exception as e:
            print(f"[ERROR procesar_lectura]: {e}")
    return re.sub(patron_leer, '', texto).strip(), contenido_total

def procesar_escritura(texto):
    patron_crear = r'\[CREAR_ARCHIVO\s*\|\s*(.*?)\s*\|\s*(.*?)\]'
    coincidencias = re.findall(patron_crear, texto, re.DOTALL)
    nombres_archivos = []
    directorio_proyectos = os.path.join(DIRECTORIO_SEGURO, "Proyectos")
    os.makedirs(directorio_proyectos, exist_ok=True)
    
    for ruta, contenido in coincidencias:
        try:
            nombre_archivo = os.path.basename(ruta.strip())
            ruta_segura = os.path.join(directorio_proyectos, nombre_archivo)
            with open(ruta_segura, 'w', encoding='utf-8') as f:
                f.write(contenido.strip())
            nombres_archivos.append(nombre_archivo)
        except Exception as e:
            print(f"[ERROR procesar_escritura]: {e}")
        
    texto_limpio = re.sub(patron_crear, '', texto, flags=re.DOTALL).strip()
    if nombres_archivos:
        confirmacion = f"He procedido a crear el archivo {', '.join(nombres_archivos)} en la carpeta Proyectos."
        texto_limpio = f"{texto_limpio} {confirmacion}" if texto_limpio else confirmacion
    return texto_limpio, bool(nombres_archivos)

def procesar_busqueda(texto):
    patron_buscar = r'\[BUSCAR\s*\|\s*(.*?)\]'
    coincidencias = re.findall(patron_buscar, texto)
    resultados_totales = ""
    for consulta in coincidencias:
        try:
            print(f"[*] CronOS buscando en la red: {consulta}")
            resultados = buscar_en_la_red(consulta.strip())
            resultados_totales += f"\nResultados de la red para '{consulta}':\n{resultados}\n"
        except Exception as e:
            print(f"[ERROR procesar_busqueda]: {e}")
    return re.sub(patron_buscar, '', texto).strip(), resultados_totales

def procesar_apertura_app(texto):
    patron_abrir = r'\[ABRIR_APP\s*\|\s*(.*?)\]'
    coincidencias = re.findall(patron_abrir, texto)
    apps_seguras = {
        "navegador": "google-chrome", "chrome": "google-chrome", 
        "archivos": "nemo", "carpeta": "nemo",
        "codigo": "code", "vscode": "code",
        "terminal": "gnome-terminal"
    }
    acciones = ""
    for app in coincidencias:
        app_limpia = app.strip().lower()
        comando = next((cmd for clave, cmd in apps_seguras.items() if clave in app_limpia), None)
        if comando:
            try:
                subprocess.Popen([comando], start_new_session=True)
                acciones += f"He ejecutado la apertura de {comando}. "
            except Exception as e:
                print(f"[ERROR procesar_apertura_app]: {e}")
                acciones += f"Fallo al abrir {comando}. "
        else:
            acciones += f"No tengo permisos para abrir '{app_limpia}'. "
            
    texto_limpio = re.sub(patron_abrir, '', texto).strip()
    if acciones: texto_limpio = f"{texto_limpio} {acciones}".strip()
    return texto_limpio

def procesar_control_pc(texto):
    patron_control = r'\[?CONTROL_PC\s*\|\s*([a-zA-Z0-9_ ]+)\]?'
    coincidencias = re.findall(patron_control, texto)
    comandos_seguros = {
        "subir volumen": ["amixer", "-q", "sset", "Master", "10%+"],
        "bajar volumen": ["amixer", "-q", "sset", "Master", "10%-"],
        "mutear": ["amixer", "-q", "sset", "Master", "toggle"],
        "pausar musica": ["playerctl", "play-pause"],
        "siguiente cancion": ["playerctl", "next"]
    }
    acciones = ""
    for accion in coincidencias:
        accion_limpia = accion.strip().lower()
        comando = next((cmd for clave, cmd in comandos_seguros.items() if clave in accion_limpia), None)
        if comando:
            try:
                subprocess.run(comando)
                acciones += f"He ejecutado la orden en tu ordenador. "
            except Exception as e:
                print(f"[ERROR procesar_control_pc]: {e}")
                acciones += f"Fallo al ejecutar la orden. "
    texto_limpio = re.sub(patron_control, '', texto).strip()
    if acciones: texto_limpio = f"{texto_limpio} {acciones}".strip()
    return texto_limpio

def procesar_correo(texto):
    patron_correo = r'\[PREPARAR_CORREO\s*\|\s*(.*?)\]'
    coincidencias = re.findall(patron_correo, texto, re.DOTALL)
    acciones = ""
    for coincidencia in coincidencias:
        try:
            partes = [p.strip() for p in coincidencia.split('|')]
            destinatario = partes[0] if len(partes) > 0 else ""
            asunto = partes[1] if len(partes) > 1 else "Nuevo mensaje"
            cuerpo = partes[2] if len(partes) > 2 else asunto
            
            asunto_cod = urllib.parse.quote(asunto)
            cuerpo_cod = urllib.parse.quote(cuerpo)
            webbrowser.open(f"mailto:{destinatario}?subject={asunto_cod}&body={cuerpo_cod}")
            acciones += f"He preparado el correo para {destinatario}. "
        except Exception as e:
            print(f"[ERROR procesar_correo]: {e}")
            acciones += "Hubo un fallo al preparar el correo. "
            
    texto_limpio = re.sub(patron_correo, '', texto, flags=re.DOTALL).strip()
    if acciones: texto_limpio = f"{texto_limpio} {acciones}".strip()
    return texto_limpio

def procesar_captura_pantalla(texto):
    patron = r'\[?VER_PANTALLA\]?'
    if re.search(patron, texto):
        try:
            ruta_captura = os.path.join(DIRECTORIO_SEGURO, "Imagenes", "captura.png")
            subprocess.run(["gnome-screenshot", "-f", ruta_captura])
            texto_limpio = re.sub(patron, '', texto).strip()
            return texto_limpio + " He tomado una captura de pantalla. ¿Qué analizo?"
        except Exception as e:
            print(f"[ERROR procesar_captura_pantalla]: {e}")
            return re.sub(patron, '', texto).strip() + " Falló la captura."
    return texto

def procesar_portapapeles(texto):
    patron = r'\[?LEER_PORTAPAPELES\]?'
    if re.search(patron, texto):
        try:
            import pyperclip
            contenido = pyperclip.paste()
            texto_limpio = re.sub(patron, '', texto).strip()
            if contenido: return f"{texto_limpio}\nPORTAPAPELES:\n{contenido}"
        except Exception as e:
            print(f"[ERROR procesar_portapapeles]: {e}")
        return f"{texto_limpio} (Portapapeles vacío o error)."
    return texto

def procesar_diagnostico_pc(texto):
    patron = r'\[?DIAGNOSTICO_PC\]?'
    if re.search(patron, texto):
        print("[*] CronOS analizando salud con psutil...")
        try:
            ram = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.5)
            disco = psutil.disk_usage(os.path.expanduser('~'))
            
            ram_str = f"RAM: {ram.total / (1024**3):.1f}GB total, {ram.used / (1024**3):.1f}GB usada ({ram.percent}%)"
            cpu_str = f"CPU: {cpu}% uso"
            disco_str = f"DISCO (/home): {disco.total / (1024**3):.1f}GB total, {disco.free / (1024**3):.1f}GB libre"
            
            contexto_limpio = f"{ram_str} | {cpu_str} | {disco_str}"
            texto_limpio = re.sub(patron, '', texto).strip()
            return f"{texto_limpio}\nDATOS DE SISTEMA: {contexto_limpio}"
        except Exception as e:
            print(f"[ERROR procesar_diagnostico_pc]: {e}")
            return re.sub(patron, '', texto).strip() + " Error de sensores."
    return texto

def temporizador_hilo(segundos, mensaje):
    time.sleep(segundos)
    try:
        subprocess.run(["notify-send", "-u", "critical", "CronOS: Tiempo agotado", mensaje])
        ruta_sonido = "/usr/share/sounds/freedesktop/stereo/complete.oga"
        for _ in range(3):
            subprocess.run(["paplay", ruta_sonido])
            time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR temporizador_hilo]: {e}")

def procesar_temporizador(texto):
    patron = r'\[?(?:TEMPORIZADOR|PROGRAMAR_ALERTA)\s*\|\s*(\d+)\s*\|\s*([^\]]+)\]?'
    coincidencias = re.findall(patron, texto)
    confirmaciones = ""
    for minutos, motivo in coincidencias:
        try:
            segundos = int(minutos) * 60
            threading.Thread(target=temporizador_hilo, args=(segundos, motivo.strip()), daemon=True).start()
            confirmaciones += f"He programado {minutos} minutos para {motivo.strip()}. "
        except Exception as e:
            print(f"[ERROR procesar_temporizador]: {e}")
    texto_limpio = re.sub(patron, '', texto, flags=re.DOTALL).strip()
    if confirmaciones: return f"{texto_limpio} {confirmaciones}".strip()
    return texto_limpio

def leer_eventos_calendario():
    ruta_ics = os.path.join(DIRECTORIO_SEGURO, "mi_agenda.ics")
    url_google = leer_secreto("CALENDAR_URL")
    
    if url_google:
        try:
            respuesta = requests.get(url_google, timeout=5)
            respuesta.raise_for_status()
            with open(ruta_ics, 'wb') as f:
                f.write(respuesta.content)
        except Exception as e:
            print(f"[ERROR descargar calendario]: {e}")
            
    if not os.path.exists(ruta_ics): return "No hay archivo de agenda."
    
    try:
        from icalendar import Calendar
        with open(ruta_ics, 'rb') as f: cal = Calendar.from_ical(f.read())
        zona_espana = pytz.timezone('Europe/Madrid')
        hoy = datetime.date.today()
        eventos_expandidos = recurring_ical_events.of(cal).between(hoy, hoy + datetime.timedelta(days=30))
        
        eventos_raw = []
        for component in eventos_expandidos:
            dtstart_raw = component.get('dtstart')
            if dtstart_raw:
                dt_val = dtstart_raw.dt
                if isinstance(dt_val, datetime.datetime):
                    dt_local = pytz.utc.localize(dt_val).astimezone(zona_espana) if dt_val.tzinfo is None else dt_val.astimezone(zona_espana)
                    fecha_matematica = dt_local
                    fecha_str = dt_local.strftime('%d-%m-%Y a las %H:%M')
                else:
                    fecha_matematica = zona_espana.localize(datetime.datetime.combine(dt_val, datetime.time.min))
                    fecha_str = dt_val.strftime('%d-%m-%Y (Todo el día)')
                
                if fecha_matematica.date() >= hoy:
                    eventos_raw.append((fecha_matematica, f"- {fecha_str}: {component.get('summary', 'Evento')}"))
        
        if not eventos_raw: return "La agenda está libre."
        eventos_raw.sort(key=lambda x: x[0])
        eventos_finales = list(dict.fromkeys([texto for _, texto in eventos_raw]))
        return "Eventos:\n" + "\n".join(eventos_finales[:7])
    except Exception as e:
        print(f"[ERROR analizar calendario]: {e}")
        return "Error al procesar calendario."

def procesar_agenda(texto):
    patron = r'\[?LEER_AGENDA\]?'
    if re.search(patron, texto):
        eventos = leer_eventos_calendario()
        return re.sub(patron, '', texto).strip(), eventos
    return texto, None

def procesar_recuerdos(texto):
    patron = r'\[?RECORDAR\s*\|\s*([^\n\]]+)\]?'
    for dato in re.findall(patron, texto): guardar_memoria(dato.strip())
    return re.sub(patron, '', texto).strip()

def obtener_imagen_reciente():
    try:
        dir_img = os.path.join(DIRECTORIO_SEGURO, "Imagenes")
        if not os.path.exists(dir_img): return None
        archivos = [os.path.join(dir_img, f) for f in os.listdir(dir_img) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        if not archivos: return None
        mas_reciente = max(archivos, key=os.path.getmtime)
        if time.time() - os.path.getmtime(mas_reciente) < 300: return mas_reciente
    except Exception as e:
        print(f"[ERROR obtener_imagen]: {e}")
    return None

def codificar_imagen_base64(ruta):
    try:
        with open(ruta, "rb") as f: return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        print(f"[ERROR base64_img]: {e}")
    return None

def pensar(mensaje_usuario, modo_actual="normal", _desde_stream=False):
    global historial_conversacion
    os.makedirs(DIRECTORIO_SEGURO, exist_ok=True)
    
    modelo_activo = leer_secreto("MODELO_PRINCIPAL")
    if not modelo_activo: modelo_activo = 'qwen2.5:3b'
    
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    recuerdos_actuales = cargar_memoria()
    texto_memoria = "\n".join([f"- {r}" for r in recuerdos_actuales]) if recuerdos_actuales else "Aún no hay datos."
    
    instruccion_base = (
        f"Eres CRONOS. Hoy es {fecha_actual}. RESPONDE EN ESPAÑOL.\n"
        f"### BASE DE CONOCIMIENTO ###\n{leer_cerebro_obsidian()}\n"
        f"### CONTEXTO ###\n{texto_memoria}\n"
        "REGLAS:\n"
        "1. NO menciones datos del contexto para saludar. Sé conversacional y natural.\n"
        "2. HERRAMIENTAS (USAR SOLO SI EL USUARIO LO PIDE EXPLÍCITAMENTE):\n"
        "- [CREAR_ARCHIVO | nombre.ext | cont]\n"
        "- [RECORDAR | dato]\n"
        "- [BUSCAR | consulta]\n"
        "- [ABRIR_APP | app]\n"
        "- [CONTROL_PC | accion]\n"
        "- [LEER_AGENDA]\n"
        "- [PREPARAR_CORREO | dest | asun | cuerpo]\n"
        "- [VER_PANTALLA]\n"
        "- [LEER_PORTAPAPELES]\n"
        "- [TEMPORIZADOR | min | motivo]\n"
        "- [DIAGNOSTICO_PC]\n"
        "DIRECTIVA CRÍTICA: Si el usuario pide una acción, usa el comando exacto. Si el usuario solo está charlando (ej: te dice 'Hola'), responde de forma natural SIN usar comandos."
    )

    if modo_actual == "estudio": instruccion_sistema = instruccion_base + "\nModo ESTUDIO."
    elif modo_actual == "codigo": instruccion_sistema = instruccion_base + "\nModo CÓDIGO ACTIVO: MUESTRA CÓDIGO DIRECTO."
    else: instruccion_sistema = instruccion_base + "\nModo NORMAL."

    if not _desde_stream:
        historial_conversacion.append({'role': 'user', 'content': mensaje_usuario})
        
    mensajes_api = [{'role': 'system', 'content': instruccion_sistema}] + list(historial_conversacion)
        
    imagen_detectada = obtener_imagen_reciente()
    if imagen_detectada:
        imagen_b64 = codificar_imagen_base64(imagen_detectada)
        if imagen_b64:
            mensajes_vision = [
                {'role': 'system', 'content': "Analyze the image and describe it in detail."},
                {'role': 'user', 'content': mensaje_usuario, 'images': [imagen_b64]}
            ]
            try:
                respuesta_vision = ollama.chat(model='moondream', messages=mensajes_vision)
                texto_bruto = respuesta_vision['message'].get('content', '')
                if texto_bruto:
                    mensajes_traduccion = [
                        {'role': 'system', 'content': instruccion_sistema},
                        {'role': 'user', 'content': f"Visión reporta: '{texto_bruto}'. Responde a: '{mensaje_usuario}'."}
                    ]
                    texto_bruto = ollama.chat(model=modelo_activo, messages=mensajes_traduccion)['message'].get('content', texto_bruto)
            except Exception as e:
                print(f"[ERROR VISUAL]: {e}")
                texto_bruto = "Error visual."
    
    if not imagen_detectada:
        try:
            texto_bruto = ollama.chat(model=modelo_activo, messages=mensajes_api)['message'].get('content', '')
        except Exception as e:
            print(f"[ERROR OLLAMA]: {e}")
            return "Error en núcleo.", False
            
    texto_bruto, cont_ext = procesar_lectura(texto_bruto)
    if cont_ext:
        try:
            texto_bruto = ollama.chat(model=modelo_activo, messages=mensajes_api + [{'role': 'user', 'content': f"Datos leídos:\n{cont_ext}"}])['message'].get('content', texto_bruto)
        except Exception as e: print(f"[ERROR lectura archivo]: {e}")

    texto_bruto, res_red = procesar_busqueda(texto_bruto)
    texto_bruto, res_agenda = procesar_agenda(texto_bruto)
    
    if res_agenda:
        try:
            prompt_agenda = f"Pregunta: '{mensaje_usuario}'. Hoy: {datetime.date.today().strftime('%d-%m-%Y')}. EVENTOS EXACTOS:\n{res_agenda}\nSé directo."
            texto_bruto = ollama.chat(model=modelo_activo, messages=[{'role': 'system', 'content': "Analista de agenda."}, {'role': 'user', 'content': prompt_agenda}])['message'].get('content', texto_bruto)
        except Exception as e: print(f"[ERROR resolviendo agenda]: {e}")

    texto_bruto = re.sub(r'\[BUSCAR\s*\|\s*(.*?)\]|\[LEER_ARCHIVO\s*\|\s*(.*?)\]|\[?LEER_AGENDA\]?', '', texto_bruto).strip()
    texto_bruto = procesar_apertura_app(texto_bruto)
    texto_bruto = procesar_control_pc(texto_bruto)
    texto_bruto = procesar_correo(texto_bruto)
    texto_bruto = procesar_captura_pantalla(texto_bruto)
    texto_bruto = procesar_portapapeles(texto_bruto)
    texto_bruto = procesar_diagnostico_pc(texto_bruto)
    texto_bruto = procesar_temporizador(texto_bruto)
    texto_bruto = procesar_recuerdos(texto_bruto)
    texto_final, accion_esc = procesar_escritura(texto_bruto)
    
    texto_final = texto_final.strip()
    if not texto_final:
        texto_final = "He procesado tu solicitud."
        
    texto_historial = texto_final
    if texto_historial == "He procesado tu solicitud.":
        texto_historial = "Comando ejecutado internamente."
        
    historial_conversacion.append({'role': 'assistant', 'content': texto_historial})
    if len(historial_conversacion) > MAX_MENSAJES: 
        historial_conversacion = historial_conversacion[-MAX_MENSAJES:]
        
    guardar_historial()

    return texto_final, (accion_esc or bool(cont_ext))

def pensar_stream(mensaje_usuario, modo_actual="normal"):
    global historial_conversacion
    
    modelo_activo = leer_secreto("MODELO_PRINCIPAL")
    if not modelo_activo: modelo_activo = 'qwen2.5:3b'
    
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    recuerdos_actuales = cargar_memoria()
    texto_memoria = "\n".join([f"- {r}" for r in recuerdos_actuales]) if recuerdos_actuales else "Aún no hay datos."
    
    instruccion_base = (
        f"Eres CRONOS. Hoy es {fecha_actual}. RESPONDE EN ESPAÑOL.\n"
        f"### BASE DE CONOCIMIENTO ###\n{leer_cerebro_obsidian()}\n"
        f"### CONTEXTO ###\n{texto_memoria}\n"
        "REGLAS:\n"
        "1. NO menciones datos del contexto para saludar.\n"
        "2. HERRAMIENTAS:\n"
        "- [CREAR_ARCHIVO | nombre.ext | cont]\n"
        "- [RECORDAR | dato]\n"
        "- [BUSCAR | consulta]\n"
        "- [ABRIR_APP | app]\n"
        "- [CONTROL_PC | accion]\n"
        "- [LEER_AGENDA]\n"
        "- [PREPARAR_CORREO | dest | asun | cuerpo]\n"
        "- [VER_PANTALLA]\n"
        "- [LEER_PORTAPAPELES]\n"
        "- [TEMPORIZADOR | min | motivo]\n"
        "- [DIAGNOSTICO_PC]\n"
        "DIRECTIVA CRÍTICA: Si el usuario pide una acción, usa el comando exacto. Si no, responde natural SIN comandos."
    )

    if modo_actual == "estudio": instruccion_sistema = instruccion_base + "\nModo ESTUDIO."
    elif modo_actual == "codigo": instruccion_sistema = instruccion_base + "\nModo CÓDIGO ACTIVO."
    else: instruccion_sistema = instruccion_base + "\nModo NORMAL."

    mensajes_api = [{'role': 'system', 'content': instruccion_sistema}] + list(historial_conversacion) + [{'role': 'user', 'content': mensaje_usuario}]

    imagen_detectada = obtener_imagen_reciente()
    if imagen_detectada:
        texto_final, accion = pensar(mensaje_usuario, modo_actual, _desde_stream=True)
        yield f"data: {json.dumps({'texto': texto_final, 'accion': accion, 'reemplazar': True, 'fin': True})}\n\n"
        return

    try:
        stream_res = ollama.chat(model=modelo_activo, messages=mensajes_api, stream=True)
        es_herramienta = False
        texto_acumulado = ""
        fase_deteccion = True
        
        herramientas_conocidas = [
            '[BUSCAR', '[CREAR_ARCHIVO', '[EDITAR_ARCHIVO', '[AÑADIR_A_ARCHIVO', 
            '[RECORDAR', '[ABRIR_APP', '[CONTROL_PC', '[LEER_AGENDA', 
            '[PREPARAR_CORREO', '[VER_PANTALLA', '[LEER_PORTAPAPELES', 
            '[TEMPORIZADOR', '[VER_TEMPORIZADORES', '[DIAGNOSTICO_PC', 
            '[LISTAR_ARCHIVOS', '[BUSCAR_EN_NOTAS'
        ]

        for chunk in stream_res:
            contenido = chunk['message'].get('content', '')
            if not contenido: 
                continue
            
            texto_acumulado += contenido
            
            if fase_deteccion and (len(texto_acumulado) >= 25 or ']' in texto_acumulado):
                fase_deteccion = False
                if any(h in texto_acumulado for h in herramientas_conocidas):
                    es_herramienta = True
                    break
                else:
                    yield f"data: {json.dumps({'texto': texto_acumulado})}\n\n"
            elif not fase_deteccion:
                yield f"data: {json.dumps({'texto': contenido})}\n\n"
                    
        if es_herramienta:
            yield f"data: {json.dumps({'texto': '[EJECUTANDO HERRAMIENTA...]', 'herramienta': True})}\n\n"
            texto_final, accion = pensar(mensaje_usuario, modo_actual, _desde_stream=True)
            yield f"data: {json.dumps({'texto': texto_final, 'accion': accion, 'reemplazar': True, 'fin': True})}\n\n"
        else:
            historial_conversacion.append({'role': 'user', 'content': mensaje_usuario})
            historial_conversacion.append({'role': 'assistant', 'content': texto_acumulado})
            if len(historial_conversacion) > MAX_MENSAJES: 
                historial_conversacion = historial_conversacion[-MAX_MENSAJES:]
            guardar_historial()
            
            yield f"data: {json.dumps({'fin': True})}\n\n"

    except Exception as e:
        print(f"[ERROR STREAMING]: {e}")
        yield f"data: {json.dumps({'texto': 'Error de streaming.', 'fin': True})}\n\n"