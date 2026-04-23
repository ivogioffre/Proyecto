import customtkinter as ctk


def crear_encabezado_canciones(parent, columnas=None, pesos=None):
    """Crea una fila de encabezados para la lista de canciones.
    
    Args:
        parent: widget padre donde se empaca el encabezado
        columnas: lista de nombres de columnas (default: ["Título", "Artista", "Álbum", "Año", "Género", "Duración"])
        pesos: lista de pesos para grid_columnconfigure (default: [4, 3, 3, 2, 2, 1, 0])
    """
    if columnas is None:
        columnas = ["Título", "Artista", "Álbum", "Año", "Género", "Duración"]
    
    if pesos is None:
        pesos = [4, 3, 3, 2, 2, 1, 0]

    encabezado = ctk.CTkFrame(parent, fg_color="#1f003d", corner_radius=10)
    encabezado.pack(fill="x", pady=(5, 0), padx=20)

    for i, peso in enumerate(pesos):
        encabezado.grid_columnconfigure(i, weight=peso, uniform="col")

    for index, texto in enumerate(columnas):
        lbl = ctk.CTkLabel(
            encabezado,
            text=texto,
            text_color="#00ffff",
            font=("Arial", 12, "bold"),
            anchor="w"
        )
        lbl.grid(row=0, column=index, sticky="w", padx=(10 if index == 0 else 5, 5), pady=10)

    return encabezado
