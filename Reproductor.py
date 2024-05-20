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