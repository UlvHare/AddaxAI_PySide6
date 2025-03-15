# app/frontend/utils/logger.py
"""
Centralized logging configuration for AddaxAI GUI
"""

import os
import sys
import logging
from pathlib import Path
import platform
from datetime import datetime

# Default log levels
DEFAULT_CONSOLE_LEVEL = logging.INFO
DEFAULT_FILE_LEVEL = logging.DEBUG

# Global logger instance
_logger = None

def setup_logging(log_dir=None, console_level=DEFAULT_CONSOLE_LEVEL, file_level=DEFAULT_FILE_LEVEL):
    """Configure logging for the application.
    
    Args:
        log_dir: Directory to store log files
        console_level: Logging level for console output
        file_level: Logging level for file output
    
    Returns:
        logging.Logger: The configured root logger
    """
    global _logger
    
    if _logger:
        return _logger
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Console handler
    console = logging.StreamHandler()
    console.setLevel(console_level)
    console.setFormatter(console_formatter)
    logger.addHandler(console)
    
    # File handler (if log_dir is provided)
    if log_dir:
        try:
            log_dir = Path(log_dir)
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped log file
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            log_file = log_dir / f"addaxai_{timestamp}.log"
            
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(file_level)
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
            
            logger.debug(f"Log file created at: {log_file}")
        except Exception as e:
            logger.error(f"Error setting up file logging: {e}")
    
    # System info
    logger.debug(f"AddaxAI GUI Started")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {platform.platform()}")
    logger.debug(f"System: {platform.system()}, Release: {platform.release()}")
    
    _logger = logger
    return logger


def get_logger(name=None):
    """Get a logger instance.
    
    Args:
        name: Logger name (module name)
        
    Returns:
        logging.Logger: Logger instance
    """
    global _logger
    
    # Setup root logger if not already done
    if not _logger:
        try:
            # Determine log directory
            if platform.system() == "Windows":
                log_dir = os.path.join(os.environ["APPDATA"], "AddaxAI", "logs")
            elif platform.system() == "Darwin":  # macOS
                log_dir = os.path.join(os.path.expanduser("~/Library/Logs"), "AddaxAI")
            else:  # Linux
                log_dir = os.path.join(os.path.expanduser("~/.config"), "AddaxAI", "logs")
                
            setup_logging(log_dir)
        except Exception as e:
            # Fall back to console-only logging
            setup_logging()
            _logger.error(f"Error determining log directory: {e}")
    
    # Return module-specific logger if name provided
    if name:
        return logging.getLogger(name)
    else:
        return _logger
        
