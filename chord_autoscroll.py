import sys
import os
import math
import re
import json
import chardet
from PyQt6.QtGui import (QFont, QAction, QActionGroup, QDragEnterEvent, QDropEvent, QTextCursor,
                         QShortcut, QKeySequence)
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout,
                             QWidget, QPushButton, QLabel, QSlider, QFileDialog, QMenuBar,
                             QMenu, QMessageBox, QInputDialog, QFontDialog, QTabWidget)
from PyQt6.QtCore import Qt, QTimer, QUrl, QTranslator, QLocale, QLibraryInfo

class CustomTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)  # Desactivar el manejo de drops por defecto

class TextScrollerApp(QMainWindow):
# Dentro de la clase `TextScrollerApp`
    def show_about_dialog(self):
        about_text = (
            "<h2><b>Chord autoscroll</b></h2>"
            "<p>Este programa sirve para la transposición de acordes, podrás cargar tus canciones que contengan "
            "letras y acordes para transportarlas fácilmente y desplazarte automáticamente por el texto, "
            "para tus ensayos.</p>"
            "<p>Copyright 2025  Washington Indacochea Delgado.<br>"
            "wachin.id@gmail.com<br>"
            "Licencia GPL 3</p>"
            "<p>Para más información revisa:</p>"
            '<a href="https://github.com/wachin/py_chord_autoscroll">https://github.com/wachin/py_chord_autoscroll</a>'
        )

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Acerca de Chord Autoscroll")
        dialog.setTextFormat(Qt.TextFormat.RichText)  # Permitir formato HTML
        dialog.setText(about_text)
        dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
        dialog.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        dialog.exec()

    def __init__(self):
        super().__init__()
        self.translator = QTranslator()

        translations_path = QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)
        print(f"Ruta de traducciones: {translations_path}")  # Depuración

        # Cargar traducción al español
        if self.translator.load("qtbase_es", translations_path):
            QApplication.installTranslator(self.translator)
            print("Traducción al español cargada correctamente.")
        else:
            print("No se pudo cargar la traducción al español.")

        self.setWindowTitle("Lector y Editor de Letras con Acordes")
        self.setGeometry(100, 100, 800, 500)

        self.current_file = None
        self.is_scrolling = False
        self.max_speed = 400  # Velocidad máxima predeterminada
        self.scroll_speed = self.calculate_speed(15)  # Velocidad predeterminada

        self.config_file = 'config12.json'

        self.opened_files = {}  # Diccionario para rutas de archivos
        self.file_encodings = {}  # Diccionario para guardar codificaciones

        # Inicializar configuración antes de usarla
        self.config = {}
        self.load_config()

        # Diccionario para rastrear archivos abiertos en pestañas
        self.opened_files = {}

        self.init_ui()

        # Actualizar el menú "Abrir reciente" después de cargar la configuración
        self.update_recent_files_menu()

    def select_font(self):
        # Abrir diálogo de selección de fuente
        font, ok = QFontDialog.getFont(QFont(self.config.get('font_family', 'Noto Mono'),
                                            self.config.get('font_size', 10)),
                                    self, "Selecciona una fuente")

        # Si el usuario selecciona una fuente y presiona OK
        if ok:
            # Aplicar la fuente seleccionada al área de texto
            current_widget = self.get_current_text_widget()
            if current_widget:
                current_widget.setFont(font)

            # Guardar la fuente seleccionada en la configuración
            self.config['font_family'] = font.family()
            self.config['font_size'] = font.pointSize()
            self.save_config()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Contenedor de pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        layout.addWidget(self.tab_widget)

        # Crear la primera pestaña
        self.add_new_tab()

        # Controles para desplazamiento y transposición
        control_layout = QHBoxLayout()
        layout.addLayout(control_layout)

        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_scrolling)
        control_layout.addWidget(self.start_button)

        self.pause_button = QPushButton("Pausar")
        self.pause_button.clicked.connect(self.pause_scrolling)
        control_layout.addWidget(self.pause_button)

        control_layout.addWidget(QLabel("Velocidad:"))

        self.speed_slider = QSlider(Qt.Orientation.Horizontal)
        self.speed_slider.setRange(1, 30)

        # Restaurar la posición del deslizador desde la configuración
        last_position = self.config.get('last_slider_position', 15)
        self.speed_slider.setValue(last_position)

        # Recalcular la velocidad al iniciar el programa
        self.update_speed()

        self.speed_slider.valueChanged.connect(self.update_speed)
        control_layout.addWidget(self.speed_slider)

        self.transpose_button = QPushButton("Transponer")
        self.transpose_button.clicked.connect(self.show_transpose_menu)
        control_layout.addWidget(self.transpose_button)
        
        # Añadir etiqueta para mostrar la codificación
        self.encoding_label = QLabel("Codificación: UTF-8")
        self.encoding_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.encoding_label)

        self.create_menu_bar()

        # Crear el atajo de teclado para iniciar/pausar el scroll
        shortcut = QShortcut(QKeySequence("Ctrl+Space"), self)
        shortcut.activated.connect(self.toggle_scroll)

        self.tab_widget.currentChanged.connect(self.update_encoding_label)  # Conectar evento

        self.setAcceptDrops(True)

    def update_encoding_label(self, index):
        print(f"Actualizando etiqueta para la pestaña {index}")
        file_path = self.opened_files.get(index, None)
        if file_path and file_path in self.file_encodings:
            encoding = self.file_encodings[file_path]['encoding']
            line_ending = self.file_encodings[file_path]['line_ending']
            self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")

            # Actualizar el título de la ventana con el nombre del archivo
            self.setWindowTitle(f"{os.path.basename(file_path)} - Lector y Editor de Texto con acordes")
        else:
            self.encoding_label.setText("Codificación: N/A | Terminador de línea: N/A")
            self.setWindowTitle("Lector y Editor de Texto con acordes")

    def toggle_scroll(self):
        if self.is_scrolling:
            self.pause_scrolling()
        else:
            self.start_scrolling()

    def add_new_tab(self, file_name=None, content="", file_path=None):
        # Crear un nuevo área de texto
        text_widget = CustomTextEdit()
        text_widget.setUndoRedoEnabled(True)
        text_widget.document().setModified(False)  # Inicialmente no modificado

        text_widget.textChanged.connect(self.on_text_changed)

        # Aplicar la fuente predeterminada desde la configuración
        default_font = self.config.get('font_family', 'Noto Mono')
        default_font_size = self.config.get('font_size', 10)
        text_widget.setFont(QFont(default_font, default_font_size))

        # Cargar contenido si se proporciona
        if content:
            text_widget.setPlainText(content)
            text_widget.document().setModified(False)  # Marcar como no modificado

        # Agregar el área de texto como nueva pestaña
        tab_name = file_name if file_name else "Nuevo archivo"
        index = self.tab_widget.addTab(text_widget, tab_name)

        # Asociar la pestaña con la ruta del archivo (si existe)
        if file_path:
            self.opened_files[index] = file_path
        else:
            self.opened_files[index] = None

        # Establecer como la pestaña activa
        self.tab_widget.setCurrentWidget(text_widget)

        # Actualizar el título de la ventana
        self.update_window_title()

    def on_text_changed(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_index = self.tab_widget.currentIndex()
            file_path = self.opened_files.get(current_index, None)

            # Verificar que el archivo exista en la lista de archivos abiertos
            if file_path:
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')  # Obtener la codificación

                try:
                    # Leer el contenido guardado del archivo
                    with open(file_path, 'r', encoding=encoding) as f:
                        saved_content = f.read()
                except Exception as e:
                    saved_content = ""  # Si ocurre un error al leer, asumir contenido vacío

                # Obtener el contenido actual del widget
                current_content = current_widget.toPlainText()

                # Comparar ambos para verificar si realmente ha sido modificado
                is_modified = current_content != saved_content
                current_widget.document().setModified(is_modified)

                # Actualizar el título de la ventana
                self.update_window_title()

    def update_window_title(self):
        # Obtener el índice de la pestaña activa
        current_index = self.tab_widget.currentIndex()

        # Obtener el nombre del archivo asociado a la pestaña activa
        file_path = self.opened_files.get(current_index, "Nuevo archivo")
        file_name = os.path.basename(file_path) if file_path else "Nuevo archivo"

        # Verificar si el documento tiene cambios no guardados
        modified = "*" if self.get_current_text_widget().document().isModified() else ""

        # Actualizar el título de la ventana
        self.setWindowTitle(f"{file_name} {modified} - Lector y Editor de Letras con Acordes")

    def close_tab(self, index):
        # Obtener el área de texto de la pestaña
        current_widget = self.tab_widget.widget(index)
        if isinstance(current_widget, CustomTextEdit) and current_widget.document().isModified():
            # Mostrar cuadro de diálogo
            reply = QMessageBox.question(
                self, "Cerrar documento",
                f'El documento "{self.tab_widget.tabText(index)}" ha sido modificado. '
                "¿Desea guardar los cambios, o descartarlos?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Save:
                self.tab_widget.setCurrentIndex(index)
                self.save_file()  # Guardar cambios
            elif reply == QMessageBox.StandardButton.Cancel:
                return  # No cerrar la pestaña

        # Cerrar la pestaña
        self.tab_widget.removeTab(index)

    def closeEvent(self, event):
        for index in range(self.tab_widget.count()):
            self.tab_widget.setCurrentIndex(index)
            current_widget = self.tab_widget.widget(index)
            if isinstance(current_widget, CustomTextEdit) and current_widget.document().isModified():
                reply = QMessageBox.question(
                    self, "Cerrar aplicación",
                    f'El documento "{self.tab_widget.tabText(index)}" ha sido modificado. '
                    "¿Desea guardar los cambios, o descartarlos?",
                    QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Save:
                    self.save_file()
                elif reply == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                    return

        event.accept()

    def get_current_text_widget(self):
        # Obtener el área de texto de la pestaña activa
        widget = self.tab_widget.currentWidget()
        if isinstance(widget, CustomTextEdit):
            return widget
        return None

        # Nueva función: Copiar
    def copy_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.copy()

        # Nueva función: Pegar
    def paste_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.paste()

    def cut_text(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.cut()

    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Menú Archivo
        file_menu = menu_bar.addMenu("Archivo")

        new_action = QAction("Nuevo archivo", self)
        new_action.triggered.connect(self.add_new_tab)
        new_action.setShortcut("Ctrl+N")  # Atajo: Ctrl+N
        file_menu.addAction(new_action)

        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_file)
        open_action.setShortcut("Ctrl+O")  # Atajo: Ctrl+O
        file_menu.addAction(open_action)

        # Menú Abrir reciente
        recent_menu = file_menu.addMenu("Abrir reciente")
        self.recent_menu = recent_menu  # Guardar referencia al menú para actualizarlo

        save_action = QAction("Guardar", self)
        save_action.triggered.connect(self.save_file)
        save_action.setShortcut("Ctrl+S")  # Atajo: Ctrl+S
        file_menu.addAction(save_action)

        save_as_action = QAction("Guardar como", self)
        save_as_action.triggered.connect(self.save_file_as_original)  # Llama a save_file_as en lugar de save_file
        save_as_action.setShortcut("Ctrl+Shift+S")  # Atajo: Ctrl+Shift+S
        file_menu.addAction(save_as_action)

        # Opción Guardar Codificación como
        save_as_encoding_action = QAction("Guardar Codificación como...", self)
        save_as_encoding_action.triggered.connect(self.save_file_with_encoding)
        file_menu.addAction(save_as_encoding_action)

        file_menu.addSeparator()

        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")  # Atajo: Ctrl+Q
        file_menu.addAction(exit_action)

        # Menú Editar
        edit_menu = menu_bar.addMenu("Editar")

        undo_action = QAction("Deshacer", self)
        undo_action.triggered.connect(lambda: self.get_current_text_widget().undo())
        undo_action.setShortcut("Ctrl+Z")  # Atajo: Ctrl+Z
        edit_menu.addAction(undo_action)

        redo_action = QAction("Rehacer", self)
        redo_action.triggered.connect(lambda: self.get_current_text_widget().redo())
        redo_action.setShortcut("Ctrl+Shift+Z")  # Atajo: Ctrl+Shift+Z
        edit_menu.addAction(redo_action)

        # Añadir un separador
        edit_menu.addSeparator()

        # Nueva opción: Copiar
        copy_action = QAction("Copiar", self)
        copy_action.triggered.connect(self.copy_text)
        copy_action.setShortcut("Ctrl+C")  # Atajo de teclado: Ctrl+C
        edit_menu.addAction(copy_action)

        # Nueva opción: Pegar
        paste_action = QAction("Pegar", self)
        paste_action.triggered.connect(self.paste_text)
        paste_action.setShortcut("Ctrl+V")  # Atajo de teclado: Ctrl+V
        edit_menu.addAction(paste_action)

        # Nueva opción: Cortar

        cut_action = QAction("Cortar", self)
        cut_action.triggered.connect(self.cut_text)
        cut_action.setShortcut("Ctrl+X")  # Atajo de teclado: Ctrl+X
        edit_menu.addAction(cut_action)

        select_all_action = QAction("Seleccionar todo", self)
        select_all_action.triggered.connect(lambda: self.get_current_text_widget().selectAll())
        select_all_action.setShortcut("Ctrl+A")  # Atajo: Ctrl+A
        edit_menu.addAction(select_all_action)

        # Menú Opciones
        options_menu = menu_bar.addMenu("Opciones")

        # Opción para usar sostenidos
        sharps_action = QAction("Usar Sostenidos al bajar semitonos", self)
        sharps_action.setCheckable(True)
        sharps_action.setChecked(self.config['use_sharps'])
        sharps_action.triggered.connect(lambda: self.toggle_accidentals(True))
        options_menu.addAction(sharps_action)

        # Opción para usar bemoles
        flats_action = QAction("Usar Bemoles al bajar semitonos", self)
        flats_action.setCheckable(True)
        flats_action.setChecked(not self.config['use_sharps'])
        flats_action.triggered.connect(lambda: self.toggle_accidentals(False))
        options_menu.addAction(flats_action)

        # Añadir un separador
        options_menu.addSeparator()

        # Agrupar las opciones para que sean mutuamente excluyentes
        group = QActionGroup(self)
        group.addAction(sharps_action)
        group.addAction(flats_action)

        # ... Opción de cambiar la fuente
        change_font_action = QAction("Cambiar fuente", self)
        change_font_action.triggered.connect(self.select_font)
        change_font_action.setShortcut("Ctrl+F")
        options_menu.addAction(change_font_action)

        # ... Opción de cambiar la velocidad máxima
        change_speed_action = QAction("Cambiar velocidad máxima", self)
        change_speed_action.triggered.connect(self.change_max_speed)
        change_speed_action.setShortcut("Ctrl+Shift+V")
        options_menu.addAction(change_speed_action)

        # Menú Ayuda
        help_menu = menu_bar.addMenu("Ayuda")

        about_action = QAction("Acerca de...", self)
        about_action.triggered.connect(self.show_about_dialog)
        about_action.setShortcut("Ctrl+H")
        help_menu.addAction(about_action)

    def update_recent_files_menu(self):
        self.recent_menu.clear()
        recent_files = self.config.get('recent_files', [])

        for entry in recent_files:
            file_path = entry['path']
            timestamp = entry['timestamp']

            # Acción con el nombre y la fecha
            action = QAction(f"{os.path.basename(file_path)} - {timestamp}", self)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_menu.addAction(action)

            # Acción separadora para mostrar la ruta completa como texto no clicable
            path_action = QAction(f"Ruta: {file_path}", self)
            path_action.setEnabled(False)  # Deshabilitar para que no sea clicable
            self.recent_menu.addAction(path_action)

        if not recent_files:
            self.recent_menu.addAction("No hay archivos recientes").setEnabled(False)

    def open_recent_file(self, file_path):
        if os.path.exists(file_path):
            self.open_dropped_file(file_path)
        else:
            QMessageBox.warning(self, "Error", f"El archivo '{file_path}' no existe.")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self.open_dropped_file(file_path)
            event.acceptProposedAction()
        else:
            event.ignore()

    def open_dropped_file(self, file_path):
        if os.path.exists(file_path) and file_path.lower().endswith('.txt'):
            try:
                # Detectar la codificación del archivo
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'utf-8'

                # Detectar terminador de línea en modo binario
                if b'\r\n' in raw_data:
                    line_ending = "Windows (CRLF)"
                elif b'\n' in raw_data:
                    line_ending = "Unix (LF)"
                elif b'\r' in raw_data:
                    line_ending = "Mac (CR)"
                else:
                    line_ending = "Desconocido"

                # Leer el archivo con la codificación detectada
                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    content = file.read()

                # Guardar codificación y terminador de línea
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}

                # Actualizar etiqueta de codificación
                self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")

                # Cargar el contenido en la pestaña actual o abrir una nueva
                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.opened_files[index] = file_path
                else:
                    self.add_new_tab(file_name=os.path.basename(file_path), content=content, file_path=file_path)

                # Guardar la última ruta en la configuración
                self.config['last_opened_path'] = os.path.dirname(file_path)
                self.save_config()  # Guardar la configuración actualizada

                # Actualizar el título de la ventana
                self.update_window_title()

                # Añadir a la lista de archivos recientes
                self.add_to_recent_files(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "El archivo no es válido o no existe.")

    def new_file(self):
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.clear()
        self.current_file = None
        self.setWindowTitle("Lector y Editor de Texto - Nuevo archivo")

    def add_to_recent_files(self, file_path):
        from datetime import datetime

        recent_files = self.config.get('recent_files', [])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Eliminar si ya existe
        recent_files = [f for f in recent_files if f['path'] != file_path]

        # Añadir al inicio
        recent_files.insert(0, {'path': file_path, 'timestamp': timestamp})

        # Limitar a 15 archivos
        self.config['recent_files'] = recent_files[:9]
        self.save_config()
        self.update_recent_files_menu()

    def open_file(self):
        # Obtener la última ruta desde la configuración
        last_path = self.config.get('last_opened_path', '')

        # Abrir el cuadro de diálogo de selección de archivo, iniciando en la última ruta
        file_path, _ = QFileDialog.getOpenFileName(self, "Abrir archivo", last_path, "Archivos de texto (*.txt)")
        if file_path:
            try:
                # Detectar la codificación del archivo
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    detected = chardet.detect(raw_data)
                    encoding = detected['encoding'] or 'utf-8'

                # Detectar el tipo de terminador de línea en modo binario
                if b'\r\n' in raw_data:
                    line_ending = "Windows (CRLF)"
                elif b'\n' in raw_data:
                    line_ending = "Unix (LF)"
                elif b'\r' in raw_data:
                    line_ending = "Mac (CR)"
                else:
                    line_ending = "Desconocido"

                # Leer el archivo con la codificación detectada
                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    content = file.read()

                # Guardar la codificación y el terminador de línea
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}

                # Actualizar la etiqueta de codificación y terminador de línea
                self.encoding_label.setText(f"Codificación: {encoding} | Terminador de línea: {line_ending}")

                # Cargar el contenido en la pestaña actual o abrir una nueva
                current_widget = self.get_current_text_widget()
                if current_widget and not current_widget.toPlainText().strip():
                    current_widget.setPlainText(content)
                    index = self.tab_widget.indexOf(current_widget)
                    self.tab_widget.setTabText(index, os.path.basename(file_path))
                    self.opened_files[index] = file_path
                else:
                    self.add_new_tab(file_name=os.path.basename(file_path), content=content, file_path=file_path)

                # Guardar la última ruta en la configuración
                self.config['last_opened_path'] = os.path.dirname(file_path)
                self.save_config()  # Guardar la configuración actualizada

                # Actualizar el título de la ventana
                self.update_window_title()

                # Añadir a la lista de archivos recientes
                self.add_to_recent_files(file_path)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def load_file(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                current_widget = self.get_current_text_widget()
                if current_widget:
                    current_widget.setPlainText(content)
            self.current_file = file_path
            self.setWindowTitle(f"Lector y Editor de Texto - {os.path.basename(file_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo: {str(e)}")

    def save_file(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        index = self.tab_widget.currentIndex()
        file_path = self.opened_files.get(index)

        if file_path:
            # Guardar directamente en la ubicación conocida con la codificación y fin de línea originales
            try:
                encoding = self.file_encodings.get(file_path, {}).get('encoding', 'utf-8')
                line_ending = self.file_encodings.get(file_path, {}).get('line_ending', 'Unix (LF)')

                # Obtener el contenido y ajustar el fin de línea
                content = current_widget.toPlainText()
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                with open(file_path, 'w', encoding=encoding) as file:
                    file.write(content)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")
        else:
            # Si no hay ubicación conocida, mostrar "Guardar como"
            self.save_file_as()

        current_widget.document().setModified(False)  # Marcar como no modificado
        self.update_window_title()  # Actualizar el título

    def save_file_as_original(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        # Obtener el índice de la pestaña actual y el nombre del archivo asociado
        index = self.tab_widget.currentIndex()
        suggested_name = self.opened_files.get(index, "Nuevo archivo.txt")

        # Mostrar cuadro de diálogo "Guardar como"
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)")
        if file_path:
            try:
                # Obtener la codificación y el fin de línea originales
                encoding = self.file_encodings.get(suggested_name, {}).get('encoding', 'utf-8')
                line_ending = self.file_encodings.get(suggested_name, {}).get('line_ending', 'Unix (LF)')

                # Ajustar el fin de línea en el contenido
                content = current_widget.toPlainText()
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                # Guardar el archivo
                with open(file_path, 'w', encoding=encoding) as file:
                    file.write(content)

                # Actualizar datos del archivo en la pestaña
                self.opened_files[index] = file_path
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}
                self.tab_widget.setTabText(index, os.path.basename(file_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")

    def save_file_with_encoding(self):
        current_widget = self.get_current_text_widget()
        if not current_widget:
            QMessageBox.warning(self, "Error", "No hay ninguna pestaña activa para guardar.")
            return

        # Obtener el índice de la pestaña actual y el nombre del archivo asociado
        index = self.tab_widget.currentIndex()
        suggested_name = self.opened_files.get(index, "Nuevo archivo.txt")

        # Mostrar cuadro de diálogo "Guardar como"
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar archivo", suggested_name, "Archivos de texto (*.txt)")
        if file_path:
            # Cuadro de diálogo para seleccionar codificación
            encoding, ok = QInputDialog.getItem(
                self,
                "Seleccionar codificación",
                "Codificación:",
                ["UTF-8", "UTF-16 LE", "UTF-16 BE", "UTF-8 con BOM", "ANSI", "ISO-8859-1"],
                0,
                False
            )
            if not ok:
                return

            # Cuadro de diálogo para seleccionar tipo de fin de línea
            line_ending, ok = QInputDialog.getItem(
                self,
                "Seleccionar terminador de línea",
                "Terminador de línea:",
                ["Windows (CRLF)", "Unix (LF)", "Mac (CR)"],
                0,
                False
            )
            if not ok:
                return

            try:
                # Ajustar el fin de línea en el contenido
                content = current_widget.toPlainText()
                if line_ending == "Windows (CRLF)":
                    content = content.replace('\n', '\r\n')
                elif line_ending == "Mac (CR)":
                    content = content.replace('\n', '\r')

                # Guardar con la codificación seleccionada
                if encoding == "UTF-8 con BOM":
                    with open(file_path, 'w', encoding='utf-8-sig') as file:
                        file.write(content)
                elif encoding == "ANSI":
                    with open(file_path, 'w', encoding='windows-1252') as file:
                        file.write(content)
                else:
                    with open(file_path, 'w', encoding=encoding.lower().replace(" ", "-")) as file:
                        file.write(content)

                # Actualizar datos del archivo en la pestaña
                self.opened_files[index] = file_path
                self.file_encodings[file_path] = {'encoding': encoding, 'line_ending': line_ending}
                self.tab_widget.setTabText(index, os.path.basename(file_path))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar el archivo: {str(e)}")


    def start_scrolling(self):
        if not self.is_scrolling:
            self.is_scrolling = True
            self.scroll_text()

    def pause_scrolling(self):
        self.is_scrolling = False

    def scroll_text(self):
        if self.is_scrolling:
            current_widget = self.get_current_text_widget()
            if current_widget:
                scrollbar = current_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.value() + 1)
            QTimer.singleShot(self.scroll_speed, self.scroll_text)

    def calculate_speed(self, value):
        min_speed = 1
        factor = math.log(self.max_speed / min_speed) / 29
        return max(1, int(min_speed * math.exp(factor * (30 - value))))

    def update_speed(self):
        self.scroll_speed = self.calculate_speed(self.speed_slider.value())
        # Guardar la posición del deslizador en la configuración
        self.config['last_slider_position'] = self.speed_slider.value()
        self.save_config()

    def change_max_speed(self):
        new_max_speed, ok = QInputDialog.getInt(
            self, "Cambiar velocidad máxima",
            "Ingrese la nueva velocidad máxima (1-1000):",
            value=self.max_speed, min=1, max=1000
        )
        if ok:
            self.max_speed = new_max_speed
            self.update_speed()
            self.save_config()
            QMessageBox.information(self, "Velocidad actualizada",
                                    f"La velocidad máxima se ha actualizado a {self.max_speed}.\n"
                                    f"Use el control deslizante para ajustar la velocidad entre 1 y {self.max_speed}.")

    def show_transpose_menu(self):
        transpose_menu = QMenu(self)
        for i in range(-7, 8):
            action = QAction(f"{i:+d}" if i != 0 else "0 (Original)", self)
            action.triggered.connect(lambda checked, x=i: self.transpose_chords(x))
            transpose_menu.addAction(action)
        transpose_menu.exec(self.transpose_button.mapToGlobal(self.transpose_button.rect().bottomLeft()))

    def transpose_chords(self, semitones):
        # Guardar la posición actual del scroll
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_scroll_position = current_widget.verticalScrollBar().value()

        # Obtener el contenido actual y transponerlo
        current_widget = self.get_current_text_widget()
        if current_widget:
            content = current_widget.toPlainText()
        transposed_content = self.transpose_text(content, semitones)

        # Usar QTextCursor para reemplazar el texto sin perder el historial de deshacer
        current_widget = self.get_current_text_widget()
        if current_widget:
            cursor = current_widget.textCursor()
        cursor.beginEditBlock()  # Agrupa los cambios para que sean una sola acción de deshacer
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.insertText(transposed_content)
        cursor.endEditBlock()

        # Restaurar la posición del scroll
        current_widget = self.get_current_text_widget()
        if current_widget:
            current_widget.verticalScrollBar().setValue(current_scroll_position)

    def transpose_text(self, text, semitones):
        chord_pattern = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?!\w)'
        chord_base = [
            ['C'], ['C#', 'Db'], ['D'], ['D#', 'Eb'], ['E'], ['F'],
            ['F#', 'Gb'], ['G'], ['G#', 'Ab'], ['A'], ['A#', 'Bb'], ['B']
        ]

        use_sharps = self.config['use_sharps']

        def transpose_chord(chord, spaces_after):
            root = chord[0]
            accidental = '#' if '#' in chord else 'b' if 'b' in chord else ''
            suffix = chord[len(root + accidental):]

            current_index = next(i for i, group in enumerate(chord_base) if root + accidental in group)
            new_index = (current_index + semitones) % len(chord_base)

            # Elegir entre sostenidos y bemoles según la configuración
            new_root = chord_base[new_index][0] if self.config['use_sharps'] else chord_base[new_index][-1]

            # Reconstruir el acorde con la nueva raíz
            return new_root + suffix, ' ' * spaces_after

        def is_chord_line(line):
            words = line.split()
            matches = [bool(re.fullmatch(chord_pattern, word)) for word in words]
            # Considera la línea como acorde si más del 50% de las palabras coinciden con el patrón de acordes
            return sum(matches) > len(words) / 2

        def process_line(line):
            chord_positions = list(re.finditer(chord_pattern, line))
            if not chord_positions:
                return line

            new_line = []
            last_end = 0

            for i, match in enumerate(chord_positions):
                # Añadir el texto entre acordes
                new_line.append(line[last_end:match.start()])

                # Calcular espacios después del acorde
                next_pos = chord_positions[i + 1].start() if i + 1 < len(chord_positions) else len(line)
                spaces_after = next_pos - match.end()

                # Transponer el acorde
                new_chord, new_spaces = transpose_chord(match.group(), spaces_after)
                new_line.append(new_chord + new_spaces)

                last_end = next_pos

            # Añadir el resto de la línea después del último acorde
            new_line.append(line[last_end:])
            return ''.join(new_line)

        lines = text.split('\n')
        transposed_lines = [process_line(line) if is_chord_line(line) else line for line in lines]
        return '\n'.join(transposed_lines)

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                'max_speed': 100,
                'font_family': 'Noto Mono',
                'font_size': 10,
                'last_opened_path': '',  # Valor predeterminado para la última ruta
                'use_sharps': True
            }

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)  # Guardar con formato legible

    def toggle_accidentals(self, use_sharps):
        # Cambiar la configuración de uso de sostenidos o bemoles
        self.config['use_sharps'] = use_sharps
        self.save_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextScrollerApp()
    window.show()
    sys.exit(app.exec())
