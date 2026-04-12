import json
import os

# Nombre del archivo donde se almacenarán las canciones
ARCHIVO_JSON = "canciones.json"


def cargar_canciones():
    """Carga las canciones desde el archivo JSON."""
    if os.path.exists(ARCHIVO_JSON):
        try:
            with open(ARCHIVO_JSON, "r", encoding="utf-8") as archivo:
                return json.load(archivo)
        except json.JSONDecodeError:
            return []
    return []


def guardar_canciones(canciones):
    """Guarda la lista de canciones en el archivo JSON."""
    with open(ARCHIVO_JSON, "w", encoding="utf-8") as archivo:
        json.dump(canciones, archivo, indent=4, ensure_ascii=False)