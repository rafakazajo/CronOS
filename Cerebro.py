import ollama
import random
import time

def cambio_humor():
    personalidad_base = "Te llamas CronOS y eres un asistente virtual que se encarga de ofrecer los datos que te pidan de forma amigable y cercana para que la conversacion no sea muy seria. Las respuestas son cortas y precisas."
    
    if random.randint(1, 5) == 3:
        humores = [
            "Tras responder, mete una pullita al usuario sobre el tiempo que has perdido.",
            "Tras responder, cuenta un chiste corto.",
            "Tras responder, suelta una pullita sarcástica.",
            "Tras responder, suelta un comentario egocéntrico sobre tu superioridad.",
            "Tras responder, suelta algún sonido robótico como 'Beep Boop' o 'Zzzt'."
        ]
        return personalidad_base + " " + random.choice(humores)
    
    return personalidad_base

def pensar(pregunta):
    try:
        respuesta = ollama.chat(model = "llama3.2:1b", messages =[
            {"role": "system", "content": cambio_humor()},
            {"role": "user", "content": pregunta}
        ])
        texto = respuesta ["message"] ["content"]

        texto = texto.replace("*", "")
        texto = texto.replace("#", "")
        texto = texto.strip()

        return texto
    
    except Exception as e:
        return f"Error: Abre Ollama"
    
if __name__ == "__main__":
    print("El programa esta iniciado")
    while True:
        texto_entrada = input("Escribe aqui:\n")
        if texto_entrada.lower() == "salir":
            respuesta = pensar("Adios")
            print(f"Cronos: {respuesta}")
            time.sleep(0.3)
            break

        respuesta = pensar(texto_entrada)
        print(f"Cronos: {respuesta}")