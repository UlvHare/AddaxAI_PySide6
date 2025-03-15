# The backend package containing all the core functionality of AddaxAI
"""
This package contains the backend modules for AddaxAI, including:
- deploy: Model deployment logic
- postprocess: Post-processing functions
- human_verification: Human-in-the-loop verification
- utils: Utility functions
- plot_utils: Plotting functions
- model_utils: Model-related utilities
"""

# Global variables and paths
import os
import sys
import platform
from pathlib import Path

# Set global variables
AddaxAI_files = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
CLS_DIR = os.path.join(AddaxAI_files, "models", "cls")
DET_DIR = os.path.join(AddaxAI_files, "models", "det")

# set environment variables
if os.name == 'nt':  # windows
    env_dir_fpath = os.path.join(AddaxAI_files, "envs")
elif platform.system() == 'Darwin':  # macos
    env_dir_fpath = os.path.join(AddaxAI_files, "envs")
else:  # linux
    env_dir_fpath = os.path.join(AddaxAI_files, "envs")

# Set versions
with open(os.path.join(AddaxAI_files, 'AddaxAI', 'version.txt'), 'r') as file:
    current_EA_version = file.read().strip()
corresponding_model_info_version = "5"

# Colors
green_primary = '#0B6065'
green_secondary = '#073d40'
yellow_primary = '#fdfae7'
yellow_secondary = '#F0EEDC'
yellow_tertiary = '#E4E1D0'

# Insert dependencies to system variables
cuda_toolkit_path = os.environ.get("CUDA_HOME") or os.environ.get("CUDA_PATH")
paths_to_add = [
    os.path.join(AddaxAI_files),
    os.path.join(AddaxAI_files, "cameratraps"),
    os.path.join(AddaxAI_files, "cameratraps", "megadetector"),
    os.path.join(AddaxAI_files, "AddaxAI")
]
if cuda_toolkit_path:
    paths_to_add.append(os.path.join(cuda_toolkit_path, "bin"))
for path in paths_to_add:
    sys.path.insert(0, path)
PYTHONPATH_separator = ":" if platform.system() != "Windows" else ";"
os.environ["PYTHONPATH"] = os.environ.get("PYTHONPATH", "") + PYTHONPATH_separator + PYTHONPATH_separator.join(paths_to_add)

# Import modules from forked repositories
from visualise_detection.bounding_box import bounding_box as bb
from cameratraps.megadetector.detection.video_utils import frame_results_to_video_results, FrameToVideoOptions, VIDEO_EXTENSIONS
from cameratraps.megadetector.utils.path_utils import IMG_EXTENSIONS

# Set DPI awareness on Windows
if platform.system() == "Windows":
    import ctypes
    try:
        # attempt
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except AttributeError:
        # fallback for older versions of Windows
        ctypes.windll.user32.SetProcessDPIAware()

# launch_count_file path
launch_count_file = os.path.join(AddaxAI_files, 'launch_count.json')

# Ensure PIL loads truncated images
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
