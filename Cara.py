# Cara.py - Interfaz Avanzada con Animaciones y Bucle Continuo
import customtkinter as ctk
import threading
import math
import random
import time
import Cerebro
import Boca
import Oido

ctk.set_appearance_mode("dark")

class NucleoEnergia(ctk.CTkCanvas):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs, highlightthickness=0, bg="#1a1a1a")
        self.centro = (125, 125)
        self.radio_base = 45
        self.estado = "IDLE"
        self.frame = 0
        self.dibujar_frame()

    def dibujar_frame(self):
        self.delete("all")
        self.frame += 1

        if self.estado == "IDLE":
            pulso = math.sin(self.frame * 0.03) * 5
            radio = self.radio_base + pulso
            color = "#2ecc71"
            
            self.create_oval(self.centro[0] - radio - 10, self.centro[1] - radio - 10,
                            self.centro[0] + radio + 10, self.centro[1] + radio + 10, outline=color, width=1, dash=(2, 4))
            self.create_oval(self.centro[0] - radio, self.centro[1] - radio,
                            self.centro[0] + radio, self.centro[1] + radio, fill="#145a32", outline=color, width=2)
            self.create_text(self.centro[0], self.centro[1], text="⏻", fill="white", font=("Arial", 30))

        elif self.estado == "ESCUCHANDO":
            pulso = math.sin(self.frame * 0.15) * 8
            radio = self.radio_base + pulso
            color = "#f1c40f"
            
            onda_radio = (self.frame * 3) % 100
            if onda_radio > radio:
                self.create_oval(self.centro[0] - onda_radio, self.centro[1] - onda_radio,
                                self.centro[0] + onda_radio, self.centro[1] + onda_radio, outline=color, width=2)
            
            self.create_oval(self.centro[0] - radio, self.centro[1] - radio,
                            self.centro[0] + radio, self.centro[1] + radio, fill="#7d6608", outline=color, width=2)
            self.create_text(self.centro[0], self.centro[1], text="🎙️", fill="white", font=("Arial", 25))

        elif self.estado == "PENSANDO":
            radio = self.radio_base
            color = "#3498db"
            
            self.create_oval(self.centro[0] - radio, self.centro[1] - radio,
                            self.centro[0] + radio, self.centro[1] + radio, fill="#154360", outline=color, width=2)
            
            distancia_orbita = 65
            for i in range(3):
                angulo = (self.frame * 0.05) + (i * (2 * math.pi / 3))
                x = self.centro[0] + math.cos(angulo) * distancia_orbita
                y = self.centro[1] + math.sin(angulo) * distancia_orbita
                self.create_oval(x-5, y-5, x+5, y+5, fill=color)

            self.create_text(self.centro[0], self.centro[1], text="👤", fill="white", font=("Arial", 30))

        elif self.estado == "HABLANDO":
            radio = self.radio_base
            color = "#9b59b6"
            
            self.create_oval(self.centro[0] - radio, self.centro[1] - radio,
                            self.centro[0] + radio, self.centro[1] + radio, fill="#4a235a", outline=color, width=2)
            
            self.create_text(self.centro[0], self.centro[1] - 15, text="🔊", fill="white", font=("Arial", 20))
            
            num_barras = 5
            ancho_barra = 6
            espacio = 10
            inicio_x = self.centro[0] - ((num_barras * espacio) / 2) + 2
            
            for i in range(num_barras):
                altura = random.randint(5, 25) 
                x = inicio_x + (i * espacio)
                y_base = self.centro[1] + 25
                self.create_rectangle(x, y_base - altura, x + ancho_barra, y_base, fill="white")

        self.after(20, self.dibujar_frame)


class CronosApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CronOS AI - Core Visual Avanzado")
        self.geometry("450x750")
        self.configure(fg_color="#1a1a1a")
        
        self.sistema_activo = False

        self.canvas_container = ctk.CTkFrame(self, fg_color="transparent")
        self.canvas_container.pack(pady=20)
        
        self.nucleo = NucleoEnergia(self.canvas_container, width=250, height=250)
        self.nucleo.pack()

        self.label_estado = ctk.CTkLabel(self, text="MODO REPOSO", font=("Orbitron", 16, "bold"), text_color="#2ecc71")
        self.label_estado.pack()
        
        self.label_accion = ctk.CTkLabel(self, text="Esperando activación...", font=("Arial", 12), text_color="gray")
        self.label_accion.pack()

        self.chat_frame = ctk.CTkTextbox(self, width=400, height=280, state="disabled", fg_color="#2b2b2b")
        self.chat_frame.pack(pady=15, padx=20)

        self.btn_accion = ctk.CTkButton(
            self, text="🔌 ACTIVAR CRONOS", 
            command=self.toggle_sistema,
            height=50, corner_radius=25, font=("Arial", 16, "bold"),
            fg_color="#1f538d", hover_color="#14375e"
        )
        self.btn_accion.pack(pady=10)

    def log(self, mensaje):
        self.chat_frame.configure(state="normal")
        self.chat_frame.insert("end", mensaje + "\n\n")
        self.chat_frame.see("end")
        self.chat_frame.configure(state="disabled")

    def actualizar_ui(self, estado, texto_estado, accion_detalle=""):
        self.nucleo.estado = estado
        
        colores = {"IDLE": "#2ecc71", "ESCUCHANDO": "#f1c40f", "PENSANDO": "#3498db", "HABLANDO": "#9b59b6"}
        self.label_estado.configure(text=texto_estado, text_color=colores.get(estado, "white"))
        self.label_accion.configure(text=accion_detalle)

    def toggle_sistema(self):
        if self.sistema_activo:
            self.sistema_activo = False
            self.btn_accion.configure(text="🔌 ACTIVAR CRONOS", fg_color="#1f538d", hover_color="#14375e")
            self.actualizar_ui("IDLE", "MODO REPOSO", "Esperando activación manual.")
        else:
            self.sistema_activo = True
            self.btn_accion.configure(text="🛑 DETENER CRONOS", fg_color="#c0392b", hover_color="#922b21")
            threading.Thread(target=self.bucle_continuo, daemon=True).start()

    def bucle_continuo(self):
        """Este bucle se repite indefinidamente mientras el sistema esté activo."""
        self.log("Sistema: Secuencia de inicio automática activada.")
        
        while self.sistema_activo:
            self.actualizar_ui("ESCUCHANDO", "ESCUCHANDO...", "Ajustando micrófonos y esperando voz.")
            entrada = Oido.escuchar()
            
            if not self.sistema_activo: 
                break
                
            if not entrada:
                self.log("Sistema: Silencio detectado. Volviendo a reposo automático.")
                self.sistema_activo = False
                self.btn_accion.configure(text="🔌 ACTIVAR CRONOS", fg_color="#1f538d")
                self.actualizar_ui("IDLE", "MODO REPOSO", "Apagado por inactividad vocal.")
                break

            self.log(f"Tú: {entrada}")

            if "salir" in entrada.lower() or "apagar" in entrada.lower() or "duerme" in entrada.lower():
                self.actualizar_ui("PENSANDO", "APAGANDO...", "Desconectando enlaces.")
                Boca.hablar("Entendido. Desconectando sistemas de escucha. Nos vemos.")
                self.sistema_activo = False
                self.btn_accion.configure(text="🔌 ACTIVAR CRONOS", fg_color="#1f538d")
                self.actualizar_ui("IDLE", "MODO REPOSO", "Apagado por comando de voz.")
                break

            self.actualizar_ui("PENSANDO", "PROCESANDO...", "Enrutando respuesta por Ollama.")
            respuesta = Cerebro.pensar(entrada)
            self.log(f"CronOS: {respuesta}")

            if not self.sistema_activo: 
                break

            self.actualizar_ui("HABLANDO", "TRANSMITIENDO...", "Sintetizando voz neuronal.")
            Boca.hablar(respuesta)
            


if __name__ == "__main__":
    app = CronosApp()
    app.mainloop()