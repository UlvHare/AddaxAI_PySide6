# coding=utf-8

# GUI to simplify camera trap image analysis with species recognition models
# https://addaxdatascience.com/addaxai/
# Created by Peter van Lunteren
# Latest edit by Peter van Lunteren on 2 Apr 2025

<<<<<<< HEAD:AddaxAI_GUI_orig.py
=======
# TODO: DEPTH - add depth estimation model: https://pytorch.org/hub/intelisl_midas_v2/
# TODO: CLEAN - if the processing is done, and a image is deleted before the post processing, it crashes and just stops, i think it should just skip the file and then do the rest. I had to manually delete certain entries from the image_recognition_file.json to make it work
# TODO: RESUME DOWNLOAD - make some sort of mechanism that either continues the model download when interrupted, or downloads it to /temp/ folder and only moves it to the correct location after successful download. Otherwise delete from /temp/. That makes sure that users will not be able to continue with half downloaded models.
# TODO: BUG - when moving files during postprocessing and exporting xlsx on Windows, it errors with an "file is in use". There must be something going on with opening files... does not happen when copying files or on Mac.
# TODO: PYINSTALLER - Get rid of the PyInstaller apps. Then there wont be the weird histation when opning. While you're at it, remove version number in the execution files. Then you can use the same shortcuts.
# TODO: WIDGET - make a slider widget for the line width of the bounding box.
# TODO: Microsoft Amazon is not working on MacOS, and Iran is not working on Windows.
# TODO: MERGE JSON - for timelapse it is already merged. Would be great to merge the image and video jsons together for AddaxAI too, and process videos and jsons together. See merge_jsons() function.
# TODO: LAT LON 0 0 - filter out the 0,0 coords for map creation
# TODO: JSON - remove the original json if not running AddaxAI in Timelapse mode. No need to keep that anymore.
# TODO: JSON - remove the part where MD stores its typical threshold values etc in the AddaxAI altered json. It doesn't make sense anymore if the detection caterogies are changed.
# TODO: VIDEO - create video tutorials of all the steps (simple mode, advanced mode, annotation, postprocessing, etc.)
# TODO: EMPTIES - add a checkbox for folder separation where you can skip the empties from being copied
# TODO: LOG SEQUENCE INFO - add sequence information to JSON, CSV, and XSLX
# TODO: SEQ SEP - add feature to separate images into sequence subdirs. Something like "treat sequence as detection" or "Include all images in the sequence" while doing the separation step.
# TODO: INFO - add a messagebox when the deployment is done via advanced mode. Now it just says there were errors. Perhaps just one messagebox with extra text if there are errors or warnings. And some counts.
# TODO: JSON - keep track of confidences for each detection and classification in the JSON. And put that in CSV/XSLX, and visualise it in the images.
# TODO: CSV/XLSX - add frame number and frama rate to the CSV and XLSX files
# TODO: VIS VIDEO - add option to visualise frame with highest confidence
# TODO: N_CORES - add UI "--ncores” option - see email Dan "mambaforge vs. miniforge"
# TODO: REPORTS - add postprocessing reports - see email Dan "mambaforge vs. miniforge"
# TODO: MINOR - By the way, in the AddaxAI UI, I think the frame extraction status popup uses the same wording as the detection popup. They both say something about "frame X of Y". I think for the frame extraction, it should be "video X of Y".
# TODO: JSON - keep track of the original confidence scores whenever it changes (from detection to classification, after human verification, etc.)
# TODO: SMALL FIXES - see list from Saul ('RE: tentative agenda / discussion points') - 12 July 01:11.
# TODO: ANNOTATION - improve annotation experience
    # - make one progress windows in stead of all separate pbars when using large jsons
    # - I've converted pyqt5 to pyside6 for apple silicon so we don't need to install it via homebrew
    #         the unix install clones a pyside6 branch of my human-in-the-loop fork. Test windows on this
    #         on this version too and make it the default
    # - implement image progress status into main labelimg window, so you don't have two separate windows
    # - apparently you still get images in which a class is found under the annotation threshold,
    #         it should count only the images that have classes above the set annotation threshold,
    #         at this point it only checks whether it should draw an bbox or not, but still shows the image
    # - Add custom shortcuts. See email Grant ('Possible software feature').
    # - Add option to order chronological See email Grant ('A few questions I've come up with').
    # - If you press the '?' button in the selection window, it doesn't scroll all the way down anymore. So
    #         adjust the scroll region, of make an option to close the help text
    # - shift forcus on first label. See email Grant ('Another small request').
    # - get rid of the default label pane in the top right. Or at least make it less prominent.
    # - remove the X cross to remove the box label pane. No need to have an option to remove it. It's difficult to get it back on macOS.
    # - see if you can add the conf of the bbox in the box label pane too. just for clarification purposes for threshold settings (see email Grant "Showing confidence level")
    # - there should be a setting that shows box labels inside the image. turn this on by default.
    # - remove the messagebox that warns you that you're not completely done with the human verification before postprocess. just do it.
    # - why do I ask if the user is done after verification anyway? why not just take the results as they are and accept it?
    # - take the annotation confidence ranges the same as the image confidence ranges if the user specified them. Otherwise use 0.6-1.0.
    # - When I zoom in, I always zoom in on the center, and then I can’t manage to move the image.
    # - I figured out when the label becomes greyed out. For me, it happens when I draw a bounding box myself, and then when I go to the next image, "edit label" is greyed out. If I then close the annotation (but not the entire app) and continue, it works again.

>>>>>>> upstream/main:AddaxAI_GUI.py
#import packages like a very pointy half christmas tree
import os
import re
import io
import sys
import cv2
import csv
import json
import math
import time
import glob
import random
import signal
import shutil
import pickle
import folium
import hashlib
import argparse
import calendar
import platform
import requests
import tempfile
import datetime
import traceback
import subprocess
import webbrowser
import numpy as np
import PIL.ExifTags
import pandas as pd
import tkinter as tk
import customtkinter
import seaborn as sns
from tqdm import tqdm
from tkinter import *
from pathlib import Path
import plotly.express as px
from subprocess import Popen
from functools import partial
from tkinter.font import Font
from GPSPhoto import gpsphoto
from CTkTable import CTkTable
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from collections import defaultdict
import xml.etree.cElementTree as ET
from PIL import ImageTk, Image, ImageFile
from RangeSlider.RangeSlider import RangeSliderH
from tkinter import filedialog, ttk, messagebox as mb
from folium.plugins import HeatMap, Draw, MarkerCluster
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# check if the script is ran from the macOS installer executable
# if so, don't actually execute the script - it is meant just for installation purposes
if len(sys.argv) > 1:
    if sys.argv[1] == "installer":
        exit()

# set global variables
AddaxAI_files = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
ImageFile.LOAD_TRUNCATED_IMAGES = True
CLS_DIR = os.path.join(AddaxAI_files, "models", "cls")
DET_DIR = os.path.join(AddaxAI_files, "models", "det")

# set environment variables
if os.name == 'nt': # windows
    env_dir_fpath = os.path.join(AddaxAI_files, "envs")
elif platform.system() == 'Darwin': # macos
    env_dir_fpath = os.path.join(AddaxAI_files, "envs")
else: # linux
    env_dir_fpath = os.path.join(AddaxAI_files, "envs")

# set versions
with open(os.path.join(AddaxAI_files, 'AddaxAI', 'version.txt'), 'r') as file:
    current_AA_version = file.read().strip()
corresponding_model_info_version = "5"

# colors
# most of the colors are set in the ./themes/addaxai.json file
green_primary = '#0B6065'
green_secondary = '#073d40'
yellow_primary = '#fdfae7'
yellow_secondary = '#F0EEDC'
yellow_tertiary = '#E4E1D0'

# images
PIL_sidebar = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "side-bar.png"))
PIL_logo_incl_text = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "square_logo_incl_text.png"))
PIL_checkmark = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "checkmark.png"))
PIL_dir_image = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "image-gallery.png"))
PIL_mdl_image = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "tech.png"))
PIL_spp_image = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "paw.png"))
PIL_run_image = PIL.Image.open(os.path.join(AddaxAI_files, "AddaxAI", "imgs", "shuttle.png"))
launch_count_file = os.path.join(AddaxAI_files, 'launch_count.json')

# insert dependencies to system variables
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

# import modules from forked repositories
from visualise_detection.bounding_box import bounding_box as bb
from cameratraps.megadetector.detection.video_utils import frame_results_to_video_results, FrameToVideoOptions, VIDEO_EXTENSIONS
from cameratraps.megadetector.utils.path_utils import IMG_EXTENSIONS

# log pythonpath
print(sys.path)

# set DPI awareness on Windows
scale_factor = 1.0
if platform.system() == "Windows":
    import ctypes
    try:
        # attempt
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    except AttributeError:
        # fallback for older versions of Windows
        ctypes.windll.user32.SetProcessDPIAware()

# load previous settings
def load_global_vars():
    var_file = os.path.join(AddaxAI_files, "AddaxAI", "global_vars.json")
    with open(var_file, 'r') as file:
        variables = json.load(file)
    return variables
global_vars = load_global_vars()

# language settings
languages_available = ['English', 'Español']
lang_idx = global_vars["lang_idx"]
step_txt = ['Step', 'Paso']
browse_txt = ['Browse', 'Examinar']
cancel_txt = ["Cancel", "Cancelar"]
change_folder_txt = ['Change folder', '¿Cambiar carpeta']
view_results_txt = ['View results', 'Ver resultados']
custom_model_txt = ['Custom model', "Otro modelo"]
again_txt = ['Again?', '¿Otra vez?']
eg_txt = ['E.g.', 'Ejem.']
show_txt = ["Show", "Mostrar"]
new_project_txt = ["<new project>", "<nuevo proyecto>"]
warning_txt = ["Warning", "Advertencia"]
information_txt = ["Information", "Información"]
error_txt = ["Error", "Error"]
select_txt = ["Select", "Seleccionar"]
invalid_value_txt = ["Invalid value", "Valor no válido"]
none_txt = ["None", "Ninguno"]
of_txt = ["of", "de"]
suffixes_for_sim_none = [" - just show me where the animals are",
                         " - muéstrame dónde están los animales"]


#############################################
############# BACKEND FUNCTIONS #############
#############################################

# post-process files
def postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, exp, plt, exp_format, data_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # update progress window
    progress_window.update_values(process = f"{data_type}_pst", status = "load")

    # plt needs csv files so make sure to produce them, even if the user didn't specify
    # if the user didn't specify to export to csv, make sure to remove them later on
    remove_csv = False
    if plt and not exp:
        # except if the csv are already created ofcourse
        if not (os.path.isfile(os.path.join(dst_dir, "results_detections.csv")) and
                os.path.isfile(os.path.join(dst_dir, "results_files.csv"))):
            exp = True
            exp_format = dpd_options_exp_format[lang_idx][1] # CSV
            remove_csv = True

    # get correct json file
    if data_type == "img":
        recognition_file = os.path.join(src_dir, "image_recognition_file.json")
    else:
        recognition_file = os.path.join(src_dir, "video_recognition_file.json")

    # check if user is not in the middle of an annotation session
    if data_type == "img" and get_hitl_var_in_json(recognition_file) == "in-progress":
        if not mb.askyesno("Verification session in progress", f"Your verification session is not yet done. You can finish the session "
                                                               f"by clicking 'Continue' at '{lbl_hitl_main_txt[lang_idx]}', or just continue to post-process "
                                                               "with the results as they are now.\n\nDo you want to continue to post-process?"):
            return

    # init vars
    global cancel_var
    start_time = time.time()
    nloop = 1

    # warn user
    if data_type == "vid":
        if vis or crp or plt:
            check_json_presence_and_warn_user(["visualize, crop, or plot", "visualizar, recortar o trazar"][lang_idx],
                                              ["visualizing, cropping, or plotting", "visualizando, recortando o trazando"][lang_idx],
                                              ["visualization, cropping, and plotting", "visualización, recorte y trazado"][lang_idx])
            vis, crp, plt = [False] * 3

    # fetch label map
    label_map = fetch_label_map_from_json(recognition_file)
    inverted_label_map = {v: k for k, v in label_map.items()}

    # create list with colours for visualisation
    if vis:
        colors = ["fuchsia", "blue", "orange", "yellow", "green", "red", "aqua", "navy", "teal", "olive", "lime", "maroon", "purple"]
        colors = colors * 30

    # make sure json has relative paths
    json_paths_converted = False
    if check_json_paths(recognition_file) != "relative":
        make_json_relative(recognition_file)
        json_paths_converted = True

    # set cancel bool
    cancel_var = False

    # open json file
    with open(recognition_file) as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
    n_images = len(data['images'])

    # initialise the csv files
    # csv files are always created, no matter what the user specified as export format
    # these csv files are then converted to the desired format and deleted, if required
    if exp:
        # for files
        csv_for_files = os.path.join(dst_dir, "results_files.csv")
        if not os.path.isfile(csv_for_files):
            df = pd.DataFrame(list(), columns=["absolute_path", "relative_path", "data_type", "n_detections", "file_height", "file_width", "max_confidence", "human_verified",
                                               'DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make',
                                               'Model', 'Flash', 'ExifOffset', 'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution',
                                               'ExifVersion', 'ComponentsConfiguration', 'FlashPixVersion', 'ColorSpace', 'ExifImageWidth',
                                               'ISOSpeedRatings', 'ExifImageHeight', 'ExposureMode', 'WhiteBalance', 'SceneCaptureType',
                                               'ExposureTime', 'Software', 'Sharpness', 'Saturation', 'ReferenceBlackWhite'])
            df.to_csv(csv_for_files, encoding='utf-8', index=False)

        # for detections
        csv_for_detections = os.path.join(dst_dir, "results_detections.csv")
        if not os.path.isfile(csv_for_detections):
            df = pd.DataFrame(list(), columns=["absolute_path", "relative_path", "data_type", "label", "confidence", "human_verified", "bbox_left",
                                               "bbox_top", "bbox_right", "bbox_bottom", "file_height", "file_width", 'DateTimeOriginal', 'DateTime',
                                               'DateTimeDigitized', 'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make', 'Model', 'Flash', 'ExifOffset',
                                               'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution', 'ExifVersion', 'ComponentsConfiguration',
                                               'FlashPixVersion', 'ColorSpace', 'ExifImageWidth', 'ISOSpeedRatings', 'ExifImageHeight', 'ExposureMode',
                                               'WhiteBalance', 'SceneCaptureType', 'ExposureTime', 'Software', 'Sharpness', 'Saturation', 'ReferenceBlackWhite'])
            df.to_csv(csv_for_detections, encoding='utf-8', index=False)

    # set global vars
    global postprocessing_error_log
    postprocessing_error_log = os.path.join(dst_dir, "postprocessing_error_log.txt")

    # count the number of rows to make sure it doesn't exceed the limit for an excel sheet
    if exp and exp_format == dpd_options_exp_format[lang_idx][0]: # if exp_format is the first option in the dropdown menu -> XLSX
        n_rows_files = 1
        n_rows_detections = 1
        for image in data['images']:
            n_rows_files += 1
            if 'detections' in image:
                for detection in image['detections']:
                    if detection["conf"] >= thresh:
                        n_rows_detections += 1
        if n_rows_detections > 1048576 or n_rows_files > 1048576:
            mb.showerror(["To many rows", "Demasiadas filas"][lang_idx],
                         ["The XLSX file you are trying to create is too large!\n\nThe maximum number of rows in an XSLX file is "
                          f"1048576, while you are trying to create a sheet with {max(n_rows_files, n_rows_detections)} rows.\n\nIf"
                          " you require the results in XLSX format, please run the process on smaller chunks so that it doesn't "
                          f"exceed Microsoft's row limit. Or choose CSV as {lbl_exp_format_txt[lang_idx]} in advanced mode.",
                          "¡El archivo XLSX que está intentando crear es demasiado grande!\n\nEl número máximo de filas en un archivo"
                          f" XSLX es 1048576, mientras que usted está intentando crear una hoja con {max(n_rows_files, n_rows_detections)}"
                          " filas.\n\nSi necesita los resultados en formato XLSX, ejecute el proceso en trozos más pequeños para que no "
                          f"supere el límite de filas de Microsoft. O elija CSV como {lbl_exp_format_txt[lang_idx]} en modo avanzado."][lang_idx])
            return

    # loop through images
    for image in data['images']:

        # cancel process if required
        if cancel_var:
            break

        # check for failure
        if "failure" in image:

            # write warnings to log file
            with open(postprocessing_error_log, 'a+') as f:
                f.write(f"File '{image['file']}' was skipped by post processing features because '{image['failure']}'\n")
            f.close()

            # calculate stats
            elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
            time_left_sep = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
            progress_window.update_values(process = f"{data_type}_pst",
                                            status = "running",
                                            cur_it = nloop,
                                            tot_it = n_images,
                                            time_ela = elapsed_time_sep,
                                            time_rem = time_left_sep,
                                            cancel_func = cancel)

            nloop += 1
            root.update()

            # skip this iteration
            continue

        # get image info
        file = image['file']
        detections_list = image['detections']
        n_detections = len(detections_list)

        # check if it has been manually verified
        manually_checked = False
        if 'manually_checked' in image:
            if image['manually_checked']:
                manually_checked = True

        # init vars
        max_detection_conf = 0.0
        unique_labels = []
        bbox_info = []

        # open files
        if vis or crp or exp:
            if data_type == "img":
                im_to_vis = cv2.imread(os.path.normpath(os.path.join(src_dir, file)))

                # check if that image was able to be loaded
                if im_to_vis is None:
                    with open(postprocessing_error_log, 'a+') as f:
                        f.write(f"File '{image['file']}' was skipped by post processing features. This might be due to the file being moved or deleted after analysis, or because of a special character in the file path.\n")
                    f.close()
                    elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
                    time_left_sep = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
                    progress_window.update_values(process = f"{data_type}_pst",
                                                    status = "running",
                                                    cur_it = nloop,
                                                    tot_it = n_images,
                                                    time_ela = elapsed_time_sep,
                                                    time_rem = time_left_sep,
                                                    cancel_func = cancel)
                    nloop += 1
                    root.update()
                    continue

                im_to_crop_path = os.path.join(src_dir, file)

                # load old image and extract EXIF
                origImage = Image.open(os.path.join(src_dir, file))
                try:
                    exif = origImage.info['exif']
                except:
                    exif = None

                origImage.close()
            else:
                vid = cv2.VideoCapture(os.path.join(src_dir, file))

            # read image dates etc
            if exp:

                # try to read metadata
                try:
                    img_for_exif = PIL.Image.open(os.path.join(src_dir, file))
                    metadata = {
                        PIL.ExifTags.TAGS[k]: v
                        for k, v in img_for_exif._getexif().items()
                        if k in PIL.ExifTags.TAGS
                    }
                    img_for_exif.close()
                except:
                    metadata = {'GPSInfo': None,
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
                                 'ExifImageHeight': None}

                # try to add GPS data
                try:
                    gpsinfo = gpsphoto.getGPSData(os.path.join(src_dir, file))
                    if 'Latitude' in gpsinfo and 'Longitude' in gpsinfo:
                        gpsinfo['GPSLink'] = f"https://maps.google.com/?q={gpsinfo['Latitude']},{gpsinfo['Longitude']}"
                except:
                    gpsinfo = {'Latitude': None,
                               'Longitude': None,
                               'GPSLink': None}

                # combine metadata and gps data
                exif_data = {**metadata, **gpsinfo}

                # check if datetime values can be found
                exif_params = []
                for param in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized', 'Latitude', 'Longitude', 'GPSLink', 'Altitude', 'Make', 'Model',
                              'Flash', 'ExifOffset', 'ResolutionUnit', 'YCbCrPositioning', 'XResolution', 'YResolution', 'ExifVersion',
                              'ComponentsConfiguration', 'FlashPixVersion', 'ColorSpace', 'ExifImageWidth', 'ISOSpeedRatings',
                              'ExifImageHeight', 'ExposureMode', 'WhiteBalance', 'SceneCaptureType', 'ExposureTime', 'Software',
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

        # loop through detections
        if 'detections' in image:
            for detection in image['detections']:

                # get confidence
                conf = detection["conf"]

                # write max conf
                if manually_checked:
                    max_detection_conf = "NA"
                elif conf > max_detection_conf:
                    max_detection_conf = conf

                # if above user specified thresh
                if conf >= thresh:

                    # change conf to string for verified images
                    if manually_checked:
                        conf = "NA"

                    # get detection info
                    category = detection["category"]
                    label = label_map[category]
                    if sep:
                        unique_labels.append(label)
                        unique_labels = sorted(list(set(unique_labels)))

                    # get bbox info
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

                        # store in list
                        bbox_info.append([label, conf, manually_checked, left, top, right, bottom, height, width, xo, yo, w_box, h_box])

        # collect info to append to csv files
        if exp:

            # read shape again - this is a temporary solution
            # read in the height and width of the images and videos, as this was giving a bunch of bugs...
            if data_type == "img":
                img = cv2.imread(os.path.normpath(os.path.join(src_dir, file)))
                height, width = img.shape[:2]
            else:
                cap = cv2.VideoCapture(os.path.join(src_dir, file))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                cap.release()

            # file info CSV
            row = pd.DataFrame([[src_dir, file, data_type, len(bbox_info), height, width, max_detection_conf, manually_checked, *exif_params]])
            row.to_csv(csv_for_files, encoding='utf-8', mode='a', index=False, header=False)

            # detections info CSV
            rows = []
            for bbox in bbox_info:
                row = [src_dir, file, data_type, *bbox[:9], *exif_params]
                rows.append(row)
            rows = pd.DataFrame(rows)
            rows.to_csv(csv_for_detections, encoding='utf-8', mode='a', index=False, header=False)

        # separate files
        if sep:
            if n_detections == 0:
                file = move_files(file, "empty", file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
            else:
                if len(unique_labels) > 1:
                    labels_str = "_".join(unique_labels)
                    file = move_files(file, labels_str, file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
                elif len(unique_labels) == 0:
                    file = move_files(file, "empty", file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)
                else:
                    file = move_files(file, label, file_placement, max_detection_conf, sep_conf, dst_dir, src_dir, manually_checked)

        # visualize images
        if vis and len(bbox_info) > 0:

            # blur people
            if var_vis_blur.get():
                for bbox in bbox_info:
                    if bbox[0] == "person":
                        im_to_vis = blur_box(im_to_vis, *bbox[3:7], bbox[8], bbox[7])

            # draw bounding boxes
            if var_vis_bbox.get():
                for bbox in bbox_info:
                    if manually_checked:
                        vis_label = f"{bbox[0]} (verified)"
                    else:
                        conf_label = round(bbox[1], 2) if round(bbox[1], 2) != 1.0 else 0.99
                        vis_label = f"{bbox[0]} {conf_label}"
                    color = colors[int(inverted_label_map[bbox[0]])]
                    bb.add(im_to_vis, *bbox[3:7], vis_label, color, size = dpd_options_vis_size[lang_idx].index(var_vis_size.get())) # convert string to index, e.g. "small" -> 0

            im = os.path.join(dst_dir, file)
            Path(os.path.dirname(im)).mkdir(parents=True, exist_ok=True)
            cv2.imwrite(im, im_to_vis)

            # load new image and save exif
            if (exif != None):
                image_new = Image.open(im)
                image_new.save(im, exif=exif)
                image_new.close()

        # crop images
        if crp and len(bbox_info) > 0:
            counter = 1
            for bbox in bbox_info:

                # if files have been moved
                if sep:
                    im_to_crp = Image.open(os.path.join(dst_dir,file))
                else:
                    im_to_crp = Image.open(im_to_crop_path)
                crp_im = im_to_crp.crop((bbox[3:7]))
                im_to_crp.close()
                filename, file_extension = os.path.splitext(file)
                im_path = os.path.join(dst_dir, filename + '_crop' + str(counter) + '_' + bbox[0] + file_extension)
                Path(os.path.dirname(im_path)).mkdir(parents=True, exist_ok=True)
                crp_im.save(im_path)
                counter += 1

                 # load new image and save exif
                if (exif != None):
                    image_new = Image.open(im_path)
                    image_new.save(im_path, exif=exif)
                    image_new.close()

        # calculate stats
        elapsed_time_sep = str(datetime.timedelta(seconds=round(time.time() - start_time)))
        time_left_sep = str(datetime.timedelta(seconds=round(((time.time() - start_time) * n_images / nloop) - (time.time() - start_time))))
        progress_window.update_values(process = f"{data_type}_pst",
                                        status = "running",
                                        cur_it = nloop,
                                        tot_it = n_images,
                                        time_ela = elapsed_time_sep,
                                        time_rem = time_left_sep,
                                        cancel_func = cancel)

        nloop += 1
        root.update()

    # create summary csv
    if exp:
        csv_for_summary = os.path.join(dst_dir, "results_summary.csv")
        if os.path.exists(csv_for_summary):
            os.remove(csv_for_summary)
        det_info = pd.DataFrame(pd.read_csv(csv_for_detections, dtype=dtypes, low_memory=False))
        summary = pd.DataFrame(det_info.groupby(['label', 'data_type']).size().sort_values(ascending=False).reset_index(name='n_detections'))
        summary.to_csv(csv_for_summary, encoding='utf-8', mode='w', index=False, header=True)

    # convert csv to xlsx if required
    if exp and exp_format == dpd_options_exp_format[lang_idx][0]: # if exp_format is the first option in the dropdown menu -> XLSX
        xlsx_path = os.path.join(dst_dir, "results.xlsx")

        # check if the excel file exists, e.g. when processing both img and vid
        dfs = []
        for result_type in ['detections', 'files', 'summary']:
            csv_path = os.path.join(dst_dir, f"results_{result_type}.csv")
            if os.path.isfile(xlsx_path):

                #  if so, add new rows to existing ones
                df_xlsx = pd.read_excel(xlsx_path, sheet_name=result_type)
                df_csv = pd.read_csv(os.path.join(dst_dir, f"results_{result_type}.csv"), dtype=dtypes, low_memory=False)
                df = pd.concat([df_xlsx, df_csv], ignore_index=True)
            else:
                df = pd.read_csv(os.path.join(dst_dir, f"results_{result_type}.csv"), dtype=dtypes, low_memory=False)
            dfs.append(df)

            # plt needs the csv's, so don't remove just yet
            if not plt:
                if os.path.isfile(csv_path):
                    os.remove(csv_path)

        # overwrite rows to xlsx file
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            for idx, result_type in enumerate(['detections', 'files', 'summary']):
                df = dfs[idx]
                if result_type in ['detections', 'files']:
                    df['DateTimeOriginal'] = pd.to_datetime(df['DateTimeOriginal'], format='%d/%m/%y %H:%M:%S')
                    df['DateTime'] = pd.to_datetime(df['DateTime'], format='%d/%m/%y %H:%M:%S')
                    df['DateTimeDigitized'] = pd.to_datetime(df['DateTimeDigitized'], format='%d/%m/%y %H:%M:%S')
                df.to_excel(writer, sheet_name=result_type, index=None, header=True)

    # convert csv to tsv if required
    if exp and exp_format == dpd_options_exp_format[lang_idx][3]: # if exp_format is the third option in the dropdown menu -> TSV

        # Check if the TSV file exists, e.g., when processing both img and vid
        csv_path = os.path.join(dst_dir, f"results_detections.csv")
        tsv_path = os.path.join(dst_dir, f"results_sensing_clues.tsv")

        if os.path.isfile(tsv_path):  # Append if TSV exists
            with open(csv_path, 'r', newline='') as csv_file, open(tsv_path, 'a', newline='') as tsv_file:
                csv_reader = csv.reader(x.replace('\0', '') for x in csv_file)
                tsv_writer = csv.writer(tsv_file, delimiter='\t')

                csv_header = next(csv_reader)
                idx_date, idx_lat, idx_lon = map(csv_header.index, ["DateTimeOriginal", "Latitude", "Longitude"])

                for row in csv_reader:
                    unique_id = generate_unique_id(row)
                    formatted_date = format_datetime(row[idx_date])
                    new_row = [unique_id, formatted_date, row[idx_lat], row[idx_lon], "AddaxAI"] + row
                    tsv_writer.writerow(new_row)

        else:  # Create new TSV file
            with open(csv_path, 'r', newline='') as csv_file, open(tsv_path, 'w', newline='') as tsv_file:
                csv_reader = csv.reader(x.replace('\0', '') for x in csv_file)
                tsv_writer = csv.writer(tsv_file, delimiter='\t')

                csv_header = next(csv_reader)
                idx_date, idx_lat, idx_lon = map(csv_header.index, ["DateTimeOriginal", "Latitude", "Longitude"])

                tsv_writer.writerow(["ID", "Date", "Lat", "Long", "Method"] + csv_header)

                for row in csv_reader:
                    unique_id = generate_unique_id(row)
                    formatted_date = format_datetime(row[idx_date])
                    new_row = [unique_id, formatted_date, row[idx_lat], row[idx_lon], "AddaxAI"] + row
                    tsv_writer.writerow(new_row)

        # plt needs the CSVs, so don't remove just yet
        if not plt:
            for result_type in ['detections', 'files', 'summary']:
                csv_path = os.path.join(dst_dir, f"results_{result_type}.csv")
                if os.path.isfile(csv_path):
                    os.remove(csv_path)

    # convert csv to coco format if required
    if exp and exp_format == dpd_options_exp_format[lang_idx][2]: # COCO

        # init vars
        coco_path = os.path.join(dst_dir, f"results_coco_{data_type}.json")
        detections_df = pd.read_csv(os.path.join(dst_dir, f"results_detections.csv"), dtype=dtypes, low_memory=False)
        files_df = pd.read_csv(os.path.join(dst_dir, f"results_files.csv"), dtype=dtypes, low_memory=False)

        # convert csv to coco format
        csv_to_coco(
            detections_df=detections_df,
            files_df=files_df,
            output_path=coco_path
        )

        # only plt needs the csv's, so if the user didn't specify plt, remove csvs
        if not plt:
            for result_type in ['detections', 'files', 'summary']:
                csv_path = os.path.join(dst_dir, f"results_{result_type}.csv")
                if os.path.isfile(csv_path):
                    os.remove(csv_path)

    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_absolute(recognition_file)

    # let the user know it's done
    progress_window.update_values(process = f"{data_type}_pst", status = "done")
    root.update()

    # create graphs
    if plt:
        produce_plots(dst_dir)

        # if user wants XLSX (0), COCO (2), or TSV (3) as output, or if user didn't specify exp all-
        # together but the files were created for plt -> remove CSV files
        if (exp and exp_format == dpd_options_exp_format[lang_idx][0]) or \
            (exp and exp_format == dpd_options_exp_format[lang_idx][2]) or \
            (exp and exp_format == dpd_options_exp_format[lang_idx][3]) or \
            remove_csv:
            for result_type in ['detections', 'files', 'summary']:
                csv_path = os.path.join(dst_dir, f"results_{result_type}.csv")
                if os.path.isfile(csv_path):
                    os.remove(csv_path)

def clean_line(line):
    return line.replace('\0', '')

def generate_unique_id(row):
    """Generate a unique hash for a row based on its contents."""
    row_str = "".join(row).encode('utf-8')
    return hashlib.md5(row_str).hexdigest()

def format_datetime(date_str):
    """Convert 'DD/MM/YY HH:MM:SS' to 'YYYY-MM-DDTHH:MM:SS', handle 'NA' gracefully."""
    try:
        dt = datetime.datetime.strptime(date_str, "%d/%m/%y %H:%M:%S")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return 'NA'

# convert csv to coco format
def csv_to_coco(detections_df, files_df, output_path):

    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}\n")

    # init coco structure
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
            "description": f"Object detection results exported from AddaxAI (v{str(current_AA_version)}).",
            "url": "https://addaxdatascience.com/addaxai/",
            "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    # prepare categories and category mapping
    category_mapping = {}
    current_category_id = 1

    # assign categories from detections
    for label in detections_df['label'].unique():
        if label not in category_mapping:
            category_mapping[label] = current_category_id
            coco['categories'].append({
                "id": current_category_id,
                "name": label
                })
            current_category_id += 1

    # process each image and its detections
    annotation_id = 1
    for _, file_info in files_df.iterrows():

        # create image entry
        image_id = len(coco['images']) + 1

        # get date captured
        if type(file_info['DateTimeOriginal']) == float: # means NA value
            date_captured = "NA"
        else:
            date_captured = datetime.datetime.strptime(file_info['DateTimeOriginal'],
                                                        "%d/%m/%y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")

        # add image to coco
        image_entry = {
            "id": image_id,
            "width": int(file_info['file_width']),
            "height": int(file_info['file_height']),
            "file_name": file_info['relative_path'],
            "license": 1,
            "date_captured": date_captured
        }
        coco['images'].append(image_entry)

        # add annotations for this image
        image_detections = detections_df[detections_df['relative_path'] == file_info['relative_path']]
        for _, detection in image_detections.iterrows():
            bbox_left = int(detection['bbox_left'])
            bbox_top = int(detection['bbox_top'])
            bbox_right = int(detection['bbox_right'])
            bbox_bottom = int(detection['bbox_bottom'])

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

    # save when done
    with open(output_path, 'w') as output_file:
        json.dump(coco, output_file, indent=4)

# set data types for csv import so that the machine doesn't run out of memory with large files (>0.5M rows)
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

# create dict with country codes for speciesnet
countries = [
    "ABW    \tAruba",
    "AFG    \tAfghanistan",
    "AGO    \tAngola",
    "AIA    \tAnguilla",
    "ALA    \t\u00c5land Islands",
    "ALB    \tAlbania",
    "AND    \tAndorra",
    "ARE    \tUnited Arab Emirates",
    "ARG    \tArgentina",
    "ARM    \tArmenia",
    "ASM    \tAmerican Samoa",
    "ATA    \tAntarctica",
    "ATF    \tFrench Southern Territories",
    "ATG    \tAntigua and Barbuda",
    "AUS    \tAustralia",
    "AUT    \tAustria",
    "AZE    \tAzerbaijan",
    "BDI    \tBurundi",
    "BEL    \tBelgium",
    "BEN    \tBenin",
    "BES    \tBonaire, Sint Eustatius and Saba",
    "BFA    \tBurkina Faso",
    "BGD    \tBangladesh",
    "BGR    \tBulgaria",
    "BHR    \tBahrain",
    "BHS    \tBahamas",
    "BIH    \tBosnia and Herzegovina",
    "BLM    \tSaint Barth\u00e9lemy",
    "BLR    \tBelarus",
    "BLZ    \tBelize",
    "BMU    \tBermuda",
    "BOL    \tBolivia, Plurinational State of",
    "BRA    \tBrazil",
    "BRB    \tBarbados",
    "BRN    \tBrunei Darussalam",
    "BTN    \tBhutan",
    "BVT    \tBouvet Island",
    "BWA    \tBotswana",
    "CAF    \tCentral African Republic",
    "CAN    \tCanada",
    "CCK    \tCocos (Keeling) Islands",
    "CHE    \tSwitzerland",
    "CHL    \tChile",
    "CHN    \tChina",
    "CIV    \tC\u00f4te d'Ivoire",
    "CMR    \tCameroon",
    "COD    \tCongo, Democratic Republic of the",
    "COG    \tCongo",
    "COK    \tCook Islands",
    "COL    \tColombia",
    "COM    \tComoros",
    "CPV    \tCabo Verde",
    "CRI    \tCosta Rica",
    "CUB    \tCuba",
    "CUW    \tCura\u00e7ao",
    "CXR    \tChristmas Island",
    "CYM    \tCayman Islands",
    "CYP    \tCyprus",
    "CZE    \tCzechia",
    "DEU    \tGermany",
    "DJI    \tDjibouti",
    "DMA    \tDominica",
    "DNK    \tDenmark",
    "DOM    \tDominican Republic",
    "DZA    \tAlgeria",
    "ECU    \tEcuador",
    "EGY    \tEgypt",
    "ERI    \tEritrea",
    "ESH    \tWestern Sahara",
    "ESP    \tSpain",
    "EST    \tEstonia",
    "ETH    \tEthiopia",
    "FIN    \tFinland",
    "FJI    \tFiji",
    "FLK    \tFalkland Islands (Malvinas)",
    "FRA    \tFrance",
    "FRO    \tFaroe Islands",
    "FSM    \tMicronesia, Federated States of",
    "GAB    \tGabon",
    "GBR    \tUnited Kingdom of Great Britain and Northern Ireland",
    "GEO    \tGeorgia",
    "GGY    \tGuernsey",
    "GHA    \tGhana",
    "GIB    \tGibraltar",
    "GIN    \tGuinea",
    "GLP    \tGuadeloupe",
    "GMB    \tGambia",
    "GNB    \tGuinea-Bissau",
    "GNQ    \tEquatorial Guinea",
    "GRC    \tGreece",
    "GRD    \tGrenada",
    "GRL    \tGreenland",
    "GTM    \tGuatemala",
    "GUF    \tFrench Guiana",
    "GUM    \tGuam",
    "GUY    \tGuyana",
    "HKG    \tHong Kong",
    "HMD    \tHeard Island and McDonald Islands",
    "HND    \tHonduras",
    "HRV    \tCroatia",
    "HTI    \tHaiti",
    "HUN    \tHungary",
    "IDN    \tIndonesia",
    "IMN    \tIsle of Man",
    "IND    \tIndia",
    "IOT    \tBritish Indian Ocean Territory",
    "IRL    \tIreland",
    "IRN    \tIran, Islamic Republic of",
    "IRQ    \tIraq",
    "ISL    \tIceland",
    "ISR    \tIsrael",
    "ITA    \tItaly",
    "JAM    \tJamaica",
    "JEY    \tJersey",
    "JOR    \tJordan",
    "JPN    \tJapan",
    "KAZ    \tKazakhstan",
    "KEN    \tKenya",
    "KGZ    \tKyrgyzstan",
    "KHM    \tCambodia",
    "KIR    \tKiribati",
    "KNA    \tSaint Kitts and Nevis",
    "KOR    \tKorea, Republic of",
    "KWT    \tKuwait",
    "LAO    \tLao People's Democratic Republic",
    "LBN    \tLebanon",
    "LBR    \tLiberia",
    "LBY    \tLibya",
    "LCA    \tSaint Lucia",
    "LIE    \tLiechtenstein",
    "LKA    \tSri Lanka",
    "LSO    \tLesotho",
    "LTU    \tLithuania",
    "LUX    \tLuxembourg",
    "LVA    \tLatvia",
    "MAC    \tMacao",
    "MAF    \tSaint Martin (French part)",
    "MAR    \tMorocco",
    "MCO    \tMonaco",
    "MDA    \tMoldova, Republic of",
    "MDG    \tMadagascar",
    "MDV    \tMaldives",
    "MEX    \tMexico",
    "MHL    \tMarshall Islands",
    "MKD    \tNorth Macedonia",
    "MLI    \tMali",
    "MLT    \tMalta",
    "MMR    \tMyanmar",
    "MNE    \tMontenegro",
    "MNG    \tMongolia",
    "MNP    \tNorthern Mariana Islands",
    "MOZ    \tMozambique",
    "MRT    \tMauritania",
    "MSR    \tMontserrat",
    "MTQ    \tMartinique",
    "MUS    \tMauritius",
    "MWI    \tMalawi",
    "MYS    \tMalaysia",
    "MYT    \tMayotte",
    "NAM    \tNamibia",
    "NCL    \tNew Caledonia",
    "NER    \tNiger",
    "NFK    \tNorfolk Island",
    "NGA    \tNigeria",
    "NIC    \tNicaragua",
    "NIU    \tNiue",
    "NLD    \tNetherlands, Kingdom of the",
    "NOR    \tNorway",
    "NPL    \tNepal",
    "NRU    \tNauru",
    "NZL    \tNew Zealand",
    "OMN    \tOman",
    "PAK    \tPakistan",
    "PAN    \tPanama",
    "PCN    \tPitcairn",
    "PER    \tPeru",
    "PHL    \tPhilippines",
    "PLW    \tPalau",
    "PNG    \tPapua New Guinea",
    "POL    \tPoland",
    "PRI    \tPuerto Rico",
    "PRK    \tKorea, Democratic People's Republic of",
    "PRT    \tPortugal",
    "PRY    \tParaguay",
    "PSE    \tPalestine, State of",
    "PYF    \tFrench Polynesia",
    "QAT    \tQatar",
    "REU    \tR\u00e9union",
    "ROU    \tRomania",
    "RUS    \tRussian Federation",
    "RWA    \tRwanda",
    "SAU    \tSaudi Arabia",
    "SDN    \tSudan",
    "SEN    \tSenegal",
    "SGP    \tSingapore",
    "SGS    \tSouth Georgia and the South Sandwich Islands",
    "SHN    \tSaint Helena, Ascension and Tristan da Cunha",
    "SJM    \tSvalbard and Jan Mayen",
    "SLB    \tSolomon Islands",
    "SLE    \tSierra Leone",
    "SLV    \tEl Salvador",
    "SMR    \tSan Marino",
    "SOM    \tSomalia",
    "SPM    \tSaint Pierre and Miquelon",
    "SRB    \tSerbia",
    "SSD    \tSouth Sudan",
    "STP    \tSao Tome and Principe",
    "SUR    \tSuriname",
    "SVK    \tSlovakia",
    "SVN    \tSlovenia",
    "SWE    \tSweden",
    "SWZ    \tEswatini",
    "SXM    \tSint Maarten (Dutch part)",
    "SYC    \tSeychelles",
    "SYR    \tSyrian Arab Republic",
    "TCA    \tTurks and Caicos Islands",
    "TCD    \tChad",
    "TGO    \tTogo",
    "THA    \tThailand",
    "TJK    \tTajikistan",
    "TKL    \tTokelau",
    "TKM    \tTurkmenistan",
    "TLS    \tTimor-Leste",
    "TON    \tTonga",
    "TTO    \tTrinidad and Tobago",
    "TUN    \tTunisia",
    "TUR    \tT\u00fcrkiye",
    "TUV    \tTuvalu",
    "TWN    \tTaiwan, Province of China",
    "TZA    \tTanzania, United Republic of",
    "UGA    \tUganda",
    "UKR    \tUkraine",
    "UMI    \tUnited States Minor Outlying Islands",
    "URY    \tUruguay",
    "USA-AL    \tUnited States of America - Alabama",
    "USA-AK    \tUnited States of America - Alaska",
    "USA-AZ    \tUnited States of America - Arizona",
    "USA-AR    \tUnited States of America - Arkansas",
    "USA-CA    \tUnited States of America - California",
    "USA-CO    \tUnited States of America - Colorado",
    "USA-CT    \tUnited States of America - Connecticut",
    "USA-DE    \tUnited States of America - Delaware",
    "USA-FL    \tUnited States of America - Florida",
    "USA-GA    \tUnited States of America - Georgia",
    "USA-HI    \tUnited States of America - Hawaii",
    "USA-ID    \tUnited States of America - Idaho",
    "USA-IL    \tUnited States of America - Illinois",
    "USA-IN    \tUnited States of America - Indiana",
    "USA-IA    \tUnited States of America - Iowa",
    "USA-KS    \tUnited States of America - Kansas",
    "USA-KY    \tUnited States of America - Kentucky",
    "USA-LA    \tUnited States of America - Louisiana",
    "USA-ME    \tUnited States of America - Maine",
    "USA-MD    \tUnited States of America - Maryland",
    "USA-MA    \tUnited States of America - Massachusetts",
    "USA-MI    \tUnited States of America - Michigan",
    "USA-MN    \tUnited States of America - Minnesota",
    "USA-MS    \tUnited States of America - Mississippi",
    "USA-MO    \tUnited States of America - Missouri",
    "USA-MT    \tUnited States of America - Montana",
    "USA-NE    \tUnited States of America - Nebraska",
    "USA-NV    \tUnited States of America - Nevada",
    "USA-NH    \tUnited States of America - New Hampshire",
    "USA-NJ    \tUnited States of America - New Jersey",
    "USA-NM    \tUnited States of America - New Mexico",
    "USA-NY    \tUnited States of America - New York",
    "USA-NC    \tUnited States of America - North Carolina",
    "USA-ND    \tUnited States of America - North Dakota",
    "USA-OH    \tUnited States of America - Ohio",
    "USA-OK    \tUnited States of America - Oklahoma",
    "USA-OR    \tUnited States of America - Oregon",
    "USA-PA    \tUnited States of America - Pennsylvania",
    "USA-RI    \tUnited States of America - Rhode Island",
    "USA-SC    \tUnited States of America - South Carolina",
    "USA-SD    \tUnited States of America - South Dakota",
    "USA-TN    \tUnited States of America - Tennessee",
    "USA-TX    \tUnited States of America - Texas",
    "USA-UT    \tUnited States of America - Utah",
    "USA-VT    \tUnited States of America - Vermont",
    "USA-VA    \tUnited States of America - Virginia",
    "USA-WA    \tUnited States of America - Washington",
    "USA-WV    \tUnited States of America - West Virginia",
    "USA-WI    \tUnited States of America - Wisconsin",
    "USA-WY    \tUnited States of America - Wyoming",
    "UZB    \tUzbekistan",
    "VAT    \tHoly See",
    "VCT    \tSaint Vincent and the Grenadines",
    "VEN    \tVenezuela, Bolivarian Republic of",
    "VGB    \tVirgin Islands (British)",
    "VIR    \tVirgin Islands (U.S.)",
    "VNM    \tViet Nam",
    "VUT    \tVanuatu",
    "WLF    \tWallis and Futuna",
    "WSM    \tSamoa",
    "YEM    \tYemen",
    "ZAF    \tSouth Africa",
    "ZMB    \tZambia",
    "ZWE    \tZimbabwe"
]
# for simplicity, the same list is used for both english as spanish I'll fix everything properly in the new version
dpd_options_sppnet_location = [countries, countries]

# open progress window and initiate the post-process progress window
def start_postprocess():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # save settings for next time
    write_global_vars({
        "lang_idx": lang_idx,
        "var_separate_files": var_separate_files.get(),
        "var_file_placement": var_file_placement.get(),
        "var_sep_conf": var_sep_conf.get(),
        "var_vis_files": var_vis_files.get(),
        "var_crp_files": var_crp_files.get(),
        "var_exp": var_exp.get(),
        "var_exp_format_idx": dpd_options_exp_format[lang_idx].index(var_exp_format.get()),
        "var_vis_size_idx": dpd_options_vis_size[lang_idx].index(var_vis_size.get()),
        "var_vis_bbox": var_vis_bbox.get(),
        "var_vis_blur": var_vis_blur.get(),
        "var_plt": var_plt.get(),
        "var_thresh": var_thresh.get()
    })

    # fix user input
    src_dir = var_choose_folder.get()
    dst_dir = var_output_dir.get()
    thresh = var_thresh.get()
    sep = var_separate_files.get()
    file_placement = var_file_placement.get()
    sep_conf = var_sep_conf.get()
    vis = var_vis_files.get()
    crp = var_crp_files.get()
    exp = var_exp.get()
    plt = var_plt.get()
    exp_format = var_exp_format.get()

    # init cancel variable
    global cancel_var
    cancel_var = False

    # check which json files are present
    img_json = False
    if os.path.isfile(os.path.join(src_dir, "image_recognition_file.json")):
        img_json = True
    vid_json = False
    if os.path.isfile(os.path.join(src_dir, "video_recognition_file.json")):
        vid_json = True
    if not img_json and not vid_json:
        mb.showerror(error_txt[lang_idx], ["No model output file present. Make sure you run step 2 before post-processing the files.",
                                       "No hay archivo de salida del modelo. Asegúrese de ejecutar el paso 2 antes de postprocesar"
                                       " los archivos."][lang_idx])
        return

    # check if destination dir is valid and set to input dir if not
    if dst_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(dst_dir):
        mb.showerror(["Destination folder not set", "Carpeta de destino no establecida."][lang_idx],
                        ["Destination folder not set.\n\n You have not specified where the post-processing results should be placed or the set "
                        "folder does not exist. This is required.",
                        "Carpeta de destino no establecida. No ha especificado dónde deben colocarse los resultados del postprocesamiento o la "
                        "carpeta establecida no existe. Esto opción es obligatoria."][lang_idx])
        return

    # warn user if the original files will be overwritten with visualized files
    if os.path.normpath(dst_dir) == os.path.normpath(src_dir) and vis and not sep:
        if not mb.askyesno(["Original images will be overwritten", "Las imágenes originales se sobrescribirán."][lang_idx],
                      [f"WARNING! The visualized images will be placed in the folder with the original data: '{src_dir}'. By doing this, you will overwrite the original images"
                      " with the visualized ones. Visualizing is permanent and cannot be undone. Are you sure you want to continue?",
                      f"ATENCIÓN. Las imágenes visualizadas se colocarán en la carpeta con los datos originales: '{src_dir}'. Al hacer esto, se sobrescribirán las imágenes "
                      "originales con las visualizadas. La visualización es permanente y no se puede deshacer. ¿Está seguro de que desea continuar?"][lang_idx]):
            return

    # warn user if images will be moved and visualized
    if sep and file_placement == 1 and vis:
        if not mb.askyesno(["Original images will be overwritten", "Las imágenes originales se sobrescribirán."][lang_idx],
                      [f"WARNING! You specified to visualize the original images. Visualizing is permanent and cannot be undone. If you don't want to visualize the original "
                      f"images, please select 'Copy' as '{lbl_file_placement_txt}'. Are you sure you want to continue with the current settings?",
                      "ATENCIÓN. Ha especificado visualizar las imágenes originales. La visualización es permanente y no puede deshacerse. Si no desea visualizar las "
                      f"imágenes originales, seleccione 'Copiar' como '{lbl_file_placement_txt}'. ¿Está seguro de que desea continuar con la configuración actual?"][lang_idx]):
            return

    # initialise progress window with processes
    processes = []
    if img_json:
        processes.append("img_pst")
    if plt:
        processes.append("plt")
    if vid_json:
        processes.append("vid_pst")
    global progress_window
    progress_window = ProgressWindow(processes = processes)
    progress_window.open()

    try:
        # postprocess images
        if img_json:
            postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, exp, plt, exp_format, data_type = "img")

        # postprocess videos
        if vid_json and not cancel_var:
            postprocess(src_dir, dst_dir, thresh, sep, file_placement, sep_conf, vis, crp, exp, plt, exp_format, data_type = "vid")

        # complete
        complete_frame(fth_step)

        # check if there are postprocessing errors written
        if os.path.isfile(postprocessing_error_log):
            mb.showwarning(warning_txt[lang_idx], [f"One or more files failed to be analysed by the model (e.g., corrupt files) and will be skipped by "
                                                f"post-processing features. See\n\n'{postprocessing_error_log}'\n\nfor more info.",
                                                f"Uno o más archivos no han podido ser analizados por el modelo (por ejemplo, ficheros corruptos) y serán "
                                                f"omitidos por las funciones de post-procesamiento. Para más información, véase\n\n'{postprocessing_error_log}'"][lang_idx])

        # close progress window
        progress_window.close()

    except Exception as error:
        # log error
        print("ERROR:\n" + str(error) + "\n\nDETAILS:\n" + str(traceback.format_exc()) + "\n\n")

        # show error
        mb.showerror(title=error_txt[lang_idx],
                     message=["An error has occurred", "Ha ocurrido un error"][lang_idx] + " (AddaxAI v" + current_AA_version + "): '" + str(error) + "'.",
                     detail=traceback.format_exc())

        # close window
        progress_window.close()
