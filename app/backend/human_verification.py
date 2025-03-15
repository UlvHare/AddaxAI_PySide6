# backend/human_verification.py
"""
Handles the human-in-the-loop verification process. This module will provide
functionality for users to verify and annotate the detection results.
"""
import os
import re
import sys
import json
import glob
import pickle
import random
import shutil
import subprocess
import platform
import xml.etree.cElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image, ImageFile

from . import AddaxAI_files
from .utils import fetch_label_map_from_json, check_json_paths, make_json_relative, make_json_absolute

class HumanVerification:
    """Class for managing human-in-the-loop verification of detection results."""

    def __init__(self, folder_path, progress_callback=None):
        """Initialize human verification.

        Args:
            folder_path: Path to the folder with detection results
            progress_callback: Function to call with progress updates
        """
        self.folder_path = folder_path
        self.progress_callback = progress_callback
        self.temp_folder = os.path.join(folder_path, 'temp-folder')
        self.file_list_txt = os.path.join(self.temp_folder, 'hitl_file_list.txt')
        self.class_list_txt = os.path.join(self.temp_folder, 'hitl_class_list.txt')
        self.recognition_file = os.path.join(folder_path, 'image_recognition_file.json')

        # Create temp folder if it doesn't exist
        Path(self.temp_folder).mkdir(parents=True, exist_ok=True)

    def prepare_verification(self, selection_criteria):
        """Prepare files for verification based on selection criteria.

        Args:
            selection_criteria: Dictionary of selection criteria for each class

        Returns:
            dict: Statistics about selected files
        """
        print(f"EXECUTED: prepare_verification({selection_criteria})\n")

        # Make sure JSON has relative paths
        json_paths_converted = False
        if check_json_paths(self.recognition_file) != "relative":
            make_json_relative(self.recognition_file, self.folder_path)
            json_paths_converted = True

        # Initialize variables
        label_map = fetch_label_map_from_json(self.recognition_file)
        selected_files = {}
        total_files = 0

        # Extract selection criteria
        selected_categories = []
        min_confs = []
        max_confs = []
        ann_min_confs_specific = {}
        annotation_threshold_mode = selection_criteria.get('annotation_threshold_mode', 1)
        ann_min_confs_generic = selection_criteria.get('ann_min_confs_generic', 0.6)

        # Process class-specific criteria
        for class_name, criteria in selection_criteria.get('classes', {}).items():
            if criteria.get('selected', False):
                selected_categories.append(class_name)
                min_confs.append(criteria.get('min_conf', 0.2))
                max_confs.append(criteria.get('max_conf', 0.8))
                ann_min_confs_specific[class_name] = criteria.get('ann_min_conf', 0.6)
                selected_files[class_name] = []

        # Remove old file list if present
        if os.path.isfile(self.file_list_txt):
            os.remove(self.file_list_txt)

        # Process the recognition file to select files for verification
        img_and_detections_dict = {}
        with open(self.recognition_file, "r") as json_file:
            data = json.load(json_file)

            # Loop through all images
            for image in data.get('images', []):
                image_path = os.path.join(self.folder_path, image['file'])
                annotations = []
                image_already_added = False

                # Check if already manually verified
                human_verified = image.get('manually_checked', False)

                # Check all detections in the image
                if 'detections' in image:
                    for detection in image['detections']:
                        category_id = detection['category']
                        category = label_map.get(category_id, "unknown")
                        conf = detection['conf']

                        # Check if this detection matches selection criteria
                        for i, cat in enumerate(selected_categories):
                            if category == cat and conf >= min_confs[i] and conf <= max_confs[i]:
                                # Add this image to selected files
                                if not image_already_added:
                                    selected_files[cat].append(image_path)
                                    image_already_added = True

                        # Determine whether to display this annotation
                        display_annotation = False

                        # Generic threshold for all classes
                        if annotation_threshold_mode == 1 and conf >= ann_min_confs_generic:
                            display_annotation = True

                        # Class-specific thresholds
                        elif annotation_threshold_mode == 2 and conf >= ann_min_confs_specific.get(category, 0.6):
                            display_annotation = True

                        # Add this detection to annotations list if it should be displayed
                        if display_annotation:
                            # Get image dimensions
                            with Image.open(image_path) as im:
                                width, height = im.size

                            # Calculate bounding box coordinates
                            left = int(round(detection['bbox'][0] * width))  # xmin
                            top = int(round(detection['bbox'][1] * height))  # ymin
                            right = int(round(detection['bbox'][2] * width)) + left  # width + left
                            bottom = int(round(detection['bbox'][3] * height)) + top  # height + top

                            # Format as CSV string: left,top,None,None,right,bottom,None,category
                            annotation_list = [left, top, None, None, right, bottom, None, category]
                            annotation_str = ','.join(map(str, annotation_list))
                            annotations.append(annotation_str)

                # Store annotations for this image
                img_and_detections_dict[image_path] = {"annotations": annotations, "human_verified": human_verified}

        # Apply selection method (all, percentage, or fixed number) and randomization
        for category, files in selected_files.items():
            criteria = selection_criteria.get('classes', {}).get(category, {})
            selection_mode = criteria.get('selection_mode', 1)  # 1=all, 2=percentage, 3=fixed

            # Randomize if not using all files
            if selection_mode != 1:
                random.shuffle(files)

            # Apply percentage selection
            if selection_mode == 2:
                percentage = criteria.get('percentage', 100)
                total_n = len(files)
                n_selected = int(total_n * (percentage / 100))
                files = files[:n_selected]

            # Apply fixed number selection
            elif selection_mode == 3:
                n_selected = criteria.get('count', len(files))
                files = files[:n_selected]

            # Update total count
            total_files += len(files)

            # Sort files naturally
            files.sort(key=self._natural_sort_key)

            # Create file list for verification
            for img in files:
                with open(self.file_list_txt, 'a+') as f:
                    f.write(f"{os.path.normpath(img)}\n")

                # Create XML annotation file if it doesn't exist
                self._create_pascal_voc_annotation(
                    img,
                    img_and_detections_dict[img]["annotations"],
                    img_and_detections_dict[img]["human_verified"]
                )

        # Create class list file
        with open(self.class_list_txt, 'a+') as f:
            for _, v in label_map.items():
                f.write(f"{v}\n")

        # Save selection criteria for later use
        self._save_annotation_info(img_and_detections_dict, label_map)

        # Restore JSON paths if converted
        if json_paths_converted:
            make_json_absolute(self.recognition_file, self.folder_path)

        return {
            "total_files": total_files,
            "files_by_category": {cat: len(files) for cat, files in selected_files.items()}
        }

    def get_verification_status(self):
        """Get the current status of verification.

        Returns:
            dict: Status information including counts
        """
        status = self._get_hitl_status()

        if status == "never-started":
            return {"status": status, "verified_count": 0, "total_count": 0}

        # Count total and verified files
        total_count = 0
        verified_count = 0

        if os.path.isfile(self.file_list_txt):
            with open(self.file_list_txt) as f:
                file_list = f.read().splitlines()
                total_count = len(file_list)

                for img_path in file_list:
                    annotation_path = self._get_xml_path(img_path)
                    if os.path.isfile(annotation_path) and self._check_verification_status(annotation_path):
                        verified_count += 1

        return {
            "status": status,
            "verified_count": verified_count,
            "total_count": total_count
        }

    def start_verification(self):
        """Start or continue the verification process.

        Returns:
            bool: True if verification process was launched successfully
        """
        # Check if there are files to verify
        if not os.path.isfile(self.file_list_txt):
            return False

        # Check for corrupted images
        corrupted_images = self._check_images()

        # Fix corrupted images if found
        if corrupted_images:
            self._fix_images(corrupted_images)

        # Update verification status in JSON
        self._set_hitl_status("in-progress")

        # Get label map
        label_map = fetch_label_map_from_json(self.recognition_file)

        # Launch external verification tool
        return self._launch_verification_tool()

    def complete_verification(self):
        """Complete the verification process by updating the JSON with verified annotations.

        Returns:
            dict: Statistics about verification
        """
        # Update progress
        if self.progress_callback:
            self.progress_callback(status="updating", message="Processing verification results...")

        # Check conversion needed for images
        imgs_needing_converting = []
        verified_count = 0
        total_count = 0

        with open(self.file_list_txt) as f:
            file_list = f.read().splitlines()
            total_count = len(file_list)

            for img_path in file_list:
                annotation_path = self._get_xml_path(img_path)

                # Check which images need converting
                if self._check_if_img_needs_converting(img_path):
                    imgs_needing_converting.append(img_path)

                # Count verified
                if self._check_verification_status(annotation_path):
                    verified_count += 1

        # Make sure JSON has relative paths
        json_paths_converted = False
        if check_json_paths(self.recognition_file) != "relative":
            make_json_relative(self.recognition_file, self.folder_path)
            json_paths_converted = True

        # Get label map
        label_map = fetch_label_map_from_json(self.recognition_file)
        inverted_label_map = {v: k for k, v in label_map.items()}

        # Update the JSON with verified annotations
        self._update_json_from_img_list(imgs_needing_converting, inverted_label_map)

        # Update verification status of images in JSON that were previously verified but now unverified
        with open(self.recognition_file, "r") as json_file:
            data = json.load(json_file)

        for image in data['images']:
            image_path = image['file']
            if json_paths_converted:
                image_path = os.path.join(self.folder_path, image_path)

            if 'manually_checked' in image and image['manually_checked']:
                xml_path = self._get_xml_path(image_path)
                if os.path.isfile(xml_path):
                    if not self._check_verification_status(xml_path):
                        image['manually_checked'] = False
                        if 'detections' in image:
                            for detection in image['detections']:
                                detection['conf'] = 0.7  # reset from 1.0 to arbitrary value

        # Write updated data to JSON
        with open(self.recognition_file, "w") as json_file:
            json.dump(data, json_file, indent=1)

        # Restore JSON paths if converted
        if json_paths_converted:
            make_json_absolute(self.recognition_file, self.folder_path)

        # Mark verification as done if all files verified
        if verified_count == total_count:
            self._set_hitl_status("done")

        return {
            "verified_count": verified_count,
            "total_count": total_count,
            "completed": verified_count == total_count
        }

    def export_verified_data(self, dst_dir, copy_mode=True):
        """Export verified data to a destination directory.

        Args:
            dst_dir: Destination directory for exported data
            copy_mode: Whether to copy (True) or move (False) files

        Returns:
            int: Number of exported files
        """
        # Check if there are files to export
        if not os.path.isfile(self.file_list_txt):
            return 0

        # Get file list
        with open(self.file_list_txt) as f:
            file_list = f.read().splitlines()

        # Count files to export
        total_files = len(file_list)
        if total_files == 0:
            return 0

        # Export each file
        for img_path in file_list:
            # Get image relative path
            img_rel_path = os.path.relpath(img_path, self.folder_path)

            # Create destination paths
            dst_img = os.path.join(dst_dir, img_rel_path)
            Path(os.path.dirname(dst_img)).mkdir(parents=True, exist_ok=True)

            # Copy or move image
            if copy_mode:
                shutil.copy2(img_path, dst_img)
            else:
                shutil.move(img_path, dst_img)

            # Handle annotation file
            ann_rel_path = os.path.splitext(img_rel_path)[0] + ".xml"
            src_ann = self._get_xml_path(img_path)
            dst_ann = os.path.join(dst_dir, ann_rel_path)
            Path(os.path.dirname(dst_ann)).mkdir(parents=True, exist_ok=True)

            # Move the annotation file (always move since it's in the temp folder)
            shutil.move(src_ann, dst_ann)

        # Clean up temp files
        self.cleanup()

        return total_files

    def cleanup(self):
        """Clean up temporary files."""
        if os.path.isdir(self.temp_folder):
            shutil.rmtree(self.temp_folder)

    def _natural_sort_key(self, s):
        """Key function for natural sorting of strings with numbers."""
        return [int(c) if c.isdigit() else c.lower() for c in re.split('(\d+)', s)]

    def _get_xml_path(self, img_path):
        """Get the path to the XML annotation file for an image.

        Args:
            img_path: Path to the image file

        Returns:
            str: Path to the XML annotation file
        """
        head_path = self.folder_path
        tail_path = os.path.splitext(os.path.relpath(img_path, head_path))
        temp_xml_path = os.path.join(head_path, "temp-folder", tail_path[0] + ".xml")
        return os.path.normpath(temp_xml_path)

    def _check_verification_status(self, xml_path):
        """Check if an XML annotation file has been verified.

        Args:
            xml_path: Path to the XML annotation file

        Returns:
            bool: True if verified, False otherwise
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            return root.attrib.get('verified', 'no') == 'yes'
        except:
            return False

    def _check_if_img_needs_converting(self, img_path):
        """Check if an image's annotations need to be converted to JSON.

        Args:
            img_path: Path to the image file

        Returns:
            bool: True if conversion needed, False otherwise
        """
        try:
            # Open XML
            xml_path = self._get_xml_path(img_path)
            root = ET.parse(xml_path).getroot()

            # Check verification status
            verification_status = root.attrib.get('verified', 'no') == 'yes'

            # Check JSON update status
            json_update_status = root.attrib.get('json_updated', 'no') == 'yes'

            # Return whether it needs converting
            return verification_status and not json_update_status
        except:
            return False

    def _create_pascal_voc_annotation(self, image_path, annotation_list, human_verified):
        """Create a Pascal VOC annotation file for an image.

        Args:
            image_path: Path to the image file
            annotation_list: List of annotation strings
            human_verified: Whether the image has been manually verified
        """
        try:
            # Get image dimensions
            img = np.array(Image.open(image_path).convert('RGB'))

            # Create XML structure
            annotation = ET.Element('annotation')

            # Set verified flag
            if human_verified:
                annotation.set('verified', 'yes')

            ET.SubElement(annotation, 'folder').text = str(Path(image_path).parent.name)
            ET.SubElement(annotation, 'filename').text = str(Path(image_path).name)
            ET.SubElement(annotation, 'path').text = str(image_path)

            source = ET.SubElement(annotation, 'source')
            ET.SubElement(source, 'database').text = 'Unknown'

            size = ET.SubElement(annotation, 'size')
            ET.SubElement(size, 'width').text = str(img.shape[1])
            ET.SubElement(size, 'height').text = str(img.shape[0])
            ET.SubElement(size, 'depth').text = str(img.shape[2])

            ET.SubElement(annotation, 'segmented').text = '0'

            # Add each annotation
            for annot in annotation_list:
                tmp_annot = annot.split(',')
                cords, label = tmp_annot[0:-2], tmp_annot[-1]
                xmin, ymin, xmax, ymax = cords[0], cords[1], cords[4], cords[5]  # left, top, right, bottom

                obj = ET.SubElement(annotation, 'object')
                ET.SubElement(obj, 'name').text = label
                ET.SubElement(obj, 'pose').text = 'Unspecified'
                ET.SubElement(obj, 'truncated').text = '0'
                ET.SubElement(obj, 'difficult').text = '0'

                bndbox = ET.SubElement(obj, 'bndbox')
                ET.SubElement(bndbox, 'xmin').text = str(xmin)
                ET.SubElement(bndbox, 'ymin').text = str(ymin)
                ET.SubElement(bndbox, 'xmax').text = str(xmax)
                ET.SubElement(bndbox, 'ymax').text = str(ymax)

            # Format XML with proper indentation
            self._indent_xml(annotation)

            # Save XML file
            tree = ET.ElementTree(annotation)
            xml_file_name = self._get_xml_path(image_path)
            Path(os.path.dirname(xml_file_name)).mkdir(parents=True, exist_ok=True)
            tree.write(xml_file_name)

        except Exception as e:
            print(f"Error creating Pascal VOC annotation for {image_path}: {str(e)}")

    def _indent_xml(self, elem, level=0):
        """Add proper indentation to XML elements for readability.

        Args:
            elem: XML element to indent
            level: Current indentation level
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent_xml(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def _convert_xml_to_coco(self, xml_path, inverted_label_map):
        """Convert XML annotation to COCO format.

        Args:
            xml_path: Path to the XML annotation file
            inverted_label_map: Mapping from label names to category IDs

        Returns:
            tuple: (verified_image, verification_status, new_class, updated_label_map)
        """
        try:
            # Parse XML
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Check verification status
            verification_status = root.attrib.get('verified', 'no') == 'yes'

            # Get image path and dimensions
            path = root.findtext('path')
            size = root.find('size')
            im_width = int(size.findtext('width'))
            im_height = int(size.findtext('height'))

            # Initialize variables
            verified_detections = []
            new_class = False

            # Process each object
            for obj in root.findall('object'):
                name = obj.findtext('name')

                # Check if this is a new class
                if name not in inverted_label_map:
                    new_class = True
                    highest_index = 0
                    for key, value in inverted_label_map.items():
                        value = int(value)
                        if value > highest_index:
                            highest_index = value
                    inverted_label_map[name] = str(highest_index + 1)

                category = inverted_label_map[name]

                # Get bounding box coordinates
                bndbox = obj.find('bndbox')
                xmin = int(float(bndbox.findtext('xmin')))
                ymin = int(float(bndbox.findtext('ymin')))
                xmax = int(float(bndbox.findtext('xmax')))
                ymax = int(float(bndbox.findtext('ymax')))

                # Convert to COCO format
                w_box = round(abs(xmax - xmin) / im_width, 5)
                h_box = round(abs(ymax - ymin) / im_height, 5)
                xo = round(xmin / im_width, 5)
                yo = round(ymin / im_height, 5)
                bbox = [xo, yo, w_box, h_box]

                # Create detection
                verified_detection = {
                    'category': category,
                    'conf': 1.0,
                    'bbox': bbox
                }
                verified_detections.append(verified_detection)

            # Create image data
            verified_image = {
                'file': path,
                'detections': verified_detections
            }

            return verified_image, verification_status, new_class, inverted_label_map

        except Exception as e:
            print(f"Error converting XML to COCO: {str(e)}")
            return None, False, False, inverted_label_map

    def _update_json_from_img_list(self, verified_images, inverted_label_map):
        """Update JSON with verified annotations.

        Args:
            verified_images: List of verified image paths
            inverted_label_map: Mapping from label names to category IDs
        """
        if not verified_images:
            return

        # Open JSON
        with open(self.recognition_file, "r") as json_file:
            data = json.load(json_file)

        # Check if JSON paths are relative
        json_paths_are_relative = check_json_paths(self.recognition_file) == "relative"

        # Update each image in the JSON
        for image in data['images']:
            image_path = image['file']
            if json_paths_are_relative:
                image_path = os.path.normpath(os.path.join(os.path.dirname(self.recognition_file), image_path))

            if image_path in verified_images:
                # Read XML
                xml_path = self._get_xml_path(image_path)
                verified_image, verification_status, new_class, inverted_label_map = self._convert_xml_to_coco(xml_path, inverted_label_map)

                # Update image info
                if verified_image:
                    image['manually_checked'] = verification_status
                    if verification_status:
                        image['detections'] = verified_image['detections']

                    # Update categories if new classes were added
                    if new_class:
                        data['detection_categories'] = {v: k for k, v in inverted_label_map.items()}

                    # Mark XML as updated
                    try:
                        tree = ET.parse(xml_path)
                        root = tree.getroot()
                        root.set('json_updated', 'yes')
                        self._indent_xml(root)
                        tree.write(xml_path)
                    except Exception as e:
                        print(f"Error updating XML {xml_path}: {str(e)}")

        # Write updated JSON
        with open(self.recognition_file, "w") as json_file:
            json.dump(data, json_file, indent=1)

    def _get_hitl_status(self):
        """Get the human-in-the-loop status from JSON.

        Returns:
            str: Status ('never-started', 'in-progress', or 'done')
        """
        try:
            with open(self.recognition_file, "r") as json_file:
                data = json.load(json_file)
                addaxai_metadata = data['info'].get("addaxai_metadata") or data['info'].get("ecoassist_metadata")

                if "hitl_status" in addaxai_metadata:
                    return addaxai_metadata["hitl_status"]
                return "never-started"
        except:
            return "never-started"

    def _set_hitl_status(self, status):
        """Set the human-in-the-loop status in JSON.

        Args:
            status: Status to set ('never-started', 'in-progress', or 'done')
        """
        try:
            with open(self.recognition_file, "r") as json_file:
                data = json.load(json_file)

                # Ensure addaxai_metadata exists
                if 'info' not in data:
                    data['info'] = {}
                if 'addaxai_metadata' not in data['info']:
                    data['info']['addaxai_metadata'] = {}

                data['info']["addaxai_metadata"]["hitl_status"] = status

                with open(self.recognition_file, "w") as outfile:
                    json.dump(data, outfile, indent=1)
        except Exception as e:
            print(f"Error setting HITL status: {str(e)}")

    def _save_annotation_info(self, img_and_detections_dict, label_map):
        """Save annotation information for later use.

        Args:
            img_and_detections_dict: Dictionary mapping image paths to annotations
            label_map: Mapping from category IDs to label names
        """
        annotation_arguments = {
            "recognition_file": self.recognition_file,
            "class_list_txt": self.class_list_txt,
            "file_list_txt": self.file_list_txt,
            "label_map": label_map,
            "img_and_detections_dict": img_and_detections_dict
        }

        annotation_arguments_pkl = os.path.join(self.temp_folder, 'annotation_information.pkl')
        with open(annotation_arguments_pkl, 'wb') as fp:
            pickle.dump(annotation_arguments, fp)

    def _check_images(self):
        """Check for corrupted images in the file list.

        Returns:
            list: List of corrupted image paths
        """
        corrupted_images = []

        if not os.path.isfile(self.file_list_txt):
            return corrupted_images

        with open(self.file_list_txt, 'r') as file:
            image_paths = file.read().splitlines()

            for image_path in image_paths:
                if os.path.exists(image_path):
                    if self._is_image_corrupted(image_path):
                        corrupted_images.append(image_path)

        return corrupted_images

    def _is_image_corrupted(self, image_path):
        """Check if an image is corrupted.

        Args:
            image_path: Path to the image file

        Returns:
            bool: True if corrupted, False otherwise
        """
        try:
            ImageFile.LOAD_TRUNCATED_IMAGES = False
            with Image.open(image_path) as img:
                img.load()
            ImageFile.LOAD_TRUNCATED_IMAGES = True
            return False
        except:
            return True

    def _fix_images(self, image_paths):
        """Try to fix corrupted images.

        Args:
            image_paths: List of corrupted image paths
        """
        for image_path in image_paths:
            if os.path.exists(image_path):
                try:
                    ImageFile.LOAD_TRUNCATED_IMAGES = True
                    with Image.open(image_path) as img:
                        img_copy = img.copy()
                        img_copy.save(image_path, format=img.format, exif=img.info.get('exif'))
                except Exception as e:
                    print(f"Could not fix image {image_path}: {e}")

    def _launch_verification_tool(self):
        """Launch the external annotation tool for verification.

        Returns:
            bool: True if launched successfully, False otherwise
        """
        try:
            # Determine platform-specific command
            labelImg_script = os.path.join(AddaxAI_files, "external", "labelImg", "labelImg.py")
            python_executable = "python"

            if platform.system() == "Windows":
                command = [
                    python_executable,
                    labelImg_script,
                    self.folder_path,
                    self.class_list_txt,
                    self.temp_folder,
                    self.file_list_txt
                ]
            else:  # macOS or Linux
                command = [
                    python_executable,
                    labelImg_script,
                    self.folder_path,
                    self.class_list_txt,
                    self.temp_folder,
                    self.file_list_txt
                ]

            # Launch the annotation tool
            print(f"Launching verification tool with command: {command}")
            subprocess.Popen(command)
            return True

        except Exception as e:
            print(f"Error launching verification tool: {str(e)}")
            return False

def prepare_verification(folder_path, selection_criteria, progress_callback=None):
    """Prepare files for verification based on specified criteria.

    Args:
        folder_path: Path to the folder with detection results
        selection_criteria: Dictionary of selection criteria for each class
        progress_callback: Function to call with progress updates

    Returns:
        dict: Statistics about selected files
    """
    verifier = HumanVerification(folder_path, progress_callback)
    return verifier.prepare_verification(selection_criteria)


def start_verification(folder_path, progress_callback=None):
    """Start or continue the verification process.

    Args:
        folder_path: Path to the folder with detection results
        progress_callback: Function to call with progress updates

    Returns:
        bool: True if verification process was launched successfully
    """
    verifier = HumanVerification(folder_path, progress_callback)
    return verifier.start_verification()


def get_verification_status(folder_path, progress_callback=None):
    """Get the current status of verification.

    Args:
        folder_path: Path to the folder with detection results
        progress_callback: Function to call with progress updates

    Returns:
        dict: Status information including counts
    """
    verifier = HumanVerification(folder_path, progress_callback)
    return verifier.get_verification_status()


def complete_verification(folder_path, progress_callback=None):
    """Complete the verification process by updating the JSON with verified annotations.

    Args:
        folder_path: Path to the folder with detection results
        progress_callback: Function to call with progress updates

    Returns:
        dict: Statistics about verification
    """
    verifier = HumanVerification(folder_path, progress_callback)
    return verifier.complete_verification()


def export_verified_data(folder_path, dst_dir, copy_mode=True, progress_callback=None):
    """Export verified data to a destination directory.

    Args:
        folder_path: Path to the folder with detection results
        dst_dir: Destination directory for exported data
        copy_mode: Whether to copy (True) or move (False) files
        progress_callback: Function to call with progress updates

    Returns:
        int: Number of exported files
    """
    verifier = HumanVerification(folder_path, progress_callback)
    return verifier.export_verified_data(dst_dir, copy_mode)
