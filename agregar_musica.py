#agregar_musica.py
import customtkinter as ctk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import os
import shutil
import json_utils
import playlist

CARPETA_CANCIONES = "canciones_guardadas"


def agregar_musica(app):
    rutas = filedialog.askopenfilenames(
        title="Seleccionar canciones",
        filetypes=[("Archivos de audio", "*.mp3")]
    )
    if not rutas:
        return

    if not os.path.exists(CARPETA_CANCIONES):
        os.makedirs(CARPETA_CANCIONES)

    for ruta_original in rutas:
        try:
            nombre_archivo = os.path.basename(ruta_original)
            ruta_destino = os.path.join(CARPETA_CANCIONES, nombre_archivo)

            if any(c["ruta"] == ruta_destino for c in app.canciones):
                continue

            if not os.path.exists(ruta_destino):
                shutil.copy2(ruta_original, ruta_destino)

            titulo  = os.path.splitext(nombre_archivo)[0]
            artista = "Desconocido"
            album   = "Desconocido"
            año     = "Desconocido"
            genero  = "Desconocido"

            audio    = MP3(ruta_destino)
            duracion = int(audio.info.length)

            try:
                etiquetas = EasyID3(ruta_destino)
                titulo  = etiquetas.get("title",  [titulo])[0]
                artista = etiquetas.get("artist", ["Desconocido"])[0]
                album   = etiquetas.get("album",  ["Desconocido"])[0]
                año     = etiquetas.get("date",   ["Desconocido"])[0]
                genero  = etiquetas.get("genre",  ["Desconocido"])[0]
            except Exception:
                pass

            minutos = duracion // 60
            segundos = duracion % 60
            tiempo = f"{minutos:02}:{segundos:02}"

            cancion = {
                "ruta":     ruta_destino,
                "titulo":   titulo,
                "artista":  artista,
                "album":    album,
                "año":      año,
                "genero":   genero,
                "duracion": tiempo
            }

            app.canciones.append(cancion)
            json_utils.guardar_canciones(app.canciones)
            mostrar_cancion(app, cancion, len(app.canciones) - 1)

        except Exception as e:
            print(f"Error al cargar {ruta_original}: {e}")


def mostrar_cancion(app, cancion, index, mostrar_boton_agregar=True):
    frame = ctk.CTkFrame(
        app.scroll_canciones,
        fg_color="#220044",
        corner_radius=10,
        height=50
    )
    frame.pack(fill="x", pady=5, padx=10)
    frame.pack_propagate(False)

    frame.grid_columnconfigure(0, weight=4, uniform="col")
    frame.grid_columnconfigure(1, weight=3, uniform="col")
    frame.grid_columnconfigure(2, weight=3, uniform="col")
    frame.grid_columnconfigure(3, weight=2, uniform="col")
    frame.grid_columnconfigure(4, weight=2, uniform="col")
    frame.grid_columnconfigure(5, weight=1, uniform="col")
    frame.grid_columnconfigure(6, weight=0)

    datos = [
        f"🎵 {cancion.get('titulo', '')}",
        cancion.get("artista", ""),
        cancion.get("album", ""),
        cancion.get("año", ""),
        cancion.get("genero", ""),
        cancion.get("duracion", "")
    ]

    labels = []
    for i, texto in enumerate(datos):
        lbl = ctk.CTkLabel(
            frame,
            text=texto,
            text_color="#00ffff" if i == 5 else "white",
            anchor="w"
        )
        lbl.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
        labels.append(lbl)

    if mostrar_boton_agregar:
        btn_add = ctk.CTkButton(
            frame,
            text="+",
            width=40,
            fg_color="#ff00ff",
            hover_color="#ff66ff",
            text_color="black",
            command=lambda: playlist.agregar_a_playlist(app, cancion)
        )
        btn_add.grid(row=0, column=6, padx=10)

    # Registrar fila en el reproductor para highlight
    app.player.registrar_fila(cancion["ruta"], frame, labels)

    def reproducir_con_click(event=None):
        app.player.reproducir_indice(index)

    # Bind solo en frame y labels — nunca en el botón "+"
    frame.bind("<Button-1>", reproducir_con_click)
    for lbl in labels:
        lbl.bind("<Button-1>", reproducir_con_click)