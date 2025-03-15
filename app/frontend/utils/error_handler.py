# app/frontend/utils/error_handler.py
"""
Centralized error handling for AddaxAI GUI
"""

import sys
import traceback
import logging
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)

class ErrorHandler(QObject):
    """Centralized error handler for the application."""
    
    errorOccurred = Signal(str, str, str)  # error_type, title, message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Connect to global excepthook
        sys.excepthook = self.handle_global_exception
    
    def handle_global_exception(self, exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions from the application.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        # Log the error
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Format traceback as string
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Emit signal for UI handling
        self.errorOccurred.emit(
            exc_type.__name__,
            "Application Error",
            f"{str(exc_value)}\n\nPlease report this issue with the log file."
        )
        
        # Don't exit - let the application decide how to handle it
    
    def show_error_dialog(self, error_type, title, message, parent=None):
        """Show error dialog to the user.
        
        Args:
            error_type: Type of error (string)
            title: Dialog title
            message: Error message
            parent: Parent widget
        """
        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Critical)
        dialog.setWindowTitle(title)
        dialog.setText(message)
        dialog.setDetailedText(f"Error type: {error_type}")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()
    
    def handle_task_error(self, task, error_message, parent=None):
        """Handle errors from background tasks.
        
        Args:
            task: Task identifier
            error_message: Error message
            parent: Parent widget
        """
        # Log the error
        logger.error(f"Task error in '{task}': {error_message}")
        
        # Show dialog
        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Warning)
        dialog.setWindowTitle("Task Error")
        dialog.setText(f"An error occurred during the {task} task.")
        dialog.setDetailedText(error_message)
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()
    
    def handle_backend_not_available(self, feature, parent=None):
        """Handle case when backend feature is not available.
        
        Args:
            feature: Feature name
            parent: Parent widget
        """
        # Log the error
        logger.warning(f"Backend feature not available: {feature}")
        
        # Show dialog
        dialog = QMessageBox(parent)
        dialog.setIcon(QMessageBox.Information)
        dialog.setWindowTitle("Feature Not Available")
        dialog.setText(f"The {feature} feature is not available in this environment.")
        dialog.setInformativeText("This may be due to missing dependencies or an incomplete installation.")
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.exec()
