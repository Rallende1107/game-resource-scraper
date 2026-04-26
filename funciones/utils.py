
import os

# ================================================
# FUNCIONES PARA LISTAR CARPETAS
# ================================================
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
def generador_rutas(carpeta_base, formatos, EXCLUIR_CARPETAS, ruta_destino_final):
    """
    GENERADOR: En lugar de crear una lista gigante que colapse la RAM,
    encuentra un archivo y lo 'escupe' (yield) uno por uno bajo demanda.
    """
    for root, dirs, files in os.walk(carpeta_base):
        dirs[:] = [
            d for d in dirs
            if not (d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == os.path.normpath(carpeta_base))
            and not d.startswith(".")
        ]

        for archivo in files:
            if archivo.lower().endswith(tuple(formatos)):
                origen = os.path.join(root, archivo)
                rel = os.path.relpath(origen, carpeta_base)
                destino_final = os.path.join(ruta_destino_final, os.path.dirname(rel))

                yield (origen, destino_final, archivo)



# def archivos_por_extension(ruta, extensiones):
#     """Cuenta la cantidad de archivos con las extensiones especificadas en el directorio dado."""
#     print ("Ejecutando Función archivos por extension")

#     if not isinstance(extensiones, list):
#         extensiones = [extensiones]

#     try:
#         contador = 0
#         for root, _, files in os.walk(ruta):
#             for archivo in files:
#                 if any(archivo.lower().endswith(ext.lower()) for ext in extensiones):
#                     contador += 1
#         print (f"\nSe encontraron {contador} archivos con las extensiones {extensiones} \nEn la ruta: {ruta}")
#         return contador

#     except Exception as e:
#         print(f"Error al ejecutar la función 'archivos_por_extension': {str(e)}")
#         return 0

def archivos_por_extension(ruta, extensiones):
    """Cuenta la cantidad de archivos con las extensiones especificadas en el directorio dado."""
    print("Ejecutando Función archivos por extension")

    # 1. Asegurar que extensiones sea una lista/tupla
    if isinstance(extensiones, str):
        extensiones = [extensiones]

    # 🔥 LA MAGIA: Convertir la lista a una TUPLA con todo en minúsculas UNA SOLA VEZ.
    ext_tupla = tuple(ext.lower() for ext in extensiones)

    try:
        contador = 0
        for root, _, files in os.walk(ruta):
            for archivo in files:
                # 2. Comprobación nativa ultrarrápida.
                # Le pasamos la tupla entera a endswith()
                if archivo.lower().endswith(ext_tupla):
                    contador += 1

        print(f"\nSe encontraron {contador} archivos con las extensiones {extensiones} \nEn la ruta: {ruta}")
        return contador

    except Exception as e:
        print(f"❌ Error al ejecutar la función 'archivos_por_extension': {str(e)}")
        return 0