import pygame
import edge_tts
import asyncio
import os
import re

esta_hablando = False
voz = "es-ES-AlvaroNeural"

pygame.mixer.init()

async def crear_voz(texto):
    global esta_hablando
    archivo_audio = "respuesta.mp3"
    
    texto_limpio = re.sub(r'```.*?```', ' Aquí tienes el código en la pantalla. ', texto, flags=re.DOTALL)
    texto_limpio = re.sub(r'~?/[a-zA-Z0-9_./-]+', 'el archivo indicado', texto_limpio)
    texto_limpio = re.sub(r'\[.*?\]', '', texto_limpio)
    texto_limpio = texto_limpio.replace('*', '').replace('#', '').replace('`', '')

    try:
        llamada_microsoft = edge_tts.Communicate(texto_limpio, voice=voz) 
        await llamada_microsoft.save(archivo_audio)

        esta_hablando = True  
        pygame.mixer.music.load(archivo_audio)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
    except Exception:
        pass
    finally:
        esta_hablando = False  

def hablar(texto):
    asyncio.run(crear_voz(texto))

def callar():
    global esta_hablando
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    esta_hablando = False