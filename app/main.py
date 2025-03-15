# main.py
import sys
import os
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from AddaxAI.frontend.main_window import MainWindow
from AddaxAI.backend import AddaxAI_files


def main():
    """Main entry point for the application."""
    # Create and run the application
    app = QApplication(sys.argv)

    # Set app name and organization for settings
    app.setApplicationName("AddaxAI")
    app.setOrganizationName("AddaxAI")

    # Set application icon
    icon_path = os.path.join(AddaxAI_files, "AddaxAI", "frontend", "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
