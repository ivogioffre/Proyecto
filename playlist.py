import customtkinter as ctk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image
import os
import json
import shutil

import agregar_musica

ARCHIVO_PLAYLISTS = "playlist.json"
CARPETA_PORTADAS = "playlists"


def cargar_playlists():
    if os.path.exists(ARCHIVO_PLAYLISTS):
        try:
            with open(ARCHIVO_PLAYLISTS, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return {}
    return {}


def guardar_playlists(playlists):
    with open(ARCHIVO_PLAYLISTS, "w", encoding="utf-8") as archivo:
        json.dump(playlists, archivo, indent=4, ensure_ascii=False)


def limpiar_scroll(app):
    for widget in app.scroll_canciones.winfo_children():
        widget.destroy()


def formato_tiempo(segundos):
    segundos = int(segundos)
    minutos = segundos // 60
    seg = segundos % 60
    return f"{minutos}:{seg:02}"


def duracion_total_playlist(app, lista_rutas):
    total = 0
    for ruta in lista_rutas:
        cancion = next((c for c in app.canciones if c["ruta"] == ruta), None)
        if cancion:
            try:
                partes = cancion.get("duracion", "0:00").split(":")
                total += int(partes[0]) * 60 + int(partes[1])
            except Exception:
                pass
    return total


def _guardar_portada(nombre_playlist, ruta_imagen):
    if not ruta_imagen:
        return ""

    if not os.path.exists(CARPETA_PORTADAS):
        os.makedirs(CARPETA_PORTADAS)

    extension = os.path.splitext(ruta_imagen)[1]
    destino = os.path.join(CARPETA_PORTADAS, f"{nombre_playlist}{extension}")
    shutil.copy2(ruta_imagen, destino)
    return destino


def _elegir_portada(nombre_playlist):
    ruta = filedialog.askopenfilename(
        title="Elegir portada",
        filetypes=[("Imágenes", "*.png *.jpg *.jpeg")]
    )
    if not ruta:
        return ""
    return _guardar_portada(nombre_playlist, ruta)


def _actualizar_cola_reproductor(app, old_rutas, new_rutas, indice_afectado=None):
    if not hasattr(app, "player"):
        return

    player = app.player

    if player.cola_actual != old_rutas:
        return

    player.cola_actual = list(new_rutas)

    if not new_rutas:
        player.indice_actual = None
        player.tiempo_acumulado = 0.0
        player.duracion = 0.0
        return

    if player.indice_actual is None:
        return

    if indice_afectado is not None and player.indice_actual >= indice_afectado:
        player.indice_actual -= 1

    if player.indice_actual < 0:
        player.indice_actual = -1


def mostrar_biblioteca(app):
    limpiar_scroll(app)

    playlists = cargar_playlists()

    titulo = ctk.CTkLabel(
        app.scroll_canciones,
        text="Biblioteca",
        text_color="#00ffff",
        font=("Arial", 28, "bold")
    )
    titulo.pack(anchor="w", padx=20, pady=(10, 5))

    btn_crear = ctk.CTkButton(
        app.scroll_canciones,
        text="+ Crear playlist",
        fg_color="#ff00ff",
        hover_color="#ff66ff",
        text_color="black",
        height=45,
        command=lambda: crear_playlist(app)
    )
    btn_crear.pack(fill="x", padx=20, pady=(0, 15))

    if not playlists:
        vacio = ctk.CTkLabel(
            app.scroll_canciones,
            text="No hay playlists creadas todavía.",
            text_color="white",
            font=("Arial", 16)
        )
        vacio.pack(pady=30)
        return

    for nombre, datos in playlists.items():
        canciones = datos.get("canciones", [])
        portada = datos.get("portada", "")
        total = formato_tiempo(duracion_total_playlist(app, canciones))

        card = ctk.CTkFrame(
            app.scroll_canciones,
            fg_color="#220044",
            corner_radius=16,
            height=140
        )
        card.pack(fill="x", padx=20, pady=10)
        card.pack_propagate(False)

        cont = ctk.CTkFrame(card, fg_color="transparent")
        cont.pack(fill="both", expand=True, padx=12, pady=12)

        if portada and os.path.exists(portada):
            try:
                img = ctk.CTkImage(
                    light_image=Image.open(portada),
                    dark_image=Image.open(portada),
                    size=(110, 110)
                )
                if hasattr(app, "imagenes"):
                    app.imagenes.append(img)
                lbl_img = ctk.CTkLabel(cont, image=img, text="")
                lbl_img.bind("<Button-1>", lambda e, n=nombre: cambiar_portada(app, n))
            except Exception:
                lbl_img = ctk.CTkButton(
                    cont,
                    text="+",
                    width=110,
                    height=110,
                    fg_color="#1a0033",
                    hover_color="#ff00ff",
                    command=lambda n=nombre: cambiar_portada(app, n)
                )
        else:
            lbl_img = ctk.CTkButton(
                cont,
                text="+",
                width=110,
                height=110,
                fg_color="#1a0033",
                hover_color="#ff00ff",
                command=lambda n=nombre: cambiar_portada(app, n)
            )

        lbl_img.pack(side="left")

        centro = ctk.CTkFrame(cont, fg_color="transparent")
        centro.pack(side="left", fill="both", expand=True, padx=18)

        lbl_nombre = ctk.CTkLabel(
            centro,
            text=nombre,
            text_color="white",
            font=("Arial", 28, "bold"),
            anchor="w"
        )
        lbl_nombre.pack(anchor="w")

        lbl_info = ctk.CTkLabel(
            centro,
            text=f"{len(canciones)} canciones",
            text_color="#00ffff",
            font=("Arial", 14),
            anchor="w"
        )
        lbl_info.pack(anchor="w", pady=(6, 0))

        derecha = ctk.CTkFrame(cont, fg_color="transparent")
        derecha.pack(side="right", fill="y")

        lbl_duracion = ctk.CTkLabel(
            derecha,
            text=total,
            text_color="white",
            font=("Arial", 18, "bold")
        )
        lbl_duracion.pack(side="right", padx=10)

        btn_eliminar = ctk.CTkButton(
            derecha,
            text="✕",
            width=38,
            height=38,
            fg_color="#ff0055",
            hover_color="#ff3366",
            command=lambda n=nombre: eliminar_playlist(app, n)
        )
        btn_eliminar.pack(side="right", padx=(0, 10))

        btn_play = ctk.CTkButton(
            derecha,
            text="▶",
            width=38,
            height=38,
            fg_color="#ff00ff",
            hover_color="#ff66ff",
            text_color="black",
            command=lambda n=nombre: reproducir_playlist_desde_biblioteca(app, n)
        )
        btn_play.pack(side="right", padx=(0, 10))

        card.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))
        cont.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))
        lbl_nombre.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))
        lbl_info.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))
        lbl_duracion.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))
        centro.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))
        derecha.bind("<Button-1>", lambda e, n=nombre: abrir_playlist(app, n))


def crear_playlist(app, cancion=None):
    nombre = simpledialog.askstring("Nueva playlist", "Nombre de la playlist:")
    if not nombre:
        return

    playlists = cargar_playlists()
    if nombre in playlists:
        messagebox.showerror("Error", "Ya existe una playlist con ese nombre.")
        return

    portada_destino = _elegir_portada(nombre)

    playlists[nombre] = {
        "portada": portada_destino,
        "canciones": []
    }

    if cancion is not None:
        playlists[nombre]["canciones"].append(cancion["ruta"])

    guardar_playlists(playlists)
    mostrar_biblioteca(app)


def cambiar_portada(app, nombre_playlist):
    playlists = cargar_playlists()
    if nombre_playlist not in playlists:
        return

    portada_destino = _elegir_portada(nombre_playlist)
    if not portada_destino:
        return

    playlists[nombre_playlist]["portada"] = portada_destino
    guardar_playlists(playlists)
    mostrar_biblioteca(app)


def eliminar_playlist(app, nombre):
    if not messagebox.askyesno("Confirmar", f"¿Eliminar la playlist '{nombre}'?"):
        return

    playlists = cargar_playlists()
    if nombre not in playlists:
        return

    portada = playlists[nombre].get("portada", "")
    if portada and os.path.exists(portada):
        try:
            os.remove(portada)
        except Exception:
            pass

    playlists.pop(nombre, None)
    guardar_playlists(playlists)
    mostrar_biblioteca(app)


def abrir_playlist(app, nombre):
    limpiar_scroll(app)

    playlists = cargar_playlists()
    datos = playlists.get(nombre)
    if not datos:
        return

    portada = datos.get("portada", "")
    rutas = datos.get("canciones", [])

    header = ctk.CTkFrame(app.scroll_canciones, fg_color="#1a0033", corner_radius=18)
    header.pack(fill="x", padx=20, pady=20)

    cont = ctk.CTkFrame(header, fg_color="transparent")
    cont.pack(fill="x", padx=18, pady=18)

    if portada and os.path.exists(portada):
        try:
            img = ctk.CTkImage(
                light_image=Image.open(portada),
                dark_image=Image.open(portada),
                size=(180, 180)
            )
            if hasattr(app, "imagenes"):
                app.imagenes.append(img)
            lbl_img = ctk.CTkLabel(cont, image=img, text="")
            lbl_img.bind("<Button-1>", lambda e, n=nombre: cambiar_portada(app, n))
        except Exception:
            lbl_img = ctk.CTkButton(
                cont,
                text="+",
                width=180,
                height=180,
                fg_color="#1a0033",
                hover_color="#ff00ff",
                command=lambda n=nombre: cambiar_portada(app, n)
            )
    else:
        lbl_img = ctk.CTkButton(
            cont,
            text="+",
            width=180,
            height=180,
            fg_color="#1a0033",
            hover_color="#ff00ff",
            command=lambda n=nombre: cambiar_portada(app, n)
        )

    lbl_img.pack(side="left")

    info = ctk.CTkFrame(cont, fg_color="transparent")
    info.pack(side="left", fill="both", expand=True, padx=18)

    lbl_nombre = ctk.CTkLabel(
        info,
        text=nombre,
        text_color="white",
        font=("Arial", 42, "bold"),
        anchor="w"
    )
    lbl_nombre.pack(anchor="w")

    total = formato_tiempo(duracion_total_playlist(app, rutas))
    lbl_detalle = ctk.CTkLabel(
        info,
        text=f"{len(rutas)} canciones · {total}",
        text_color="#00ffff",
        font=("Arial", 16),
        anchor="w"
    )
    lbl_detalle.pack(anchor="w", pady=(10, 0))

    botones = ctk.CTkFrame(info, fg_color="transparent")
    botones.pack(anchor="w", pady=(22, 0))

    btn_play = ctk.CTkButton(
        botones,
        text="",
        image=app.player.img_play if getattr(app.player, "img_play", None) else None,
        width=58,
        height=58,
        fg_color="#ff00ff",
        hover_color="#ff66ff",
        text_color="black",
        command=lambda: app.player.reproducir_playlist(rutas)
    )
    if not getattr(app.player, "img_play", None):
        btn_play.configure(text="▶")
    btn_play.pack(side="left", padx=(0, 10))

    btn_agregar = ctk.CTkButton(
        botones,
        text="+ Agregar canciones",
        fg_color="#1a0033",
        hover_color="#ff00ff",
        command=lambda: agregar_canciones_a_playlist(app, nombre)
    )
    btn_agregar.pack(side="left")

    btn_eliminar_playlist = ctk.CTkButton(
        botones,
        text="✕ Eliminar playlist",
        fg_color="#ff0055",
        hover_color="#ff3366",
        command=lambda: eliminar_playlist(app, nombre)
    )
    btn_eliminar_playlist.pack(side="left", padx=(10, 0))

    lbl_songs = ctk.CTkLabel(
        app.scroll_canciones,
        text="Canciones",
        text_color="white",
        font=("Arial", 22, "bold")
    )
    lbl_songs.pack(anchor="w", padx=20, pady=(0, 10))

    if not rutas:
        vacio = ctk.CTkLabel(
            app.scroll_canciones,
            text="Esta playlist todavía no tiene canciones.",
            text_color="white",
            font=("Arial", 15)
        )
        vacio.pack(pady=20)
        return

    for ruta in rutas:
        cancion = next((c for c in app.canciones if c["ruta"] == ruta), None)
        if cancion:
            mostrar_cancion_en_playlist(app, nombre, cancion)


def mostrar_cancion_en_playlist(app, nombre_playlist, cancion):
    frame = ctk.CTkFrame(
        app.scroll_canciones,
        fg_color="#220044",
        corner_radius=10
    )
    frame.pack(fill="x", pady=5, padx=20)

    info = ctk.CTkLabel(
        frame,
        text=f"🎵 {cancion['titulo']} - {cancion['artista']}",
        text_color="white",
        anchor="w"
    )
    info.pack(side="left", padx=10, pady=10, expand=True, fill="x")

    tiempo = ctk.CTkLabel(
        frame,
        text=cancion["duracion"],
        text_color="#00ffff"
    )
    tiempo.pack(side="left", padx=10)

    btn_eliminar = ctk.CTkButton(
        frame,
        text="✕",
        width=40,
        fg_color="#ff0055",
        hover_color="#ff3366",
        command=lambda r=cancion["ruta"]: eliminar_cancion_de_playlist(app, nombre_playlist, r)
    )
    btn_eliminar.pack(side="right", padx=10)

    def reproducir_con_click(event=None):
        rutas = cargar_playlists().get(nombre_playlist, {}).get("canciones", [])
        try:
            indice = rutas.index(cancion["ruta"])
        except ValueError:
            indice = 0
        app.player.reproducir_indice(indice, lista=rutas)

    frame.bind("<Button-1>", reproducir_con_click)
    info.bind("<Button-1>", reproducir_con_click)
    tiempo.bind("<Button-1>", reproducir_con_click)


def eliminar_cancion_de_playlist(app, nombre_playlist, ruta):
    playlists = cargar_playlists()
    if nombre_playlist not in playlists:
        return

    old_rutas = list(playlists[nombre_playlist]["canciones"])
    if ruta in playlists[nombre_playlist]["canciones"]:
        indice_eliminado = playlists[nombre_playlist]["canciones"].index(ruta)
        playlists[nombre_playlist]["canciones"].remove(ruta)
        guardar_playlists(playlists)

        new_rutas = list(playlists[nombre_playlist]["canciones"])
        _actualizar_cola_reproductor(app, old_rutas, new_rutas, indice_afectado=indice_eliminado)

    abrir_playlist(app, nombre_playlist)


def agregar_canciones_a_playlist(app, nombre_playlist):
    ventana = ctk.CTkToplevel(app.root)
    ventana.title("Agregar canciones")
    ventana.geometry("650x520")
    ventana.grab_set()

    titulo = ctk.CTkLabel(
        ventana,
        text=f"Agregar canciones a '{nombre_playlist}'",
        text_color="#00ffff",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=12)

    frame_scroll = ctk.CTkScrollableFrame(ventana, fg_color="#140028")
    frame_scroll.pack(fill="both", expand=True, padx=12, pady=12)

    playlists = cargar_playlists()

    for cancion in app.canciones:
        fila = ctk.CTkFrame(frame_scroll, fg_color="#220044", corner_radius=12)
        fila.pack(fill="x", pady=6)

        lbl = ctk.CTkLabel(
            fila,
            text=f"{cancion['titulo']} - {cancion['artista']}",
            text_color="white",
            anchor="w"
        )
        lbl.pack(side="left", padx=12, pady=10, expand=True, fill="x")

        ya_esta = cancion["ruta"] in playlists[nombre_playlist]["canciones"]

        btn = ctk.CTkButton(
            fila,
            text="Agregada" if ya_esta else "+",
            width=80,
            fg_color="#ff00ff" if not ya_esta else "#444444",
            hover_color="#ff66ff",
            state="disabled" if ya_esta else "normal",
            command=lambda r=cancion["ruta"]: _agregar_ruta_a_playlist(app, nombre_playlist, r, ventana)
        )
        btn.pack(side="right", padx=12, pady=8)

    btn_cerrar = ctk.CTkButton(
        ventana,
        text="Cerrar",
        fg_color="#1a0033",
        hover_color="#ff00ff",
        command=ventana.destroy
    )
    btn_cerrar.pack(pady=10)


def _agregar_ruta_a_playlist(app, nombre_playlist, ruta, ventana=None):
    playlists = cargar_playlists()
    if nombre_playlist not in playlists:
        return

    old_rutas = list(playlists[nombre_playlist]["canciones"])

    if ruta not in playlists[nombre_playlist]["canciones"]:
        playlists[nombre_playlist]["canciones"].append(ruta)
        guardar_playlists(playlists)

        new_rutas = list(playlists[nombre_playlist]["canciones"])
        _actualizar_cola_reproductor(app, old_rutas, new_rutas)

    if ventana is not None:
        ventana.destroy()

    abrir_playlist(app, nombre_playlist)


def agregar_a_playlist(app, cancion):
    playlists = cargar_playlists()

    if not playlists:
        crear_playlist(app, cancion)
        return

    ventana = ctk.CTkToplevel(app.root)
    ventana.title("Agregar a playlist")
    ventana.geometry("420x420")
    ventana.grab_set()

    titulo = ctk.CTkLabel(
        ventana,
        text="Elegí una playlist",
        text_color="#00ffff",
        font=("Arial", 18, "bold")
    )
    titulo.pack(pady=12)

    frame = ctk.CTkScrollableFrame(ventana, fg_color="#140028")
    frame.pack(fill="both", expand=True, padx=12, pady=10)

    for nombre in playlists.keys():
        btn = ctk.CTkButton(
            frame,
            text=nombre,
            fg_color="#220044",
            hover_color="#ff00ff",
            command=lambda n=nombre: _agregar_cancion_a_playlist(app, cancion, n, ventana)
        )
        btn.pack(fill="x", pady=6)

    def crear_y_agregar():
        ventana.destroy()
        app.root.after(100, lambda: crear_playlist(app, cancion))

    btn_nueva = ctk.CTkButton(
        ventana,
        text="+ Crear nueva playlist",
        fg_color="#ff00ff",
        hover_color="#ff66ff",
        text_color="black",
        command=crear_y_agregar
    )
    btn_nueva.pack(pady=10)


def _agregar_cancion_a_playlist(app, cancion, nombre_playlist, ventana):
    playlists = cargar_playlists()
    if nombre_playlist not in playlists:
        return

    old_rutas = list(playlists[nombre_playlist]["canciones"])

    if cancion["ruta"] not in playlists[nombre_playlist]["canciones"]:
        playlists[nombre_playlist]["canciones"].append(cancion["ruta"])
        guardar_playlists(playlists)

        new_rutas = list(playlists[nombre_playlist]["canciones"])
        _actualizar_cola_reproductor(app, old_rutas, new_rutas)

    ventana.destroy()
    messagebox.showinfo("Listo", f"Se agregó a '{nombre_playlist}'.")


def reproducir_playlist_desde_biblioteca(app, nombre_playlist):
    playlists = cargar_playlists()
    datos = playlists.get(nombre_playlist)
    if not datos:
        return

    rutas = datos.get("canciones", [])
    if not rutas:
        messagebox.showinfo("Playlist vacía", "Esa playlist no tiene canciones.")
        return

    app.player.reproducir_playlist(rutas)