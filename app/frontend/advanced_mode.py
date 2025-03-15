# frontend/advanced_mode.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel,
    QFileDialog, QProgressBar, QMessageBox, QTabWidget, QCheckBox,
    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QGroupBox, QScrollArea,
    QSplitter, QTextEdit, QFrame, QSlider, QRadioButton, QButtonGroup,
    QStackedWidget
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QDir
from PySide6.QtGui import QFont, QPixmap, QIcon

from pathlib import Path
import os
import sys

from AddaxAI.backend import AddaxAI_files, utils
from AddaxAI.backend.utils import load_global_vars, write_global_vars
from .task_manager import TaskManager
from .widgets import RangeSlider, SpeciesSelector
from .dialogs import ProgressDialog, VerificationDialog, ExportDialog


class AdvancedMode(QWidget):
    """Advanced mode widget with full control over detection settings."""

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

        # Load settings from global vars
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface for Advanced Mode."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Header with logo and title
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Logo
        logo_path = os.path.join(AddaxAI_files, "AddaxAI", "frontend", "resources", "logo.png")
        if os.path.exists(logo_path):
            logo_label = QLabel()
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            header_layout.addWidget(logo_label)

        # Title
        title_label = QLabel("AddaxAI - Advanced Mode")
        title_font = QFont("sans", 16, QFont.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label, 1)

        main_layout.addWidget(header_widget)

        # Folder selection
        folder_widget = QWidget()
        folder_layout = QHBoxLayout(folder_widget)
        folder_layout.setContentsMargins(0, 0, 0, 0)

        folder_title = QLabel("Folder:")
        folder_title.setFixedWidth(60)
        self.folder_label = QLabel("No folder selected")
        self.folder_label.setStyleSheet("background-color: rgba(255, 255, 255, 80); padding: 8px; border-radius: 4px;")

        self.folder_button = QPushButton("Select Folder")
        self.folder_button.clicked.connect(self.on_select_folder)

        folder_layout.addWidget(folder_title)
        folder_layout.addWidget(self.folder_label, 1)
        folder_layout.addWidget(self.folder_button)

        main_layout.addWidget(folder_widget)

        # Create SplitView for settings and log
        splitter = QSplitter(Qt.Vertical)
        splitter.setChildrenCollapsible(False)

        # Settings area
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(0, 0, 0, 0)

        # Tab widget for different settings groups
        self.tab_widget = QTabWidget()

        # Detection tab
        detection_tab = self.create_detection_tab()
        self.tab_widget.addTab(detection_tab, "Detection")

        # Process tab
        process_tab = self.create_process_tab()
        self.tab_widget.addTab(process_tab, "Process")

        # Output tab
        output_tab = self.create_output_tab()
        self.tab_widget.addTab(output_tab, "Output")

        settings_layout.addWidget(self.tab_widget)

        # Log and progress area
        log_widget = QWidget()
        log_layout = QVBoxLayout(log_widget)
        log_layout.setContentsMargins(0, 0, 0, 0)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        log_layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        log_layout.addWidget(self.status_label)

        # Log text area
        log_group = QGroupBox("Log")
        log_group_layout = QVBoxLayout(log_group)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("monospace"))
        log_group_layout.addWidget(self.log_text)

        log_layout.addWidget(log_group)

        # Add widgets to splitter
        splitter.addWidget(settings_widget)
        splitter.addWidget(log_widget)

        # Set initial sizes
        splitter.setSizes([600, 200])

        main_layout.addWidget(splitter, 1)

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

        self.verify_button = QPushButton("Verify Results")
        self.verify_button.clicked.connect(self.on_verify_results)
        self.verify_button.setEnabled(False)

        self.export_button = QPushButton("Export Results")
        self.export_button.clicked.connect(self.on_export_results)
        self.export_button.setEnabled(False)

        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.verify_button)
        buttons_layout.addWidget(self.export_button)

        main_layout.addWidget(buttons_widget)

    def create_detection_tab(self):
        """Create the detection settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Model selection group
        model_group = QGroupBox("Model Selection")
        model_layout = QGridLayout(model_group)

        # Detection model
        model_layout.addWidget(QLabel("Detection Model:"), 0, 0)
        self.det_model_combo = QComboBox()
        # Will be populated later with available models
        self.det_model_combo.addItem("MegaDetector 5a")
        self.det_model_combo.addItem("Custom Model")
        model_layout.addWidget(self.det_model_combo, 0, 1)

        # Detection model path (for custom model)
        model_layout.addWidget(QLabel("Custom Model Path:"), 1, 0)
        self.det_model_path = QLineEdit()
        self.det_model_path.setReadOnly(True)
        det_path_layout = QHBoxLayout()
        det_path_layout.addWidget(self.det_model_path)
        self.browse_det_model = QPushButton("Browse")
        self.browse_det_model.clicked.connect(self.on_browse_det_model)
        det_path_layout.addWidget(self.browse_det_model)
        model_layout.addLayout(det_path_layout, 1, 1)

        # Classification model
        model_layout.addWidget(QLabel("Classification Model:"), 2, 0)
        self.cls_model_combo = QComboBox()
        # Will be populated later with available models
        self.cls_model_combo.addItem("None")
        self.cls_model_combo.addItem("Species Classifier")
        model_layout.addWidget(self.cls_model_combo, 2, 1)

        # Hardware options
        model_layout.addWidget(QLabel("Hardware:"), 3, 0)
        self.disable_gpu = QCheckBox("Disable GPU")
        model_layout.addWidget(self.disable_gpu, 3, 1)

        layout.addWidget(model_group)

        # Threshold settings group
        threshold_group = QGroupBox("Threshold Settings")
        threshold_layout = QGridLayout(threshold_group)

        # Detection threshold
        threshold_layout.addWidget(QLabel("Detection Threshold:"), 0, 0)
        self.det_threshold_slider = RangeSlider(min_value=0.0, max_value=1.0, start_min=0.2, start_max=1.0)
        threshold_layout.addWidget(self.det_threshold_slider, 0, 1)
        self.det_threshold_value = QLabel("0.2")
        threshold_layout.addWidget(self.det_threshold_value, 0, 2)
        self.det_threshold_slider.valueChanged.connect(
            lambda min_val, max_val: self.det_threshold_value.setText(f"{min_val:.2f}")
        )

        # Classification threshold
        threshold_layout.addWidget(QLabel("Classification Threshold:"), 1, 0)
        self.cls_threshold_slider = RangeSlider(min_value=0.0, max_value=1.0, start_min=0.5, start_max=1.0)
        threshold_layout.addWidget(self.cls_threshold_slider, 1, 1)
        self.cls_threshold_value = QLabel("0.5")
        threshold_layout.addWidget(self.cls_threshold_value, 1, 2)
        self.cls_threshold_slider.valueChanged.connect(
            lambda min_val, max_val: self.cls_threshold_value.setText(f"{min_val:.2f}")
        )

        layout.addWidget(threshold_group)

        # Animal smoothening
        self.smooth_animal = QCheckBox("Smooth animal classifications across frames")
        layout.addWidget(self.smooth_animal)

        # Add spacer
        layout.addStretch()

        return tab

    def create_process_tab(self):
        """Create the process settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # File processing group
        file_group = QGroupBox("File Processing")
        file_layout = QGridLayout(file_group)

        # Process images checkbox
        self.process_images = QCheckBox("Process images")
        self.process_images.setChecked(True)
        file_layout.addWidget(self.process_images, 0, 0)

        # Process videos checkbox
        self.process_videos = QCheckBox("Process videos")
        self.process_videos.setChecked(True)
        file_layout.addWidget(self.process_videos, 0, 1)

        # Exclude subdirectories checkbox
        self.exclude_subdirs = QCheckBox("Exclude subdirectories")
        file_layout.addWidget(self.exclude_subdirs, 1, 0)

        # Absolute paths checkbox
        self.use_absolute_paths = QCheckBox("Use absolute paths in JSON")
        file_layout.addWidget(self.use_absolute_paths, 1, 1)

        layout.addWidget(file_group)

        # Video processing group
        video_group = QGroupBox("Video Processing")
        video_layout = QGridLayout(video_group)

        # Process every nth frame
        video_layout.addWidget(QLabel("Process every:"), 0, 0)
        self.frame_interval = QDoubleSpinBox()
        self.frame_interval.setRange(0.1, 60)
        self.frame_interval.setValue(1.0)
        self.frame_interval.setSuffix(" seconds")
        video_layout.addWidget(self.frame_interval, 0, 1)

        # Process all frames checkbox
        self.process_all_frames = QCheckBox("Process all frames")
        self.process_all_frames.stateChanged.connect(
            lambda state: self.frame_interval.setEnabled(not state)
        )
        video_layout.addWidget(self.process_all_frames, 1, 0, 1, 2)

        layout.addWidget(video_group)

        # Checkpoint settings group
        checkpoint_group = QGroupBox("Checkpoint Settings")
        checkpoint_layout = QGridLayout(checkpoint_group)

        # Use checkpoints checkbox
        self.use_checkpoints = QCheckBox("Use checkpoints")
        checkpoint_layout.addWidget(self.use_checkpoints, 0, 0)

        # Checkpoint frequency
        checkpoint_layout.addWidget(QLabel("Checkpoint every:"), 1, 0)
        self.checkpoint_freq = QSpinBox()
        self.checkpoint_freq.setRange(50, 5000)
        self.checkpoint_freq.setValue(500)
        self.checkpoint_freq.setSuffix(" images")
        self.checkpoint_freq.setEnabled(False)
        checkpoint_layout.addWidget(self.checkpoint_freq, 1, 1)

        # Continue from checkpoint checkbox
        self.continue_checkpoint = QCheckBox("Continue from checkpoint if available")
        self.continue_checkpoint.setEnabled(False)
        checkpoint_layout.addWidget(self.continue_checkpoint, 2, 0, 1, 2)

        # Connect checkpoint checkbox to enable/disable related inputs
        self.use_checkpoints.stateChanged.connect(self.on_checkpoint_changed)

        layout.addWidget(checkpoint_group)

        # Add spacer
        layout.addStretch()

        return tab

    def create_output_tab(self):
        """Create the output settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Post-processing group
        postprocess_group = QGroupBox("Post-processing")
        postprocess_layout = QGridLayout(postprocess_group)

        # Separate files by categories
        self.separate_files = QCheckBox("Separate files by categories")
        postprocess_layout.addWidget(self.separate_files, 0, 0, 1, 2)

        # Separate by confidence
        self.separate_confidence = QCheckBox("Separate by confidence level")
        postprocess_layout.addWidget(self.separate_confidence, 1, 0, 1, 2)

        # File placement options
        postprocess_layout.addWidget(QLabel("File placement:"), 2, 0)
        self.file_placement = QComboBox()
        self.file_placement.addItem("Move")
        self.file_placement.addItem("Copy")
        postprocess_layout.addWidget(self.file_placement, 2, 1)

        # Visualization options
        self.visualize_detections = QCheckBox("Draw bounding boxes")
        postprocess_layout.addWidget(self.visualize_detections, 3, 0)

        # Crop detections
        self.crop_detections = QCheckBox("Crop detections")
        postprocess_layout.addWidget(self.crop_detections, 3, 1)

        layout.addWidget(postprocess_group)

        # Export options group
        export_group = QGroupBox("Export Options")
        export_layout = QGridLayout(export_group)

        # Export results checkbox
        self.export_results = QCheckBox("Export results")
        export_layout.addWidget(self.export_results, 0, 0)

        # Export format
        export_layout.addWidget(QLabel("Export format:"), 1, 0)
        self.export_format = QComboBox()
        self.export_format.addItem("CSV")
        self.export_format.addItem("XLSX")
        self.export_format.addItem("COCO JSON")
        export_layout.addWidget(self.export_format, 1, 1)

        # Create plots checkbox
        self.create_plots = QCheckBox("Create analysis plots")
        export_layout.addWidget(self.create_plots, 2, 0, 1, 2)

        layout.addWidget(export_group)

        # Advanced options group
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QGridLayout(advanced_group)

        # Custom image size
        self.custom_image_size = QCheckBox("Custom image size:")
        advanced_layout.addWidget(self.custom_image_size, 0, 0)

        self.image_size = QSpinBox()
        self.image_size.setRange(320, 1920)
        self.image_size.setSingleStep(32)
        self.image_size.setValue(640)
        self.image_size.setEnabled(False)
        advanced_layout.addWidget(self.image_size, 0, 1)

        # Connect checkbox to enable/disable image size input
        self.custom_image_size.stateChanged.connect(
            lambda state: self.image_size.setEnabled(state)
        )

        layout.addWidget(advanced_group)

        # Add spacer
        layout.addStretch()

        return tab

    def on_checkpoint_changed(self, state):
        """Handle checkpoint checkbox state changes."""
        self.checkpoint_freq.setEnabled(state)
        self.continue_checkpoint.setEnabled(state)

    def on_browse_det_model(self):
        """Browse for custom detection model."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Detection Model", QDir.homePath(),
            "Model Files (*.pt *.pth *.weights);;All Files (*)"
        )

        if file_path:
            self.det_model_path.setText(file_path)
            # Select custom model in combo box
            self.det_model_combo.setCurrentIndex(1)  # "Custom Model" option

    def on_select_folder(self):
        """Handle folder selection button click."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder with Images/Videos", QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if folder:
            self.selected_folder = folder
            # Show only the folder name to keep UI clean
            folder_name = Path(folder).name
            self.folder_label.setText(f"{folder_name} ({folder})")
            self.folder_selected.emit(folder)
            self.start_button.setEnabled(True)
            self.status_label.setText("Folder selected. Ready to start detection.")
            self.add_log_message(f"Selected folder: {folder}")

    def on_start_detection(self):
        """Handle start detection button click."""
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        # Save settings before starting
        self.save_settings()

        # Create and show progress dialog
        self.progress_dialog = ProgressDialog("Detection Progress", self)
        self.progress_dialog.cancelRequested.connect(self.task_manager.cancel_task)
        self.progress_dialog.show()

        self.is_running = True
        self.start_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.folder_button.setEnabled(False)
        self.tab_widget.setEnabled(False)
        self.progress_bar.setValue(0)
        self.status_label.setText("Starting detection process...")
        self.add_log_message("Starting detection process...")
        self.detection_started.emit()

        # Start detection task with current settings
        self.task_manager.run_task("detection", {
            "folder_path": self.selected_folder,
            "simple_mode": False  # Using advanced settings
        })

    def on_cancel(self):
        """Handle cancel button click."""
        if self.is_running:
            reply = QMessageBox.question(
                self, "Confirm Cancel",
                "Are you sure you want to cancel the detection process?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.status_label.setText("Cancelling detection process...")
                self.add_log_message("Cancelling detection process...")
                self.task_manager.cancel_task()

    def on_verify_results(self):
        """Handle verify results button click."""
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder with detection results first.")
            return

        # Check if detection files exist
        image_json = os.path.join(self.selected_folder, "image_recognition_file.json")
        video_json = os.path.join(self.selected_folder, "video_recognition_file.json")

        if not (os.path.isfile(image_json) or os.path.isfile(video_json)):
            QMessageBox.warning(self, "Warning", "No detection results found in the selected folder.")
            return

        # Show verification dialog
        dialog = VerificationDialog(self.selected_folder, self)
        dialog.startVerification.connect(self.on_start_verification)
        dialog.exec()

    def on_export_results(self):
        """Handle export results button click."""
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder with detection results first.")
            return

        # Check if detection files exist
        image_json = os.path.join(self.selected_folder, "image_recognition_file.json")
        video_json = os.path.join(self.selected_folder, "video_recognition_file.json")

        if not (os.path.isfile(image_json) or os.path.isfile(video_json)):
            QMessageBox.warning(self, "Warning", "No detection results found in the selected folder.")
            return

        # Show export dialog
        dialog = ExportDialog(self.selected_folder, self)
        dialog.startExport.connect(self.on_start_export)
        dialog.exec()

        # Select destination folder
        dst_dir = QFileDialog.getExistingDirectory(
            self, "Select Destination Folder for Exports", QDir.homePath(),
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not dst_dir:
            return

        # Get export settings from UI
        export_params = {
            "src_dir": self.selected_folder,
            "dst_dir": dst_dir,
            "thresh": float(self.det_threshold_value.text()),
            "separate": self.separate_files.isChecked(),
            "file_mode": 1 if self.file_placement.currentText() == "Move" else 2,
            "sep_conf": self.separate_confidence.isChecked(),
            "visualize": self.visualize_detections.isChecked(),
            "crop": self.crop_detections.isChecked(),
            "export": self.export_results.isChecked(),
            "plot": self.create_plots.isChecked(),
            "export_format": self.export_format.currentText(),
            "data_type": "img"  # Start with images
        }

        # Start postprocessing task
        self.task_manager.run_task("postprocessing", export_params)

        self.status_label.setText("Starting export process...")
        self.add_log_message(f"Exporting results to: {dst_dir}")

    def add_log_message(self, message):
        """Add a message to the log text area."""
        self.log_text.append(message)
        # Scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def on_task_started(self, task):
        """Handle task started event."""
        if task == "detection":
            self.status_label.setText("Detection process started...")
            self.add_log_message("Detection process started")
        elif task == "postprocessing":
            self.status_label.setText("Export process started...")
            self.add_log_message("Export process started")

    def on_task_progress(self, task, status, progress, message, details):
        """Handle task progress updates."""
        if task in ["detection", "postprocessing", "verification"]:
            if progress >= 0:
                self.progress_bar.setValue(progress)
            else:
                # Indeterminate progress
                self.progress_bar.setRange(0, 0)

            self.status_label.setText(message)
            if details:
                self.add_log_message(details)

            # Update progress dialog if it exists
            if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
                self.progress_dialog.update_progress(
                    task_name=task.capitalize(),
                    status=status,
                    progress=progress,
                    message=message,
                    details=details
                )

    def on_task_completed(self, task, success, results):
        """Handle task completion."""
        if task == "detection":
            self.is_running = False
            self.start_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.folder_button.setEnabled(True)
            self.tab_widget.setEnabled(True)
            self.progress_bar.setRange(0, 100)

            # Update progress dialog
            if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
                self.progress_dialog.update_progress(
                    task_name="Detection",
                    status="done",
                    progress=100,
                    message="Detection completed successfully!" if success else "Detection failed.",
                    details=""
                )

            if success:
                self.progress_bar.setValue(100)
                self.status_label.setText("Detection completed successfully!")
                self.add_log_message("Detection process completed successfully")
                self.verify_button.setEnabled(True)
                self.export_button.setEnabled(True)
            else:
                if results.get("aborted", False):
                    self.status_label.setText("Detection process was cancelled.")
                    self.add_log_message("Detection process was cancelled by user")
                else:
                    self.status_label.setText("Detection process failed.")
                    self.add_log_message("Detection process failed")

            self.detection_completed.emit(success)

        elif task == "postprocessing":
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            # Update progress dialog
            if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
                self.progress_dialog.update_progress(
                    task_name="Export",
                    status="done",
                    progress=100,
                    message="Export completed successfully!" if success else "Export failed.",
                    details=""
                )

            if success:
                self.status_label.setText("Export completed successfully!")
                self.add_log_message("Export process completed successfully")

                # Open destination folder
                dst_dir = results.get("dst_dir")
                if dst_dir and os.path.isdir(dst_dir):
                    from AddaxAI.backend.utils import open_file_or_folder
                    open_file_or_folder(dst_dir)
            else:
                self.status_label.setText("Export process failed.")
                self.add_log_message("Export process failed")

        elif task == "verification":
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(100)

            # Update progress dialog
            if hasattr(self, 'progress_dialog') and self.progress_dialog.isVisible():
                self.progress_dialog.update_progress(
                    task_name="Verification",
                    status="done",
                    progress=100,
                    message="Verification setup completed!" if success else "Verification setup failed.",
                    details=""
                )

            if success:
                # Get verification result
                result = results.get("result", {})
                total_files = result.get("total_files", 0)

                if total_files > 0:
                    self.status_label.setText(f"Verification setup completed with {total_files} files.")
                    self.add_log_message(f"Verification setup completed with {total_files} files.")

                    # Start human verification tool based on action
                    action = results.get("action")
                    if action == "prepare":
                        # Check if we should start verification immediately
                        self.task_manager.run_task("verification", {
                            "folder_path": self.selected_folder,
                            "action": "start"
                        })
                else:
                    self.status_label.setText("No files match the verification criteria.")
                    self.add_log_message("No files match the verification criteria.")
            else:
                self.status_label.setText("Verification setup failed.")
                self.add_log_message("Verification setup failed.")

    def on_task_error(self, task, error_message):
        """Handle task errors."""
        if task in ["detection", "postprocessing"]:
            self.is_running = False
            self.start_button.setEnabled(True)
            self.cancel_button.setEnabled(False)
            self.folder_button.setEnabled(True)
            self.tab_widget.setEnabled(True)
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setValue(0)

            self.status_label.setText(f"Error during {task}")
            self.add_log_message(f"ERROR: {error_message}")

            QMessageBox.critical(
                self,
                f"{task.capitalize()} Error",
                f"An error occurred during {task}:\n\n{error_message}"
            )

            if task == "detection":
                self.detection_completed.emit(False)

    def load_settings(self):
        """Load settings from global variables."""
        try:
            global_vars = load_global_vars()

            # Detection model
            det_model_idx = global_vars.get('var_det_model_idx', 0)
            if det_model_idx >= len(self.det_model_combo) - 1:
                # Custom model
                self.det_model_combo.setCurrentIndex(1)
                self.det_model_path.setText(global_vars.get('var_det_model_path', ''))
            else:
                self.det_model_combo.setCurrentIndex(det_model_idx)

            # Classification model
            cls_model_idx = global_vars.get('var_cls_model_idx', 0)
            self.cls_model_combo.setCurrentIndex(min(cls_model_idx, len(self.cls_model_combo) - 1))

            # Hardware
            self.disable_gpu.setChecked(global_vars.get('var_disable_GPU', False))

            # Thresholds
            self.det_threshold_slider.set_values(global_vars.get('var_cls_detec_thresh', 0.2), 1.0)
            self.det_threshold_value.setText(f"{global_vars.get('var_cls_detec_thresh', 0.2):.2f}")

            self.cls_threshold_slider.set_values(global_vars.get('var_cls_class_thresh', 0.5), 1.0)
            self.cls_threshold_value.setText(f"{global_vars.get('var_cls_class_thresh', 0.5):.2f}")

            # Animal smoothening
            self.smooth_animal.setChecked(global_vars.get('var_smooth_cls_animal', False))

            # File processing
            self.process_images.setChecked(global_vars.get('var_process_img', True))
            self.process_videos.setChecked(global_vars.get('var_process_vid', True))
            self.exclude_subdirs.setChecked(global_vars.get('var_exclude_subs', False))
            self.use_absolute_paths.setChecked(global_vars.get('var_abs_paths', False))

            # Video processing
            self.process_all_frames.setChecked(not global_vars.get('var_not_all_frames', True))
            self.frame_interval.setValue(float(global_vars.get('var_nth_frame', 1.0)))
            self.frame_interval.setEnabled(global_vars.get('var_not_all_frames', True))

            # Checkpoint settings
            self.use_checkpoints.setChecked(global_vars.get('var_use_checkpnts', False))
            self.checkpoint_freq.setValue(int(global_vars.get('var_checkpoint_freq', 500)))
            self.continue_checkpoint.setChecked(global_vars.get('var_cont_checkpnt', False))
            self.checkpoint_freq.setEnabled(global_vars.get('var_use_checkpnts', False))
            self.continue_checkpoint.setEnabled(global_vars.get('var_use_checkpnts', False))

            # Post-processing
            self.separate_files.setChecked(global_vars.get('var_postprocess_sep', False))
            self.separate_confidence.setChecked(global_vars.get('var_postprocess_sep_conf', False))
            self.file_placement.setCurrentIndex(int(global_vars.get('var_postprocess_file_placement', 1)) - 1)
            self.visualize_detections.setChecked(global_vars.get('var_postprocess_vis', False))
            self.crop_detections.setChecked(global_vars.get('var_postprocess_crp', False))

            # Export options
            self.export_results.setChecked(global_vars.get('var_postprocess_exp', False))
            export_format = global_vars.get('var_postprocess_exp_format', 'CSV')
            for i in range(self.export_format.count()):
                if self.export_format.itemText(i) == export_format:
                    self.export_format.setCurrentIndex(i)
                    break
            self.create_plots.setChecked(global_vars.get('var_postprocess_plt', False))

            # Advanced options
            self.custom_image_size.setChecked(global_vars.get('var_use_custom_img_size_for_deploy', False))
            self.image_size.setValue(int(global_vars.get('var_image_size_for_deploy', 640)))
            self.image_size.setEnabled(global_vars.get('var_use_custom_img_size_for_deploy', False))

        except Exception as e:
            self.add_log_message(f"Error loading settings: {str(e)}")

    def save_settings(self):
        """Save current settings to global variables."""
        try:
            settings = {}

            # Detection model
            settings['var_det_model_idx'] = self.det_model_combo.currentIndex()
            if self.det_model_combo.currentIndex() == 1:  # Custom model
                settings['var_det_model_path'] = self.det_model_path.text()

            # Classification model
            settings['var_cls_model_idx'] = self.cls_model_combo.currentIndex()

            # Hardware
            settings['var_disable_GPU'] = self.disable_gpu.isChecked()

            # Thresholds
            settings['var_cls_detec_thresh'] = float(self.det_threshold_value.text())
            settings['var_cls_class_thresh'] = float(self.cls_threshold_value.text())

            # Animal smoothening
            settings['var_smooth_cls_animal'] = self.smooth_animal.isChecked()

            # File processing
            settings['var_process_img'] = self.process_images.isChecked()
            settings['var_process_vid'] = self.process_videos.isChecked()
            settings['var_exclude_subs'] = self.exclude_subdirs.isChecked()
            settings['var_abs_paths'] = self.use_absolute_paths.isChecked()

            # Video processing
            settings['var_not_all_frames'] = not self.process_all_frames.isChecked()
            settings['var_nth_frame'] = str(self.frame_interval.value())

            # Checkpoint settings
            settings['var_use_checkpnts'] = self.use_checkpoints.isChecked()
            settings['var_checkpoint_freq'] = str(self.checkpoint_freq.value())
            settings['var_cont_checkpnt'] = self.continue_checkpoint.isChecked()

            # Post-processing
            settings['var_postprocess_sep'] = self.separate_files.isChecked()
            settings['var_postprocess_sep_conf'] = self.separate_confidence.isChecked()
            settings['var_postprocess_file_placement'] = 1 if self.file_placement.currentText() == "Move" else 2
            settings['var_postprocess_vis'] = self.visualize_detections.isChecked()
            settings['var_postprocess_crp'] = self.crop_detections.isChecked()

            # Export options
            settings['var_postprocess_exp'] = self.export_results.isChecked()
            settings['var_postprocess_exp_format'] = self.export_format.currentText()
            settings['var_postprocess_plt'] = self.create_plots.isChecked()

            # Advanced options
            settings['var_use_custom_img_size_for_deploy'] = self.custom_image_size.isChecked()
            settings['var_image_size_for_deploy'] = str(self.image_size.value())

            # Save settings
            write_global_vars(settings)

        except Exception as e:
            self.add_log_message(f"Error saving settings: {str(e)}")

    def on_start_verification(self, verification_params):
        """Start verification with the provided parameters.

        Args:
            verification_params: Dictionary with verification parameters
        """
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog("Verification Setup", self)
        self.progress_dialog.cancelRequested.connect(self.task_manager.cancel_task)
        self.progress_dialog.show()

        self.status_label.setText("Setting up verification...")
        self.add_log_message("Setting up verification...")

        # Start verification setup task
        self.task_manager.run_task("verification", {
            "folder_path": self.selected_folder,
            "action": "prepare",
            "selection_criteria": verification_params
        })

    def on_start_export(self, export_params):
        """Start export with the provided parameters.

        Args:
            export_params: Dictionary with export parameters
        """
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog("Export Progress", self)
        self.progress_dialog.cancelRequested.connect(self.task_manager.cancel_task)
        self.progress_dialog.show()

        self.status_label.setText("Starting export process...")
        self.add_log_message(f"Exporting results to: {export_params['dst_dir']}")

        # Start postprocessing task
        self.task_manager.run_task("postprocessing", export_params)
