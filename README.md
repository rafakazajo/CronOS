# CronOS
**rafakazajo**

Este es mi asistente virtual personal llamado CronOS con una IA en local. Es un proyecto casero hecho por diversión, ganas de investigar y pasión por la Inteligencia Artificial y la domótica.

---

## Cómo funciona

CronOS es un asistente interactivo con personalidad propia, diseñado para funcionar como un ente independiente. Utiliza una arquitectura de **Privacidad Híbrida** que combina procesamiento neuronal 100% local con herramientas de alta velocidad.

## Hardware del Proyecto

Este proyecto está diseñado para convertirse en un asistente personal físico, capaz de interactuar sin necesidad de usar un ordenador tradicional:

???

## Arquitectura de Software (CronOS v1.0)

* **Motor Lógico:** Ollama corriendo el modelo `qwen2.5` (Lógico, rapidísimo y sin censura).
* **Interfaz:** Servidor web Flask con una UI dinámica en HTML/CSS/JS (animaciones en tiempo real, ecualizador sincronizado).
* **Reconocimiento de Voz:** Web Speech API del navegador (Alta precisión y velocidad).
* **Síntesis de Voz:** `edge-tts` y `pygame` (Voz humana fluida).
* **Conexión a Internet (RAG):** `duckduckgo-search` para dotar al asistente de memoria actual, fecha y noticias en tiempo real.

---

## Instalación y Uso

Si quieres desplegar este núcleo en tu propia máquina, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/rafakazajo/CronOS.git](https://github.com/rafakazajo/CronOS.git)
   cd CronOS
   ```

2. **Instalar Ollama y el Modelo:**

    Asegúrate de tener Ollama instalado en tu sistema. Luego, descarga el cerebro:

    ```bash
    ollama run qwen2.5
    ```

3. **Instalar las dependencias de Python:**

    ```bash
    pip install -r Requisitos.txt
    ```

4. **Despertar a CronOS:**

    Ejecuta el servidor principal:

    ```bash
    python App.py
    ```

    Abre tu navegador (Chrome/Edge recomendado para el micrófono) y entra en http://localhost:5000 o usa la IP de tu Mini PC para controlarlo desde tu móvil.

---

### 3. Tus notas para Obsidian
Obsidian es perfecto para estructurar cómo funciona tu sistema por dentro. Crea una nota llamada `Proyecto CronOS` y pega esto. Te servirá como mapa mental para cuando quieras retomar las mejoras en el futuro:

# Proyecto CronOS - Asistente IA
**Estado actual:** Estable (Privacidad Híbrida)
**Tags:** #IA #Local #Python #Hardware #Asistente

## Arquitectura del Sistema
CronOS funciona con un ecosistema modular gestionado a través de un servidor Flask.

- **Cerebro.py:** Gestiona la lógica mediante la API de `ollama`. Usa el modelo **Qwen 2.5**. Incorpora un sistema de reloj (`datetime`) para inyectar la fecha actual y evitar alucinaciones temporales. Si detecta palabras clave (busca, hoy, precio), utiliza `duckduckgo-search` para inyectar contexto de la red (RAG).
- **Boca.py:** Convierte texto a voz. Usa `edge-tts` (Microsoft) para obtener una voz hiper-realista y `pygame` para reproducirlo en el altavoz Jabra. Cuenta con un sensor global `esta_hablando` para sincronizar la UI.
- **App.py:** Enruta las peticiones de la web a los scripts de Python.
- **Frontend (index.html):** Interfaz limpia estilo terminal (`Comic Mono`). Controla el Oído usando `webkitSpeechRecognition` para una transcripción inmediata. Tiene un ecualizador que consulta cada 500ms al servidor si debe seguir moviéndose.

## El concepto de "Privacidad Híbrida"
Decisión de diseño tomada para optimizar un Mini PC sin GPU dedicada:
1. **Peticiones diarias (Voz):** Pasan por Chrome/Edge para mayor precisión y velocidad sin saturar la CPU.
2. **Peticiones críticas (Teclado):** Se escriben a mano, asegurando que 0 bytes salgan hacia Google. El procesamiento de texto (Ollama) siempre es 100% local.