# CronOS (v1.1)
**rafakazajo**

**CronOS** es un asistente virtual avanzado de código abierto diseñado para ejecutarse localmente. Esta versión 1.1 transforma la interacción básica en una experiencia inmersiva con gestión de archivos, seguridad perimetral y una interfaz visual reactiva de alto rendimiento.

---

## Novedades de la Versión 1.1

### Evolución de la Interfaz (UI/UX)
* **Diseño "Pastilla":** UI modernizada con bordes redondeados y botones circulares optimizados para pantallas táctiles (Samsung S24 Ultra) y escritorio.
* **Sistema de Carga Dinámica:** * **Thinking Wave:** Burbuja de carga con 6 barras verdes animadas en forma de ola.
    * **Work Loader:** Animación de puntos amarillos pulsantes exclusiva para procesos de gestión de archivos.
* **Ecualizador Aleatorio V2:** Visualizador de 10 barras con frecuencias aleatorias sincronizadas con la síntesis de voz.
* **Efecto Typewriter:** Renderizado de texto letra por letra para una sensación de computación orgánica.

### Lógica y Sinergia de Datos
* **Perfiles Especializados:** Selector de modo (**Normal, Estudio, Código**) que ajusta la temperatura y el sistema de instrucciones del modelo.
* **Sinergia de Archivos:** Capacidad para leer y crear documentos en el directorio seguro `~/CronOS_Archivos`.
* **Confirmación Verbal:** CronOS informa por voz tras completar con éxito operaciones de escritura.
* **Control Idiomático:** Refuerzo de instrucciones para garantizar respuestas estrictamente en español.

### Seguridad y Mantenimiento
* **Filtro por IP:** Acceso restringido mediante lista blanca, protegiendo el núcleo de accesos no autorizados en la red local.
* **Ciclo de Limpieza de 30 Días:** Mantenimiento automático del sistema de archivos para eliminar basura temporal de forma mensual.

---

## Especificaciones Técnicas

* **Cerebro:** Ollama - Modelo `qwen2.5` (Procesamiento local).
* **Backend:** Flask multihilo (Python 3.10+).
* **Voz:** Síntesis neuronal con `edge-tts` y salida de audio via `pygame`.
* **Frontend:** HTML5, CSS3 (Animaciones avanzadas) y JavaScript (Reconocimiento Web Speech API).
* **RAG Ligero:** Integración con DuckDuckGo Search para datos de actualidad.

---

## Estructura del Proyecto

* `App.py`: Núcleo del servidor, seguridad IP y mantenimiento de 30 días.
* `Cerebro.py`: Procesamiento de lenguaje, perfiles y gestión de archivos (Lectura/Escritura).
* `Boca.py`: Módulo de síntesis de voz neuronal.
* `templates/index.html`: Interfaz de usuario con lógica de animaciones y máquina de escribir.

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

## Licencia y Derechos de Autor

Este proyecto se distribuye bajo la **Licencia MIT**, lo que permite su uso, modificación y distribución libre, siempre que se mantengan los créditos del autor original.

> [!IMPORTANT]
> **Excepción de Identidad Visual:** Los logotipos, el nombre "CronOS" y la identidad visual asociada contenidos en este repositorio son propiedad exclusiva de **rafakazajo**. El permiso otorgado por la licencia MIT **no incluye** el derecho a utilizar estos elementos gráficos para proyectos derivados, comerciales o marcas de terceros sin autorización expresa.

---

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

## Licencia y Derechos de Autor

Este proyecto se distribuye bajo la **Licencia MIT**, lo que permite su uso, modificación y distribución libre, siempre que se mantengan los créditos del autor original.

> [!IMPORTANT]
> **Excepción de Identidad Visual:** Los logotipos, el nombre "CronOS" y la identidad visual asociada contenidos en este repositorio son propiedad exclusiva de **rafakazajo**. El permiso otorgado por la licencia MIT **no incluye** el derecho a utilizar estos elementos gráficos para proyectos derivados, comerciales o marcas de terceros sin autorización expresa.