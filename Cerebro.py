import ollama
import random
import Boca

historial_conversacion = []

def obtener_personalidad():
    return (
        "Eres CronOS, un asistente virtual útil y directo. "
        "Responde siempre en español. Máximo dos frases."
    )

def pensar(pregunta):
    global historial_conversacion
    if not historial_conversacion:
        historial_conversacion.append({"role": "system", "content": obtener_personalidad()})
    
    historial_conversacion.append({"role": "user", "content": pregunta})

    try:
        respuesta = ollama.chat(model="llama3.2", messages=historial_conversacion)
        texto = respuesta["message"]["content"]
        texto = texto.replace("*", "").replace("#", "").strip()
        
        historial_conversacion.append({"role": "assistant", "content": texto})
        
        if len(historial_conversacion) > 11:
            historial_conversacion = [historial_conversacion[0]] + historial_conversacion[-10:]
            
        return texto
    except Exception as e:
        return f"Error de conexión: {e}"

def saludo_aleatorio():
    return random.choice(["Núcleo en línea.", "Sistemas cargados.", "Escuchando."])