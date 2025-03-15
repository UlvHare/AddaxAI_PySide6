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
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        # Start event loop
        result = app.exec()
        
        logger.info("AddaxAI exited with code %d", result)
        return result
        
    except Exception as e:
        logger.critical("Application crashed: %s", str(e), exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
