

FORMATOS_IMAGEN = ['.jpg', '.jpeg', '.webp', '.png', '.bmp', '.gif', '.tiff', '.tif', '.svg', '.rpgmvp', '.avif',]
FORMATOS_FUENTE = ['.woff', '.otf', '.ttf', '.ttc',]
FORMATOS_VIDEOS = [".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv",]
FORMATOS_MUSICA = [".mp3", ".aac", ".ogg", ".wma", ".wav",]


# Diccionario para asociar los tipos con sus variables globales y carpetas
TIPOS_FORMATOS = {
    "imagen": (FORMATOS_IMAGEN, "Imagenes"),
    "fuente": (FORMATOS_FUENTE, "Fuentes"),
    "musica": (FORMATOS_MUSICA, "Audio"),
    "video": (FORMATOS_VIDEOS, "Videos"),
}


CONFIG_JUEGOS = {
    # general
    0: {"excluir_carpetas": []},
    # renpy
    1: {"excluir_carpetas": ["cache", "tmp", "__pycache__", "lib", "renpy"]},
    # unity (ejemplo)
    2: {"excluir_carpetas": ["_data", "mono", "plugins"]}
}

VERSIONES_RPA = [
    "RPA-3.0", "RPA-3.2", "RPA-4.0",
    "RPA-2.0", "RPA-1.0",
    "ALT-1.0", "ZiX-12A", "ZiX-12B"
]

