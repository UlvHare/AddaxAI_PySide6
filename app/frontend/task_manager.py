# frontend/task_manager.py
from PySide6.QtCore import QObject, Signal, Slot, QThread, QMutex, QWaitCondition
import time
import traceback
import os
import sys
import logging
from pathlib import Path

# Import the backend adapter
from app.frontend.backend_adapter import (
    run_wild_animal_detection, 
    process_results,
    setup_verification, 
    start_verification_tool
)

# Configure logging
logger = logging.getLogger(__name__)

class TaskWorker(QThread):
    """Worker thread to handle long-running tasks."""
    
    taskStarted = Signal(str)
    taskProgress = Signal(str, str, int, str, str)  # task, status, progress, message, details
    taskCompleted = Signal(str, bool, object)  # task, success, results
    taskError = Signal(str, str)  # task, error_message
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.abort = False
        self.restart = False
        self.task = None
        self.params = None
    
    def run_task(self, task, params):
        """Set up a task to run.
        
        Args:
            task: String identifier for the task
            params: Dictionary of parameters for the task
        """
        locker = QMutex()
        locker.lock()
        self.task = task
        self.params = params
        self.restart = True
        self.condition.wakeOne()
        locker.unlock()
        
        if not self.isRunning():
            self.start(QThread.LowestPriority)
    
    def cancel_task(self):
        """Cancel the current task."""
        self.mutex.lock()
        self.abort = True
        self.mutex.unlock()
    
    def run(self):
        """Main worker loop."""
        while True:
            self.mutex.lock()
            task = self.task
            params = self.params
            self.mutex.unlock()
            
            if task:
                self.taskStarted.emit(task)
                
                try:
                    # Run the appropriate task
                    if task == "detection":
                        self.run_detection(params)
                    elif task == "postprocessing":
                        self.run_postprocessing(params)
                    elif task == "verification":
                        self.run_verification(params)
                    else:
                        # Unknown task
                        self.taskError.emit(task, f"Unknown task type: {task}")
                except Exception as e:
                    # Handle task error
                    error_msg = str(e)
                    tb = traceback.format_exc()
                    logger.error(f"Task error ({task}): {error_msg}\n{tb}")
                    self.taskError.emit(task, f"{error_msg}\n\n{tb}")
            
            # Wait for next task
            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.abort = False
            self.task = None
            self.mutex.unlock()
    
    def check_abort(self):
        """Check if the task was aborted.
        
        Returns:
            bool: True if the task was aborted
        """
        self.mutex.lock()
        abort = self.abort
        self.mutex.unlock()
        return abort
    
    def emit_progress(self, task, status, progress, message, details):
        """Emit progress signal with standardized parameters."""
        self.taskProgress.emit(task, status, progress, message, details)
    
    def run_detection(self, params):
        """Run animal detection task.
        
        Args:
            params: Dictionary with parameters:
                - folder_path: Path to folder containing images/videos
                - simple_mode: Whether to use simple mode settings
        """
        folder_path = params.get("folder_path")
        simple_mode = params.get("simple_mode", True)
        
        if not folder_path or not os.path.isdir(folder_path):
            self.taskError.emit("detection", f"Invalid folder path: {folder_path}")
            return
        
        # Setup progress callback
        def progress_callback(item_count, total_items, message, data_type=None):
            if self.check_abort():
                return True  # Signal to abort
            
            progress = int((item_count / max(total_items, 1)) * 100) if total_items > 0 else -1
            details = f"Processing {data_type or 'item'} {item_count} of {total_items}: {message}"
            
            self.emit_progress(
                "detection", 
                "running", 
                progress, 
                f"Processed {item_count} of {total_items} items", 
                details
            )
            
            return False  # Continue processing
        
        try:
            # Update UI with starting message
            self.emit_progress(
                "detection", 
                "starting", 
                0, 
                "Starting detection process...", 
                f"Analyzing folder: {folder_path}"
            )
            
            # Call backend detection function with callback
            result = run_wild_animal_detection(
                input_dir=folder_path,
                progress_callback=progress_callback,
                simple_mode=simple_mode
            )
            
            # Check if aborted
            if self.check_abort():
                self.taskCompleted.emit("detection", False, {"aborted": True})
                return
            
            # Task completed successfully
            self.taskCompleted.emit("detection", True, {"result": result})
            
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            logger.error(f"Detection error: {error_msg}\n{tb}")
            self.taskError.emit("detection", f"{error_msg}\n\n{tb}")
    
    def run_postprocessing(self, params):
        """Run postprocessing task for export/visualization.
        
        Args:
            params: Dictionary with export parameters
        """
        src_dir = params.get("src_dir")
        dst_dir = params.get("dst_dir")
        
        if not src_dir or not os.path.isdir(src_dir):
            self.taskError.emit("postprocessing", f"Invalid source directory: {src_dir}")
            return
            
        if not dst_dir or not os.path.isdir(dst_dir):
            self.taskError.emit("postprocessing", f"Invalid destination directory: {dst_dir}")
            return
        
        # Setup progress callback
        def progress_callback(item_count, total_items, message, data_type=None):
            if self.check_abort():
                return True  # Signal to abort
            
            progress = int((item_count / max(total_items, 1)) * 100) if total_items > 0 else -1
            details = f"Processing {data_type or 'item'} {item_count} of {total_items}: {message}"
            
            self.emit_progress(
                "postprocessing", 
                "running", 
                progress, 
                f"Processed {item_count} of {total_items} items", 
                details
            )
            
            return False  # Continue processing
        
        try:
            # Update UI with starting message
            self.emit_progress(
                "postprocessing", 
                "starting", 
                0, 
                "Starting export process...", 
                f"Exporting from {src_dir} to {dst_dir}"
            )
            
            # Add the callback to params
            params["progress_callback"] = progress_callback
            
            # Call backend processing function
            result = process_results(**params)
            
            # Check if aborted
            if self.check_abort():
                self.taskCompleted.emit("postprocessing", False, {"aborted": True})
                return
            
            # Add destination to result
            result["dst_dir"] = dst_dir
            
            # Task completed successfully
            self.taskCompleted.emit("postprocessing", True, result)
            
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            logger.error(f"Postprocessing error: {error_msg}\n{tb}")
            self.taskError.emit("postprocessing", f"{error_msg}\n\n{tb}")
    
    def run_verification(self, params):
        """Run verification setup and tool.
        
        Args:
            params: Dictionary with verification parameters
        """
        folder_path = params.get("folder_path")
        action = params.get("action")  # "prepare" or "start"
        
        if not folder_path or not os.path.isdir(folder_path):
            self.taskError.emit("verification", f"Invalid folder path: {folder_path}")
            return
        
        # Setup progress callback
        def progress_callback(item_count, total_items, message, data_type=None):
            if self.check_abort():
                return True  # Signal to abort
            
            progress = int((item_count / max(total_items, 1)) * 100) if total_items > 0 else -1
            details = f"Processing {data_type or 'item'} {item_count} of {total_items}: {message}"
            
            self.emit_progress(
                "verification", 
                "running", 
                progress, 
                f"Processed {item_count} of {total_items} items", 
                details
            )
            
            return False  # Continue processing
        
        try:
            if action == "prepare":
                # Update UI with starting message
                self.emit_progress(
                    "verification", 
                    "starting", 
                    0, 
                    "Preparing verification...", 
                    f"Setting up verification for folder: {folder_path}"
                )
                
                # Get selection criteria
                selection_criteria = params.get("selection_criteria", {})
                
                # Call backend setup function
                result = setup_verification(
                    folder_path=folder_path,
                    selection_criteria=selection_criteria,
                    progress_callback=progress_callback
                )
                
                # Check if aborted
                if self.check_abort():
                    self.taskCompleted.emit("verification", False, {"aborted": True})
                    return
                
                # Task completed successfully
                self.taskCompleted.emit(
                    "verification", 
                    True, 
                    {"result": result, "action": "prepare"}
                )
                
            elif action == "start":
                # Update UI with starting message
                self.emit_progress(
                    "verification", 
                    "starting", 
                    0, 
                    "Starting verification tool...", 
                    f"Opening verification tool for folder: {folder_path}"
                )
                
                # Call backend verification tool
                result = start_verification_tool(folder_path)
                
                # Task completed successfully
                self.taskCompleted.emit(
                    "verification", 
                    True, 
                    {"result": result, "action": "start"}
                )
                
            else:
                self.taskError.emit(
                    "verification", 
                    f"Invalid verification action: {action}"
                )
                
        except Exception as e:
            error_msg = str(e)
            tb = traceback.format_exc()
            logger.error(f"Verification error: {error_msg}\n{tb}")
            self.taskError.emit("verification", f"{error_msg}\n\n{tb}")


class TaskManager(QObject):
    """Manager for handling background tasks."""
    
    taskStarted = Signal(str)
    taskProgress = Signal(str, str, int, str, str)  # task, status, progress, message, details
    taskCompleted = Signal(str, bool, object)  # task, success, results
    taskError = Signal(str, str)  # task, error_message
    
    def __init__(self, parent=None, error_handler=None):
        super().__init__(parent)
        
        # Save error handler reference
        self.error_handler = error_handler
        
        # Create worker thread
        self.worker = TaskWorker()
        
        # Connect worker signals to manager signals
        self.worker.taskStarted.connect(self.on_task_started)
        self.worker.taskProgress.connect(self.on_task_progress)
        self.worker.taskCompleted.connect(self.on_task_completed)
        self.worker.taskError.connect(self.on_task_error)

    
    def run_task(self, task, params=None):
        """Run a task in the background.
        
        Args:
            task: String identifier for the task
            params: Dictionary of parameters for the task
        """
        if params is None:
            params = {}
            
        self.worker.run_task(task, params)
    
    def cancel_task(self):
        """Cancel the current task."""
        self.worker.cancel_task()
    
    @Slot(str)
    def on_task_started(self, task):
        """Handle task started event."""
        self.taskStarted.emit(task)
    
    @Slot(str, str, int, str, str)
    def on_task_progress(self, task, status, progress, message, details):
        """Handle task progress event."""
        self.taskProgress.emit(task, status, progress, message, details)
    
    @Slot(str, bool, object)
    def on_task_completed(self, task, success, results):
        """Handle task completion event."""
        self.taskCompleted.emit(task, success, results)
    
    @Slot(str, str)
    def on_task_error(self, task, error_message):
        """Handle task error event."""
        # Emit signal
        self.taskError.emit(task, error_message)
        
        # Use error handler if available
        if self.error_handler:
            self.error_handler.handle_task_error(task, error_message, self.parent())
            
