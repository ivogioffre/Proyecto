import customtkinter as ctk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import os
import shutil
import json_utils

# Carpeta donde se almacenarán las canciones copiadas
CARPETA_CANCIONES = "canciones_guardadas"


def agregar_musica(app):
    """
    Permite seleccionar archivos de audio, copiarlos a una carpeta local,
    leer sus metadatos y mostrarlos en la interfaz principal del reproductor.
    """
    rutas = filedialog.askopenfilenames(
        title="Seleccionar canciones",
        filetypes=[("Archivos de audio", "*.mp3")]
    )

    if not rutas:
        return

    # Crear la carpeta si no existe
    if not os.path.exists(CARPETA_CANCIONES):
        os.makedirs(CARPETA_CANCIONES)

    for ruta_original in rutas:
        try:
            nombre_archivo = os.path.basename(ruta_original)
            ruta_destino = os.path.join(CARPETA_CANCIONES, nombre_archivo)

            # Evitar duplicados en el JSON
            if any(c["ruta"] == ruta_destino for c in app.canciones):
                continue

            # Si el archivo no existe en la carpeta, copiarlo
            if not os.path.exists(ruta_destino):
                shutil.copy2(ruta_original, ruta_destino)

            # Título por defecto
            titulo = os.path.splitext(nombre_archivo)[0]
            artista = "Desconocido"

            # Obtener duración y metadatos
            audio = MP3(ruta_destino)
            duracion = int(audio.info.length)

            try:
                etiquetas = EasyID3(ruta_destino)
                titulo = etiquetas.get("title", [titulo])[0]
                artista = etiquetas.get("artist", ["Desconocido"])[0]
            except Exception:
                pass

            # Formatear duración
            minutos = duracion // 60
            segundos = duracion % 60
            tiempo = f"{minutos:02}:{segundos:02}"

            cancion = {
                "ruta": ruta_destino,
                "titulo": titulo,
                "artista": artista,
                "duracion": tiempo
            }

            # Agregar a la lista y guardar en JSON
            app.canciones.append(cancion)
            json_utils.guardar_canciones(app.canciones)

            # Mostrar en la interfaz
            mostrar_cancion(app, cancion)

        except Exception as e:
            print(f"Error al cargar {ruta_original}: {e}")


def mostrar_cancion(app, cancion):
    """
    Muestra una canción en la interfaz con estética neón.
    """
    frame = ctk.CTkFrame(
        app.scroll_canciones,
        fg_color="#220044",
        corner_radius=10
    )
    frame.pack(fill="x", pady=5, padx=5)

    # Título y artista
    info = ctk.CTkLabel(
        frame,
        text=f"🎵 {cancion['titulo']} - {cancion['artista']}",
        text_color="white",
        anchor="w"
    )
    info.pack(side="left", padx=10, pady=10, expand=True, fill="x")

    # Duración
    tiempo = ctk.CTkLabel(
        frame,
        text=cancion["duracion"],
        text_color="#00ffff"
    )
    tiempo.pack(side="left", padx=10)

    # Botón para agregar a playlist (visual por ahora)
    btn_add = ctk.CTkButton(
        frame,
        text="➕",
        width=40,
        fg_color="#ff00ff",
        hover_color="#ff66ff",
        text_color="black"
    )
    btn_add.pack(side="right", padx=10)