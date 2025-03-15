# app/frontend/utils/state_manager.py
"""
Application state management and recovery system
"""

import os
import json
import logging
from pathlib import Path
import platform
from datetime import datetime
import tempfile
import shutil

logger = logging.getLogger(__name__)

class StateManager:
    """Manages application state and provides recovery mechanisms."""
    
    def __init__(self):
        # Determine state file location based on platform
        if platform.system() == "Windows":
            state_dir = os.path.join(os.environ["APPDATA"], "AddaxAI")
        elif platform.system() == "Darwin":  # macOS
            state_dir = os.path.join(os.path.expanduser("~/Library/Application Support"), "AddaxAI")
        else:  # Linux
            state_dir = os.path.join(os.path.expanduser("~/.config"), "AddaxAI")
        
        # Create directory if it doesn't exist
        os.makedirs(state_dir, exist_ok=True)
        
        self.state_file = os.path.join(state_dir, "app_state.json")
        self.temp_dir = os.path.join(tempfile.gettempdir(), "AddaxAI")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize state
        self.state = self._load_state()
    
    def _load_state(self):
        """Load application state from file.
        
        Returns:
            dict: Application state
        """
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {
                "last_used_folders": [],
                "recent_projects": [],
                "settings": {
                    "theme": "system",
                    "language": "en",
                    "auto_save": True,
                    "check_updates": True
                },
                "window": {
                    "width": 1000,
                    "height": 700,
                    "maximized": False
                },
                "last_mode": "simple",  # "simple" or "advanced"
                "crash_recovery": {
                    "has_unsaved_changes": False,
                    "last_folder": None,
                    "last_operation": None,
                    "timestamp": None
                }
            }
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return self._get_default_state()
    
    def _get_default_state(self):
        """Get default application state.
        
        Returns:
            dict: Default state
        """
        return {
            "last_used_folders": [],
            "recent_projects": [],
            "settings": {
                "theme": "system",
                "language": "en",
                "auto_save": True,
                "check_updates": True
            },
            "window": {
                "width": 1000,
                "height": 700,
                "maximized": False
            },
            "last_mode": "simple",
            "crash_recovery": {
                "has_unsaved_changes": False,
                "last_folder": None,
                "last_operation": None,
                "timestamp": None
            }
        }
    
    def save_state(self):
        """Save current application state to file."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2)
            logger.debug("Application state saved")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def get_setting(self, key, default=None):
        """Get setting value.
        
        Args:
            key: Setting name
            default: Default value if setting not found
            
        Returns:
            Setting value
        """
        return self.state.get("settings", {}).get(key, default)
    
    def set_setting(self, key, value):
        """Set setting value.
        
        Args:
            key: Setting name
            value: Setting value
        """
        if "settings" not in self.state:
            self.state["settings"] = {}
        self.state["settings"][key] = value
    
    def add_recent_folder(self, folder_path):
        """Add folder to recent folders list.
        
        Args:
            folder_path: Path to folder
        """
        if not folder_path:
            return
            
        # Normalize path
        folder_path = os.path.normpath(folder_path)
        
        # Get current list and remove existing entry if present
        folders = self.state.get("last_used_folders", [])
        if folder_path in folders:
            folders.remove(folder_path)
        
        # Add to beginning of list
        folders.insert(0, folder_path)
        
        # Keep only last 10 folders
        self.state["last_used_folders"] = folders[:10]
    
    def get_recent_folders(self, max_count=10):
        """Get list of recent folders.
        
        Args:
            max_count: Maximum number of folders to return
            
        Returns:
            list: List of folder paths
        """
        folders = self.state.get("last_used_folders", [])
        
        # Filter out non-existent folders
        existing_folders = [f for f in folders if os.path.isdir(f)]
        
        return existing_folders[:max_count]
    
    def set_window_geometry(self, width, height, maximized=False):
        """Save window geometry.
        
        Args:
            width: Window width
            height: Window height
            maximized: Whether window is maximized
        """
        self.state["window"] = {
            "width": width,
            "height": height,
            "maximized": maximized
        }
    
    def get_window_geometry(self):
        """Get saved window geometry.
        
        Returns:
            tuple: (width, height, maximized)
        """
        window = self.state.get("window", {})
        width = window.get("width", 1000)
        height = window.get("height", 700)
        maximized = window.get("maximized", False)
        return width, height, maximized
    
    def set_last_mode(self, mode):
        """Save last used mode.
        
        Args:
            mode: "simple" or "advanced"
        """
        self.state["last_mode"] = mode
    
    def get_last_mode(self):
        """Get last used mode.
        
        Returns:
            str: "simple" or "advanced"
        """
        return self.state.get("last_mode", "simple")
    
    def mark_operation_in_progress(self, folder, operation):
        """Mark that an operation is in progress for crash recovery.
        
        Args:
            folder: Working folder path
            operation: Operation name
        """
        self.state["crash_recovery"] = {
            "has_unsaved_changes": True,
            "last_folder": folder,
            "last_operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        self.save_state()
    
    def clear_operation_in_progress(self):
        """Clear the in-progress operation state."""
        self.state["crash_recovery"] = {
            "has_unsaved_changes": False,
            "last_folder": None,
            "last_operation": None,
            "timestamp": None
        }
        self.save_state()
    
    def has_crash_recovery(self):
        """Check if there's a crash recovery state.
        
        Returns:
            bool: True if crash recovery exists
        """
        crash = self.state.get("crash_recovery", {})
        return crash.get("has_unsaved_changes", False)
    
    def get_crash_recovery_info(self):
        """Get crash recovery information.
        
        Returns:
            dict: Crash recovery information
        """
        return self.state.get("crash_recovery", {})
    
    def backup_working_files(self, folder_path, backup_name=None):
        """Backup working files for recovery.
        
        Args:
            folder_path: Path to folder containing working files
            backup_name: Name for backup (or None for auto-generated)
            
        Returns:
            str: Backup directory path
        """
        try:
            if not os.path.isdir(folder_path):
                logger.warning(f"Cannot backup non-existent folder: {folder_path}")
                return None
            
            # Create backup name if not provided
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            # Create backup directory
            backup_dir = os.path.join(self.temp_dir, backup_name)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy JSON files (detection results)
            for file in ["image_recognition_file.json", "video_recognition_file.json"]:
                src_file = os.path.join(folder_path, file)
                if os.path.isfile(src_file):
                    shutil.copy2(src_file, os.path.join(backup_dir, file))
            
            logger.debug(f"Created backup at: {backup_dir}")
            return backup_dir
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
    
    def restore_from_backup(self, backup_dir, destination_dir):
        """Restore files from backup.
        
        Args:
            backup_dir: Backup directory
            destination_dir: Destination directory
            
        Returns:
            bool: Success
        """
        try:
            if not os.path.isdir(backup_dir) or not os.path.isdir(destination_dir):
                return False
                
            # Copy files from backup to destination
            for file in os.listdir(backup_dir):
                src_file = os.path.join(backup_dir, file)
                dst_file = os.path.join(destination_dir, file)
                if os.path.isfile(src_file):
                    shutil.copy2(src_file, dst_file)
            
            logger.debug(f"Restored from backup: {backup_dir} to {destination_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
            
