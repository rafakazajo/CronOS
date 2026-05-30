# CronOS v1.3 - Sistema Operativo de IA Local
**rafakazajo**

**CronOS** es un asistente virtual avanzado de grado de producción, diseñado bajo una arquitectura modular y enfocado 100% en la privacidad y ejecución local. Permite interactuar con el sistema operativo, gestionar archivos de notas (Bóveda de Obsidian), programar alertas y buscar información mediante lenguaje natural (Voz y Texto).

---

## Visión del Proyecto
El objetivo de CronOS es actuar como una capa de inteligencia superior sobre el hardware del usuario. A diferencia de otros asistentes, CronOS procesa la voz, la lógica y la síntesis de forma local, utilizando modelos cuantizados para ofrecer una respuesta fluida en CPUs de consumo (Intel i5/i7).

## Arquitectura Modular
El sistema se divide en micro-módulos independientes para garantizar la escalabilidad y evitar bloqueos de hilos:

- **Cerebro.py:** Núcleo lógico que conecta con **Ollama (Qwen 2.5)**. Gestiona el procesamiento de herramientas mediante Regex y la memoria persistente de la sesión.
- **Oido.py:** Módulo STT (Speech-to-Text) que utiliza **Faster-Whisper** (modelo small/int8) para una transcripción local ultra-rápida.
- **Boca.py:** Módulo TTS (Text-to-Speech) que utiliza **Edge-TTS** para una síntesis de voz neuronal y fluida.
- **App.py:** Servidor backend robusto desplegado con **Waitress + Flask**, que gestiona la interfaz web y el streaming de datos concurrentes en tiempo real (SSE).
- **Estado.py:** Gestor global de estados y bus de eventos. Evita colisiones de hilos, protege contra pulsaciones dobles y permite interrupciones limpias en plena escucha.
- **Cara.py:** Interfaz de escritorio desarrollada con **CustomTkinter** para interacción directa fuera del navegador.

## Características Principales
- **Interfaz UI/UX Sci-Fi:** Panel de mandos web con terminal estilo hacker (colores neón por módulos: SYS, MIC, LLM) y un logo SVG animado con feedback interactivo táctil.
- **Telemetría en Vivo:** Diagnóstico de hardware (CPU, RAM, Disco) representado mediante gráficos *sparkline* en tiempo real.
- **Streaming de Texto (SSE):** Las respuestas se muestran de forma orgánica palabra por palabra, sin bloquear la interfaz.
- **Integración con Obsidian:** Capacidad para leer, escribir, listar y buscar dentro de carpetas de notas.
- **Visión Computacional:** Capacidad de analizar imágenes mediante el modelo local **Moondream**.
- **Búsqueda Web (RAG Ligero):** Integración con DuckDuckGo para obtener datos actualizados sin rastreo.
- **Seguridad Perimetral:** Filtro por IP para restringir el acceso solo a dispositivos autorizados en la red local.

## Requisitos del Sistema
- **SO:** Linux (Optimizado para Linux Mint) / Windows / macOS.
- **Python:** 3.10 o superior.
- **Hardware:** Mínimo 8GB RAM (Recomendado 16GB) y CPU con 4+ núcleos.
- **Modelos:** Ollama instalado con los modelos `qwen2.5:3b` y `moondream`.

---

## Instalación y Uso

Si quieres desplegar este núcleo en tu propia máquina, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/rafakazajo/CronOS.git](https://github.com/rafakazajo/CronOS.git)
   cd CronOS
   ```

2. **Instalar dependencias:**

    ```bash
    pip install -r Requisitos.txt
    ```

3. **Instalar Ollama y descargar el Cerebro:**

Asegúrate de tener Ollama instalado en tu sistema. Luego ejecuta:

    ```bash
    ollama run qwen2.5:3b
    ```

4. **Configurar el entorno:**

    Crea un archivo .env o edita la configuración inicial en el código para definir la ruta de tu DIRECTORIO_SEGURO (Bóveda de Obsidian).

5. **Despertar a CronOS:**

Ejecuta el servidor principal:

    ```bash
    python App.py    
    ```
Abre tu navegador (Chrome/Edge recomendado para el micrófono) y entra en http://localhost:5000 o usa la IP de tu PC para controlarlo desde tu móvil.

---

## Licencia y Derechos de Autor

Este proyecto se distribuye bajo la **Licencia MIT**, lo que permite su uso, modificación y distribución libre, siempre que se mantengan los créditos del autor original.

> [!IMPORTANT]
> **Excepción de Identidad Visual:** Los logotipos, el nombre "CronOS" y la identidad visual asociada contenidos en este repositorio son propiedad exclusiva de **rafakazajo**. El permiso otorgado por la licencia MIT **no incluye** el derecho a utilizar estos elementos gráficos para proyectos derivados, comerciales o marcas de terceros sin autorización expresa.