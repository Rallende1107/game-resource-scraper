import sys, os
from ui.main_view import Ui_MainWindow
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QPlainTextEdit, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QThread, Signal

from funciones.procesador import procesar_renpy, procesar_html, procesar_rpgm, procesar_unity, procesar_multimedia, procesar_directorios, procesar_descargas

# ==========================================
# EL "ANTI-COLGADOR" (Obrero en segundo plano)
# ==========================================
class WorkerRenpy(QThread):
    senal_log = Signal(str)
    senal_progreso = Signal(int, int)

    def __init__(self, origen, destino, tipo_directorio, opciones):
        super().__init__()
        self.origen = origen
        self.destino = destino
        self.tipo_directorio = tipo_directorio
        self.opciones = opciones
        self._is_cancelled = False  # <--- NUEVO: Bandera de cancelación

    def cancelar(self):
        """Esta función la llamará el botón Cancelar de la interfaz"""
        self._is_cancelled = True

    def verificar_cancelacion(self):
        """Esta función la consultará el procesador constantemente"""
        return self._is_cancelled

    def run(self):
        try:
            # Llamamos al procesador y le pasamos los walkie-talkies (emits)
            procesar_renpy(
                origen=self.origen,
                destino=self.destino,
                tipo_directorio=self.tipo_directorio,
                opciones=self.opciones,
                log_callback=self.senal_log.emit,
                progress_callback=self.senal_progreso.emit,
                is_cancelled_callback=self.verificar_cancelacion
            )

            if self._is_cancelled:
                self.senal_log.emit("\n🛑 PROCESO CANCELADO POR EL USUARIO")
            else:
                self.senal_log.emit("\n✅ PROCESO COMPLETADO CON ÉXITO")

        except Exception as e:
            self.senal_log.emit(f"\n❌ ERROR CRÍTICO: {str(e)}")

# ==========================================
# MAIN WINDOW
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # ==========================================
        # ARREGLO PARA EL PANEL DE LOG
        # ==========================================
        self.plainTextEdit_log = QPlainTextEdit(self.ui.tab_log)
        self.plainTextEdit_log.setReadOnly(True)
        self.plainTextEdit_log.setStyleSheet("background-color: #2b2b2b; color: #ffffff; font-family: Consolas; font-size: 11pt;")
        layout_log = QVBoxLayout(self.ui.tab_log)
        layout_log.addWidget(self.plainTextEdit_log)
        # ==========================================

        # ==========================================
        # CREAR BOTÓN CANCELAR EN EL FRAME DE RESULTADOS
        # ==========================================
        self.btn_cancelar = QPushButton("Cancelar", self.ui.frame_resultados)
        self.btn_cancelar.setGeometry(650, 40, 100, 25) # Lo ponemos a la derecha de la barra
        self.btn_cancelar.setStyleSheet("background-color: #ff4c4c; color: white; font-weight: bold;")
        self.btn_cancelar.clicked.connect(self.cancelar_proceso)
        self.btn_cancelar.hide() # Lo ocultamos al principio
        # ==========================================

        # Hide rpyc_renpy
        self.ui.chk_rpyc_renpy.hide()

        self.ui.tabWidget.setCurrentWidget(self.ui.tab_inicio)

        # Cambiar el título de la ventana
        self.setWindowTitle("Extracción Media Juegos")
        # Hacer que la ventana no se pueda redimensionar
        self.setFixedSize(self.size())

        # Ocultar frame de resultados al inicio
        self.ui.frame_resultados.setVisible(False)
        self.ui.groupBox_tcopia_renpy.setVisible(False)
        self.ui.groupBox_tipoCopia_html.setVisible(False)
        self.ui.groupBox_tipoCopia_rpgm.setVisible(False)
        self.ui.groupBox_tipoCopia_unity.setVisible(False)

        # Conectar los botones "Seleccionar" a la función select_directory
        self._setup_directory_selectors()
        self._setup_directory_selector()

        # Conectar los checkboxes "Seleccionar todo" a la función toggle_all_checkboxes
        self._setup_checkbox_selectors()

        # Conectar la validación del botón "Iniciar"
        self._setup_renpy_button_validation()
        self.validate_renpy_start_button()
        self.ui.btn_inicio_renpy.clicked.connect(self.on_btn_inicio_renpy_clicked)

        self._setup_html_button_validation()
        self.validate_html_start_button()
        self.ui.btn_inicio_html.clicked.connect(self.on_btn_inicio_html_clicked)

        self._setup_rpgm_button_validation()
        self.validate_rpgm_start_button()
        self.ui.btn_inicio_rpgm.clicked.connect(self.on_btn_inicio_rpgm_clicked)

        self._setup_unity_button_validation()
        self.validate_unity_start_button()
        self.ui.btn_inicio_unity.clicked.connect(self.on_btn_inicio_unity_clicked)

        self._setup_multimedia_button_validation()
        self.validate_multimedia_start_button()
        self.ui.btn_inicio_multimedia.clicked.connect(self.on_btn_inicio_multimedia_clicked)

        self._setup_directorios_button_validation()
        self.validate_directorios_start_button()
        self.ui.btn_inicio_directorios.clicked.connect(self.on_btn_inicio_directorios_clicked)

        self._setup_descargas_button_validation()
        self.validate_descargas_start_button()
        self.ui.btn_inicio_descargas.clicked.connect(self.on_btn_inicio_descargas_clicked)

    def select_directory(self, line_edit):
        """Abre un cuadro de diálogo para seleccionar un directorio y lo muestra en un QLineEdit."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar directorio")
        if directory:
            line_edit.setText(directory)

    def on_btn_inicio_renpy_clicked(self):
        if not self.validate_destination_directory_renpy():
            return

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_renpy.text().strip()
        destino = self.ui.it_destino_renpy.text().strip()
        tipo_directorio = "único" if self.ui.rb_dir_unico_renpy.isChecked() else "múltiple"

        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_rpyc_renpy.isChecked(): opciones.append("rpyc")
        if self.ui.chk_rpa_renpy.isChecked(): opciones.append("rpa")
        if self.ui.chk_video_renpy.isChecked(): opciones.append("video")
        if self.ui.chk_music_renpy.isChecked(): opciones.append("audio")
        if self.ui.chk_img_renpy.isChecked(): opciones.append("image")
        if self.ui.chk_sources_renpy.isChecked(): opciones.append("font")

        # --- AQUÍ CONECTAMOS EL ANTI-COLGADOR ---

        # 1. Preparamos la interfaz
        self.ui.frame_resultados.setVisible(True)     # Mostramos la barra de progreso
        self.ui.btn_inicio_renpy.setEnabled(False)    # Bloqueamos el botón Iniciar
        self.ui.groupBox_dirs_renpy.setEnabled(False)
        self.ui.groupBox_actions_renpy.setEnabled(False)
        self.ui.groupBox_tcopia_renpy.setEnabled(False)
        self.ui.widget_dirs_renpy.setEnabled(False)
        self.ui.btn_inicio_renpy.hide()               # Escondemos iniciar

        self.plainTextEdit_log.clear()                # Limpiamos el panel
        self.ui.progressBar.setValue(0)               # Reseteamos la barra
        self.ui.statusTextLabel.setText("Procesando...")
        self.btn_cancelar.setEnabled(True)
        self.btn_cancelar.show()

        # Cambiamos la vista automáticamente a la pestaña del Log
        self.ui.tabWidget.setCurrentWidget(self.ui.tab_log)

        # 2. Creamos al trabajador
        self.worker_renpy = WorkerRenpy(origen, destino, tipo_directorio, opciones)

        # 3. Conectamos sus señales a nuestras funciones de interfaz
        self.worker_renpy.senal_log.connect(self.escribir_en_log)
        self.worker_renpy.senal_progreso.connect(self.actualizar_barra)
        self.worker_renpy.finished.connect(self.proceso_terminado_renpy)

        # 4. ¡A trabajar en segundo plano!
        self.worker_renpy.start()

    def validate_destination_directory_renpy(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
        checkboxes = [
            self.ui.chk_video_renpy,
            self.ui.chk_music_renpy,
            self.ui.chk_img_renpy,
            self.ui.chk_sources_renpy
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_destination_dir = bool(self.ui.it_destino_renpy.text().strip())

        if has_checked_checkbox and not has_destination_dir:
            reply = QMessageBox.question(
                self,
                "Directorio de destino vacío",
                "No ha ingresado un directorio de destino. ¿Desea continuar sin destino?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes

        return True

# Funciones Configuracion Btn HTML.
    def _setup_html_button_validation(self):
        self.ui.it_origen_html.textChanged.connect(self.validate_html_start_button)
        checkboxes = [
            self.ui.chk_video_html,
            self.ui.chk_music_html,
            self.ui.chk_img_html,
            self.ui.chk_sources_html,
            self.ui.chk_all_html
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_html_start_button)
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_html_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_html_start_button)

    def validate_html_start_button(self):
        has_origin_dir = bool(self.ui.it_origen_html.text().strip())
        checkboxes = [
            self.ui.chk_video_html,
            self.ui.chk_music_html,
            self.ui.chk_img_html,
            self.ui.chk_sources_html,
            self.ui.chk_all_html
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_selected_radio = self.ui.rb_dir_unico_html.isChecked() or self.ui.rb_dir_multiple_html.isChecked()
        self.ui.btn_inicio_html.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)

    def validate_destination_directory_html(self):
        checkboxes = [
            self.ui.chk_video_html,
            self.ui.chk_music_html,
            self.ui.chk_img_html,
            self.ui.chk_sources_html
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_destination_dir = bool(self.ui.it_destino_html.text().strip())

        if has_checked_checkbox and not has_destination_dir:
            reply = QMessageBox.question(
                self,
                "Directorio de destino vacío",
                "No ha ingresado un directorio de destino. ¿Desea continuar sin destino?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def on_btn_inicio_html_clicked(self):
        if not self.validate_destination_directory_html(): return
        origen = self.ui.it_origen_html.text().strip()
        destino = self.ui.it_destino_html.text().strip()
        tipo_directorio = "único" if self.ui.rb_dir_unico_html.isChecked() else "múltiple"
        opciones = []
        if self.ui.chk_video_html.isChecked(): opciones.append("video")
        if self.ui.chk_music_html.isChecked(): opciones.append("music")
        if self.ui.chk_img_html.isChecked(): opciones.append("img")
        if self.ui.chk_sources_html.isChecked(): opciones.append("sources")

        procesar_html(origen, destino, tipo_directorio, opciones)
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn RPGM.
    def _setup_rpgm_button_validation(self):
        self.ui.it_origen_rpgm.textChanged.connect(self.validate_rpgm_start_button)
        checkboxes = [
            self.ui.chk_video_rpgm,
            self.ui.chk_music_rpgm,
            self.ui.chk_img_rpgm,
            self.ui.chk_sources_rpgm,
            self.ui.chk_all_rpgm
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_rpgm_start_button)
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_rpgm_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_rpgm_start_button)

    def validate_rpgm_start_button(self):
        has_origin_dir = bool(self.ui.it_origen_rpgm.text().strip())
        checkboxes = [
            self.ui.chk_video_rpgm,
            self.ui.chk_music_rpgm,
            self.ui.chk_img_rpgm,
            self.ui.chk_sources_rpgm,
            self.ui.chk_all_rpgm
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_selected_radio = self.ui.rb_dir_unico_rpgm.isChecked() or self.ui.rb_dir_multiple_rpgm.isChecked()
        self.ui.btn_inicio_rpgm.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)

    def validate_destination_directory_rpgm(self):
        checkboxes = [
            self.ui.chk_video_rpgm,
            self.ui.chk_music_rpgm,
            self.ui.chk_img_rpgm,
            self.ui.chk_sources_rpgm
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_destination_dir = bool(self.ui.it_destino_rpgm.text().strip())

        if has_checked_checkbox and not has_destination_dir:
            reply = QMessageBox.question(
                self,
                "Directorio de destino vacío",
                "No ha ingresado un directorio de destino. ¿Desea continuar sin destino?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def on_btn_inicio_rpgm_clicked(self):
        if not self.validate_destination_directory_rpgm(): return
        origen = self.ui.it_origen_rpgm.text().strip()
        destino = self.ui.it_destino_rpgm.text().strip()
        tipo_directorio = "único" if self.ui.rb_dir_unico_rpgm.isChecked() else "múltiple"
        opciones = []
        if self.ui.chk_video_rpgm.isChecked(): opciones.append("video")
        if self.ui.chk_music_rpgm.isChecked(): opciones.append("music")
        if self.ui.chk_img_rpgm.isChecked(): opciones.append("img")
        if self.ui.chk_sources_rpgm.isChecked(): opciones.append("sources")

        procesar_rpgm(origen, destino, tipo_directorio, opciones)
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Unity.
    def _setup_unity_button_validation(self):
        self.ui.it_origen_unity.textChanged.connect(self.validate_unity_start_button)
        checkboxes = [
            self.ui.chk_video_unity,
            self.ui.chk_music_unity,
            self.ui.chk_img_unity,
            self.ui.chk_sources_unity,
            self.ui.chk_all_unity
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_unity_start_button)
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_unity_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_unity_start_button)

    def validate_unity_start_button(self):
        has_origin_dir = bool(self.ui.it_origen_unity.text().strip())
        checkboxes = [
            self.ui.chk_video_unity,
            self.ui.chk_music_unity,
            self.ui.chk_img_unity,
            self.ui.chk_sources_unity,
            self.ui.chk_all_unity
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_selected_radio = self.ui.rb_dir_unico_unity.isChecked() or self.ui.rb_dir_multiple_unity.isChecked()
        self.ui.btn_inicio_unity.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)

    def validate_destination_directory_unity(self):
        checkboxes = [
            self.ui.chk_video_unity,
            self.ui.chk_music_unity,
            self.ui.chk_img_unity,
            self.ui.chk_sources_unity
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_destination_dir = bool(self.ui.it_destino_unity.text().strip())

        if has_checked_checkbox and not has_destination_dir:
            reply = QMessageBox.question(
                self,
                "Directorio de destino vacío",
                "No ha ingresado un directorio de destino. ¿Desea continuar sin destino?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def on_btn_inicio_unity_clicked(self):
        if not self.validate_destination_directory_unity(): return
        origen = self.ui.it_origen_unity.text().strip()
        destino = self.ui.it_destino_unity.text().strip()
        tipo_directorio = "único" if self.ui.rb_dir_unico_unity.isChecked() else "múltiple"
        opciones = []
        if self.ui.chk_video_unity.isChecked(): opciones.append("video")
        if self.ui.chk_music_unity.isChecked(): opciones.append("music")
        if self.ui.chk_img_unity.isChecked(): opciones.append("img")
        if self.ui.chk_sources_unity.isChecked(): opciones.append("sources")

        procesar_unity(origen, destino, tipo_directorio, opciones)
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Multimedia.
    def _setup_multimedia_button_validation(self):
        self.ui.it_origen_multimedia.textChanged.connect(self.validate_multimedia_start_button)
        checkboxes = [
            self.ui.chk_video_multimedia,
            self.ui.chk_music_multimedia,
            self.ui.chk_img_multimedia,
            self.ui.chk_sources_multimedia,
            self.ui.chk_all_multimedia
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_multimedia_start_button)
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_multimedia_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_multimedia_start_button)
        self.ui.rb_tcopia_organizada_multimedia.toggled.connect(self.validate_multimedia_start_button)
        self.ui.rb_tcopia_directa_multimedia.toggled.connect(self.validate_multimedia_start_button)

    def validate_multimedia_start_button(self):
        has_origin_dir = bool(self.ui.it_origen_multimedia.text().strip())
        checkboxes = [
            self.ui.chk_video_multimedia,
            self.ui.chk_music_multimedia,
            self.ui.chk_img_multimedia,
            self.ui.chk_sources_multimedia,
            self.ui.chk_all_multimedia
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_selected_radio = self.ui.rb_dir_unico_multimedia.isChecked() or self.ui.rb_dir_multiple_multimedia.isChecked()
        has_selected_radio_tipo = self.ui.rb_tcopia_organizada_multimedia.isChecked() or self.ui.rb_tcopia_directa_multimedia.isChecked()
        self.ui.btn_inicio_multimedia.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio and has_selected_radio_tipo)

    def validate_destination_directory_multimedia(self):
        checkboxes = [
            self.ui.chk_video_multimedia,
            self.ui.chk_music_multimedia,
            self.ui.chk_img_multimedia,
            self.ui.chk_sources_multimedia
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_destination_dir = bool(self.ui.it_destino_multimedia.text().strip())

        if has_checked_checkbox and not has_destination_dir:
            reply = QMessageBox.question(
                self,
                "Directorio de destino vacío",
                "No ha ingresado un directorio de destino. ¿Desea continuar sin destino?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def on_btn_inicio_multimedia_clicked(self):
        if not self.validate_destination_directory_multimedia(): return
        origen = self.ui.it_origen_multimedia.text().strip()
        destino = self.ui.it_destino_multimedia.text().strip()
        tipo_directorio = "único" if self.ui.rb_dir_unico_multimedia.isChecked() else "múltiple"
        tipo_copia = "directa" if self.ui.rb_tcopia_directa_multimedia.isChecked() else "organizada"
        opciones = []
        if self.ui.chk_video_multimedia.isChecked(): opciones.append("video")
        if self.ui.chk_music_multimedia.isChecked(): opciones.append("music")
        if self.ui.chk_img_multimedia.isChecked(): opciones.append("img")
        if self.ui.chk_sources_multimedia.isChecked(): opciones.append("sources")

        procesar_multimedia(origen, destino, tipo_directorio, opciones, tipo_copia)
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Directorios.
    def _setup_directorios_button_validation(self):
        self.ui.it_origen_directorios.textChanged.connect(self.validate_directorios_start_button)
        checkboxes = [
            self.ui.chk_listar_directorios,
            self.ui.chk_lista_completa_directorios,
            self.ui.chk_empity_directorios,
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_directorios_start_button)

    def validate_directorios_start_button(self):
        has_origin_dir = bool(self.ui.it_origen_directorios.text().strip())
        checkboxes = [
            self.ui.chk_listar_directorios,
            self.ui.chk_lista_completa_directorios,
            self.ui.chk_empity_directorios,
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        self.ui.btn_inicio_directorios.setEnabled(has_origin_dir and has_checked_checkbox)

    def validate_destination_directory_directorios(self):
        checkboxes = [
            self.ui.chk_listar_directorios,
            self.ui.chk_lista_completa_directorios,
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)
        has_destination_dir = bool(self.ui.it_destino_directorios.text().strip())

        if has_checked_checkbox and not has_destination_dir:
            reply = QMessageBox.question(
                self,
                "Directorio de destino vacío",
                "No ha ingresado un directorio de destino. ¿Desea continuar sin destino?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            return reply == QMessageBox.Yes
        return True

    def on_btn_inicio_directorios_clicked(self):
        if not self.validate_destination_directory_directorios(): return
        origen = self.ui.it_origen_directorios.text().strip()
        destino = self.ui.it_destino_directorios.text().strip()
        opciones = []
        if self.ui.chk_listar_directorios.isChecked(): opciones.append("lista")
        if self.ui.chk_lista_completa_directorios.isChecked(): opciones.append("lista_completa")
        if self.ui.chk_empity_directorios.isChecked(): opciones.append("eliminar_directorios_vacios")

        procesar_directorios(origen, destino, opciones)
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Descargas.
    def _setup_descargas_button_validation(self):
        self.ui.it_destino_descargas.textChanged.connect(self.validate_descargas_start_button)
        self.ui.textEdit_descargas.textChanged.connect(self.validate_descargas_start_button)
        self.ui.rb_yt_descargas.toggled.connect(self.validate_descargas_start_button)
        self.ui.rb_img_descargas.toggled.connect(self.validate_descargas_start_button)

    def validate_descargas_start_button(self):
        has_content_in_textedit = bool(self.ui.textEdit_descargas.toPlainText().strip())
        has_destination_dir = bool(self.ui.it_destino_descargas.text().strip())
        has_checked_radiobutton = self.ui.rb_yt_descargas.isChecked() or self.ui.rb_img_descargas.isChecked()
        self.ui.btn_inicio_descargas.setEnabled(has_content_in_textedit and has_destination_dir and has_checked_radiobutton)

    def validate_destination_directory_descargas(self):
        has_destination_dir = bool(self.ui.it_destino_descargas.text().strip())
        if not has_destination_dir:
            QMessageBox.warning(self, "Error de destino", "Debe ingresar un directorio de destino para continuar.", QMessageBox.Ok)
            return False
        return True

    def on_btn_inicio_descargas_clicked(self):
        if not self.validate_destination_directory_descargas(): return
        origen = self.ui.textEdit_descargas.toPlainText().strip()
        destino = self.ui.it_destino_descargas.text().strip()
        opciones = []
        if self.ui.rb_yt_descargas.isChecked(): opciones.append("utube")
        elif self.ui.rb_img_descargas.isChecked(): opciones.append("img")

        procesar_descargas(origen, destino, opciones)
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Utilidades Generales
    def _setup_directory_selectors(self):
        directories = [
            (self.ui.it_origen_renpy, self.ui.it_destino_renpy),
            (self.ui.it_origen_html, self.ui.it_destino_html),
            (self.ui.it_origen_rpgm, self.ui.it_destino_rpgm),
            (self.ui.it_origen_unity, self.ui.it_destino_unity),
            (self.ui.it_origen_multimedia, self.ui.it_destino_multimedia),
            (self.ui.it_origen_directorios, self.ui.it_destino_directorios)
        ]
        for origin, destination in directories:
            origin.mousePressEvent = lambda event, le=origin: self.select_directory(le)
            destination.mousePressEvent = lambda event, le=destination: self.select_directory(le)

    def _setup_directory_selector(self):
        directories = [self.ui.it_destino_descargas]
        for destination in directories:
            destination.mousePressEvent = lambda event, le=destination: self.select_directory(le)

    def _setup_checkbox_selectors(self):
        checkboxes_dict = {
            'multimedia': [self.ui.chk_video_multimedia, self.ui.chk_music_multimedia, self.ui.chk_img_multimedia, self.ui.chk_sources_multimedia],
            'unity': [self.ui.chk_video_unity, self.ui.chk_music_unity, self.ui.chk_img_unity, self.ui.chk_sources_unity],
            'rpgm': [self.ui.chk_video_rpgm, self.ui.chk_music_rpgm, self.ui.chk_img_rpgm, self.ui.chk_sources_rpgm],
            'html': [self.ui.chk_video_html, self.ui.chk_music_html, self.ui.chk_img_html, self.ui.chk_sources_html],
            'renpy': [self.ui.chk_video_renpy, self.ui.chk_music_renpy, self.ui.chk_img_renpy, self.ui.chk_sources_renpy],
        }
        for checkbox, checkboxes in checkboxes_dict.items():
            getattr(self.ui, f'chk_all_{checkbox}').stateChanged.connect(lambda state, checkboxes=checkboxes: self.toggle_all_checkboxes(state, checkboxes))

    def toggle_all_checkboxes(self, state, checkboxes):
        checked = state == 2  # 2 es Qt.Checked
        for checkbox in checkboxes:
            checkbox.blockSignals(True)
            checkbox.setChecked(checked)
            checkbox.blockSignals(False)

    def show_alert(self, title, message, icon=QMessageBox.Information):
        """Muestra un mensaje de alerta usando QMessageBox."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    # ==========================================
    # RECEPTORES DE SEÑALES (Actualizan la UI)
    # ==========================================
    def cancelar_proceso(self):
        """Función que se dispara al pulsar el botón Cancelar"""
        if hasattr(self, 'worker_renpy') and self.worker_renpy.isRunning():
            self.plainTextEdit_log.appendPlainText("\n⚠️ Solicitando cancelación... por favor espere.")
            self.worker_renpy.cancelar()
            self.btn_cancelar.setEnabled(False) # Evitar que hagan spam de clics

    def escribir_en_log(self, mensaje):
        """Recibe texto del Worker y lo escribe en el panel negro"""
        self.plainTextEdit_log.appendPlainText(mensaje)

    def actualizar_barra(self, actual, total):
        """Recibe los números del Worker y mueve la barra"""
        self.ui.progressBar.setMaximum(total)
        self.ui.progressBar.setValue(actual)
        self.ui.statusTextLabel.setText(f"Copiando... {actual} de {total}")

    def proceso_terminado_renpy(self):
        """Se activa solo cuando el Worker termina"""
        # 1. DESBLOQUEAR LA INTERFAZ
        self.ui.groupBox_dirs_renpy.setEnabled(True)
        self.ui.groupBox_actions_renpy.setEnabled(True)
        self.ui.groupBox_tcopia_renpy.setEnabled(True)
        self.ui.widget_dirs_renpy.setEnabled(True)

        # 2. RESTAURAR BOTONES
        self.ui.btn_inicio_renpy.setEnabled(True)
        self.ui.btn_inicio_renpy.show()
        self.btn_cancelar.hide()

        self.ui.statusTextLabel.setText("Finalizado.")
        self.show_alert("Proceso completado", "El procesamiento ha finalizado.")


# Funciones Configuracion Btn Renpy.
    def _setup_renpy_button_validation(self):
        """Configura las conexiones para la validación del botón de inicio Ren'Py."""
        # Monitoriza el campo de entrada del directorio origen
        self.ui.it_origen_renpy.textChanged.connect(self.validate_renpy_start_button)

        # Lista de checkboxes relevantes
        checkboxes = [
            self.ui.chk_rpyc_renpy,
            self.ui.chk_rpa_renpy,
            self.ui.chk_video_renpy,
            self.ui.chk_music_renpy,
            self.ui.chk_img_renpy,
            self.ui.chk_sources_renpy,
            self.ui.chk_all_renpy
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_renpy_start_button)

        # Monitoriza los radio buttons
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_renpy_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_renpy_start_button)

    def validate_renpy_start_button(self):
        # Verificar si el campo de origen tiene texto
        """Habilita o deshabilita el botón de inicio de Ren'Py basado en las condiciones dadas."""
        origen = self.ui.it_origen_renpy.text().strip()

        # Verificar si el campo de origen tiene texto y si el directorio existe
        has_origin_dir = bool(origen) and os.path.isdir(origen)

        # Verificar si al menos un checkbox está marcado
        checkboxes = [
            self.ui.chk_rpyc_renpy,
            self.ui.chk_rpa_renpy,
            self.ui.chk_video_renpy,
            self.ui.chk_music_renpy,
            self.ui.chk_img_renpy,
            self.ui.chk_sources_renpy,
            self.ui.chk_all_renpy
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)

        # Verificar si al menos un radio button está marcado
        has_selected_radio = self.ui.rb_dir_unico_renpy.isChecked() or self.ui.rb_dir_multiple_renpy.isChecked()

        # Habilitar el botón si todas las condiciones se cumplen
        self.ui.btn_inicio_renpy.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())