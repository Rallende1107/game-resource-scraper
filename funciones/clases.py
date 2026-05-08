import os, shutil, subprocess, logging
import concurrent.futures

from unrpa import UnRPA
from unrpa.versions import official_rpa
from unrpa.versions.version import HeaderBasedVersion
from .constantes import TIPOS_FORMATOS
# Importamos la librería unrpa directamente (¡adiós subprocess para los RPA!)
from typing import List




# from rpycdec import decompile, cli, rpa, save, translate

# ==========================================
# EL "HACK" PARA JUEGOS PROTEGIDOS
# ==========================================
class WHATEVER(HeaderBasedVersion):
    name = "WHATEVER"
    header = b"WHATEVER"

    def find_offset_and_key(self, archive):
        line = archive.readline()
        offset = int(line[8:24], 16)
        key = int(line[25:33], 16)
        return offset, key

# ==========================================
# Renpy
# ==========================================
class RenpyUtils:
    def __init__(self, log_callback=print, is_cancelled_callback=None):
        self.log = log_callback
        self.verificar_cancelacion = is_cancelled_callback

    def es_juego_renpy(self, directorio: str) -> bool:
        ESPERADO_RENPY = ['game']

        carpetas = [
            sub_directorio.lower()
            for sub_directorio in os.listdir(directorio)
            if os.path.isdir(os.path.join(directorio, sub_directorio))
        ]

        es_valido = all(c in carpetas for c in ESPERADO_RENPY)

        # 👇 log simple como querías
        if es_valido:
            self.log(f"✔️ {os.path.basename(directorio)} es juego Ren'Py")
        else:
            self.log(f"❌ {os.path.basename(directorio)} NO es juego Ren'Py")

        return es_valido

    def lista_juegos_renpy(self, directorio_padre: str) -> List[str]:
        self.log(f"🔍 Buscando juegos Ren'Py en: '{directorio_padre}'...")
        resultados = []

        try:
            for sub_directorio in os.listdir(directorio_padre):
                ruta = os.path.join(directorio_padre, sub_directorio)

                if not os.path.isdir(ruta):
                    continue

                if self.es_juego_renpy(ruta):
                    resultados.append(ruta)
                else:
                    self.log(f"{sub_directorio} no es Juego Renpy")

            return resultados

        except Exception as e:
            self.log(f"❌ Error: {e}")
            return []

    def listar_archivos(self, ruta_juego: str, extension: str) -> List[str]:
        game_path = os.path.join(ruta_juego, 'game')

        return [
            os.path.join(root, f)
            for root, _, files in os.walk(game_path)
            for f in files
            if f.lower().endswith(extension)
        ]

    def worker_rpa(self, ruta_completa, carpeta_game):
        """Worker que usa la API nativa de unrpa con soporte para ofuscación."""
        archivo_rpa = os.path.basename(ruta_completa)

        if self.verificar_cancelacion and self.verificar_cancelacion():
            return False

        # 1. ¡Gritamos que empezamos a lo loco!
        self.log(f"🔥 [ABRIENDO] Desempaquetando RPA: {archivo_rpa} ...")

        try:
            with open(ruta_completa, "rb") as f:
                header = f.read(32).decode(errors="ignore")
        except Exception:
            header = ""

        if header.startswith("RWA"):
            self.log(f"   ⛔ [SALTADO] {archivo_rpa} está protegido ({header.strip()})")
            return False

        try:
            # verbosity=0 para que la librería no imprima en la consola invisible
            extractor = UnRPA(filename=ruta_completa, path=carpeta_game, continue_on_error=True, verbosity=0)
            extractor.extract_files()

        except Exception as e1:
            try:
                # INTENTO 2: Forzando la versión estándar RPA-3.0
                self.log(f"   ⚠️ [REINTENTO] Forzando V3 en {archivo_rpa}...")
                extractor = UnRPA(filename=ruta_completa, path=carpeta_game, version=official_rpa.RPA3, verbosity=0)
                extractor.extract_files()

            except Exception as e2:
                try:
                    # INTENTO 3: El Hack Maestro "WHATEVER" para juegos ofuscados
                    self.log(f"   ☢️ [HACK] Usando WHATEVER en {archivo_rpa}...")
                    extractor = UnRPA(filename=ruta_completa, path=carpeta_game, version=WHATEVER, verbosity=0)
                    extractor.extract_files()

                except Exception as e3:
                    # Si fallan los 3, reportamos el último error
                    self.log(f"   ❌ [ERROR] Falló {archivo_rpa}: {str(e3)}")
                    return False

        # Si llegamos aquí, uno de los 3 intentos funcionó perfectamente
        try: os.remove(ruta_completa)
        except Exception: pass
        self.log(f"   ✅ [LISTO] -> {archivo_rpa} extraído y destruido.")
        return True

    def procesar_rpa(self, ruta_carpeta):
        nombre_carpeta = os.path.basename(ruta_carpeta)
        carpeta_game = os.path.join(ruta_carpeta, 'game')

        # Un título bien grande para que se note en el Log
        self.log(f"\n" + "="*50)
        self.log(f"📦 EXTRACCIÓN RPA DE: {nombre_carpeta}")
        self.log("="*50)

        # archivos_rpa = [(os.path.join(r, f), f) for r, _, fs in os.walk(carpeta_game) for f in fs if f.lower().endswith('.rpa')]
        archivos_rpa = self.listar_archivos(ruta_juego=ruta_carpeta, extension='.rpa')
        total_rpa = len(archivos_rpa)

        if total_rpa == 0:
            self.log("   🤷‍♂️ No hay archivos .RPA aquí.")
            return

        self.log(f"🎯 Se detectaron {total_rpa} archivos RPA.\n")
        archivos_extraidos = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futuros = [executor.submit(self.worker_rpa, ruta, carpeta_game) for ruta in archivos_rpa]

            for futuro in concurrent.futures.as_completed(futuros):
                try:
                    exito = futuro.result()
                    if exito: archivos_extraidos += 1
                except Exception as e:
                    self.log(f"❌ Error en hilo: {e}")

        self.log(f"\n🎉 EXTRACCIÓN FINALIZADA: {archivos_extraidos}/{total_rpa} paquetes de {nombre_carpeta}\n")

    def descompile_rpyc(self, ruta_juego):
        nombre_carpeta = os.path.basename(ruta_juego)
        sub_directorio_game = os.path.join(ruta_juego, 'game')

        self.log(f"\n>>> 📜 INICIANDO DESCOMPILACIÓN RPYC: {nombre_carpeta}")

        try:
            process = subprocess.Popen(["python", "-m", "rpycdec", "decompile", sub_directorio_game], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            for line in process.stdout:
                mensaje = line.strip()
                if " -> " in mensaje:
                    izq, der = mensaje.split(" -> ", 1)
                    self.log(f"  [DESCOMPILANDO] {os.path.basename(izq.replace('\\', '/'))} -> {os.path.basename(der.replace('\\', '/'))}")
            process.wait()

            if process.returncode == 0:
                self.log(f"🎉 Descompilación de {nombre_carpeta} completada.")
        except Exception as e:
            self.log(f"❌ Error crítico al descompilar: {str(e)}")


# ==========================================
# Copiado
# ==========================================
class CopyUtils:
    def __init__(self, log_callback=print, progress_callback=None, is_cancelled_callback=None):
        self.log = log_callback
        self.actualizar_progreso = progress_callback
        self.verificar_cancelacion = is_cancelled_callback


    def copia_organizada(self, origen, destino, tipo_nombre, formatos, total_archivos, excluir=None):
        """Copia archivos manteniendo la estructura original."""
        if excluir is None: excluir = []
        EXCLUIR_CARPETAS = [c.lower() for c in excluir]
        origen_norm = os.path.normpath(origen)

        nombre_carpeta = os.path.basename(origen)
        base_dest = os.path.dirname(origen) if destino == origen or not destino.strip() else destino
        ruta_destino_final = os.path.join(base_dest, nombre_carpeta, tipo_nombre)

        # --- LOG ESTILO PANEL INFORMATIVO ---
        self.log(f"\n" + "="*50)
        self.log(f"📂 INICIANDO COPIA ORGANIZADA: {tipo_nombre.upper()}")
        self.log("="*50)
        self.log(f"   📍 Origen:  {nombre_carpeta}")
        self.log(f"   🎯 Destino: {os.path.basename(ruta_destino_final)}")
        self.log(f"   📦 Total a mover: {total_archivos} archivos\n")

        os.makedirs(ruta_destino_final, exist_ok=True)
        archivos_copiados = 0


        try:
            for root, dirs, files in os.walk(origen):
                # 👇 2. Frenar si el usuario presionó Cancelar al buscar carpetas
                if self.verificar_cancelacion and self.verificar_cancelacion():
                    self.log("   🛑 [INTERRUMPIDO] Copia cancelada por el usuario.")
                    break

                dirs[:] = [
                    d for d in dirs
                    if not (d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == origen_norm)
                    and not d.startswith(".")
                ]

                for archivo in files:
                    # 👇 3. Frenar si presionó Cancelar en medio de la copia de archivos
                    if self.verificar_cancelacion and self.verificar_cancelacion():
                        break

                    if archivo.lower().endswith(tuple(formatos)):
                        origen_archivo = os.path.join(root, archivo)
                        rel = os.path.relpath(origen_archivo, origen)
                        destino_archivo = os.path.join(ruta_destino_final, rel)

                        os.makedirs(os.path.dirname(destino_archivo), exist_ok=True)
                        shutil.copyfile(origen_archivo, destino_archivo)

                        archivos_copiados += 1

                        if self.actualizar_progreso:
                            self.actualizar_progreso(archivos_copiados, total_archivos)
                        elif archivos_copiados % 10 == 0 or archivos_copiados == total_archivos:
                            print(f"\r  [Copiando] {archivos_copiados}/{total_archivos}...", end='', flush=True)

            # Si terminó naturalmente (sin cancelar), lanzamos el log de éxito
            if not self.verificar_cancelacion or not self.verificar_cancelacion():
                if not self.actualizar_progreso: print()
                self.log(f"🎉 FINALIZADO: Se copiaron {archivos_copiados}/{total_archivos} archivos de {tipo_nombre}.")

        except Exception as e:
            self.log(f"❌ Error crítico en copia organizada: {e}")

    def copia_directa(self, origen, destino, tipo_nombre, formatos, total_archivos, excluir=None):
        """Copia archivos aplanando la estructura."""
        if excluir is None: excluir = []
        EXCLUIR_CARPETAS = [c.lower() for c in excluir]
        origen_norm = os.path.normpath(origen)

        nombre_carpeta = os.path.basename(origen)
        base_dest = os.path.dirname(origen) if destino == origen or not destino.strip() else destino
        ruta_destino_final = os.path.join(base_dest, f"{nombre_carpeta}_Extraccion", tipo_nombre)

        # --- LOG ESTILO PANEL INFORMATIVO ---
        self.log(f"\n" + "="*50)
        self.log(f"📑 INICIANDO COPIA DIRECTA: {tipo_nombre.upper()}")
        self.log("="*50)
        self.log(f"   📍 Origen:  {nombre_carpeta}")
        self.log(f"   🎯 Destino: {os.path.basename(ruta_destino_final)}")
        self.log(f"   📦 Total a mover: {total_archivos} archivos\n")

        os.makedirs(ruta_destino_final, exist_ok=True)
        archivos_copiados = 0

        try:
            for root, dirs, files in os.walk(origen):
                if self.verificar_cancelacion and self.verificar_cancelacion():
                    self.log("   🛑 [INTERRUMPIDO] Copia directa cancelada por el usuario.")
                    break

                dirs[:] = [
                    d for d in dirs
                    if not (d.lower() in EXCLUIR_CARPETAS and os.path.normpath(root) == origen_norm)
                    and not d.startswith(".")
                ]

                for archivo in files:
                    if self.verificar_cancelacion and self.verificar_cancelacion():
                        break

                    if archivo.lower().endswith(tuple(formatos)):
                        ruta_origen = os.path.join(root, archivo)
                        partes_ruta = os.path.relpath(root, origen).split(os.sep)
                        prefijo = "_".join([p for p in partes_ruta if p != "."])
                        nuevo_nombre = f"{prefijo}_{archivo}" if prefijo else archivo

                        shutil.copy2(ruta_origen, os.path.join(ruta_destino_final, nuevo_nombre))
                        archivos_copiados += 1

                        if self.actualizar_progreso:
                            self.actualizar_progreso(archivos_copiados, total_archivos)
                        elif archivos_copiados % 10 == 0 or archivos_copiados == total_archivos:
                            print(f"\r  [Copiando] {archivos_copiados}/{total_archivos}...", end='', flush=True)

            if not self.verificar_cancelacion or not self.verificar_cancelacion():
                if not self.actualizar_progreso: print()
                self.log(f"🎉 FINALIZADO: Copia directa de {archivos_copiados}/{total_archivos} archivos de {tipo_nombre} completada.")

        except Exception as e:
            self.log(f"❌ Error crítico en copia directa: {e}")