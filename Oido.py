import speech_recognition as sr
from faster_whisper import WhisperModel
import os

print("[SISTEMA] Cargando modelo Whisper (Base)...")
modelo = WhisperModel("small", device="cpu", compute_type="int8")
def escuchar_y_transcribir():
    r = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\n[*] Calibrando ruido de fondo (1 segundo)...")
        r.adjust_for_ambient_noise(source, duration=1)
        
        print("[*] Te escucho...")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=15)
        except sr.WaitTimeoutError:
            return None
        except Exception as e:
            print(f"[ERROR DE HARDWARE]: {e}")
            return None

    archivo_temp = "temp_record.wav"
    try:
        with open(archivo_temp, "wb") as f:
            f.write(audio.get_wav_data())
    except Exception as e:
        print(f"[ERROR DE ESCRITURA]: No se pudo guardar el audio. {e}")
        return None

    print("[*] Procesando transcripción en local...")
    try:
        segments, _ = modelo.transcribe(
            archivo_temp, 
            language="es",
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        texto = "".join([segment.text for segment in segments]).strip()
        
        if os.path.exists(archivo_temp):
            os.remove(archivo_temp)
            
        if texto:
            return texto
        return None
        
    except Exception as e:
        print(f"[ERROR TRANSCRIPCIÓN]: {e}")
        return None

if __name__ == "__main__":
    while True:
        texto = escuchar_y_transcribir()
        if texto:
            print(f"-> Has dicho: '{texto}'")
            break
        else:
            print("-> (Silencio o ruido ignorado. Volviendo a intentar...)")
            import time
            time.sleep(1)