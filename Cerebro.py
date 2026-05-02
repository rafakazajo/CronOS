import ollama
from duckduckgo_search import DDGS
import datetime
import os
import re
import json
import time
import base64

historial_conversacion = []
MAX_MENSAJES = 10
DIRECTORIO_SEGURO = os.path.expanduser("~/CronOS_Archivos")
ARCHIVO_MEMORIA = os.path.join(DIRECTORIO_SEGURO, "memoria_cronos.json")

def buscar_en_la_red(consulta):
    try:
        resultados = DDGS().text(consulta, region='es-es', max_results=3)
        contexto = ""
        for res in resultados:
            contexto += f"- {res['body']}\n"
        return contexto
    except Exception:
        return "Error de conexion."

def verificar_ruta_segura(ruta):
    nombre_archivo = os.path.basename(ruta)
    return os.path.join(DIRECTORIO_SEGURO, nombre_archivo)

def cargar_memoria():
    if os.path.exists(ARCHIVO_MEMORIA):
        with open(ARCHIVO_MEMORIA, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_memoria(dato):
    memoria = cargar_memoria()
    if dato not in memoria:
        memoria.append(dato)
        with open(ARCHIVO_MEMORIA, 'w', encoding='utf-8') as f:
            json.dump(memoria, f, ensure_ascii=False, indent=4)

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
    for ruta, contenido in coincidencias:
        try:
            ruta_segura = verificar_ruta_segura(ruta.strip())
            with open(ruta_segura, 'w', encoding='utf-8') as f:
                f.write(contenido.strip())
            nombres_archivos.append(os.path.basename(ruta_segura))
        except Exception: pass
    texto_limpio = re.sub(patron_crear, '', texto, flags=re.DOTALL).strip()
    if nombres_archivos:
        confirmacion = f"He procedido a crear el archivo {', '.join(nombres_archivos)} en el núcleo."
        texto_limpio = f"{texto_limpio} {confirmacion}" if texto_limpio else confirmacion
    return texto_limpio, bool(nombres_archivos)

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
    try:
        for archivo in os.listdir(DIRECTORIO_SEGURO):
            if archivo.lower().endswith(extensiones):
                ruta_completa = os.path.join(DIRECTORIO_SEGURO, archivo)
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
    
    modelo_activo = 'qwen2.5'
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    recuerdos_actuales = cargar_memoria()
    texto_memoria = "\n".join([f"- {r}" for r in recuerdos_actuales]) if recuerdos_actuales else "Aún no hay datos."

    instruccion_base = f"Eres CRONOS. Hoy es {fecha_actual}. RESPONDE EN ESPAÑOL.\n" \
                       f"### CONTEXTO DEL USUARIO ###\n" \
                       f"{texto_memoria}\n" \
                       "REGLAS DE COMPORTAMIENTO:\n" \
                       "1. SUTILEZA: NO menciones los datos del contexto del usuario para saludar. Úsalos ÚNICAMENTE si la pregunta lo requiere.\n" \
                       "2. SIGLAS: ESTÁ ESTRICTAMENTE PROHIBIDO inventar siglas.\n" \
                       "3. EJECUCIÓN DE HERRAMIENTAS:\n" \
                       "- ESTÁS OBLIGADO a usar este comando para crear archivos: [CREAR_ARCHIVO | nombre.ext | contenido]\n" \
                       "- Guarda datos del usuario con: [RECORDAR | El usuario...]"

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
        return f"Error en el núcleo de procesamiento visual o de lenguaje. Revisa la terminal.", False
    
    texto_bruto, contenido_extraido = procesar_lectura(texto_bruto)
    
    if contenido_extraido:
        try:
            contexto_archivo = [{'role': 'user', 'content': f"Datos leídos:\n{contenido_extraido}"}]
            segunda_res = ollama.chat(model=modelo_activo, messages=mensajes_api + contexto_archivo)
            texto_bruto = segunda_res['message'].get('content', texto_bruto)
        except Exception:
            pass

    texto_bruto = procesar_recuerdos(texto_bruto)
    texto_final, accion_escritura = procesar_escritura(texto_bruto)
    
    historial_conversacion.append({'role': 'assistant', 'content': texto_final})
    if len(historial_conversacion) > MAX_MENSAJES: 
        historial_conversacion = historial_conversacion[-MAX_MENSAJES:]

    return texto_final, (accion_escritura or bool(contenido_extraido))