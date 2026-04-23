# Nickify - Reproductor de Música 
Proyecto desarrollado por: Ivo Gioffre
Materia: Laboratorio de Laboratorio de Algoritmos y Estructura de Datos

## Descripción de archivos

- Main.py
  Archivo principal del programa. Inicializa la interfaz gráfica, gestiona la navegación entre vistas (inicio, biblioteca, playlists) y conecta todos los módulos

- agregar_musica.py
  Permite seleccionar archivos MP3 desde el sistema, extraer sus metadatos (título, artista, etc.) y agregarlos a la biblioteca del programa

- playlist.py
  Maneja la creación, edición y eliminación de playlists. También controla la visualización de la biblioteca y la gestión de canciones dentro de cada playlist 

- reproducir.py
  Contiene la lógica del reproductor de audio: reproducir, pausar, avanzar, retroceder, shuffle, repeat y actualización de la interfaz del reproductor

- json_utils.py  
  Se encarga de guardar y cargar las canciones desde un archivo JSON para mantener la información persistente

- canciones.json
  Archivo donde se almacenan las canciones agregadas por el usuario con ruta, titulo,artista,albúm,año de lanzamiento y genero musical ademas de la duración

- playlist.json
  Archivo donde se guardan las playlists creadas

- canciones_guardadas
  Carpeta donde se copian físicamente las canciones agregadas al programa

- Carpeta Playlist
    Carpeta donde se guardan las imágenes de portada de las playlists

- Carpeta imagenes  
    Contiene los íconos desarrollados e imágenes utilizadas en la interfaz (botones, logo, etc)

## Tecnologías utilizadas

- Python 3
- CustomTkinter (interfaz gráfica)
- Pygame (reproducción de audio)
- Mutagen (metadatos de MP3)
- Pillow (manejo de imágenes)


## Instalación

1- Clonar Repositorio 
2- instalar dependencias:pip install -r requirements.txt
3- Ejeución: python main.py


## Funcionamiento

- Al iniciar el programa, se cargan automáticamente las canciones almacenadas en un archivo JSON, lo que permite mantener la información entre ejecuciones

- Las canciones que el usuario agrega se copian a una carpeta interna del sistema, asegurando su disponibilidad independientemente de su ubicación original.

- El reproductor permite navegar entre canciones y playlists manteniendo el estado actual de reproducción, sin interrupciones innecesarias

- El buscador funciona de manera dinámica, filtrando en tiempo real según título, artista, álbum, género o año

- Las playlists se guardan de forma persistente en un archivo JSON, conservando tanto las canciones como sus configuraciones asociadas


## Vitacora de progreso 

8/4
Se diseña la interfaz inicial con un estilo neon y se le da una estetica visual aunque por ahora sin funciones. 

9/4

se agrego la funcion de agregar canciones con su titulo artista,duracion y un mas que en un futuro permitira agregarla a la playlist e introduce el logo del proyecto.

12/04

se agrega la opcion de reproducir canciones, adelantarlas, atrasarlas,pasar a la siguiente y subir el volumen.

16/04

1-Se agrega la funcion de crear playlist con el nombre que quieras y la imagen que quieras  de portada,en esta se podra agregar y borrar canciones de las disponibles en el inicio, tambien desde el incios se podran agregar canciones a las playlist y si no hay ninguna crearla.

16/04 Parte 2
Se agrega la opcion de escuchar en moso aleatorio y de repetir la cancion cuando finalize tanto en las playlist como en el incio.

19/04

Se implementa el buscador tanto en el inicio como en las playlist filtrando por nombre de cancion artista album año y genero

ahora cuando una cancion esta en reproduccion aparece realtada

se hacen cambios en el modo aleatorio entre otros cambios generales que mejoran la experiencia en el reproductor.

22/04

Se agregan canciones con nombre artista album año y genero correspondiente cada una.

23/04

Se cambia el README agregando informacion sobre el funcionamiento de cada uno de los archivos del proyecto y en general,ademas de información sobre la instalación de librerías necesarias.

Se corrigue bug en las playlists.
