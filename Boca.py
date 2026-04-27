import pygame
import edge_tts
import asyncio
import os

voz = "es-ES-AlvaroNeural"

async def crear_voz(texto):
    archivo_texto = "respuesta.mp3"
    llamada_microsoft = edge_tts.Communicate(texto, voice=voz) 
    await llamada_microsoft.save(archivo_texto)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(archivo_texto)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        
    except Exception as e:
        print(f"Ha habido un error al reproducir la voz\nError: {e}")

def hablar(texto):
    asyncio.run(crear_voz(texto))