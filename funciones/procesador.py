import os, shutil, subprocess, requests, re
from pytubefix import YouTube
from .utils import verificar_estructura_renpy, listar_carpetas_renpy, archivos_por_extension, listar_sub_carpetas
from .utils import verificar_estructura_html, listar_carpetas_html


import unrpa as unrpa
from rpycdec import decompile, translate

formatos_imagen = ['.jpg', '.jpeg', '.webp', '.png', '.bmp', '.gif', '.tiff', '.tif', '.svg', '.rpgmvp', '.avif',]
formatos_fuente = ['.woff', '.otf', '.ttf', '.ttc',]
formatos_videos = [".mp4", ".mkv", ".avi", ".mov", ".webm", ".wmv", ".flv",]
formatos_musica = [".mp3", ".aac", ".ogg", ".wma", ".wav", ]

# Diccionario para asociar los tipos con sus variables globales y carpetas
TIPOS_FORMATOS = {
    "imagen": (formatos_imagen, "Imagenes"),
    "fuente": (formatos_fuente, "Fuentes"),
    "musica": (formatos_musica, "Canciones"),
    "video": (formatos_videos, "Videos"),
}

def procesar_renpy(origen, destino, tipo_directorio, opciones):
    CARPETAS = []

    if tipo_directorio == 'único':
        if verificar_estructura_renpy(origen):
            CARPETAS.append(origen)
    else:
        CARPETAS = listar_carpetas_renpy(origen)

    if destino is None or destino == '':
        destino = origen

    for carpeta in CARPETAS:
        carpeta_game = os.path.join(carpeta, "game")
        nombre_carpeta = os.path.basename(carpeta)

        cantidad_rpa = archivos_por_extension(carpeta_game, '.rpa')
        cantidad_rpy = archivos_por_extension(carpeta_game, '.rpy')
        cantidad_rpyc = archivos_por_extension(carpeta_game, '.rpyc')

        # Extraer RPA si es necesario
        if cantidad_rpa > 0:
            if 'rpa' in opciones or ('rpyc' in opciones and cantidad_rpyc == 0) or any(opcion in opciones for opcion in ['img', 'sources', 'music', 'video']):
                extraer_rpa(carpeta, nombre_carpeta)
        elif 'rpa' in opciones:
            print(f'No hay archivos RPA para extraer en {nombre_carpeta}')

        # Descompilar RPYC
        if 'rpyc' in opciones:
            if cantidad_rpyc > 0 or cantidad_rpa > 0:
                decompilar_rpyc(carpeta, nombre_carpeta)

        # Mapeo de opciones con tipos para copia_organizada
        operaciones_copia = {
            'img': "imagen",
            'sources': "fuente",
            'music': "musica",
            'video': "video",
        }
        cantidad_rpa = archivos_por_extension(carpeta_game, '.rpa')
        cantidad_rpy = archivos_por_extension(carpeta_game, '.rpy')
        cantidad_rpyc = archivos_por_extension(carpeta_game, '.rpyc')

        # Ejecutar copias
        for opcion, tipo in operaciones_copia.items():
            if opcion in opciones:
                formatos, _ = TIPOS_FORMATOS[tipo]  # Obtener los formatos del tipo
                # cantidad_archivos = archivos_por_extension(carpeta_game, formatos)
                cantidad_archivos = archivos_por_extension(carpeta, formatos)

                if cantidad_rpa == 0 and cantidad_archivos > 0:
                    print(f'📂 Copiando {tipo} desde {nombre_carpeta} hacia {destino}')
                    # copia_organizada(carpeta, destino, cantidad_archivos, tipo)
                    copia_organizada(carpeta=carpeta, destino=destino, tipo=tipo, tipo_juego=1)


def procesar_multimedia(origen, destino, tipo_directorio, opciones, tipo_copia):
    CARPETAS = []

    if tipo_directorio == 'único':
        CARPETAS.append(origen)
    else:
        CARPETAS = listar_sub_carpetas(origen)

    if destino is None or destino == '':
        destino = origen

    for carpeta in CARPETAS:
        nombre_carpeta = os.path.basename(carpeta)
        operaciones_copia = {
            'img': "imagen",
            'sources': "fuente",
            'music': "musica",
            'video': "video",
        }
        # Ejecutar copias
        for opcion, tipo in operaciones_copia.items():
            if opcion in opciones:
                formatos, _ = TIPOS_FORMATOS[tipo]
                cantidad_archivos = archivos_por_extension(carpeta, formatos)

                if cantidad_archivos > 0:
                    print(f'📂 Copiando {tipo} desde {nombre_carpeta} hacia {destino}')
                    if tipo_copia == 'directa':
                        copia_directa(carpeta, destino, cantidad_archivos, tipo)
                    else:
                        copia_organizada(carpeta, destino, cantidad_archivos, tipo)



def procesar_html(origen, destino, tipo_directorio, opciones):
    CARPETAS = []

    if tipo_directorio == 'único':
        if verificar_estructura_html(origen):
            CARPETAS.append(origen)
    else:
        CARPETAS = listar_carpetas_html(origen)

    if destino is None or destino == '':
        destino = origen

    for carpeta in CARPETAS:

        # Mapeo de opciones con tipos para copia_organizada
        operaciones_copia = {
            'img': "imagen",
            'sources': "fuente",
            'music': "musica",
            'video': "video",
        }

        # Ejecutar copias
        for opcion, tipo in operaciones_copia.items():
            if opcion in opciones:
                formatos, _ = TIPOS_FORMATOS[tipo]  # Obtener los formatos del tipo
                cantidad_archivos = archivos_por_extension(carpeta, formatos)
                print(f'📂 Copiando {tipo} desde {carpeta} hacia {destino}')
                copia_organizada(carpeta, destino, cantidad_archivos, tipo)


def procesar_rpgm(origen, destino, tipo_directorio, opciones):
    pass

def procesar_unity(origen, destino, tipo_directorio, opciones):
    pass



def procesar_directorios(origen, destino,  opciones):
    if not destino.strip():
        destino = origen  # Si no hay destino, usamos la misma carpeta de origen

    nombre_carpeta = os.path.basename(origen)
    archivo_destino = f"Lista_{nombre_carpeta}.txt"
    ruta_destino_final = os.path.join(destino, archivo_destino)

    with open(ruta_destino_final, 'w', encoding='utf-8') as archivo:
        if "lista" in opciones:
            # Lista solo el contenido inmediato del directorio sin entrar en subdirectorios
            contenido = os.listdir(origen)
            archivo.write("\n".join(contenido) + "\n")

        if "lista_completa" in opciones:
            # Lista recursivamente todos los archivos y carpetas dentro del directorio
            for dirpath, dirnames, filenames in os.walk(origen):
                archivo.write(f"Directorio: {dirpath}\n")
                for nombre in dirnames:
                    archivo.write(f"    {nombre}/\n")  # Subcarpeta
                for nombre in filenames:
                    archivo.write(f"        {nombre}\n")  # Archivo
                archivo.write("\n")

        if "eliminar_directorios_vacios" in opciones:
            eliminar_carpetas_vacias(origen)

    print(f"✅ Listado guardado en: {ruta_destino_final}")

# ================================================
# FUNCIONES Proceso
# ================================================
# def proceso_renpy(lista_carpetas, opciones, destino):
#     for carpeta in lista_carpetas:
#         carpeta_game = os.path.join(carpeta, "game")
#         nombre_carpeta = os.path.basename(carpeta)
#         cantidad_rpa = archivos_por_extension(carpeta_game, '.rpa')
#         cantidad_rpyc = archivos_por_extension(carpeta_game, '.rpyc')

#         if cantidad_rpa > 0:
#             if 'rpa' in opciones or ('rpyc' in opciones and cantidad_rpyc == 0) or any(opcion in opciones for opcion in ['img', 'sources', 'music', 'video']):
#                 extraer_rpa(carpeta, nombre_carpeta)
#         elif 'rpa' in opciones:
#             print(f'No hay archivos RPA para extraer en {nombre_carpeta}')

#         # Descompilar RPYC
#         if 'rpyc' in opciones:
#             if cantidad_rpyc > 0 or cantidad_rpa > 0:
#                 decompilar_rpyc(carpeta, nombre_carpeta)

#         # Mapeo de opciones con tipos para copia_organizada
#         operaciones_copia = {
#             'img': "imagen",
#             'sources': "fuente",
#             'music': "musica",
#             'video': "video",
#         }
#         cantidad_rpa = archivos_por_extension(carpeta_game, '.rpa')

#         # Ejecutar copias
#         for opcion, tipo in operaciones_copia.items():
#             if opcion in opciones:
#                 formatos, _ = TIPOS_FORMATOS[tipo]  # Obtener los formatos del tipo
#                 cantidad_archivos = archivos_por_extension(carpeta_game, formatos)

#                 if cantidad_rpa == 0 and cantidad_archivos > 0:
#                     print(f'📂 Copiando {tipo} desde {nombre_carpeta} hacia {destino}')
#                     copia_organizada(carpeta=carpeta, destino=destino, cantidad_total=cantidad_archivos, tipo=tipo, renpy=True)

# ================================================
# FUNCIONES Copiado
# ================================================
# def copia_organizada(carpeta, destino, cantidad_total, tipo, renpy=False):
#     """Copia archivos de un tipo específico (imagen, fuente, video, música...) desde una carpeta de origen a un destino."""

#     if tipo not in TIPOS_FORMATOS:
#         raise ValueError(f"❌ Tipo '{tipo}' no admitido. Opciones: {list(TIPOS_FORMATOS.keys())}")

#     formatos, tipo_str = TIPOS_FORMATOS[tipo]
#     print(f"\n>>> Iniciando copia de {tipo_str}...")

#     archivos_copiados = 0
#     carpeta_game = carpeta
#     # if renpy:
#     #     carpeta_game = os.path.join(carpeta, 'game')
#     # else:
#     #     carpeta_game = os.path.join(carpeta)

#     nombre_carpeta = os.path.basename(carpeta)
#     carpeta_destino = f"{nombre_carpeta}_Extraccion"

#     # Definir ruta de destino
#     ruta_destino_final = os.path.join(
#         os.path.dirname(carpeta) if destino == carpeta or not destino.strip() else destino,
#         carpeta_destino,
#         tipo_str
#     )

#     try:
#         # Contar archivos disponibles
#         total_archivos = sum(
#             len(files) for r, _, files in os.walk(carpeta_game)
#             if any(f.lower().endswith(tuple(formatos)) for f in files)
#         )

#         if total_archivos == 0:
#             print(f"⚠️ No hay {tipo_str} para copiar.")
#             return
#         else:
#             os.makedirs(ruta_destino_final, exist_ok=True)
#             print(f"📂 Carpeta de destino: {ruta_destino_final}")

#         # total_archivos = min(total_archivos, cantidad_total)

#         print(f"🔍 {tipo_str} encontrados: {total_archivos}, se copiarán: {total_archivos}")

#         # Copiar archivos
#         for directorio_raiz, _, archivos in os.walk(carpeta_game):
#             for archivo in archivos:
#                 if archivo.lower().endswith(tuple(formatos)):
#                     ruta_origen = os.path.join(directorio_raiz, archivo)
#                     ruta_relativa = os.path.relpath(ruta_origen, carpeta_game)
#                     carpeta_destino_especifica = os.path.join(ruta_destino_final, os.path.dirname(ruta_relativa))

#                     os.makedirs(carpeta_destino_especifica, exist_ok=True)

#                     shutil.copyfile(ruta_origen, os.path.join(carpeta_destino_especifica, archivo))
#                     archivos_copiados += 1
#                     print(f"\r✅ Copiando {tipo}: {archivos_copiados} - {total_archivos} de {tipo_str}", end='', flush=True)

#                     if archivos_copiados >= total_archivos:
#                         break
#             if archivos_copiados >= total_archivos:
#                 break

#         print(f"\n🎉 Se copiaron {archivos_copiados} {tipo_str} correctamente.")

#     except Exception as e:
#         print(f"❌ Error durante la copia: {e}")

# def copia_organizada(carpeta, destino, tipo, tipo_juego="general"):

#     config = CONFIG_JUEGOS.get(tipo_juego, {})
#     EXCLUIR_CARPETAS = [c.lower() for c in config.get("excluir_carpetas", [])]

#     if tipo not in TIPOS_FORMATOS:
#         raise ValueError(f"❌ Tipo '{tipo}' no admitido. Opciones: {list(TIPOS_FORMATOS.keys())}")

#     formatos, tipo_str = TIPOS_FORMATOS[tipo]
#     print(f"\n>>> Iniciando copia de {tipo_str}...")

#     carpeta_base = carpeta
#     nombre_carpeta = os.path.basename(carpeta)
#     carpeta_destino = f"{nombre_carpeta}_Extraccion"

#     ruta_destino_final = os.path.join(
#         os.path.dirname(carpeta) if destino == carpeta or not destino.strip() else destino,
#         carpeta_destino,
#         tipo_str
#     )

#     try:
#         total_archivos = sum(
#             len(files) for r, _, files in os.walk(carpeta_base)
#             if any(f.lower().endswith(tuple(formatos)) for f in files)
#         )

#         if total_archivos == 0:
#             print(f"⚠️ No hay {tipo_str} para copiar.")
#             return

#         os.makedirs(ruta_destino_final, exist_ok=True)
#         print(f"📂 Carpeta de destino: {ruta_destino_final}")
#         print(f"🔍 {tipo_str} encontrados: {total_archivos}")

#         archivos_copiados = 0



#         for root, dirs, files in os.walk(carpeta_base):
#             dirs[:] = [d for d in dirs if d.lower() not in EXCLUIR_CARPETAS]
#             for archivo in files:
#                 if archivo.lower().endswith(tuple(formatos)):
#                     origen = os.path.join(root, archivo)
#                     rel = os.path.relpath(origen, carpeta_base)
#                     destino_final = os.path.join(ruta_destino_final, os.path.dirname(rel))

#                     os.makedirs(destino_final, exist_ok=True)
#                     shutil.copyfile(origen, os.path.join(destino_final, archivo))

#                     archivos_copiados += 1
#                     print(f"\r✅ Copiando {tipo}: {archivos_copiados}/{total_archivos}", end='', flush=True)

#         print(f"\n🎉 Se copiaron {archivos_copiados} {tipo_str} correctamente.")

#     except Exception as e:
#         print(f"❌ Error durante la copia: {e}")


CONFIG_JUEGOS = {
    0: {  # general
        "excluir_carpetas": []
    },
    1: {  # renpy
        "excluir_carpetas": ["cache", "tmp", "__pycache__", "lib", "renpy"]
    },
    2: {  # unity (ejemplo)
        "excluir_carpetas": ["_data", "mono", "plugins"]
    }
}

def copia_organizada(carpeta, destino, tipo, tipo_juego=0):

    config = CONFIG_JUEGOS.get(tipo_juego, CONFIG_JUEGOS.get(0, {}))
    EXCLUIR_CARPETAS = [c.lower() for c in config.get("excluir_carpetas", [])]

    if tipo not in TIPOS_FORMATOS:
        raise ValueError(f"❌ Tipo '{tipo}' no admitido. Opciones: {list(TIPOS_FORMATOS.keys())}")

    formatos, tipo_str = TIPOS_FORMATOS[tipo]
    print(f"\n>>> Iniciando copia de {tipo_str}...")

    carpeta_base = carpeta
    nombre_carpeta = os.path.basename(carpeta)
    carpeta_destino = f"{nombre_carpeta}_Extraccion"

    ruta_destino_final = os.path.join(
        os.path.dirname(carpeta) if destino == carpeta or not destino.strip() else destino,
        carpeta_destino,
        tipo_str
    )

    try:
        # 🔥 CONTEO (con lógica correcta)
        total_archivos = 0

        for root, dirs, files in os.walk(carpeta_base):
            dirs[:] = [
                d for d in dirs
                if not (
                    d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == os.path.normpath(carpeta_base)
                )
                and not d.startswith(".")
            ]

            total_archivos += sum(
                1 for f in files if f.lower().endswith(tuple(formatos))
            )

        if total_archivos == 0:
            print(f"⚠️ No hay {tipo_str} para copiar.")
            return

        os.makedirs(ruta_destino_final, exist_ok=True)
        print(f"📂 Carpeta de destino: {ruta_destino_final}")
        print(f"🔍 {tipo_str} encontrados: {total_archivos}")

        archivos_copiados = 0

        # 🔥 COPIA (misma lógica exacta)
        for root, dirs, files in os.walk(carpeta_base):
            dirs[:] = [
                d for d in dirs
                if not (
                    d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == os.path.normpath(carpeta_base)
                )
                and not d.startswith(".")
            ]

            for archivo in files:
                if archivo.lower().endswith(tuple(formatos)):
                    origen = os.path.join(root, archivo)
                    rel = os.path.relpath(origen, carpeta_base)
                    destino_final = os.path.join(
                        ruta_destino_final,
                        os.path.dirname(rel)
                    )

                    os.makedirs(destino_final, exist_ok=True)
                    shutil.copyfile(
                        origen,
                        os.path.join(destino_final, archivo)
                    )

                    archivos_copiados += 1
                    print(
                        f"\r✅ Copiando {tipo}: {archivos_copiados}/{total_archivos}",
                        end='',
                        flush=True
                    )

        print(f"\n🎉 Se copiaron {archivos_copiados} {tipo_str} correctamente.")

    except Exception as e:
        print(f"❌ Error durante la copia: {e}")

# def copia_organizada(carpeta, destino, tipo, tipo_juego=0):

#     config = CONFIG_JUEGOS.get(tipo_juego, {})
#     EXCLUIR_CARPETAS = [c.lower() for c in config.get("excluir_carpetas", [])]

#     if tipo not in TIPOS_FORMATOS:
#         raise ValueError(f"❌ Tipo '{tipo}' no admitido. Opciones: {list(TIPOS_FORMATOS.keys())}")

#     formatos, tipo_str = TIPOS_FORMATOS[tipo]
#     print(f"\n>>> Iniciando copia de {tipo_str}...")

#     carpeta_base = carpeta
#     nombre_carpeta = os.path.basename(carpeta)
#     carpeta_destino = f"{nombre_carpeta}_Extraccion"

#     ruta_destino_final = os.path.join(
#         os.path.dirname(carpeta) if destino == carpeta or not destino.strip() else destino,
#         carpeta_destino,
#         tipo_str
#     )

#     try:
#         # 🔥 Conteo CORRECTO (con exclusión aplicada)
#         total_archivos = 0
#         for root, dirs, files in os.walk(carpeta_base):
#             dirs[:] = [
#                 d for d in dirs
#                 if d.lower() not in EXCLUIR_CARPETAS and not d.startswith(".")
#             ]

#             total_archivos += sum(
#                 1 for f in files if f.lower().endswith(tuple(formatos))
#             )

#         if total_archivos == 0:
#             print(f"⚠️ No hay {tipo_str} para copiar.")
#             return

#         os.makedirs(ruta_destino_final, exist_ok=True)
#         print(f"📂 Carpeta de destino: {ruta_destino_final}")
#         print(f"🔍 {tipo_str} encontrados: {total_archivos}")

#         archivos_copiados = 0

#         # 🔥 Copia (misma lógica de exclusión)
#         for root, dirs, files in os.walk(carpeta_base):
#             # dirs[:] = [
#             #     d for d in dirs
#             #     if d.lower() not in EXCLUIR_CARPETAS and not d.startswith(".")
#             # ]
#             dirs[:] = [
#                 d for d in dirs
#                 if not (
#                     d.lower() in EXCLUIR_CARPETAS
#                     and root == carpeta_base  # 👈 SOLO en raíz
#                 )
#                 and not d.startswith(".")
#             ]


#             for archivo in files:
#                 if archivo.lower().endswith(tuple(formatos)):
#                     origen = os.path.join(root, archivo)
#                     rel = os.path.relpath(origen, carpeta_base)
#                     destino_final = os.path.join(
#                         ruta_destino_final,
#                         os.path.dirname(rel)
#                     )

#                     os.makedirs(destino_final, exist_ok=True)
#                     shutil.copyfile(
#                         origen,
#                         os.path.join(destino_final, archivo)
#                     )

#                     archivos_copiados += 1
#                     print(
#                         f"\r✅ Copiando {tipo}: {archivos_copiados}/{total_archivos}",
#                         end='',
#                         flush=True
#                     )

#         print(f"\n🎉 Se copiaron {archivos_copiados} {tipo_str} correctamente.")

#     except Exception as e:
#         print(f"❌ Error durante la copia: {e}")

def copia_directa(carpeta, destino, cantidad_total, tipo):
    """Copia archivos de un tipo específico (imagen, fuente, video, música...) desde una carpeta de origen a un destino."""

    if tipo not in TIPOS_FORMATOS:
        raise ValueError(f"❌ Tipo '{tipo}' no admitido. Opciones: {list(TIPOS_FORMATOS.keys())}")

    formatos, tipo_str = TIPOS_FORMATOS[tipo]
    print(f"\n>>> Iniciando copia de {tipo_str}...")

    archivos_copiados = 0
    nombre_carpeta = os.path.basename(carpeta)
    carpeta_destino = f"{nombre_carpeta}_Extraccion"

    # Definir ruta de destino
    ruta_destino_final = os.path.join(
        os.path.dirname(carpeta) if destino == carpeta or not destino.strip() else destino,
        carpeta_destino,
        tipo_str
    )

    try:
        # Contar archivos disponibles
        total_archivos = sum(len(files) for r, _, files in os.walk(carpeta)if any(f.lower().endswith(tuple(formatos)) for f in files))

        if total_archivos == 0:
            print(f"⚠️ No hay {tipo_str} para copiar.")
            return
        else:
            os.makedirs(ruta_destino_final, exist_ok=True)
            print(f"📂 Carpeta de destino: {ruta_destino_final}")

        total_archivos = min(total_archivos, cantidad_total)

        print(f"🔍 {tipo_str} encontrados: {total_archivos}, se copiarán: {total_archivos}")

    #     # Copiar archivos con el nuevo formato de nombre
        for raiz, dirs, archivos in os.walk(carpeta):
            for archivo in archivos:
                if archivo.lower().endswith(tuple(formatos)):
                    ruta_origen = os.path.join(raiz, archivo)

                    # Obtener el nombre de la subcarpeta (si existe)
                    partes_ruta = os.path.relpath(raiz, carpeta).split(os.sep)

                    # Renombrar el archivo con el formato correcto
                    nuevo_nombre = '_'.join(partes_ruta) + '_' + archivo
                    ruta_destino = os.path.join(ruta_destino_final, nuevo_nombre)

                    # Copiar el archivo
                    shutil.copy2(ruta_origen, ruta_destino)
                    archivos_copiados += 1
                    # print(f" Copiado: {nuevo_nombre}")
                    print(f"\r📑 Copiando {tipo}: {archivos_copiados} - {total_archivos} de {tipo_str}", end='', flush=True)

                    if archivos_copiados >= total_archivos:
                        print(f"✅ Se copiaron {archivos_copiados} archivos.")
                        return

    except Exception as e:
        print(f"❌ Error durante la copia: {e}")

# ================================================
# FUNCIONES Renpy
# ================================================
def decompilar_rpyc(carpeta, nombre_carpeta):
    print('Inicio Descompilar RPYC')
    carpeta_game = os.path.join(carpeta, 'game')
    print(carpeta_game)

    if not os.path.isdir(carpeta_game):
        print(f"No se encontró la carpeta 'game' en {nombre_carpeta}.")
        return

    print(f"Descompilando los archivos RPYC de la carpeta {nombre_carpeta}...")

    archivos_extraidos = []

    # Recorrer todos los archivos en el directorio "game" buscando los .rpyc
    for root, _, files in os.walk(carpeta_game):
        for archivo_rpyc in files:
            if archivo_rpyc.lower().endswith(".rpyc"):
                ruta_completa = os.path.join(root, archivo_rpyc)
                # print(ruta_completa)

                try:
                    # Ejecutar el comando descompile para descompilar el archivo .rpyc
                    resultado = subprocess.run(["python", "-m", "rpycdec", "decompile", carpeta_game])
                        # ["rpycdec", "decompile", ruta_completa], check=True)


                    # Si el proceso es exitoso, agregar a la lista de archivos extraídos
                    print(f"Archivo {archivo_rpyc} descompilado correctamente.")
                    archivos_extraidos.append(ruta_completa)

                except subprocess.CalledProcessError:
                    print(f"Error al descompilar el archivo {archivo_rpyc}.")
                    continue

    if archivos_extraidos:
        print(f"Archivos RPYC descompilados: {', '.join(archivos_extraidos)}")
    else:
        print("No se descompiló ningún archivo RPYC.")

# def extraer_rpa(carpeta, nombre_carpeta):
#     print('Inicio extraer_rpa')
#     carpeta_game = os.path.join(carpeta, 'game')

#     if not os.path.isdir(carpeta_game):
#         print(f"No se encontró la carpeta 'game' en {nombre_carpeta}.")
#         return

#     print(f"Extrayendo archivos RPA de la carpeta {nombre_carpeta}...")

#     archivos_extraidos = []

#     for root, _, files in os.walk(carpeta_game):
#         for archivo_rpa in files:
#             if archivo_rpa.lower().endswith(".rpa"):
#                 ruta_completa = os.path.join(root, archivo_rpa)

#                 try:
#                     # Intentar extracción sin argumento --force
#                     # resultado = subprocess.run(["unrpa", "-mp", carpeta_game, ruta_completa], check=True)
#                     resultado = subprocess.run(["python", "-m", "unrpa", "-mp", carpeta_game, ruta_completa], check=True)

#                     print(f"Archivo {archivo_rpa} extraído correctamente.")
#                     archivos_extraidos.append(ruta_completa)
#                 except subprocess.CalledProcessError:
#                     # Si falla, intentar extracción con argumento --force
#                     try:
#                         print(f"Error al extraer el archivo {archivo_rpa}, reintentando con --force.")
#                         resultado = subprocess.run(["python", "-m", "unrpa", "-f", carpeta_game, ruta_completa], check=True)

#                         print(f"Archivo {archivo_rpa} extraído correctamente con --force.")
#                         archivos_extraidos.append(ruta_completa)
#                     except subprocess.CalledProcessError:
#                         print(f"Error al extraer el archivo {archivo_rpa} después de reintentar con --force.")
#                         continue

#     for archivo_rpa in archivos_extraidos:
#         try:
#             os.remove(archivo_rpa)
#             print(f"Archivo {archivo_rpa} eliminado correctamente.")
#         except Exception as e:
#             print(f"Error al eliminar el archivo {archivo_rpa}: {e}")


def extraer_rpa(carpeta, nombre_carpeta):
    import os
    import subprocess

    print('Inicio extraer_rpa')
    carpeta_game = os.path.join(carpeta, 'game')

    if not os.path.isdir(carpeta_game):
        print(f"No se encontró la carpeta 'game' en {nombre_carpeta}.")
        return

    print(f"Extrayendo archivos RPA de la carpeta {nombre_carpeta}...")

    archivos_extraidos = []

    # Versiones soportadas por unrpa
    VERSIONES_RPA = [
        "RPA-3.0", "RPA-3.2", "RPA-4.0",
        "RPA-2.0", "RPA-1.0",
        "ALT-1.0", "ZiX-12A", "ZiX-12B"
    ]

    for root, _, files in os.walk(carpeta_game):
        for archivo_rpa in files:
            if not archivo_rpa.lower().endswith(".rpa"):
                continue

            ruta_completa = os.path.join(root, archivo_rpa)

            # 🔍 Leer header (para detectar protecciones)
            try:
                with open(ruta_completa, "rb") as f:
                    header = f.read(32).decode(errors="ignore")
            except:
                header = ""

            # 🚫 Detectar formatos protegidos tipo RWA
            if header.startswith("RWA"):
                print(f"⛔ {archivo_rpa} usa formato protegido ({header.strip()}) → saltando")
                continue

            # 🔹 Intento normal
            try:
                subprocess.run(
                    ["python", "-m", "unrpa", "-mp", carpeta_game, ruta_completa],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"✔️ {archivo_rpa} extraído correctamente.")
                archivos_extraidos.append(ruta_completa)

                os.remove(ruta_completa)
                print(f"🗑️ {archivo_rpa} eliminado tras extracción.")
                continue

            except subprocess.CalledProcessError:
                print(f"⚠️ Fallo inicial con {archivo_rpa}, probando versiones...")

            # 🔹 Intentar con versiones conocidas
            extraido = False
            for version in VERSIONES_RPA:
                try:
                    subprocess.run(
                        ["python", "-m", "unrpa", "-f", version, "-mp", carpeta_game, ruta_completa],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"✔️ {archivo_rpa} extraído con {version}")
                    archivos_extraidos.append(ruta_completa)
                    extraido = True
                    break

                except subprocess.CalledProcessError:
                    continue

            if not extraido:
                print(f"❌ No se pudo extraer {archivo_rpa} con ninguna versión.")
# ================================================
# Eliminar Directorios Vacios
# ================================================
def eliminar_carpetas_vacias(origen):
    """Elimina todas las carpetas vacías dentro del directorio de origen, incluyendo subdirectorios."""
    eliminadas = 0  # Contador de carpetas eliminadas

    for dirpath, dirnames, _ in os.walk(origen, topdown=False):  # Recorre desde las hojas hacia la raíz
        for dirname in dirnames:
            carpeta = os.path.join(dirpath, dirname)
            if not os.listdir(carpeta):  # Si está vacía
                os.rmdir(carpeta)  # Eliminar carpeta vacía
                print(f"🗑️ Eliminada: {carpeta}")
                eliminadas += 1

    if eliminadas == 0:
        print("✅ No se encontraron carpetas vacías.")
    else:
        print(f"🔹 Se eliminaron {eliminadas} carpetas vacías.")


def procesar_descargas(origen, destino, opciones):

    # Dividir el texto de origen en varias URLs (suponiendo que las URLs están separadas por salto de línea)
    enlaces = origen.splitlines()

    # Procesar las descargas según las opciones
    if 'utube' in opciones:
        # Ruta donde se crearán las descargas de YouTube
        ruta_destino_youtube = os.path.join(destino, 'Descargas_YouTube')
        os.makedirs(ruta_destino_youtube, exist_ok=True)
        print(f"📂 Se Creo la carpeta de destino: {ruta_destino_youtube}")

        print("Iniciando descarga de YouTube...")
        for enlace in enlaces:
            try:
                # Obtener el objeto YouTube
                yt = YouTube(enlace)

                # Seleccionar el stream (puedes personalizar esto, por ejemplo, eligiendo la resolución)
                stream = yt.streams.get_highest_resolution()

                try:
                    # Definir el nombre del archivo y la ruta de destino
                    nombre_video = yt.title + ".mp4"
                    # Limpiar caracteres no válidos para nombres de archivo
                    nombre_video = nombre_video.replace("?", "_").replace("&", "_").replace(" ", "_")
                    nombre_video = re.sub(r'[<>:"/\\|?*]', '_', nombre_video)
                    ruta_video = os.path.join(ruta_destino_youtube, nombre_video)

                    # Descargar el video
                    stream.download(output_path=ruta_destino_youtube, filename=nombre_video)

                    print(f"Video descargado: {ruta_video}")
                except Exception as e:
                    print(f"Error al guardar el video {yt.title}: {e}")

            except Exception as e:
                print(f"Error al descargar el video de YouTube {enlace}: {e}")

    if 'img' in opciones:
        # Ruta donde se crearán las descargas de imágenes
        ruta_destino_imagenes = os.path.join(destino, 'Descargas_Images')
        os.makedirs(ruta_destino_imagenes, exist_ok=True)
        print(f"📂 Se Creo la carpeta de destino: {ruta_destino_imagenes}")

        print("Iniciando descarga de imágenes...")
        for url in enlaces:
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()

                nombre = url.split("/")[-1]
                nombre = nombre.replace("?", "_").replace("&", "_")
                nombre = re.sub(r'[<>:"/\\|?*]', '_', nombre)

                nombre_archivo = os.path.join(ruta_destino_imagenes, nombre)


                with open(nombre_archivo, "wb") as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)

                print(f"Imagen descargada: {nombre_archivo}")
            except requests.exceptions.RequestException as e:
                print(f"Error al descargar {url}: {e}")

    print(f"Las descargas se guardarán en: {destino}")