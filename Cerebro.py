import ollama
from duckduckgo_search import DDGS
import datetime
import os
import re
import json

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

def pensar(mensaje_usuario, modo_actual="normal"):
    global historial_conversacion
    os.makedirs(DIRECTORIO_SEGURO, exist_ok=True)
    
    MODELO_ELEGIDO = 'qwen2.5'
    fecha_actual = datetime.datetime.now().strftime("%d de %B de %Y")
    
    recuerdos_actuales = cargar_memoria()
    texto_memoria = "\n".join([f"- {r}" for r in recuerdos_actuales]) if recuerdos_actuales else "Aún no hay datos."

    instruccion_base = f"Eres CRONOS. Hoy es {fecha_actual}. RESPONDE EN ESPAÑOL.\n" \
                       f"### CONTEXTO DEL USUARIO ###\n" \
                       f"{texto_memoria}\n" \
                       "REGLAS DE COMPORTAMIENTO:\n" \
                       "1. SUTILEZA: NO menciones los datos del contexto del usuario para saludar. Úsalos ÚNICAMENTE si la pregunta lo requiere.\n" \
                       "2. SIGLAS: ESTÁ ESTRICTAMENTE PROHIBIDO inventar siglas.\n" \
                       "3. EJECUCIÓN DE HERRAMIENTAS (¡MUY IMPORTANTE!):\n" \
                       "- Si el usuario te pide CREAR, GUARDAR o HACER un archivo, ESTÁS OBLIGADO a usar este comando exacto al final de tu respuesta, en una línea nueva: [CREAR_ARCHIVO | nombre_del_archivo.ext | contenido del archivo]\n" \
                       "- Si el usuario menciona un dato nuevo sobre sí mismo, guárdalo obligatoriamente: [RECORDAR | El usuario...]\n" \
                       "- NUNCA le digas al usuario que copie y pegue el código en un archivo si te ha pedido que lo crees tú."

    if modo_actual == "estudio":
        instruccion_sistema = instruccion_base + "\nModo ESTUDIO: Eres un tutor experto. Explica los conceptos paso a paso con analogías."
    elif modo_actual == "codigo":
        instruccion_sistema = instruccion_base + "\nModo CÓDIGO ACTIVO: Eres un Ingeniero Senior. MUESTRA EL CÓDIGO DIRECTAMENTE. REGLA DE ORO: ESTÁ TOTAL Y ABSOLUTAMENTE PROHIBIDO AÑADIR COMENTARIOS (# o //) DENTRO DEL CÓDIGO. NINGUNO. CERO. Si incumples esto, el sistema fallará."
    else:
        instruccion_sistema = instruccion_base + "\nModo NORMAL: Profesional, directo y amable."

    historial_conversacion.append({'role': 'user', 'content': mensaje_usuario})
    
    respuesta = ollama.chat(model=MODELO_ELEGIDO, messages=[{'role': 'system', 'content': instruccion_sistema}] + historial_conversacion)
    texto_bruto = respuesta['message']['content']
    
    texto_bruto, contenido_extraido = procesar_lectura(texto_bruto)
    
    if contenido_extraido:
        contexto_archivo = [{'role': 'user', 'content': f"Datos leídos:\n{contenido_extraido}"}]
        segunda_res = ollama.chat(model=MODELO_ELEGIDO, messages=[{'role': 'system', 'content': instruccion_sistema}] + historial_conversacion + contexto_archivo)
        texto_bruto = segunda_res['message']['content']

    texto_bruto = procesar_recuerdos(texto_bruto)
    texto_final, accion_escritura = procesar_escritura(texto_bruto)
    
    historial_conversacion.append({'role': 'assistant', 'content': texto_final})
    if len(historial_conversacion) > MAX_MENSAJES: historial_conversacion = historial_conversacion[-MAX_MENSAJES:]

    return texto_final, (accion_escritura or bool(contenido_extraido))