# frontend/simple_mode.py
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QProgressBar,
    QMessageBox,
    QFrame,
)
from PySide6.QtCore import Qt, Signal, Slot, QDir
from PySide6.QtGui import QFont, QPixmap

from pathlib import Path
import os

from AddaxAI.backend import AddaxAI_files
from .task_manager import TaskManager


class SimpleMode(QWidget):
    """Widget for Simple Mode interface of AddaxAI."""

    # Signals
    folder_selected = Signal(str)
    detection_started = Signal()
    detection_completed = Signal(bool)
    progress_updated = Signal(int, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Setup UI
        self.setup_ui()

        # Initialize states
        self.selected_folder = None
        self.is_running = False

        # Create task manager
        self.task_manager = TaskManager(self)

        # Connect task manager signals
        self.task_manager.taskStarted.connect(self.on_task_started)
        self.task_manager.taskProgress.connect(self.on_task_progress)
        self.task_manager.taskCompleted.connect(self.on_task_completed)
        self.task_manager.taskError.connect(self.on_task_error)

    def setup_ui(self):
        """Set up the user interface for Simple Mode."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header with logo
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)

        # Logo
        logo_path = os.path.join(
            AddaxAI_files, "AddaxAI", "frontend", "resources", "logo.png"
        )
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(
                logo_pixmap.scaled(
                    120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
            )
            header_layout.addWidget(logo_label)

        # Title
        header_label = QLabel("AddaxAI - Simple Mode")
        header_font = QFont("sans", 18, QFont.Bold)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(header_label, 1)

        main_layout.addWidget(header_widget)

        # Description
        description_label = QLabel(
            "Detect and classify wildlife in your images and videos with just a few clicks.\n"
            "Select a folder, start detection, and view the results."
        )
        description_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(description_label)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # Folder selection
        folder_widget = QWidget()
        folder_layout = QHBoxLayout(folder_widget)
        folder_layout.setContentsMargins(0, 0, 0, 0)

        folder_title = QLabel("Folder:")
        folder_title.setFixedWidth(60)
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet(
            "background-color: rgba(255, 255, 255, 80); padding: 8px; border-radius: 4px;"
        )

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.on_select_folder)

        folder_layout.addWidget(folder_title)
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.folder_button)

        main_layout.addWidget(folder_widget)

        # Progress section
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 0, 0, 0)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-weight: bold;")
        progress_layout.addWidget(self.status_label)

        main_layout.addWidget(progress_widget)

        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.start_button = QPushButton("Start Detection")
        self.start_button.clicked.connect(self.on_start_detection)
        self.start_button.setEnabled(False)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)
        self.cancel_button.setEnabled(False)

        self.view_results_button = QPushButton("View Results")
        self.view_results_button.clicked.connect(self.on_view_results)
        self.view_results_button.setEnabled(False)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.view_results_button)

        main_layout.addWidget(buttons_widget)

        # Add stretch at the end for better spacing
        main_layout.addStretch(1)

    def on_select_folder(self):
        """Handle folder selection button click."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder with Images/Videos",
            QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )

        if folder:
            self.selected_folder = folder
            # Show only the folder name to keep UI clean
            folder_name = Path(folder).name
            self.folder_label.setText(f"{folder_name} ({folder})")
            self.folder_selected.emit(folder)
            self.start_button.setEnabled(True)
            self.status_label.setText("Folder selected. Ready to start detection.")

    # Start detection process will be implemented with QThread
    def on_start_detection(self):
        """Handle start detection button click."""
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.is_running = True
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.folder_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting detection process...")
        self.detection_started.emit()

        # Mark operation in progress for crash recovery
        if hasattr(self.parent(), "state_manager"):
            self.parent().state_manager.mark_operation_in_progress(
                self.folder_path, "simple_detection"
            )

            # Create backup of any existing results
            self.parent().state_manager.backup_working_files(self.folder_path)

        # Show dialog with progress bar
        self.progress_dialog = ProgressDialog("Processing Images and Videos", self)
        self.progress_dialog.cancelRequested.connect(self.task_manager.cancel_task)
        self.progress_dialog.show()

        # Start processing task
        self.task_manager.run_task(
            "detection", {"folder_path": self.folder_path, "simple_mode": True}
        )

        # Update status label
        self.status_label.setText("Processing...")

        # Start detection task
        self.task_manager.run_task(
            "detection", {"folder_path": self.selected_folder, "simple_mode": True}
        )

    def on_cancel(self):
        """Handle cancel button click."""
        if self.is_running:
            reply = QMessageBox.question(
                self,
                "Confirm Cancel",
                "Are you sure you want to cancel the detection process?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.Yes:
                self.status_label.setText("Cancelling detection process...")
                self.task_manager.cancel_task()

    def on_view_results(self):
        """Handle view results button click."""
        if self.selected_folder:
            from AddaxAI.backend.utils import open_file_or_folder

            open_file_or_folder(self.selected_folder)
            self.status_label.setText("Opening results folder...")

    def update_progress(self, value, status_text=None):
        """Update progress bar and status text.

        Args:
            value: Progress percentage (0-100)
            status_text: Optional status text to display
        """
        self.progress_bar.setValue(value)
        if status_text:
            self.status_label.setText(status_text)
        self.progress_updated.emit(value, status_text or "")

    def on_detection_finished(self, success):
        """Handle detection process completion.

        Args:
            success: Whether the detection completed successfully
        """
        self.is_running = False
        self.start_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.folder_button.setEnabled(True)

        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("Detection completed successfully!")
            self.view_results_button.setEnabled(True)
        else:
            self.status_label.setText("Detection process failed or was cancelled.")

        self.detection_completed.emit(success)

    def on_task_started(self, task):
        """Handle task started event."""
        if task == "detection":
            self.status_label.setText("Detection process started...")

    def on_task_progress(self, task, status, progress, message, details):
        """Handle task progress updates."""
        if task == "detection":
            if progress >= 0:
                self.progress_bar.setValue(progress)
            else:
                # Indeterminate progress
                self.progress_bar.setRange(0, 0)

            self.status_label.setText(message)

    def on_task_completed(self, task, success, results):
        """Handle task completion."""
        if task == "detection":
            self.is_running = False
            self.start_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.folder_button.setEnabled(True)
            self.progress_bar.setRange(0, 100)

            if success:
                self.progress_bar.setValue(100)
                self.status_label.setText("Detection completed successfully!")
                self.view_results_button.setEnabled(True)
            else:
                if results.get("aborted", False):
                    self.status_label.setText("Detection process was cancelled.")
                else:
                    self.status_label.setText("Detection process failed.")

            self.detection_completed.emit(success)

    def on_task_error(self, task, error_message):
        """Handle task errors."""
        if task == "detection":
            self.is_running = False
            self.start_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.folder_button.setEnabled(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

            self.status_label.setText("Error during detection")

            QMessageBox.critical(
                self,
                "Detection Error",
                f"An error occurred during detection:\n\n{error_message}",
            )

            self.detection_completed.emit(False)
