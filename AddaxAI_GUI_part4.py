# open the human-in-the-loop settings window
def open_hitl_settings_window():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # fetch confs for histograms
    confs = fetch_confs_per_class(
        os.path.join(var_choose_folder.get(), "image_recognition_file.json")
    )

    # set global vars
    global selection_dict
    global rad_ann_var
    global hitl_ann_selection_frame
    global hitl_settings_canvas
    global hitl_settings_window
    global lbl_n_total_imgs

    # init vars
    selected_dir = var_choose_folder.get()
    recognition_file = os.path.join(selected_dir, "image_recognition_file.json")

    # init window
    hitl_settings_window = customtkinter.CTkToplevel(root)
    hitl_settings_window.title(
        [
            "Verification selection settings",
            "Configuración de selección de verificación",
        ][lang_idx]
    )
    hitl_settings_window.geometry("+10+10")
    hitl_settings_window.maxsize(width=ADV_WINDOW_WIDTH, height=800)

    # set scrollable frame
    hitl_settings_scroll_frame = Frame(hitl_settings_window)
    hitl_settings_scroll_frame.pack(fill=BOTH, expand=1)

    # set canvas
    hitl_settings_canvas = Canvas(hitl_settings_scroll_frame)
    hitl_settings_canvas.pack(side=LEFT, fill=BOTH, expand=1)

    # set scrollbar
    hitl_settings_scrollbar = tk.Scrollbar(
        hitl_settings_scroll_frame, orient=VERTICAL, command=hitl_settings_canvas.yview
    )
    hitl_settings_scrollbar.pack(side=RIGHT, fill=Y)

    # enable scroll on mousewheel
    def hitl_settings_canvas_mousewheel(event):
        if os.name == "nt":
            hitl_settings_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            hitl_settings_canvas.yview_scroll(int(-1 * (event.delta / 2)), "units")

    # configure canvas and bind scroll events
    hitl_settings_canvas.configure(yscrollcommand=hitl_settings_scrollbar.set)
    hitl_settings_canvas.bind(
        "<Configure>",
        lambda e: hitl_settings_canvas.configure(
            scrollregion=hitl_settings_canvas.bbox("all")
        ),
    )
    hitl_settings_canvas.bind_all("<MouseWheel>", hitl_settings_canvas_mousewheel)
    hitl_settings_canvas.bind_all("<Button-4>", hitl_settings_canvas_mousewheel)
    hitl_settings_canvas.bind_all("<Button-5>", hitl_settings_canvas_mousewheel)

    # set labelframe to fill with widgets
    hitl_settings_main_frame = LabelFrame(hitl_settings_canvas)

    # img selection frame
    hitl_img_selection_frame = LabelFrame(
        hitl_settings_main_frame,
        text=[" Image selection criteria ", " Criterios de selección de imágenes "][
            lang_idx
        ],
        pady=2,
        padx=5,
        relief="solid",
        highlightthickness=5,
        font=100,
        fg=green_primary,
        labelanchor="n",
    )
    hitl_img_selection_frame.configure(font=(text_font, 15, "bold"))
    hitl_img_selection_frame.grid(column=0, row=1, columnspan=2, sticky="ew")
    hitl_img_selection_frame.columnconfigure(0, weight=1, minsize=50 * scale_factor)
    hitl_img_selection_frame.columnconfigure(1, weight=1, minsize=200 * scale_factor)
    hitl_img_selection_frame.columnconfigure(2, weight=1, minsize=200 * scale_factor)
    hitl_img_selection_frame.columnconfigure(3, weight=1, minsize=200 * scale_factor)
    hitl_img_selection_frame.columnconfigure(4, weight=1, minsize=200 * scale_factor)

    # show explanation and resize window
    def show_text_hitl_img_selection_explanation():
        text_hitl_img_selection_explanation.grid(
            column=0, row=0, columnspan=5, padx=5, pady=5, sticky="ew"
        )
        hitl_settings_window.update()
        w = hitl_settings_main_frame.winfo_width() + 30
        h = hitl_settings_main_frame.winfo_height() + 10
        hitl_settings_window.geometry(f"{w}x{h}")
        hitl_settings_window.update()

    # img explanation
    Button(
        master=hitl_img_selection_frame,
        text="?",
        width=1,
        command=show_text_hitl_img_selection_explanation,
    ).grid(column=0, row=0, columnspan=1, padx=5, pady=5, sticky="ew")
    text_hitl_img_selection_explanation = Text(
        master=hitl_img_selection_frame,
        wrap=WORD,
        width=1,
        height=12 * explanation_text_box_height_factor,
    )
    text_hitl_img_selection_explanation.tag_config(
        "explanation",
        font=f"{text_font} {int(13 * text_size_adjustment_factor)} normal",
        lmargin1=10,
        lmargin2=10,
    )
    text_hitl_img_selection_explanation.insert(
        END,
        [
            "Here, you can specify which images you wish to review. If a detection aligns with the chosen criteria, the image will be "
            "chosen for the verification process. In the review process, you’ll need to make sure all detections in the image are correct. "
            "You have the option to select a subset of your images based on specific classes, confidence ranges, and selection methods. For "
            "instance, the default settings will enable you to verify images with detections that the model is medium-sure about (with"
            " confidences between 0.2 and 0.8). This means that you don’t review high-confidence detections of more than 0.8 confidence and "
            "avoid wasting time on low-confidence detections of less than 0.2. Feel free to adjust these settings to suit your data. To "
            "determine the number of images that will require verification based on the selected criteria, press the “Update counts” button "
            "below. If required, you can specify a selection method that will randomly choose a subset based on a percentage or an absolute "
            "number. Verification will adjust the results in the JSON file. This means that you can continue to use AddaxAI with verified "
            "results and post-process as usual.",
            "Aquí puede especificar qué imágenes desea revisar. Si una detección se alinea con los "
            "criterios elegidos, la imagen será elegida para el proceso de verificación. Tiene la opción de seleccionar un subconjunto de "
            "sus imágenes según clases específicas, rangos de confianza y métodos de selección. Por ejemplo, la configuración"
            " predeterminada le permitirá verificar imágenes con detecciones de las que el modelo está medio seguro "
            "(con confianzas entre 0,2 y 0,8). Esto significa que no revisa las detecciones de alta confianza con "
            "más de 0,8 de confianza y evita perder tiempo en detecciones de baja confianza de menos de 0,2. Siéntase"
            " libre de ajustar estas configuraciones para adaptarlas a sus datos. Para determinar la cantidad de imágenes "
            "que requerirán verificación según los criterios seleccionados, presione el botón 'Actualizar recuentos' a continuación. Si es "
            "necesario, puede especificar un método de selección que elegirá aleatoriamente un subconjunto en función de un porcentaje o un "
            "número absoluto. La verificación ajustará los resultados en el archivo JSON. Esto significa que puede continuar usando AddaxAI"
            " con resultados verificados y realizar el posprocesamiento como de costumbre.",
        ][lang_idx],
    )
    text_hitl_img_selection_explanation.tag_add("explanation", "1.0", "1.end")

    # img table headers
    ttk.Label(master=hitl_img_selection_frame, text="").grid(column=0, row=1)
    ttk.Label(
        master=hitl_img_selection_frame, text="Class", font=f"{text_font} 13 bold"
    ).grid(column=1, row=1)
    ttk.Label(
        master=hitl_img_selection_frame,
        text="Confidence range",
        font=f"{text_font} 13 bold",
    ).grid(column=2, row=1)
    ttk.Label(
        master=hitl_img_selection_frame,
        text="Selection method",
        font=f"{text_font} 13 bold",
    ).grid(column=3, row=1)
    ttk.Label(
        master=hitl_img_selection_frame,
        text="Number of images",
        font=f"{text_font} 13 bold",
    ).grid(column=4, row=1)

    # ann selection frame
    hitl_ann_selection_frame = LabelFrame(
        hitl_settings_main_frame,
        text=[
            " Annotation selection criteria ",
            " Criterios de selección de anotaciones ",
        ][lang_idx],
        pady=2,
        padx=5,
        relief="solid",
        highlightthickness=5,
        font=100,
        fg=green_primary,
        labelanchor="n",
    )
    hitl_ann_selection_frame.configure(font=(text_font, 15, "bold"))
    hitl_ann_selection_frame.grid(column=0, row=2, columnspan=2, sticky="ew")
    hitl_ann_selection_frame.columnconfigure(0, weight=1, minsize=50)
    hitl_ann_selection_frame.columnconfigure(1, weight=1, minsize=200)
    hitl_ann_selection_frame.columnconfigure(2, weight=1, minsize=200)
    hitl_ann_selection_frame.columnconfigure(3, weight=1, minsize=200)
    hitl_ann_selection_frame.columnconfigure(4, weight=1, minsize=200)

    # ann explanation
    text_hitl_ann_selection_explanation = Text(
        master=hitl_ann_selection_frame,
        wrap=WORD,
        width=1,
        height=5 * explanation_text_box_height_factor,
    )
    text_hitl_ann_selection_explanation.grid(
        column=0, row=0, columnspan=5, padx=5, pady=5, sticky="ew"
    )
    text_hitl_ann_selection_explanation.tag_config(
        "explanation",
        font=f"{text_font} {int(13 * text_size_adjustment_factor)} normal",
        lmargin1=10,
        lmargin2=10,
    )
    text_hitl_ann_selection_explanation.insert(
        END,
        [
            "In the previous step, you selected which images to verify. In this frame, you can specify which annotations to display "
            "on these images. During the verification process, all instances of all classes need to be labeled. That is why you want to display "
            "all annotations above a reasonable confidence threshold. You can select generic or class-specific confidence thresholds. If you are"
            " uncertain, just stick with the default value. A threshold of 0.2 is probably a conservative threshold for most projects.",
            "En el paso anterior, seleccionó qué imágenes verificar. En este marco, puede especificar qué anotaciones mostrar en estas imágenes."
            " Durante el proceso de verificación, se deben etiquetar todas las instancias de todas las clases. Es por eso que desea mostrar todas"
            " las anotaciones por encima de un umbral de confianza razonable. Puede seleccionar umbrales de confianza genéricos o específicos de"
            " clase. Si no está seguro, siga con el valor predeterminado. Un umbral de 0,2 es un umbral conservador para la mayoría"
            " de los proyectos.",
        ][lang_idx],
    )
    text_hitl_ann_selection_explanation.tag_add("explanation", "1.0", "1.end")

    # ann same thresh
    rad_ann_var = IntVar()
    rad_ann_var.set(1)
    rad_ann_same = Radiobutton(
        hitl_ann_selection_frame,
        text=[
            "Same annotation confidence threshold for all classes",
            "Mismo umbral de confianza para todas las clases",
        ][lang_idx],
        variable=rad_ann_var,
        value=1,
        command=lambda: toggle_hitl_ann_selection(
            rad_ann_var, hitl_ann_selection_frame
        ),
    )
    rad_ann_same.grid(row=1, column=1, columnspan=2, sticky="w")
    frame_ann_same = LabelFrame(
        hitl_ann_selection_frame, text="", pady=2, padx=5, relief=RAISED
    )
    frame_ann_same.grid(column=3, row=1, columnspan=2, sticky="ew")
    frame_ann_same.columnconfigure(0, weight=1, minsize=200)
    frame_ann_same.columnconfigure(1, weight=1, minsize=200)
    lbl_ann_same = ttk.Label(
        master=frame_ann_same, text=["All classes", "Todas las clases"][lang_idx]
    )
    lbl_ann_same.grid(row=0, column=0, sticky="w")
    scl_ann_var_generic = DoubleVar()
    scl_ann_var_generic.set(0.60)
    scl_ann = Scale(
        frame_ann_same,
        from_=0,
        to=1,
        resolution=0.01,
        orient=HORIZONTAL,
        variable=scl_ann_var_generic,
        width=10,
        length=1,
        showvalue=0,
    )
    scl_ann.grid(row=0, column=1, sticky="we")
    dsp_scl_ann = Label(frame_ann_same, textvariable=scl_ann_var_generic)
    dsp_scl_ann.grid(row=0, column=0, sticky="e", padx=5)

    # ann specific thresh
    rad_ann_gene = Radiobutton(
        hitl_ann_selection_frame,
        text=[
            "Class-specific annotation confidence thresholds",
            "Umbrales de confianza específicas de clase",
        ][lang_idx],
        variable=rad_ann_var,
        value=2,
        command=lambda: toggle_hitl_ann_selection(
            rad_ann_var, hitl_ann_selection_frame
        ),
    )
    rad_ann_gene.grid(row=2, column=1, columnspan=2, sticky="w")

    # create widgets and vars for each class
    label_map = fetch_label_map_from_json(recognition_file)
    selection_dict = {}
    for i, [k, v] in enumerate(label_map.items()):
        # image selection frame
        row = i + 2
        frame = LabelFrame(
            hitl_img_selection_frame, text="", pady=2, padx=5, relief=RAISED
        )
        frame.grid(column=0, row=1, columnspan=2, sticky="ew")
        frame.columnconfigure(0, weight=1, minsize=50)
        frame.columnconfigure(1, weight=1, minsize=200)
        frame.columnconfigure(2, weight=1, minsize=200)
        frame.columnconfigure(3, weight=1, minsize=200)
        frame.columnconfigure(4, weight=1, minsize=200)
        chb_var = BooleanVar()
        chb_var.set(False)
        chb = tk.Checkbutton(
            frame, variable=chb_var, command=lambda e=row: enable_selection_widgets(e)
        )
        lbl_class = ttk.Label(master=frame, text=v, state=DISABLED)
        min_conf = DoubleVar(value=0.2)
        max_conf = DoubleVar(value=1.0)
        fig = plt.figure(figsize=(2, 0.3))
        plt.hist(confs[k], bins=10, range=(0, 1), color=green_primary, rwidth=0.8)
        plt.xticks([])
        plt.yticks([])
        dist_graph = FigureCanvasTkAgg(fig, frame)
        plt.close()
        rsl = RangeSliderH(
            frame,
            [min_conf, max_conf],
            padX=11,
            digit_precision=".2f",
            bgColor="#ececec",
            Width=180,
            font_size=10,
            font_family=text_font,
        )
        rad_var = IntVar()
        rad_var.set(1)
        rad_all = Radiobutton(
            frame,
            text=["All images in range", "Todo dentro del rango"][lang_idx],
            variable=rad_var,
            value=1,
            state=DISABLED,
            command=lambda e=row: enable_amt_per_ent(e),
        )
        rad_per = Radiobutton(
            frame,
            text=["Subset percentage", "Subconjunto %"][lang_idx],
            variable=rad_var,
            value=2,
            state=DISABLED,
            command=lambda e=row: enable_amt_per_ent(e),
        )
        rad_amt = Radiobutton(
            frame,
            text=["Subset number", "Subconjunto no."][lang_idx],
            variable=rad_var,
            value=3,
            state=DISABLED,
            command=lambda e=row: enable_amt_per_ent(e),
        )
        ent_per_var = StringVar()
        ent_per = tk.Entry(frame, textvariable=ent_per_var, width=4, state=DISABLED)
        ent_amt_var = StringVar()
        ent_amt = tk.Entry(frame, textvariable=ent_amt_var, width=4, state=DISABLED)
        lbl_n_img = ttk.Label(master=frame, text="0", state=DISABLED)

        # annotation selection frame
        frame_ann = LabelFrame(
            hitl_ann_selection_frame, text="", pady=2, padx=5, relief=SUNKEN
        )
        frame_ann.grid(column=3, row=row, columnspan=2, sticky="ew")
        frame_ann.columnconfigure(0, weight=1, minsize=200)
        frame_ann.columnconfigure(1, weight=1, minsize=200)
        lbl_ann_gene = ttk.Label(master=frame_ann, text=v, state=DISABLED)
        lbl_ann_gene.grid(row=0, column=0, sticky="w")
        scl_ann_var_specific = DoubleVar()
        scl_ann_var_specific.set(0.60)
        scl_ann_gene = Scale(
            frame_ann,
            from_=0,
            to=1,
            resolution=0.01,
            orient=HORIZONTAL,
            variable=scl_ann_var_specific,
            width=10,
            length=1,
            showvalue=0,
            state=DISABLED,
        )
        scl_ann_gene.grid(row=0, column=1, sticky="we")
        dsp_scl_ann_gene = Label(
            frame_ann, textvariable=scl_ann_var_specific, state=DISABLED
        )
        dsp_scl_ann_gene.grid(row=0, column=0, sticky="e", padx=5)

        # store info in a dictionary
        item = {
            "row": row,
            "label_map_id": k,
            "class": v,
            "frame": frame,
            "min_conf_var": min_conf,
            "max_conf_var": max_conf,
            "chb_var": chb_var,
            "lbl_class": lbl_class,
            "range_slider_widget": rsl,
            "lbl_n_img": lbl_n_img,
            "rad_all": rad_all,
            "rad_per": rad_per,
            "rad_amt": rad_amt,
            "rad_var": rad_var,
            "ent_per_var": ent_per_var,
            "ent_per": ent_per,
            "ent_amt_var": ent_amt_var,
            "ent_amt": ent_amt,
            "scl_ann_var_specific": scl_ann_var_specific,
            "scl_ann_var_generic": scl_ann_var_generic,
        }
        selection_dict[row] = item

        # place widgets
        frame.grid(row=row, column=0, columnspan=5)
        chb.grid(row=1, column=0)
        lbl_class.grid(row=1, column=1)
        rsl.lower()
        dist_graph.get_tk_widget().grid(row=0, rowspan=3, column=2, sticky="n")
        rad_all.grid(row=0, column=3, sticky="w")
        rad_per.grid(row=1, column=3, sticky="w")
        ent_per.grid(row=1, column=3, sticky="e")
        rad_amt.grid(row=2, column=3, sticky="w")
        ent_amt.grid(row=2, column=3, sticky="e")
        lbl_n_img.grid(row=1, column=4)

        # set row minsize
        set_minsize_rows(frame)

        # update window
        hitl_settings_window.update_idletasks()

        # place in front
        bring_window_to_top_but_not_for_ever(hitl_settings_window)

    # set minsize for rows
    row_count = hitl_img_selection_frame.grid_size()[1]
    for row in range(row_count):
        hitl_img_selection_frame.grid_rowconfigure(row, minsize=minsize_rows)

    # add row with total number of images to review
    total_imgs_frame = LabelFrame(
        hitl_img_selection_frame, text="", pady=2, padx=5, relief=RAISED
    )
    total_imgs_frame.columnconfigure(0, weight=1, minsize=50)
    total_imgs_frame.columnconfigure(1, weight=1, minsize=200)
    total_imgs_frame.columnconfigure(2, weight=1, minsize=200)
    total_imgs_frame.columnconfigure(3, weight=1, minsize=200)
    total_imgs_frame.columnconfigure(4, weight=1, minsize=200)
    total_imgs_frame.grid(row=row_count, column=0, columnspan=5)
    lbl_n_total_imgs = ttk.Label(master=total_imgs_frame, text="TOTAL: 0", state=NORMAL)
    lbl_n_total_imgs.grid(row=1, column=4)

    # button frame
    hitl_test_frame = LabelFrame(
        hitl_settings_main_frame,
        text=[" Actions ", " Acciones "][lang_idx],
        pady=2,
        padx=5,
        relief="solid",
        highlightthickness=5,
        font=100,
        fg=green_primary,
        labelanchor="n",
    )
    hitl_test_frame.configure(font=(text_font, 15, "bold"))
    hitl_test_frame.grid(column=0, row=3, columnspan=2, sticky="ew")
    hitl_test_frame.columnconfigure(0, weight=1, minsize=115)
    hitl_test_frame.columnconfigure(1, weight=1, minsize=115)
    hitl_test_frame.columnconfigure(2, weight=1, minsize=115)

    # shorten texts for linux
    if sys.platform == "linux" or sys.platform == "linux2":
        btn_hitl_update_txt = ["Update counts", "La actualización cuenta"][lang_idx]
        btn_hitl_show_txt = ["Show / hide annotation", "Mostrar / ocultar anotaciones"][
            lang_idx
        ]
        btn_hitl_start_txt = ["Start review process", "Iniciar proceso de revisión"][
            lang_idx
        ]
    else:
        btn_hitl_update_txt = ["Update counts", "La actualización cuenta"][lang_idx]
        btn_hitl_show_txt = [
            "Show / hide annotation selection criteria",
            "Mostrar / ocultar criterios de anotaciones",
        ][lang_idx]
        btn_hitl_start_txt = [
            "Start review process with selected criteria",
            "Iniciar proceso de revisión",
        ][lang_idx]

    # buttons
    btn_hitl_update = Button(
        master=hitl_test_frame,
        text=btn_hitl_update_txt,
        width=1,
        command=lambda: select_detections(
            selection_dict=selection_dict, prepare_files=False
        ),
    )
    btn_hitl_update.grid(row=0, column=0, rowspan=1, sticky="nesw", padx=5)
    btn_hitl_show = Button(
        master=hitl_test_frame,
        text=btn_hitl_show_txt,
        width=1,
        command=toggle_hitl_ann_selection_frame,
    )
    btn_hitl_show.grid(row=0, column=1, rowspan=1, sticky="nesw", padx=5)
    btn_hitl_start = Button(
        master=hitl_test_frame,
        text=btn_hitl_start_txt,
        width=1,
        command=lambda: select_detections(
            selection_dict=selection_dict, prepare_files=True
        ),
    )
    btn_hitl_start.grid(row=0, column=2, rowspan=1, sticky="nesw", padx=5)

    # create scrollable canvas window
    hitl_settings_canvas.create_window(
        (0, 0), window=hitl_settings_main_frame, anchor="nw"
    )

    # hide annotation selection frame
    toggle_hitl_ann_selection_frame(cmd="hide")

    # update counts after the window is created
    select_detections(selection_dict=selection_dict, prepare_files=False)

    # adjust window size to widgets
    w = hitl_settings_main_frame.winfo_width() + 30
    h = hitl_settings_main_frame.winfo_height() + 10
    hitl_settings_window.geometry(f"{w}x{h}")


# helper function to quickly check the verification status of xml
def verification_status(xml):
    tree = ET.parse(xml)
    root = tree.getroot()
    try:
        verification_status = True if root.attrib["verified"] == "yes" else False
    except:
        verification_status = False
    return verification_status


# helper function to blur person bbox
def blur_box(
    image, bbox_left, bbox_top, bbox_right, bbox_bottom, image_width, image_height
):
    x1, y1, x2, y2 = map(int, [bbox_left, bbox_top, bbox_right, bbox_bottom])
    if (
        x1 >= x2
        or y1 >= y2
        or x1 < 0
        or y1 < 0
        or x2 > image_width
        or y2 > image_height
    ):
        raise ValueError(f"Invalid bounding box: ({x1}, {y1}, {x2}, {y2})")
    roi = image[y1:y2, x1:x2]
    if roi.size == 0:
        raise ValueError("Extracted ROI is empty. Check the bounding box coordinates.")
    blurred_roi = cv2.GaussianBlur(roi, (71, 71), 0)
    image[y1:y2, x1:x2] = blurred_roi
    return image


# helper function to correctly indent pascal voc annotation files
def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


# make sure the program quits when simple or advanced window is closed
def on_toplevel_close():
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
    root.destroy()


# check if image is corrupted by attempting to load them
def is_image_corrupted(image_path):
    try:
        ImageFile.LOAD_TRUNCATED_IMAGES = False
        with Image.open(image_path) as img:
            img.load()
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        return False
    except:
        return True


# read file list and check all images if they are corrupted
def check_images(image_list_file):
    corrupted_images = []
    with open(image_list_file, "r") as file:
        image_paths = file.read().splitlines()
    for image_path in image_paths:
        if os.path.exists(image_path):
            if is_image_corrupted(image_path):
                corrupted_images.append(image_path)
    return corrupted_images


# try to fix truncated file by opening and saving it again
def fix_images(image_paths):
    for image_path in image_paths:
        if os.path.exists(image_path):
            try:
                ImageFile.LOAD_TRUNCATED_IMAGES = True
                with Image.open(image_path) as img:
                    img_copy = img.copy()
                    img_copy.save(
                        image_path, format=img.format, exif=img.info.get("exif")
                    )
            except Exception as e:
                print(f"Could not fix image: {e}")


# remove non ansi characters from text
def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


# classes to open window with speciesnet output
class SpeciesNetOutputWindow:
    def __init__(self):
        self.sppnet_output_window_root = customtkinter.CTkToplevel(root)
        self.sppnet_output_window_root.title("SpeciesNet output")
        self.text_area = tk.Text(
            self.sppnet_output_window_root, wrap=tk.WORD, height=7, width=85
        )
        self.text_area.pack(padx=10, pady=10)
        self.close_button = tk.Button(
            self.sppnet_output_window_root, text="Cancel", command=self.cancel
        )
        self.close_button.pack(pady=5)
        self.sppnet_output_window_root.protocol(
            "WM_DELETE_WINDOW", self.close
        )  # Handle window close
        bring_window_to_top_but_not_for_ever(self.sppnet_output_window_root)

    def add_string(self, text, process=None):
        if process is not None:
            self.process = process
        if text.strip():
            print(text)

            clean_text = remove_ansi_escape_sequences(text)

            # Check if this is a progress bar update
            is_pbar = "%" in clean_text

            if not is_pbar:
                # Insert non-progress-bar messages above the progress section
                self.text_area.insert(tk.END, clean_text + "\n")  # Insert at the top
                self.text_area.see(tk.END)
                self.sppnet_output_window_root.update()
                return  # Exit function early, don't process as a progress bar

            # Ensure attributes exist before updating
            if not hasattr(self, "detector_preprocess_line"):
                self.detector_preprocess_line = " Detector preprocess:   0%\n"
            if not hasattr(self, "detector_predict_line"):
                self.detector_predict_line = " Detector predict:      0%\n"
            if not hasattr(self, "classifier_preprocess_line"):
                self.classifier_preprocess_line = " Classifier preprocess: 0%\n"
            if not hasattr(self, "classifier_predict_line"):
                self.classifier_predict_line = " Classifier predict:    0%\n"
            if not hasattr(self, "geolocation_line"):
                self.geolocation_line = " Geolocation:           0%\n"

            # Update progress bar lines based on prefixes
            if clean_text.startswith("Detector preprocess"):
                self.detector_preprocess_line = clean_text
            elif clean_text.startswith("Detector predict"):
                self.detector_predict_line = clean_text
            elif clean_text.startswith("Classifier preprocess"):
                self.classifier_preprocess_line = clean_text
            elif clean_text.startswith("Classifier predict"):
                self.classifier_predict_line = clean_text
            elif clean_text.startswith("Geolocation"):
                self.geolocation_line = clean_text

            # Insert all progress bars together to maintain order
            self.text_area.insert(
                tk.END, f"\n {self.detector_preprocess_line}", "progress"
            )
            self.text_area.insert(tk.END, f" {self.detector_predict_line}", "progress")
            self.text_area.insert(
                tk.END, f" {self.classifier_preprocess_line}", "progress"
            )
            self.text_area.insert(
                tk.END, f" {self.classifier_predict_line}", "progress"
            )
            self.text_area.insert(tk.END, f" {self.geolocation_line}", "progress")

            # Ensure scrolling to the latest update
            self.text_area.see(tk.END)
            self.sppnet_output_window_root.update()

    def close(self):
        self.sppnet_output_window_root.destroy()

    def cancel(self):
        global cancel_speciesnet_deploy_pressed
        global btn_start_deploy
        global sim_run_btn
        if os.name == "nt":
            Popen(f"TASKKILL /F /PID {self.process.pid} /T")
        else:
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
        btn_start_deploy.configure(state=NORMAL)
        sim_run_btn.configure(state=NORMAL)
        cancel_speciesnet_deploy_pressed = True
        self.sppnet_output_window_root.destroy()


# temporary function to deploy speciesnet
def deploy_speciesnet(chosen_folder, sppnet_output_window, simple_mode=False):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # prepare variables
    chosen_folder = str(Path(chosen_folder))
    python_executable = get_python_interprator("speciesnet")
    sppnet_output_file = os.path.join(chosen_folder, "sppnet_output_file.json")

    # save settings for next time
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

    # save advanced settings for next time
    if not simple_mode:
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

    # get param values
    model_vars = load_model_vars()
    if simple_mode:
        cls_detec_thresh = model_vars["var_cls_detec_thresh_default"]
    else:
        cls_detec_thresh = var_cls_detec_thresh.get()

    # get location information
    location_args = []
    country_code = var_sppnet_location.get()[:3]
    location_args.append(f"--country={country_code}")
    if country_code == "USA":
        state_code = var_sppnet_location.get()[4:6]
        location_args.append(f"--admin1_region={state_code}")
    write_global_vars(
        {
            "var_sppnet_location_idx": dpd_options_sppnet_location[lang_idx].index(
                var_sppnet_location.get()
            )
        }
    )

    # create commands for Windows
    if os.name == "nt":
        if location_args == []:
            command = [
                python_executable,
                "-m",
                "speciesnet.scripts.run_model",
                f"--folders={chosen_folder}",
                f"--predictions_json={sppnet_output_file}",
            ]
        else:
            command = [
                python_executable,
                "-m",
                "speciesnet.scripts.run_model",
                f"--folders={chosen_folder}",
                f"--predictions_json={sppnet_output_file}",
                *location_args,
            ]

    # create command for MacOS and Linux
    else:
        if location_args == []:
            command = [
                f"'{python_executable}' -m speciesnet.scripts.run_model --folders='{chosen_folder}' --predictions_json='{sppnet_output_file}'"
            ]
        else:
            location_args = "' '".join(location_args)
            command = [
                f"'{python_executable}' -m speciesnet.scripts.run_model --folders='{chosen_folder}' --predictions_json='{sppnet_output_file}' '{location_args}'"
            ]

    # log command
    print("command:")
    print(json.dumps(command, indent=4))

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

    global cancel_speciesnet_deploy_pressed
    cancel_speciesnet_deploy_pressed = False

    # read output
    for line in p.stdout:
        # log
        sppnet_output_window.add_string(line, p)

        # early exit if cancel button is pressed
        if cancel_speciesnet_deploy_pressed:
            sppnet_output_window.add_string("\n\nCancel button pressed!")
            time.sleep(2)
            return

        # temporary fix for macOS package conflict
        # since the env is compiled on macOS 10.15, scipy is not compatible with macOS 10.14
        if line.startswith("ImportError: "):
            sppnet_output_window.add_string(
                f"\n\nThere seems to be a mismatch between macOS versions: {line}\n\n"
            )
            sppnet_output_window.add_string(
                "Attempting to solve conflict automatically...\n\n"
            )

            # uninstall scipy
            p = Popen(
                f"{python_executable} -m pip uninstall -y scipy",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True,
                preexec_fn=os.setsid,
            )
            for line in p.stdout:
                sppnet_output_window.add_string(line)

            # install scipy again
            p = Popen(
                f"{python_executable} -m pip install --no-cache-dir scipy",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                bufsize=1,
                shell=True,
                universal_newlines=True,
                preexec_fn=os.setsid,
            )
            for line in p.stdout:
                sppnet_output_window.add_string(line)

            # retry
            return "restart"

    # convert json to AddaxAI format
    sppnet_output_window.add_string(
        "\n\nConverting SpeciesNet output to AddaxAI format..."
    )
    speciesnet_to_md_py = os.path.join(
        AddaxAI_files,
        "AddaxAI",
        "classification_utils",
        "model_types",
        "speciesnet_to_md.py",
    )
    recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")

    # cmd for windows
    if os.name == "nt":
        p = Popen(
            [
                f"{python_executable}",
                f"{speciesnet_to_md_py}",
                f"{sppnet_output_file}",
                f"{recognition_file}",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            shell=True,
            universal_newlines=True,
        )

    # cmd for macos and linux
    else:
        p = Popen(
            [
                f'"{python_executable}" "{speciesnet_to_md_py}" "{sppnet_output_file}" "{recognition_file}"'
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            shell=True,
            universal_newlines=True,
            preexec_fn=os.setsid,
        )

    # log output
    for line in p.stdout:
        sppnet_output_window.add_string(line, p)
    sppnet_output_window.add_string("\n\nConverting Done!")

    # if that is done, remove the speciesnet output file
    if os.path.exists(sppnet_output_file):
        os.remove(sppnet_output_file)

    # create addaxai metadata
    sppnet_output_window.add_string("\n\nAdding AddaxAI metadata...")
    addaxai_metadata = {
        "addaxai_metadata": {
            "version": current_AA_version,
            "custom_model": False,
            "custom_model_info": {},
        }
    }

    # write metadata to json and make absolute if specified
    append_to_json(recognition_file, addaxai_metadata)

    # get rid of absolute paths if specified
    if check_json_paths(recognition_file) == "absolute":
        make_json_relative(recognition_file)

    # if in timelapse mode, change name of recognition file
    if timelapse_mode:
        timelapse_json = os.path.join(chosen_folder, "timelapse_recognition_file.json")
        os.rename(recognition_file, timelapse_json)
        mb.showinfo(
            "Analysis done!",
            f"Recognition file created at \n\n{timelapse_json}\n\nTo use it in Timelapse, return to "
            "Timelapse with the relevant image set open, select the menu item 'Recognition > Import "
            "recognition data for this image set' and navigate to the file above.",
        )
        open_file_or_folder(os.path.dirname(timelapse_json))

    # convert JSON to AddaxAI format if not in timelapse mode
    else:
        with open(recognition_file) as image_recognition_file_content:
            data = json.load(image_recognition_file_content)

            # fetch and invert label maps
            cls_label_map = data["classification_categories"]
            det_label_map = data["detection_categories"]
            inverted_cls_label_map = {v: k for k, v in cls_label_map.items()}
            inverted_det_label_map = {v: k for k, v in det_label_map.items()}

            # add cls classes to det label map
            # if a model shares category names with MD, add to existing value
            for k, _ in inverted_cls_label_map.items():
                if k in inverted_det_label_map.keys():
                    value = str(inverted_det_label_map[k])
                    inverted_det_label_map[k] = value
                else:
                    inverted_det_label_map[k] = str(len(inverted_det_label_map) + 1)

            # loop and adjust
            for image in data["images"]:
                if "detections" in image:
                    for detection in image["detections"]:
                        category_id = detection["category"]
                        category_conf = detection["conf"]
                        if (
                            category_conf >= cls_detec_thresh
                            and det_label_map[category_id] == "animal"
                        ):
                            if "classifications" in detection:
                                highest_classification = detection["classifications"][0]
                                class_idx = highest_classification[0]
                                class_name = cls_label_map[class_idx]
                                detec_idx = inverted_det_label_map[class_name]
                                detection["prev_conf"] = detection["conf"]
                                detection["prev_category"] = detection["category"]
                                detection["conf"] = highest_classification[1]
                                detection["category"] = str(detec_idx)

        # write json to be used by AddaxAI
        data["detection_categories_original"] = data["detection_categories"]
        data["detection_categories"] = {v: k for k, v in inverted_det_label_map.items()}

        # overwrite the file wit adjusted data
        with open(recognition_file, "w") as json_file:
            json.dump(data, json_file, indent=1)

    # reset window
    update_frame_states()
    root.update()


# convert pascal bbox to yolo
def convert_bbox_pascal_to_yolo(size, box):
    dw = 1.0 / (size[0])
    dh = 1.0 / (size[1])
    x = (box[0] + box[1]) / 2.0 - 1
    y = (box[2] + box[3]) / 2.0 - 1
    w = box[1] - box[0]
    h = box[3] - box[2]
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)


# special function because the sim dpd has a different value for 'None'
def sim_mdl_dpd_callback(self):
    # this means the user chose SpeciesNet in simple mode, so tell user to use the advanced mode
    if self == "Global - SpeciesNet - Google":
        mb.showerror(
            ["SpeciesNet not available", "SpeciesNet no disponible"][lang_idx],
            message=[
                f"'Global - SpeciesNet - Google' is not available in simple mode. Please switch to advanced mode to use SpeciesNet.",
                f"'Global - SpeciesNet - Google' no está disponible en modo simple. Cambie al modo avanzado para usar SpeciesNet.",
            ][lang_idx],
        )

    var_cls_model.set(
        dpd_options_cls_model[lang_idx][sim_dpd_options_cls_model[lang_idx].index(self)]
    )
    model_cls_animal_options(var_cls_model.get())


# return xml path with temp-folder squeezed in
def return_xml_path(img_path):
    head_path = var_choose_folder.get()
    tail_path = os.path.splitext(os.path.relpath(img_path, head_path))
    temp_xml_path = os.path.join(head_path, "temp-folder", tail_path[0] + ".xml")
    return os.path.normpath(temp_xml_path)


# temporary file which labelImg writes to notify AddaxAI that it should convert xml to coco
class LabelImgExchangeDir:
    def __init__(self, dir):
        self.dir = dir
        Path(self.dir).mkdir(parents=True, exist_ok=True)

    def create_file(self, content, idx):
        timestamp_milliseconds = str(
            str(datetime.date.today())
            + str(datetime.datetime.now().strftime("%H%M%S%f"))
        ).replace("-", "")
        temp_file = os.path.normpath(
            os.path.join(self.dir, f"{timestamp_milliseconds}-{idx}.txt")
        )
        with open(temp_file, "w") as f:
            f.write(content)

    def read_file(self, fp):
        with open(fp, "r") as f:
            content = f.read()
            return content

    def delete_file(self, fp):
        if os.path.exists(fp):
            os.remove(fp)

    def exist_file(self):
        filelist = glob.glob(os.path.normpath(os.path.join(self.dir, "*.txt")))
        for fn in sorted(filelist):
            return [True, fn]
        return [False, ""]


# delete temp folder
def delete_temp_folder(file_list_txt):
    temp_folder = os.path.dirname(file_list_txt)
    if os.path.isdir(temp_folder):
        shutil.rmtree(temp_folder)


# browse file and display result
def browse_file(var, var_short, var_path, dsp, filetype, cut_off_length, options, nrow):
    # choose file
    file = filedialog.askopenfilename(filetypes=filetype)

    # shorten if needed
    dsp_file = os.path.basename(file)
    if len(dsp_file) > cut_off_length:
        dsp_file = "..." + dsp_file[0 - cut_off_length + 3 :]

    # set variables
    var_short.set(dsp_file)

    # reset to default if faulty
    if file != "":
        dsp.grid(column=0, row=nrow, sticky="e")
        var_path.set(file)
    else:
        var.set(options[0])


# switches the yolov5 version by modifying the python import path
def switch_yolov5_version(model_type):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({model_type})\n")

    # set the path to the desired version
    base_path = os.path.join(AddaxAI_files, "yolov5_versions")
    if model_type == "old models":
        version_path = os.path.join(base_path, "yolov5_old", "yolov5")
    elif model_type == "new models":
        version_path = os.path.join(base_path, "yolov5_new", "yolov5")
    else:
        raise ValueError("Invalid model_type")

    # add yolov5 checkout to PATH if not already there
    if version_path not in sys.path:
        sys.path.insert(0, version_path)

    # add yolov5 checkout to PYTHONPATH if not already there
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    PYTHONPATH_to_add = version_path + PYTHONPATH_separator
    if not current_pythonpath.startswith(PYTHONPATH_to_add):
        os.environ["PYTHONPATH"] = PYTHONPATH_to_add + current_pythonpath


# extract label map from custom model
def extract_label_map_from_model(model_file):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})")

    # import module from cameratraps dir
    from cameratraps.megadetector.detection.pytorch_detector import PTDetector

    # load model
    label_map_detector = PTDetector(model_file, force_cpu=True)

    # fetch classes
    try:
        CUSTOM_DETECTOR_LABEL_MAP = {}
        for id in label_map_detector.model.names:
            CUSTOM_DETECTOR_LABEL_MAP[id] = label_map_detector.model.names[id]
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
            message=[
                "An error has occurred when trying to extract classes",
                "Se ha producido un error al intentar extraer las clases",
            ][lang_idx]
            + " (AddaxAI v"
            + current_AA_version
            + "): '"
            + str(error)
            + "'"
            + [
                ".\n\nWill try to proceed and produce the output json file, but post-processing features of AddaxAI will not work.",
                ".\n\nIntentará continuar y producir el archivo json de salida, pero las características de post-procesamiento de AddaxAI no funcionarán.",
            ][lang_idx],
            detail=traceback.format_exc(),
        )

    # delete and free up memory
    del label_map_detector

    # log
    print(f"Label map: {CUSTOM_DETECTOR_LABEL_MAP})\n")

    # return label map
    return CUSTOM_DETECTOR_LABEL_MAP


# fetch label map from json
def fetch_label_map_from_json(path_to_json):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    label_map = data["detection_categories"]
    return label_map


# check if json paths are relative or absolute
def check_json_paths(path_to_json):
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
    path = os.path.normpath(data["images"][0]["file"])
    if path.startswith(os.path.normpath(var_choose_folder.get())):
        return "absolute"
    else:
        return "relative"


# make json paths relative
def make_json_relative(path_to_json):
    if check_json_paths(path_to_json) == "absolute":
        # open
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)

        # adjust
        for image in data["images"]:
            absolute_path = os.path.normpath(image["file"])
            relative_path = absolute_path.replace(
                os.path.normpath(var_choose_folder.get()), ""
            )[1:]
            image["file"] = relative_path

        # write
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)


# make json paths absolute
def make_json_absolute(path_to_json):
    if check_json_paths(path_to_json) == "relative":
        # open
        with open(path_to_json, "r") as json_file:
            data = json.load(json_file)

        # adjust
        for image in data["images"]:
            relative_path = image["file"]
            absolute_path = os.path.normpath(
                os.path.join(var_choose_folder.get(), relative_path)
            )
            image["file"] = absolute_path

        # write
        with open(path_to_json, "w") as json_file:
            json.dump(data, json_file, indent=1)


# add information to json file
def append_to_json(path_to_json, object_to_be_appended):
    # open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)

    # adjust
    data["info"].update(object_to_be_appended)

    # write
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)


# change human-in-the-loop prgress variable
def change_hitl_var_in_json(path_to_json, status):
    # open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)

    # adjust
    data["info"]["addaxai_metadata"]["hitl_status"] = status

    # write
    with open(path_to_json, "w") as json_file:
        json.dump(data, json_file, indent=1)


# get human-in-the-loop prgress variable
def get_hitl_var_in_json(path_to_json):
    # open
    with open(path_to_json, "r") as json_file:
        data = json.load(json_file)
        addaxai_metadata = data["info"].get("addaxai_metadata") or data["info"].get(
            "ecoassist_metadata"
        )  # include old name 'EcoAssist' for backwards compatibility

    # get status
    if "hitl_status" in addaxai_metadata:
        status = addaxai_metadata["hitl_status"]
    else:
        status = "never-started"

    # return
    return status


# show warning for video post-processing
def check_json_presence_and_warn_user(infinitive, continuous, noun):
    # check json presence
    img_json = False
    if os.path.isfile(
        os.path.join(var_choose_folder.get(), "image_recognition_file.json")
    ):
        img_json = True
    vid_json = False
    if os.path.isfile(
        os.path.join(var_choose_folder.get(), "video_recognition_file.json")
    ):
        vid_json = True

    # show warning
    if not img_json:
        if vid_json:
            mb.showerror(
                error_txt[lang_idx],
                [
                    f"{noun.capitalize()} is not supported for videos.",
                    f"{noun.capitalize()} no es compatible con vídeos.",
                ][lang_idx],
            )
            return True
        if not vid_json:
            mb.showerror(
                error_txt[lang_idx],
                [
                    f"No model output file present. Make sure you run step 2 before {continuous} the files. {noun.capitalize()} "
                    "is only supported for images.",
                    f"No hay archivos de salida del modelo. Asegúrese de ejecutar el paso 2 antes de {continuous} los archivos. "
                    f"{noun.capitalize()} sólo es compatible con imágenes",
                ][lang_idx],
            )
            return True
    if img_json:
        if vid_json:
            mb.showinfo(
                warning_txt[lang_idx],
                [
                    f"{noun.capitalize()} is not supported for videos. Will continue to only {infinitive} the images...",
                    f"No se admiten {noun.capitalize()} para los vídeos. Continuará sólo {infinitive} las imágenes...",
                ][lang_idx],
            )


# dir names for when separating on confidence
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
    1.0: "conf_0.9-1.0",
}


# move files into subdirectories
def move_files(
    file,
    detection_type,
    var_file_placement,
    max_detection_conf,
    var_sep_conf,
    dst_root,
    src_dir,
    manually_checked,
):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # squeeze in extra dir if sorting on confidence
    if var_sep_conf and detection_type != "empty":
        global conf_dirs
        if manually_checked:
            confidence_dir = "verified"
        else:
            ceiled_confidence = math.ceil(max_detection_conf * 10) / 10.0
            confidence_dir = conf_dirs[ceiled_confidence]
        new_file = os.path.join(detection_type, confidence_dir, file)
    else:
        new_file = os.path.join(detection_type, file)

    # set paths
    src = os.path.join(src_dir, file)
    dst = os.path.join(dst_root, new_file)

    # create subfolder
    Path(os.path.dirname(dst)).mkdir(parents=True, exist_ok=True)

    # place image or video in subfolder
    if var_file_placement == 1:  # move
        shutil.move(src, dst)
    elif var_file_placement == 2:  # copy
        shutil.copy2(src, dst)

    # return new relative file path
    return new_file


# sort multiple checkpoint in order from recent to last
def sort_checkpoint_files(files):
    def get_timestamp(file):
        timestamp_str = file.split("_")[1].split(".")[0]
        return datetime.datetime.strptime(timestamp_str, "%Y%m%d%H%M%S")

    sorted_files = sorted(files, key=get_timestamp, reverse=True)
    return sorted_files


# check if checkpoint file is present and assign global variable
def check_checkpnt():
    global loc_chkpnt_file
    loc_chkpnt_files = []
    for filename in os.listdir(var_choose_folder.get()):
        if re.search("^md_checkpoint_\d+\.json$", filename):
            loc_chkpnt_files.append(filename)
    if len(loc_chkpnt_files) == 0:
        mb.showinfo(
            [
                "No checkpoint file found",
                "No se ha encontrado ningún archivo de puntos de control",
            ][lang_idx],
            [
                "There is no checkpoint file found. Cannot continue from checkpoint file...",
                "No se ha encontrado ningún archivo de punto de control. No se puede continuar desde el archivo de punto de control...",
            ][lang_idx],
        )
        return False
    if len(loc_chkpnt_files) == 1:
        loc_chkpnt_file = os.path.join(var_choose_folder.get(), loc_chkpnt_files[0])
    elif len(loc_chkpnt_files) > 1:
        loc_chkpnt_file = os.path.join(
            var_choose_folder.get(), sort_checkpoint_files(loc_chkpnt_files)[0]
        )
    return True


# cut off string if it is too long
def shorten_path(path, length):
    if len(path) > length:
        path = "..." + path[0 - length + 3 :]
    return path


# browse directory
def browse_dir(
    var, var_short, dsp, cut_off_length, n_row, n_column, str_sticky, source_dir=False
):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # choose directory
    chosen_dir = filedialog.askdirectory()

    # early exit
    if chosen_dir in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(chosen_dir):
        return

    # set choice to variable
    var.set(chosen_dir)

    # shorten, set and grid display
    dsp_chosen_dir = chosen_dir
    dsp_chosen_dir = shorten_path(dsp_chosen_dir, cut_off_length)
    var_short.set(dsp_chosen_dir)
    dsp.grid(column=n_column, row=n_row, sticky=str_sticky)

    # also update simple mode if it regards the source dir
    if source_dir:
        global sim_dir_pth
        sim_dir_pth.configure(text=dsp_chosen_dir, text_color="black")


# choose a custom classifier for animals
def model_cls_animal_options(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set simple mode cls dropdown to the same index for its own dpd list
    sim_mdl_dpd.set(
        sim_dpd_options_cls_model[lang_idx][dpd_options_cls_model[lang_idx].index(self)]
    )

    # remove or show widgets
    if self not in none_txt:
        cls_frame.grid(row=cls_frame_row, column=0, columnspan=2, sticky="ew")
    else:
        cls_frame.grid_forget()

    # get model specific variable values
    global sim_spp_scr
    if (
        self not in none_txt and self != "Global - SpeciesNet - Google"
    ):  # normal procedure for all classifiers other than speciesnet
        model_vars = load_model_vars()
        dsp_choose_classes.configure(
            text=f"{len(model_vars['selected_classes'])} of {len(model_vars['all_classes'])}"
        )
        var_cls_detec_thresh.set(model_vars["var_cls_detec_thresh"])
        var_cls_class_thresh.set(model_vars["var_cls_class_thresh"])
        var_smooth_cls_animal.set(model_vars["var_smooth_cls_animal"])

        # remove widgets of species net
        lbl_sppnet_location.grid_remove()
        dpd_sppnet_location.grid_remove()

        # show widgets for other classifiers
        lbl_choose_classes.grid(row=row_choose_classes, sticky="nesw", pady=2)
        btn_choose_classes.grid(row=row_choose_classes, column=1, sticky="nesw", padx=5)
        dsp_choose_classes.grid(row=row_choose_classes, column=0, sticky="e", padx=0)
        lbl_cls_class_thresh.grid(row=row_cls_class_thresh, sticky="nesw", pady=2)
        scl_cls_class_thresh.grid(
            row=row_cls_class_thresh, column=1, sticky="ew", padx=10
        )
        dsp_cls_class_thresh.grid(
            row=row_cls_class_thresh, column=0, sticky="e", padx=0
        )
        lbl_smooth_cls_animal.grid(row=row_smooth_cls_animal, sticky="nesw", pady=2)
        chb_smooth_cls_animal.grid(
            row=row_smooth_cls_animal, column=1, sticky="nesw", padx=5
        )

        # set rowsize
        set_minsize_rows(cls_frame)

        # adjust simple_mode window
        sim_spp_lbl.configure(text_color="black")
        sim_spp_scr.grid_forget()
        sim_spp_scr = SpeciesSelectionFrame(
            master=sim_spp_frm,
            height=sim_spp_scr_height,
            all_classes=model_vars["all_classes"],
            selected_classes=model_vars["selected_classes"],
            command=on_spp_selection,
        )
        sim_spp_scr._scrollbar.configure(height=0)
        sim_spp_scr.grid(
            row=1, column=0, padx=PADX, pady=(PADY / 4, PADY), sticky="ew", columnspan=2
        )

    elif self == "Global - SpeciesNet - Google":  # special procedure for speciesnet
        # remove widgets for other classifiers
        lbl_choose_classes.grid_remove()
        btn_choose_classes.grid_remove()
        dsp_choose_classes.grid_remove()
        lbl_cls_class_thresh.grid_remove()
        scl_cls_class_thresh.grid_remove()
        dsp_cls_class_thresh.grid_remove()
        lbl_smooth_cls_animal.grid_remove()
        chb_smooth_cls_animal.grid_remove()

        # set rowsize to 0
        cls_frame.grid_rowconfigure(2, minsize=0)
        cls_frame.grid_rowconfigure(3, minsize=0)
        cls_frame.grid_rowconfigure(4, minsize=0)

        # place widgets for speciesnet
        lbl_sppnet_location.grid(row=row_sppnet_location, sticky="nesw", pady=2)
        dpd_sppnet_location.grid(
            row=row_sppnet_location, column=1, sticky="nesw", padx=5, pady=2
        )

        # set selection frame to dummy spp again
        sim_spp_lbl.configure(text_color="grey")
        sim_spp_scr.grid_forget()
        sim_spp_scr = SpeciesSelectionFrame(
            master=sim_spp_frm, height=sim_spp_scr_height, dummy_spp=True
        )
        sim_spp_scr._scrollbar.configure(height=0)
        sim_spp_scr.grid(
            row=1, column=0, padx=PADX, pady=(PADY / 4, PADY), sticky="ew", columnspan=2
        )

    else:
        # set selection frame to dummy spp again
        sim_spp_lbl.configure(text_color="grey")
        sim_spp_scr.grid_forget()
        sim_spp_scr = SpeciesSelectionFrame(
            master=sim_spp_frm, height=sim_spp_scr_height, dummy_spp=True
        )
        sim_spp_scr._scrollbar.configure(height=0)
        sim_spp_scr.grid(
            row=1, column=0, padx=PADX, pady=(PADY / 4, PADY), sticky="ew", columnspan=2
        )

    # save settings
    write_global_vars(
        {
            "var_cls_model_idx": dpd_options_cls_model[lang_idx].index(
                var_cls_model.get()
            ),  # write index instead of value
            "var_sppnet_location_idx": dpd_options_sppnet_location[lang_idx].index(
                var_sppnet_location.get()
            ),  # write index instead of value
        }
    )

    # finish up
    toggle_cls_frame()
    resize_canvas_to_content()


# load a custom yolov5 model
def model_options(self):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # if custom model is selected
    if var_det_model.get() in custom_model_txt:
        # choose, display and set global var
        browse_file(
            var_det_model,
            var_det_model_short,
            var_det_model_path,
            dsp_model,
            [("Yolov5 model", "*.pt")],
            30,
            dpd_options_model[lang_idx],
            row_model,
        )

    else:
        var_det_model_short.set("")
        var_det_model_path.set("")

    # save settings
    write_global_vars(
        {
            "var_det_model_idx": dpd_options_model[lang_idx].index(
                var_det_model.get()
            ),  # write index instead of value
            "var_det_model_short": var_det_model_short.get(),
            "var_det_model_path": var_det_model_path.get(),
        }
    )


# view results after processing
def view_results(frame):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})")
    print(f"frame text: {frame.cget('text')}\n")

    # convert path separators
    chosen_folder = os.path.normpath(var_choose_folder.get())

    # set json paths
    image_recognition_file = os.path.join(chosen_folder, "image_recognition_file.json")
    video_recognition_file = os.path.join(chosen_folder, "video_recognition_file.json")

    # open json files at step 2
    if frame.cget("text").startswith(f" {step_txt[lang_idx]} 2"):
        if os.path.isfile(image_recognition_file):
            open_file_or_folder(image_recognition_file)
        if os.path.isfile(video_recognition_file):
            open_file_or_folder(video_recognition_file)

    # open destination folder at step 4
    if frame.cget("text").startswith(f" {step_txt[lang_idx]} 4"):
        open_file_or_folder(var_output_dir.get())


# open file or folder
def open_file_or_folder(path, show_error=True):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # set language var
    error_opening_results_txt = [
        "Error opening results",
        "Error al abrir los resultados",
    ]

    # open file
    if platform.system() == "Darwin":  # mac
        try:
            subprocess.call(("open", path))
        except:
            if show_error:
                mb.showerror(
                    error_opening_results_txt[lang_idx],
                    [
                        f"Could not open '{path}'. You'll have to find it yourself...",
                        f"No se ha podido abrir '{path}'. Tendrás que encontrarlo tú mismo...",
                    ][lang_idx],
                )
    elif platform.system() == "Windows":  # windows
        try:
            os.startfile(path)
        except:
            if show_error:
                mb.showerror(
                    error_opening_results_txt[lang_idx],
                    [
                        f"Could not open '{path}'. You'll have to find it yourself...",
                        f"No se ha podido abrir '{path}'. Tendrás que encontrarlo tú mismo...",
                    ][lang_idx],
                )
    else:  # linux
        try:
            subprocess.call(("xdg-open", path))
        except:
            try:
                subprocess.call(("gnome-open", path))
            except:
                if show_error:
                    mb.showerror(
                        error_opening_results_txt[lang_idx],
                        [
                            f"Could not open '{path}'. Neither the 'xdg-open' nor 'gnome-open' command worked. "
                            "You'll have to find it yourself...",
                            f"No se ha podido abrir '{path}'. Ni el comando 'xdg-open' ni el 'gnome-open' funcionaron. "
                            "Tendrá que encontrarlo usted mismo...",
                        ][lang_idx],
                    )


# retrieve model specific variables from file
def load_model_vars(model_type="cls"):
    if var_cls_model.get() in none_txt and model_type == "cls":
        return {}
    model_dir = var_cls_model.get() if model_type == "cls" else var_det_model.get()
    var_file = os.path.join(
        AddaxAI_files, "models", model_type, model_dir, "variables.json"
    )
    try:
        with open(var_file, "r") as file:
            variables = json.load(file)
        return variables
    except:
        return {}


# write global variables to file
def write_global_vars(new_values=None):
    # adjust
    variables = load_global_vars()
    if new_values is not None:
        for key, value in new_values.items():
            if key in variables:
                variables[key] = value
            else:
                print(
                    f"Warning: Variable {key} not found in the loaded model variables."
                )

    # write
    var_file = os.path.join(AddaxAI_files, "AddaxAI", "global_vars.json")
    with open(var_file, "w") as file:
        json.dump(variables, file, indent=4)


# check which models are known and should be listed in the dpd
def fetch_known_models(root_dir):
    return sorted(
        [
            subdir
            for subdir in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, subdir))
        ]
    )


# convert plt graph to img via in-memory buffer
def fig2img(fig):
    import io

    buf = io.BytesIO()
    fig.savefig(buf)
    buf.seek(0)
    img = Image.open(buf)
    return img


# make piechart from results.xlsx
def create_pie_chart(file_path, looks, st_angle=45):
    # log
    print(f"EXECUTED : {sys._getframe().f_code.co_name}({locals()})\n")

    df = pd.read_excel(file_path, sheet_name="summary")
    labels = df["label"]
    detections = df["n_detections"]
    total_detections = sum(detections)
    percentages = (detections / total_detections) * 100
    rows = []
    for i in range(len(labels.values.tolist())):
        rows.append(
            [
                labels.values.tolist()[i],
                detections.values.tolist()[i],
                f"{round(percentages.values.tolist()[i], 1)}%",
            ]
        )
    _, ax = plt.subplots(
        figsize=(6, 3), subplot_kw=dict(aspect="equal"), facecolor="#CFCFCF"
    )
    wedges, _ = ax.pie(
        detections, startangle=st_angle, colors=sns.color_palette("Set2")
    )
    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    if looks != "no-lines":
        kw = dict(
            arrowprops=dict(arrowstyle="-"), bbox=bbox_props, zorder=0, va="center"
        )
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2.0 + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        if looks == "nice":
            kw["arrowprops"].update(
                {"connectionstyle": connectionstyle}
            )  # nicer, but sometimes raises bug: https://github.com/matplotlib/matplotlib/issues/12820
        elif looks == "simple":
            kw["arrowprops"].update({"arrowstyle": "-"})
        if looks != "no-lines":
            ax.annotate(
                labels[i],
                xy=(x, y),
                xytext=(1.35 * np.sign(x), 1.4 * y),
                horizontalalignment=horizontalalignment,
                **kw,
            )
    img = fig2img(plt)
    plt.close()
    return [img, rows]


# format the appropriate size unit
def format_size(size):
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024.0:
            return f"{round(size)} {unit}"
        size /= 1024.0


# function to create a dir and create a model_vars.json
# it does not yet download the model, but it will show up in the dropdown
def set_up_unknown_model(title, model_dict, model_type):
    model_dir = os.path.join(AddaxAI_files, "models", model_type, title)
    Path(model_dir).mkdir(parents=True, exist_ok=True)
    var_file = os.path.join(model_dir, "variables.json")
    with open(var_file, "w") as vars:
        json.dump(model_dict, vars, indent=2)


# check if this is the first startup since install
def is_first_startup():
    return os.path.exists(os.path.join(AddaxAI_files, "first-startup.txt"))


# remove the first startup file
def remove_first_startup_file():
    first_startup_file = os.path.join(AddaxAI_files, "first-startup.txt")
    os.remove(first_startup_file)


# read existing model info and distribute separate jsons to all models
# will only be executed once: at first startup
def distribute_individual_model_jsons(model_info_fpath):
    # log
    print(f"EXECUTED : {sys._getframe().f_code.co_name}({locals()})\n")

    model_info = json.load(open(model_info_fpath))
    for typ in ["det", "cls"]:
        model_dicts = model_info[typ]
        all_models = list(model_dicts.keys())
        for model_id in all_models:
            model_dict = model_dicts[model_id]
            set_up_unknown_model(title=model_id, model_dict=model_dict, model_type=typ)


# this function downloads a json with model info and tells the user is there is a new model
def fetch_latest_model_info():
    # log
    print(f"EXECUTED : {sys._getframe().f_code.co_name}({locals()})\n")

    # if this is the first time starting, take the existing model info file in the repo and use that
    # no need to download th same file again
    model_info_fpath = os.path.join(
        AddaxAI_files,
        "AddaxAI",
        "model_info",
        f"model_info_v{corresponding_model_info_version}.json",
    )
    if is_first_startup():
        distribute_individual_model_jsons(model_info_fpath)
        remove_first_startup_file()
        update_model_dropdowns()

    # if this is not the first startup, it should try to download the latest model json version
    # and check if there are any new models the user should know about
    else:
        start_time = time.time()
        release_info_url = (
            "https://api.github.com/repos/PetervanLunteren/AddaxAI/releases"
        )
        model_info_url = f"https://raw.githubusercontent.com/PetervanLunteren/AddaxAI/main/model_info/model_info_v{corresponding_model_info_version}.json"
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
                "Accept-Encoding": "*",
                "Connection": "keep-alive",
            }
            model_info_response = requests.get(
                model_info_url, timeout=1, headers=headers
            )
            release_info_response = requests.get(
                release_info_url, timeout=1, headers=headers
            )

            # model info
            if model_info_response.status_code == 200:
                with open(model_info_fpath, "wb") as file:
                    file.write(model_info_response.content)
                print(f"Updated model_info.json successfully.")

                # check if there is a new model available
                model_info = json.load(open(model_info_fpath))
                for typ in ["det", "cls"]:
                    model_dicts = model_info[typ]
                    all_models = list(model_dicts.keys())
                    known_models = fetch_known_models(
                        CLS_DIR if typ == "cls" else DET_DIR
                    )
                    unknown_models = [e for e in all_models if e not in known_models]

                    # show a description of all the unknown models, except if first startup
                    if unknown_models != []:
                        for model_id in unknown_models:
                            model_dict = model_dicts[model_id]
                            show_model_info(
                                title=model_id, model_dict=model_dict, new_model=True
                            )
                            set_up_unknown_model(
                                title=model_id, model_dict=model_dict, model_type=typ
                            )

            # release info
            if release_info_response.status_code == 200:
                print("Checking release info")

                # check which releases are already shown
                release_shown_json = os.path.join(
                    AddaxAI_files, "AddaxAI", "releases_shown.json"
                )
                if os.path.exists(release_shown_json):
                    with open(release_shown_json, "r") as f:
                        already_shown_releases = json.load(f)
                else:
                    already_shown_releases = []
                    with open(release_shown_json, "w") as f:
                        json.dump([], f)

                # check internet
                releases = release_info_response.json()
                release_info_list = []
                for release in releases:
                    # clean tag
                    release_str = release.get("tag_name")
                    if "v." in release_str:
                        release_str = release_str.replace("v.", "")
                    elif "v" in release_str:
                        release_str = release_str.replace("v", "")

                    # collect newer versions
                    newer_version = needs_EA_update(release_str)
                    already_shown = release_str in already_shown_releases
                    if newer_version and not already_shown:
                        print(f"Found newer version: {release_str}")
                        release_info = {
                            "tag_name_raw": release.get("tag_name"),
                            "tag_name_clean": release_str,
                            "newer_version": newer_version,
                            "name": release.get("name"),
                            "body": release.get("body"),
                            "created_at": release.get("created_at"),
                            "published_at": release.get("published_at"),
                        }
                        release_info_list.append(release_info)

                # show user
                for release_info in release_info_list:
                    show_release_info(release_info)
                    already_shown_releases.append(release_info["tag_name_clean"])

                # remember shown releases
                with open(release_shown_json, "w") as f:
                    json.dump(already_shown_releases, f)

        except requests.exceptions.Timeout:
            print("Request timed out. File download stopped.")

        except Exception as e:
            print(f"Could not update model and version info: {e}")

        # update root so that the new models show up in the dropdown menu,
        # but also the correct species for the existing models
        update_model_dropdowns()
        print(f"model info updated in {round(time.time() - start_time, 2)} seconds")


# open window with release info
def show_release_info(release):
    # define functions
    def close():
        rl_root.destroy()

    def update():
        webbrowser.open("https://addaxdatascience.com/addaxai/#install")

    # catch vars
    name_var = release["name"]
    body_var_raw = release["body"]
    date_var = datetime.datetime.strptime(
        release["published_at"], "%Y-%m-%dT%H:%M:%SZ"
    ).strftime("%B %d, %Y")

    # tidy body
    filtered_lines = [
        line for line in body_var_raw.split("\r\n") if "Full Changelog" not in line
    ]
    body_var = "\n".join(filtered_lines)

    # create window
    rl_root = customtkinter.CTkToplevel(root)
    rl_root.title("Release information")
    rl_root.geometry("+10+10")
    bring_window_to_top_but_not_for_ever(rl_root)

    # new version label
    lbl = customtkinter.CTkLabel(
        rl_root, text="New version available!", font=main_label_font
    )
    lbl.grid(
        row=0, column=0, padx=PADX, pady=(PADY, PADY / 4), columnspan=2, sticky="nswe"
    )

    # name frame
    row_idx = 1
    name_frm_1 = model_info_frame(master=rl_root)
    name_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    name_frm_2 = model_info_frame(master=name_frm_1)
    name_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    name_lbl_1 = customtkinter.CTkLabel(name_frm_1, text="Name", font=main_label_font)
    name_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    name_lbl_2 = customtkinter.CTkLabel(name_frm_2, text=name_var)
    name_lbl_2.grid(
        row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
    )

    # date frame
    row_idx += 1
    date_frm_1 = model_info_frame(master=rl_root)
    date_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    date_frm_2 = model_info_frame(master=date_frm_1)
    date_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    date_lbl_1 = customtkinter.CTkLabel(
        date_frm_1, text="Release date", font=main_label_font
    )
    date_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    date_lbl_2 = customtkinter.CTkLabel(date_frm_2, text=date_var)
    date_lbl_2.grid(
        row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
    )

    # body frame
    row_idx += 1
    body_frm_1 = model_info_frame(master=rl_root)
    body_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    body_frm_2 = model_info_frame(master=body_frm_1)
    body_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    body_lbl_1 = customtkinter.CTkLabel(
        body_frm_1, text="Description", font=main_label_font
    )
    body_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    body_txt_1 = customtkinter.CTkTextbox(
        master=body_frm_2,
        corner_radius=10,
        height=150,
        wrap="word",
        fg_color="transparent",
    )
    body_txt_1.grid(
        row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), columnspan=2, sticky="nswe"
    )
    body_txt_1.insert("0.0", body_var)
    body_txt_1.configure(state="disabled")

    # buttons frame
    row_idx += 1
    btns_frm = customtkinter.CTkFrame(master=rl_root)
    btns_frm.columnconfigure(0, weight=1, minsize=10)
    btns_frm.columnconfigure(1, weight=1, minsize=10)
    btns_frm.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    close_btn = customtkinter.CTkButton(btns_frm, text="Close", command=close)
    close_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    updat_btn = customtkinter.CTkButton(btns_frm, text="Update", command=update)
    updat_btn.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")


# check if the user needs an update
def needs_EA_update(required_version):
    current_parts = list(map(int, current_AA_version.split(".")))
    required_parts = list(map(int, required_version.split(".")))

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


# download required files for a particular model
def download_model(model_dir, skip_ask=False):
    # init vars
    model_title = os.path.basename(model_dir)
    model_type = os.path.basename(os.path.dirname(model_dir))
    model_vars = load_model_vars(model_type=model_type)
    download_info = model_vars["download_info"]
    total_download_size = model_vars["total_download_size"]

    # download
    try:
        # check if the user wants to download
        if not skip_ask:
            if not mb.askyesno(
                ["Download required", "Descarga necesaria"][lang_idx],
                [
                    f"The model {model_title} is not downloaded yet. It will take {total_download_size}"
                    f" of storage. Do you want to download?",
                    f"El modelo {model_title} aún no se ha descargado."
                    f" Ocupará {total_download_size} de almacenamiento. ¿Desea descargarlo?",
                ][lang_idx],
            ):
                return False

        # set headers to trick host to thinking we are a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive",
        }

        # some models have multiple files to be downloaded
        # check the total size first
        total_size = 0
        for download_url, _ in download_info:
            response = requests.get(
                download_url, stream=True, timeout=30, headers=headers
            )
            response.raise_for_status()
            total_size += int(response.headers.get("content-length", 0))

        # if yes, initiate download and show progress
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
        download_popup = ModelDownloadProgressWindow(
            model_title=model_title, total_size_str=format_size(total_size)
        )
        download_popup.open()
        for download_url, fname in download_info:
            file_path = os.path.join(model_dir, fname)
            response = requests.get(
                download_url, stream=True, timeout=30, headers=headers
            )
            response.raise_for_status()

            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=65536):
                    if chunk:
                        file.write(chunk)
                        progress_bar.update(len(chunk))
                        percentage_done = progress_bar.n / total_size
                        download_popup.update_progress(percentage_done)
        progress_bar.close()
        download_popup.close()
        print(f"Download successful. File saved at: {file_path}")
        return True

    # catch errors
    except Exception as error:
        print(
            "ERROR:\n"
            + str(error)
            + "\n\nDETAILS:\n"
            + str(traceback.format_exc())
            + "\n\n"
        )
        try:
            # remove incomplete download
            if os.path.isfile(file_path):
                os.remove(file_path)
        except UnboundLocalError:
            # file_path is not set, meaning there is no incomplete download
            pass
        show_download_error_window(model_title, model_dir, model_vars)


# download environment
def download_environment(env_name, model_vars, skip_ask=False):
    # download
    try:
        env_dir = os.path.join(AddaxAI_files, "envs")
        # set environment variables
        if os.name == "nt":  # windows
            download_pinned_url = f"https://addaxaipremiumstorage.blob.core.windows.net/github-zips/v{current_AA_version}/windows/envs/env-{env_name}.zip"
            download_latest_url = f"https://addaxaipremiumstorage.blob.core.windows.net/github-zips/latest/windows/envs/env-{env_name}.zip"
            filename = f"{env_name}.zip"
        elif platform.system() == "Darwin":  # macos
            import tarfile

            download_pinned_url = f"https://addaxaipremiumstorage.blob.core.windows.net/github-zips/v{current_AA_version}/macos/envs/env-{env_name}.tar.xz"
            download_latest_url = f"https://addaxaipremiumstorage.blob.core.windows.net/github-zips/latest/macos/envs/env-{env_name}.tar.xz"
            filename = f"{env_name}.tar.xz"
        else:  # linux
            return False  # linux install this during setup

        # set headers to trick host to thinking we are a browser
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
            "Accept-Encoding": "*",
            "Connection": "keep-alive",
        }

        # check the total size first
        try:
            # first try the pinned version
            total_size = 0
            response = requests.get(
                download_pinned_url, stream=True, timeout=60, headers=headers
            )
            response.raise_for_status()
            total_size += int(response.headers.get("content-length", 0))
            download_url = download_pinned_url
        except:
            # if that link doesn't woprk anymore, revert back to the latest version
            total_size = 0
            response = requests.get(
                download_latest_url, stream=True, timeout=60, headers=headers
            )
            response.raise_for_status()
            total_size += int(response.headers.get("content-length", 0))
            download_url = download_latest_url

        # check if the user wants to download
        if not skip_ask:
            if not mb.askyesno(
                ["Download required", "Descarga necesaria"][lang_idx],
                [
                    f"The model you selected needs the virtual environment '{env_name}', which is not downloaded yet. It will take {format_size(total_size)}"
                    f" of storage. Do you want to download?",
                    f"El envo {env_name} aún no se ha descargado."
                    f" Ocupará {format_size(total_size)} de almacenamiento. ¿Desea descargarlo?",
                ][lang_idx],
            ):
                return False

        # if yes, initiate download and show progress
        progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
        download_popup = EnvDownloadProgressWindow(
            env_title=env_name, total_size_str=format_size(total_size)
        )
        download_popup.open()
        file_path = os.path.join(env_dir, filename)
        response = requests.get(download_url, stream=True, timeout=60, headers=headers)
        response.raise_for_status()
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=65536):
                if chunk:
                    file.write(chunk)
                    progress_bar.update(len(chunk))
                    percentage_done = progress_bar.n / total_size
                    download_popup.update_download_progress(percentage_done)
        progress_bar.close()
        print(f"Download successful. File saved at: {file_path}")

        # After download, begin extraction
        if filename.endswith(".tar.xz"):
            # Extract the .tar.xz file
            with tarfile.open(file_path, "r:xz") as tar:
                # Get the total number of files to be extracted
                total_files = len(tar.getnames())
                extraction_progress_bar = tqdm(
                    total=total_files, unit="file", desc="Extracting"
                )

                # Extract each file and update the extraction progress
                for member in tar:
                    tar.extract(member, path=env_dir)
                    extraction_progress_bar.update(1)
                    extraction_progress_percentage = (
                        extraction_progress_bar.n / total_files
                    )
                    download_popup.update_extraction_progress(
                        extraction_progress_percentage
                    )
                extraction_progress_bar.close()
            download_popup.close()
            print(f"Extraction successful. Files extracted to: {env_dir}")

            # Remove the .tar.xz file after extraction
            try:
                os.remove(file_path)
                print(f"Removed the .tar.xz file: {file_path}")
            except Exception as e:
                print(f"Error removing file: {e}")

        if filename.endswith(".zip"):
            import zipfile

            # open the zip file for extraction
            with zipfile.ZipFile(file_path, "r") as zip_ref:
                # get the total number of files to be extracted
                total_files = len(zip_ref.namelist())
                extraction_progress_bar = tqdm(
                    total=total_files, unit="file", desc="Extracting"
                )

                # extract each file and update the extraction progress
                for member in zip_ref.namelist():
                    zip_ref.extract(member, path=env_dir)
                    extraction_progress_bar.update(1)
                    extraction_progress_percentage = (
                        extraction_progress_bar.n / total_files
                    )
                    download_popup.update_extraction_progress(
                        extraction_progress_percentage
                    )
                extraction_progress_bar.close()
            download_popup.close()
            print(f"Extraction successful. Files extracted to: {env_dir}")

            # Remove the zip file after extraction
            try:
                os.remove(file_path)
                print(f"Removed the zip file: {file_path}")
            except Exception as e:
                print(f"Error removing file: {e}")

        # return success
        return True

    # catch errors
    except Exception as error:
        print(
            "ERROR:\n"
            + str(error)
            + "\n\nDETAILS:\n"
            + str(traceback.format_exc())
            + "\n\n"
        )
        try:
            # remove incomplete archive
            if os.path.isfile(file_path):
                os.remove(file_path)

            # remove incomplete extracted dir
            extracted_dir = os.path.join(env_dir, f"env-{env_name}")
            if os.path.isdir(extracted_dir):
                shutil.rmtree(extracted_dir)

            # close popup
            download_popup.close()

        except UnboundLocalError:
            # file_path is not set, meaning there is no incomplete download
            pass

        # show internet options
        show_download_error_window_env(env_name, env_dir, model_vars)
