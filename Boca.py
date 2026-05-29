import pygame
import edge_tts
import asyncio
import os
import re
import threading
import tempfile
import Oido
import Cerebro
from Estado import estado_global

esta_hablando = False
voz = "es-ES-AlvaroNeural"

audio_lock = threading.Lock()

pygame.mixer.init()

async def crear_voz(texto):
    global esta_hablando
    
    with audio_lock:
        esta_hablando = True  
        
    fd, archivo_audio = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    
    texto_limpio = re.sub(r'```.*?```', ' Aquí tienes el código en la pantalla. ', texto, flags=re.DOTALL)
    texto_limpio = re.sub(r'~?/[a-zA-Z0-9_./-]+', 'el archivo indicado', texto_limpio)
    texto_limpio = re.sub(r'\[.*?\]', '', texto_limpio)
    texto_limpio = texto_limpio.replace('*', '').replace('#', '').replace('`', '')

    try:
        llamada_microsoft = edge_tts.Communicate(texto_limpio, voice=voz) 
        await llamada_microsoft.save(archivo_audio)

        with audio_lock:
            pygame.mixer.music.load(archivo_audio)
            pygame.mixer.music.play()
        
        en_reproduccion = True
        while en_reproduccion:
            with audio_lock:
                en_reproduccion = pygame.mixer.music.get_busy()
            if en_reproduccion:
                pygame.time.Clock().tick(10)
            
        with audio_lock:
            pygame.mixer.music.unload()
    except Exception as e:
        print(f"[ERROR BOCA]: {e}")
    finally:
        with audio_lock:
            esta_hablando = False
        
        if os.path.exists(archivo_audio):
            try:
                os.remove(archivo_audio)
            except Exception:
                pass

def hablar(texto):
    asyncio.run(crear_voz(texto))

def callar():
    global esta_hablando
    
    with audio_lock: 
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        esta_hablando = False

def ciclo_voz():
    try:
        estado_global["estado"] = "escuchando"
        estado_global["log"] = "[MIC] Escuchando..."
        
        texto = Oido.escuchar_y_transcribir()
        
        if estado_global.get("cancelar"):
            estado_global["cancelar"] = False
            return

        if not texto:
            estado_global["estado"] = "reposo"
            estado_global["log"] = "[MIC] Silencio detectado."
            return

        estado_global["log"] = f"[STT] Transcrito: {texto}"

        estado_global["estado"] = "pensando"
        estado_global["log"] = "[LLM] Procesando respuesta..."

        respuesta, _ = Cerebro.pensar(texto, "normal")

        estado_global["log"] = f"[LLM] Respuesta lista ({len(respuesta)} chars)"

        estado_global["estado"] = "hablando"
        estado_global["log"] = "[TTS] Sintetizando voz..."

        hablar(respuesta)

        estado_global["log"] = "[VOZ] Reproducción completada."
    except Exception as e:
        estado_global["log"] = f"[ERROR] {e}"
    finally:
        estado_global["cancelar"] = False
        estado_global["estado"] = "reposo"
        estado_global["log"] = "[MIC] Esperando activación táctil..."
        estado_global["ocupado"] = False