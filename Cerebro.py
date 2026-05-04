import ollama
from ddgs import DDGS
import datetime
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

historial_conversacion = []
MAX_MENSAJES = 10
DIRECTORIO_SEGURO = os.path.expanduser("~/CronOS_Obsidian/Cerebro_CronOS")
ARCHIVO_MEMORIA = os.path.join(DIRECTORIO_SEGURO, "Memoria_CronOS.md")

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
        print(f"[ERROR DE RED]: {e}")
        return "SISTEMA: Fallo de conexión o librería. Informa al usuario de que no puedes acceder a Internet ahora mismo."

def verificar_ruta_segura(ruta):
    nombre_archivo = os.path.basename(ruta)
    return os.path.join(DIRECTORIO_SEGURO, nombre_archivo)

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
            return [linea.strip('- \n') for linea in lineas if linea.startswith('-')]
    return []

def guardar_memoria(dato):
    memoria = cargar_memoria()
    if dato not in memoria:
        memoria.append(dato)
        
        if len(memoria) > 20:
            memoria = memoria[-20:]
            
        with open(ARCHIVO_MEMORIA, 'w', encoding='utf-8') as f:
            for m in memoria:
                f.write(f"- {m}\n")

def leer_secreto(clave):
    ruta_secrets = os.path.join(DIRECTORIO_SEGURO, "Secreto.txt")
    if os.path.exists(ruta_secrets):
        with open(ruta_secrets, 'r') as f:
            for linea in f:
                if linea.startswith(f"{clave}="):
                    return linea.strip().split("=", 1)[1]
    return None

def leer_cerebro_obsidian():
    conocimiento_base = ""
    conocimiento_extra = ""
    archivos_criticos = ["01_Personalidad_CronOS.md", "02_Perfil_Rafael.md", "memoria_cronos.md"]
    
    try:
        for archivo in archivos_criticos:
            ruta = os.path.join(DIRECTORIO_SEGURO, archivo)
            if os.path.exists(ruta):
                with open(ruta, 'r', encoding='utf-8') as f:
                    conocimiento_base += f"\n[DOCUMENTO CRÍTICO: {archivo}]\n{f.read()}\n"
        
        for archivo in os.listdir(DIRECTORIO_SEGURO):
            if archivo.lower().endswith(".md") and archivo not in archivos_criticos:
                ruta = os.path.join(DIRECTORIO_SEGURO, archivo)
                with open(ruta, 'r', encoding='utf-8') as f:
                    conocimiento_extra += f"\n[DOCUMENTO: {archivo}]\n{f.read()}\n"
        
        espacio_restante = 8000 - len(conocimiento_base)
        if espacio_restante > 0:
            conocimiento_final = conocimiento_base + conocimiento_extra[:espacio_restante]
        else:
            conocimiento_final = conocimiento_base
            
        return conocimiento_final
    except Exception:
        return ""

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
        except Exception: pass
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
        except Exception: pass
        
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
            print(f"[*] CronOS buscando en la red global: {consulta}")
            resultados = buscar_en_la_red(consulta.strip())
            resultados_totales += f"\nResultados de la red para '{consulta}':\n{resultados}\n"
        except Exception:
            pass
    return re.sub(patron_buscar, '', texto).strip(), resultados_totales

def procesar_apertura_app(texto):
    patron_abrir = r'\[ABRIR_APP\s*\|\s*(.*?)\]'
    coincidencias = re.findall(patron_abrir, texto)
    
    apps_seguras = {
        "navegador": "google-chrome",
        "chrome": "google-chrome",
        "google chrome": "google-chrome",
        "archivos": "nemo",
        "nemo": "nemo",
        "carpeta": "nemo",
        "codigo": "code",
        "code": "code",
        "vscode": "code",
        "terminal": "gnome-terminal",
        "consola": "gnome-terminal"
    }
    
    acciones = ""
    for app in coincidencias:
        app_limpia = app.strip().lower()
        print(f"[*] CronOS intentando ejecutar comando: '{app_limpia}'")
        
        comando_a_ejecutar = None
        for clave, comando in apps_seguras.items():
            if clave in app_limpia:
                comando_a_ejecutar = comando
                break
        
        if comando_a_ejecutar:
            try:
                subprocess.Popen([comando_a_ejecutar], start_new_session=True)
                acciones += f"He ejecutado la apertura de {comando_a_ejecutar}. "
            except Exception as e:
                print(f"[ERROR DE SISTEMA]: No se pudo abrir {comando_a_ejecutar}. {e}")
                acciones += f"Hubo un fallo en Linux Mint al intentar abrir {comando_a_ejecutar}. "
        else:
            acciones += f"No tengo permisos de seguridad para abrir la aplicación '{app_limpia}'. "
            
    texto_limpio = re.sub(patron_abrir, '', texto).strip()
    
    if acciones:
        texto_limpio = f"{texto_limpio} {acciones}".strip()
        
    return texto_limpio

def procesar_control_pc(texto):
    patron_control = r'\[?CONTROL_PC\s*\|\s*([a-zA-Z0-9_ ]+)\]?'
    coincidencias = re.findall(patron_control, texto)
    
    comandos_seguros = {
        "subir volumen": ["amixer", "-q", "sset", "Master", "10%+"],
        "subir_volumen": ["amixer", "-q", "sset", "Master", "10%+"],
        "bajar volumen": ["amixer", "-q", "sset", "Master", "10%-"],
        "bajar_volumen": ["amixer", "-q", "sset", "Master", "10%-"],
        "mutear": ["amixer", "-q", "sset", "Master", "toggle"],
        "silenciar": ["amixer", "-q", "sset", "Master", "toggle"],
        "volumen maximo": ["amixer", "-q", "sset", "Master", "100%"],
        "volumen_maximo": ["amixer", "-q", "sset", "Master", "100%"],
        "suspender": ["systemctl", "suspend"]
    }
    
    acciones = ""
    for accion in coincidencias:
        accion_limpia = accion.strip().lower()
        print(f"[*] CronOS ejecutando orden de sistema: '{accion_limpia}'")
        
        comando_a_ejecutar = None
        for clave, cmd in comandos_seguros.items():
            if clave in accion_limpia:
                comando_a_ejecutar = cmd
                break
                
        if comando_a_ejecutar:
            try:
                import subprocess
                subprocess.run(comando_a_ejecutar)
                acciones += f"He ejecutado la orden en tu ordenador. "
            except Exception as e:
                print(f"[ERROR DE SISTEMA]: {e}")
                acciones += f"No he podido ejecutar la orden debido a un error del sistema operativo. "
        else:
            acciones += f"La orden '{accion_limpia}' no está en mi lista de protocolos seguros. "

    texto_limpio = re.sub(patron_control, '', texto).strip()
    if acciones:
        texto_limpio = f"{texto_limpio} {acciones}".strip()
        
    return texto_limpio

def leer_eventos_calendario():
    ruta_ics = os.path.join(DIRECTORIO_SEGURO, "mi_agenda.ics")
    
    url_google = leer_secreto("CALENDAR_URL")
    
    if url_google:
        try:
            print("[*] Sincronizando agenda con la nube de Google...")
            respuesta = requests.get(url_google, timeout=5)
            respuesta.raise_for_status()
            with open(ruta_ics, 'wb') as f:
                f.write(respuesta.content)
            print("[*] Agenda sincronizada correctamente.")
        except Exception as e:
            print(f"[ERROR DE RED] No se pudo actualizar el calendario desde Google. Detalle: {e}")
    else:
        print("[AVISO] No se encontró 'CALENDAR_URL' en secrets.txt. Usando copia local si existe.")
    
    if not os.path.exists(ruta_ics):
        return "No se encontró el archivo de agenda."
    
    try:
        from icalendar import Calendar
        import recurring_ical_events
        import pytz
        
        with open(ruta_ics, 'rb') as f:
            cal = Calendar.from_ical(f.read())
        
        zona_espana = pytz.timezone('Europe/Madrid')
        hoy = datetime.date.today()
        fecha_fin = hoy + datetime.timedelta(days=30) 
        
        eventos_expandidos = recurring_ical_events.of(cal).between(hoy, fecha_fin)
        
        eventos_raw = []
        
        for component in eventos_expandidos:
            dtstart_raw = component.get('dtstart')
            if dtstart_raw is not None:
                dt_val = dtstart_raw.dt
                
                if isinstance(dt_val, datetime.datetime):
                    if dt_val.tzinfo is None:
                        dt_val = pytz.utc.localize(dt_val)
                    dt_local = dt_val.astimezone(zona_espana)
                    
                    fecha_str = dt_local.strftime('%d-%m-%Y a las %H:%M')
                    fecha_matematica = dt_local
                else:
                    fecha_str = dt_val.strftime('%d-%m-%Y (Todo el día)')
                    fecha_matematica = zona_espana.localize(datetime.datetime.combine(dt_val, datetime.time.min))
                
                if fecha_matematica.date() >= hoy:
                    resumen = component.get('summary', 'Evento sin título')
                    eventos_raw.append((fecha_matematica, f"- {fecha_str}: {resumen}"))
        
        if not eventos_raw:
            return "La agenda está libre, no hay eventos próximos."
        
        eventos_raw.sort(key=lambda x: x[0])
        
        eventos_finales = []
        textos_vistos = set()
        for _, texto in eventos_raw:
            if texto not in textos_vistos:
                textos_vistos.add(texto)
                eventos_finales.append(texto)
        
        return "Eventos próximos:\n" + "\n".join(eventos_finales[:7])
        
    except Exception as e:
        return f"Error interno al analizar el calendario: {e}"
    
def procesar_agenda(texto):
    patron_agenda = r'\[?LEER_AGENDA\]?'
    if re.search(patron_agenda, texto):
        print("[*] CronOS accediendo a la agenda local...")
        eventos = leer_eventos_calendario()
        texto_limpio = re.sub(patron_agenda, '', texto).strip()
        return texto_limpio, eventos
    return texto, None

def procesar_recuerdos(texto):
    patron_memoria = r'\[?RECORDAR\s*\|\s*([^\n\]]+)\]?'
    coincidencias = re.findall(patron_memoria, texto)
    for dato in coincidencias:
        guardar_memoria(dato.strip())
    return re.sub(patron_memoria, '', texto).strip()

def limpiar_historial():
    global historial_conversacion
    historial_conversacion = []

def obtener_imagen_reciente():
    extensiones = ('.png', '.jpg', '.jpeg')
    archivos_validos = []
    directorio_imagenes = os.path.join(DIRECTORIO_SEGURO, "Imagenes")
    try:
        if not os.path.exists(directorio_imagenes):
            return None
        for archivo in os.listdir(directorio_imagenes):
            if archivo.lower().endswith(extensiones):
                ruta_completa = os.path.join(directorio_imagenes, archivo)
                archivos_validos.append(ruta_completa)
        if not archivos_validos:
            return None
        archivo_mas_reciente = max(archivos_validos, key=os.path.getmtime)
        if time.time() - os.path.getmtime(archivo_mas_reciente) < 300:
            return archivo_mas_reciente
    except Exception:
        pass
    return None

def codificar_imagen_base64(ruta):
    try:
        with open(ruta, "rb") as archivo_imagen:
            return base64.b64encode(archivo_imagen.read()).decode('utf-8')
    except Exception:
        return None

def pensar(mensaje_usuario, modo_actual="normal"):
    global historial_conversacion
    os.makedirs(DIRECTORIO_SEGURO, exist_ok=True)
    
    modelo_activo = 'qwen2.5:3b'
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    recuerdos_actuales = cargar_memoria()
    texto_memoria = "\n".join([f"- {r}" for r in recuerdos_actuales]) if recuerdos_actuales else "Aún no hay datos."
    
    conocimiento_obsidian = leer_cerebro_obsidian()

    instruccion_base = f"Eres CRONOS. Hoy es {fecha_actual}. RESPONDE EN ESPAÑOL.\n" \
                        f"### BASE DE CONOCIMIENTO (OBSIDIAN) ###\n" \
                        f"{conocimiento_obsidian}\n" \
                        f"### CONTEXTO DEL USUARIO ###\n" \
                        f"{texto_memoria}\n" \
                        "REGLAS DE COMPORTAMIENTO:\n" \
                        "1. SUTILEZA: NO menciones los datos del contexto para saludar.\n" \
                        "2. SIGLAS: ESTÁ ESTRICTAMENTE PROHIBIDO inventar siglas.\n" \
                        "3. EJECUCIÓN DE HERRAMIENTAS (USO OBLIGATORIO Y ESTRICTO):\n" \
                        "- Crear archivos: [CREAR_ARCHIVO | nombre.ext | contenido]\n" \
                        "- Guardar datos: [RECORDAR | El usuario...]\n" \
                        "- Buscar en Internet: [BUSCAR | palabras clave]\n" \
                        "- Abrir programas: [ABRIR_APP | app]\n" \
                        "- Controlar sistema: [CONTROL_PC | accion]\n" \
                        "- Consultar agenda del usuario: [LEER_AGENDA]\n" \
                        "DIRECTIVA CRÍTICA: Responde a las peticiones de acción ÚNICAMENTE con el formato exacto del comando INCLUYENDO LOS CORCHETES. Si el usuario te pregunta por sus eventos, citas o exámenes, usa SIEMPRE [LEER_AGENDA] y detente. Yo interceptaré el comando."
    
    if modo_actual == "estudio":
        instruccion_sistema = instruccion_base + "\nModo ESTUDIO: Eres un tutor experto."
    elif modo_actual == "codigo":
        instruccion_sistema = instruccion_base + "\nModo CÓDIGO ACTIVO: MUESTRA EL CÓDIGO DIRECTAMENTE. ESTÁ PROHIBIDO AÑADIR COMENTARIOS DENTRO DEL CÓDIGO."
    else:
        instruccion_sistema = instruccion_base + "\nModo NORMAL: Profesional y directo."

    historial_conversacion.append({'role': 'user', 'content': mensaje_usuario})
    
    mensajes_api = [{'role': 'system', 'content': instruccion_sistema}]
    for msg in historial_conversacion:
        mensajes_api.append(dict(msg))
        
    imagen_detectada = obtener_imagen_reciente()
    
    if imagen_detectada:
        imagen_b64 = codificar_imagen_base64(imagen_detectada)
        if imagen_b64:
            modelo_activo = 'moondream'
            mensajes_api[-1]['images'] = [imagen_b64]
            mensajes_api[0]['content'] = "Analyze the image and describe it in detail."

    try:
        respuesta = ollama.chat(model=modelo_activo, messages=mensajes_api)
        texto_bruto = respuesta['message'].get('content', '')
        
        if not texto_bruto:
            return "He analizado la imagen, pero el núcleo visual ha devuelto una respuesta vacía. Intenta hacer una pregunta más específica.", False

        if modelo_activo == 'moondream':
            mensajes_traduccion = [
                {'role': 'system', 'content': instruccion_sistema},
                {'role': 'user', 'content': f"El módulo visual reporta esto de la imagen: '{texto_bruto}'. Usando esta información, responde en español a mi pregunta original: '{mensaje_usuario}'. IMPORTANTE: Responde directamente y de forma natural. NO uses encabezados, ni etiquetas Markdown como '### Respuesta ###', ni preámbulos."}
            ]
            respuesta_qwen = ollama.chat(model='qwen2.5', messages=mensajes_traduccion)
            texto_bruto = respuesta_qwen['message'].get('content', texto_bruto)

    except Exception as e:
        print(f"[ERROR CRÍTICO OLLAMA]: {e}")
        return f"Error en el núcleo de procesamiento. Revisa la terminal.", False
    
    texto_bruto, contenido_extraido = procesar_lectura(texto_bruto)
    if contenido_extraido:
        try:
            contexto_archivo = [{'role': 'user', 'content': f"Datos leídos:\n{contenido_extraido}"}]
            segunda_res = ollama.chat(model=modelo_activo, messages=mensajes_api + contexto_archivo)
            texto_bruto = segunda_res['message'].get('content', texto_bruto)
        except Exception:
            pass

    texto_bruto, resultados_red = procesar_busqueda(texto_bruto)
    texto_bruto, resultados_agenda = procesar_agenda(texto_bruto)
    if resultados_agenda:
        print("\n--- [DEPURACIÓN] DATOS CRUDOS DEL CALENDARIO ---")
        print(resultados_agenda)
        print("------------------------------------------------\n")
        
        try:
            hoy_dt = datetime.date.today()
            manana_dt = hoy_dt + datetime.timedelta(days=1)
            hoy_str = hoy_dt.strftime('%d-%m-%Y')
            manana_str = manana_dt.strftime('%d-%m-%Y')
            
            prompt_agenda = (
                f"El usuario pregunta: '{mensaje_usuario}'.\n"
                f"REFERENCIA DE TIEMPO: Hoy es {hoy_str}. Mañana es {manana_str}.\n\n"
                f"EVENTOS EXACTOS DE SU CALENDARIO:\n{resultados_agenda}\n\n"
                "INSTRUCCIÓN CRÍTICA: "
                "1. Busca la fecha solicitada usando la REFERENCIA DE TIEMPO. "
                "2. Dime los eventos y sus horas para esa fecha. "
                "3. PROHIBIDO INVENTAR. Si la fecha que pide no está en la lista de eventos, di que no tiene nada. "
                "4. Sé directo, breve y no hagas preguntas."
            )
            
            mensajes_limpios = [
                {'role': 'system', 'content': "Eres CronOS, una IA analítica de agenda."},
                {'role': 'user', 'content': prompt_agenda}
            ]
            
            cuarta_res = ollama.chat(model=modelo_activo, messages=mensajes_limpios)
            texto_bruto = cuarta_res['message'].get('content', texto_bruto)
        except Exception:
            pass

    texto_bruto = re.sub(r'\[BUSCAR\s*\|\s*(.*?)\]', '', texto_bruto).strip()
    texto_bruto = re.sub(r'\[LEER_ARCHIVO\s*\|\s*(.*?)\]', '', texto_bruto).strip()
    texto_bruto = re.sub(r'\[?LEER_AGENDA\]?', '', texto_bruto).strip() # <-- NUEVA DEFENSA
    texto_bruto = procesar_apertura_app(texto_bruto)
    texto_bruto = procesar_control_pc(texto_bruto)

    texto_bruto = procesar_recuerdos(texto_bruto)
    texto_final, accion_escritura = procesar_escritura(texto_bruto)
    
    historial_conversacion.append({'role': 'assistant', 'content': texto_final})
    if len(historial_conversacion) > MAX_MENSAJES: 
        historial_conversacion = historial_conversacion[-MAX_MENSAJES:]

    return texto_final, (accion_escritura or bool(contenido_extraido))