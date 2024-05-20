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