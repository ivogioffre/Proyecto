import os
import time
import random

import customtkinter as ctk
import pygame
from PIL import Image
from mutagen.mp3 import MP3


class ReproductorAudio:
    def __init__(self, app):
        self.app = app
        pygame.mixer.init()

        self.indice_actual = None
        self.cola_actual = None

        self.reproduciendo = False
        self.pausado = False

        self.shuffle = False
        self.repeat = False

        self.duracion = 0.0
        self.tiempo_acumulado = 0.0
        self.inicio_reanudado = None

        self.actualizando_slider = False

        self.barra = None
        self.lbl_titulo = None
        self.lbl_artista = None
        self.lbl_tiempo = None
        self.slider_progreso = None
        self.slider_volumen = None
        self.btn_play_pausa = None

        self.img_play = self._cargar_imagen("imagenes/boton_play.png", (42, 42))
        self.img_pausa = self._cargar_imagen("imagenes/boton_pausa.png", (42, 42))
        self.img_siguiente = self._cargar_imagen("imagenes/boton_siguiente.png", (38, 38))
        self.img_anterior = self._cargar_imagen("imagenes/boton_anterior.png", (38, 38))
        self.img_shuffle = self._cargar_imagen("imagenes/aleatorio.png", (34, 34))
        self.img_repeat = self._cargar_imagen("imagenes/repetir.png", (34, 34))

    def _cargar_imagen(self, ruta, size):
        try:
            if os.path.exists(ruta):
                img = Image.open(ruta)
                return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except Exception as e:
            print(f"No se pudo cargar {ruta}: {e}")
        return None

    def crear_barra_reproductor(self):
        self.barra = ctk.CTkFrame(self.app.root, height=120, fg_color="#0d0d0d")
        self.barra.pack(side="bottom", fill="x")
        self.barra.pack_propagate(False)

        self.barra.grid_columnconfigure(0, weight=3)
        self.barra.grid_columnconfigure(1, weight=5)
        self.barra.grid_columnconfigure(2, weight=2)

        frame_info = ctk.CTkFrame(self.barra, fg_color="transparent")
        frame_info.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)

        self.lbl_titulo = ctk.CTkLabel(
            frame_info,
            text="Ninguna canción reproduciéndose",
            text_color="#ffffff",
            anchor="w",
            font=("Arial", 16, "bold")
        )
        self.lbl_titulo.pack(anchor="w")

        self.lbl_artista = ctk.CTkLabel(
            frame_info,
            text="",
            text_color="#00ffff",
            anchor="w",
            font=("Arial", 13)
        )
        self.lbl_artista.pack(anchor="w", pady=(5, 0))

        frame_centro = ctk.CTkFrame(self.barra, fg_color="transparent")
        frame_centro.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        frame_botones = ctk.CTkFrame(frame_centro, fg_color="transparent")
        frame_botones.pack(pady=(5, 8))

        self.btn_shuffle = ctk.CTkButton(
            frame_botones,
            text="" if self.img_shuffle else "🔀",
            image=self.img_shuffle,
            width=48,
            height=48,
            fg_color="#1a0033",
            hover_color="#ff00ff",
            command=self.toggle_shuffle
        )
        self.btn_shuffle.pack(side="left", padx=8)

        self.btn_anterior = ctk.CTkButton(
            frame_botones,
            text="" if self.img_anterior else "⏮",
            image=self.img_anterior,
            width=56,
            height=56,
            fg_color="#1a0033",
            hover_color="#ff00ff",
            command=self.anterior
        )
        self.btn_anterior.pack(side="left", padx=8)

        self.btn_play_pausa = ctk.CTkButton(
            frame_botones,
            text="" if self.img_play else "▶",
            image=self.img_play,
            width=60,
            height=60,
            fg_color="#ff00ff",
            hover_color="#ff66ff",
            text_color="black",
            command=self.toggle_play_pausa
        )
        self.btn_play_pausa.pack(side="left", padx=8)

        self.btn_siguiente = ctk.CTkButton(
            frame_botones,
            text="" if self.img_siguiente else "⏭",
            image=self.img_siguiente,
            width=56,
            height=56,
            fg_color="#1a0033",
            hover_color="#ff00ff",
            command=self.siguiente
        )
        self.btn_siguiente.pack(side="left", padx=8)

        self.btn_repeat = ctk.CTkButton(
            frame_botones,
            text="" if self.img_repeat else "🔁",
            image=self.img_repeat,
            width=48,
            height=48,
            fg_color="#1a0033",
            hover_color="#ff00ff",
            command=self.toggle_repeat
        )
        self.btn_repeat.pack(side="left", padx=8)

        self.slider_progreso = ctk.CTkSlider(
            frame_centro,
            from_=0,
            to=100,
            height=18,
            progress_color="#ff00ff",
            button_color="#00ffff",
            button_hover_color="#ff66ff",
            command=self._al_mover_progreso
        )
        self.slider_progreso.pack(fill="x", padx=15, pady=(8, 2))

        self.lbl_tiempo = ctk.CTkLabel(
            frame_centro,
            text="00:00 / 00:00",
            text_color="#ffffff",
            font=("Arial", 12)
        )
        self.lbl_tiempo.pack(pady=(2, 0))

        frame_volumen = ctk.CTkFrame(self.barra, fg_color="transparent")
        frame_volumen.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)

        lbl_vol = ctk.CTkLabel(
            frame_volumen,
            text="Volumen",
            text_color="#ffffff",
            font=("Arial", 13, "bold")
        )
        lbl_vol.pack(anchor="e")

        self.slider_volumen = ctk.CTkSlider(
            frame_volumen,
            from_=0,
            to=1,
            number_of_steps=100,
            height=18,
            progress_color="#00ffff",
            button_color="#ff00ff",
            button_hover_color="#ff66ff",
            command=self.set_volumen
        )
        self.slider_volumen.set(0.5)
        self.slider_volumen.pack(anchor="e", fill="x", pady=(10, 0))

        self.set_volumen(0.5)
        self._actualizar_botones_modos()
        self.app.root.after(200, self._actualizar_estado)

    def _formato_tiempo(self, segundos):
        segundos = max(0, int(segundos))
        minutos = segundos // 60
        segundos = segundos % 60
        return f"{minutos:02}:{segundos:02}"

    def _buscar_cancion_por_ruta(self, ruta):
        return next((c for c in self.app.canciones if c["ruta"] == ruta), None)

    def _canciones_fuente(self):
        if self.cola_actual is not None:
            return self.cola_actual
        return [c["ruta"] for c in self.app.canciones]

    def _cancion_actual(self):
        if self.indice_actual is None:
            return None

        fuente = self._canciones_fuente()
        if 0 <= self.indice_actual < len(fuente):
            ruta = fuente[self.indice_actual]
            return self._buscar_cancion_por_ruta(ruta)
        return None

    def _duracion_cancion(self, ruta):
        try:
            audio = MP3(ruta)
            return float(audio.info.length)
        except Exception:
            return 0.0

    def _posicion_actual(self):
        if self.indice_actual is None:
            return 0.0

        if self.pausado or self.inicio_reanudado is None:
            return self.tiempo_acumulado

        return self.tiempo_acumulado + (time.monotonic() - self.inicio_reanudado)

    def _actualizar_info_ui(self):
        cancion = self._cancion_actual()
        if cancion is None:
            self.lbl_titulo.configure(text="Ninguna canción reproduciéndose")
            self.lbl_artista.configure(text="")
            self.lbl_tiempo.configure(text="00:00 / 00:00")
            self.slider_progreso.set(0)
            return

        self.lbl_titulo.configure(text=cancion.get("titulo", "Sin título"))
        self.lbl_artista.configure(text=cancion.get("artista", "Desconocido"))

    def _actualizar_icono_play(self):
        if self.pausado:
            if self.img_play:
                self.btn_play_pausa.configure(image=self.img_play, text="")
            else:
                self.btn_play_pausa.configure(image=None, text="▶")
        else:
            if self.img_pausa:
                self.btn_play_pausa.configure(image=self.img_pausa, text="")
            else:
                self.btn_play_pausa.configure(image=None, text="⏸")

    def _actualizar_botones_modos(self):
        if self.shuffle:
            self.btn_shuffle.configure(fg_color="#ff00ff")
        else:
            self.btn_shuffle.configure(fg_color="#1a0033")

        if self.repeat:
            self.btn_repeat.configure(fg_color="#ff00ff")
        else:
            self.btn_repeat.configure(fg_color="#1a0033")

    def _indice_aleatorio_diferente(self):
        fuente = self._canciones_fuente()
        if not fuente:
            return None

        if len(fuente) == 1:
            return 0

        if self.indice_actual is None:
            return random.randint(0, len(fuente) - 1)

        opciones = list(range(len(fuente)))
        if self.indice_actual in opciones:
            opciones.remove(self.indice_actual)

        if not opciones:
            return self.indice_actual

        return random.choice(opciones)

    def reproducir_indice(self, indice, lista=None):
        if not self.app.canciones:
            return

        fuente = list(lista) if lista is not None else [c["ruta"] for c in self.app.canciones]
        if indice < 0 or indice >= len(fuente):
            return

        self.cola_actual = fuente if lista is not None else None
        self.indice_actual = indice

        ruta = fuente[indice]

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.play()

            self.reproduciendo = True
            self.pausado = False
            self.duracion = self._duracion_cancion(ruta)
            self.tiempo_acumulado = 0.0
            self.inicio_reanudado = time.monotonic()

            self._actualizar_info_ui()
            self._actualizar_icono_play()
            self._actualizar_slider_y_tiempo()

        except Exception as e:
            print(f"Error al reproducir {ruta}: {e}")

    def reproducir_playlist(self, rutas):
        if not rutas:
            return
        self.reproducir_indice(0, lista=rutas)

    def toggle_play_pausa(self):
        if not self.app.canciones:
            return

        if self.indice_actual is None:
            self.reproducir_indice(0)
            return

        if not self.reproduciendo:
            self.reproducir_indice(self.indice_actual, self.cola_actual)
            return

        if self.pausado:
            pygame.mixer.music.unpause()
            self.pausado = False
            self.inicio_reanudado = time.monotonic()
        else:
            self.tiempo_acumulado = self._posicion_actual()
            pygame.mixer.music.pause()
            self.pausado = True

        self._actualizar_icono_play()

    def siguiente(self):
        fuente = self._canciones_fuente()
        if not fuente:
            return

        if self.indice_actual is None:
            self.reproducir_indice(0, self.cola_actual)
            return

        if self.shuffle:
            nuevo = self._indice_aleatorio_diferente()
        else:
            nuevo = (self.indice_actual + 1) % len(fuente)

        if nuevo is None:
            return

        self.reproducir_indice(nuevo, self.cola_actual)

    def anterior(self):
        fuente = self._canciones_fuente()
        if not fuente:
            return

        if self.indice_actual is None:
            self.reproducir_indice(0, self.cola_actual)
            return

        if self.shuffle:
            nuevo = self._indice_aleatorio_diferente()
        else:
            nuevo = (self.indice_actual - 1) % len(fuente)

        if nuevo is None:
            return

        self.reproducir_indice(nuevo, self.cola_actual)

    def toggle_shuffle(self):
        self.shuffle = not self.shuffle
        self._actualizar_botones_modos()

    def toggle_repeat(self):
        self.repeat = not self.repeat
        self._actualizar_botones_modos()

    def set_volumen(self, valor):
        try:
            pygame.mixer.music.set_volume(float(valor))
        except Exception:
            pass

    def _al_mover_progreso(self, valor):
        if self.indice_actual is None or self.duracion <= 0:
            return

        if self.actualizando_slider:
            return

        nuevo_segundo = (float(valor) / 100) * self.duracion
        self.tiempo_acumulado = nuevo_segundo
        self.inicio_reanudado = time.monotonic()

        fuente = self._canciones_fuente()
        if not fuente or self.indice_actual >= len(fuente):
            return

        ruta = fuente[self.indice_actual]

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(ruta)

            if self.pausado:
                pygame.mixer.music.play(start=float(nuevo_segundo))
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.play(start=float(nuevo_segundo))

        except Exception as e:
            print(f"Error al mover progreso: {e}")

        self._actualizar_slider_y_tiempo()

    def _actualizar_slider_y_tiempo(self):
        if self.indice_actual is None or self.duracion <= 0:
            return

        posicion = self._posicion_actual()
        porcentaje = (posicion / self.duracion) * 100 if self.duracion > 0 else 0
        if porcentaje < 0:
            porcentaje = 0
        if porcentaje > 100:
            porcentaje = 100

        self.actualizando_slider = True
        self.slider_progreso.set(porcentaje)
        self.actualizando_slider = False

        self.lbl_tiempo.configure(
            text=f"{self._formato_tiempo(posicion)} / {self._formato_tiempo(self.duracion)}"
        )

    def _termino_cancion(self):
        if self.repeat:
            self.reproducir_indice(self.indice_actual, self.cola_actual)
        else:
            self.siguiente()

    def _actualizar_estado(self):
        try:
            if self.indice_actual is not None and self.reproduciendo and not self.pausado:
                if not pygame.mixer.music.get_busy():
                    self._termino_cancion()
                    self.app.root.after(200, self._actualizar_estado)
                    return

            if self.indice_actual is not None:
                self._actualizar_slider_y_tiempo()

        except Exception as e:
            print(f"Error actualizando reproductor: {e}")

        self.app.root.after(200, self._actualizar_estado)