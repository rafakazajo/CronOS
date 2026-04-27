import speech_recognition as sr

def escuchar():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Oído: Ajustando al ruido de fondo... un momento.")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("Oído: Te escucho...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("Oído: Procesando...")
            texto = recognizer.recognize_google(audio, language="es-ES")
            return texto
            
        except sr.WaitTimeoutError:
            # Si pasa el tiempo y no hablas
            return "" 
        except sr.UnknownValueError:
            print("Oído: No he entendido lo que has dicho.")
            return ""
        except sr.RequestError as e:
            print(f"Oído: Error del servicio de reconocimiento: {e}")
            return "Error de conexión en el Oído."

if __name__ == "__main__":
    print("Prueba de módulo Oído iniciada.")
    frase = escuchar()
    print(f"Has dicho: {frase}")