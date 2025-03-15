# frontend/about_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QTextEdit, QWidget
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

import os
from pathlib import Path
from AddaxAI.backend import AddaxAI_files, current_EA_version


class AboutDialog(QDialog):
    """Dialog showing information about the application."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("About AddaxAI")
        self.setMinimumSize(500, 400)
        self.setModal(True)

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with logo and title
        header_layout = QHBoxLayout()

        # Logo
        logo_path = os.path.join(AddaxAI_files, "AddaxAI", "frontend", "resources", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            header_layout.addWidget(logo_label)

        # Title and version info
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("AddaxAI")
        title_font = QFont("sans", 18, QFont.Bold)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)

        version_label = QLabel(f"Version {current_EA_version}")
        version_font = QFont("sans", 10)
        version_label.setFont(version_font)
        title_layout.addWidget(version_label)

        header_layout.addWidget(title_widget, 1)
        layout.addLayout(header_layout)

        # Tab widget for different information sections
        tab_widget = QTabWidget()

        # About tab
        about_tab = QWidget()
        about_layout = QVBoxLayout(about_tab)

        about_text = QTextEdit()
        about_text.setReadOnly(True)
        about_text.setHtml("""
        <p>AddaxAI is a wildlife detection and classification application that uses advanced AI models to identify animals in images and videos.</p>
        <p>The application provides two modes:</p>
        <ul>
            <li><b>Simple Mode</b>: Easy to use interface with default settings</li>
            <li><b>Advanced Mode</b>: Full control over detection and classification settings</li>
        </ul>
        <p>For more information, visit the <a href="https://github.com/PetervanLunteren/AddaxAI">GitHub repository</a>.</p>
        <p>Also see the related article: <a href="https://www.sciencedirect.com/science/article/pii/S1574954124003492">Automatic wild animal classification in videos</a></p>
        """)
        about_layout.addWidget(about_text)

        tab_widget.addTab(about_tab, "About")

        # Credits tab
        credits_tab = QWidget()
        credits_layout = QVBoxLayout(credits_tab)

        credits_text = QTextEdit()
        credits_text.setReadOnly(True)
        credits_text.setHtml("""
        <p><b>Original Development:</b> Peter van Lunteren</p>
        <p><b>PySide6 Refactoring:</b> Alexander Varshavskiy, IPEE RAS</p>
        <p>This application uses several open-source components:</p>
        <ul>
            <li>MegaDetector - Microsoft AI for Earth</li>
            <li>PySide6 - Qt for Python</li>
            <li>Various Python packages for image and data processing</li>
        </ul>
        <p>Special thanks to all contributors and testers.</p>
        """)
        credits_layout.addWidget(credits_text)

        tab_widget.addTab(credits_tab, "Credits")

        # License tab - Read from LICENSE file
        license_tab = QWidget()
        license_layout = QVBoxLayout(license_tab)

        license_text = QTextEdit()
        license_text.setReadOnly(True)
        license_text.setFont(QFont("monospace"))

        # Try to find LICENSE file in the project root
        license_content = "License file not found."
        try:
            # Get project root directory (assuming structure: .../AddaxAI/)
            root_dir = Path(AddaxAI_files).parent
            license_path = root_dir / "LICENSE"

            # If not found, try parent directory
            if not license_path.exists():
                root_dir = root_dir.parent
                license_path = root_dir / "LICENSE"

            # If still not found, try common variations
            if not license_path.exists():
                for name in ["LICENSE.txt", "LICENSE.md", "license", "License.txt"]:
                    alt_path = root_dir / name
                    if alt_path.exists():
                        license_path = alt_path
                        break

            # Read license file if found
            if license_path.exists():
                with open(license_path, 'r', encoding='utf-8') as f:
                    license_content = f.read()
            else:
                license_content = "License file not found. Please refer to the project repository for license information."

        except Exception as e:
            license_content = f"Error reading license file: {str(e)}"

        license_text.setText(license_content)
        license_layout.addWidget(license_text)

        tab_widget.addTab(license_tab, "License")

        layout.addWidget(tab_widget, 1)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
