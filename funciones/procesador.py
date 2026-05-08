import os, shutil, subprocess, requests, re
from .constantes import TIPOS_FORMATOS, EXCLUIR_CARPETAS,  OPCIONES_COPIA
from .clases import RenpyUtils, CopyUtils
from .utils import files_in_folder, archivos_por_extension, listar_sub_carpetas, verificar_estructura_html, listar_carpetas_html

# from pytubefix import YouTube
def procesar_renpy(origen, destino, tipo_directorio, opciones, log_callback=print, progress_callback=None, is_cancelled_callback=None):
    utils = RenpyUtils(log_callback=log_callback, is_cancelled_callback=is_cancelled_callback)
    copiadora = CopyUtils(log_callback=log_callback, progress_callback=progress_callback, is_cancelled_callback=is_cancelled_callback)

    excluir = EXCLUIR_CARPETAS[1]["excluir_carpetas"]
    # 👇 1. Le pasamos la señal a RenpyUtils
    # =========================
    # detectar carpetas
    # =========================
    utils.log(opciones)
    if tipo_directorio == 'único':
        CARPETAS = [origen] if utils.es_juego_renpy(directorio=origen) else []
    else:
        CARPETAS = utils.lista_juegos_renpy(directorio_padre=origen)

    destino = destino if destino else origen
    # =========================
    # procesar cada juego
    # =========================
    quiere_rpa = 'rpa' in opciones
    quiere_rpyc = 'rpyc' in opciones
    quiere_copiar = any(op in opciones for op in OPCIONES_COPIA)

    for carpeta in CARPETAS:

        if is_cancelled_callback and is_cancelled_callback():
            break

        nombre_carpeta = os.path.basename(carpeta)
        utils.log(f"\n>>> 🚀 PROCESANDO: {nombre_carpeta}")

        conteos = files_in_folder(folder_path=carpeta, excluir=excluir)
        count_rpa = conteos.get('.rpa', 0)


        # =========================
        # 📦 RPYC (si aplica)
        # =========================
        if quiere_rpyc:
            utils.log("⚠️ Descompilación RPYC no implementada en la interfaz actual.")
            # utils.log("\n📦 Extrayendo TODOS los archivos '.RPYC'")
            # utils.descompile_rpyc(ruta_juego=carpeta)
            # conteos = get_files_by_extension(carpeta=carpeta, excluir=excluir_renpy)
            pass

        # ==========================================================
        # 📦 FASE DE EXTRACCIÓN (Unificada)
        # ==========================================================
        # Extraemos si: el usuario lo pidió O si quiere copiar pero hay RPAs
        if count_rpa > 0 and (quiere_rpa or quiere_copiar):
            if quiere_rpa:
                utils.log("📦 Opción RPA seleccionada. Extrayendo...")
            else:
                utils.log("📦 Archivos RPA detectados (necesarios para la copia). Extrayendo...")

            utils.procesar_rpa(ruta_carpeta=carpeta)

            utils.log("🔄 Actualizando inventario post-extracción...")
            conteos = files_in_folder(folder_path=carpeta, excluir=excluir)
            count_rpa = conteos.get('.rpa', 0)

        elif quiere_rpa and count_rpa == 0:
            utils.log("❌ No hay archivos RPA para extraer.")

        # ==========================================================
        # 📂 FASE DE COPIA (Solo si hay algo que copiar)
        # ==========================================================
        if quiere_copiar:
            utils.log(f"📂 Iniciando fase de copiado organizado...")
            for op_key in OPCIONES_COPIA:
                if op_key in opciones:
                    # Obtenemos formatos y nombres (ej: "img" -> "Imágenes")
                    formatos, nombre_plural = TIPOS_FORMATOS[op_key]
                    cantidad = sum(conteos.get(ext, 0) for ext in formatos)

                    if cantidad > 0:
                        utils.log(f"✔️ {nombre_plural} encontrados: {cantidad}. Copiando...")
                        copiadora.copia_organizada(
                            origen=carpeta,
                            destino=destino,
                            tipo_nombre=nombre_plural,
                            formatos=formatos,
                            total_archivos=cantidad,
                            excluir=excluir
                        )
                    else:
                        utils.log(f"❌ {nombre_plural}: No se encontraron archivos sueltos.")



def procesar_multimedia(origen, destino, tipo_directorio, opciones, tipo_copia):
    pass
    # CARPETAS = []

    # if tipo_directorio == 'único':
    #     CARPETAS.append(origen)
    # else:
    #     CARPETAS = listar_sub_carpetas(origen)

    # if destino is None or destino == '':
    #     destino = origen

    # for carpeta in CARPETAS:
    #     nombre_carpeta = os.path.basename(carpeta)

    #     # Ejecutar copias
    #     for opcion, tipo in OP_COPIAS.items():
    #         if opcion in opciones:
    #             formatos, _ = TIPOS_FORMATOS[tipo]
    #             cantidad_archivos = archivos_por_extension(carpeta, formatos)

    #             if cantidad_archivos > 0:
    #                 print(f'📂 Copiando {tipo} desde {nombre_carpeta} hacia {destino}')
    #                 if tipo_copia == 'directa':
    #                     copia_directa(carpeta, destino, cantidad_archivos, tipo)
    #                 else:
    #                     copia_organizada(carpeta, destino, cantidad_archivos, tipo)



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
def copia_organizada(carpeta, destino, tipo, tipo_juego=0):
    pass

    # config = CONFIG_JUEGOS.get(tipo_juego, CONFIG_JUEGOS.get(0, {}))
    # EXCLUIR_CARPETAS = [c.lower() for c in config.get("excluir_carpetas", [])]

    # if tipo not in TIPOS_FORMATOS:
    #     raise ValueError(f"❌ Tipo '{tipo}' no admitido. Opciones: {list(TIPOS_FORMATOS.keys())}")

    # formatos, tipo_str = TIPOS_FORMATOS[tipo]
    # print(f"\n>>> Iniciando copia de {tipo_str}...")

    # carpeta_base = carpeta
    # nombre_carpeta = os.path.basename(carpeta)
    # carpeta_destino = f"{nombre_carpeta}"

    # ruta_destino_final = os.path.join(
    #     os.path.dirname(carpeta) if destino == carpeta or not destino.strip() else destino,
    #     carpeta_destino,
    #     tipo_str
    # )

    # try:
    #     # 🔥 CONTEO (con lógica correcta)
    #     total_archivos = 0

    #     for root, dirs, files in os.walk(carpeta_base):
    #         dirs[:] = [
    #             d for d in dirs
    #             if not (
    #                 d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == os.path.normpath(carpeta_base)
    #             )
    #             and not d.startswith(".")
    #         ]

    #         total_archivos += sum(
    #             1 for f in files if f.lower().endswith(tuple(formatos))
    #         )

    #     if total_archivos == 0:
    #         print(f"⚠️ No hay {tipo_str} para copiar.")
    #         return

    #     os.makedirs(ruta_destino_final, exist_ok=True)
    #     print(f"📂 Carpeta de destino: {ruta_destino_final}")
    #     print(f"🔍 {tipo_str} encontrados: {total_archivos}")

    #     archivos_copiados = 0

    #     # 🔥 COPIA (misma lógica exacta)
    #     for root, dirs, files in os.walk(carpeta_base):
    #         dirs[:] = [
    #             d for d in dirs
    #             if not (
    #                 d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == os.path.normpath(carpeta_base)
    #             )
    #             and not d.startswith(".")
    #         ]

    #         for archivo in files:
    #             if archivo.lower().endswith(tuple(formatos)):
    #                 origen = os.path.join(root, archivo)
    #                 rel = os.path.relpath(origen, carpeta_base)
    #                 destino_final = os.path.join(
    #                     ruta_destino_final,
    #                     os.path.dirname(rel)
    #                 )

    #                 os.makedirs(destino_final, exist_ok=True)
    #                 shutil.copyfile(
    #                     origen,
    #                     os.path.join(destino_final, archivo)
    #                 )

    #                 archivos_copiados += 1
    #                 print(
    #                     f"\r✅ Copiando {tipo}: {archivos_copiados}/{total_archivos}",
    #                     end='',
    #                     flush=True
    #                 )

    #     print(f"\n🎉 Se copiaron {archivos_copiados} {tipo_str} correctamente.")

    # except Exception as e:
    #     print(f"❌ Error durante la copia: {e}")


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
        # for enlace in enlaces:
        #     try:
        #         # Obtener el objeto YouTube
        #         yt = YouTube(enlace)

        #         # Seleccionar el stream (puedes personalizar esto, por ejemplo, eligiendo la resolución)
        #         stream = yt.streams.get_highest_resolution()

        #         try:
        #             # Definir el nombre del archivo y la ruta de destino
        #             nombre_video = yt.title + ".mp4"
        #             # Limpiar caracteres no válidos para nombres de archivo
        #             nombre_video = nombre_video.replace("?", "_").replace("&", "_").replace(" ", "_")
        #             nombre_video = re.sub(r'[<>:"/\\|?*]', '_', nombre_video)
        #             ruta_video = os.path.join(ruta_destino_youtube, nombre_video)

        #             # Descargar el video
        #             stream.download(output_path=ruta_destino_youtube, filename=nombre_video)

        #             print(f"Video descargado: {ruta_video}")
        #         except Exception as e:
        #             print(f"Error al guardar el video {yt.title}: {e}")

        #     except Exception as e:
        #         print(f"Error al descargar el video de YouTube {enlace}: {e}")

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
