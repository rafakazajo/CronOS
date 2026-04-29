import ollama
from duckduckgo_search import DDGS
import datetime
import os
import re

historial_conversacion = []
MAX_MENSAJES = 10
DIRECTORIO_SEGURO = os.path.expanduser("~/CronOS_Archivos")

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
    
    # Si se crearon archivos, añadimos la confirmación verbal
    if nombres_archivos:
        confirmacion = f"He procedido a crear el archivo {', '.join(nombres_archivos)} en el núcleo."
        if texto_limpio:
            texto_limpio += " " + confirmacion
        else:
            texto_limpio = confirmacion
            
    return texto_limpio, bool(nombres_archivos)

def pensar(mensaje_usuario, modo_actual="normal"):
    global historial_conversacion
    os.makedirs(DIRECTORIO_SEGURO, exist_ok=True)
    
    MODELO_ELEGIDO = 'qwen2.5'
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")

    instruccion_base = f"Eres CRONOS. Hoy es {fecha_actual}. RESPONDE SIEMPRE EN ESPAÑOL. " \
                       f"Carpeta: {DIRECTORIO_SEGURO}. " \
                       "Para escribir: [CREAR_ARCHIVO | nombre | contenido]. Para leer: [LEER_ARCHIVO | nombre]."

    if modo_actual == "estudio":
        instruccion_sistema = instruccion_base + "\nModo ESTUDIO: Tutor experto. Explica conceptos paso a paso."
    elif modo_actual == "codigo":
        instruccion_sistema = instruccion_base + "\nModo CÓDIGO: Ingeniero senior. Código limpio sin comentarios internos."
    else:
        instruccion_sistema = instruccion_base + "\nModo NORMAL: Profesional y directo."

    historial_conversacion.append({'role': 'user', 'content': mensaje_usuario})
    
    respuesta = ollama.chat(model=MODELO_ELEGIDO, messages=[{'role': 'system', 'content': instruccion_sistema}] + historial_conversacion)
    texto_bruto = respuesta['message']['content']
    
    texto_bruto, contenido_extraido = procesar_lectura(texto_bruto)
    
    if contenido_extraido:
        contexto_archivo = [{'role': 'user', 'content': f"Datos leídos:\n{contenido_extraido}"}]
        segunda_res = ollama.chat(model=MODELO_ELEGIDO, messages=[{'role': 'system', 'content': instruccion_sistema}] + historial_conversacion + contexto_archivo)
        texto_bruto = segunda_res['message']['content']

    texto_final, accion_escritura = procesar_escritura(texto_bruto)
    
    historial_conversacion.append({'role': 'assistant', 'content': texto_final})
    if len(historial_conversacion) > MAX_MENSAJES: historial_conversacion = historial_conversacion[-MAX_MENSAJES:]

    return texto_final, (accion_escritura or bool(contenido_extraido))