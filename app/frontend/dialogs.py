# frontend/dialogs.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QComboBox, QCheckBox, QRadioButton, QButtonGroup,
    QGroupBox, QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QLineEdit, QWidget, QGridLayout,
    QScrollArea, QSlider, QTabWidget, QFrame, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize, QDir
from PySide6.QtGui import QFont, QIcon, QPixmap

from pathlib import Path
import os
import sys

from AddaxAI.backend import AddaxAI_files, utils
from AddaxAI.frontend.widgets import RangeSlider, SpeciesSelector


class ProgressDialog(QDialog):
    """Dialog for showing progress during a long-running operation."""

    cancelRequested = Signal()

    def __init__(self, title="Processing", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setModal(True)

        # Set up the UI
        self.setup_ui()

        # Initialize timer for auto-closing
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)

        # Prevent closing with escape key
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Task label
        self.task_label = QLabel("Starting...")
        self.task_label.setFont(QFont("sans", 11, QFont.Bold))
        self.task_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.task_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Details label
        self.details_label = QLabel("")
        self.details_label.setWordWrap(True)
        font = QFont("monospace")
        font.setPointSize(9)
        self.details_label.setFont(font)
        layout.addWidget(self.details_label)

        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def update_progress(self, task_name="", status="", progress=-1, message="", details=""):
        """Update progress dialog with new information.

        Args:
            task_name: Name of the current task
            status: Status of the task (e.g., "running", "done")
            progress: Progress percentage (0-100), or -1 for indeterminate
            message: Main message to display
            details: Additional details
        """
        # Update task label if provided
        if task_name:
            self.task_label.setText(task_name)

        # Update progress bar
        if progress >= 0:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(progress)
        else:
            # Indeterminate progress
            self.progress_bar.setRange(0, 0)

        # Update status
        if message:
            self.status_label.setText(message)

        # Update details
        if details:
            self.details_label.setText(details)

        # Handle completion
        if status == "done":
            self.progress_bar.setValue(100)
            self.cancel_button.setText("Close")

            # Auto-close after 2 seconds
            self.timer.start(2000)

    def on_cancel(self):
        """Handle cancel button click."""
        if self.cancel_button.text() == "Cancel":
            # Confirm cancellation
            reply = QMessageBox.question(
                self, "Confirm Cancel",
                "Are you sure you want to cancel this operation?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.cancelRequested.emit()
                self.cancel_button.setEnabled(False)
                self.status_label.setText("Cancelling...")
        else:
            # Just close the dialog
            self.accept()

    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.cancel_button.text() == "Cancel":
            # Prevent closing if task is still running
            event.ignore()
            self.on_cancel()
        else:
            event.accept()


class VerificationDialog(QDialog):
    """Dialog for setting up human verification of detection results."""

    startVerification = Signal(dict)

    def __init__(self, folder_path, parent=None):
        super().__init__(parent)

        self.folder_path = folder_path
        self.setWindowTitle("Human Verification Setup")
        self.setMinimumSize(600, 500)

        # Setup UI
        self.setup_ui()

        # Load classes from detection results
        self.load_classes()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Intro label
        intro_label = QLabel(
            "Human verification allows you to review and correct detection results. "
            "Select which species to verify and how many samples to include."
        )
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)

        # Create a split view
        splitter = QSplitter(Qt.Horizontal)

        # Left side - class selection
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        classes_group = QGroupBox("Classes to Verify")
        classes_layout = QVBoxLayout(classes_group)

        # Classes list
        self.classes_list = QListWidget()
        self.classes_list.setSelectionMode(QListWidget.MultiSelection)
        classes_layout.addWidget(self.classes_list)

        # Select all/none buttons
        buttons_layout = QHBoxLayout()

        self.select_all_button = QPushButton("Select All")
        self.select_all_button.clicked.connect(self.select_all_classes)
        buttons_layout.addWidget(self.select_all_button)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_selection)
        buttons_layout.addWidget(self.clear_button)

        classes_layout.addLayout(buttons_layout)
        left_layout.addWidget(classes_group)

        # Right side - settings
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Sample selection group
        sample_group = QGroupBox("Sample Selection")
        sample_layout = QVBoxLayout(sample_group)

        # Selection mode
        self.select_all_radio = QRadioButton("Select all matches")
        self.select_percent_radio = QRadioButton("Select by percentage")
        self.select_count_radio = QRadioButton("Select fixed count")

        # Default selection
        self.select_all_radio.setChecked(True)

        # Create button group
        selection_group = QButtonGroup(self)
        selection_group.addButton(self.select_all_radio)
        selection_group.addButton(self.select_percent_radio)
        selection_group.addButton(self.select_count_radio)
        selection_group.buttonClicked.connect(self.on_selection_mode_changed)

        sample_layout.addWidget(self.select_all_radio)

        # Percentage selection
        percent_layout = QHBoxLayout()
        percent_layout.addWidget(self.select_percent_radio)
        self.percent_spin = QSpinBox()
        self.percent_spin.setRange(1, 100)
        self.percent_spin.setValue(50)
        self.percent_spin.setSuffix("%")
        self.percent_spin.setEnabled(False)
        percent_layout.addWidget(self.percent_spin)
        percent_layout.addStretch()
        sample_layout.addLayout(percent_layout)

        # Count selection
        count_layout = QHBoxLayout()
        count_layout.addWidget(self.select_count_radio)
        self.count_spin = QSpinBox()
        self.count_spin.setRange(1, 1000)
        self.count_spin.setValue(50)
        self.count_spin.setSuffix(" images")
        self.count_spin.setEnabled(False)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        sample_layout.addLayout(count_layout)

        right_layout.addWidget(sample_group)

        # Threshold group
        threshold_group = QGroupBox("Confidence Thresholds")
        threshold_layout = QVBoxLayout(threshold_group)

        # Threshold mode
        self.thresh_mode_label = QLabel("Annotation threshold mode:")
        threshold_layout.addWidget(self.thresh_mode_label)

        self.thresh_mode_combo = QComboBox()
        self.thresh_mode_combo.addItem("Use generic threshold for all classes")
        self.thresh_mode_combo.addItem("Use class-specific thresholds")
        threshold_layout.addWidget(self.thresh_mode_combo)

        # Generic threshold
        generic_layout = QHBoxLayout()
        generic_layout.addWidget(QLabel("Generic threshold:"))
        self.generic_thresh_slider = RangeSlider(min_value=0.0, max_value=1.0, start_min=0.6, start_max=1.0)
        generic_layout.addWidget(self.generic_thresh_slider, 1)
        self.generic_thresh_value = QLabel("0.6")
        generic_layout.addWidget(self.generic_thresh_value)
        threshold_layout.addLayout(generic_layout)

        # Connect slider to label
        self.generic_thresh_slider.valueChanged.connect(
            lambda min_val, max_val: self.generic_thresh_value.setText(f"{min_val:.2f}")
        )

        right_layout.addWidget(threshold_group)

        # Add scroll area for right side if needed
        right_scroll = QScrollArea()
        right_scroll.setWidgetResizable(True)
        right_scroll.setWidget(right_widget)

        # Add widgets to splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_scroll)
        splitter.setSizes([200, 400])

        layout.addWidget(splitter, 1)

        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.start_button = QPushButton("Start Verification")
        self.start_button.clicked.connect(self.on_start)
        self.start_button.setEnabled(False)  # Disabled until classes are selected

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.start_button)

        layout.addWidget(buttons_widget)

    def load_classes(self):
        """Load classes from detection results."""
        try:
            # Look for image or video recognition files
            image_json = os.path.join(self.folder_path, "image_recognition_file.json")
            video_json = os.path.join(self.folder_path, "video_recognition_file.json")

            # Select the appropriate file
            if os.path.isfile(image_json):
                json_file = image_json
            elif os.path.isfile(video_json):
                json_file = video_json
            else:
                QMessageBox.warning(
                    self, "Warning",
                    "No detection results found in the selected folder."
                )
                self.reject()
                return

            # Load label map from JSON
            label_map = utils.fetch_label_map_from_json(json_file)

            # Add classes to list
            self.classes_list.clear()
            for class_id, class_name in label_map.items():
                item = QListWidgetItem(class_name)
                item.setData(Qt.UserRole, class_id)
                self.classes_list.addItem(item)

            # Connect selection signal
            self.classes_list.itemSelectionChanged.connect(self.on_selection_changed)

        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Error loading classes from detection results: {str(e)}"
            )
            self.reject()

    def select_all_classes(self):
        """Select all classes in the list."""
        for i in range(self.classes_list.count()):
            self.classes_list.item(i).setSelected(True)

    def clear_selection(self):
        """Clear class selection."""
        self.classes_list.clearSelection()

    def on_selection_changed(self):
        """Handle changes in class selection."""
        # Enable start button if at least one class is selected
        self.start_button.setEnabled(len(self.classes_list.selectedItems()) > 0)

    def on_selection_mode_changed(self, button):
        """Handle changes in selection mode."""
        self.percent_spin.setEnabled(button == self.select_percent_radio)
        self.count_spin.setEnabled(button == self.select_count_radio)

    def on_start(self):
        """Prepare verification parameters and start the process."""
        # Get selected classes
        selected_classes = {}
        for item in self.classes_list.selectedItems():
            class_name = item.text()
            class_id = item.data(Qt.UserRole)

            # Default selection mode
            selection_mode = 1  # All
            if self.select_percent_radio.isChecked():
                selection_mode = 2  # Percentage
            elif self.select_count_radio.isChecked():
                selection_mode = 3  # Fixed count

            # Build class parameters
            selected_classes[class_name] = {
                "selected": True,
                "selection_mode": selection_mode,
                "percentage": self.percent_spin.value(),
                "count": self.count_spin.value(),
                "min_conf": 0.2,  # Minimum confidence for detection
                "max_conf": 0.8,  # Maximum confidence for detection
                "ann_min_conf": float(self.generic_thresh_value.text())  # Threshold for annotation
            }

        # Build verification parameters
        verification_params = {
            "classes": selected_classes,
            "annotation_threshold_mode": self.thresh_mode_combo.currentIndex() + 1,  # 1-based index
            "ann_min_confs_generic": float(self.generic_thresh_value.text())
        }

        # Emit signal with parameters
        self.startVerification.emit(verification_params)
        self.accept()


class ExportDialog(QDialog):
    """Dialog for configuring export settings."""

    startExport = Signal(dict)

    def __init__(self, folder_path, parent=None):
        super().__init__(parent)

        self.folder_path = folder_path
        self.setWindowTitle("Export Results")
        self.setMinimumSize(500, 400)

        # Setup UI
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Intro label
        intro_label = QLabel(
            "Configure how you want to export the detection results. "
            "You can create visualizations, export to different formats, and more."
        )
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)

        # Source folder
        source_group = QGroupBox("Source")
        source_layout = QHBoxLayout(source_group)

        source_layout.addWidget(QLabel("Source folder:"))
        self.source_label = QLabel(self.folder_path)
        self.source_label.setWordWrap(True)
        source_layout.addWidget(self.source_label, 1)

        layout.addWidget(source_group)

        # Destination folder
        dest_group = QGroupBox("Destination")
        dest_layout = QHBoxLayout(dest_group)

        dest_layout.addWidget(QLabel("Destination folder:"))
        self.dest_path = QLineEdit()
        self.dest_path.setReadOnly(True)
        dest_layout.addWidget(self.dest_path, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.on_browse)
        dest_layout.addWidget(self.browse_button)

        layout.addWidget(dest_group)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QGridLayout(options_group)

        # File operations
        self.separate_files = QCheckBox("Separate files by categories")
        options_layout.addWidget(self.separate_files, 0, 0, 1, 2)

        self.separate_confidence = QCheckBox("Separate by confidence level")
        options_layout.addWidget(self.separate_confidence, 1, 0, 1, 2)

        options_layout.addWidget(QLabel("File placement:"), 2, 0)
        self.file_placement = QComboBox()
        self.file_placement.addItem("Move")
        self.file_placement.addItem("Copy")
        options_layout.addWidget(self.file_placement, 2, 1)

        # Confidence threshold
        options_layout.addWidget(QLabel("Confidence threshold:"), 3, 0)
        self.confidence_threshold = QDoubleSpinBox()
        self.confidence_threshold.setRange(0.0, 1.0)
        self.confidence_threshold.setValue(0.2)
        self.confidence_threshold.setSingleStep(0.05)
        options_layout.addWidget(self.confidence_threshold, 3, 1)

        # Visualization options
        self.visualize_detections = QCheckBox("Draw bounding boxes")
        options_layout.addWidget(self.visualize_detections, 4, 0)

        self.crop_detections = QCheckBox("Crop detections")
        options_layout.addWidget(self.crop_detections, 4, 1)

        layout.addWidget(options_group)

        # Data export options
        data_group = QGroupBox("Data Export")
        data_layout = QGridLayout(data_group)

        self.export_data = QCheckBox("Export data")
        data_layout.addWidget(self.export_data, 0, 0)

        data_layout.addWidget(QLabel("Format:"), 1, 0)
        self.export_format = QComboBox()
        self.export_format.addItem("CSV")
        self.export_format.addItem("XLSX")
        self.export_format.addItem("COCO JSON")
        data_layout.addWidget(self.export_format, 1, 1)

        self.create_plots = QCheckBox("Create analysis plots")
        data_layout.addWidget(self.create_plots, 2, 0, 1, 2)

        # Enable/disable format selection based on export checkbox
        self.export_data.stateChanged.connect(
            lambda state: self.export_format.setEnabled(state)
        )
        self.export_data.stateChanged.connect(
            lambda state: self.create_plots.setEnabled(state)
        )

        layout.addWidget(data_group)

        # Action buttons
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.on_export)
        self.export_button.setEnabled(False)  # Disabled until destination is selected

        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.export_button)

        layout.addWidget(buttons_widget)

    def on_browse(self):
        """Browse for destination folder."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Destination Folder", QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder:
            self.dest_path.setText(folder)
            self.export_button.setEnabled(True)

    def on_export(self):
        """Prepare export parameters and start the process."""
        if not self.dest_path.text():
            QMessageBox.warning(
                self, "Warning",
                "Please select a destination folder."
            )
            return

        # Collect export parameters
        params = {
            "src_dir": self.folder_path,
            "dst_dir": self.dest_path.text(),
            "thresh": self.confidence_threshold.value(),
            "separate": self.separate_files.isChecked(),
            "file_mode": 1 if self.file_placement.currentText() == "Move" else 2,
            "sep_conf": self.separate_confidence.isChecked(),
            "visualize": self.visualize_detections.isChecked(),
            "crop": self.crop_detections.isChecked(),
            "export": self.export_data.isChecked(),
            "export_format": self.export_format.currentText(),
            "plot": self.create_plots.isChecked()
        }

        # Emit signal with parameters
        self.startExport.emit(params)
        self.accept()

