import pygame
import edge_tts
import asyncio
import os

esta_hablando = False
voz = "es-ES-AlvaroNeural"

pygame.mixer.init()

async def crear_voz(texto):
    global esta_hablando
    archivo_audio = "respuesta.mp3"
    
    texto_limpio = texto.replace('*', '').replace('#', '')

    try:
        llamada_microsoft = edge_tts.Communicate(texto_limpio, voice=voz) 
        await llamada_microsoft.save(archivo_audio)

        esta_hablando = True  
        
        pygame.mixer.music.load(archivo_audio)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"Error al generar la voz: {e}")
    finally:
        esta_hablando = False  

def hablar(texto):
    asyncio.run(crear_voz(texto))