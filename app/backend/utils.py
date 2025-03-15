import os
import platform
import re
import sys
import json
import math
import time
import glob
import shutil
import pickle
import datetime
import traceback
import subprocess
import webbrowser
import numpy as np
import pandas as pd
import xml.etree.cElementTree as ET
from PIL import Image, ExifTags
from pathlib import Path
from GPSPhoto import gpsphoto
from collections import defaultdict

from . import AddaxAI_files, current_EA_version, IMG_EXTENSIONS, VIDEO_EXTENSIONS


def load_global_vars():
    """Load global variables from the global_vars.json file."""
    var_file = os.path.join(AddaxAI_files, "AddaxAI", "global_vars.json")
    with open(var_file, 'r') as file:
        variables = json.load(file)
    return variables


def write_global_vars(new_values=None):
    """Write values to the global_vars.json file."""
    # adjust
    variables = load_global_vars()
    if new_values is not None:
        for key, value in new_values.items():
            if key in variables:
                variables[key] = value
            else:
                print(f"Warning: Variable {key} not found in the loaded model variables.")

    # write
    var_file = os.path.join(AddaxAI_files, "AddaxAI", "global_vars.json")
    with open(var_file, 'w') as file:
        json.dump(variables, file, indent=4)


def load_model_vars(model_type="cls"):
    """Load model specific variables from the model's variables.json file."""
    global_vars = load_global_vars()
    model_idx_key = f"var_{model_type}_model_idx"

    # Check if we have a model selected (not 'None')
    if model_type == "cls" and global_vars.get(model_idx_key, 0) == 0:
        return {}

    # Get model directories
    cls_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "cls"))
    det_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "det"))

    # Get correct model based on index
    if model_type == "cls":
        models = ["None"] + cls_models
        idx = global_vars.get(model_idx_key, 0)
        if idx == 0:  # "None" selected
            return {}
        model_dir = models[idx]
    else:  # det
        models = det_models + ["Custom model"]
        idx = global_vars.get(model_idx_key, 0)
        model_dir = models[idx]

        # For custom model, we need to get the path
        if model_dir == "Custom model":
            var_file = os.path.join(AddaxAI_files, "models", model_type, model_dir, "variables.json")
            if not os.path.exists(var_file):
                return {}

    # Get variables from model directory
    var_file = os.path.join(AddaxAI_files, "models", model_type, model_dir, "variables.json")
    try:
        with open(var_file, 'r') as file:
            variables = json.load(file)
        return variables
    except:
        return {}


def write_model_vars(model_type="cls", new_values=None):
    """Write model specific variables to the model's variables.json file."""
    global_vars = load_global_vars()
    model_idx_key = f"var_{model_type}_model_idx"

    # Exit if no model is selected for cls
    if model_type == "cls" and global_vars.get(model_idx_key, 0) == 0:
        return

    # Get model directories
    cls_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "cls"))
    det_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "det"))

    # Get correct model based on index
    if model_type == "cls":
        models = ["None"] + cls_models
        idx = global_vars.get(model_idx_key, 0)
        if idx == 0:  # "None" selected
            return
        model_dir = models[idx]
    else:  # det
        models = det_models + ["Custom model"]
        idx = global_vars.get(model_idx_key, 0)
        model_dir = models[idx]

    # Exit if no model directory
    if not model_dir:
        return

    variables = load_model_vars(model_type)
    if new_values is not None:
        for key, value in new_values.items():
            if key in variables:
                variables[key] = value
            else:
                print(f"Warning: Variable {key} not found in the loaded model variables.")

    # Write
    var_file = os.path.join(AddaxAI_files, "models", model_type, model_dir, "variables.json")
    with open(var_file, 'w') as file:
        json.dump(variables, file, indent=4)


def fetch_known_models(root_dir):
    """Get list of model directories in the specified root directory."""
    return sorted([subdir for subdir in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, subdir))])


def fetch_label_map_from_json(path_to_json):
    """Extract label map from a JSON file."""
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    label_map = data['detection_categories']
    return label_map


def check_json_paths(path_to_json):
    """Check if JSON paths are relative or absolute."""
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    path = data['images'][0]['file']
    source_folder = os.path.dirname(path_to_json)
    if path.startswith(os.path.normpath(source_folder)):
        return "absolute"
    else:
        return "relative"


def make_json_relative(path_to_json, source_folder=None):
    """Convert paths in JSON to relative paths."""
    if check_json_paths(path_to_json) == "absolute":
        # If source_folder is not provided, use the directory of the JSON file
        if source_folder is None:
            source_folder = os.path.dirname(path_to_json)

        # Open and adjust paths
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)

        for image in data['images']:
            absolute_path = image['file']
            relative_path = os.path.relpath(absolute_path, source_folder)
            image['file'] = relative_path

        # Write back
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)


def make_json_absolute(path_to_json, source_folder=None):
    """Convert paths in JSON to absolute paths."""
    if check_json_paths(path_to_json) == "relative":
        # If source_folder is not provided, use the directory of the JSON file
        if source_folder is None:
            source_folder = os.path.dirname(path_to_json)

        # Open and adjust paths
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)

        for image in data['images']:
            relative_path = image['file']
            absolute_path = os.path.normpath(os.path.join(source_folder, relative_path))
            image['file'] = absolute_path

        # Write back
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)


def append_to_json(path_to_json, object_to_be_appended):
    """Add information to JSON file."""
    # Open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)

    # Adjust
    data['info'].update(object_to_be_appended)

    # Write
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)


def change_hitl_var_in_json(path_to_json, status):
    """Change human-in-the-loop progress variable in JSON."""
    # Open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)

    # Adjust
    data['info']["addaxai_metadata"]["hitl_status"] = status

    # Write
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)


def get_hitl_var_in_json(path_to_json):
    """Get human-in-the-loop progress variable from JSON."""
    # Open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
        addaxai_metadata = data['info'].get("addaxai_metadata") or data['info'].get("ecoassist_metadata")  # include old name 'EcoAssist' for backwards compatibility

    # Get status
    if "hitl_status" in addaxai_metadata:
        status = addaxai_metadata["hitl_status"]
    else:
        status = "never-started"

    # Return
    return status


def extract_label_map_from_model(model_file):
    """Extract label map from a custom model."""
    print(f"EXECUTED: extract_label_map_from_model({model_file})")

    # Import module from cameratraps dir
    from cameratraps.megadetector.detection.pytorch_detector import PTDetector

    # Load model
    label_map_detector = PTDetector(model_file, force_cpu=True)

    # Fetch classes
    try:
        CUSTOM_DETECTOR_LABEL_MAP = {}
        for id in label_map_detector.model.names:
            CUSTOM_DETECTOR_LABEL_MAP[id] = label_map_detector.model.names[id]
    except Exception as error:
        # Log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")

    # Delete and free up memory
    del label_map_detector

    # Log
    print(f"Label map: {CUSTOM_DETECTOR_LABEL_MAP})\n")

    # Return label map
    return CUSTOM_DETECTOR_LABEL_MAP


def get_python_interprator(env_name):
    """Get the path to the Python interpreter based on environment and platform."""
    if platform.system() == 'Windows':
        return os.path.join(AddaxAI_files, "envs", f"env-{env_name}", "python.exe")
    else:
        return os.path.join(AddaxAI_files, "envs", f"env-{env_name}", "bin", "python")


def switch_yolov5_version(model_type):
    """Switch the YOLOv5 version by modifying the Python import path."""
    print(f"EXECUTED: switch_yolov5_version({model_type})\n")

    # Set the path to the desired version
    base_path = os.path.join(AddaxAI_files, "yolov5_versions")
    if model_type == "old models":
        version_path = os.path.join(base_path, "yolov5_old", "yolov5")
    elif model_type == "new models":
        version_path = os.path.join(base_path, "yolov5_new", "yolov5")
    else:
        raise ValueError("Invalid model_type")

    # Add yolov5 checkout to PATH if not already there
    if version_path not in sys.path:
        sys.path.insert(0, version_path)

    # Add yolov5 checkout to PYTHONPATH if not already there
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    PYTHONPATH_separator = ":" if platform.system() != "Windows" else ";"
    PYTHONPATH_to_add = version_path + PYTHONPATH_separator
    if not current_pythonpath.startswith(PYTHONPATH_to_add):
        os.environ["PYTHONPATH"] = PYTHONPATH_to_add + current_pythonpath


def is_valid_float(value):
    """Check if a string can be converted to float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def contains_special_characters(path):
    """Check if a path contains special characters."""
    allowed_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./ +\:'()")
    for char in path:
        if char not in allowed_characters:
            return [True, char]
    return [False, ""]


def open_file_or_folder(path, show_error=True):
    """Open a file or folder using the platform's default application."""
    if platform.system() == 'Darwin':  # mac
        try:
            subprocess.call(('open', path))
        except:
            if show_error:
                print(f"Error opening: {path}")
                return False
    elif platform.system() == 'Windows':  # windows
        try:
            os.startfile(path)
        except:
            if show_error:
                print(f"Error opening: {path}")
                return False
    else:  # linux
        try:
            subprocess.call(('xdg-open', path))
        except:
            try:
                subprocess.call(('gnome-open', path))
            except:
                if show_error:
                    print(f"Error opening: {path}. Neither 'xdg-open' nor 'gnome-open' command worked.")
                    return False
    return True


def get_size(path):
    """Get the size of a file in appropriate units (bytes, KB, MB, GB)."""
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024, 2):
        return f"{round(size/1024, 2)} KB"
    elif size < pow(1024, 3):
        return f"{round(size/(pow(1024, 2)), 2)} MB"
    elif size < pow(1024, 4):
        return f"{round(size/(pow(1024, 3)), 2)} GB"


def format_size(size):
    """Format a size in bytes to an appropriate unit."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{round(size)} {unit}"
        size /= 1024.0


def check_checkpnt(folder_path):
    """Check if checkpoint file is present and return its path."""
    checkpoint_files = []
    for filename in os.listdir(folder_path):
        if re.search('^md_checkpoint_\d+\.json$', filename):
            checkpoint_files.append(filename)

    if not checkpoint_files:
        return False, None

    if len(checkpoint_files) == 1:
        return True, os.path.join(folder_path, checkpoint_files[0])
    else:
        # Sort by timestamp (latest first)
        sorted_files = sort_checkpoint_files(checkpoint_files)
        return True, os.path.join(folder_path, sorted_files[0])


def sort_checkpoint_files(files):
    """Sort checkpoint files by timestamp (newest first)."""
    def get_timestamp(file):
        timestamp_str = file.split('_')[1].split('.')[0]
        return datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")
    sorted_files = sorted(files, key=get_timestamp, reverse=True)
    return sorted_files


def load_launch_count():
    """Load the number of times the application has been launched."""
    if not os.path.exists(launch_count_file):
        with open(launch_count_file, 'w') as f:
            json.dump({'count': 0}, f)
    with open(launch_count_file, 'r') as f:
        data = json.load(f)
        count = data.get('count', 0)
        print(f"Launch count: {count}")
        return count


def save_launch_count(count):
    """Save the updated launch count."""
    with open(launch_count_file, 'w') as f:
        json.dump({'count': count}, f)


def needs_EA_update(required_version):
    """Check if the current version is lower than the required version."""
    current_parts = list(map(int, current_EA_version.split('.')))
    required_parts = list(map(int, required_version.split('.')))

    # Pad the shorter version with zeros
    while len(current_parts) < len(required_parts):
        current_parts.append(0)
    while len(required_parts) < len(current_parts):
        required_parts.append(0)

    # Compare each part of the version
    for current, required in zip(current_parts, required_parts):
        if current < required:
            return True  # current_version is lower than required_version
        elif current > required:
            return False  # current_version is higher than required_version

    # All parts are equal, consider versions equal
    return False


def model_needs_downloading(model_type):
    """Check if a model needs to be downloaded, and where to download it to."""
    global_vars = load_global_vars()
    model_idx_key = f"var_{model_type}_model_idx"
    idx = global_vars.get(model_idx_key, 0)

    # Get model directories
    cls_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "cls"))
    det_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "det"))

    # Get correct model based on index
    if model_type == "cls":
        models = ["None"] + cls_models
        if idx == 0:  # "None" selected
            return [False, ""]
        model_name = models[idx]
    else:  # det
        models = det_models + ["Custom model"]
        if idx >= len(models) - 1:  # Custom model selected
            return [False, ""]
        model_name = models[idx]

    # Check if model files exist
    model_vars = load_model_vars(model_type)
    if not model_vars:
        return [False, ""]

    model_fname = model_vars.get("model_fname", "")
    model_dir = os.path.join(AddaxAI_files, "models", model_type, model_name)
    model_fpath = os.path.join(model_dir, model_fname)

    if os.path.isfile(model_fpath):
        # The model file is already present
        return [False, ""]
    else:
        # The model is not present yet
        min_version = model_vars.get("min_version", "1000.1")

        # Check if the model works with the current EA version
        if needs_EA_update(min_version):
            return [None, ""]
        else:
            return [True, model_dir]
