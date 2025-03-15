# backend/postprocess.py
"""
Handles the post-processing functionality for images and videos after detection and classification.

1. The core `PostProcessor` class with the main processing logic
2. Helper methods for specific tasks within the post-processing workflow
3. Methods for handling different export formats (CSV, XLSX, COCO)
4. A simplified module-level function for easy access to the functionality
"""

import os
import re
import sys
import cv2
import json
import math
import time
import shutil
import datetime
import traceback
import numpy as np
import pandas as pd
from PIL import Image, ExifTags
from pathlib import Path
from GPSPhoto import gpsphoto

from . import AddaxAI_files, bb, IMG_EXTENSIONS, VIDEO_EXTENSIONS
from .utils import fetch_label_map_from_json, check_json_paths, make_json_relative, make_json_absolute


# Dictionary for confidence directory naming
conf_dirs = {
    0.0: "conf_0.0",
    0.1: "conf_0.0-0.1",
    0.2: "conf_0.1-0.2",
    0.3: "conf_0.2-0.3",
    0.4: "conf_0.3-0.4",
    0.5: "conf_0.4-0.5",
    0.6: "conf_0.5-0.6",
    0.7: "conf_0.6-0.7",
    0.8: "conf_0.7-0.8",
    0.9: "conf_0.8-0.9",
    1.0: "conf_0.9-1.0"
}

# Define data types for CSV import to optimize memory usage for large files
dtypes = {
    'absolute_path': 'str',
    'relative_path': 'str',
    'data_type': 'str',
    'label': 'str',
    'confidence': 'float64',
    'human_verified': 'bool',
    'bbox_left': 'str',
    'bbox_top': 'str',
    'bbox_right': 'str',
    'bbox_bottom': 'str',
    'file_height': 'str',
    'file_width': 'str',
    'DateTimeOriginal': 'str',
    'DateTime': 'str',
    'DateTimeDigitized': 'str',
    'Latitude': 'str',
    'Longitude': 'str',
    'GPSLink': 'str',
    'Altitude': 'str',
    'Make': 'str',
    'Model': 'str',
    'Flash': 'str',
    'ExifOffset': 'str',
    'ResolutionUnit': 'str',
    'YCbCrPositioning': 'str',
    'XResolution': 'str',
    'YResolution': 'str',
    'ExifVersion': 'str',
    'ComponentsConfiguration': 'str',
    'FlashPixVersion': 'str',
    'ColorSpace': 'str',
    'ExifImageWidth': 'str',
    'ISOSpeedRatings': 'str',
    'ExifImageHeight': 'str',
    'ExposureMode': 'str',
    'WhiteBalance': 'str',
    'SceneCaptureType': 'str',
    'ExposureTime': 'str',
    'Software': 'str',
    'Sharpness': 'str',
    'Saturation': 'str',
    'ReferenceBlackWhite': 'str',
    'n_detections': 'int64',
    'max_confidence': 'float64',
}


class PostProcessor:
    """Class for post-processing detection and classification results."""

    def __init__(self, src_dir, dst_dir, progress_callback=None):
        """Initialize the post-processor.

        Args:
            src_dir: Source directory with detection/classification results
            dst_dir: Destination directory for post-processed files
            progress_callback: Function to call with progress updates
        """
        self.src_dir = src_dir
        self.dst_dir = dst_dir
        self.progress_callback = progress_callback
        self.cancel_requested = False
        self.error_log_path = os.path.join(dst_dir, "postprocessing_error_log.txt")

    def cancel(self):
        """Request cancellation of the current process."""
        self.cancel_requested = True

    def process(self, thresh=0.2, sep=False, file_placement=1, sep_conf=False,
                vis=False, crp=False, exp=False, plt=False, exp_format="CSV", data_type="img"):
        """Process files based on the specified options.

        Args:
            thresh: Confidence threshold for detections
            sep: Whether to separate files into subdirectories by class
            file_placement: 1 for move, 2 for copy
            sep_conf: Whether to separate by confidence level
            vis: Whether to visualize detections
            crp: Whether to crop detections
            exp: Whether to export results
            plt: Whether to create plots
            exp_format: Export format (CSV, XLSX, COCO)
            data_type: Type of data to process ('img' or 'vid')

        Returns:
            bool: True if successful, False if cancelled or error
        """
        # Log execution
        print(f"EXECUTED: PostProcessor.process(thresh={thresh}, sep={sep}, file_placement={file_placement}, "
              f"sep_conf={sep_conf}, vis={vis}, crp={crp}, exp={exp}, plt={plt}, "
              f"exp_format={exp_format}, data_type={data_type})\n")

        # Update progress
        if self.progress_callback:
            self.progress_callback(process=f"{data_type}_pst", status="load")

        # Initialize variables
        start_time = time.time()
        nloop = 1
        json_paths_converted = False

        # Get the appropriate recognition file
        if data_type == "img":
            recognition_file = os.path.join(self.src_dir, "image_recognition_file.json")
        else:
            recognition_file = os.path.join(self.src_dir, "video_recognition_file.json")

        # Make sure JSON has relative paths for processing
        if check_json_paths(recognition_file) != "relative":
            make_json_relative(recognition_file, self.src_dir)
            json_paths_converted = True

        # If plotting is requested but export isn't, we need to export first
        remove_csv = False
        if plt and not exp:
            # Check if CSV files already exist
            if not (os.path.isfile(os.path.join(self.dst_dir, "results_detections.csv")) and
                    os.path.isfile(os.path.join(self.dst_dir, "results_files.csv"))):
                exp = True
                exp_format = "CSV"
                remove_csv = True

        # Get label map
        label_map = fetch_label_map_from_json(recognition_file)
        inverted_label_map = {v: k for k, v in label_map.items()}

        # Create list of colors for visualization
        colors = []
        if vis:
            colors = ["fuchsia", "blue", "orange", "yellow", "green", "red", "aqua",
                      "navy", "teal", "olive", "lime", "maroon", "purple"]
            colors = colors * 30

        # Initialize CSV files if export is requested
        if exp:
            self._initialize_csv_files(self.dst_dir)

        # Open JSON file
        with open(recognition_file) as json_file:
            data = json.load(json_file)
        n_images = len(data['images'])

        # Process each image
        for image in data['images']:
            # Check for cancellation
            if self.cancel_requested:
                break

            # Check for failure in processing
            if "failure" in image:
                self._log_error(f"File '{image['file']}' was skipped by post processing features because '{image['failure']}'")

                # Update progress
                if self.progress_callback:
                    elapsed_time = str(datetime.timedelta(seconds=round(time.time() - start_time)))
                    remaining = (time.time() - start_time) * n_images / nloop - (time.time() - start_time)
                    time_left = str(datetime.timedelta(seconds=round(remaining)))
                    self.progress_callback(
                        process=f"{data_type}_pst",
                        status="running",
                        cur_it=nloop,
                        tot_it=n_images,
                        time_ela=elapsed_time,
                        time_rem=time_left,
                        cancel_func=self.cancel
                    )

                nloop += 1
                continue

            # Get image info
            file = image['file']
            detections_list = image.get('detections', [])
            n_detections = len(detections_list)

            # Check if manually verified
            manually_checked = False
            if 'manually_checked' in image and image['manually_checked']:
                manually_checked = True

            # Initialize variables for this image
            max_detection_conf = 0.0
            unique_labels = []
            bbox_info = []

            # Process each detection
            if vis or crp or exp:
                # Open image
                if data_type == "img":
                    im_path = os.path.join(self.src_dir, file)
                    im_to_vis = cv2.imread(os.path.normpath(im_path))

                    # Check if image was loaded successfully
                    if im_to_vis is None:
                        self._log_error(f"File '{image['file']}' was skipped by post processing features. This might be due to the file being moved or deleted after analysis, or because of a special character in the file path.")

                        # Update progress
                        if self.progress_callback:
                            elapsed_time = str(datetime.timedelta(seconds=round(time.time() - start_time)))
                            remaining = (time.time() - start_time) * n_images / nloop - (time.time() - start_time)
                            time_left = str(datetime.timedelta(seconds=round(remaining)))
                            self.progress_callback(
                                process=f"{data_type}_pst",
                                status="running",
                                cur_it=nloop,
                                tot_it=n_images,
                                time_ela=elapsed_time,
                                time_rem=time_left,
                                cancel_func=self.cancel
                            )

                        nloop += 1
                        continue

                    # Get EXIF data
                    try:
                        orig_image = Image.open(im_path)
                        exif = orig_image.info.get('exif')
                        orig_image.close()
                    except:
                        exif = None

                elif data_type == "vid":
                    vid = cv2.VideoCapture(os.path.join(self.src_dir, file))

            # Extract metadata for export
            exif_params = []
            if exp:
                exif_data = self._extract_metadata(os.path.join(self.src_dir, file))

                for param in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'Latitude', 'Longitude',
                              'GPSLink', 'Altitude', 'Make', 'Model', 'Flash', 'ExifOffset', 'ResolutionUnit',
                              'YCbCrPositioning', 'XResolution', 'YResolution', 'ExifVersion', 'ComponentsConfiguration',
                              'FlashPixVersion', 'ColorSpace', 'ExifImageWidth', 'ISOSpeedRatings', 'ExifImageHeight',
                              'ExposureMode', 'WhiteBalance', 'SceneCaptureType', 'ExposureTime', 'Software',
                              'Sharpness', 'Saturation', 'ReferenceBlackWhite']:
                    try:
                        if param.startswith('DateTime'):
                            datetime_raw = str(exif_data[param])
                            param_value = datetime.datetime.strptime(datetime_raw, '%Y:%m:%d %H:%M:%S').strftime('%d/%m/%y %H:%M:%S')
                        else:
                            param_value = str(exif_data[param])
                    except:
                        param_value = "NA"
                    exif_params.append(param_value)

            # Process detections in the image
            if 'detections' in image:
                for detection in image['detections']:
                    # Get confidence
                    conf = detection["conf"]

                    # Track maximum confidence
                    if not manually_checked and conf > max_detection_conf:
                        max_detection_conf = conf

                    # Only process detections above threshold
                    if conf >= thresh:
                        # Handle manually verified images
                        if manually_checked:
                            conf = "NA"

                        # Get detection info
                        category = detection["category"]
                        label = label_map[category]

                        # Track unique labels for separation
                        if sep:
                            unique_labels.append(label)
                            unique_labels = sorted(list(set(unique_labels)))

                        # Extract bounding box info for visualization/cropping/export
                        if vis or crp or exp:
                            if data_type == "img":
                                height, width = im_to_vis.shape[:2]
                            else:
                                height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
                                width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

                            w_box = detection['bbox'][2]
                            h_box = detection['bbox'][3]
                            xo = detection['bbox'][0] + (w_box/2)
                            yo = detection['bbox'][1] + (h_box/2)
                            left = int(round(detection['bbox'][0] * width))
                            top = int(round(detection['bbox'][1] * height))
                            right = int(round(w_box * width)) + left
                            bottom = int(round(h_box * height)) + top

                            bbox_info.append([label, conf, manually_checked, left, top, right, bottom, height, width, xo, yo, w_box, h_box])

            # Separate files into directories based on detections
            if sep:
                if n_detections == 0:
                    file = self._move_files(file, "empty", file_placement, max_detection_conf, sep_conf, manually_checked)
                else:
                    if len(unique_labels) > 1:
                        labels_str = "_".join(unique_labels)
                        file = self._move_files(file, labels_str, file_placement, max_detection_conf, sep_conf, manually_checked)
                    elif len(unique_labels) == 0:
                        file = self._move_files(file, "empty", file_placement, max_detection_conf, sep_conf, manually_checked)
                    else:
                        file = self._move_files(file, unique_labels[0], file_placement, max_detection_conf, sep_conf, manually_checked)

            # Export to CSV
            if exp and len(bbox_info) > 0:
                self._export_to_csv(file, data_type, bbox_info, exif_params, manually_checked, max_detection_conf)
            elif exp:
                # Export file info even if no detections
                with Image.open(os.path.normpath(os.path.join(self.src_dir, file))) as pil_img:
                    file_width, file_height = pil_img.size

                row = pd.DataFrame([[self.src_dir, file, data_type, 0, file_height, file_width, max_detection_conf, manually_checked, *exif_params]])
                row.to_csv(os.path.join(self.dst_dir, "results_files.csv"), encoding='utf-8', mode='a', index=False, header=False)

            # Visualize images
            if vis and data_type == "img" and len(bbox_info) > 0:
                self._visualize_image(im_to_vis, bbox_info, file, exif, colors, inverted_label_map)

            # Crop detections
            if crp and data_type == "img" and len(bbox_info) > 0:
                self._crop_detections(file, bbox_info, sep, exif)

            # Update progress
            if self.progress_callback:
                elapsed_time = str(datetime.timedelta(seconds=round(time.time() - start_time)))
                remaining = (time.time() - start_time) * n_images / nloop - (time.time() - start_time)
                time_left = str(datetime.timedelta(seconds=round(remaining)))
                self.progress_callback(
                    process=f"{data_type}_pst",
                    status="running",
                    cur_it=nloop,
                    tot_it=n_images,
                    time_ela=elapsed_time,
                    time_rem=time_left,
                    cancel_func=self.cancel
                )

            nloop += 1

        # Convert CSV to other formats if required
        if exp:
            self._create_summary_csv()

            if exp_format == "XLSX":
                self._convert_csv_to_xlsx()
            elif exp_format == "COCO":
                self._convert_csv_to_coco()

            # Remove CSV files if not needed
            if not plt and exp_format != "CSV" or remove_csv:
                for result_type in ['detections', 'files', 'summary']:
                    csv_path = os.path.join(self.dst_dir, f"results_{result_type}.csv")
                    if os.path.isfile(csv_path):
                        os.remove(csv_path)

        # Change JSON paths back if converted earlier
        if json_paths_converted:
            make_json_absolute(recognition_file, self.src_dir)

        # Create plots if requested
        if plt and not self.cancel_requested:
            from . plot_utils import produce_plots
            produce_plots(self.dst_dir, self.progress_callback)

        # Update progress to done
        if self.progress_callback:
            self.progress_callback(process=f"{data_type}_pst", status="done")

        return not self.cancel_requested
    def _log_error(self, message):
        """Log an error message to the postprocessing error log.

        Args:
            message: Error message to log
        """
        with open(self.error_log_path, 'a+') as f:
            f.write(f"{message}\n")

    def _move_files(self, file, detection_type, file_placement, max_detection_conf, sep_conf, manually_checked):
        """Move or copy files into appropriate subdirectories.

        Args:
            file: Relative path to the file
            detection_type: Type of detection/class name
            file_placement: 1 for move, 2 for copy
            max_detection_conf: Maximum confidence value
            sep_conf: Whether to separate by confidence level
            manually_checked: Whether the file was manually verified

        Returns:
            str: New relative path of the file
        """
        print(f"EXECUTED: _move_files({file}, {detection_type}, {file_placement}, {max_detection_conf}, {sep_conf}, {manually_checked})")

        # Determine target directory with confidence level if requested
        if sep_conf and detection_type != "empty":
            if manually_checked:
                confidence_dir = "verified"
            else:
                ceiled_confidence = math.ceil(max_detection_conf * 10) / 10.0
                confidence_dir = conf_dirs[ceiled_confidence]
            new_file = os.path.join(detection_type, confidence_dir, file)
        else:
            new_file = os.path.join(detection_type, file)

        # Set source and destination paths
        src = os.path.join(self.src_dir, file)
        dst = os.path.join(self.dst_dir, new_file)

        # Create subfolder if it doesn't exist
        Path(os.path.dirname(dst)).mkdir(parents=True, exist_ok=True)

        # Move or copy the file
        if file_placement == 1:  # move
            shutil.move(src, dst)
        elif file_placement == 2:  # copy
            shutil.copy2(src, dst)

        # Return the new relative path
        return new_file

    def _initialize_csv_files(self, dst_dir):
        """Initialize CSV files for export.

        Args:
            dst_dir: Destination directory for CSV files
        """
        # For files
        csv_for_files = os.path.join(dst_dir, "results_files.csv")
        if not os.path.isfile(csv_for_files):
            df = pd.DataFrame(
                list(),
                columns=[
                    "absolute_path", "relative_path", "data_type", "n_detections",
                    "file_height", "file_width", "max_confidence", "human_verified",
                    'DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'Latitude',
                    'Longitude', 'GPSLink', 'Altitude', 'Make', 'Model', 'Flash',
                    'ExifOffset', 'ResolutionUnit', 'YCbCrPositioning', 'XResolution',
                    'YResolution', 'ExifVersion', 'ComponentsConfiguration', 'FlashPixVersion',
                    'ColorSpace', 'ExifImageWidth', 'ISOSpeedRatings', 'ExifImageHeight',
                    'ExposureMode', 'WhiteBalance', 'SceneCaptureType', 'ExposureTime',
                    'Software', 'Sharpness', 'Saturation', 'ReferenceBlackWhite'
                ]
            )
            df.to_csv(csv_for_files, encoding='utf-8', index=False)

        # For detections
        csv_for_detections = os.path.join(dst_dir, "results_detections.csv")
        if not os.path.isfile(csv_for_detections):
            df = pd.DataFrame(
                list(),
                columns=[
                    "absolute_path", "relative_path", "data_type", "label", "confidence",
                    "human_verified", "bbox_left", "bbox_top", "bbox_right", "bbox_bottom",
                    "file_height", "file_width", 'DateTimeOriginal', 'DateTime', 'DateTimeDigitized',
                    'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make', 'Model', 'Flash',
                    'ExifOffset', 'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution',
                    'ExifVersion', 'ComponentsConfiguration', 'FlashPixVersion', 'ColorSpace',
                    'ExifImageWidth', 'ISOSpeedRatings', 'ExifImageHeight', 'ExposureMode',
                    'WhiteBalance', 'SceneCaptureType', 'ExposureTime', 'Software', 'Sharpness',
                    'Saturation', 'ReferenceBlackWhite'
                ]
            )
            df.to_csv(csv_for_detections, encoding='utf-8', index=False)

    def _extract_metadata(self, file_path):
        """Extract metadata from an image.

        Args:
            file_path: Path to the image file

        Returns:
            dict: Dictionary of metadata
        """
        # Try to read EXIF data
        metadata = {}
        try:
            img_for_exif = Image.open(file_path)
            if hasattr(img_for_exif, '_getexif') and img_for_exif._getexif():
                metadata = {
                    ExifTags.TAGS[k]: v
                    for k, v in img_for_exif._getexif().items()
                    if k in ExifTags.TAGS
                }
            img_for_exif.close()
        except:
            metadata = {
                'GPSInfo': None,
                'ResolutionUnit': None,
                'ExifOffset': None,
                'Make': None,
                'Model': None,
                'DateTime': None,
                'YCbCrPositioning': None,
                'XResolution': None,
                'YResolution': None,
                'ExifVersion': None,
                'ComponentsConfiguration': None,
                'ShutterSpeedValue': None,
                'DateTimeOriginal': None,
                'DateTimeDigitized': None,
                'FlashPixVersion': None,
                'UserComment': None,
                'ColorSpace': None,
                'ExifImageWidth': None,
                'ExifImageHeight': None
            }

        # Try to add GPS data
        gpsinfo = {}
        try:
            gpsdata = gpsphoto.getGPSData(file_path)
            if 'Latitude' in gpsdata and 'Longitude' in gpsdata:
                gpsinfo = gpsdata.copy()
                gpsinfo['GPSLink'] = f"https://maps.google.com/?q={gpsdata['Latitude']},{gpsdata['Longitude']}"
        except:
            gpsinfo = {
                'Latitude': None,
                'Longitude': None,
                'GPSLink': None,
                'Altitude': None
            }

        # Combine metadata
        return {**metadata, **gpsinfo}

    def _export_to_csv(self, file, data_type, bbox_info, exif_params, manually_checked, max_detection_conf):
        """Export detection and file information to CSV.

        Args:
            file: Relative path to the file
            data_type: Type of data ('img' or 'vid')
            bbox_info: List of bounding box information
            exif_params: List of EXIF parameters
            manually_checked: Whether the file was manually verified
            max_detection_conf: Maximum confidence value
        """
        # File info CSV
        file_height = bbox_info[0][7]
        file_width = bbox_info[0][8]
        row = pd.DataFrame([[self.src_dir, file, data_type, len(bbox_info), file_height, file_width, max_detection_conf, manually_checked, *exif_params]])
        row.to_csv(os.path.join(self.dst_dir, "results_files.csv"), encoding='utf-8', mode='a', index=False, header=False)

        # Detections info CSV
        rows = []
        for bbox in bbox_info:
            row = [self.src_dir, file, data_type, *bbox[:9], *exif_params]
            rows.append(row)
        rows = pd.DataFrame(rows)
        rows.to_csv(os.path.join(self.dst_dir, "results_detections.csv"), encoding='utf-8', mode='a', index=False, header=False)

    def _create_summary_csv(self):
        """Create a summary CSV file of detections by label and data type."""
        csv_for_summary = os.path.join(self.dst_dir, "results_summary.csv")
        if os.path.exists(csv_for_summary):
            os.remove(csv_for_summary)

        try:
            det_info = pd.DataFrame(pd.read_csv(os.path.join(self.dst_dir, "results_detections.csv"), dtype=dtypes, low_memory=False))
            summary = pd.DataFrame(det_info.groupby(['label', 'data_type']).size().sort_values(ascending=False).reset_index(name='n_detections'))
            summary.to_csv(csv_for_summary, encoding='utf-8', mode='w', index=False, header=True)
        except Exception as e:
            self._log_error(f"Error creating summary CSV: {str(e)}")

    def _visualize_image(self, im_to_vis, bbox_info, file, exif, colors, inverted_label_map):
        """Visualize detections on an image.

        Args:
            im_to_vis: OpenCV image to visualize on
            bbox_info: List of bounding box information
            file: Relative path to the file
            exif: EXIF data to preserve
            colors: List of colors for visualization
            inverted_label_map: Inverted label map for color selection
        """
        try:
            # Blur people if requested
            if self.blur_people:
                for bbox in bbox_info:
                    if bbox[0] == "person":
                        im_to_vis = self._blur_box(im_to_vis, *bbox[3:7], bbox[8], bbox[7])

            # Draw bounding boxes
            if self.draw_bboxes:
                for bbox in bbox_info:
                    if bbox[2]:  # manually_checked
                        vis_label = f"{bbox[0]} (verified)"
                    else:
                        conf_label = round(float(bbox[1]), 2) if isinstance(bbox[1], (float, int)) else 0.99
                        vis_label = f"{bbox[0]} {conf_label}"

                    color = colors[int(inverted_label_map[bbox[0]])]
                    bb.add(im_to_vis, *bbox[3:7], vis_label, color, size=self.bbox_size)

            # Save the image
            output_path = os.path.join(self.dst_dir, file)
            Path(os.path.dirname(output_path)).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(output_path, im_to_vis)

            # Preserve EXIF data
            if exif is not None:
                image_new = Image.open(output_path)
                image_new.save(output_path, exif=exif)
                image_new.close()

        except Exception as e:
            self._log_error(f"Error visualizing image {file}: {str(e)}")

    def _crop_detections(self, file, bbox_info, sep, exif):
        """Crop detections from an image.

        Args:
            file: Relative path to the file
            bbox_info: List of bounding box information
            sep: Whether files were separated (affects source path)
            exif: EXIF data to preserve
        """
        try:
            counter = 1
            for bbox in bbox_info:
                # Open image from correct location
                if sep:
                    im_to_crp = Image.open(os.path.join(self.dst_dir, file))
                else:
                    im_to_crp = Image.open(os.path.join(self.src_dir, file))

                # Crop the image
                crp_im = im_to_crp.crop((bbox[3:7]))
                im_to_crp.close()

                # Save the cropped image
                filename, file_extension = os.path.splitext(file)
                im_path = os.path.join(self.dst_dir, filename + '_crop' + str(counter) + '_' + bbox[0] + file_extension)
                Path(os.path.dirname(im_path)).mkdir(parents=True, exist_ok=True)
                crp_im.save(im_path)
                counter += 1

                # Preserve EXIF data
                if exif is not None:
                    image_new = Image.open(im_path)
                    image_new.save(im_path, exif=exif)
                    image_new.close()

        except Exception as e:
            self._log_error(f"Error cropping image {file}: {str(e)}")

    def _blur_box(self, image, bbox_left, bbox_top, bbox_right, bbox_bottom, image_width, image_height):
        """Blur a portion of an image (for privacy).

        Args:
            image: OpenCV image to blur
            bbox_left, bbox_top, bbox_right, bbox_bottom: Bounding box coordinates
            image_width, image_height: Image dimensions

        Returns:
            np.ndarray: Blurred image
        """
        try:
            x1, y1, x2, y2 = map(int, [bbox_left, bbox_top, bbox_right, bbox_bottom])

            # Validate coordinates
            if x1 >= x2 or y1 >= y2 or x1 < 0 or y1 < 0 or x2 > image_width or y2 > image_height:
                raise ValueError(f"Invalid bounding box: ({x1}, {y1}, {x2}, {y2})")

            # Extract region of interest
            roi = image[y1:y2, x1:x2]
            if roi.size == 0:
                raise ValueError("Extracted ROI is empty. Check the bounding box coordinates.")

            # Apply Gaussian blur
            blurred_roi = cv2.GaussianBlur(roi, (71, 71), 0)

            # Replace the region with the blurred version
            image[y1:y2, x1:x2] = blurred_roi

            return image

        except Exception as e:
            self._log_error(f"Error blurring box: {str(e)}")
            return image

    def _convert_csv_to_xlsx(self):
        """Convert CSV files to a single XLSX file with multiple sheets."""
        import pandas as pd

        xlsx_path = os.path.join(self.dst_dir, "results.xlsx")

        try:
            # Check if Excel file already exists
            dfs = []
            for result_type in ['detections', 'files', 'summary']:
                csv_path = os.path.join(self.dst_dir, f"results_{result_type}.csv")

                if os.path.isfile(xlsx_path):
                    # Add new rows to existing ones
                    df_xlsx = pd.read_excel(xlsx_path, sheet_name=result_type)
                    df_csv = pd.read_csv(csv_path, dtype=dtypes, low_memory=False)
                    df = pd.concat([df_xlsx, df_csv], ignore_index=True)
                else:
                    df = pd.read_csv(csv_path, dtype=dtypes, low_memory=False)

                dfs.append(df)

            # Write to Excel file
            with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
                for idx, result_type in enumerate(['detections', 'files', 'summary']):
                    df = dfs[idx]
                    if result_type in ['detections', 'files']:
                        # Convert date columns to datetime objects
                        for date_col in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
                            try:
                                df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%y %H:%M:%S', errors='coerce')
                            except:
                                pass
                    df.to_excel(writer, sheet_name=result_type, index=None, header=True)

        except Exception as e:
            self._log_error(f"Error converting CSV to XLSX: {str(e)}")

    def _convert_csv_to_coco(self):
        """Convert CSV files to COCO format JSON."""
        try:
            # Initialize paths
            coco_path = os.path.join(self.dst_dir, "results_coco.json")

            # Read CSV files
            detections_df = pd.read_csv(os.path.join(self.dst_dir, "results_detections.csv"), dtype=dtypes, low_memory=False)
            files_df = pd.read_csv(os.path.join(self.dst_dir, "results_files.csv"), dtype=dtypes, low_memory=False)

            # Convert to COCO format
            self._csv_to_coco(detections_df, files_df, coco_path)

        except Exception as e:
            self._log_error(f"Error converting CSV to COCO: {str(e)}")

    def _csv_to_coco(self, detections_df, files_df, output_path):
        """Convert detection and file DataFrames to COCO format JSON.

        Args:
            detections_df: DataFrame of detections
            files_df: DataFrame of files
            output_path: Path to save COCO JSON
        """
        # Initialize COCO structure
        coco = {
            "images": [],
            "annotations": [],
            "categories": [],
            "licenses": [{
                "id": 1,
                "name": "Unknown",
                "url": "NA"
            }],
            "info": {
                "description": f"Object detection results exported from AddaxAI.",
                "url": "https://addaxdatascience.com/addaxai/",
                "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        # Prepare categories and mapping
        category_mapping = {}
        current_category_id = 1

        # Assign categories from detections
        for label in detections_df['label'].unique():
            if label not in category_mapping:
                category_mapping[label] = current_category_id
                coco['categories'].append({
                    "id": current_category_id,
                    "name": label
                })
                current_category_id += 1

        # Process images and annotations
        annotation_id = 1
        for _, file_info in files_df.iterrows():
            # Create image entry
            image_id = len(coco['images']) + 1

            # Get date captured
            if pd.isna(file_info['DateTimeOriginal']) or file_info['DateTimeOriginal'] == 'NA':
                date_captured = "NA"
            else:
                try:
                    date_captured = datetime.datetime.strptime(
                        file_info['DateTimeOriginal'],
                        "%d/%m/%y %H:%M:%S"
                    ).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    date_captured = "NA"

            # Add image to COCO
            image_entry = {
                "id": image_id,
                "width": int(file_info['file_width']),
                "height": int(file_info['file_height']),
                "file_name": file_info['relative_path'],
                "license": 1,
                "date_captured": date_captured
            }
            coco['images'].append(image_entry)

            # Add annotations for this image
            image_detections = detections_df[detections_df['relative_path'] == file_info['relative_path']]
            for _, detection in image_detections.iterrows():
                try:
                    bbox_left = int(float(detection['bbox_left']))
                    bbox_top = int(float(detection['bbox_top']))
                    bbox_right = int(float(detection['bbox_right']))
                    bbox_bottom = int(float(detection['bbox_bottom']))

                    bbox_width = bbox_right - bbox_left
                    bbox_height = bbox_bottom - bbox_top

                    annotation_entry = {
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": category_mapping[detection['label']],
                        "bbox": [bbox_left, bbox_top, bbox_width, bbox_height],
                        "area": float(bbox_width * bbox_height),
                        "iscrowd": 0
                    }
                    coco['annotations'].append(annotation_entry)
                    annotation_id += 1
                except Exception as e:
                    self._log_error(f"Error creating annotation for detection: {str(e)}")

        # Save to file
        with open(output_path, 'w') as output_file:
            json.dump(coco, output_file, indent=4)

def postprocess(src_dir, dst_dir, thresh=0.2, sep=False, file_placement=1,
                sep_conf=False, vis=False, crp=False, exp=False, plt=False,
                exp_format="CSV", data_type="img", progress_callback=None,
                vis_settings=None):
    """Post-process detection/classification results.

    Args:
        src_dir: Source directory with detection/classification results
        dst_dir: Destination directory for post-processed files
        thresh: Confidence threshold for detections
        sep: Whether to separate files into subdirectories by class
        file_placement: 1 for move, 2 for copy
        sep_conf: Whether to separate by confidence level
        vis: Whether to visualize detections
        crp: Whether to crop detections
        exp: Whether to export results
        plt: Whether to create plots
        exp_format: Export format (CSV, XLSX, COCO)
        data_type: Type of data to process ('img' or 'vid')
        progress_callback: Function to call with progress updates
        vis_settings: Dictionary with visualization settings

    Returns:
        bool: True if successful, False if cancelled or error
    """
    print(f"EXECUTED: postprocess({locals()})\n")

    # Create post-processor
    processor = PostProcessor(src_dir, dst_dir, progress_callback)

    # Set visualization properties if provided
    if vis_settings:
        processor.blur_people = vis_settings.get('blur_people', False)
        processor.draw_bboxes = vis_settings.get('draw_bboxes', True)
        processor.bbox_size = vis_settings.get('bbox_size', 1)
    else:
        processor.blur_people = True
        processor.draw_bboxes = True
        processor.bbox_size = 1

    # Run the post-processing
    success = processor.process(
        thresh=thresh,
        sep=sep,
        file_placement=file_placement,
        sep_conf=sep_conf,
        vis=vis,
        crp=crp,
        exp=exp,
        plt=plt,
        exp_format=exp_format,
        data_type=data_type
    )

    return success
