import sys, os
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from ui.main_view import Ui_MainWindow
from PySide6.QtCore import Qt
from funciones.procesador import procesar_renpy, procesar_html, procesar_rpgm, procesar_unity, procesar_multimedia, procesar_directorios, procesar_descargas

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        index = self.ui.tabWidget.indexOf(self.ui.tab_log)
        self.ui.tabWidget.removeTab(index)

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
        # self.ui.groupBox_tipoCopia_directorios.setVisible(False)


        # Conectar los botones "Seleccionar" a la función select_directory
        self._setup_directory_selectors()
        self._setup_directory_selector()


        # Conectar los checkboxes "Seleccionar todo" a la función toggle_all_checkboxes
        self._setup_checkbox_selectors()

        # Conectar la validación del botón "Iniciar"
        # Agregado para inicializar las validaciones
        self._setup_renpy_button_validation()
        # Asegurar estado inicial del botón
        self.validate_renpy_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_renpy.clicked.connect(self.on_btn_inicio_renpy_clicked)

        # Agregado para inicializar las validaciones
        self._setup_html_button_validation()
        # Asegurar estado inicial del botón
        self.validate_html_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_html.clicked.connect(self.on_btn_inicio_html_clicked)

        # Agregado para inicializar las validaciones
        self._setup_rpgm_button_validation()
        # Asegurar estado inicial del botón
        self.validate_rpgm_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_rpgm.clicked.connect(self.on_btn_inicio_rpgm_clicked)

        # Agregado para inicializar las validaciones
        self._setup_unity_button_validation()
        # Asegurar estado inicial del botón
        self.validate_unity_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_unity.clicked.connect(self.on_btn_inicio_unity_clicked)

        # Agregado para inicializar las validaciones
        self._setup_multimedia_button_validation()
        # Asegurar estado inicial del botón
        self.validate_multimedia_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_multimedia.clicked.connect(self.on_btn_inicio_multimedia_clicked)

        # Agregado para inicializar las validaciones
        self._setup_directorios_button_validation()
        # Asegurar estado inicial del botón
        self.validate_directorios_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_directorios.clicked.connect(self.on_btn_inicio_directorios_clicked)


        # Agregado para inicializar las validaciones
        self._setup_descargas_button_validation()
        # Asegurar estado inicial del botón
        self.validate_descargas_start_button()
        # Conectar el botón "Iniciar" a su acción
        self.ui.btn_inicio_descargas.clicked.connect(self.on_btn_inicio_descargas_clicked)







    def select_directory(self, line_edit):
        """Abre un cuadro de diálogo para seleccionar un directorio y lo muestra en un QLineEdit."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar directorio")
        if directory:
            line_edit.setText(directory)

# Configuraciones iniciales.
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

# Configuraciones iniciales.
    def _setup_directory_selector(self):
        directories = [
            self.ui.it_destino_descargas,
        ]
        for destination in directories:
            destination.mousePressEvent = lambda event, le=destination: self.select_directory(le)


    def _setup_checkbox_selectors(self):
        checkboxes_dict = {
            # 'directorios': [self.ui.chk_video_directorios, self.ui.chk_listar_directorios, self.ui.chk_all_directorios, self.ui.chk_sources_directorios],
            'multimedia': [self.ui.chk_video_multimedia, self.ui.chk_music_multimedia, self.ui.chk_img_multimedia, self.ui.chk_sources_multimedia],
            'unity': [self.ui.chk_video_unity, self.ui.chk_music_unity, self.ui.chk_img_unity, self.ui.chk_sources_unity],
            'rpgm': [self.ui.chk_video_rpgm, self.ui.chk_music_rpgm, self.ui.chk_img_rpgm, self.ui.chk_sources_rpgm],
            'html': [self.ui.chk_video_html, self.ui.chk_music_html, self.ui.chk_img_html, self.ui.chk_sources_html],
            'renpy': [self.ui.chk_video_renpy, self.ui.chk_music_renpy, self.ui.chk_img_renpy, self.ui.chk_sources_renpy],
        }

        for checkbox, checkboxes in checkboxes_dict.items():
            getattr(self.ui, f'chk_all_{checkbox}').stateChanged.connect(lambda state, checkboxes=checkboxes: self.toggle_all_checkboxes(state, checkboxes))

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

    def on_btn_inicio_renpy_clicked(self):
        if not self.validate_destination_directory_renpy():
            return  # Si el usuario elige "No", se cancela la ejecución

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_renpy.text().strip()
        destino = self.ui.it_destino_renpy.text().strip()

        # Determinamos el tipo de directorio
        tipo_directorio = "único" if self.ui.rb_dir_unico_renpy.isChecked() else "múltiple"
        # tipo_directorio = "único" if self.ui.rb_dir_unico_renpy.isChecked() else "múltiple"

        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_rpyc_renpy.isChecked():
            opciones.append("rpyc")
        if self.ui.chk_rpa_renpy.isChecked():
            opciones.append("rpa")
        if self.ui.chk_video_renpy.isChecked():
            opciones.append("video")
        if self.ui.chk_music_renpy.isChecked():
            opciones.append("music")
        if self.ui.chk_img_renpy.isChecked():
            opciones.append("img")
        if self.ui.chk_sources_renpy.isChecked():
            opciones.append("sources")

        # Llamamos a la función externa pasando los datos
        procesar_renpy(origen, destino, tipo_directorio, opciones)

        # Mostramos una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

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
        """Configura las conexiones para la validación del botón de inicio Ren'Py."""
        # Monitoriza el campo de entrada del directorio origen
        self.ui.it_origen_html.textChanged.connect(self.validate_html_start_button)

        # Lista de checkboxes relevantes
        checkboxes = [
            self.ui.chk_video_html,
            self.ui.chk_music_html,
            self.ui.chk_img_html,
            self.ui.chk_sources_html,
            self.ui.chk_all_html
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_html_start_button)

        # Monitoriza los radio buttons
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_html_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_html_start_button)

    def validate_html_start_button(self):
        """Habilita o deshabilita el botón de inicio de Ren'Py basado en las condiciones dadas."""
        # Verificar si el campo de origen tiene texto
        has_origin_dir = bool(self.ui.it_origen_html.text().strip())

        # Verificar si al menos un checkbox está marcado
        checkboxes = [
            self.ui.chk_video_html,
            self.ui.chk_music_html,
            self.ui.chk_img_html,
            self.ui.chk_sources_html,
            self.ui.chk_all_html
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)

        # Verificar si al menos un radio button está marcado
        has_selected_radio = self.ui.rb_dir_unico_html.isChecked() or self.ui.rb_dir_multiple_html.isChecked()

        # Habilitar el botón si todas las condiciones se cumplen
        self.ui.btn_inicio_html.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)

    def validate_destination_directory_html(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
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
        if not self.validate_destination_directory_html():
            return  # Si el usuario elige "No", se cancela la ejecución

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_html.text().strip()
        destino = self.ui.it_destino_html.text().strip()

        # Determinamos el tipo de directorio
        tipo_directorio = "único" if self.ui.rb_dir_unico_html.isChecked() else "múltiple"

        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_video_html.isChecked():
            opciones.append("video")
        if self.ui.chk_music_html.isChecked():
            opciones.append("music")
        if self.ui.chk_img_html.isChecked():
            opciones.append("img")
        if self.ui.chk_sources_html.isChecked():
            opciones.append("sources")

        # Llamamos a la función externa pasando los datos
        procesar_html(origen, destino, tipo_directorio, opciones)

        # Mostramos una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn RPGM.
    def _setup_rpgm_button_validation(self):
        """Configura las conexiones para la validación del botón de inicio Ren'Py."""
        # Monitoriza el campo de entrada del directorio origen
        self.ui.it_origen_rpgm.textChanged.connect(self.validate_rpgm_start_button)

        # Lista de checkboxes relevantes
        checkboxes = [
            self.ui.chk_video_rpgm,
            self.ui.chk_music_rpgm,
            self.ui.chk_img_rpgm,
            self.ui.chk_sources_rpgm,
            self.ui.chk_all_rpgm
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_rpgm_start_button)

        # Monitoriza los radio buttons
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_rpgm_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_rpgm_start_button)

    def validate_rpgm_start_button(self):
        """Habilita o deshabilita el botón de inicio de Ren'Py basado en las condiciones dadas."""
        # Verificar si el campo de origen tiene texto
        has_origin_dir = bool(self.ui.it_origen_rpgm.text().strip())

        # Verificar si al menos un checkbox está marcado
        checkboxes = [
            self.ui.chk_video_rpgm,
            self.ui.chk_music_rpgm,
            self.ui.chk_img_rpgm,
            self.ui.chk_sources_rpgm,
            self.ui.chk_all_rpgm
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)

        # Verificar si al menos un radio button está marcado
        has_selected_radio = self.ui.rb_dir_unico_rpgm.isChecked() or self.ui.rb_dir_multiple_rpgm.isChecked()

        # Habilitar el botón si todas las condiciones se cumplen
        self.ui.btn_inicio_rpgm.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)

    def validate_destination_directory_rpgm(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
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
        if not self.validate_destination_directory_rpgm():
            return  # Si el usuario elige "No", se cancela la ejecución

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_rpgm.text().strip()
        destino = self.ui.it_destino_rpgm.text().strip()

        # Determinamos el tipo de directorio
        tipo_directorio = "único" if self.ui.rb_dir_unico_rpgm.isChecked() else "múltiple"

        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_video_rpgm.isChecked():
            opciones.append("video")
        if self.ui.chk_music_rpgm.isChecked():
            opciones.append("music")
        if self.ui.chk_img_rpgm.isChecked():
            opciones.append("img")
        if self.ui.chk_sources_rpgm.isChecked():
            opciones.append("sources")

        # Llamamos a la función externa pasando los datos
        procesar_rpgm(origen, destino, tipo_directorio, opciones)

        # Mostramos una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Unity.
    def _setup_unity_button_validation(self):
        """Configura las conexiones para la validación del botón de inicio Ren'Py."""
        # Monitoriza el campo de entrada del directorio origen
        self.ui.it_origen_unity.textChanged.connect(self.validate_unity_start_button)

        # Lista de checkboxes relevantes
        checkboxes = [
            self.ui.chk_video_unity,
            self.ui.chk_music_unity,
            self.ui.chk_img_unity,
            self.ui.chk_sources_unity,
            self.ui.chk_all_unity
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_unity_start_button)

        # Monitoriza los radio buttons
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_unity_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_unity_start_button)

    def validate_unity_start_button(self):
        """Habilita o deshabilita el botón de inicio de Ren'Py basado en las condiciones dadas."""
        # Verificar si el campo de origen tiene texto
        has_origin_dir = bool(self.ui.it_origen_unity.text().strip())

        # Verificar si al menos un checkbox está marcado
        checkboxes = [
            self.ui.chk_video_unity,
            self.ui.chk_music_unity,
            self.ui.chk_img_unity,
            self.ui.chk_sources_unity,
            self.ui.chk_all_unity
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)

        # Verificar si al menos un radio button está marcado
        has_selected_radio = self.ui.rb_dir_unico_unity.isChecked() or self.ui.rb_dir_multiple_unity.isChecked()

        # Habilitar el botón si todas las condiciones se cumplen
        self.ui.btn_inicio_unity.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio)

    def validate_destination_directory_unity(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
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
        if not self.validate_destination_directory_unity():
            return  # Si el usuario elige "No", se cancela la ejecución

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_unity.text().strip()
        destino = self.ui.it_destino_unity.text().strip()

        # Determinamos el tipo de directorio
        tipo_directorio = "único" if self.ui.rb_dir_unico_unity.isChecked() else "múltiple"

        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_video_unity.isChecked():
            opciones.append("video")
        if self.ui.chk_music_unity.isChecked():
            opciones.append("music")
        if self.ui.chk_img_unity.isChecked():
            opciones.append("img")
        if self.ui.chk_sources_unity.isChecked():
            opciones.append("sources")

        # Llamamos a la función externa pasando los datos
        procesar_unity(origen, destino, tipo_directorio, opciones)

        # Mostramos una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Multimedia.
    def _setup_multimedia_button_validation(self):
        """Configura las conexiones para la validación del botón de inicio Ren'Py."""
        # Monitoriza el campo de entrada del directorio origen
        self.ui.it_origen_multimedia.textChanged.connect(self.validate_multimedia_start_button)

        # Lista de checkboxes relevantes
        checkboxes = [
            self.ui.chk_video_multimedia,
            self.ui.chk_music_multimedia,
            self.ui.chk_img_multimedia,
            self.ui.chk_sources_multimedia,
            self.ui.chk_all_multimedia
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_multimedia_start_button)

        # Monitoriza los radio buttons
        self.ui.rb_dir_unico_renpy.toggled.connect(self.validate_multimedia_start_button)
        self.ui.rb_dir_multiple_renpy.toggled.connect(self.validate_multimedia_start_button)
        self.ui.rb_tcopia_organizada_multimedia.toggled.connect(self.validate_multimedia_start_button)
        self.ui.rb_tcopia_directa_multimedia.toggled.connect(self.validate_multimedia_start_button)

    def validate_multimedia_start_button(self):
        """Habilita o deshabilita el botón de inicio de Ren'Py basado en las condiciones dadas."""
        # Verificar si el campo de origen tiene texto
        has_origin_dir = bool(self.ui.it_origen_multimedia.text().strip())

        # Verificar si al menos un checkbox está marcado
        checkboxes = [
            self.ui.chk_video_multimedia,
            self.ui.chk_music_multimedia,
            self.ui.chk_img_multimedia,
            self.ui.chk_sources_multimedia,
            self.ui.chk_all_multimedia
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)

        # Verificar si al menos un radio button está marcado
        has_selected_radio = self.ui.rb_dir_unico_multimedia.isChecked() or self.ui.rb_dir_multiple_multimedia.isChecked()
        has_selected_radio_tipo = self.ui.rb_tcopia_organizada_multimedia.isChecked() or self.ui.rb_tcopia_directa_multimedia.isChecked()

        # Habilitar el botón si todas las condiciones se cumplen
        self.ui.btn_inicio_multimedia.setEnabled(has_origin_dir and has_checked_checkbox and has_selected_radio and has_selected_radio_tipo)

    def validate_destination_directory_multimedia(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
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
        if not self.validate_destination_directory_multimedia():
            return  # Si el usuario elige "No", se cancela la ejecución

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_multimedia.text().strip()
        destino = self.ui.it_destino_multimedia.text().strip()

        # Determinamos el tipo de directorio
        tipo_directorio = "único" if self.ui.rb_dir_unico_multimedia.isChecked() else "múltiple"
        tipo_copia = "directa" if self.ui.rb_tcopia_directa_multimedia.isChecked() else "organizada"

        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_video_multimedia.isChecked():
            opciones.append("video")
        if self.ui.chk_music_multimedia.isChecked():
            opciones.append("music")
        if self.ui.chk_img_multimedia.isChecked():
            opciones.append("img")
        if self.ui.chk_sources_multimedia.isChecked():
            opciones.append("sources")

        # Llamamos a la función externa pasando los datos
        procesar_multimedia(origen, destino, tipo_directorio, opciones, tipo_copia)

        # Mostramos una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")

# Funciones Configuracion Btn Directorios.
    def _setup_directorios_button_validation(self):
        """Configura las conexiones para la validación del botón de inicio Directorios."""
        self.ui.it_origen_directorios.textChanged.connect(self.validate_directorios_start_button)

        # Lista de checkboxes relevantes
        checkboxes = [
            self.ui.chk_listar_directorios,
            self.ui.chk_lista_completa_directorios,
            self.ui.chk_empity_directorios,
        ]
        for checkbox in checkboxes:
            checkbox.stateChanged.connect(self.validate_directorios_start_button)

    def validate_directorios_start_button(self):
        """Habilita o deshabilita el botón de inicio de Ren'Py basado en las condiciones dadas."""
        # Verificar si el campo de origen tiene texto
        has_origin_dir = bool(self.ui.it_origen_directorios.text().strip())

        # Verificar si al menos un checkbox está marcado
        checkboxes = [
            self.ui.chk_listar_directorios,
            self.ui.chk_lista_completa_directorios,
            self.ui.chk_empity_directorios,
        ]
        has_checked_checkbox = any(checkbox.isChecked() for checkbox in checkboxes)

        self.ui.btn_inicio_directorios.setEnabled(has_origin_dir and has_checked_checkbox)

    def validate_destination_directory_directorios(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
        checkboxes = [
            self.ui.chk_listar_directorios,
            self.ui.chk_lista_completa_directorios,
            # self.ui.chk_empity_directorios,
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
        if not self.validate_destination_directory_directorios():
            return  # Si el usuario elige "No", se cancela la ejecución

        # Obtenemos los valores seleccionados
        origen = self.ui.it_origen_directorios.text().strip()
        destino = self.ui.it_destino_directorios.text().strip()

        # Determinamos el tipo de directorio


        # Obtenemos los checkboxes marcados
        opciones = []
        if self.ui.chk_listar_directorios.isChecked():
            opciones.append("lista")
        if self.ui.chk_lista_completa_directorios.isChecked():
            opciones.append("lista_completa")
        if self.ui.chk_empity_directorios.isChecked():
            opciones.append("eliminar_directorios_vacios")

        # Llamamos a la función externa pasando los datos
        procesar_directorios(origen, destino, opciones)

        # Mostramos una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")



# Funciones Configuracion Btn Directorios.
    # Funciones Configuracion Btn Descargas.
    def _setup_descargas_button_validation(self):
        """Configura las conexiones para la validación del botón de inicio Descargas."""
        # Conexiones de texto a campos de destino y links
        self.ui.it_destino_descargas.textChanged.connect(self.validate_descargas_start_button)
        self.ui.textEdit_descargas.textChanged.connect(self.validate_descargas_start_button)

        # Conexiones de RadioButtons
        self.ui.rb_yt_descargas.toggled.connect(self.validate_descargas_start_button)
        self.ui.rb_img_descargas.toggled.connect(self.validate_descargas_start_button)

    def validate_descargas_start_button(self):
        """Habilita o deshabilita el botón de inicio Descargas basado en las condiciones dadas."""

        # Verificar si el QTextEdit tiene contenido (links pegados)
        has_content_in_textedit = bool(self.ui.textEdit_descargas.toPlainText().strip())

        # Verificar si el campo de destino tiene texto
        has_destination_dir = bool(self.ui.it_destino_descargas.text().strip())

        # Verificar si al menos un RadioButton está marcado
        has_checked_radiobutton = self.ui.rb_yt_descargas.isChecked() or self.ui.rb_img_descargas.isChecked()

        # El botón de inicio solo se habilita si:
        # - El QTextEdit tiene contenido.
        # - El campo de destino no está vacío.
        # - Al menos un RadioButton está marcado.
        self.ui.btn_inicio_descargas.setEnabled(
            has_content_in_textedit and has_destination_dir and has_checked_radiobutton
        )

    def validate_destination_directory_descargas(self):
        """Verifica si es necesario mostrar la alerta de directorio destino vacío."""
        # Asegurarse de que se haya ingresado un directorio de destino
        has_checked_radiobutton = self.ui.rb_yt_descargas.isChecked() or self.ui.rb_img_descargas.isChecked()
        has_destination_dir = bool(self.ui.it_destino_descargas.text().strip())

        if not has_destination_dir:  # Si el directorio de destino está vacío
            # Mostrar un mensaje indicando que el directorio de destino es obligatorio
            QMessageBox.warning(
                self,
                "Error de destino",
                "Debe ingresar un directorio de destino para continuar.",
                QMessageBox.Ok
            )
            return False  # No se puede continuar sin un directorio de destino

        return True  # El destino está presente, se puede continuar

    def on_btn_inicio_descargas_clicked(self):
        if not self.validate_destination_directory_descargas():
            return  # Si el directorio de destino no es válido, se cancela la ejecución

        # Obtener el texto de links y destino
        origen = self.ui.textEdit_descargas.toPlainText().strip()
        destino = self.ui.it_destino_descargas.text().strip()

        # Determinar las opciones seleccionadas con los RadioButtons
        opciones = []
        if self.ui.rb_yt_descargas.isChecked():
            opciones.append("utube")  # Tipo de descarga YouTube
        elif self.ui.rb_img_descargas.isChecked():
            opciones.append("img")  # Tipo de descarga Imágenes

        # Llamar a la función externa pasando los datos
        procesar_descargas(origen, destino, opciones)

        # Mostrar una alerta de confirmación
        self.show_alert("Proceso iniciado", "El procesamiento ha comenzado.")











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



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
