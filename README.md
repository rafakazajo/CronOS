# CronOS
## Rafael Caro Amanbayev

Este es mi asistente virtual personal llamado CronOS con una IA en local, es un proyecto casero hecho por diversion y las ganas de investigar

---

## Como funciona

Este asistente tendra una personalidad y capacidad para interactuar con el ordenador para la gestion de archivos y tambien podra resolver dudas

## Piezas

Este poryecto lo quiero convertir en un asistente personal fisico para que interactue sin la necesidad de que el ordenador este encendido

* **Mini PC:** Voy a comprar un mini pc de segunda mano mas exactamente el *HP EliteDesk 800 G3* el cual viene con una i5-6600T y 16 GB de RAM

* **Microfono y altavoz:** Para que el asistente no se escuche a si mismo voy a usar el *Jabra speak 410* el cual sirve como los dos y asi tambien queda mas estetico

* **Monitor:** Le quiero poner un monitor a mi asistente para que el asistente me pueda enseñar cosas a traves de ella y la he cogido tactil para que pueda interactuar tambien y la que he escogido es la *Waveshare 7 inch* que es de 7 pulgadas para que tambien quede estetico el asistente

* **Camara:** Y por ultimo le agregare un modulo de camara para que tenga reconocimiento facial ya que se me hace curiosa la posibilidad y asi que la experiencia sea personalizada y la camara que he escogido es un modulo de camara generico de Amazon

* **Inteligencia artificial:** Para el asistente uso Ollama (Llama 3.2) ya que con el puedo hacer la IA en local

### Cronos Beta v0.1

De momento solo he importado la IA le he dado una personalidad y una forma de hablar con la IA pero por el teclado de momento es muy simple

---

## 🚀 Si quieres probarlo

Si quieres ejecutar este proyecto en tu ordenador, sigue estos pasos:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/rafakazajo/CronOS.git](https://github.com/rafakazajo/CronOS.git)
    cd CronOS
    ```

2.  **Instalar las dependencias:**
    ```bash
    pip install -r Requisitos.txt
    ```

3.  **Ejecutar a CronOS:**
    Asegúrate de tener [Ollama](https://ollama.com/) instalado y ejecutándose (`ollama serve`).
    ```bash
    python3 Cerebro.py
    ```