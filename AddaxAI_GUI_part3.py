# update json from list with verified images
def update_json_from_img_list(
    verified_images, inverted_label_map, recognition_file, patience_dialog, current
):
    # check if the json has relative paths
    if check_json_paths(recognition_file) == "relative":
        json_paths_are_relative = True
    else:
        json_paths_are_relative = False

    # open
    with open(recognition_file, "r") as image_recognition_file_content:
        data = json.load(image_recognition_file_content)

    # adjust
    for image in data["images"]:
        image_path = image["file"]
        if json_paths_are_relative:
            image_path = os.path.normpath(
                os.path.join(os.path.dirname(recognition_file), image_path)
            )
        if image_path in verified_images:
            # update progress
            patience_dialog.update_progress(current=current, percentage=True)
            current += 1

            # read
            xml = return_xml_path(image_path)
            coco, verification_status, new_class, inverted_label_map = (
                convert_xml_to_coco(xml, inverted_label_map)
            )
            image["manually_checked"] = verification_status
            if new_class:
                data["detection_categories"] = {
                    v: k for k, v in inverted_label_map.items()
                }
            if verification_status:
                image["detections"] = coco["detections"]

                # adjust xml file
                tree = ET.parse(xml)
                root = tree.getroot()
                root.set("json_updated", "yes")
                indent(root)
                tree.write(xml)
    image_recognition_file_content.close()

    # write
    print(recognition_file)
    with open(recognition_file, "w") as json_file:
        json.dump(data, json_file, indent=1)
    image_recognition_file_content.close()


# write model specific variables to file
def write_model_vars(model_type="cls", new_values=None):
    # exit is no cls is selected
    if var_cls_model.get() in none_txt:
        return

    # adjust
    variables = load_model_vars(model_type)
    if new_values is not None:
        for key, value in new_values.items():
            if key in variables:
                variables[key] = value
            else:
                print(
                    f"Warning: Variable {key} not found in the loaded model variables."
                )

    # write
    model_dir = var_cls_model.get() if model_type == "cls" else var_det_model.get()
    var_file = os.path.join(
        AddaxAI_files, "models", model_type, model_dir, "variables.json"
    )
    with open(var_file, "w") as file:
        json.dump(variables, file, indent=4)


# take MD json and classify detections
def classify_detections(json_fpath, data_type, simple_mode=False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # show user it's loading
    progress_window.update_values(process=f"{data_type}_cls", status="load")
    root.update()

    # load model specific variables
    model_vars = load_model_vars()
    cls_model_fname = model_vars["model_fname"]
    cls_model_type = model_vars["type"]
    cls_model_fpath = os.path.join(
        AddaxAI_files, "models", "cls", var_cls_model.get(), cls_model_fname
    )

    # if present take os-specific env else take general env
    if os.name == "nt":  # windows
        cls_model_env = model_vars.get("env-windows", model_vars["env"])
    elif platform.system() == "Darwin":  # macos
        cls_model_env = model_vars.get("env-macos", model_vars["env"])
    else:  # linux
        cls_model_env = model_vars.get("env-linux", model_vars["env"])

    # get param values
    if simple_mode:
        cls_disable_GPU = False
        cls_detec_thresh = model_vars["var_cls_detec_thresh_default"]
        cls_class_thresh = model_vars["var_cls_class_thresh_default"]
        cls_animal_smooth = False
    else:
        cls_disable_GPU = var_disable_GPU.get()
        cls_detec_thresh = var_cls_detec_thresh.get()
        cls_class_thresh = var_cls_class_thresh.get()
        cls_animal_smooth = var_smooth_cls_animal.get()

    # init paths
    python_executable = get_python_interprator(cls_model_env)
    inference_script = os.path.join(
        AddaxAI_files,
        "AddaxAI",
        "classification_utils",
        "model_types",
        cls_model_type,
        "classify_detections.py",
    )

    # create command
    command_args = []
    command_args.append(python_executable)
    command_args.append(inference_script)
    command_args.append(AddaxAI_files)
    command_args.append(cls_model_fpath)
    command_args.append(str(cls_detec_thresh))
    command_args.append(str(cls_class_thresh))
    command_args.append(str(cls_animal_smooth))
    command_args.append(json_fpath)
    try:
        command_args.append(temp_frame_folder)
    except NameError:
        command_args.append("None")
        pass

    # adjust command for unix OS
    if os.name != "nt":
        command_args = "'" + "' '".join(command_args) + "'"

    # prepend with os-specific commands
    if os.name == "nt":  # windows
        if cls_disable_GPU:
            command_args = ['set CUDA_VISIBLE_DEVICES="" &'] + command_args
    elif platform.system() == "Darwin":  # macos
        command_args = "export PYTORCH_ENABLE_MPS_FALLBACK=1 && " + command_args
    else:  # linux
        if cls_disable_GPU:
            command_args = "CUDA_VISIBLE_DEVICES='' " + command_args
        else:
            command_args = "export PYTORCH_ENABLE_MPS_FALLBACK=1 && " + command_args

    # log command
    print(command_args)

    # prepare process and cancel method per OS
    if os.name == "nt":
        # run windows command
        p = Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            shell=True,
            universal_newlines=True,
        )

    else:
        # run unix command
        p = Popen(
            command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            shell=True,
            universal_newlines=True,
            preexec_fn=os.setsid,
        )

    # set global vars
    global subprocess_output
    subprocess_output = ""

    # calculate metrics while running
    status_setting = "running"
    for line in p.stdout:
        # save output if something goes wrong
        subprocess_output = subprocess_output + line
        subprocess_output = subprocess_output[-1000:]

        # log
        print(line, end="")

        # catch early exit if there are no detections that meet the requirmentents to classify
        if line.startswith("n_crops_to_classify is zero. Nothing to classify."):
            mb.showinfo(
                information_txt[lang_idx],
                [
                    "There are no animal detections that meet the criteria. You either "
                    "have selected images without any animals present, or you have set "
                    "your detection confidence threshold to high.",
                    "No hay detecciones"
                    " de animales que cumplan los criterios. O bien ha seleccionado "
                    "imágenes sin presencia de animales, o bien ha establecido el umbral"
                    " de confianza de detección en alto.",
                ][lang_idx],
            )
            elapsed_time = ("00:00",)
            time_left = ("00:00",)
            current_im = ("0",)
            total_im = ("0",)
            processing_speed = ("0it/s",)
            percentage = ("100",)
            GPU_param = ("Unknown",)
            data_type = (data_type,)
            break

        # catch smoothening info lines
        if "<EA>" in line:
            smooth_output_line = (
                re.search("<EA>(.+)<EA>", line).group().replace("<EA>", "")
            )
            smooth_output_file = os.path.join(
                os.path.dirname(json_fpath), "smooth-output.txt"
            )
            with open(smooth_output_file, "a+") as f:
                f.write(f"{smooth_output_line}\n")
            f.close()

        # if smoothing, the pbar should change description
        if "<EA-status-change>" in line:
            status_setting = (
                re.search("<EA-status-change>(.+)<EA-status-change>", line)
                .group()
                .replace("<EA-status-change>", "")
            )

        # get process stats and send them to tkinter
        if line.startswith("GPU available: False"):
            GPU_param = "CPU"
        elif line.startswith("GPU available: True"):
            GPU_param = "GPU"
        elif "%" in line[0:4]:
            # read stats
            times = re.search("(\[.*?\])", line)[1]
            progress_bar = re.search("^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
            percentage = re.search("\d*%", progress_bar)[0][:-1]
            current_im = re.search("\d*\/", progress_bar)[0][:-1]
            total_im = re.search("\/\d*", progress_bar)[0][1:]
            elapsed_time = re.search("(?<=\[)(.*)(?=<)", times)[1]
            time_left = re.search("(?<=<)(.*)(?=,)", times)[1]
            processing_speed = re.search("(?<=,)(.*)(?=])", times)[1].strip()

            # print stats
            progress_window.update_values(
                process=f"{data_type}_cls",
                status=status_setting,
                cur_it=int(current_im),
                tot_it=int(total_im),
                time_ela=elapsed_time,
                time_rem=time_left,
                speed=processing_speed,
                hware=GPU_param,
                cancel_func=lambda: cancel_subprocess(p),
            )
        root.update()

    # process is done
    progress_window.update_values(
        process=f"{data_type}_cls",
        status="done",
        time_ela=elapsed_time,
        speed=processing_speed,
    )

    root.update()


# quit popen process
def cancel_subprocess(process):
    global cancel_deploy_model_pressed
    global btn_start_deploy
    global sim_run_btn
    if os.name == "nt":
        Popen(f"TASKKILL /F /PID {process.pid} /T")
    else:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    btn_start_deploy.configure(state=NORMAL)
    sim_run_btn.configure(state=NORMAL)
    cancel_deploy_model_pressed = True
    progress_window.close()


# deploy model and create json output files
warn_smooth_vid = True


def deploy_model(path_to_image_folder, selected_options, data_type, simple_mode=False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # note if user is video analysing without smoothing
    global warn_smooth_vid
    if (
        (var_cls_model.get() not in none_txt)
        and (var_smooth_cls_animal.get() == False)
        and data_type == "vid"
        and simple_mode == False
        and warn_smooth_vid == True
    ):
        warn_smooth_vid = False
        if not mb.askyesno(
            information_txt[lang_idx],
            [
                "You are about to analyze videos without smoothing the confidence scores. "
                "Typically, a video may contain many frames of the same animal, increasing the likelihood that at least "
                f"one of the labels could be a false prediction. With '{lbl_smooth_cls_animal_txt[lang_idx]}' enabled, all"
                " predictions from a single video will be averaged, resulting in only one label per video. Do you wish to"
                " continue without smoothing?\n\nPress 'No' to go back.",
                "Estás a punto de analizar videos sin suavizado "
                "habilitado. Normalmente, un video puede contener muchos cuadros del mismo animal, lo que aumenta la "
                "probabilidad de que al menos una de las etiquetas pueda ser una predicción falsa. Con "
                f"'{lbl_smooth_cls_animal_txt[lang_idx]}' habilitado, todas las predicciones de un solo video se promediarán,"
                " lo que resultará en una sola etiqueta por video. ¿Deseas continuar sin suavizado habilitado?\n\nPresiona "
                "'No' para regresar.",
            ][lang_idx],
        ):
            return

    # display loading window
    # try to update progress window, if AttributeError, it means it tries to update the img_det and we're working with a full image classifier
    try:
        progress_window.update_values(process=f"{data_type}_det", status="load")
    except AttributeError:
        pass

    # prepare variables
    chosen_folder = str(Path(path_to_image_folder))
    run_detector_batch_py = os.path.join(
        AddaxAI_files,
        "cameratraps",
        "megadetector",
        "detection",
        "run_detector_batch.py",
    )
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    process_video_py = os.path.join(
        AddaxAI_files, "cameratraps", "megadetector", "detection", "process_video.py"
    )
    video_recognition_file = "--output_json_file=" + os.path.join(
        chosen_folder, "video_recognition_file.json"
    )
    GPU_param = "Unknown"
    python_executable = get_python_interprator("base")

    # select model based on user input via dropdown menu, or take MDv5a for simple mode
    custom_model_bool = False
    if simple_mode:
        det_model_fpath = os.path.join(DET_DIR, "MegaDetector 5a", "md_v5a.0.0.pt")
        switch_yolov5_version("old models")
    elif (
        var_det_model.get() != dpd_options_model[lang_idx][-1]
    ):  # if not chosen the last option, which is "custom model"
        det_model_fname = load_model_vars("det")["model_fname"]
        det_model_fpath = os.path.join(DET_DIR, var_det_model.get(), det_model_fname)
        switch_yolov5_version("old models")
    else:
        # set model file
        det_model_fpath = var_det_model_path.get()
        custom_model_bool = True

        # set yolov5 git to accommodate new models (checkout depending on how you retrain MD)
        switch_yolov5_version("new models")

        # extract classes
        label_map = extract_label_map_from_model(det_model_fpath)

        # write labelmap to separate json
        json_object = json.dumps(label_map, indent=1)
        native_model_classes_json_file = os.path.join(
            chosen_folder, "native_model_classes.json"
        )
        with open(native_model_classes_json_file, "w") as outfile:
            outfile.write(json_object)

        # add argument to command call
        selected_options.append(
            "--class_mapping_filename=" + native_model_classes_json_file
        )

    # set global cancel bool
    global cancel_deploy_model_pressed
    cancel_deploy_model_pressed = False

    # if a full image classifier is selected, imitate object detection to get full bboxes
    full_image_cls = load_model_vars("cls").get("full_image_cls", False)
    if full_image_cls:
        imitate_object_detection_for_full_image_classifier(chosen_folder)

    # for crop classifiers we need to run the detection first
    else:
        # create commands for Windows
        if os.name == "nt":
            if selected_options == []:
                img_command = [
                    python_executable,
                    run_detector_batch_py,
                    det_model_fpath,
                    "--threshold=0.01",
                    chosen_folder,
                    image_recognition_file,
                ]
                vid_command = [
                    python_executable,
                    process_video_py,
                    "--max_width=1280",
                    "--verbose",
                    "--quality=85",
                    video_recognition_file,
                    det_model_fpath,
                    chosen_folder,
                ]
            else:
                img_command = [
                    python_executable,
                    run_detector_batch_py,
                    det_model_fpath,
                    *selected_options,
                    "--threshold=0.01",
                    chosen_folder,
                    image_recognition_file,
                ]
                vid_command = [
                    python_executable,
                    process_video_py,
                    *selected_options,
                    "--max_width=1280",
                    "--verbose",
                    "--quality=85",
                    video_recognition_file,
                    det_model_fpath,
                    chosen_folder,
                ]

        # create command for MacOS and Linux
        else:
            if selected_options == []:
                img_command = [
                    f"'{python_executable}' '{run_detector_batch_py}' '{det_model_fpath}' '--threshold=0.01' '{chosen_folder}' '{image_recognition_file}'"
                ]
                vid_command = [
                    f"'{python_executable}' '{process_video_py}' '--max_width=1280' '--verbose' '--quality=85' '{video_recognition_file}' '{det_model_fpath}' '{chosen_folder}'"
                ]
            else:
                selected_options = "' '".join(selected_options)
                img_command = [
                    f"'{python_executable}' '{run_detector_batch_py}' '{det_model_fpath}' '{selected_options}' '--threshold=0.01' '{chosen_folder}' '{image_recognition_file}'"
                ]
                vid_command = [
                    f"'{python_executable}' '{process_video_py}' '{selected_options}' '--max_width=1280' '--verbose' '--quality=85' '{video_recognition_file}' '{det_model_fpath}' '{chosen_folder}'"
                ]

        # pick one command
        if data_type == "img":
            command = img_command
        else:
            command = vid_command

        # if user specified to disable GPU, prepend and set system variable
        if var_disable_GPU.get() and not simple_mode:
            if os.name == "nt":  # windows
                command[:0] = ["set", 'CUDA_VISIBLE_DEVICES=""', "&"]
            elif platform.system() == "Darwin":  # macos
                mb.showwarning(
                    warning_txt[lang_idx],
                    [
                        "Disabling GPU processing is currently only supported for CUDA devices on Linux and Windows "
                        "machines, not on macOS. Proceeding without GPU disabled.",
                        "Deshabilitar el procesamiento de "
                        "la GPU actualmente sólo es compatible con dispositivos CUDA en máquinas Linux y Windows, no en"
                        " macOS. Proceder sin GPU desactivada.",
                    ][lang_idx],
                )
                var_disable_GPU.set(False)
            else:  # linux
                command = "CUDA_VISIBLE_DEVICES='' " + command

        # log
        print(f"command:\n\n{command}\n\n")

        # prepare process and cancel method per OS
        if os.name == "nt":
            # run windows command
            p = Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True,
            )

        else:
            # run unix command
            p = Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True,
                preexec_fn=os.setsid,
            )

        # set global vars
        global subprocess_output
        subprocess_output = ""
        previous_processed_img = [
            "There is no previously processed image. The problematic character is in the first image to analyse.",
            "No hay ninguna imagen previamente procesada. El personaje problemático está en la primera imagen a analizar.",
        ][lang_idx]
        extracting_frames_mode = False

        # check if the unit shown should be frame or video
        if data_type == "vid" and var_cls_model.get() in none_txt:
            frame_video_choice = "video"
        elif data_type == "vid" and var_cls_model.get() not in none_txt:
            frame_video_choice = "frame"
        else:
            frame_video_choice = None

        # read output
        for line in p.stdout:
            # save output if something goes wrong
            subprocess_output = subprocess_output + line
            subprocess_output = subprocess_output[-1000:]

            # log
            print(line, end="")

            # catch model errors
            if line.startswith("No image files found"):
                mb.showerror(
                    ["No images found", "No se han encontrado imágenes"][lang_idx],
                    [
                        f"There are no images found in '{chosen_folder}'. \n\nAre you sure you specified the correct folder?"
                        f" If the files are in subdirectories, make sure you don't tick '{lbl_exclude_subs_txt[lang_idx]}'.",
                        f"No se han encontrado imágenes en '{chosen_folder}'. \n\n¿Está seguro de haber especificado la carpeta correcta?",
                    ][lang_idx],
                )
                return
            if line.startswith("No videos found"):
                mb.showerror(
                    ["No videos found", "No se han encontrado vídeos"][lang_idx],
                    line
                    + [
                        f"\n\nAre you sure you specified the correct folder? If the files are in subdirectories, make sure you don't tick '{lbl_exclude_subs_txt[lang_idx]}'.",
                        "\n\n¿Está seguro de haber especificado la carpeta correcta?",
                    ][lang_idx],
                )
                return
            if line.startswith("No frames extracted"):
                mb.showerror(
                    ["Could not extract frames", "No se pueden extraer fotogramas"][
                        lang_idx
                    ],
                    line
                    + [
                        "\n\nConverting the videos to .mp4 might fix the issue.",
                        "\n\nConvertir los vídeos a .mp4 podría solucionar el problema.",
                    ][lang_idx],
                )
                return
            if line.startswith("UnicodeEncodeError:"):
                mb.showerror(
                    "Unparsable special character",
                    [
                        f"{line}\n\nThere seems to be a special character in a filename that cannot be parsed. Unfortunately, it's not"
                        " possible to point you to the problematic file directly, but I can tell you that the last successfully analysed"
                        f" image was\n\n{previous_processed_img}\n\nThe problematic character should be in the file or folder name of "
                        "the next image, alphabetically. Please remove any special characters from the path and try again.",
                        f"{line}\n\nParece que hay un carácter especial en un nombre de archivo que no se puede analizar. Lamentablemente,"
                        " no es posible indicarle directamente el archivo problemático, pero puedo decirle que la última imagen analizada "
                        f"con éxito fue\n\n{previous_processed_img}\n\nEl carácter problemático debe estar en el nombre del archivo o "
                        "carpeta de la siguiente imagen, alfabéticamente. Elimine los caracteres especiales de la ruta e inténtelo de "
                        "nuevo.",
                    ][lang_idx],
                )
                return
            if line.startswith("Processing image "):
                previous_processed_img = line.replace("Processing image ", "")

            # write errors to log file
            if "Exception:" in line:
                with open(model_error_log, "a+") as f:
                    f.write(f"{line}\n")
                f.close()

            # write warnings to log file
            if "Warning:" in line:
                if (
                    not "could not determine MegaDetector version" in line
                    and not "no metadata for unknown detector version" in line
                    and not "using user-supplied image size" in line
                    and not "already exists and will be overwritten" in line
                ):
                    with open(model_warning_log, "a+") as f:
                        f.write(f"{line}\n")
                    f.close()

            # print frame extraction progress and dont continue until done
            if "Extracting frames for folder " in line and data_type == "vid":
                progress_window.update_values(
                    process=f"{data_type}_det", status="extracting frames"
                )
                extracting_frames_mode = True
            if extracting_frames_mode:
                if "%" in line[0:4]:
                    progress_window.update_values(
                        process=f"{data_type}_det",
                        status="extracting frames",
                        extracting_frames_txt=[
                            f"Extracting frames... {line[:3]}%",
                            f"Extrayendo fotogramas... {line[:3]}%",
                        ],
                    )
            if "Extracted frames for" in line and data_type == "vid":
                extracting_frames_mode = False
            if extracting_frames_mode:
                continue

            # get process stats and send them to tkinter
            if line.startswith("GPU available: False"):
                GPU_param = "CPU"
            elif line.startswith("GPU available: True"):
                GPU_param = "GPU"
            elif "%" in line[0:4]:
                # read stats
                times = re.search("(\[.*?\])", line)[1]
                progress_bar = re.search("^[^\/]*[^[^ ]*", line.replace(times, ""))[0]
                percentage = re.search("\d*%", progress_bar)[0][:-1]
                current_im = re.search("\d*\/", progress_bar)[0][:-1]
                total_im = re.search("\/\d*", progress_bar)[0][1:]
                elapsed_time = re.search("(?<=\[)(.*)(?=<)", times)[1]
                time_left = re.search("(?<=<)(.*)(?=,)", times)[1]
                processing_speed = re.search("(?<=,)(.*)(?=])", times)[1].strip()

                # show progress
                progress_window.update_values(
                    process=f"{data_type}_det",
                    status="running",
                    cur_it=int(current_im),
                    tot_it=int(total_im),
                    time_ela=elapsed_time,
                    time_rem=time_left,
                    speed=processing_speed,
                    hware=GPU_param,
                    cancel_func=lambda: cancel_subprocess(p),
                    frame_video_choice=frame_video_choice,
                )
            root.update()

        # process is done
        progress_window.update_values(process=f"{data_type}_det", status="done")
        root.update()

    # create addaxai metadata
    addaxai_metadata = {
        "addaxai_metadata": {
            "version": current_AA_version,
            "custom_model": custom_model_bool,
            "custom_model_info": {},
        }
    }
    if custom_model_bool:
        addaxai_metadata["addaxai_metadata"]["custom_model_info"] = {
            "model_name": os.path.basename(os.path.normpath(det_model_fpath)),
            "label_map": label_map,
        }

    # write metadata to json and make absolute if specified
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.json")
    if data_type == "img" and os.path.isfile(image_recognition_file):
        append_to_json(image_recognition_file, addaxai_metadata)
        if var_abs_paths.get():
            make_json_absolute(image_recognition_file)
    if data_type == "vid" and os.path.isfile(video_recognition_file):
        append_to_json(video_recognition_file, addaxai_metadata)
        if var_abs_paths.get():
            make_json_absolute(video_recognition_file)

    # classify detections if specified by user
    if not cancel_deploy_model_pressed:
        if var_cls_model.get() not in none_txt:
            if data_type == "img":
                classify_detections(
                    os.path.join(chosen_folder, "image_recognition_file.json"),
                    data_type,
                    simple_mode=simple_mode,
                )
            else:
                classify_detections(
                    os.path.join(chosen_folder, "video_recognition_file.json"),
                    data_type,
                    simple_mode=simple_mode,
                )


# merge image and video jsons together
def merge_jsons(image_json, video_json, output_file_path):
    # Load the image recognition JSON file
    if image_json:
        with open(image_json, "r") as image_file:
            image_data = json.load(image_file)

    # Load the video recognition JSON file
    if video_json:
        with open(video_json, "r") as video_file:
            video_data = json.load(video_file)

    # Merge the "images" lists
    if image_json and video_json:
        merged_images = image_data["images"] + video_data["images"]
        detection_categories = image_data["detection_categories"]
        info = image_data["info"]
        classification_categories = (
            image_data["classification_categories"]
            if "classification_categories" in image_data
            else {}
        )
        forbidden_classes = (
            image_data["forbidden_classes"] if "forbidden_classes" in image_data else {}
        )
    elif image_json:
        merged_images = image_data["images"]
        detection_categories = image_data["detection_categories"]
        info = image_data["info"]
        classification_categories = (
            image_data["classification_categories"]
            if "classification_categories" in image_data
            else {}
        )
        forbidden_classes = (
            image_data["forbidden_classes"] if "forbidden_classes" in image_data else {}
        )
    elif video_json:
        merged_images = video_data["images"]
        detection_categories = video_data["detection_categories"]
        info = video_data["info"]
        classification_categories = (
            video_data["classification_categories"]
            if "classification_categories" in video_data
            else {}
        )
        forbidden_classes = (
            video_data["forbidden_classes"] if "forbidden_classes" in video_data else {}
        )

    # Create the merged data
    merged_data = {
        "images": merged_images,
        "detection_categories": detection_categories,
        "info": info,
        "classification_categories": classification_categories,
        "forbidden_classes": forbidden_classes,
    }

    # Save the merged data to a new JSON file
    with open(output_file_path, "w") as output_file:
        json.dump(merged_data, output_file, indent=1)

    print(f"merged json file saved to {output_file_path}")


# pop up window showing the user that an AddaxAI update is required for a particular model
def show_update_info(model_vars, model_name):
    # create window
    su_root = customtkinter.CTkToplevel(root)
    su_root.title("Update required")
    su_root.geometry("+10+10")
    su_root.columnconfigure(0, weight=1, minsize=300)
    su_root.columnconfigure(1, weight=1, minsize=300)
    lbl1 = customtkinter.CTkLabel(
        su_root, text=f"Update required for model {model_name}", font=main_label_font
    )
    lbl1.grid(
        row=0, column=0, padx=PADX, pady=(PADY, PADY / 2), columnspan=2, sticky="nsew"
    )
    lbl2 = customtkinter.CTkLabel(
        su_root,
        text=f"Minimum AddaxAI version required is v{model_vars['min_version']}, while your current version is v{current_AA_version}.",
    )
    lbl2.grid(row=1, column=0, padx=PADX, pady=(0, PADY), columnspan=2, sticky="nsew")

    # define functions
    def close():
        su_root.destroy()

    def read_more():
        webbrowser.open("https://addaxdatascience.com/addaxai/")
        su_root.destroy()

    # buttons frame
    btns_frm = customtkinter.CTkFrame(master=su_root)
    btns_frm.columnconfigure(0, weight=1, minsize=10)
    btns_frm.columnconfigure(1, weight=1, minsize=10)
    btns_frm.grid(
        row=5, column=0, padx=PADX, pady=(0, PADY), columnspan=2, sticky="nswe"
    )
    close_btn = customtkinter.CTkButton(btns_frm, text="Cancel", command=close)
    close_btn.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nswe")
    lmore_btn = customtkinter.CTkButton(btns_frm, text="Update", command=read_more)
    lmore_btn.grid(row=2, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")


# check if a particular model needs downloading
def model_needs_downloading(model_vars, model_type):
    model_name = var_cls_model.get() if model_type == "cls" else var_det_model.get()
    if model_name not in none_txt:
        model_fpath = os.path.join(
            AddaxAI_files,
            "models",
            model_type,
            model_name,
            load_model_vars(model_type)["model_fname"],
        )
        if os.path.isfile(model_fpath):
            # the model file is already present
            return [False, ""]
        else:
            # the model is not present yet
            min_version = model_vars["min_version"]

            # let's check if the model works with the current EA version
            if needs_EA_update(min_version):
                show_update_info(model_vars, model_name)
                return [None, ""]
            else:
                return [True, os.path.dirname(model_fpath)]
    else:
        # user selected none
        return [False, ""]


# check if a particular environment needs downloading
def environment_needs_downloading(model_vars):
    # find out which env is required
    # if present take os-specific env else take general env
    if os.name == "nt":  # windows
        env_name = model_vars.get("env-windows", model_vars.get("env", "base"))
    elif platform.system() == "Darwin":  # macos
        env_name = model_vars.get("env-macos", model_vars.get("env", "base"))
    else:  # linux
        env_name = model_vars.get("env-linux", model_vars.get("env", "base"))

    # check if that env is already present
    if os.path.isdir(os.path.join(AddaxAI_files, "envs", f"env-{env_name}")):
        return [False, env_name]
    else:
        return [True, env_name]


# check if path contains special characters
def contains_special_characters(path):
    allowed_characters = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-./ +\:'()"
    )
    for char in path:
        if char not in allowed_characters:
            return [True, char]
    return [False, ""]


# we run this instead of a detection model for full image classification
def imitate_object_detection_for_full_image_classifier(chosen_folder):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # List all images in the chosen folder
    image_files = [
        f
        for f in os.listdir(chosen_folder)
        if f.lower().endswith(("jpg", "jpeg", "png"))
    ]

    # Initialize the JSON structure
    result = {
        "images": [],
        "detection_categories": {"1": "animal", "2": "person", "3": "vehicle"},
        "info": {
            "detection_completion_time": datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "format_version": "",
            "detector": None,
            "detector_metadata": {},
        },
    }

    # Loop through each image in the folder and add it to the result
    for image_file in image_files:
        # Prepare the image's detections with the full image bounding box
        image_data = {
            "file": image_file,
            "detections": [
                {
                    "category": "1",  # Assuming all detections are animals
                    "conf": 1.0,  # High confidence for full-image detection
                    "bbox": [0.0, 0.0, 1.0, 1.0],  # Full image bounding box
                }
            ],
        }

        # Add image data to the images list
        result["images"].append(image_data)

    # Save the result as a JSON file
    json_filename = os.path.join(chosen_folder, "image_recognition_file.json")
    with open(json_filename, "w") as json_file:
        json.dump(result, json_file, indent=4)

    print(f"JSON file created: {json_filename}")


# open progress window and initiate the model deployment
def start_deploy(simple_mode=False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # check if there are any images or videos in the folder
    chosen_folder = var_choose_folder.get()
    if simple_mode:
        check_img_presence = True
        check_vid_presence = True
    else:
        check_img_presence = var_process_img.get()
        check_vid_presence = var_process_vid.get()
    img_present = False
    vid_present = False
    if var_exclude_subs.get():
        # non recursive
        for f in os.listdir(chosen_folder):
            if check_img_presence:
                if f.lower().endswith(IMG_EXTENSIONS):
                    img_present = True
            if check_vid_presence:
                if f.lower().endswith(VIDEO_EXTENSIONS):
                    vid_present = True
            if (
                (img_present and vid_present)
                or (img_present and not check_vid_presence)
                or (vid_present and not check_img_presence)
                or (not check_img_presence and not check_vid_presence)
            ):
                break
    else:
        # recursive
        for main_dir, _, files in os.walk(chosen_folder):
            for file in files:
                if check_img_presence and file.lower().endswith(IMG_EXTENSIONS):
                    img_present = True
                if check_vid_presence and file.lower().endswith(VIDEO_EXTENSIONS):
                    vid_present = True
            if (
                (img_present and vid_present)
                or (img_present and not check_vid_presence)
                or (vid_present and not check_img_presence)
                or (not check_img_presence and not check_vid_presence)
            ):
                break

    # check if user selected to process either images or videos
    if not img_present and not vid_present:
        if simple_mode:
            mb.showerror(
                ["No data found", "No se han encontrado datos"][lang_idx],
                message=[
                    f"There are no images nor videos found.\n\nAddaxAI accepts images in the format {IMG_EXTENSIONS}."
                    f"\n\nIt accepts videos in the format {VIDEO_EXTENSIONS}.",
                    f"No se han encontrado imágenes ni vídeos.\n\nAddaxAI acepta imágenes en formato {IMG_EXTENSIONS}."
                    f"\n\nAcepta vídeos en formato {VIDEO_EXTENSIONS}.",
                ][lang_idx],
            )
        else:
            mb.showerror(
                ["No data found", "No se han encontrado datos"][lang_idx],
                message=[
                    f"There are no images nor videos found, or you selected not to search for them. If there is indeed data to be "
                    f"processed, make sure the '{lbl_process_img_txt[lang_idx]}' and/or '{lbl_process_vid_txt[lang_idx]}' options "
                    f"are selected. You must select at least one of these.\n\nAddaxAI accepts images in the format {IMG_EXTENSIONS}."
                    f"\n\nIt accepts videos in the format {VIDEO_EXTENSIONS}.",
                    f"No se han encontrado imágenes ni vídeos, o ha seleccionado no buscarlos. Si efectivamente hay datos para procesar,"
                    f" asegúrese de que las opciones '{lbl_process_img_txt[lang_idx]}' y/o '{lbl_process_vid_txt[lang_idx]}' están seleccionadas."
                    f" Debe seleccionar al menos una de ellas.\n\nAddaxAI acepta imágenes en formato {IMG_EXTENSIONS}."
                    f"\n\nAcepta vídeos en formato {VIDEO_EXTENSIONS}.",
                ][lang_idx],
            )
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        return

    # run species net
    if var_cls_model.get() == "Global - SpeciesNet - Google":
        # if simple mode, tell user to use the advanced mode
        if simple_mode:
            mb.showerror(
                ["SpeciesNet not available", "SpeciesNet no disponible"][lang_idx],
                message=[
                    f"SpeciesNet is not available in simple mode. Please switch to advanced mode to use SpeciesNet.",
                    f"SpeciesNet no está disponible en modo simple. Cambie al modo avanzado para usar SpeciesNet.",
                ][lang_idx],
            )

            # reset
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return

        # if videos present, tell users that Species net cannot process them
        if vid_present:
            mb.showerror(
                ["SpeciesNet not available", "SpeciesNet no disponible"][lang_idx],
                message=[
                    f"SpeciesNet cannot process videos. Please select images only.",
                    f"SpeciesNet no puede procesar vídeos. Seleccione sólo imágenes.",
                ][lang_idx],
            )
            # reset
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return

        # check if env-speciesnet needs to be downloaded
        model_vars = load_model_vars(model_type="cls")
        bool, env_name = environment_needs_downloading(model_vars)
        if bool:  # env needs be downloaded, ask user
            user_wants_to_download = download_environment(env_name, model_vars)
            if not user_wants_to_download:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return  # user doesn't want to download

        # open progress window
        sppnet_output_window = SpeciesNetOutputWindow()
        sppnet_output_window.add_string("SpeciesNet is starting up...\n\n")

        # deploy speciesnet
        return_value = deploy_speciesnet(chosen_folder, sppnet_output_window)

        # due to a package conflict on macos there might need to be a restart
        if return_value == "restart":
            sppnet_output_window.add_string("\n\nRestarting SpeciesNet...\n\n")
            deploy_speciesnet(chosen_folder, sppnet_output_window)

        # enable button
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        sppnet_output_window.close()
        return

    # note if user is video analysing without smoothing
    global warn_smooth_vid
    if (
        (var_cls_model.get() not in none_txt)
        and (var_smooth_cls_animal.get() == False)
        and vid_present
        and simple_mode == False
        and warn_smooth_vid == True
    ):
        warn_smooth_vid = False
        if not mb.askyesno(
            information_txt[lang_idx],
            [
                "You are about to analyze videos without smoothing the confidence scores. "
                "Typically, a video may contain many frames of the same animal, increasing the likelihood that at least "
                f"one of the labels could be a false prediction. With '{lbl_smooth_cls_animal_txt[lang_idx]}' enabled, all"
                " predictions from a single video will be averaged, resulting in only one label per video. Do you wish to"
                " continue without smoothing?\n\nPress 'No' to go back.",
                "Estás a punto de analizar videos sin suavizado "
                "habilitado. Normalmente, un video puede contener muchos cuadros del mismo animal, lo que aumenta la "
                "probabilidad de que al menos una de las etiquetas pueda ser una predicción falsa. Con "
                f"'{lbl_smooth_cls_animal_txt[lang_idx]}' habilitado, todas las predicciones de un solo video se promediarán,"
                " lo que resultará en una sola etiqueta por video. ¿Deseas continuar sin suavizado habilitado?\n\nPresiona "
                "'No' para regresar.",
            ][lang_idx],
        ):
            return

    # de not allow full image classifier to process videos
    full_image_cls = load_model_vars("cls").get("full_image_cls", False)
    if full_image_cls:
        vid_present = False

    # check which processes need to be listed on the progress window
    if simple_mode:
        processes = []
        if img_present:
            processes.append("img_det")
            if var_cls_model.get() not in none_txt:
                processes.append("img_cls")
        if vid_present:
            processes.append("vid_det")
            if var_cls_model.get() not in none_txt:
                processes.append("vid_cls")
        if not timelapse_mode and img_present:
            processes.append("img_pst")
        if not timelapse_mode and vid_present:
            processes.append("vid_pst")
        if not timelapse_mode:
            processes.append("plt")
    else:
        processes = []
        if img_present:
            processes.append("img_det")
            if var_cls_model.get() not in none_txt:
                processes.append("img_cls")
        if vid_present:
            processes.append("vid_det")
            if var_cls_model.get() not in none_txt:
                processes.append("vid_cls")

    # if working with a full image classifier is selected, remove the detection processes and video stuff
    full_image_cls = load_model_vars("cls").get("full_image_cls", False)
    if full_image_cls:
        if "img_det" in processes:
            processes.remove("img_det")
        if "vid_det" in processes:
            processes.remove("vid_det")
        if "vid_cls" in processes:
            processes.remove("vid_cls")
        if "vid_pst" in processes:
            processes.remove("vid_pst")

    # redirect warnings and error to log files
    global model_error_log
    model_error_log = os.path.join(chosen_folder, "model_error_log.txt")
    global model_warning_log
    model_warning_log = os.path.join(chosen_folder, "model_warning_log.txt")
    global model_special_char_log
    model_special_char_log = os.path.join(chosen_folder, "model_special_char_log.txt")

    # set global variable
    temp_frame_folder_created = False

    # make sure user doesn't press the button twice
    btn_start_deploy.configure(state=DISABLED)
    sim_run_btn.configure(state=DISABLED)
    root.update()

    # check if models need to be downloaded
    if simple_mode:
        var_det_model.set("MegaDetector 5a")
    for model_type in ["cls", "det"]:
        model_vars = load_model_vars(model_type=model_type)
        if model_vars == {}:  # if selected model is None
            continue
        bool, dirpath = model_needs_downloading(model_vars, model_type)
        if bool is None:  # EA needs updating, return to window
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return
        elif bool:  # model can be downloaded, ask user
            user_wants_to_download = download_model(dirpath)
            if not user_wants_to_download:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return  # user doesn't want to download

    # check if environment need to be downloaded
    if simple_mode:
        var_det_model.set("MegaDetector 5a")
    for model_type in ["cls", "det"]:
        model_vars = load_model_vars(model_type=model_type)
        if model_vars == {}:  # if selected model is None
            continue
        bool, env_name = environment_needs_downloading(model_vars)
        if bool:  # env needs be downloaded, ask user
            user_wants_to_download = download_environment(env_name, model_vars)
            if not user_wants_to_download:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return  # user doesn't want to download

    # run some checks that make sense for both simple and advanced mode
    # check if chosen folder is valid
    if chosen_folder in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(
        chosen_folder
    ):
        mb.showerror(
            error_txt[lang_idx],
            message=[
                "Please specify a directory with data to be processed.",
                "Por favor, especifique un directorio con los datos a procesar.",
            ][lang_idx],
        )
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        return

    # save simple settings for next time
    write_global_vars(
        {
            "lang_idx": lang_idx,
            "var_cls_model_idx": dpd_options_cls_model[lang_idx].index(
                var_cls_model.get()
            ),
            "var_sppnet_location_idx": dpd_options_sppnet_location[lang_idx].index(
                var_sppnet_location.get()
            ),
        }
    )

    # simple_mode and advanced mode shared image settings
    additional_img_options = ["--output_relative_filenames"]

    # simple_mode and advanced mode shared video settings
    additional_vid_options = ["--json_confidence_threshold=0.01"]
    if timelapse_mode:
        additional_vid_options.append("--include_all_processed_frames")
    temp_frame_folder_created = False
    if vid_present:
        if var_cls_model.get() not in none_txt:
            global temp_frame_folder
            temp_frame_folder_obj = tempfile.TemporaryDirectory()
            temp_frame_folder_created = True
            temp_frame_folder = temp_frame_folder_obj.name
            additional_vid_options.append("--frame_folder=" + temp_frame_folder)
            additional_vid_options.append("--keep_extracted_frames")

    # if user deployed from simple mode everything will be default, so easy
    if simple_mode:
        # simple mode specific image options
        additional_img_options.append("--recursive")

        # simple mode specific video options
        additional_vid_options.append("--recursive")
        additional_vid_options.append("--time_sample=1")

    # if the user comes from the advanced mode, there are more settings to be checked
    else:
        # save advanced settings for next time
        write_global_vars(
            {
                "var_det_model_idx": dpd_options_model[lang_idx].index(
                    var_det_model.get()
                ),
                "var_det_model_path": var_det_model_path.get(),
                "var_det_model_short": var_det_model_short.get(),
                "var_exclude_subs": var_exclude_subs.get(),
                "var_use_custom_img_size_for_deploy": var_use_custom_img_size_for_deploy.get(),
                "var_image_size_for_deploy": var_image_size_for_deploy.get()
                if var_image_size_for_deploy.get().isdigit()
                else "",
                "var_abs_paths": var_abs_paths.get(),
                "var_disable_GPU": var_disable_GPU.get(),
                "var_process_img": var_process_img.get(),
                "var_use_checkpnts": var_use_checkpnts.get(),
                "var_checkpoint_freq": var_checkpoint_freq.get()
                if var_checkpoint_freq.get().isdecimal()
                else "",
                "var_cont_checkpnt": var_cont_checkpnt.get(),
                "var_process_vid": var_process_vid.get(),
                "var_not_all_frames": var_not_all_frames.get(),
                "var_nth_frame": var_nth_frame.get()
                if var_nth_frame.get().isdecimal()
                else "",
            }
        )

        # check if checkpoint entry is valid
        if (
            var_use_custom_img_size_for_deploy.get()
            and not var_image_size_for_deploy.get().isdecimal()
        ):
            mb.showerror(
                invalid_value_txt[lang_idx],
                [
                    "You either entered an invalid value for the image size, or none at all. You can only "
                    "enter numeric characters.",
                    "Ha introducido un valor no válido para el tamaño de la imagen o no ha introducido ninguno. "
                    "Sólo puede introducir caracteres numéricos.",
                ][lang_idx],
            )
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            return

        # check if checkpoint entry is valid
        if var_use_checkpnts.get() and not var_checkpoint_freq.get().isdecimal():
            if mb.askyesno(
                invalid_value_txt[lang_idx],
                [
                    "You either entered an invalid value for the checkpoint frequency, or none at all. You can only "
                    "enter numeric characters.\n\nDo you want to proceed with the default value 500?",
                    "Ha introducido un valor no válido para la frecuencia del punto de control o no ha introducido ninguno. "
                    "Sólo puede introducir caracteres numéricos.\n\n¿Desea continuar con el valor por defecto 500?",
                ][lang_idx],
            ):
                var_checkpoint_freq.set("500")
                ent_checkpoint_freq.configure(fg="black")
            else:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)

                return

        # check if the nth frame entry is valid
        if var_not_all_frames.get() and not is_valid_float(var_nth_frame.get()):
            if mb.askyesno(
                invalid_value_txt[lang_idx],
                [
                    f"Invalid input for '{lbl_nth_frame_txt[lang_idx]}'. Please enter a numeric value (e.g., '1', '1.5', '0.3', '7')."
                    " Non-numeric values like 'two' or '1,2' are not allowed.\n\nWould you like to proceed with the default value"
                    " of 1?\n\nThis means the program will only process 1 frame every second.",
                    "Entrada no válida para "
                    f"'{lbl_nth_frame_txt[lang_idx]}'. Introduzca un valor numérico (por ejemplo, 1, 1.5, 0.3). Valores no numéricos como"
                    " 'dos' o '1,2' no están permitidos.\n\n¿Desea continuar con el valor predeterminado de 1?\n\nEsto significa que"
                    " el programa solo procesará 1 fotograma cada segundo.",
                ][lang_idx],
            ):
                var_nth_frame.set("1")
                ent_nth_frame.configure(fg="black")
            else:
                btn_start_deploy.configure(state=NORMAL)
                sim_run_btn.configure(state=NORMAL)
                return

        # create command for the image process to be passed on to run_detector_batch.py
        if not var_exclude_subs.get():
            additional_img_options.append("--recursive")
        if var_use_checkpnts.get():
            additional_img_options.append(
                "--checkpoint_frequency=" + var_checkpoint_freq.get()
            )
        if var_cont_checkpnt.get() and check_checkpnt():
            additional_img_options.append("--resume_from_checkpoint=" + loc_chkpnt_file)
        if var_use_custom_img_size_for_deploy.get():
            additional_img_options.append(
                "--image_size=" + var_image_size_for_deploy.get()
            )

        # create command for the video process to be passed on to process_video.py
        if not var_exclude_subs.get():
            additional_vid_options.append("--recursive")
        if var_not_all_frames.get():
            additional_vid_options.append("--time_sample=" + var_nth_frame.get())

    # open progress window with frames for each process that needs to be done
    global progress_window
    progress_window = ProgressWindow(processes=processes)
    progress_window.open()

    # check the chosen folder of special characters and alert the user is there are any
    isolated_special_fpaths = {"total_saved_images": 0}
    for main_dir, _, files in os.walk(chosen_folder):
        for file in files:
            file_path = os.path.join(main_dir, file)
            if os.path.splitext(file_path)[1].lower() in [
                ".jpg",
                ".jpeg",
                ".png",
                ".mp4",
                ".avi",
                ".mpeg",
                ".mpg",
            ]:
                bool, char = contains_special_characters(file_path)
                if bool:
                    drive, rest_of_path = os.path.splitdrive(file_path)
                    path_components = rest_of_path.split(os.path.sep)
                    isolated_special_fpath = drive
                    for (
                        path_component
                    ) in path_components:  # check the largest dir that is faulty
                        isolated_special_fpath = os.path.join(
                            isolated_special_fpath, path_component
                        )
                        if contains_special_characters(path_component)[0]:
                            isolated_special_fpaths["total_saved_images"] += 1
                            if isolated_special_fpath in isolated_special_fpaths:
                                isolated_special_fpaths[isolated_special_fpath][0] += 1
                            else:
                                isolated_special_fpaths[isolated_special_fpath] = [
                                    1,
                                    char,
                                ]
    n_special_chars = len(isolated_special_fpaths) - 1
    total_saved_images = isolated_special_fpaths["total_saved_images"]
    del isolated_special_fpaths["total_saved_images"]

    if total_saved_images > 0:
        # write to log file
        if os.path.isfile(model_special_char_log):
            os.remove(model_special_char_log)
        for k, v in isolated_special_fpaths.items():
            line = f"There are {str(v[0]).ljust(4)} files hidden behind the {str(v[1])} character in folder '{k}'"
            if not line.isprintable():
                line = repr(line)
                print(
                    f"\nSPECIAL CHARACTER LOG: This special character is going to give an error : {line}\n"
                )  # log
            with open(model_special_char_log, "a+", encoding="utf-8") as f:
                f.write(f"{line}\n")

        # log to console
        print(
            f"\nSPECIAL CHARACTER LOG: There are {total_saved_images} files hidden behind {n_special_chars} special characters.\n"
        )

        # prompt user
        special_char_popup_btns = [
            [
                "Continue with filepaths as they are now",
                "Open log file and review the problematic filepaths",
            ],
            [
                "Continuar con las rutas de archivo tal y como están ahora",
                "Abrir el archivo de registro y revisar las rutas de archivo probelmáticas",
            ],
        ][lang_idx]
        special_char_popup = TextButtonWindow(
            title=["Special characters found", "Caracteres especiales encontrados"][
                lang_idx
            ],
            text=[
                "Special characters can be problematic during analysis, resulting in files being skipped.\n"
                f"With your current folder structure, there are a total of {total_saved_images} files that will be potentially skipped.\n"
                f"If you want to make sure these images will be analysed, you would need to manually adjust the names of {n_special_chars} folders.\n"
                "You can find an overview of the probelematic characters and filepaths in the log file:\n\n"
                f"'{model_special_char_log}'\n\n"
                f"You can also decide to continue with the filepaths as they are now, with the risk of excluding {total_saved_images} files.",
                "Los caracteres especiales pueden ser problemáticos durante el análisis, haciendo que se omitan archivos.\n"
                f"Con su actual estructura de carpetas, hay un total de {total_saved_images} archivos que serán potencialmente omitidos.\n"
                f"Si desea asegurarse de que estas imágenes se analizarán, deberá ajustar manualmente los nombres de las carpetas {n_special_chars}.\n"
                "Puede encontrar un resumen de los caracteres problemáticos y las rutas de los archivos en el archivo de registro:\n\n"
                f"'{model_special_char_log}'\n\n"
                f"También puede decidir continuar con las rutas de archivo tal y como están ahora, con el riesgo de excluir archivos {total_saved_images}",
            ][lang_idx],
            buttons=special_char_popup_btns,
        )

        # run option window and check user input
        user_input = special_char_popup.run()
        if user_input != special_char_popup_btns[0]:
            # user does not want to continue as is
            if user_input == special_char_popup_btns[1]:
                # user chose to review paths, so open log file
                open_file_or_folder(model_special_char_log)
            # close progressbar and fix deploy buttuns
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)
            progress_window.close()
            return

    try:
        # process images and/or videos
        if img_present:
            deploy_model(
                chosen_folder,
                additional_img_options,
                data_type="img",
                simple_mode=simple_mode,
            )
        if vid_present:
            deploy_model(
                chosen_folder,
                additional_vid_options,
                data_type="vid",
                simple_mode=simple_mode,
            )

        # if deployed through simple mode, add predefined postprocess directly after deployment and classification
        if simple_mode and not timelapse_mode:
            # if only analysing images, postprocess images with plots
            if "img_pst" in processes and not "vid_pst" in processes:
                postprocess(
                    src_dir=chosen_folder,
                    dst_dir=chosen_folder,
                    thresh=global_vars["var_thresh_default"],
                    sep=False,
                    file_placement=1,
                    sep_conf=False,
                    vis=False,
                    crp=False,
                    exp=True,
                    plt=True,
                    exp_format="XLSX",
                    data_type="img",
                )

            # if only analysing videos, postprocess videos with plots
            elif "vid_pst" in processes and not "img_pst" in processes:
                postprocess(
                    src_dir=chosen_folder,
                    dst_dir=chosen_folder,
                    thresh=global_vars["var_thresh_default"],
                    sep=False,
                    file_placement=1,
                    sep_conf=False,
                    vis=False,
                    crp=False,
                    exp=True,
                    plt=True,
                    exp_format="XLSX",
                    data_type="vid",
                )

            # otherwise postprocess first images without plots, and then videos with plots
            else:
                postprocess(
                    src_dir=chosen_folder,
                    dst_dir=chosen_folder,
                    thresh=global_vars["var_thresh_default"],
                    sep=False,
                    file_placement=1,
                    sep_conf=False,
                    vis=False,
                    crp=False,
                    exp=True,
                    plt=False,
                    exp_format="XLSX",
                    data_type="img",
                )
                postprocess(
                    src_dir=chosen_folder,
                    dst_dir=chosen_folder,
                    thresh=global_vars["var_thresh_default"],
                    sep=False,
                    file_placement=1,
                    sep_conf=False,
                    vis=False,
                    crp=False,
                    exp=True,
                    plt=True,
                    exp_format="XLSX",
                    data_type="vid",
                )

        # let's organise all the json files and check their presence
        image_recognition_file = os.path.join(
            chosen_folder, "image_recognition_file.json"
        )
        image_recognition_file_original = os.path.join(
            chosen_folder, "image_recognition_file_original.json"
        )
        video_recognition_file = os.path.join(
            chosen_folder, "video_recognition_file.json"
        )
        video_recognition_file_original = os.path.join(
            chosen_folder, "video_recognition_file_original.json"
        )
        video_recognition_file_frame = os.path.join(
            chosen_folder, "video_recognition_file.frames.json"
        )
        video_recognition_file_frame_original = os.path.join(
            chosen_folder, "video_recognition_file.frames_original.json"
        )
        timelapse_json = os.path.join(chosen_folder, "timelapse_recognition_file.json")
        exif_data_json = os.path.join(chosen_folder, "exif_data.json")

        # convert to frame jsons to video jsons if frames are classified
        if (
            os.path.isfile(video_recognition_file)
            and os.path.isfile(video_recognition_file_frame)
            and os.path.isfile(video_recognition_file_frame_original)
        ):
            # get the frame_rates from the video_recognition_file.json
            frame_rates = {}
            with open(video_recognition_file) as f:
                data = json.load(f)
                images = data["images"]
                for image in images:
                    file = image["file"]
                    frame_rate = image["frame_rate"]
                    frame_rates[file] = frame_rate

            # convert frame results to video results
            options = FrameToVideoOptions()
            if timelapse_mode:
                options.include_all_processed_frames = True
            else:
                options.include_all_processed_frames = False
            frame_results_to_video_results(
                input_file=video_recognition_file_frame,
                output_file=video_recognition_file,
                options=options,
                video_filename_to_frame_rate=frame_rates,
            )
            frame_results_to_video_results(
                input_file=video_recognition_file_frame_original,
                output_file=video_recognition_file_original,
                options=options,
                video_filename_to_frame_rate=frame_rates,
            )

        # remove unnecessary jsons after conversion
        if os.path.isfile(video_recognition_file_frame_original):
            os.remove(video_recognition_file_frame_original)
        if os.path.isfile(video_recognition_file_frame):
            os.remove(video_recognition_file_frame)
        if os.path.isfile(exif_data_json):
            os.remove(exif_data_json)

        # prepare for Timelapse use
        if timelapse_mode:
            # merge json
            if var_cls_model.get() not in none_txt:
                # if a classification model is selected
                merge_jsons(
                    image_recognition_file_original
                    if os.path.isfile(image_recognition_file_original)
                    else None,
                    video_recognition_file_original
                    if os.path.isfile(video_recognition_file_original)
                    else None,
                    timelapse_json,
                )
            else:
                # if no classification model is selected
                merge_jsons(
                    image_recognition_file
                    if os.path.isfile(image_recognition_file)
                    else None,
                    video_recognition_file
                    if os.path.isfile(video_recognition_file)
                    else None,
                    timelapse_json,
                )

            # remove unnecessary jsons
            if os.path.isfile(image_recognition_file_original):
                os.remove(image_recognition_file_original)
            if os.path.isfile(image_recognition_file):
                os.remove(image_recognition_file)
            if os.path.isfile(video_recognition_file_original):
                os.remove(video_recognition_file_original)
            if os.path.isfile(video_recognition_file):
                os.remove(video_recognition_file)

        # prepare for AddaxAI use
        else:
            # # If at a later stage I want a merged json for AddaxAI too - this is the code
            # merge_jsons(image_recognition_file if os.path.isfile(image_recognition_file) else None,
            #             video_recognition_file if os.path.isfile(video_recognition_file) else None,
            #             os.path.join(chosen_folder, "merged_recognition_file.json"))

            # remove unnecessary jsons
            if os.path.isfile(image_recognition_file_original):
                os.remove(image_recognition_file_original)
            if os.path.isfile(video_recognition_file_original):
                os.remove(video_recognition_file_original)

        # reset window
        update_frame_states()

        # close progress window
        progress_window.close()

        # clean up temp folder with frames
        if temp_frame_folder_created:
            temp_frame_folder_obj.cleanup()

        # show model error pop up window
        if os.path.isfile(model_error_log):
            mb.showerror(
                error_txt[lang_idx],
                [
                    f"There were one or more model errors. See\n\n'{model_error_log}'\n\nfor more information.",
                    f"Se han producido uno o más errores de modelo. Consulte\n\n'{model_error_log}'\n\npara obtener más información.",
                ][lang_idx],
            )

        # show model warning pop up window
        if os.path.isfile(model_warning_log):
            mb.showerror(
                error_txt[lang_idx],
                [
                    f"There were one or more model warnings. See\n\n'{model_warning_log}'\n\nfor more information.",
                    f"Se han producido uno o más advertencias de modelo. Consulte\n\n'{model_warning_log}'\n\npara obtener más información.",
                ][lang_idx],
            )

        # show postprocessing warning log
        global postprocessing_error_log
        postprocessing_error_log = os.path.join(
            chosen_folder, "postprocessing_error_log.txt"
        )
        if os.path.isfile(postprocessing_error_log):
            mb.showwarning(
                warning_txt[lang_idx],
                [
                    f"One or more files failed to be analysed by the model (e.g., corrupt files) and will be skipped by "
                    f"post-processing features. See\n\n'{postprocessing_error_log}'\n\nfor more info.",
                    f"Uno o más archivos no han podido ser analizados por el modelo (por ejemplo, ficheros corruptos) y serán "
                    f"omitidos por las funciones de post-procesamiento. Para más información, véase\n\n'{postprocessing_error_log}'",
                ][lang_idx],
            )

        # enable button
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        root.update()

        # show results
        if timelapse_mode:
            mb.showinfo(
                "Analysis done!",
                f"Recognition file created at \n\n{timelapse_json}\n\nTo use it in Timelapse, return to "
                "Timelapse with the relevant image set open, select the menu item 'Recognition > Import "
                "recognition data for this image set' and navigate to the file above.",
            )
            open_file_or_folder(os.path.dirname(timelapse_json))
        elif simple_mode:
            show_result_info(os.path.join(chosen_folder, "results.xlsx"))

    except Exception as error:
        # log error
        print(
            "\n\nERROR:\n"
            + str(error)
            + "\n\nSUBPROCESS OUTPUT:\n"
            + subprocess_output
            + "\n\nTRACEBACK:\n"
            + traceback.format_exc()
            + "\n\n"
        )
        print(f"cancel_deploy_model_pressed : {cancel_deploy_model_pressed}")

        if cancel_deploy_model_pressed:
            pass

        else:
            # show error
            mb.showerror(
                title=error_txt[lang_idx],
                message=["An error has occurred", "Ha ocurrido un error"][lang_idx]
                + " (AddaxAI v"
                + current_AA_version
                + "): '"
                + str(error)
                + "'.",
                detail=subprocess_output + "\n" + traceback.format_exc(),
            )

            # close window
            progress_window.close()

            # enable button
            btn_start_deploy.configure(state=NORMAL)
            sim_run_btn.configure(state=NORMAL)


# get data from file list and create graph
def produce_graph(file_list_txt=None, dir=None):
    # if a list with images is specified
    if file_list_txt:
        count_dict = {}

        # loop through the files
        with open(file_list_txt) as f:
            for line in f:
                # open xml
                img = line.rstrip()
                annotation = return_xml_path(img)
                tree = ET.parse(annotation)
                root = tree.getroot()

                # loop through detections
                for obj in root.findall("object"):
                    # add detection to dict
                    name = obj.findtext("name")
                    if name not in count_dict:
                        count_dict[name] = 0
                    count_dict[name] += 1
            f.close()

        # create plot
        classes = list(count_dict.keys())
        counts = list(count_dict.values())
        fig = plt.figure(figsize=(10, 5))
        plt.bar(classes, counts, width=0.4, color=green_primary)
        plt.ylabel(
            ["No. of instances verified", "No de instancias verificadas"][lang_idx]
        )
        plt.close()

        # return results
        return fig


# create pascal voc annotation files from a list of detections
def create_pascal_voc_annotation(image_path, annotation_list, human_verified):
    # init vars
    image_path = Path(image_path)
    img = np.array(Image.open(image_path).convert("RGB"))
    annotation = ET.Element("annotation")

    # set verified flag if been verified in a previous session
    if human_verified:
        annotation.set("verified", "yes")

    ET.SubElement(annotation, "folder").text = str(image_path.parent.name)
    ET.SubElement(annotation, "filename").text = str(image_path.name)
    ET.SubElement(annotation, "path").text = str(image_path)

    source = ET.SubElement(annotation, "source")
    ET.SubElement(source, "database").text = "Unknown"

    size = ET.SubElement(annotation, "size")
    ET.SubElement(size, "width").text = str(img.shape[1])
    ET.SubElement(size, "height").text = str(img.shape[0])
    ET.SubElement(size, "depth").text = str(img.shape[2])

    ET.SubElement(annotation, "segmented").text = "0"

    for annot in annotation_list:
        tmp_annot = annot.split(",")
        cords, label = tmp_annot[0:-2], tmp_annot[-1]
        xmin, ymin, xmax, ymax = (
            cords[0],
            cords[1],
            cords[4],
            cords[5],
        )  # left, top, right, bottom

        object = ET.SubElement(annotation, "object")
        ET.SubElement(object, "name").text = label
        ET.SubElement(object, "pose").text = "Unspecified"
        ET.SubElement(object, "truncated").text = "0"
        ET.SubElement(object, "difficult").text = "0"

        bndbox = ET.SubElement(object, "bndbox")
        ET.SubElement(bndbox, "xmin").text = str(xmin)
        ET.SubElement(bndbox, "ymin").text = str(ymin)
        ET.SubElement(bndbox, "xmax").text = str(xmax)
        ET.SubElement(bndbox, "ymax").text = str(ymax)

    indent(annotation)
    tree = ET.ElementTree(annotation)
    xml_file_name = return_xml_path(image_path)
    Path(os.path.dirname(xml_file_name)).mkdir(parents=True, exist_ok=True)
    tree.write(xml_file_name)


# loop json and see which images and annotations fall in user-specified catgegory
def select_detections(selection_dict, prepare_files):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # open patience window
    steps_progress = PatienceDialog(
        total=8, text=[f"Loading...", f"Cargando..."][lang_idx]
    )
    steps_progress.open()
    current_step = 1
    steps_progress.update_progress(current_step)
    current_step += 1

    # init vars
    selected_dir = var_choose_folder.get()
    recognition_file = os.path.join(selected_dir, "image_recognition_file.json")
    temp_folder = os.path.join(selected_dir, "temp-folder")
    Path(temp_folder).mkdir(parents=True, exist_ok=True)
    file_list_txt = os.path.join(temp_folder, "hitl_file_list.txt")
    class_list_txt = os.path.join(temp_folder, "hitl_class_list.txt")
    steps_progress.update_progress(current_step)
    current_step += 1

    # make sure json has relative paths
    json_paths_converted = False
    if check_json_paths(recognition_file) != "relative":
        make_json_relative(recognition_file)
        json_paths_converted = True
    steps_progress.update_progress(current_step)
    current_step += 1

    # list selection criteria
    selected_categories = []
    min_confs = []
    max_confs = []
    ann_min_confs_specific = {}
    selected_files = {}
    rad_ann_val = rad_ann_var.get()
    ann_min_confs_generic = None
    steps_progress.update_progress(current_step)
    current_step += 1

    # class specific values
    for key, values in selection_dict.items():
        category = values["class"]
        chb_val = values["chb_var"].get()
        min_conf = round(values["min_conf_var"].get(), 2)
        max_conf = round(values["max_conf_var"].get(), 2)
        ann_min_conf_specific = values["scl_ann_var_specific"].get()
        ann_min_confs_generic = values["scl_ann_var_generic"].get()
        ann_min_confs_specific[category] = ann_min_conf_specific

        # if class is selected
        if chb_val:
            selected_categories.append(category)
            min_confs.append(min_conf)
            max_confs.append(max_conf)
            selected_files[category] = []
    steps_progress.update_progress(current_step)
    current_step += 1

    # remove old file list if present
    if prepare_files:
        if os.path.isfile(file_list_txt):
            os.remove(file_list_txt)
    steps_progress.update_progress(current_step)
    current_step += 1

    # loop though images and list those which pass the criteria
    img_and_detections_dict = {}
    with open(recognition_file, "r") as image_recognition_file_content:
        data = json.load(image_recognition_file_content)
        label_map = fetch_label_map_from_json(recognition_file)

        # check all images...
        for image in data["images"]:
            # set vars
            image_path = os.path.join(selected_dir, image["file"])
            annotations = []
            image_already_added = False

            # check if the image has already been human verified
            try:
                human_verified = image["manually_checked"]
            except:
                human_verified = False

            # check all detections ...
            if "detections" in image:
                for detection in image["detections"]:
                    category_id = detection["category"]
                    category = label_map[category_id]
                    conf = detection["conf"]

                    # ... if they pass any of the criteria
                    for i in range(len(selected_categories)):
                        if (
                            category == selected_categories[i]
                            and conf >= min_confs[i]
                            and conf <= max_confs[i]
                        ):
                            # this image contains one or more detections which pass
                            if not image_already_added:
                                selected_files[selected_categories[i]].append(
                                    image_path
                                )
                                image_already_added = True

                    # prepare annotations
                    if prepare_files:
                        display_annotation = False

                        # if one annotation threshold for all classes is specified
                        if rad_ann_val == 1 and conf >= ann_min_confs_generic:
                            display_annotation = True

                        # if class-specific annotation thresholds are specified
                        elif (
                            rad_ann_val == 2
                            and conf >= ann_min_confs_specific[category]
                        ):
                            display_annotation = True

                        # add this detection to the list
                        if display_annotation:
                            im = Image.open(image_path)
                            width, height = im.size
                            left = int(round(detection["bbox"][0] * width))  # xmin
                            top = int(round(detection["bbox"][1] * height))  # ymin
                            right = (
                                int(round(detection["bbox"][2] * width)) + left
                            )  # width
                            bottom = (
                                int(round(detection["bbox"][3] * height)) + top
                            )  # height
                            list = [
                                left,
                                top,
                                None,
                                None,
                                right,
                                bottom,
                                None,
                                category,
                            ]
                            string = ",".join(map(str, list))
                            annotations.append(string)

            # create pascal voc annotation file for this image
            if prepare_files:
                img_and_detections_dict[image_path] = {
                    "annotations": annotations,
                    "human_verified": human_verified,
                }
    steps_progress.update_progress(current_step)
    current_step += 1

    # update count widget
    total_imgs = 0
    for category, files in selected_files.items():
        label_map = fetch_label_map_from_json(recognition_file)
        classes_list = [v for k, v in label_map.items()]
        row = classes_list.index(category) + 2
        frame = selection_dict[row]["frame"]
        lbl_n_img = selection_dict[row]["lbl_n_img"]
        chb_var = selection_dict[row]["chb_var"].get()
        rad_var = selection_dict[row]["rad_var"].get()

        # if user specified a percentage of total images
        if chb_var and rad_var == 2:
            # check if entry is valid
            ent_per_var = selection_dict[row]["ent_per_var"].get()
            try:
                ent_per_var = float(ent_per_var)
            except:
                invalid_value_warning(
                    [
                        f"percentage of images for class '{category}'",
                        f"porcentaje de imágenes para la clase '{category}'",
                    ][lang_idx]
                )
                return
            if ent_per_var == "" or ent_per_var < 0 or ent_per_var > 100:
                invalid_value_warning(
                    [
                        f"percentage of images for class '{category}'",
                        f"porcentaje de imágenes para la clase '{category}'",
                    ][lang_idx]
                )
                return

            # randomly select percentage of images
            total_n = len(files)
            n_selected = int(total_n * (ent_per_var / 100))
            random.shuffle(files)
            files = files[:n_selected]

        # user specified a max number of images
        elif chb_var and rad_var == 3:
            # check if entry is valid
            ent_amt_var = selection_dict[row]["ent_amt_var"].get()
            try:
                ent_amt_var = float(ent_amt_var)
            except:
                invalid_value_warning(
                    [
                        f"number of images for class '{category}'",
                        f"número de imágenes para la clase '{category}'",
                    ][lang_idx]
                )
                return
            if ent_amt_var == "":
                invalid_value_warning(
                    [
                        f"number of images for class '{category}'",
                        f"número de imágenes para la clase '{category}'",
                    ][lang_idx]
                )
                return

            # randomly select specified number of images
            total_n = len(files)
            n_selected = int(ent_amt_var)
            random.shuffle(files)
            files = files[:n_selected]

        # update label text
        n_imgs = len(files)
        lbl_n_img.configure(text=str(n_imgs))
        total_imgs += n_imgs

        # loop through the ultimately selected images and create files
        if prepare_files and len(files) > 0:
            # open patience window
            patience_dialog = PatienceDialog(
                total=n_imgs,
                text=[
                    f"Preparing files for {category}...",
                    f"Preparando archivos para {category}...",
                ][lang_idx],
            )
            patience_dialog.open()
            current = 1

            # human sort images per class
            def atoi(text):
                return int(text) if text.isdigit() else text

            def natural_keys(text):
                return [atoi(c) for c in re.split("(\d+)", text)]

            files.sort(key=natural_keys)

            for img in files:
                # update patience window
                patience_dialog.update_progress(current)
                current += 1

                # create text file with images
                file_list_txt = os.path.normpath(file_list_txt)
                with open(file_list_txt, "a") as f:
                    f.write(f"{os.path.normpath(img)}\n")
                    f.close()

                # # list annotations
                annotation_path = return_xml_path(img)

                # create xml file if not already present
                if not os.path.isfile(annotation_path):
                    create_pascal_voc_annotation(
                        img,
                        img_and_detections_dict[img]["annotations"],
                        img_and_detections_dict[img]["human_verified"],
                    )

            # close patience window
            patience_dialog.close()
    steps_progress.update_progress(current_step)
    current_step += 1
    steps_progress.close()

    # update total number of images
    lbl_n_total_imgs.configure(
        text=[f"TOTAL: {total_imgs}", f"TOTAL: {total_imgs}"][lang_idx]
    )

    if prepare_files:
        # create file with classes
        with open(class_list_txt, "a") as f:
            for k, v in label_map.items():
                f.write(f"{v}\n")
            f.close()

        # write arguments to file in case user quits and continues later
        annotation_arguments = {
            "recognition_file": recognition_file,
            "class_list_txt": class_list_txt,
            "file_list_txt": file_list_txt,
            "label_map": label_map,
            "img_and_detections_dict": img_and_detections_dict,
        }

        annotation_arguments_pkl = os.path.join(
            selected_dir, "temp-folder", "annotation_information.pkl"
        )
        with open(annotation_arguments_pkl, "wb") as fp:
            pickle.dump(annotation_arguments, fp)
            fp.close()

        # start human in the loop process
        try:
            open_annotation_windows(
                recognition_file=recognition_file,
                class_list_txt=class_list_txt,
                file_list_txt=file_list_txt,
                label_map=label_map,
            )
        except Exception as error:
            # log error
            print(
                "ERROR:\n"
                + str(error)
                + "\n\nDETAILS:\n"
                + str(traceback.format_exc())
                + "\n\n"
            )

            # show error
            mb.showerror(
                title=error_txt[lang_idx],
                message=["An error has occurred", "Ha ocurrido un error"][lang_idx]
                + " (AddaxAI v"
                + current_AA_version
                + "): '"
                + str(error)
                + "'.",
                detail=traceback.format_exc(),
            )

    # change json paths back, if converted earlier
    if json_paths_converted:
        make_json_absolute(recognition_file)


# count confidence values per class for histograms
def fetch_confs_per_class(json_fpath):
    label_map = fetch_label_map_from_json(
        os.path.join(var_choose_folder.get(), "image_recognition_file.json")
    )
    confs = {}
    for key in label_map:
        confs[key] = []
    with open(json_fpath) as content:
        data = json.load(content)
        for image in data["images"]:
            if "detections" in image:
                for detection in image["detections"]:
                    conf = detection["conf"]
                    category = detection["category"]
                    confs[category].append(conf)
    return confs
