# main.py
import sys
import os
import logging
from pathlib import Path

# Add the project root directory to sys.path if needed
project_dir = Path(__file__).resolve().parent.parent
if str(project_dir) not in sys.path:
    sys.path.insert(0, str(project_dir))

# Import frontend components
from app.frontend.utils.logger import setup_logging
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from app.frontend.main_window import MainWindow

def main():
    # Setup logging
    logger = setup_logging()
    logger.info("Starting AddaxAI")
    
    try:
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("AddaxAI")
        
        # Configure system fonts
        font_db = QFontDatabase()
        default_font = QFont("sans")
        default_font.setPointSize(10)
        app.setFont(default_font)
        
        # Handle Qt messages
        app.installEventFilter(QtMessageHandler())
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        # Start event loop
        result = app.exec()
        
        logger.info("AddaxAI exited with code %d", result)
        return result
        
    except Exception as e:
        logger.critical("Application crashed: %s", str(e), exc_info=True)
        
        # Show critical error dialog
        show_critical_error(str(e), traceback.format_exc())
        return 1

def show_critical_error(message, details=None):
    """Show critical error dialog when application can't start."""
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        dialog = QMessageBox()
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle("Critical Error")
        dialog.setText("AddaxAI could not start due to an error:")
        dialog.setInformativeText(message)
        if details:
            dialog.setDetailedText(details)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()
    except:
        # Last resort if even the dialog fails
        print(f"CRITICAL ERROR: {message}")
        if details:
            print(details)


class QtMessageHandler(QObject):
    """Handler for Qt debug/warning messages."""
    
    def eventFilter(self, obj, event):
        """Filter Qt events."""
        return False  # Don't actually filter any events
    
    def __init__(self):
        super().__init__()
        # Install Qt message handler
        qInstallMessageHandler(self.handle_qt_message)
    
    def handle_qt_message(self, msg_type, context, message):
        """Handle Qt messages and log them."""
        if msg_type == QtDebugMsg:
            logger.debug(f"Qt: {message}")
        elif msg_type == QtInfoMsg:
            logger.info(f"Qt: {message}")
        elif msg_type == QtWarningMsg:
            logger.warning(f"Qt: {message}")
        elif msg_type == QtCriticalMsg:
            logger.error(f"Qt: {message}")
        elif msg_type == QtFatalMsg:
            logger.critical(f"Qt: {message}")
            
