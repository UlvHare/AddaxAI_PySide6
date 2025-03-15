# app/frontend/backend_adapter.py
"""
Adapter module to integrate the PySide6 GUI with the original AddaxAI backend.
This adapter provides a clean interface between the new GUI and the existing code.
"""

import os
import sys
import traceback
import logging
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

# Get paths from backend
try:
    from app.backend import (
        AddaxAI_files, CLS_DIR, DET_DIR,
        current_EA_version, green_primary, yellow_primary,
        IMG_EXTENSIONS, VIDEO_EXTENSIONS
    )
except ImportError as e:
    logger.error(f"Error importing backend modules: {e}")
    raise


def run_wild_animal_detection(input_dir, progress_callback=None, simple_mode=True, **kwargs):
    """Run wild animal detection with progress reporting.
    
    Args:
        input_dir: Directory containing images/videos
        progress_callback: Function to report progress
        simple_mode: Use simplified settings (True) or advanced settings (False)
        kwargs: Additional parameters for detection
        
    Returns:
        dict: Results of the detection process
    """
    try:
        # Import wild_animal_detection module
        from app.backend.wild_animal_detection import deploy
        
        # Create adapter for callback to normalize progress reporting
        if progress_callback:
            def adapted_callback(current, total, message, item_type=None):
                # Convert callback format for our GUI
                return progress_callback(current, total, message, item_type)
        else:
            adapted_callback = None
            
        # Run detection with callback
        result = deploy.run_wild_animal_detection(
            input_dir=input_dir,
            progress_callback=adapted_callback,
            simple_mode=simple_mode,
            **kwargs
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error running detection: {e}\n{traceback.format_exc()}")
        raise


def process_results(src_dir, dst_dir, thresh=0.2, separate=False, file_mode=2, 
                   sep_conf=False, visualize=False, crop=False, export=False, 
                   plot=False, export_format="CSV", progress_callback=None, **kwargs):
    """Process detection results with options for exporting, visualization, etc.
    
    Args:
        src_dir: Source directory with detection results
        dst_dir: Destination directory for output
        thresh: Confidence threshold for detection
        separate: Whether to separate files by categories
        file_mode: 1=Move, 2=Copy
        sep_conf: Separate by confidence levels
        visualize: Draw bounding boxes
        crop: Crop detections
        export: Export data to files
        plot: Create analysis plots
        export_format: Format for data export (CSV, XLSX, COCO JSON)
        progress_callback: Function to report progress
        
    Returns:
        dict: Results of the processing
    """
    try:
        # Import postprocessing module
        from app.backend.postprocess import process
        
        # Create adapter for callback
        if progress_callback:
            def adapted_callback(current, total, message, item_type=None):
                # Convert callback format for our GUI
                return progress_callback(current, total, message, item_type)
        else:
            adapted_callback = None
            
        # Run processing
        result = process.process_results(
            src_dir=src_dir,
            dst_dir=dst_dir,
            threshold=thresh,
            separate=separate,
            file_mode=file_mode,
            separate_by_confidence=sep_conf,
            visualize=visualize,
            crop=crop,
            export=export,
            create_plots=plot,
            export_format=export_format.lower(),
            progress_callback=adapted_callback,
            **kwargs
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing results: {e}\n{traceback.format_exc()}")
        raise


def setup_verification(folder_path, selection_criteria, progress_callback=None):
    """Setup human verification with selected criteria.
    
    Args:
        folder_path: Path to folder with detection results
        selection_criteria: Dictionary with verification parameters
        progress_callback: Function to report progress
        
    Returns:
        dict: Results of the verification setup
    """
    try:
        # Import human verification module
        from app.backend.human_verification import verification
        
        # Create adapter for callback
        if progress_callback:
            def adapted_callback(current, total, message, item_type=None):
                # Convert callback format for our GUI
                return progress_callback(current, total, message, item_type)
        else:
            adapted_callback = None
            
        # Setup verification
        result = verification.setup_verification(
            folder_path=folder_path,
            criteria=selection_criteria,
            progress_callback=adapted_callback
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error setting up verification: {e}\n{traceback.format_exc()}")
        raise


def start_verification_tool(folder_path):
    """Start the human verification tool.
    
    Args:
        folder_path: Path to folder with prepared verification data
        
    Returns:
        dict: Status of the verification tool launch
    """
    try:
        # Import human verification module
        from app.backend.human_verification import verification
        
        # Launch verification tool
        result = verification.start_verification_tool(folder_path)
        
        return result
        
    except Exception as e:
        logger.error(f"Error starting verification tool: {e}\n{traceback.format_exc()}")
        raise


def load_global_vars():
    """Load global variables from settings file.
    
    Returns:
        dict: Global variables
    """
    try:
        from app.backend.utils import settings
        return settings.load_global_vars()
    except Exception as e:
        logger.error(f"Error loading global variables: {e}\n{traceback.format_exc()}")
        return {}


def write_global_vars(variables):
    """Write global variables to settings file.
    
    Args:
        variables: Dictionary of variables to save
    """
    try:
        from app.backend.utils import settings
        settings.write_global_vars(variables)
    except Exception as e:
        logger.error(f"Error writing global variables: {e}\n{traceback.format_exc()}")


def fetch_label_map_from_json(json_file):
    """Extract label map from detection results JSON file.
    
    Args:
        json_file: Path to JSON file with detection results
        
    Returns:
        dict: Mapping of class IDs to class names
    """
    try:
        from app.backend.utils import json_utils
        return json_utils.fetch_label_map_from_json(json_file)
    except Exception as e:
        logger.error(f"Error fetching label map: {e}\n{traceback.format_exc()}")
        # Return default map as fallback
        return {
            "1": "Animal",
            "2": "Person",
            "3": "Vehicle"
        }


def open_file_or_folder(path):
    """Open a file or folder using the default system application.
    
    Args:
        path: Path to file or folder
    """
    try:
        from app.backend.utils import file_utils
        file_utils.open_file_or_folder(path)
    except Exception as e:
        logger.error(f"Error opening file/folder: {e}\n{traceback.format_exc()}")
        
        # Fallback implementation
        import os
        import platform
        import subprocess
        
        path = os.path.normpath(path)
        
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", path])
            else:  # Linux
                subprocess.call(["xdg-open", path])
        except Exception as e:
            logger.error(f"Fallback file/folder open failed: {e}")


def get_system_fonts():
    """Get system fonts appropriate for the current platform.
    
    Returns:
        tuple: (sans_font, serif_font, mono_font)
    """
    import platform
    
    system = platform.system()
    
    if system == "Linux":
        return "sans", "serif", "monospace"
    elif system == "Darwin":  # macOS
        return "SF Pro", "New York", "SF Mono"
    else:  # Windows
        return "Segoe UI", "Times New Roman", "Consolas"
        
