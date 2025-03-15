## backend/deploy.py
"""
Contains the core logic for deploying models on images and videos.
This is one of the most important parts of the backend as it handles
the actual model deployment process.

"""
import datetime
import glob
import os
import re
import sys
import cv2
import json
import time
import traceback
import subprocess
import tempfile
import platform
import signal
from pathlib import Path
import xml.etree.cElementTree as ET
from PIL import Image, ImageFile

from . import AddaxAI_files, current_EA_version, IMG_EXTENSIONS, VIDEO_EXTENSIONS
from .utils import (
    load_global_vars, load_model_vars, switch_yolov5_version,
    extract_label_map_from_model, is_valid_float, contains_special_characters,
    get_python_interprator, open_file_or_folder, fetch_known_models
)


class ModelDeployment:
    """Class for handling model deployment on images and videos."""

    def __init__(self, path_to_folder, progress_callback=None, simple_mode=False, timelapse_mode=False):
        """Initialize the model deployment with the given parameters.

        Args:
            path_to_folder: Path to the folder containing images/videos to process
            progress_callback: Function to call with progress updates
            simple_mode: Whether to use simple mode defaults
            timelapse_mode: Whether to use timelapse mode
        """
        self.path_to_folder = str(Path(path_to_folder))
        self.progress_callback = progress_callback
        self.simple_mode = simple_mode
        self.timelapse_mode = timelapse_mode
        self.global_vars = load_global_vars()
        self.cancel_requested = False
        self.subprocess_output = ""
        self.error_log_path = os.path.join(self.path_to_folder, "model_error_log.txt")
        self.warning_log_path = os.path.join(self.path_to_folder, "model_warning_log.txt")
        self.special_char_log_path = os.path.join(self.path_to_folder, "model_special_char_log.txt")
        self.temp_frame_folder = None
        self.temp_frame_folder_obj = None

    def check_folder_contents(self):
        """Check if the folder contains images or videos to process."""
        img_present = False
        vid_present = False

        # Determine which types to check
        if self.simple_mode:
            check_img_presence = True
            check_vid_presence = True
        else:
            check_img_presence = self.global_vars.get('var_process_img', True)
            check_vid_presence = self.global_vars.get('var_process_vid', True)

        # Check if exclude subdirectories is set
        exclude_subs = self.global_vars.get('var_exclude_subs', False)

        if exclude_subs:
            # Non-recursive check
            for f in os.listdir(self.path_to_folder):
                if check_img_presence and any(f.lower().endswith(ext) for ext in IMG_EXTENSIONS):
                    img_present = True
                if check_vid_presence and any(f.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                    vid_present = True
                if (img_present and vid_present) or \
                    (img_present and not check_vid_presence) or \
                    (vid_present and not check_img_presence) or \
                    (not check_img_presence and not check_vid_presence):
                    break
        else:
            # Recursive check
            for main_dir, _, files in os.walk(self.path_to_folder):
                for file in files:
                    if check_img_presence and any(file.lower().endswith(ext) for ext in IMG_EXTENSIONS):
                        img_present = True
                    if check_vid_presence and any(file.lower().endswith(ext) for ext in VIDEO_EXTENSIONS):
                        vid_present = True
                if (img_present and vid_present) or \
                    (img_present and not check_vid_presence) or \
                    (vid_present and not check_img_presence) or \
                    (not check_img_presence and not check_vid_presence):
                    break

        return img_present, vid_present

    def check_special_characters(self):
        """Check for special characters in file paths that might cause issues."""
        isolated_special_fpaths = {"total_saved_images": 0}

        for main_dir, _, files in os.walk(self.path_to_folder):
            for file in files:
                file_path = os.path.join(main_dir, file)
                if os.path.splitext(file_path)[1].lower() in ['.jpg', '.jpeg', '.png', '.mp4', '.avi', '.mpeg', '.mpg']:
                    has_special, char = contains_special_characters(file_path)
                    if has_special:
                        drive, rest_of_path = os.path.splitdrive(file_path)
                        path_components = rest_of_path.split(os.path.sep)
                        isolated_special_fpath = drive
                        for path_component in path_components:  # check the largest dir that is faulty
                            isolated_special_fpath = os.path.join(isolated_special_fpath, path_component)
                            if contains_special_characters(path_component)[0]:
                                isolated_special_fpaths["total_saved_images"] += 1
                                if isolated_special_fpath in isolated_special_fpaths:
                                    isolated_special_fpaths[isolated_special_fpath][0] += 1
                                else:
                                    isolated_special_fpaths[isolated_special_fpath] = [1, char]

        n_special_chars = len(isolated_special_fpaths) - 1
        total_saved_images = isolated_special_fpaths['total_saved_images']
        del isolated_special_fpaths['total_saved_images']

        if total_saved_images > 0:
            # Write to log file
            if os.path.isfile(self.special_char_log_path):
                os.remove(self.special_char_log_path)

            for k, v in isolated_special_fpaths.items():
                line = f"There are {str(v[0]).ljust(4)} files hidden behind the {str(v[1])} character in folder '{k}'"
                if not line.isprintable():
                    line = repr(line)
                    print(f"\nSPECIAL CHARACTER LOG: This special character is going to give an error : {line}\n")

                with open(self.special_char_log_path, 'a+', encoding='utf-8') as f:
                    f.write(f"{line}\n")

            # Log to console
            print(f"\nSPECIAL CHARACTER LOG: There are {total_saved_images} files hidden behind {n_special_chars} special characters.\n")

        return total_saved_images, n_special_chars, isolated_special_fpaths

    def prepare_deployment(self):
        """Prepare for deployment by setting up temp directories and command options."""
        # Create temp frame folder for video processing if needed
        if self.check_videos_need_classification():
            self.temp_frame_folder_obj = tempfile.TemporaryDirectory()
            self.temp_frame_folder = self.temp_frame_folder_obj.name

        # Prepare command options
        img_options = self.prepare_image_options()
        vid_options = self.prepare_video_options()

        return img_options, vid_options

    def check_videos_need_classification(self):
        """Check if videos need to be classified (need temp frame folder)."""
        # Check if video processing is enabled and cls model is selected
        process_vid = self.global_vars.get('var_process_vid', True) if not self.simple_mode else True
        cls_model_idx = self.global_vars.get('var_cls_model_idx', 0)

        # If in simple mode, check if a classification model is selected (not None)
        if self.simple_mode:
            return cls_model_idx > 0

        # For advanced mode, check both conditions
        return process_vid and cls_model_idx > 0

    def prepare_image_options(self):
        """Prepare command options for image processing."""
        options = ["--output_relative_filenames"]

        # Simple mode specific options
        if self.simple_mode:
            options.append("--recursive")
        # Advanced mode specific options
        else:
            # Recursive option
            if not self.global_vars.get('var_exclude_subs', False):
                options.append("--recursive")

            # Checkpoint options
            if self.global_vars.get('var_use_checkpnts', False):
                options.append(f"--checkpoint_frequency={self.global_vars.get('var_checkpoint_freq', '500')}")

            # Resume from checkpoint
            if self.global_vars.get('var_cont_checkpnt', False):
                has_checkpoint, checkpoint_file = self.check_for_checkpoint()
                if has_checkpoint:
                    options.append(f"--resume_from_checkpoint={checkpoint_file}")

            # Custom image size
            if self.global_vars.get('var_use_custom_img_size_for_deploy', False):
                img_size = self.global_vars.get('var_image_size_for_deploy', '')
                if img_size and img_size.isdigit():
                    options.append(f"--image_size={img_size}")

        return options

    def prepare_video_options(self):
        """Prepare command options for video processing."""
        options = ["--json_confidence_threshold=0.01"]

        # Timelapse mode option
        if self.timelapse_mode:
            options.append("--include_all_processed_frames")

        # Add temp frame folder if needed
        if self.temp_frame_folder:
            options.append(f"--frame_folder={self.temp_frame_folder}")
            options.append("--keep_extracted_frames")

        # Simple mode specific options
        if self.simple_mode:
            options.append("--recursive")
            options.append("--time_sample=1")
        # Advanced mode specific options
        else:
            # Recursive option
            if not self.global_vars.get('var_exclude_subs', False):
                options.append("--recursive")

            # Frame sampling
            if self.global_vars.get('var_not_all_frames', True):
                time_sample = self.global_vars.get('var_nth_frame', '1')
                if is_valid_float(time_sample):
                    options.append(f"--time_sample={time_sample}")

        return options

    def check_for_checkpoint(self):
        """Check if checkpoint files exist and return the path to the most recent one."""
        checkpoint_files = []
        for filename in os.listdir(self.path_to_folder):
            if re.search('^md_checkpoint_\d+\.json$', filename):
                checkpoint_files.append(filename)

        if not checkpoint_files:
            return False, None

        if len(checkpoint_files) == 1:
            return True, os.path.join(self.path_to_folder, checkpoint_files[0])

        # Sort by timestamp (latest first)
        def get_timestamp(file):
            timestamp_str = file.split('_')[1].split('.')[0]
            return datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

        sorted_files = sorted(checkpoint_files, key=get_timestamp, reverse=True)
        return True, os.path.join(self.path_to_folder, sorted_files[0])

    def get_model_path(self):
        """Get the path to the detection model file."""
        # Get model index
        det_model_idx = self.global_vars.get('var_det_model_idx', 0)

        # For simple mode, always use MegaDetector 5a
        if self.simple_mode:
            det_model_fpath = os.path.join(AddaxAI_files, "models", "det", "MegaDetector 5a", "md_v5a.0.0.pt")
            switch_yolov5_version("old models")
            return det_model_fpath, False

        # Get available detection models
        det_models = [d for d in os.listdir(os.path.join(AddaxAI_files, "models", "det"))
                      if os.path.isdir(os.path.join(AddaxAI_files, "models", "det", d))]

        # Not a custom model
        if det_model_idx < len(det_models):
            det_model_vars = load_model_vars("det")
            det_model_fname = det_model_vars.get("model_fname", "")
            det_model_fpath = os.path.join(AddaxAI_files, "models", "det", det_models[det_model_idx], det_model_fname)
            switch_yolov5_version("old models")
            return det_model_fpath, False

        # Custom model
        det_model_path = self.global_vars.get('var_det_model_path', "")
        switch_yolov5_version("new models")

        # Extract and save label map
        label_map = extract_label_map_from_model(det_model_path)
        native_model_classes_json_file = os.path.join(self.path_to_folder, "native_model_classes.json")
        with open(native_model_classes_json_file, "w") as outfile:
            json.dump(label_map, outfile, indent=1)

        return det_model_path, True

    def deploy_model(self, data_type):
        """Deploy the model on the specified data type (img/vid).

        Args:
            data_type: Type of data to process ('img' or 'vid')

        Returns:
            success: Boolean indicating if deployment was successful
        """
        # Update progress to show loading
        if self.progress_callback:
            self.progress_callback(process=f"{data_type}_det", status="load")

        # Prepare variables
        model_fpath, is_custom_model = self.get_model_path()
        run_detector_batch_py = os.path.join(AddaxAI_files, "cameratraps", "megadetector", "detection", "run_detector_batch.py")
        process_video_py = os.path.join(AddaxAI_files, "cameratraps", "megadetector", "detection", "process_video.py")
        image_recognition_file = os.path.join(self.path_to_folder, "image_recognition_file.json")
        video_recognition_file = "--output_json_file=" + os.path.join(self.path_to_folder, "video_recognition_file.json")
        GPU_param = "Unknown"
        python_executable = get_python_interprator("base")

        # Get command options
        img_options, vid_options = self.prepare_deployment()

        # Add custom model class mapping if needed
        if is_custom_model:
            native_model_classes_json_file = os.path.join(self.path_to_folder, "native_model_classes.json")
            if data_type == "img":
                img_options.append(f"--class_mapping_filename={native_model_classes_json_file}")
            else:
                vid_options.append(f"--class_mapping_filename={native_model_classes_json_file}")

        # Create commands for different platforms
        if os.name == 'nt':  # Windows
            if data_type == "img":
                command = [python_executable, run_detector_batch_py, model_fpath,
                          *img_options, '--threshold=0.01', self.path_to_folder, image_recognition_file]
            else:
                command = [python_executable, process_video_py, *vid_options,
                          '--max_width=1280', '--verbose', '--quality=85',
                          video_recognition_file, model_fpath, self.path_to_folder]
        else:  # macOS and Linux
            if data_type == "img":
                options_str = "' '".join(img_options) if img_options else ""
                command = [f"'{python_executable}' '{run_detector_batch_py}' '{model_fpath}' "
                           f"'{options_str}' '--threshold=0.01' '{self.path_to_folder}' '{image_recognition_file}'"]
            else:
                options_str = "' '".join(vid_options) if vid_options else ""
                command = [f"'{python_executable}' '{process_video_py}' '{options_str}' "
                           f"'--max_width=1280' '--verbose' '--quality=85' '{video_recognition_file}' "
                           f"'{model_fpath}' '{self.path_to_folder}'"]

        # Handle GPU disabled option
        disable_gpu = self.global_vars.get('var_disable_GPU', False) and not self.simple_mode
        if disable_gpu:
            if os.name == 'nt':  # Windows
                command[:0] = ['set', 'CUDA_VISIBLE_DEVICES=""', '&']
            elif platform.system() != 'Darwin':  # Linux (not macOS)
                command = "CUDA_VISIBLE_DEVICES='' " + command[0]

        # Log command
        print(f"command:\n\n{command}\n\n")

        # Run the command
        try:
            # Create process
            if os.name == 'nt':  # Windows
                p = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,
                    shell=True,
                    universal_newlines=True
                )
            else:  # macOS and Linux
                p = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    bufsize=1,
                    shell=True,
                    universal_newlines=True,
                    preexec_fn=os.setsid
                )

            # Reset variables
            self.cancel_requested = False
            self.subprocess_output = ""
            previous_processed_img = "There is no previously processed image. The problematic character is in the first image to analyse."
            extracting_frames_mode = False

            # Determine frame/video choice for progress reporting
            if data_type == "vid" and self.global_vars.get('var_cls_model_idx', 0) == 0:
                frame_video_choice = "video"
            elif data_type == "vid" and self.global_vars.get('var_cls_model_idx', 0) > 0:
                frame_video_choice = "frame"
            else:
                frame_video_choice = None

            # Process output in real-time
            for line in p.stdout:
                # Save output in case of error
                self.subprocess_output += line
                self.subprocess_output = self.subprocess_output[-1000:]

                # Log output
                print(line, end='')

                # Check for special conditions
                if self.process_output_line(line, previous_processed_img, data_type):
                    return False

                # Track processed images for error reporting
                if line.startswith("Processing image "):
                    previous_processed_img = line.replace("Processing image ", "")

                # Handle errors and warnings
                if "Exception:" in line:
                    with open(self.error_log_path, 'a+') as f:
                        f.write(f"{line}\n")

                if "Warning:" in line:
                    if not any(skip in line for skip in [
                        "could not determine MegaDetector version",
                        "no metadata for unknown detector version",
                        "using user-supplied image size",
                        "already exists and will be overwritten"
                    ]):
                        with open(self.warning_log_path, 'a+') as f:
                            f.write(f"{line}\n")

                # Handle frame extraction mode
                if "Extracting frames for folder " in line and data_type == "vid":
                    if self.progress_callback:
                        self.progress_callback(
                            process=f"{data_type}_det",
                            status="extracting frames"
                        )
                    extracting_frames_mode = True

                if extracting_frames_mode:
                    if '%' in line[0:4]:
                        if self.progress_callback:
                            self.progress_callback(
                                process=f"{data_type}_det",
                                status="extracting frames",
                                extracting_frames_txt=f"Extracting frames... {line[:3]}%"
                            )

                if "Extracted frames for" in line and data_type == "vid":
                    extracting_frames_mode = False

                if extracting_frames_mode:
                    continue

                # Update progress
                self.update_progress_from_line(line, data_type, frame_video_choice, p)

                # Check for cancellation
                if self.cancel_requested:
                    if os.name == 'nt':  # Windows
                        subprocess.Popen(f"TASKKILL /F /PID {p.pid} /T")
                    else:
                        os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                    return False

            # Process completed successfully
            if self.progress_callback:
                self.progress_callback(process=f"{data_type}_det", status="done")

            # Create addaxai metadata
            self.add_metadata_to_json(data_type, is_custom_model)

            return True

        except Exception as e:
            print(f"Error in deploy_model: {str(e)}")
            traceback.print_exc()
            return False

    def process_output_line(self, line, previous_processed_img, data_type):
        """Process a line of output from the subprocess, checking for errors.

        Returns:
            bool: True if an error was detected and processing should stop, False otherwise
        """
        # Check for known error patterns
        if line.startswith("No image files found"):
            print(f"No image files found in '{self.path_to_folder}'")
            return True

        if line.startswith("No videos found"):
            print(f"No videos found in '{self.path_to_folder}'")
            return True

        if line.startswith("No frames extracted"):
            print("Could not extract frames")
            return True

        if line.startswith("UnicodeEncodeError:"):
            print(f"Unicode encoding error, possibly due to special characters in filenames")
            print(f"Last successfully processed file: {previous_processed_img}")
            return True

        return False

    def update_progress_from_line(self, line, data_type, frame_video_choice, process):
        """Update progress information based on a line of output."""
        if not self.progress_callback:
            return

        # GPU detection
        if line.startswith("GPU available: False"):
            GPU_param = "CPU"
        elif line.startswith("GPU available: True"):
            GPU_param = "GPU"
        # Progress update
        elif '%' in line[0:4]:
            try:
                # Parse the progress line
                times = re.search(r"(\[.*?\])", line)[1]
                progress_bar = re.search(r"^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
                percentage = re.search(r"\d*%", progress_bar)[0][:-1]
                current_im = re.search(r"\d*\/", progress_bar)[0][:-1]
                total_im = re.search(r"\/\d*", progress_bar)[0][1:]
                elapsed_time = re.search(r"(?<=\[)(.*)(?=<)", times)[1]
                time_left = re.search(r"(?<=<)(.*)(?=,)", times)[1]
                processing_speed = re.search(r"(?<=,)(.*)(?=])", times)[1].strip()

                # Update progress
                self.progress_callback(
                    process=f"{data_type}_det",
                    status="running",
                    cur_it=int(current_im),
                    tot_it=int(total_im),
                    time_ela=elapsed_time,
                    time_rem=time_left,
                    speed=processing_speed,
                    hware=GPU_param if 'GPU_param' in locals() else "Unknown",
                    cancel_func=lambda: self.cancel_process(process),
                    frame_video_choice=frame_video_choice
                )
            except Exception as e:
                print(f"Error parsing progress: {str(e)}")

    def cancel_process(self, process):
        """Cancel the current process."""
        self.cancel_requested = True

    def add_metadata_to_json(self, data_type, is_custom_model=False, custom_label_map=None):
        """Add AddaxAI metadata to the output JSON file."""
        # Prepare metadata
        addaxai_metadata = {
            "addaxai_metadata": {
                "version": current_EA_version,
                "custom_model": is_custom_model,
                "custom_model_info": {}
            }
        }

        # Add custom model info if applicable
        if is_custom_model:
            if custom_label_map is None:
                native_model_classes_json_file = os.path.join(self.path_to_folder, "native_model_classes.json")
                with open(native_model_classes_json_file, 'r') as f:
                    custom_label_map = json.load(f)

            addaxai_metadata["addaxai_metadata"]["custom_model_info"] = {
                "model_name": os.path.basename(os.path.normpath(self.global_vars.get('var_det_model_path', ""))),
                "label_map": custom_label_map
            }

        # Paths to JSON files
        image_recognition_file = os.path.join(self.path_to_folder, "image_recognition_file.json")
        video_recognition_file = os.path.join(self.path_to_folder, "video_recognition_file.json")

        # Update JSON files
        if data_type == "img" and os.path.isfile(image_recognition_file):
            self.append_to_json(image_recognition_file, addaxai_metadata)
            if self.global_vars.get('var_abs_paths', False):
                self.make_json_absolute(image_recognition_file)

        if data_type == "vid" and os.path.isfile(video_recognition_file):
            self.append_to_json(video_recognition_file, addaxai_metadata)
            if self.global_vars.get('var_abs_paths', False):
                self.make_json_absolute(video_recognition_file)

    def append_to_json(self, path_to_json, object_to_be_appended):
        """Add information to JSON file."""
        # Open
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)

        # Adjust
        data['info'].update(object_to_be_appended)

        # Write
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)

    def make_json_absolute(self, path_to_json):
        """Convert paths in JSON to absolute paths."""
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)

        for image in data['images']:
            relative_path = image['file']
            # Check if the path is already absolute
            if not os.path.isabs(relative_path):
                absolute_path = os.path.normpath(os.path.join(self.path_to_folder, relative_path))
                image['file'] = absolute_path

        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)

    def cleanup(self):
        """Clean up temporary resources."""
        if self.temp_frame_folder_obj:
            self.temp_frame_folder_obj.cleanup()
            self.temp_frame_folder = None
            self.temp_frame_folder_obj = None


def classify_detections(json_fpath, data_type, progress_callback=None, simple_mode=False):
    """Classify detections in JSON file using specified model.

    Args:
        json_fpath: Path to JSON file with detections
        data_type: Type of data ('img' or 'vid')
        progress_callback: Function to call with progress updates
        simple_mode: Whether to use simple mode defaults

    Returns:
        success: Boolean indicating if classification was successful
    """
    # Show user it's loading
    if progress_callback:
        progress_callback(process=f"{data_type}_cls", status="load")

    try:
        # Load global and model variables
        global_vars = load_global_vars()
        model_vars = load_model_vars("cls")

        if not model_vars:
            print("No classification model selected or model variables not found")
            return False

        cls_model_fname = model_vars.get("model_fname", "")
        cls_model_type = model_vars.get("type", "")
        cls_model_dir = None

        # Get cls model directory
        cls_model_idx = global_vars.get('var_cls_model_idx', 0)
        cls_models = fetch_known_models(os.path.join(AddaxAI_files, "models", "cls"))

        if cls_model_idx == 0 or cls_model_idx > len(cls_models):
            print("No valid classification model selected")
            return False

        cls_model_dir = cls_models[cls_model_idx - 1]  # -1 because "None" is index 0
        cls_model_fpath = os.path.join(AddaxAI_files, "models", "cls", cls_model_dir, cls_model_fname)

        # Get OS-specific environment
        if os.name == 'nt':  # Windows
            cls_model_env = model_vars.get("env-windows", model_vars.get("env", "base"))
        elif platform.system() == 'Darwin':  # macOS
            cls_model_env = model_vars.get("env-macos", model_vars.get("env", "base"))
        else:  # Linux
            cls_model_env = model_vars.get("env-linux", model_vars.get("env", "base"))

        # Get parameter values
        if simple_mode:
            cls_disable_GPU = False
            cls_detec_thresh = model_vars.get("var_cls_detec_thresh_default", 0.2)
            cls_class_thresh = model_vars.get("var_cls_class_thresh_default", 0.5)
            cls_animal_smooth = False
        else:
            cls_disable_GPU = global_vars.get('var_disable_GPU', False)
            cls_detec_thresh = global_vars.get('var_cls_detec_thresh', 0.2)
            cls_class_thresh = global_vars.get('var_cls_class_thresh', 0.5)
            cls_animal_smooth = global_vars.get('var_smooth_cls_animal', False)

        # Initialize paths
        python_executable = get_python_interprator(cls_model_env)
        inference_script = os.path.join(AddaxAI_files, "AddaxAI", "classification_utils", "model_types", cls_model_type, "classify_detections.py")

        # Get the temp frame folder path if it exists
        temp_frame_folder = os.path.dirname(json_fpath)
        temp_frame_folder_glob = os.path.join(temp_frame_folder, "tmp_frames_*")
        temp_frame_dirs = glob.glob(temp_frame_folder_glob)
        temp_frame_dir = temp_frame_dirs[0] if temp_frame_dirs else "None"

        # Create command
        command_args = []
        command_args.append(python_executable)
        command_args.append(inference_script)
        command_args.append(AddaxAI_files)
        command_args.append(cls_model_fpath)
        command_args.append(str(cls_detec_thresh))
        command_args.append(str(cls_class_thresh))
        command_args.append(str(cls_animal_smooth))
        command_args.append(json_fpath)
        command_args.append(temp_frame_dir)

        # Adjust command for Unix OS
        if os.name != 'nt':
            command_args = "'" + "' '".join(command_args) + "'"

        # Prepend with OS-specific commands for GPU control
        if os.name == 'nt':  # Windows
            if cls_disable_GPU:
                command_args = ['set', 'CUDA_VISIBLE_DEVICES=""', '&'] + command_args
        elif platform.system() == 'Darwin':  # macOS
            command_args = "export PYTORCH_ENABLE_MPS_FALLBACK=1 && " + command_args
        else:  # Linux
            if cls_disable_GPU:
                command_args = "CUDA_VISIBLE_DEVICES='' " + command_args
            else:
                command_args = "export PYTORCH_ENABLE_MPS_FALLBACK=1 && " + command_args

        # Log command
        print(f"Classification command: {command_args}")

        # Run the command
        if os.name == 'nt':  # Windows
            p = subprocess.Popen(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True
            )
        else:  # macOS and Linux
            p = subprocess.Popen(
                command_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True,
                preexec_fn=os.setsid
            )

        # Track output and status
        subprocess_output = ""
        status_setting = 'running'
        cancel_requested = False

        # Process output
        for line in p.stdout:
            # Save output
            subprocess_output += line
            subprocess_output = subprocess_output[-1000:]

            # Log
            print(line, end='')

            # Check for early exit if no detections meet criteria
            if line.startswith("n_crops_to_classify is zero. Nothing to classify."):
                print("No animal detections meet the criteria for classification")
                if progress_callback:
                    progress_callback(
                        process=f"{data_type}_cls",
                        status="done",
                        time_ela="00:00",
                        speed="0it/s"
                    )
                return True

            # Catch smoothening info lines
            if "<EA>" in line:
                smooth_output_line = re.search('<EA>(.+)<EA>', line).group().replace('<EA>', '')
                smooth_output_file = os.path.join(os.path.dirname(json_fpath), "smooth-output.txt")
                with open(smooth_output_file, 'a+') as f:
                    f.write(f"{smooth_output_line}\n")

            # Update status
            if "<EA-status-change>" in line:
                status_setting = re.search('<EA-status-change>(.+)<EA-status-change>', line).group().replace('<EA-status-change>', '')
                if progress_callback:
                    progress_callback(process=f"{data_type}_cls", status=status_setting)

            # Update progress
            if line.startswith("GPU available: False"):
                GPU_param = "CPU"
            elif line.startswith("GPU available: True"):
                GPU_param = "GPU"
            elif '%' in line[0:4]:
                try:
                    # Parse progress
                    times = re.search(r"(\[.*?\])", line)[1]
                    progress_bar = re.search(r"^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
                    percentage = re.search(r"\d*%", progress_bar)[0][:-1]
                    current_im = re.search(r"\d*\/", progress_bar)[0][:-1]
                    total_im = re.search(r"\/\d*", progress_bar)[0][1:]
                    elapsed_time = re.search(r"(?<=\[)(.*)(?=<)", times)[1]
                    time_left = re.search(r"(?<=<)(.*)(?=,)", times)[1]
                    processing_speed = re.search(r"(?<=,)(.*)(?=])", times)[1].strip()

                    # Report progress
                    if progress_callback:
                        progress_callback(
                            process=f"{data_type}_cls",
                            status=status_setting,
                            cur_it=int(current_im),
                            tot_it=int(total_im),
                            time_ela=elapsed_time,
                            time_rem=time_left,
                            speed=processing_speed,
                            hware=GPU_param if 'GPU_param' in locals() else "Unknown",
                            cancel_func=lambda: cancel_subprocess(p)
                        )
                except Exception as e:
                    print(f"Error parsing progress: {str(e)}")

            # Check for cancellation
            if cancel_requested:
                if os.name == 'nt':  # Windows
                    subprocess.Popen(f"TASKKILL /F /PID {p.pid} /T")
                else:
                    os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                return False

        # Process completed
        if progress_callback:
            progress_callback(
                process=f"{data_type}_cls",
                status="done",
                time_ela=elapsed_time if 'elapsed_time' in locals() else "00:00",
                speed=processing_speed if 'processing_speed' in locals() else "0it/s"
            )

        return True

    except Exception as e:
        print(f"Error in classify_detections: {str(e)}")
        traceback.print_exc()
        return False


def cancel_subprocess(process):
    """Kill a subprocess."""
    if os.name == 'nt':
        subprocess.Popen(f"TASKKILL /F /PID {process.pid} /T")
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)


def merge_jsons(image_json, video_json, output_file_path):
    """Merge image and video JSON files into a single JSON file.

    Args:
        image_json: Path to the image recognition JSON file
        video_json: Path to the video recognition JSON file
        output_file_path: Path to save the merged JSON file
    """
    # Load the image recognition JSON file
    if image_json and os.path.isfile(image_json):
        with open(image_json, 'r') as image_file:
            image_data = json.load(image_file)
    else:
        image_data = None

    # Load the video recognition JSON file
    if video_json and os.path.isfile(video_json):
        with open(video_json, 'r') as video_file:
            video_data = json.load(video_file)
    else:
        video_data = None

    # Merge the data
    if image_data and video_data:
        merged_images = image_data['images'] + video_data['images']
        detection_categories = image_data['detection_categories']
        info = image_data['info']
        classification_categories = image_data.get('classification_categories', {})
        forbidden_classes = image_data.get('forbidden_classes', {})
    elif image_data:
        merged_images = image_data['images']
        detection_categories = image_data['detection_categories']
        info = image_data['info']
        classification_categories = image_data.get('classification_categories', {})
        forbidden_classes = image_data.get('forbidden_classes', {})
    elif video_data:
        merged_images = video_data['images']
        detection_categories = video_data['detection_categories']
        info = video_data['info']
        classification_categories = video_data.get('classification_categories', {})
        forbidden_classes = video_data.get('forbidden_classes', {})
    else:
        print("No valid JSON files provided for merging")
        return False

    # Create the merged data
    merged_data = {
        "images": merged_images,
        "detection_categories": detection_categories,
        "info": info,
        "classification_categories": classification_categories,
        "forbidden_classes": forbidden_classes
    }

    # Save the merged data to a new JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(merged_data, output_file, indent=1)

    print(f'Merged JSON file saved to {output_file_path}')
    return True


def process_results(folder_path, simple_mode=False, timelapse_mode=False):
    """Process results after detection and classification, including merging JSON files.

    Args:
        folder_path: Path to the folder containing the results
        simple_mode: Whether to use simple mode defaults
        timelapse_mode: Whether to use timelapse mode
    """
    # Paths to JSON files
    image_recognition_file = os.path.join(folder_path, "image_recognition_file.json")
    image_recognition_file_original = os.path.join(folder_path, "image_recognition_file_original.json")
    video_recognition_file = os.path.join(folder_path, "video_recognition_file.json")
    video_recognition_file_original = os.path.join(folder_path, "video_recognition_file_original.json")
    video_recognition_file_frame = os.path.join(folder_path, "video_recognition_file.frames.json")
    video_recognition_file_frame_original = os.path.join(folder_path, "video_recognition_file.frames_original.json")
    timelapse_json = os.path.join(folder_path, "timelapse_recognition_file.json")
    exif_data_json = os.path.join(folder_path, "exif_data.json")

    # Convert frame JSONs to video JSONs if frames are classified
    if all(os.path.isfile(f) for f in [video_recognition_file, video_recognition_file_frame, video_recognition_file_frame_original]):
        try:
            # Get the frame rates from the video_recognition_file.json
            frame_rates = {}
            with open(video_recognition_file) as f:
                data = json.load(f)
                for image in data.get('images', []):
                    file = image.get('file', '')
                    frame_rate = image.get('frame_rate', 30)
                    frame_rates[file] = frame_rate

            # Define options for conversion
            from cameratraps.megadetector.detection.video_utils import FrameToVideoOptions
            options = FrameToVideoOptions()
            options.include_all_processed_frames = timelapse_mode

            # Convert frame results to video results
            from cameratraps.megadetector.detection.video_utils import frame_results_to_video_results
            frame_results_to_video_results(
                input_file=video_recognition_file_frame,
                output_file=video_recognition_file,
                options=options,
                video_filename_to_frame_rate=frame_rates
            )
            frame_results_to_video_results(
                input_file=video_recognition_file_frame_original,
                output_file=video_recognition_file_original,
                options=options,
                video_filename_to_frame_rate=frame_rates
            )

            print("Successfully converted frame results to video results")
        except Exception as e:
            print(f"Error converting frame results to video results: {str(e)}")
            traceback.print_exc()

    # Remove unnecessary JSONs after conversion
    for file_path in [video_recognition_file_frame_original, video_recognition_file_frame, exif_data_json]:
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Prepare for Timelapse use
    if timelapse_mode:
        # Merge JSON files
        cls_model_idx = load_global_vars().get('var_cls_model_idx', 0)
        if cls_model_idx > 0:  # If classification model selected
            source_img = image_recognition_file_original if os.path.isfile(image_recognition_file_original) else None
            source_vid = video_recognition_file_original if os.path.isfile(video_recognition_file_original) else None
        else:
            source_img = image_recognition_file if os.path.isfile(image_recognition_file) else None
            source_vid = video_recognition_file if os.path.isfile(video_recognition_file) else None

        # Merge the JSONs
        merge_jsons(source_img, source_vid, timelapse_json)

        # Remove unnecessary JSONs
        for file_path in [image_recognition_file_original, image_recognition_file,
                         video_recognition_file_original, video_recognition_file]:
            if os.path.isfile(file_path):
                os.remove(file_path)
    else:
        # For AddaxAI, just remove the originals
        for file_path in [image_recognition_file_original, video_recognition_file_original]:
            if os.path.isfile(file_path):
                os.remove(file_path)
