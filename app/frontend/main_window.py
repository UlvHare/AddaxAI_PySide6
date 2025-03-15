# frontend/main_window.py
import sys
import os
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStatusBar
)
from PySide6.QtGui import QFont, QIcon, QAction
from PySide6.QtCore import Qt, Signal, Slot, QSize

# Import vars from backend
from AddaxAI.backend import AddaxAI_files, green_primary, green_secondary, yellow_primary, yellow_secondary

# Import from frontend
from AddaxAI.frontend.simple_mode import SimpleMode
from AddaxAI.frontend.advanced_mode import AdvancedMode

from .about_dialog import AboutDialog

class MainWindow(QMainWindow):
    """Main application window for AddaxAI."""

    def __init__(self):
        super().__init__()

        # Base window settings
        self.setWindowTitle("AddaxAI")
        self.setMinimumSize(1200, 800)

        # System fonts setting
        self.setup_fonts()

        # Creating of the central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Создание панели инструментов
        self.create_toolbar()

        # Создание меню
        self.create_menu()

        # Создание виджета с вкладками для переключения режимов
        self.create_mode_switcher()

        # Создание stacked widget для содержимого режимов
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget, 1)  # 1 = stretch factor

        # Инициализация режимов
        self.simple_mode_widget = SimpleMode()
        self.simple_mode_widget.folder_selected.connect(self.on_folder_selected)
        self.simple_mode_widget.detection_started.connect(self.on_detection_started)
        self.simple_mode_widget.detection_completed.connect(self.on_detection_completed)

        self.advanced_mode_widget = AdvancedMode()
        self.advanced_mode_widget.folder_selected.connect(self.on_folder_selected)
        self.advanced_mode_widget.detection_started.connect(self.on_detection_started)
        self.advanced_mode_widget.detection_completed.connect(self.on_detection_completed)

        self.stacked_widget.addWidget(self.simple_mode_widget)
        self.stacked_widget.addWidget(self.advanced_mode_widget)

        # По умолчанию показываем простой режим
        self.stacked_widget.setCurrentIndex(0)
        self.simple_button.setChecked(True)

        # Создание статус-бара
        self.statusBar().showMessage("Ready")

        # Применяем стиль
        self.apply_stylesheet()
        
        # Setup error handler
        self.error_handler = ErrorHandler(self)
        self.error_handler.errorOccurred.connect(self.on_error_occurred)
        

    def setup_fonts(self):
        """Setup system fonts for the application."""
        self.font_sans = QFont("sans")
        self.font_serif = QFont("serif")
        self.font_mono = QFont("monospace")

        # Настраиваем шрифты по умолчанию
        app = QApplication.instance()
        app.setFont(self.font_sans)

    def create_toolbar(self):
        """Create main toolbar."""
        self.toolbar = self.addToolBar("Main Toolbar")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(32, 32))

        # Добавляем действия на панель инструментов
        open_action = QAction(QIcon.fromTheme("document-open"), "Open Folder", self)
        open_action.triggered.connect(self.open_folder)
        self.toolbar.addAction(open_action)

        # Добавим разделитель
        self.toolbar.addSeparator()

        # Кнопки для запуска процессов
        detect_action = QAction(QIcon.fromTheme("system-run"), "Run Detection", self)
        detect_action.triggered.connect(self.run_detection)
        self.toolbar.addAction(detect_action)

        # Действия для экспорта
        export_action = QAction(QIcon.fromTheme("document-save"), "Export Results", self)
        export_action.triggered.connect(self.export_results)
        self.toolbar.addAction(export_action)

    def create_menu(self):
        """Create application menu."""
        menu_bar = self.menuBar()

        # Меню File
        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Tools
        tools_menu = menu_bar.addMenu("&Tools")

        detect_action = QAction("&Run Detection", self)
        detect_action.triggered.connect(self.run_detection)
        tools_menu.addAction(detect_action)

        tools_menu.addSeparator()

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # Меню Help
        help_menu = menu_bar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_mode_switcher(self):
        """Create the mode switcher widget (Simple/Advanced)."""
        switcher_widget = QWidget()
        switcher_layout = QHBoxLayout(switcher_widget)
        switcher_layout.setContentsMargins(10, 5, 10, 5)

        self.simple_button = QPushButton("Simple Mode")
        self.simple_button.setCheckable(True)
        self.simple_button.clicked.connect(lambda: self.switch_mode(0))

        self.advanced_button = QPushButton("Advanced Mode")
        self.advanced_button.setCheckable(True)
        self.advanced_button.clicked.connect(lambda: self.switch_mode(1))

        switcher_layout.addWidget(self.simple_button)
        switcher_layout.addWidget(self.advanced_button)
        switcher_layout.addStretch()

        self.main_layout.addWidget(switcher_widget)

    def switch_mode(self, mode_index):
        """Switch between simple and advanced modes."""
        if mode_index == 0:  # Simple mode
            self.simple_button.setChecked(True)
            self.advanced_button.setChecked(False)
        else:  # Advanced mode
            self.simple_button.setChecked(False)
            self.advanced_button.setChecked(True)

        self.stacked_widget.setCurrentIndex(mode_index)

    def apply_stylesheet(self):
        """Apply stylesheet to the application."""
        # Convert colors from HEX for QSS
        qss = f"""
        QMainWindow, QWidget {{
            background-color: {yellow_primary};
            color: {green_primary};
        }}

        QPushButton {{
            background-color: {green_primary};
            color: {yellow_primary};
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-family: 'sans';
        }}

        QPushButton:hover {{
            background-color: {green_secondary};
        }}

        QPushButton:checked {{
            background-color: {green_secondary};
            border: 2px solid {green_primary};
        }}

        QStatusBar {{
            background-color: {green_primary};
            color: {yellow_primary};
        }}
        """
        self.setStyleSheet(qss)

    # Заглушки для будущих методов
    def run_detection(self):
        """Run detection process."""
        self.statusBar().showMessage("Run Detection clicked")

    def export_results(self):
        """Export detection results."""
        self.statusBar().showMessage("Export Results clicked")

    def show_settings(self):
        """Show application settings."""
        self.statusBar().showMessage("Settings clicked")
    # Конец заглушек

    def show_about(self):
        """Show information about the application."""
        dialog = AboutDialog(self)
        dialog.exec()

    def on_folder_selected(self, folder):
    """Handle folder selection from any mode."""
    self.statusBar().showMessage(f"Selected folder: {folder}")

    def on_detection_started(self):
        """Handle detection start from any mode."""
        self.statusBar().showMessage("Detection process started")

    def on_detection_completed(self, success):
        """Handle detection completion from any mode."""
        if success:
            self.statusBar().showMessage("Detection completed successfully")
        else:
            self.statusBar().showMessage("Detection process failed or was cancelled")

    def open_folder(self):
        """Open a folder for processing through toolbar/menu."""
        current_mode = self.stacked_widget.currentIndex()
        if current_mode == 0:
            self.simple_mode_widget.on_select_folder()
        else:
            # Will be implemented for advanced mode later
            self.statusBar().showMessage("Open Folder clicked in Advanced Mode")

    def closeEvent(self, event):
        """Handle window close event to properly shut down task managers."""
        # Shutdown SimpleMode task manager
        if hasattr(self.simple_mode_widget, 'task_manager'):
            self.simple_mode_widget.task_manager.shutdown()

        # Shutdown AdvancedMode task manager (when implemented)
        if hasattr(self.advanced_mode_widget, 'task_manager'):
            self.advanced_mode_widget.task_manager.shutdown()

        # Accept the close event
        event.accept()

@Slot(str, str, str)
def on_error_occurred(self, error_type, title, message):
    """Handle application errors.
    
    Args:
        error_type: Type of error
        title: Dialog title
        message: Error message
    """
    self.error_handler.show_error_dialog(error_type, title, message, self)
    
    # Log the error
    logger.error(f"Application error ({error_type}): {message}")
    
