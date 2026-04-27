from collections import Counter
from typing import Optional, List
import os
from collections import Counter
# ================================================
# FUNCIONES PARA LISTAR CARPETAS
# ================================================

def files_in_folder(folder_path: str, excluir: Optional[List[str]] = None) -> Counter:
    """Escanea el directorio UNA SOLA VEZ ignorando las carpetas excluidas."""
    if excluir is None: excluir = []
    EXCLUIR_CARPETAS = [c.lower() for c in excluir]
    conteos = Counter()

    try:
        for root, dirs, files in os.walk(folder_path):
            # Filtramos carpetas no deseadas en CUALQUIER nivel (ej: lib, renpy, cache)
            dirs[:] = [d for d in dirs if d.lower() not in EXCLUIR_CARPETAS and not d.startswith(".")]

            for archivo in files:
                _, ext = os.path.splitext(archivo)
                conteos[ext.lower()] += 1
        return conteos
    except Exception as e:
        print(f"❌ Error al escanear el directorio: {e}")
        return Counter()



def listar_sub_carpetas(directorio):
    """Devuelve una lista con las rutas completas de las carpetas de primer nivel dentro de un directorio, ignorando archivos y subcarpetas."""
    try:
        # Retorna las rutas completas, no solo los nombres
        return [os.path.join(directorio, nombre) for nombre in os.listdir(directorio)
                if os.path.isdir(os.path.join(directorio, nombre))]
    except Exception as e:
        print(f"Error al listar carpetas en {directorio}: {e}")
        return []

def listar_carpetas_renpy(directorio):
    print('listar carpetas')
    """Lista las carpetas dentro de un directorio dado y verifica su estructura."""

    print(f"Listar subcarpetas de: '{directorio}'")

    lista_carpetas = []
    try:
        carpetas = [f for f in os.listdir(directorio) if os.path.isdir(os.path.join(directorio, f))]
        for carpeta in carpetas:
            carpeta_path = os.path.join(directorio, carpeta)
            if verificar_estructura_renpy(carpeta_path):
                # print(f"Carpeta {carpeta_path} añadida a lista de carpetas")
                lista_carpetas.append(carpeta_path)
        return lista_carpetas
    except Exception as e:
        print(f"Error al listar carpetas en {directorio}: {e}")
        return []

def listar_carpetas_html(directorio):
    print('listar carpetas')
    """Lista las carpetas dentro de un directorio dado y verifica su estructura."""

    print(f"Listar subcarpetas de: '{directorio}'")

    lista_carpetas = []
    try:
        carpetas = [f for f in os.listdir(directorio) if os.path.isdir(os.path.join(directorio, f))]
        for carpeta in carpetas:
            carpeta_path = os.path.join(directorio, carpeta)
            if verificar_estructura_html(carpeta_path):
                lista_carpetas.append(carpeta_path)
        return lista_carpetas
    except Exception as e:
        print(f"Error al listar carpetas en {directorio}: {e}")
        return []


# ================================================
# FUNCIONES PARA VERIFICACIÓN DE ESTRUCTURA
# ================================================
def verificar_estructura_renpy(directorio):
    """Verifica que el directorio contenga las subcarpetas 'game' de manera insensible a mayúsculas y minúsculas."""
    print(f"Verificando estructura de {directorio}")

    # esperado = ['game', 'renpy', ]
    esperado = ['game', ]
    carpetas_en_directorio = [carpeta.lower() for carpeta in os.listdir(directorio) if os.path.isdir(os.path.join(directorio, carpeta))]

    for carpeta in esperado:
        if carpeta not in carpetas_en_directorio:
            path = os.path.join(directorio, carpeta)
            print(f"Estructura incorrecta: {path} no existe.")
            return False
    return True

def verificar_estructura_html(directorio):
    """
    Verifica que el directorio contenga al menos un archivo .html o .HTML.
    """
    print(f"Verificando archivos HTML en {directorio}")

    archivos_en_directorio = os.listdir(directorio)

    for archivo in archivos_en_directorio:
        if os.path.isfile(os.path.join(directorio, archivo)) and archivo.lower().endswith('.html'):
            print(f"Archivo HTML encontrado: {archivo}")
            return True

    print("No se encontró ningún archivo .html en el directorio.")
    return False

# ================================================
# FUNCIONES PARA CONTAR ARCHIVOS
# ================================================
def archivos_por_extension(ruta, extensiones):
    """Cuenta la cantidad de archivos con las extensiones especificadas en el directorio dado."""
    print ("Ejecutando Función archivos por extension")

    if not isinstance(extensiones, list):
        extensiones = [extensiones]

    try:
        contador = 0
        for root, _, files in os.walk(ruta):
            for archivo in files:
                if any(archivo.lower().endswith(ext.lower()) for ext in extensiones):
                    contador += 1
        print (f"\nSe encontraron {contador} archivos con las extensiones {extensiones} \nEn la ruta: {ruta}")
        return contador

    except Exception as e:
        print(f"Error al ejecutar la función 'archivos_por_extension': {str(e)}")
        return 0

