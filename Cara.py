import customtkinter as ctk
import threading
import math
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
            
        elif self.estado == "HABLANDO":
            ondas = 3 + int(math.sin(self.frame * 0.1) * 2)
            color = "#3498db"
            for i in range(ondas):
                r = self.radio_base + (self.frame % 20) + (i * 15)
                self.create_oval(self.centro[0] - r, self.centro[1] - r,
                                self.centro[0] + r, self.centro[1] + r, outline=color, width=2)
            self.create_oval(self.centro[0] - self.radio_base, self.centro[1] - self.radio_base,
                            self.centro[0] + self.radio_base, self.centro[1] + self.radio_base, fill="#1b4f72", outline=color, width=3)
                            
        elif self.estado == "PENSANDO":
            color = "#f1c40f"
            ang = self.frame * 0.1
            x = self.centro[0] + math.cos(ang) * 20
            y = self.centro[1] + math.sin(ang) * 20
            self.create_oval(self.centro[0] - self.radio_base, self.centro[1] - self.radio_base,
                            self.centro[0] + self.radio_base, self.centro[1] + self.radio_base, outline=color, width=2)
            self.create_oval(x - 10, y - 10, x + 10, y + 10, fill=color)

        self.after(30, self.dibujar_frame)

class InterfazCronOS(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Núcleo CronOS")
        self.geometry("400x550")
        self.configure(fg_color="#1a1a1a")
        
        self.sistema_activo = False

        self.nucleo = NucleoEnergia(self, width=250, height=250)
        self.nucleo.pack(pady=20)

        self.lbl_estado = ctk.CTkLabel(self, text="MODO REPOSO", font=("Courier", 18, "bold"), text_color="#2ecc71")
        self.lbl_estado.pack()

        self.lbl_sub = ctk.CTkLabel(self, text="Esperando orden de activación...", font=("Courier", 12), text_color="#7f8c8d")
        self.lbl_sub.pack(pady=5)

        self.txt_log = ctk.CTkTextbox(self, width=350, height=120, fg_color="#0f0f0f", text_color="#ffffff", font=("Courier", 11))
        self.txt_log.pack(pady=10)
        self.txt_log.insert("0.0", "--- SISTEMA LISTO ---\n")
        self.txt_log.configure(state="disabled")

        self.btn_accion = ctk.CTkButton(self, text="🔌 ACTIVAR CRONOS", font=("Courier", 14, "bold"), 
                                        fg_color="#1f538d", hover_color="#14375e", height=40, command=self.alternar_sistema)
        self.btn_accion.pack(pady=10)

    def log(self, texto):
        self.txt_log.configure(state="normal")
        self.txt_log.insert("end", texto + "\n")
        self.txt_log.see("end")
        self.txt_log.configure(state="disabled")

    def actualizar_ui(self, estado_nucleo, texto_principal, subtexto, color="#ffffff"):
        self.nucleo.estado = estado_nucleo
        self.lbl_estado.configure(text=texto_principal, text_color=color)
        self.lbl_sub.configure(text=subtexto)

    def alternar_sistema(self):
        if not self.sistema_activo:
            self.sistema_activo = True
            self.btn_accion.configure(text="DESCONECTAR NÚCLEO", fg_color="#c0392b", hover_color="#78281f")
            threading.Thread(target=self.bucle_continuo, daemon=True).start()
        else:
            self.sistema_activo = False
            self.btn_accion.configure(text="ACTIVAR CRONOS", fg_color="#1f538d", hover_color="#14375e")
            self.actualizar_ui("IDLE", "MODO REPOSO", "Conexión neuronal pausada.", "#2ecc71")
            self.log("Sistema apagado manualmente.")

    def bucle_continuo(self):
        self.log("Iniciando módulos...")
        Boca.hablar("Sistemas en línea. Te escucho.")
        
        while self.sistema_activo:
            self.actualizar_ui("IDLE", "ESCUCHANDO...", "Ajustando ruido de fondo.", "#3498db")
            
            entrada = Oido.escuchar_y_transcribir()
            
            if not self.sistema_activo: 
                break
                
            if not entrada:
                self.log("Sistema: Silencio detectado. Volviendo a reposo.")
                self.sistema_activo = False
                self.btn_accion.configure(text="ACTIVAR CRONOS", fg_color="#1f538d")
                self.actualizar_ui("IDLE", "MODO REPOSO", "Apagado por inactividad.")
                break

            self.log(f"Tú: {entrada}")

            if "salir" in entrada.lower() or "apagar" in entrada.lower():
                self.actualizar_ui("PENSANDO", "APAGANDO...", "Desconectando enlaces.")
                Boca.hablar("Entendido. Desconectando sistemas. Nos vemos.")
                self.sistema_activo = False
                self.btn_accion.configure(text="ACTIVAR CRONOS")
                self.actualizar_ui("IDLE", "MODO REPOSO", "Apagado por comando.")
                break

            self.actualizar_ui("PENSANDO", "PROCESANDO...", "Enrutando respuesta por Ollama.", "#f1c40f")
            respuesta = Cerebro.pensar(entrada)
            self.log(f"CronOS: {respuesta}")

            if not self.sistema_activo: 
                break

            self.actualizar_ui("HABLANDO", "TRANSMITIENDO...", "Sintetizando voz neuronal.", "#e74c3c")
            Boca.hablar(respuesta)

if __name__ == "__main__":
    app = InterfazCronOS()
    app.mainloop()