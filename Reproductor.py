import pygame
import tkinter as tk
from tkinter import filedialog, ttk
import os
from mutagen.mp3 import MP3
import pygame.mixer as mixer
import time
from Tooltip import Tooltip

class Reproductor():
    def __init__(self):
        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        self.reproduciendo = False
        self.ruta_archivo = None
        self.ruta_carpeta_seleccionada = None
        self.archivos_mp3 = []
        self.indice_actual = 0
        self.detenido = False
        self.inicio_reproducciendo = None

        self.ventana = tk.Tk()
        self.ventana.resizable(0,0)
        self.ventana.geometry("600x450")
        self.ventana.title("Reproductor de música")

        color_fondo = "#2E2255"
        self.ventana.configure(bg=color_fondo)

        marco_contenido = ttk.Frame(self.ventana)
        marco_contenido.pack(fill=tk.BOTH, expand=True)

        estilo = ttk.Style()
        estilo.theme_use('default')  
        estilo.configure('TFrame', background=color_fondo) 
        estilo.configure('TLabel', background=color_fondo, foreground='white')

        self.imagen_fondo = tk.PhotoImage(file="img.png")
        fondo_label = tk.Label(self.ventana, image=self.imagen_fondo)
        fondo_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.current_time_label = tk.Label(self.ventana, text="00:00")
        self.current_time_label.place(x=470, y=380, width=70, height=20)

        barra = ttk.Style()
        barra.theme_use('default')
        barra.configure('TProgressbar', backgroud='#2E2255', troughcolor='#2E2255', bordercolor='#2E2255', relief='float')
        barra.configure('TProgressbar::active', background='black', bordercolor='black')

        self.barra_progreso = ttk.Progressbar(self.ventana, orient='horizontal', mode='determinate', style='TProgressbar')
        self.barra_progreso.place(x=20, y=380, width=450, height=20)
        Tooltip(self.barra_progreso, "Barra de progreso")
        self.barra_progreso.bind("<Button-1>", lambda event: self.clic_posicion)

        self.btnReproducir = tk.Button(self.ventana, text="Reproducir", command=self.reproducir)
        self.btnReproducir.place(x=20, y=20, width=80, height=30)
        Tooltip(self.btnReproducir, "Presione para Reproducir la canción\nControl+R")
        self.btnReproducir.bind('<Control-r>', lambda event: self.reproducir)

        self.btnPausar = tk.Button(self.ventana, text="Pausar", command=self.pausar)
        self.btnPausar.place(x=130, y=20, width=80, height=30)
        Tooltip(self.btnPausar, "Presione para Pausar la canción\nControl+P")
        self.btnPausar.bind('<Control-p>', lambda event: self.pausar)

        self.btnReanudar = tk.Button(self.ventana, text="Reanudar", command=self.reanudar)
        self.btnReanudar.place(x=240, y=20, width=80, height=30)
        Tooltip(self.btnReanudar, "Presione para Reanudar la canción\nControl+U")
        self.btnReanudar.bind('<Control-u>', lambda event: self.reanudar)

        self.btndetener = tk.Button(self.ventana, text="Detener", command=self.detener)
        self.btndetener.place(x=350, y=20, width=80, height=30)
        Tooltip(self.btndetener, "Presione para Detener la canción\nControl+T")
        self.btndetener.bind('<Control-t>', lambda event: self.detener)

        self.btnanterior = tk.Button(self.ventana, text="Anterior", command=self.anterior)
        self.btnanterior.place(x=20, y=60, width=80, height=30)
        Tooltip(self.btnanterior, "Presione para la canción Anterior\nControl+A")
        self.btnanterior.bind('<Control-a>', lambda event: self.anterior)

        self.btnsiguiente = tk.Button(self.ventana, text="Siguiente", command=self.siguiente)
        self.btnsiguiente.place(x=350, y=60, width=80, height=30)
        Tooltip(self.btnsiguiente, "Presione para la canción Siguiente\nControl+S")
        self.btnsiguiente.bind('<Control-s>', lambda event: self.siguiente)

        self.lista_canciones = ttk.Treeview(self.ventana, columns=("Nombre", "Duración"), show="headings")
        self.lista_canciones.heading("Nombre", text="Nombre")
        self.lista_canciones.heading("Duración", text="Duración")
        self.lista_canciones.place(x=20, y=100, width=450, height=200)

        self.btncargar_canciones = tk.Button(self.ventana, text="Cargar canciones", command=self.seleccionar_carpeta)
        self.btncargar_canciones.place(x=20, y=310, width=150, height=30)
        Tooltip(self.btncargar_canciones, "Presione para la Cargar canciones desde su destino deseado")

        self.control_volumen = tk.Scale(self.ventana, from_=0, to=100, orient=tk.HORIZONTAL, command=self.event_handler)
        self.control_volumen.set(100)
        self.control_volumen.place(x=20, y=350, width=300, height=30)
        Tooltip(self.control_volumen,"gradue el volumen desde aqui")

        self.ventana.after(100, self.actualizar_posicion)

        self.ventana.bind('<<SongFinished>>', lambda e: self.song_finished())

    def reproducir(self):
            if self.archivos_mp3:
                self.ruta_archivo = self.archivos_mp3[self.indice_actual]
                mixer.music.load(self.ruta_archivo)
                mixer.music.play()
                self.lista_canciones.selection_set(self.indice_actual)
                self.lista_canciones.see(self.indice_actual)
                self.reproduciendo = True
                self.detenido = False
                self.inicio_reproducciendo = time.time()

    def pausar(self):
        if self.reproduciendo:
            mixer.music.pause()
            self.reproduciendo = False

    def reanudar(self):
        if not self.reproduciendo:
            mixer.music.unpause()
            self.reproduciendo = True

    def detener(self):
        if self.reproduciendo:
            mixer.music.stop()
            self.reproduciendo = False
            self.ruta_archivo = None
            self.detenido = True
            self.inicio_reproducciendo = 0

            self.ventana.after_cancel(self.actualizar_posicion)
            self.barra_progreso["value"] = 0
            self.current_time_label.config(text="00:00")
    
    def anterior(self):
        if self.archivos_mp3:
            self.indice_actual = (self.indice_actual - 1) % len(self.archivos_mp3)
            self.detenido = False
            self.reproducir()

    def siguiente(self):
        if self.archivos_mp3:
            self.indice_actual = (self.indice_actual + 1) % len(self.archivos_mp3)
            self.detenido = False
            self.reproducir()

    def cargar_canciones(self, ruta_carpeta):
        self.ruta_carpeta_seleccionada = ruta_carpeta
        self.archivos_mp3 = [os.path.join(ruta_carpeta, archivo) for archivo in os.listdir(ruta_carpeta) if archivo.endswith(".mp3")]

        if self.archivos_mp3:
            self.lista_canciones.delete(*self.lista_canciones.get_children())
            for index, archivo_mp3 in enumerate(self.archivos_mp3):
                nombre_cancion = os.path.splitext(os.path.basename(archivo_mp3))[0]
                duracion_cancion = self.obtener_duracion_cancion(archivo_mp3)
                self.lista_canciones.insert("", tk.END, iid=index, text=nombre_cancion, values=(nombre_cancion, duracion_cancion))

            audio = MP3(self.archivos_mp3[self.indice_actual])
            self.duracion_total = int(audio.info.length)
            self.barra_progreso.configure(maximum=self.duracion_total)

    def clic_posicion(self, event):
        if self.reproduciendo and self.duracion_total > 0:
            progreso = event.x / self.barra_progreso.winfo_width()
            nueva_posicion = progreso * self.duracion_total
            mixer.music.set_pos(int(nueva_posicion))
            self.actualizar_posicion()

    def obtener_duracion_cancion(self, ruta_archivo):
        audio = MP3(ruta_archivo)
        duracion_segundos = int(audio.info.length)
        minutos, segundos = divmod(duracion_segundos, 60)
        return f"{minutos}:{segundos:02d}"

    def format_time(self, milliseconds):
        seconds = milliseconds // 1000
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def actualizar_posicion(self):
        self.barra_progreso['value'] = 0

        if self.reproduciendo:
            tiempo_actual = time.time()
            tiempo_trascurrido = tiempo_actual - self.inicio_reproducciendo
            posicion_actual = mixer.music.get_pos() / 1000

            if self.duracion_total > 0:
                porcentaje_completado = (posicion_actual / self.duracion_total) * 100
                self.barra_progreso["value"] = porcentaje_completado
                current_time = self.format_time(tiempo_trascurrido * 1000)
                self.current_time_label.config(text=current_time)

        self.ventana.after(100, self.actualizar_posicion)

    def actualizar_volumen(self):
        volumen = float(self.control_volumen.get()) / 100
        mixer.music.set_volume(volumen)