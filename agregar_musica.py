import customtkinter as ctk
from tkinter import filedialog
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import os
import json_utils


def agregar_musica(app):
    """
    Permite seleccionar archivos de audio, leer sus metadatos
    y mostrarlos en la interfaz principal del reproductor.
    """
    rutas = filedialog.askopenfilenames(
        title="Seleccionar canciones",
        filetypes=[("Archivos de audio", "*.mp3")]
    )

    # Si el usuario cancela la selección, no hacer nada
    if not rutas:
        return

    for ruta in rutas:
        try:
            # Evitar duplicados
            if any(c["ruta"] == ruta for c in app.canciones):
                continue

            # Título por defecto: nombre del archivo
            titulo = os.path.splitext(os.path.basename(ruta))[0]
            artista = "Desconocido"

            # Obtener duración del archivo
            audio = MP3(ruta)
            duracion = int(audio.info.length)

            # Intentar leer metadatos ID3
            try:
                etiquetas = EasyID3(ruta)
                titulo = etiquetas.get("title", [titulo])[0]
                artista = etiquetas.get("artist", ["Desconocido"])[0]
            except Exception:
                pass

            # Formatear duración en mm:ss
            minutos = duracion // 60
            segundos = duracion % 60
            tiempo = f"{minutos:02}:{segundos:02}"

            # Crear diccionario de la canción
            cancion = {
                "ruta": ruta,
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
            print(f"Error al cargar {ruta}: {e}")


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