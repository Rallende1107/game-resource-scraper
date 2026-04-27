# Extensiones
FORMATOS_IMAGEN = ['.jpg', '.jpeg', '.webp', '.png', '.bmp', '.gif', '.tiff', '.tif', '.svg', '.rpgmvp', '.avif']
FORMATOS_FUENTE = ['.woff', '.otf', '.ttf', '.ttc']
FORMATOS_VIDEOS = [".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv"]
FORMATOS_MUSICA = [".mp3", ".aac", ".ogg", ".wma", ".wav"]

OPCIONES_COPIA = ["audio", "font", "image", "video",]

TIPOS_FORMATOS = {
    "image": (FORMATOS_IMAGEN, "Imagenes"),
    "font":  (FORMATOS_FUENTE, "Fuentes"),
    "audio": (FORMATOS_MUSICA, "Audios"),
    "video": (FORMATOS_VIDEOS, "Videos"),
}

# Configuración de motores de juego
EXCLUIR_CARPETAS = {
    0: {"excluir_carpetas": []}, # General
    1: {"excluir_carpetas": ["cache", "tmp", "__pycache__", "lib", "renpy"]}, # RenPy
    2: {"excluir_carpetas": ["_data", "mono", "plugins"]} # Unity
}





# ESPERADO_RENPY = ['game', 'renpy', 'lib']

