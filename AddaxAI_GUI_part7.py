def sponsor_project():
    webbrowser.open("https://addaxdatascience.com/addaxai/#donate")


class GreyTopButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=(yellow_secondary, "#333333"),
            hover_color=(yellow_tertiary, "#2B2B2B"),
            text_color=("black", "white"),
            height=10,
            width=140,
            border_width=GREY_BUTTON_BORDER_WIDTH,
        )


def reset_values():
    # set values
    var_thresh.set(global_vars["var_thresh_default"])
    var_det_model_path.set("")
    var_det_model_short.set("")
    var_exclude_subs.set(False)
    var_use_custom_img_size_for_deploy.set(False)
    var_image_size_for_deploy.set("")
    var_abs_paths.set(False)
    var_disable_GPU.set(False)
    var_process_img.set(False)
    var_use_checkpnts.set(False)
    var_checkpoint_freq.set("")
    var_cont_checkpnt.set(False)
    var_process_vid.set(False)
    var_not_all_frames.set(True)
    var_nth_frame.set("1")
    var_separate_files.set(False)
    var_file_placement.set(2)
    var_sep_conf.set(False)
    var_vis_files.set(False)
    var_vis_size.set(dpd_options_vis_size[lang_idx][global_vars["var_vis_size_idx"]])
    var_vis_bbox.set(False)
    var_vis_blur.set(False)
    var_crp_files.set(False)
    var_exp.set(True)
    var_exp_format.set(
        dpd_options_exp_format[lang_idx][global_vars["var_exp_format_idx"]]
    )

    write_global_vars(
        {
            "var_det_model_idx": dpd_options_model[lang_idx].index(var_det_model.get()),
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
            "var_separate_files": var_separate_files.get(),
            "var_file_placement": var_file_placement.get(),
            "var_sep_conf": var_sep_conf.get(),
            "var_vis_files": var_vis_files.get(),
            "var_vis_size_idx": dpd_options_vis_size[lang_idx].index(
                var_vis_size.get()
            ),
            "var_vis_bbox": var_vis_bbox.get(),
            "var_vis_blur": var_vis_blur.get(),
            "var_crp_files": var_crp_files.get(),
            "var_exp": var_exp.get(),
            "var_exp_format_idx": dpd_options_exp_format[lang_idx].index(
                var_exp_format.get()
            ),
        }
    )

    # reset model specific variables
    model_vars = load_model_vars()
    if model_vars != {}:
        # select all classes
        selected_classes = model_vars["all_classes"]
        write_model_vars(new_values={"selected_classes": selected_classes})
        model_cls_animal_options(var_cls_model.get())

        # set model specific thresholds
        var_cls_detec_thresh.set(model_vars["var_cls_detec_thresh_default"])
        var_cls_class_thresh.set(model_vars["var_cls_class_thresh_default"])
        write_model_vars(
            new_values={
                "var_cls_detec_thresh": str(var_cls_detec_thresh.get()),
                "var_cls_class_thresh": str(var_cls_class_thresh.get()),
            }
        )

    # update window
    toggle_cls_frame()
    toggle_img_frame()
    toggle_nth_frame()
    toggle_vid_frame()
    toggle_exp_frame()
    toggle_vis_frame()
    toggle_sep_frame()
    toggle_image_size_for_deploy()
    resize_canvas_to_content()


##########################################
############# TKINTER WINDOW #############
##########################################

# make it look similar on different systems
if os.name == "nt":  # windows
    text_font = "TkDefaultFont"
    resize_img_factor = 0.95
    text_size_adjustment_factor = 0.83
    first_level_frame_font_size = 13
    second_level_frame_font_size = 10
    label_width = 320 * scale_factor
    widget_width = 225 * scale_factor
    frame_width = label_width + widget_width + 60
    subframe_correction_factor = 15
    minsize_rows = 28 * scale_factor
    explanation_text_box_height_factor = 0.8
    PADY = 8
    PADX = 10
    ICON_SIZE = 35
    LOGO_WIDTH = 135
    LOGO_HEIGHT = 50
    ADV_WINDOW_WIDTH = 1194
    SIM_WINDOW_WIDTH = 630
    SIM_WINDOW_HEIGHT = 699
    ADV_EXTRA_GRADIENT_HEIGHT = 98 * scale_factor
    ADV_TOP_BANNER_WIDTH_FACTOR = 17.4
    SIM_TOP_BANNER_WIDTH_FACTOR = 6
    RESULTS_TABLE_WIDTH = 600
    RESULTS_WINDOW_WIDTH = 803
    RESULTS_WINDOW_HEIGHT = 700
    ADDAX_TXT_SIZE = 8
    GREY_BUTTON_BORDER_WIDTH = 0
elif sys.platform == "linux" or sys.platform == "linux2":  # linux
    text_font = "Times"
    resize_img_factor = 1
    text_size_adjustment_factor = 0.7
    first_level_frame_font_size = 13
    second_level_frame_font_size = 10
    label_width = 320
    widget_width = 225
    frame_width = label_width + widget_width + 60
    subframe_correction_factor = 15
    minsize_rows = 28
    explanation_text_box_height_factor = 1
    PADY = 8
    PADX = 10
    ICON_SIZE = 35
    LOGO_WIDTH = 135
    LOGO_HEIGHT = 50
    ADV_WINDOW_WIDTH = 1194
    SIM_WINDOW_WIDTH = 630
    SIM_WINDOW_HEIGHT = 683
    ADV_EXTRA_GRADIENT_HEIGHT = 90
    ADV_TOP_BANNER_WIDTH_FACTOR = 17.4
    SIM_TOP_BANNER_WIDTH_FACTOR = 6
    RESULTS_TABLE_WIDTH = 600
    RESULTS_WINDOW_WIDTH = 803
    RESULTS_WINDOW_HEIGHT = 700
    ADDAX_TXT_SIZE = 8
    GREY_BUTTON_BORDER_WIDTH = 1
else:  # macOS
    text_font = "TkDefaultFont"
    resize_img_factor = 1
    text_size_adjustment_factor = 1
    first_level_frame_font_size = 15
    second_level_frame_font_size = 13
    label_width = 350
    widget_width = 170
    frame_width = label_width + widget_width + 50
    subframe_correction_factor = 15
    minsize_rows = 28
    explanation_text_box_height_factor = 1
    PADY = 8
    PADX = 10
    ICON_SIZE = 35
    LOGO_WIDTH = 135
    LOGO_HEIGHT = 50
    ADV_WINDOW_WIDTH = 1194
    SIM_WINDOW_WIDTH = 630
    SIM_WINDOW_HEIGHT = 696
    ADV_EXTRA_GRADIENT_HEIGHT = 130
    ADV_TOP_BANNER_WIDTH_FACTOR = 23.2
    SIM_TOP_BANNER_WIDTH_FACTOR = 6
    RESULTS_TABLE_WIDTH = 600
    RESULTS_WINDOW_WIDTH = 803
    RESULTS_WINDOW_HEIGHT = 700
    ADDAX_TXT_SIZE = 9
    GREY_BUTTON_BORDER_WIDTH = 0

# TKINTER MAIN WINDOW
root = customtkinter.CTk()
AddaxAI_icon_image = tk.PhotoImage(
    file=os.path.join(AddaxAI_files, "AddaxAI", "imgs", "square_logo_excl_text.png")
)
root.iconphoto(True, AddaxAI_icon_image)
root.withdraw()
main_label_font = customtkinter.CTkFont(family="CTkFont", size=14, weight="bold")
url_label_font = customtkinter.CTkFont(family="CTkFont", underline=True)
italic_label_font = customtkinter.CTkFont(family="CTkFont", size=14, slant="italic")

# set the global appearance for the app
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme(
    os.path.join(AddaxAI_files, "AddaxAI", "themes", "addaxai.json")
)

# ADVANCED MODE WINDOW
advanc_mode_win = customtkinter.CTkToplevel(root)
advanc_mode_win.title(f"AddaxAI v{current_AA_version} - Advanced mode")
advanc_mode_win.geometry("+20+20")
advanc_mode_win.protocol("WM_DELETE_WINDOW", on_toplevel_close)
advanc_bg_image = customtkinter.CTkImage(PIL_sidebar, size=(ADV_WINDOW_WIDTH, 10))
advanc_bg_image_label = customtkinter.CTkLabel(advanc_mode_win, image=advanc_bg_image)
advanc_bg_image_label.grid(row=0, column=0)
advanc_main_frame = customtkinter.CTkFrame(
    advanc_mode_win, corner_radius=0, fg_color="transparent", bg_color=yellow_primary
)
advanc_main_frame.grid(row=0, column=0, sticky="ns")
if scale_factor != 1.0:  # set fixed width for when scaling is applied
    tabControl = ttk.Notebook(advanc_main_frame, width=int(1150 * scale_factor))
else:
    tabControl = ttk.Notebook(advanc_main_frame)
advanc_mode_win.withdraw()  # only show when all widgets are loaded

# logo
logoImage = customtkinter.CTkImage(PIL_logo_incl_text, size=(LOGO_WIDTH, LOGO_HEIGHT))
customtkinter.CTkLabel(advanc_main_frame, text="", image=logoImage).grid(
    column=0, row=0, columnspan=2, sticky="", pady=(PADY, 0), padx=0
)
adv_top_banner = customtkinter.CTkImage(
    PIL_logo_incl_text, size=(LOGO_WIDTH, LOGO_HEIGHT)
)
customtkinter.CTkLabel(advanc_main_frame, text="", image=adv_top_banner).grid(
    column=0, row=0, columnspan=2, sticky="ew", pady=(PADY, 0), padx=0
)
adv_spacer_top = customtkinter.CTkFrame(
    advanc_main_frame, height=PADY, fg_color=yellow_primary
)
adv_spacer_top.grid(column=0, row=1, columnspan=2, sticky="ew")
adv_spacer_bottom = customtkinter.CTkFrame(
    advanc_main_frame, height=PADY, fg_color=yellow_primary
)
adv_spacer_bottom.grid(column=0, row=5, columnspan=2, sticky="ew")

# prepare check mark for later use
check_mark_one_row = PIL_checkmark.resize((20, 20), Image.Resampling.LANCZOS)
check_mark_one_row = ImageTk.PhotoImage(check_mark_one_row)
check_mark_two_rows = PIL_checkmark.resize((45, 45), Image.Resampling.LANCZOS)
check_mark_two_rows = ImageTk.PhotoImage(check_mark_two_rows)

# grey top buttons
adv_btn_switch_mode_txt = ["To simple mode", "Al modo simple"]
adv_btn_switch_mode = GreyTopButton(
    master=advanc_main_frame,
    text=adv_btn_switch_mode_txt[lang_idx],
    command=switch_mode,
)
adv_btn_switch_mode.grid(
    row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan=2, sticky="nw"
)
adv_btn_switch_lang = GreyTopButton(
    master=advanc_main_frame, text="Switch language", command=set_language
)
adv_btn_switch_lang.grid(
    row=0, column=0, padx=PADX, pady=(0, 0), columnspan=2, sticky="sw"
)
adv_btn_sponsor_txt = ["Sponsor project", "Patrocine proyecto"]
adv_btn_sponsor = GreyTopButton(
    master=advanc_main_frame,
    text=adv_btn_sponsor_txt[lang_idx],
    command=sponsor_project,
)
adv_btn_sponsor.grid(
    row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan=2, sticky="ne"
)
adv_btn_reset_values_txt = ["Reset values", "Restablecer valores"]
adv_btn_reset_values = GreyTopButton(
    master=advanc_main_frame,
    text=adv_btn_reset_values_txt[lang_idx],
    command=reset_values,
)
adv_btn_reset_values.grid(
    row=0, column=0, padx=PADX, pady=(0, 0), columnspan=2, sticky="se"
)

# about
adv_abo_lbl_txt = [
    "By Addax Data Science. More conservation technology? Visit",
    "Creado por Addax Data Science. ¿Más tecnología de conservación? Visite",
]
adv_abo_lbl = tk.Label(
    advanc_main_frame,
    text=adv_abo_lbl_txt[lang_idx],
    font=Font(size=ADDAX_TXT_SIZE),
    fg="black",
    bg=yellow_primary,
)
adv_abo_lbl.grid(row=6, column=0, columnspan=2, sticky="")
adv_abo_lbl_link = tk.Label(
    advanc_main_frame,
    text="addaxdatascience.com",
    cursor="hand2",
    font=Font(size=ADDAX_TXT_SIZE, underline=1),
    fg=green_primary,
    bg=yellow_primary,
)
adv_abo_lbl_link.grid(row=7, column=0, columnspan=2, sticky="", pady=(0, PADY))
adv_abo_lbl_link.bind("<Button-1>", lambda e: callback("http://addaxdatascience.com"))

# deploy tab
deploy_tab = ttk.Frame(tabControl)
deploy_tab.columnconfigure(0, weight=1, minsize=frame_width)
deploy_tab.columnconfigure(1, weight=1, minsize=frame_width)
deploy_tab_text = ["Deploy", "Despliegue"]
tabControl.add(deploy_tab, text=deploy_tab_text[lang_idx])
deploy_canvas = tk.Canvas(deploy_tab)
deploy_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
deploy_y_scrollbar = ttk.Scrollbar(
    deploy_tab, orient=tk.VERTICAL, command=deploy_canvas.yview
)
deploy_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
deploy_canvas.configure(yscrollcommand=deploy_y_scrollbar.set)
deploy_scrollable_frame = ttk.Frame(deploy_canvas)
deploy_canvas.create_window((0, 0), window=deploy_scrollable_frame, anchor="nw")
deploy_scrollable_frame.bind(
    "<Configure>",
    lambda event: deploy_canvas.configure(scrollregion=deploy_canvas.bbox("all")),
)

# help tab
help_tab = ttk.Frame(tabControl)
help_tab_text = ["Help", "Ayuda"]
tabControl.add(help_tab, text=help_tab_text[lang_idx])

# about tab
about_tab = ttk.Frame(tabControl)
about_tab_text = ["About", "Acerca de"]
tabControl.add(about_tab, text=about_tab_text[lang_idx])

# grid
tabControl.grid(column=0, row=2, sticky="ns", pady=0)

#### deploy tab
### first step
fst_step_txt = ["Step 1: Select folder", "Paso 1: Seleccione carpeta"]
row_fst_step = 1
fst_step = LabelFrame(
    deploy_scrollable_frame,
    text=" " + fst_step_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    fg=green_primary,
    borderwidth=2,
)
fst_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
fst_step.grid(column=0, row=row_fst_step, columnspan=1, sticky="ew")
fst_step.columnconfigure(0, weight=1, minsize=label_width)
fst_step.columnconfigure(1, weight=1, minsize=widget_width)

# choose folder
lbl_choose_folder_txt = ["Source folder", "Carpeta de origen"]
row_choose_folder = 0
lbl_choose_folder = Label(
    master=fst_step, text=lbl_choose_folder_txt[lang_idx], width=1, anchor="w"
)
lbl_choose_folder.grid(row=row_choose_folder, sticky="nesw", pady=2)
var_choose_folder = StringVar()
var_choose_folder.set("")
var_choose_folder_short = StringVar()
dsp_choose_folder = Label(
    master=fst_step, textvariable=var_choose_folder_short, fg="grey", padx=5
)
btn_choose_folder = Button(
    master=fst_step,
    text=browse_txt[lang_idx],
    width=1,
    command=lambda: [
        browse_dir(
            var_choose_folder,
            var_choose_folder_short,
            dsp_choose_folder,
            25,
            row_choose_folder,
            0,
            "w",
            source_dir=True,
        ),
        update_frame_states(),
    ],
)
btn_choose_folder.grid(row=row_choose_folder, column=1, sticky="nesw", padx=5)

### second step
snd_step_txt = ["Step 2: Analysis", "Paso 2: Análisis"]
row_snd_step = 2
snd_step = LabelFrame(
    deploy_scrollable_frame,
    text=" " + snd_step_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    fg=green_primary,
    borderwidth=2,
)
snd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
snd_step.grid(column=0, row=row_snd_step, sticky="nesw")
snd_step.columnconfigure(0, weight=1, minsize=label_width)
snd_step.columnconfigure(1, weight=1, minsize=widget_width)

# check which detectors are installed
det_models = fetch_known_models(DET_DIR)
dpd_options_model = [det_models + ["Custom model"], det_models + ["Otro modelo"]]

# choose detector
lbl_model_txt = [
    "Model to detect animals, vehicles, and persons",
    "Modelo para detectar animales, vehículos y personas",
]
row_model = 0
lbl_model = Label(master=snd_step, text=lbl_model_txt[lang_idx], width=1, anchor="w")
lbl_model.grid(row=row_model, sticky="nesw", pady=2)
var_det_model = StringVar(snd_step)
var_det_model.set(
    dpd_options_model[lang_idx][global_vars["var_det_model_idx"]]
)  # take idx instead of string
var_det_model_short = StringVar()
var_det_model_short.set(global_vars["var_det_model_short"])
var_det_model_path = StringVar()
var_det_model_path.set(global_vars["var_det_model_path"])
dpd_model = OptionMenu(
    snd_step, var_det_model, *dpd_options_model[lang_idx], command=model_options
)
dpd_model.configure(width=1)
dpd_model.grid(row=row_model, column=1, sticky="nesw", padx=5)
dsp_model = Label(master=snd_step, textvariable=var_det_model_short, fg=green_primary)
if var_det_model_short.get() != "":
    dsp_model.grid(column=0, row=row_model, sticky="e")

# check if user has classifiers installed
cls_models = fetch_known_models(CLS_DIR)
dpd_options_cls_model = [["None"] + cls_models, ["Ninguno"] + cls_models]

# use classifier
lbl_cls_model_txt = [
    "Model to further identify animals",
    "Modelo para identificar mejor a los animales",
]
row_cls_model = 1
lbl_cls_model = Label(snd_step, text=lbl_cls_model_txt[lang_idx], width=1, anchor="w")
lbl_cls_model.grid(row=row_cls_model, sticky="nesw", pady=2)
var_cls_model = StringVar(snd_step)
var_cls_model.set(
    dpd_options_cls_model[lang_idx][global_vars["var_cls_model_idx"]]
)  # take idx instead of string
dpd_cls_model = OptionMenu(
    snd_step,
    var_cls_model,
    *dpd_options_cls_model[lang_idx],
    command=model_cls_animal_options,
)
dpd_cls_model.configure(width=1, state=DISABLED)
dpd_cls_model.grid(row=row_cls_model, column=1, sticky="nesw", padx=5, pady=2)

# set global model vars for startup
model_vars = load_model_vars()

## classification option frame (hidden by default)
cls_frame_txt = ["Identification options", "Opciones de identificación"]
cls_frame_row = 2
cls_frame = LabelFrame(
    snd_step,
    text=" ↳ " + cls_frame_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    borderwidth=1,
    fg="black",
)
cls_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
cls_frame.grid(row=cls_frame_row, column=0, columnspan=2, sticky="ew")
cls_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
cls_frame.columnconfigure(
    1, weight=1, minsize=widget_width - subframe_correction_factor
)
cls_frame.grid_forget()

# show model info
row_btn_model_info = 1
lbl_model_info_txt = [
    "Show model information",
    "Mostrar información del modelo (inglés)",
]
row_model_info = 0
lbl_model_info = Label(
    master=cls_frame, text="     " + lbl_model_info_txt[lang_idx], width=1, anchor="w"
)
lbl_model_info.grid(row=row_model_info, sticky="nesw", pady=2)
btn_model_info = Button(
    master=cls_frame, text=show_txt[lang_idx], width=1, command=show_model_info
)
btn_model_info.grid(row=row_model_info, column=1, sticky="nesw", padx=5)

# choose classes
lbl_choose_classes_txt = ["Select species", "Seleccionar especies"]
row_choose_classes = 1
lbl_choose_classes = Label(
    master=cls_frame,
    text="     " + lbl_choose_classes_txt[lang_idx],
    width=1,
    anchor="w",
)
lbl_choose_classes.grid(row=row_choose_classes, sticky="nesw", pady=2)
btn_choose_classes = Button(
    master=cls_frame, text=select_txt[lang_idx], width=1, command=open_species_selection
)
btn_choose_classes.grid(row=row_choose_classes, column=1, sticky="nesw", padx=5)
if var_cls_model.get() not in none_txt:
    dsp_choose_classes = Label(
        cls_frame,
        text=f"{len(model_vars.get('selected_classes', []))} of {len(model_vars.get('all_classes', []))}",
    )
else:
    dsp_choose_classes = Label(cls_frame, text="")
dsp_choose_classes.grid(row=row_choose_classes, column=0, sticky="e", padx=0)
dsp_choose_classes.configure(fg=green_primary)

# threshold to classify detections
lbl_cls_detec_thresh_txt = [
    "Detection confidence threshold",
    "Umbral de confianza de detección",
]
row_cls_detec_thresh = 2
lbl_cls_detec_thresh = Label(
    cls_frame, text="     " + lbl_cls_detec_thresh_txt[lang_idx], width=1, anchor="w"
)
lbl_cls_detec_thresh.grid(row=row_cls_detec_thresh, sticky="nesw", pady=2)
var_cls_detec_thresh = DoubleVar()
var_cls_detec_thresh.set(model_vars.get("var_cls_detec_thresh", 0.6))
scl_cls_detec_thresh = Scale(
    cls_frame,
    from_=0.01,
    to=1,
    resolution=0.01,
    orient=HORIZONTAL,
    variable=var_cls_detec_thresh,
    showvalue=0,
    width=10,
    length=1,
    state=DISABLED,
    command=lambda value: write_model_vars(
        new_values={"var_cls_detec_thresh": str(value)}
    ),
)
scl_cls_detec_thresh.grid(row=row_cls_detec_thresh, column=1, sticky="ew", padx=10)
dsp_cls_detec_thresh = Label(cls_frame, textvariable=var_cls_detec_thresh)
dsp_cls_detec_thresh.grid(row=row_cls_detec_thresh, column=0, sticky="e", padx=0)
dsp_cls_detec_thresh.configure(fg=green_primary)

# threshold accept identifications
lbl_cls_class_thresh_txt = [
    "Classification confidence threshold",
    "Umbral de confianza de la clasificación",
]
row_cls_class_thresh = 3
lbl_cls_class_thresh = Label(
    cls_frame, text="     " + lbl_cls_class_thresh_txt[lang_idx], width=1, anchor="w"
)
lbl_cls_class_thresh.grid(row=row_cls_class_thresh, sticky="nesw", pady=2)
var_cls_class_thresh = DoubleVar()
var_cls_class_thresh.set(model_vars.get("var_cls_class_thresh", 0.5))
scl_cls_class_thresh = Scale(
    cls_frame,
    from_=0.01,
    to=1,
    resolution=0.01,
    orient=HORIZONTAL,
    variable=var_cls_class_thresh,
    showvalue=0,
    width=10,
    length=1,
    state=DISABLED,
    command=lambda value: write_model_vars(new_values={"var_cls_class_thresh": value}),
)
scl_cls_class_thresh.grid(row=row_cls_class_thresh, column=1, sticky="ew", padx=10)
dsp_cls_class_thresh = Label(cls_frame, textvariable=var_cls_class_thresh)
dsp_cls_class_thresh.grid(row=row_cls_class_thresh, column=0, sticky="e", padx=0)
dsp_cls_class_thresh.configure(fg=green_primary)

# Smoothen results
lbl_smooth_cls_animal_txt = [
    "Smooth confidence scores per sequence",
    "Suavizar puntuaciones por secuencia",
]
row_smooth_cls_animal = 4
lbl_smooth_cls_animal = Label(
    cls_frame, text="     " + lbl_smooth_cls_animal_txt[lang_idx], width=1, anchor="w"
)
lbl_smooth_cls_animal.grid(row=row_smooth_cls_animal, sticky="nesw", pady=2)
var_smooth_cls_animal = BooleanVar()
var_smooth_cls_animal.set(model_vars.get("var_smooth_cls_animal", False))
chb_smooth_cls_animal = Checkbutton(
    cls_frame,
    variable=var_smooth_cls_animal,
    anchor="w",
    command=on_chb_smooth_cls_animal_change,
)
chb_smooth_cls_animal.grid(row=row_smooth_cls_animal, column=1, sticky="nesw", padx=5)

# choose location for species net
lbl_sppnet_location_txt = ["Location", "Ubicación"]
row_sppnet_location = 1
lbl_sppnet_location = Label(
    master=cls_frame,
    text="     " + lbl_sppnet_location_txt[lang_idx],
    width=1,
    anchor="w",
)
lbl_sppnet_location.grid(row=row_sppnet_location, sticky="nesw", pady=2)
var_sppnet_location = StringVar(cls_frame)
var_sppnet_location.set(
    dpd_options_sppnet_location[lang_idx][global_vars["var_sppnet_location_idx"]]
)  # take idx instead of string
dpd_sppnet_location = OptionMenu(
    cls_frame, var_sppnet_location, *dpd_options_sppnet_location[lang_idx]
)
dpd_sppnet_location.configure(width=1, state=DISABLED)
# dpd_sppnet_location.grid(row=row_sppnet_location, column=1, sticky='nesw', padx=5, pady=2) # dont grid this by default

# include subdirectories
lbl_exclude_subs_txt = ["Don't process subdirectories", "No procesar subcarpetas"]
row_exclude_subs = 3
lbl_exclude_subs = Label(
    snd_step, text=lbl_exclude_subs_txt[lang_idx], width=1, anchor="w"
)
lbl_exclude_subs.grid(row=row_exclude_subs, sticky="nesw", pady=2)
var_exclude_subs = BooleanVar()
var_exclude_subs.set(global_vars["var_exclude_subs"])
chb_exclude_subs = Checkbutton(snd_step, variable=var_exclude_subs, anchor="w")
chb_exclude_subs.grid(row=row_exclude_subs, column=1, sticky="nesw", padx=5)

# use custom image size
lbl_use_custom_img_size_for_deploy_txt = [
    "Use custom image size",
    "Usar tamaño de imagen personalizado",
]
row_use_custom_img_size_for_deploy = 4
lbl_use_custom_img_size_for_deploy = Label(
    snd_step, text=lbl_use_custom_img_size_for_deploy_txt[lang_idx], width=1, anchor="w"
)
lbl_use_custom_img_size_for_deploy.grid(
    row=row_use_custom_img_size_for_deploy, sticky="nesw", pady=2
)
var_use_custom_img_size_for_deploy = BooleanVar()
var_use_custom_img_size_for_deploy.set(
    global_vars["var_use_custom_img_size_for_deploy"]
)
chb_use_custom_img_size_for_deploy = Checkbutton(
    snd_step,
    variable=var_use_custom_img_size_for_deploy,
    command=toggle_image_size_for_deploy,
    anchor="w",
)
chb_use_custom_img_size_for_deploy.grid(
    row=row_use_custom_img_size_for_deploy, column=1, sticky="nesw", padx=5
)

# specify custom image size (not grid by default)
lbl_image_size_for_deploy_txt = ["Image size", "Tamaño imagen"]
row_image_size_for_deploy = 5
lbl_image_size_for_deploy = Label(
    snd_step, text=" ↳ " + lbl_image_size_for_deploy_txt[lang_idx], width=1, anchor="w"
)
var_image_size_for_deploy = StringVar()
var_image_size_for_deploy.set(global_vars["var_image_size_for_deploy"])
ent_image_size_for_deploy = tk.Entry(
    snd_step, textvariable=var_image_size_for_deploy, fg="grey", state=NORMAL, width=1
)
if var_image_size_for_deploy.get() == "":
    ent_image_size_for_deploy.insert(0, f"{eg_txt[lang_idx]}: 640")
else:
    ent_image_size_for_deploy.configure(fg="black")
ent_image_size_for_deploy.bind("<FocusIn>", image_size_for_deploy_focus_in)
ent_image_size_for_deploy.configure(state=DISABLED)

# use absolute paths
lbl_abs_paths_txt = [
    "Use absolute paths in output file",
    "Usar rutas absolutas en archivo de salida",
]
row_abs_path = 6
lbl_abs_paths = Label(snd_step, text=lbl_abs_paths_txt[lang_idx], width=1, anchor="w")
lbl_abs_paths.grid(row=row_abs_path, sticky="nesw", pady=2)
var_abs_paths = BooleanVar()
var_abs_paths.set(global_vars["var_abs_paths"])
chb_abs_paths = Checkbutton(
    snd_step, variable=var_abs_paths, command=abs_paths_warning, anchor="w"
)
chb_abs_paths.grid(row=row_abs_path, column=1, sticky="nesw", padx=5)

# use absolute paths
lbl_disable_GPU_txt = [
    "Disable GPU processing",
    "Desactivar el procesamiento en la GPU",
]
row_disable_GPU = 7
lbl_disable_GPU = Label(
    snd_step, text=lbl_disable_GPU_txt[lang_idx], width=1, anchor="w"
)
lbl_disable_GPU.grid(row=row_disable_GPU, sticky="nesw", pady=2)
var_disable_GPU = BooleanVar()
var_disable_GPU.set(global_vars["var_disable_GPU"])
chb_disable_GPU = Checkbutton(snd_step, variable=var_disable_GPU, anchor="w")
chb_disable_GPU.grid(row=row_disable_GPU, column=1, sticky="nesw", padx=5)

# process images
lbl_process_img_txt = [
    "Process images, if present",
    "Si está presente, procesa todas las imágenes",
]
row_process_img = 8
lbl_process_img = Label(
    snd_step, text=lbl_process_img_txt[lang_idx], width=1, anchor="w"
)
lbl_process_img.grid(row=row_process_img, sticky="nesw", pady=2)
var_process_img = BooleanVar()
var_process_img.set(global_vars["var_process_img"])
chb_process_img = Checkbutton(
    snd_step, variable=var_process_img, command=toggle_img_frame, anchor="w"
)
chb_process_img.grid(row=row_process_img, column=1, sticky="nesw", padx=5)

## image option frame (hidden by default)
img_frame_txt = ["Image options", "Opciones de imagen"]
img_frame_row = 9
img_frame = LabelFrame(
    snd_step,
    text=" ↳ " + img_frame_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    borderwidth=1,
    fg="grey80",
)
img_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
img_frame.grid(row=img_frame_row, column=0, columnspan=2, sticky="ew")
img_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
img_frame.columnconfigure(
    1, weight=1, minsize=widget_width - subframe_correction_factor
)
img_frame.grid_forget()

# use checkpoints
lbl_use_checkpnts_txt = [
    "Use checkpoints while running",
    "Usar puntos de control mientras se ejecuta",
]
row_use_checkpnts = 0
lbl_use_checkpnts = Label(
    img_frame,
    text="     " + lbl_use_checkpnts_txt[lang_idx],
    pady=2,
    state=DISABLED,
    width=1,
    anchor="w",
)
lbl_use_checkpnts.grid(row=row_use_checkpnts, sticky="nesw")
var_use_checkpnts = BooleanVar()
var_use_checkpnts.set(global_vars["var_use_checkpnts"])
chb_use_checkpnts = Checkbutton(
    img_frame,
    variable=var_use_checkpnts,
    command=toggle_checkpoint_freq,
    state=DISABLED,
    anchor="w",
)
chb_use_checkpnts.grid(row=row_use_checkpnts, column=1, sticky="nesw", padx=5)

# checkpoint frequency
lbl_checkpoint_freq_txt = ["Checkpoint frequency", "Frecuencia puntos de control"]
row_checkpoint_freq = 1
lbl_checkpoint_freq = tk.Label(
    img_frame,
    text="        ↳ " + lbl_checkpoint_freq_txt[lang_idx],
    pady=2,
    state=DISABLED,
    width=1,
    anchor="w",
)
lbl_checkpoint_freq.grid(row=row_checkpoint_freq, sticky="nesw")
var_checkpoint_freq = StringVar()
var_checkpoint_freq.set(global_vars["var_checkpoint_freq"])
ent_checkpoint_freq = tk.Entry(
    img_frame, textvariable=var_checkpoint_freq, fg="grey", state=NORMAL, width=1
)
ent_checkpoint_freq.grid(row=row_checkpoint_freq, column=1, sticky="nesw", padx=5)
if var_checkpoint_freq.get() == "":
    ent_checkpoint_freq.insert(0, f"{eg_txt[lang_idx]}: 10000")
else:
    ent_checkpoint_freq.configure(fg="black")
ent_checkpoint_freq.bind("<FocusIn>", checkpoint_freq_focus_in)
ent_checkpoint_freq.configure(state=DISABLED)

# continue from checkpoint file
lbl_cont_checkpnt_txt = [
    "Continue from last checkpoint file",
    "Continuar desde el último punto de control",
]
row_cont_checkpnt = 2
lbl_cont_checkpnt = Label(
    img_frame,
    text="     " + lbl_cont_checkpnt_txt[lang_idx],
    pady=2,
    state=DISABLED,
    width=1,
    anchor="w",
)
lbl_cont_checkpnt.grid(row=row_cont_checkpnt, sticky="nesw")
var_cont_checkpnt = BooleanVar()
var_cont_checkpnt.set(global_vars["var_cont_checkpnt"])
chb_cont_checkpnt = Checkbutton(
    img_frame,
    variable=var_cont_checkpnt,
    state=DISABLED,
    command=disable_chb_cont_checkpnt,
    anchor="w",
)
chb_cont_checkpnt.grid(row=row_cont_checkpnt, column=1, sticky="nesw", padx=5)

# process videos
lbl_process_vid_txt = [
    "Process videos, if present",
    "Si está presente, procesa todos los vídeos",
]
row_process_vid = 10
lbl_process_vid = Label(
    snd_step, text=lbl_process_vid_txt[lang_idx], width=1, anchor="w"
)
lbl_process_vid.grid(row=row_process_vid, sticky="nesw", pady=2)
var_process_vid = BooleanVar()
var_process_vid.set(global_vars["var_process_vid"])
chb_process_vid = Checkbutton(
    snd_step, variable=var_process_vid, command=toggle_vid_frame, anchor="w"
)
chb_process_vid.grid(row=row_process_vid, column=1, sticky="nesw", padx=5)

## video option frame (disabled by default)
vid_frame_txt = ["Video options", "Opciones de vídeo"]
vid_frame_row = 11
vid_frame = LabelFrame(
    snd_step,
    text=" ↳ " + vid_frame_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    borderwidth=1,
    fg="grey80",
)
vid_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
vid_frame.grid(row=vid_frame_row, column=0, columnspan=2, sticky="ew")
vid_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
vid_frame.columnconfigure(
    1, weight=1, minsize=widget_width - subframe_correction_factor
)
vid_frame.grid_forget()

# dont process all frames
lbl_not_all_frames_txt = ["Don't process every frame", "No procesar cada fotograma"]
row_not_all_frames = 0
lbl_not_all_frames = Label(
    vid_frame,
    text="     " + lbl_not_all_frames_txt[lang_idx],
    pady=2,
    state=DISABLED,
    width=1,
    anchor="w",
)
lbl_not_all_frames.grid(row=row_not_all_frames, sticky="nesw")
var_not_all_frames = BooleanVar()
var_not_all_frames.set(global_vars["var_not_all_frames"])
chb_not_all_frames = Checkbutton(
    vid_frame,
    variable=var_not_all_frames,
    command=toggle_nth_frame,
    state=DISABLED,
    anchor="w",
)
chb_not_all_frames.grid(row=row_not_all_frames, column=1, sticky="nesw", padx=5)

# process every nth frame
lbl_nth_frame_txt = [
    "Sample frames every N seconds",
    "Muestreo de tramas cada N segundos",
]
row_nth_frame = 1
lbl_nth_frame = tk.Label(
    vid_frame,
    text="        ↳ " + lbl_nth_frame_txt[lang_idx],
    pady=2,
    state=DISABLED,
    width=1,
    anchor="w",
)
lbl_nth_frame.grid(row=row_nth_frame, sticky="nesw")
var_nth_frame = StringVar()
var_nth_frame.set(global_vars["var_nth_frame"])
ent_nth_frame = tk.Entry(
    vid_frame,
    textvariable=var_nth_frame,
    fg="grey" if var_nth_frame.get().isdecimal() else "black",
    state=NORMAL,
    width=1,
)
ent_nth_frame.grid(row=row_nth_frame, column=1, sticky="nesw", padx=5)
if var_nth_frame.get() == "":
    ent_nth_frame.insert(0, f"{eg_txt[lang_idx]}: 1")
    ent_nth_frame.configure(fg="grey")
else:
    ent_nth_frame.configure(fg="black")
ent_nth_frame.bind("<FocusIn>", nth_frame_focus_in)
ent_nth_frame.configure(state=DISABLED)

# button start deploy
btn_start_deploy_txt = ["Start processing", "Empezar a procesar"]
row_btn_start_deploy = 12
btn_start_deploy = Button(
    snd_step, text=btn_start_deploy_txt[lang_idx], command=start_deploy
)
btn_start_deploy.grid(row=row_btn_start_deploy, column=0, columnspan=2, sticky="ew")

### human-in-the-loop step
trd_step_txt = ["Step 3: Annotation (optional)", "Paso 3: Anotación (opcional)"]
trd_step_row = 1
trd_step = LabelFrame(
    deploy_scrollable_frame,
    text=" " + trd_step_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    fg=green_primary,
    borderwidth=2,
)
trd_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
trd_step.grid(column=1, row=trd_step_row, sticky="nesw")
trd_step.columnconfigure(0, weight=1, minsize=label_width)
trd_step.columnconfigure(1, weight=1, minsize=widget_width)

# human-in-the-loop
lbl_hitl_main_txt = ["Manually verify results", "Verificar manualmente los resultados"]
row_hitl_main = 0
lbl_hitl_main = Label(
    master=trd_step, text=lbl_hitl_main_txt[lang_idx], width=1, anchor="w"
)
lbl_hitl_main.grid(row=row_hitl_main, sticky="nesw", pady=2)
btn_hitl_main = Button(
    master=trd_step,
    text=["Start", "Iniciar"][lang_idx],
    width=1,
    command=start_or_continue_hitl,
)
btn_hitl_main.grid(row=row_hitl_main, column=1, sticky="nesw", padx=5)

### fourth step
fth_step_txt = [
    "Step 4: Post-processing (optional)",
    "Paso 4: Post-Procesado (opcional)",
]
fth_step_row = 2
fth_step = LabelFrame(
    deploy_scrollable_frame,
    text=" " + fth_step_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    fg=green_primary,
    borderwidth=2,
)
fth_step.configure(font=(text_font, first_level_frame_font_size, "bold"))
fth_step.grid(column=1, row=fth_step_row, sticky="nesw")
fth_step.columnconfigure(0, weight=1, minsize=label_width)
fth_step.columnconfigure(1, weight=1, minsize=widget_width)

# folder for results
lbl_output_dir_txt = ["Destination folder", "Carpeta de destino"]
row_output_dir = 0
lbl_output_dir = Label(
    master=fth_step, text=lbl_output_dir_txt[lang_idx], width=1, anchor="w"
)
lbl_output_dir.grid(row=row_output_dir, sticky="nesw", pady=2)
var_output_dir = StringVar()
var_output_dir.set("")
var_output_dir_short = StringVar()
dsp_output_dir = Label(
    master=fth_step, textvariable=var_output_dir_short, fg=green_primary
)
btn_output_dir = Button(
    master=fth_step,
    text=browse_txt[lang_idx],
    width=1,
    command=lambda: browse_dir(
        var_output_dir, var_output_dir_short, dsp_output_dir, 25, row_output_dir, 0, "e"
    ),
)
btn_output_dir.grid(row=row_output_dir, column=1, sticky="nesw", padx=5)

# separate files
lbl_separate_files_txt = [
    "Separate files into subdirectories",
    "Separar archivos en subcarpetas",
]
row_separate_files = 1
lbl_separate_files = Label(
    fth_step, text=lbl_separate_files_txt[lang_idx], width=1, anchor="w"
)
lbl_separate_files.grid(row=row_separate_files, sticky="nesw", pady=2)
var_separate_files = BooleanVar()
var_separate_files.set(global_vars["var_separate_files"])
chb_separate_files = Checkbutton(
    fth_step, variable=var_separate_files, command=toggle_sep_frame, anchor="w"
)
chb_separate_files.grid(row=row_separate_files, column=1, sticky="nesw", padx=5)

## separation frame
sep_frame_txt = ["Separation options", "Opciones de separación"]
sep_frame_row = 2
sep_frame = LabelFrame(
    fth_step,
    text=" ↳ " + sep_frame_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    borderwidth=1,
    fg="grey80",
)
sep_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
sep_frame.grid(row=sep_frame_row, column=0, columnspan=2, sticky="ew")
sep_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
sep_frame.columnconfigure(
    1, weight=1, minsize=widget_width - subframe_correction_factor
)
sep_frame.grid_forget()

# method of file placement
lbl_file_placement_txt = [
    "Method of file placement",
    "Método de desplazamiento de archivo",
]
row_file_placement = 0
lbl_file_placement = Label(
    sep_frame,
    text="     " + lbl_file_placement_txt[lang_idx],
    pady=2,
    width=1,
    anchor="w",
)
lbl_file_placement.grid(row=row_file_placement, sticky="nesw")
var_file_placement = IntVar()
var_file_placement.set(global_vars["var_file_placement"])
rad_file_placement_move = Radiobutton(
    sep_frame, text=["Copy", "Copiar"][lang_idx], variable=var_file_placement, value=2
)
rad_file_placement_move.grid(row=row_file_placement, column=1, sticky="w", padx=5)
rad_file_placement_copy = Radiobutton(
    sep_frame, text=["Move", "Mover"][lang_idx], variable=var_file_placement, value=1
)
rad_file_placement_copy.grid(row=row_file_placement, column=1, sticky="e", padx=5)

# separate per confidence
lbl_sep_conf_txt = [
    "Sort results based on confidence",
    "Clasificar resultados basados en confianza",
]
row_sep_conf = 1
lbl_sep_conf = Label(
    sep_frame, text="     " + lbl_sep_conf_txt[lang_idx], width=1, anchor="w"
)
lbl_sep_conf.grid(row=row_sep_conf, sticky="nesw", pady=2)
var_sep_conf = BooleanVar()
var_sep_conf.set(global_vars["var_sep_conf"])
chb_sep_conf = Checkbutton(sep_frame, variable=var_sep_conf, anchor="w")
chb_sep_conf.grid(row=row_sep_conf, column=1, sticky="nesw", padx=5)

## visualize images
lbl_vis_files_txt = [
    "Visualise detections and blur people",
    "Mostrar detecciones y difuminar personas",
]
row_vis_files = 3
lbl_vis_files = Label(fth_step, text=lbl_vis_files_txt[lang_idx], width=1, anchor="w")
lbl_vis_files.grid(row=row_vis_files, sticky="nesw", pady=2)
var_vis_files = BooleanVar()
var_vis_files.set(global_vars["var_vis_files"])
chb_vis_files = Checkbutton(
    fth_step, variable=var_vis_files, anchor="w", command=toggle_vis_frame
)
chb_vis_files.grid(row=row_vis_files, column=1, sticky="nesw", padx=5)

## visualization options
vis_frame_txt = ["Visualization options", "Opciones de visualización"]
vis_frame_row = 4
vis_frame = LabelFrame(
    fth_step,
    text=" ↳ " + vis_frame_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    borderwidth=1,
    fg="grey80",
)
vis_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
vis_frame.grid(row=vis_frame_row, column=0, columnspan=2, sticky="ew")
vis_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
vis_frame.columnconfigure(
    1, weight=1, minsize=widget_width - subframe_correction_factor
)
vis_frame.grid_forget()

## draw bboxes
lbl_vis_bbox_txt = [
    "Draw bounding boxes and confidences",
    "Dibujar contornos y confianzas",
]
row_vis_bbox = 0
lbl_vis_bbox = Label(
    vis_frame, text="     " + lbl_vis_bbox_txt[lang_idx], width=1, anchor="w"
)
lbl_vis_bbox.grid(row=row_vis_bbox, sticky="nesw", pady=2)
var_vis_bbox = BooleanVar()
var_vis_bbox.set(global_vars["var_vis_bbox"])
chb_vis_bbox = Checkbutton(vis_frame, variable=var_vis_bbox, anchor="w")
chb_vis_bbox.grid(row=row_vis_bbox, column=1, sticky="nesw", padx=5)

# line size
lbl_vis_size_txt = [
    "Select line width and font size",
    "Ancho de línea y tamaño de fuente",
]
row_vis_size = 1
lbl_vis_size = Label(
    vis_frame,
    text="        ↳ " + lbl_vis_size_txt[lang_idx],
    pady=2,
    width=1,
    anchor="w",
)
lbl_vis_size.grid(row=row_vis_size, sticky="nesw")
dpd_options_vis_size = [
    ["Extra small", "Small", "Medium", "Large", "Extra large"],
    ["Extra pequeño", "Pequeño", "Mediano", "Grande", "Extra grande"],
]
var_vis_size = StringVar(vis_frame)
var_vis_size.set(dpd_options_vis_size[lang_idx][global_vars["var_vis_size_idx"]])
dpd_vis_size = OptionMenu(vis_frame, var_vis_size, *dpd_options_vis_size[lang_idx])
dpd_vis_size.configure(width=1)
dpd_vis_size.grid(row=row_vis_size, column=1, sticky="nesw", padx=5)

## blur people
lbl_vis_blur_txt = ["Blur people", "Desenfocar a la gente"]
row_vis_blur = 2
lbl_vis_blur = Label(
    vis_frame, text="     " + lbl_vis_blur_txt[lang_idx], width=1, anchor="w"
)
lbl_vis_blur.grid(row=row_vis_blur, sticky="nesw", pady=2)
var_vis_blur = BooleanVar()
var_vis_blur.set(global_vars["var_vis_blur"])
chb_vis_blur = Checkbutton(vis_frame, variable=var_vis_blur, anchor="w")
chb_vis_blur.grid(row=row_vis_blur, column=1, sticky="nesw", padx=5)

## crop images
lbl_crp_files_txt = ["Crop detections", "Recortar detecciones"]
row_crp_files = 5
lbl_crp_files = Label(fth_step, text=lbl_crp_files_txt[lang_idx], width=1, anchor="w")
lbl_crp_files.grid(row=row_crp_files, sticky="nesw", pady=2)
var_crp_files = BooleanVar()
var_crp_files.set(global_vars["var_crp_files"])
chb_crp_files = Checkbutton(fth_step, variable=var_crp_files, anchor="w")
chb_crp_files.grid(row=row_crp_files, column=1, sticky="nesw", padx=5)

# plot
lbl_plt_txt = ["Create maps and graphs", "Crear mapas y gráficos"]
row_plt = 6
lbl_plt = Label(fth_step, text=lbl_plt_txt[lang_idx], width=1, anchor="w")
lbl_plt.grid(row=row_plt, sticky="nesw", pady=2)
var_plt = BooleanVar()
var_plt.set(global_vars["var_plt"])
chb_plt = Checkbutton(fth_step, variable=var_plt, anchor="w")
chb_plt.grid(row=row_plt, column=1, sticky="nesw", padx=5)

# export results
lbl_exp_txt = [
    "Export results and retrieve metadata",
    "Exportar resultados y recuperar metadatos",
]
row_exp = 7
lbl_exp = Label(fth_step, text=lbl_exp_txt[lang_idx], width=1, anchor="w")
lbl_exp.grid(row=row_exp, sticky="nesw", pady=2)
var_exp = BooleanVar()
var_exp.set(global_vars["var_exp"])
chb_exp = Checkbutton(fth_step, variable=var_exp, anchor="w", command=toggle_exp_frame)
chb_exp.grid(row=row_exp, column=1, sticky="nesw", padx=5)

## exportation options
exp_frame_txt = ["Export options", "Opciones de exportación"]
exp_frame_row = 8
exp_frame = LabelFrame(
    fth_step,
    text=" ↳ " + exp_frame_txt[lang_idx] + " ",
    pady=2,
    padx=5,
    relief="solid",
    highlightthickness=5,
    font=100,
    borderwidth=1,
    fg="grey80",
)
exp_frame.configure(font=(text_font, second_level_frame_font_size, "bold"))
exp_frame.grid(row=exp_frame_row, column=0, columnspan=2, sticky="ew")
exp_frame.columnconfigure(0, weight=1, minsize=label_width - subframe_correction_factor)
exp_frame.columnconfigure(
    1, weight=1, minsize=widget_width - subframe_correction_factor
)
exp_frame.grid_forget()

# export format
lbl_exp_format_txt = ["Output file format", "Formato del archivo de salida"]
row_exp_format = 0
lbl_exp_format = Label(
    exp_frame, text="     " + lbl_exp_format_txt[lang_idx], pady=2, width=1, anchor="w"
)
lbl_exp_format.grid(row=row_exp_format, sticky="nesw")
dpd_options_exp_format = [
    ["XLSX", "CSV", "COCO", "Sensing Clues (TSV)"],
    ["XLSX", "CSV", "COCO", "Sensing Clues (TSV)"],
]
var_exp_format = StringVar(exp_frame)
var_exp_format.set(dpd_options_exp_format[lang_idx][global_vars["var_exp_format_idx"]])
dpd_exp_format = OptionMenu(
    exp_frame, var_exp_format, *dpd_options_exp_format[lang_idx]
)
dpd_exp_format.configure(width=1)
dpd_exp_format.grid(row=row_exp_format, column=1, sticky="nesw", padx=5)

# threshold
lbl_thresh_txt = ["Confidence threshold", "Umbral de confianza"]
row_lbl_thresh = 9
lbl_thresh = Label(fth_step, text=lbl_thresh_txt[lang_idx], width=1, anchor="w")
lbl_thresh.grid(row=row_lbl_thresh, sticky="nesw", pady=2)
var_thresh = DoubleVar()
var_thresh.set(global_vars["var_thresh"])
scl_thresh = Scale(
    fth_step,
    from_=0.01,
    to=1,
    resolution=0.01,
    orient=HORIZONTAL,
    variable=var_thresh,
    showvalue=0,
    width=10,
    length=1,
)
scl_thresh.grid(row=row_lbl_thresh, column=1, sticky="ew", padx=10)
dsp_thresh = Label(fth_step, textvariable=var_thresh)
dsp_thresh.configure(fg=green_primary)
dsp_thresh.grid(row=row_lbl_thresh, column=0, sticky="e", padx=0)

# postprocessing button
btn_start_postprocess_txt = ["Start post-processing", "Iniciar el postprocesamiento"]
row_start_postprocess = 10
btn_start_postprocess = Button(
    fth_step, text=btn_start_postprocess_txt[lang_idx], command=start_postprocess
)
btn_start_postprocess.grid(
    row=row_start_postprocess, column=0, columnspan=2, sticky="ew"
)

# set minsize for all rows inside labelframes...
for frame in [
    fst_step,
    snd_step,
    cls_frame,
    img_frame,
    vid_frame,
    fth_step,
    sep_frame,
    exp_frame,
    vis_frame,
]:
    set_minsize_rows(frame)

# ... but not for the hidden rows
snd_step.grid_rowconfigure(row_cls_detec_thresh, minsize=0)  # model thresh
snd_step.grid_rowconfigure(
    row_image_size_for_deploy, minsize=0
)  # image size for deploy
snd_step.grid_rowconfigure(cls_frame_row, minsize=0)  # cls options
snd_step.grid_rowconfigure(img_frame_row, minsize=0)  # image options
snd_step.grid_rowconfigure(vid_frame_row, minsize=0)  # video options
cls_frame.grid_rowconfigure(row_cls_detec_thresh, minsize=0)  # cls animal thresh
# cls_frame.grid_rowconfigure(row_smooth_cls_animal, minsize=0) # cls animal smooth
fth_step.grid_rowconfigure(sep_frame_row, minsize=0)  # sep options
fth_step.grid_rowconfigure(exp_frame_row, minsize=0)  # exp options
fth_step.grid_rowconfigure(vis_frame_row, minsize=0)  # vis options


# enable scroll on mousewheel
def deploy_canvas_mousewheel(event):
    if os.name == "nt":
        deploy_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    else:
        deploy_canvas.yview_scroll(int(-1 * (event.delta / 2)), "units")


# make deploy_tab scrollable
def bind_scroll_to_deploy_canvas():
    deploy_canvas.update_idletasks()
    deploy_canvas.configure(scrollregion=deploy_canvas.bbox("all"))
    deploy_canvas.bind_all("<MouseWheel>", deploy_canvas_mousewheel)
    deploy_canvas.bind_all("<Button-4>", deploy_canvas_mousewheel)
    deploy_canvas.bind_all("<Button-5>", deploy_canvas_mousewheel)


bind_scroll_to_deploy_canvas()

# help tab
scroll = Scrollbar(help_tab)
help_text = Text(help_tab, width=1, height=1, wrap=WORD, yscrollcommand=scroll.set)
help_text.configure(spacing1=2, spacing2=3, spacing3=2)
help_text.tag_config(
    "intro",
    font=f"{text_font} {int(13 * text_size_adjustment_factor)} italic",
    foreground="black",
    lmargin1=10,
    lmargin2=10,
    underline=False,
)
help_text.tag_config(
    "tab",
    font=f"{text_font} {int(16 * text_size_adjustment_factor)} bold",
    foreground="black",
    lmargin1=10,
    lmargin2=10,
    underline=True,
)
help_text.tag_config(
    "frame",
    font=f"{text_font} {int(15 * text_size_adjustment_factor)} bold",
    foreground=green_primary,
    lmargin1=15,
    lmargin2=15,
)
help_text.tag_config(
    "feature",
    font=f"{text_font} {int(14 * text_size_adjustment_factor)} normal",
    foreground="black",
    lmargin1=20,
    lmargin2=20,
    underline=True,
)
help_text.tag_config(
    "explanation",
    font=f"{text_font} {int(13 * text_size_adjustment_factor)} normal",
    lmargin1=25,
    lmargin2=25,
)
hyperlink1 = HyperlinkManager(help_text)


# function to write text which can be called when user changes language settings
def write_help_tab():
    global help_text
    line_number = 1

    # intro sentence
    help_text.insert(
        END,
        [
            "Below you can find detailed documentation for each setting. If you have any questions, feel free to contact me on ",
            "A continuación encontrarás documentación detallada sobre cada ajuste. Si tienes alguna pregunta, no dudes en ponerte en contacto conmigo en ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        "peter@addaxdatascience.com",
        hyperlink1.add(partial(webbrowser.open, "mailto:peter@addaxdatascience.com")),
    )
    help_text.insert(
        END, [" or raise an issue on the ", " o plantear una incidencia en "][lang_idx]
    )
    help_text.insert(
        INSERT,
        ["GitHub page", "la página de GitHub"][lang_idx],
        hyperlink1.add(
            partial(
                webbrowser.open, "https://github.com/PetervanLunteren/AddaxAI/issues"
            )
        ),
    )
    help_text.insert(END, ".\n\n")
    help_text.tag_add("intro", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # first step
    help_text.insert(END, f"{fst_step_txt[lang_idx]}\n")
    help_text.tag_add("frame", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.insert(END, f"{browse_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here you can browse for a folder which contains images and/or video's. The model will be deployed on this directory, as well as the post-processing analyses.\n\n",
            "Aquí puede buscar una carpeta que contenga imágenes y/o vídeos. El modelo se desplegará en este directorio, así como los análisis de post-procesamiento.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # second step
    help_text.insert(END, f"{snd_step_txt[lang_idx]}\n")
    help_text.tag_add("frame", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1

    # det model
    help_text.insert(END, f"{lbl_model_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "AddaxAI uses a combination of a detection model and a classification model to identify animals. The detection model will locate the animal, whereas the "
            "classification model will identify which species the animal belongs to. Here, you can select the detection model that you want to use. If the dropdown "
            "option 'Custom model' is selected, you will be prompted to select a custom YOLOv5 model file. The preloaded 'MegaDetector' models detect animals, people, "
            "and vehicles in camera trap imagery. It does not identify the animals; it just finds them. Version A and B differ only in their training data. Each model "
            "can outperform the other slightly, depending on your data. Try them both and see which one works best for you. If you really don't have a clue, just stick "
            "with the default 'MegaDetector 5a'. More info about MegaDetector models ",
            "AddaxAI utiliza una combinación de un modelo de detección y un modelo de "
            "clasificación para identificar animales. El modelo de detección localizará al animal, mientras que el modelo de clasificación identificará a qué especie "
            "pertenece el animal. Aquí puede seleccionar el modelo de detección que desea utilizar. Si selecciona la opción desplegable 'Modelo personalizado', se le "
            "pedirá que seleccione un archivo de modelo YOLOv5 personalizado. Los modelos 'MegaDetector' precargados detectan animales, personas y vehículos en imágenes"
            " de cámaras trampa. No identifica a los animales, sólo los encuentra. Las versiones A y B sólo se diferencian en los datos de entrenamiento. Cada modelo "
            "puede superar ligeramente al otro, dependiendo de sus datos. Pruebe los dos y vea cuál le funciona mejor. Si realmente no tienes ni idea, quédate con el "
            "'MegaDetector 5a' por defecto. Más información sobre los modelos MegaDetector ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        ["here", "aquí"][lang_idx],
        hyperlink1.add(
            partial(
                webbrowser.open,
                "https://github.com/ecologize/CameraTraps/blob/main/megadetector.md#megadetector-v50-20220615",
            )
        ),
    )
    help_text.insert(END, ".\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # cls model
    help_text.insert(END, f"{lbl_cls_model_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "AddaxAI uses a combination of a detection model and a classification model to identify animals. The detection model will locate the animal, whereas the "
            "classification model will identify which species the animal belongs to. Here, you can select the classification model that you want to use. Each "
            "classification model is developed for a specific area. Explore which model suits your data best, but please note that models developed for other biomes "
            "or projects do not necessarily perform equally well in other ecosystems. Always investigate the model’s accuracy on your data before accepting any results.",
            "AddaxAI utiliza una combinación de un modelo de detección y un modelo de clasificación para identificar animales. El modelo de detección localizará al "
            "animal, mientras que el modelo de clasificación identificará a qué especie pertenece el animal. Aquí puede seleccionar el modelo de clasificación que desea "
            "utilizar. Cada modelo de clasificación se desarrolla para un área específica. Explore qué modelo se adapta mejor a sus datos, pero tenga en cuenta que los "
            "modelos desarrollados para otros biomas o proyectos no funcionan necesariamente igual de bien en otros ecosistemas. Investiga siempre la precisión del modelo"
            " en tus datos antes de aceptar cualquier resultado.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # cls model info
    help_text.insert(END, f"{lbl_model_info_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This will open a window with model information.",
            "Esto abrirá una ventana con información sobre el modelo.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # cls spp selection
    help_text.insert(END, f"{lbl_choose_classes_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here, you can select and deselect the animals categories that are present in your project"
            " area. If the animal category is not selected, it will be excluded from the results. The "
            "category list will update according to the model selected.",
            "Aquí puede seleccionar y anular"
            " la selección de las categorías de animales presentes en la zona de su proyecto. Si la "
            "categoría de animales no está seleccionada, quedará excluida de los resultados. La lista de "
            "categorías se actualizará según el modelo seleccionado.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # threshold to classify detections
    help_text.insert(END, f"{lbl_cls_detec_thresh_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "AddaxAI uses a combination of a detection model and a classification model to identify animals. The detection model will locate "
            "the animal, whereas the classification model will identify which species the animal belongs to. This confidence threshold defines "
            "which animal detections will be passed on to the classification model for further identification.",
            "AddaxAI utiliza una "
            "combinación de un modelo de detección y un modelo de clasificación para identificar a los animales. El modelo de detección "
            "localizará al animal, mientras que el modelo de clasificación identificará a qué especie pertenece el animal. Este umbral de "
            "confianza define qué animales detectados se pasarán al modelo de clasificación para su posterior identificación.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # threshold to classify detections
    help_text.insert(END, f"{lbl_cls_class_thresh_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "AddaxAI uses a combination of a detection model and a classification model to identify animals. The detection model will locate "
            "the animal, whereas the classification model will identify which species the animal belongs to. This confidence threshold defines "
            "which animal identifications will be accepted.",
            "AddaxAI utiliza una combinación de un modelo de detección y un modelo de "
            "clasificación para identificar a los animales. El modelo de detección localizará al animal, mientras que el modelo de clasificación"
            " identificará a qué especie pertenece el animal. Este umbral de confianza define qué identificaciones de animales se aceptarán.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # smooth results
    help_text.insert(END, f"{lbl_smooth_cls_animal_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Sequence smoothing averages confidence scores across detections within a sequence to reduce noise. This improves accuracy by "
            "providing more stable results by combining information over multiple images. Note that it assumes a single species per "
            "sequence and should therefore only be used if multi-species sequences are rare. It does not affect detections of vehicles or "
            "people alongside animals.",
            "El suavizado de secuencias promedia las puntuaciones de confianza entre detecciones dentro de "
            "una secuencia para reducir el ruido. Esto mejora la precisión al proporcionar resultados más estables mediante la combinación"
            " de información de múltiples imágenes. Tenga en cuenta que supone una única especie por secuencia y, por lo tanto, sólo debe "
            "utilizarse si las secuencias multiespecie son poco frecuentes. No afecta a las detecciones de vehículos o personas junto a "
            "animales.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # exclude subs
    help_text.insert(END, f"{lbl_exclude_subs_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "By default, AddaxAI will recurse into subdirectories. Select this option if you want to ignore the subdirectories and process only"
            " the files directly in the chosen folder.\n\n",
            "Por defecto, AddaxAI buscará en los subdirectorios. Seleccione esta opción si "
            "desea ignorar los subdirectorios y procesar sólo los archivos directamente en la carpeta elegida.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # exclude detections
    help_text.insert(
        END,
        f"{lbl_use_custom_img_size_for_deploy_txt[lang_idx]} / {lbl_image_size_for_deploy_txt[lang_idx]}\n",
    )
    help_text.insert(
        END,
        [
            "AddaxAI will resize the images before they get processed. AddaxAI will by default resize the images to 1280 pixels. "
            "Deploying a model with a lower image size will reduce the processing time, but also the detection accuracy. Best results are obtained if you use the"
            " same image size as the model was trained on. If you trained a model in AddaxAI using the default image size, you should set this value to 640 for "
            "the YOLOv5 models. Use the default for the MegaDetector models.\n\n",
            "AddaxAI redimensionará las imágenes antes de procesarlas. Por defecto, AddaxAI redimensionará las imágenes a 1280 píxeles. Desplegar un modelo "
            "con un tamaño de imagen inferior reducirá el tiempo de procesamiento, pero también la precisión de la detección. Los mejores resultados se obtienen "
            "si se utiliza el mismo tamaño de imagen con el que se entrenó el modelo. Si ha entrenado un modelo en AddaxAI utilizando el tamaño de imagen por "
            "defecto, debe establecer este valor en 640 para los modelos YOLOv5. Utilice el valor por defecto para los modelos MegaDetector.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # use absolute paths
    help_text.insert(END, f"{lbl_abs_paths_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "By default, the paths in the output file are relative (i.e. 'image.jpg') instead of absolute (i.e. '/path/to/some/folder/image.jpg'). This "
            "option will make sure the output file contains absolute paths, but it is not recommended. Third party software (such as ",
            "Por defecto, las rutas en el archivo de salida son relativas (es decir, 'imagen.jpg') en lugar de absolutas (es decir, '/ruta/a/alguna/carpeta/"
            "imagen.jpg'). Esta opción se asegurará de que el archivo de salida contenga rutas absolutas, pero no se recomienda. Software de terceros (como ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        "Timelapse",
        hyperlink1.add(
            partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/")
        ),
    )
    help_text.insert(
        END,
        [
            ") will not be able to read the output file if the paths are absolute. Only enable this option if you know what you are doing. More information"
            " how to use Timelapse in conjunction with MegaDetector, see the ",
            ") no serán capaces de leer el archivo de salida si las rutas son absolutas. Solo active esta opción si sabe lo que está haciendo. Para más información"
            " sobre cómo utilizar Timelapse junto con MegaDetector, consulte ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        [
            "Timelapse Image Recognition Guide",
            "la Guía de Reconocimiento de Imágenes de Timelapse",
        ][lang_idx],
        hyperlink1.add(
            partial(
                webbrowser.open,
                "https://saul.cpsc.ucalgary.ca/timelapse/uploads/Guides/TimelapseImageRecognitionGuide.pdf",
            )
        ),
    )
    help_text.insert(END, ".\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # use checkpoints
    help_text.insert(END, f"{lbl_use_checkpnts_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This is a functionality to save results to checkpoints intermittently, in case a technical hiccup arises. That way, you won't have to restart"
            " the entire process again when the process is interrupted.\n\n",
            "Se trata de una funcionalidad para guardar los resultados en puntos de control de forma intermitente, en caso de que surja un contratiempo técnico. "
            "De esta forma, no tendrás que reiniciar todo el proceso de nuevo cuando éste se interrumpa.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # checkpoint frequency
    help_text.insert(END, f"{lbl_checkpoint_freq_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Fill in how often you want to save the results to checkpoints. The number indicates the number of images after which checkpoints will be saved."
            " The entry must contain only numeric characters.\n\n",
            "Introduzca la frecuencia con la que desea guardar los resultados en los puntos de control. El número indica el número de imágenes tras las cuales se "
            "guardarán los puntos de control. La entrada debe contener sólo caracteres numéricos.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # continue from checkpoint
    help_text.insert(END, f"{lbl_cont_checkpnt_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here you can choose to continue from the last saved checkpoint onwards so that the algorithm can continue where it left off. Checkpoints are"
            " saved into the main folder and look like 'checkpoint_<timestamp>.json'. When choosing this option, it will search for a valid"
            " checkpoint file and prompt you if it can't find it.\n\n",
            "Aquí puede elegir continuar desde el último punto de control guardado para que el algoritmo pueda continuar donde lo dejó. Los puntos de control se "
            "guardan en la carpeta principal y tienen el aspecto 'checkpoint_<fecha y hora>.json'. Al elegir esta opción, se buscará un archivo de punto de control "
            "válido y se le preguntará si no puede encontrarlo.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # don't process every frame
    help_text.insert(END, f"{lbl_not_all_frames_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "When processing every frame of a video, it can take a long time to finish. Here, you can specify whether you want to analyse only a selection of frames."
            f" At '{lbl_nth_frame_txt[lang_idx]}' you can specify how many frames you want to be analysed.\n\n",
            "Procesar todos los fotogramas de un vídeo puede llevar mucho tiempo. Aquí puede especificar si desea analizar sólo una selección de fotogramas. "
            f"En '{lbl_nth_frame_txt[lang_idx]}' puedes especificar cuántos fotogramas quieres que se analicen.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # analyse every nth frame
    help_text.insert(END, f"{lbl_nth_frame_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Specify the frame sampling rate you'd like to use. For example, entering '1' will process one frame per second. Typically, sampling one frame per second is sufficient and can significantly reduce processing time. The exact time savings depend on the video's frame rate. Most camera traps record at 30 frames per second, meaning this approach can reduce processing time by 97% compared to processing every frame.\n\n",
            "Especifica la tasa de muestreo de fotogramas que deseas utilizar. Por ejemplo, ingresar '1' procesará un fotograma por segundo. Generalmente, muestrear un fotograma por segundo es suficiente y puede reducir significativamente el tiempo de procesamiento. El ahorro exacto de tiempo depende de la tasa de fotogramas del video. La mayoría de las cámaras trampa graban a 30 fotogramas por segundo, lo que significa que este enfoque puede reducir el tiempo de procesamiento aproximadamente en un 97% en comparación con procesar todos los fotogramas.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # third step
    help_text.insert(END, f"{trd_step_txt[lang_idx]}\n")
    help_text.tag_add("frame", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1

    # human verification
    help_text.insert(END, f"{lbl_hitl_main_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This feature lets you verify the results of the model. You can use it to create training data or to double-check the results. When starting a new "
            "session, you will first be directed to a window where you can select which images you would like to verify. For instance, someone might be only "
            "interested in creating training data for 'class A' to unbalance his training dataset or only want to double-check detections with medium-sure "
            "confidences. After you have selected the images, you will be able to verify them. After having verified all selected images, you will be prompted"
            " if you want to create training data. If you do, the selected images and their associated annotation files will get a unique name and be either "
            "moved or copied to a folder of your choice. This is particularly handy when you want to create training data since, for training, all files must "
            "be in one folder. This way, the files will be unique, and you won't have replacement problems when adding the files to your existing training data. "
            "You can also skip the training data and just continue to post-process the verified results. Not applicable to videos.\n\n",
            "Esta característica le permite verificar los resultados del modelo. Puedes usarlo para crear datos de entrenamiento o para verificar los resultados. "
            "Al iniciar una nueva sesión, primero se le dirigirá a una ventana donde podrá seleccionar qué imágenes desea verificar. Por ejemplo, alguien podría "
            "estar interesado únicamente en crear datos de entrenamiento para la 'clase A' para desequilibrar su conjunto de datos de entrenamiento o simplemente "
            "querer verificar las detecciones con confianzas medias-seguras. Una vez que hayas seleccionado las imágenes, podrás verificarlas. Después de haber "
            "verificado todas las imágenes seleccionadas, se le preguntará si desea crear datos de entrenamiento. Si lo hace, las imágenes seleccionadas y sus "
            "archivos de anotaciones asociados obtendrán un nombre único y se moverán o copiarán a una carpeta de su elección. Esto es particularmente útil cuando"
            " desea crear datos de entrenamiento ya que, para el entrenamiento, todos los archivos deben estar en una carpeta. De esta manera, los archivos serán "
            "únicos y no tendrás problemas de reemplazo al agregar los archivos a tus datos de entrenamiento existentes. También puedes omitir los datos de "
            "entrenamiento y simplemente continuar con el posprocesamiento de los resultados verificados. No aplicable a vídeos.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # forth step
    help_text.insert(END, f"{fth_step_txt[lang_idx]}\n")
    help_text.tag_add("frame", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1

    # destination folder
    help_text.insert(END, f"{lbl_output_dir_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here you can browse for a folder in which the results of the post-processing features will be placed. If nothing is selected, the folder "
            "chosen at step one will be used as the destination folder.\n\n",
            "Aquí puede buscar una carpeta en la que se colocarán los resultados de las funciones de postprocesamiento. Si no se selecciona nada, la carpeta "
            "elegida en el primer paso se utilizará como carpeta de destino.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # separate files
    help_text.insert(END, f"{lbl_separate_files_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This function divides the files into subdirectories based on their detections. Please be warned that this will be done automatically. "
            "There will not be an option to review and adjust the detections before the images will be moved. If you want that (a human in the loop), take a look at ",
            "Esta función divide los archivos en subdirectorios en función de sus detecciones. Tenga en cuenta que esto se hará automáticamente. No habrá opción de "
            "revisar y ajustar las detecciones antes de mover las imágenes. Si quieres eso (una humano en el bucle), echa un vistazo a ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        "Timelapse",
        hyperlink1.add(
            partial(webbrowser.open, "https://saul.cpsc.ucalgary.ca/timelapse/")
        ),
    )
    help_text.insert(
        END,
        [
            ", which offers such a feature. More information about that ",
            ", que ofrece tal característica. Más información al respecto ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        ["here", "aquí"][lang_idx],
        hyperlink1.add(
            partial(
                webbrowser.open,
                "https://saul.cpsc.ucalgary.ca/timelapse/uploads/Guides/TimelapseImageRecognitionGuide.pdf",
            )
        ),
    )
    help_text.insert(
        END,
        [
            " (starting on page 9). The process of importing the output file produced by AddaxAI into Timelapse is described ",
            " (a partir de la página 9). El proceso de importación del archivo de salida producido por AddaxAI en Timelapse se describe ",
        ][lang_idx],
    )
    help_text.insert(
        INSERT,
        ["here", "aquí"][lang_idx],
        hyperlink1.add(
            partial(
                webbrowser.open,
                "https://saul.cpsc.ucalgary.ca/timelapse/pmwiki.php?n=Main.DownloadMegadetector",
            )
        ),
    )
    help_text.insert(END, ".\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # method of file placement
    help_text.insert(END, f"{lbl_file_placement_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here you can choose whether to move the files into subdirectories, or copy them so that the originals remain untouched.\n\n",
            "Aquí puedes elegir si quieres mover los archivos a subdirectorios o copiarlos de forma que los originales permanezcan intactos.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # sort results based on confidence
    help_text.insert(END, f"{lbl_sep_conf_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This feature will further separate the files based on its confidence value (in tenth decimal intervals). That means that each class will"
            " have subdirectories like e.g. 'conf_0.6-0.7', 'conf_0.7-0.8', 'conf_0.8-0.9', etc.\n\n",
            "Esta función separará aún más los archivos en función de su valor de confianza (en intervalos decimales). Esto significa que cada clase tendrá"
            " subdirectorios como, por ejemplo, 'conf_0.6-0.7', 'conf_0.7-0.8', 'conf_0.8-0.9', etc.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # visualize files
    help_text.insert(END, f"{lbl_vis_files_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This functionality draws boxes around the detections and prints their confidence values. This can be useful to visually check the results."
            " Videos can't be visualized using this tool. Please be aware that this action is permanent and cannot be undone. Be wary when using this on original images.\n\n",
            "Esta funcionalidad dibuja recuadros alrededor de las detecciones e imprime sus valores de confianza. Esto puede ser útil para comprobar visualmente los "
            "resultados. Los vídeos no pueden visualizarse con esta herramienta.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # crop files
    help_text.insert(END, f"{lbl_crp_files_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "This feature will crop the detections and save them as separate images. Not applicable for videos.\n\n",
            "Esta función recortará las detecciones y las guardará como imágenes separadas. No es aplicable a los vídeos.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # plot graphs
    help_text.insert(END, f"{lbl_plt_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here you can select to create activity patterns, bar charts, pie charts and temporal heatmaps. The time unit (year, month, "
            "week or day) will be chosen automatically based on the time period of your data. If more than 100 units are needed to "
            "visualize, they will be skipped due to long processing times. Each visualization results in a static PNG file and a dynamic"
            " HTML file to explore the data further. Additional interactive maps will be produced when geotags can be retrieved from the "
            "image metadata.",
            "Aquí puede seleccionar la creación de patrones de actividad, gráficos de barras, gráficos circulares y "
            "mapas térmicos temporales. La unidad temporal (año, mes, semana o día) se elegirá automáticamente en función del periodo de"
            " tiempo de sus datos. Si se necesitan más de 100 unidades para visualizar, se omitirán debido a los largos tiempos de "
            "procesamiento. Cada visualización da como resultado un archivo PNG estático y un archivo HTML dinámico para explorar más a "
            "fondo los datos. Se producirán mapas interactivos adicionales cuando se puedan recuperar geoetiquetas de los metadatos de "
            "las imágenes.",
        ][lang_idx],
    )
    help_text.insert(END, "\n\n")
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # export results
    help_text.insert(END, f"{lbl_exp_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Here you can select whether you want to export the results to other file formats. It will additionally try to fetch image metadata, like "
            "timestamps, locations, and more.\n\n",
            "Aquí puede seleccionar si desea exportar los resultados a otros formatos de archivo. Además, "
            "intentará obtener metadatos de la imagen, como marcas de tiempo, ubicaciones, etc. \n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # postprocess confidence threshold
    help_text.insert(END, f"{lbl_thresh_txt[lang_idx]}\n")
    help_text.insert(
        END,
        [
            "Detections below this value will not be post-processed. To adjust the threshold value, you can drag the slider or press either sides next to "
            "the slider for a 0.01 reduction or increment. Confidence values are within the [0.01, 1] interval. If you set the confidence threshold too high, "
            "you will miss some detections. On the other hand, if you set the threshold too low, you will get false positives. When choosing a threshold for your "
            f"project, it is important to choose a threshold based on your own data. My advice is to first visualize your data ('{lbl_vis_files_txt[lang_idx]}') with a low "
            "threshold to get a feeling of the confidence values in your data. This will show you how sure the model is about its detections and will give you an "
            "insight into which threshold will work best for you. If you really don't know, 0.2 is probably a conservative threshold for most projects.\n\n",
            "Las detecciones por debajo de este valor no se postprocesarán. Para ajustar el valor del umbral, puede arrastrar el control deslizante o pulsar "
            "cualquiera de los lados junto al control deslizante para una reducción o incremento de 0,01. Los valores de confianza están dentro del intervalo "
            "[0,01, 1]. Si ajusta el umbral de confianza demasiado alto, pasará por alto algunas detecciones. Por otro lado, si fija el umbral demasiado bajo, "
            "obtendrá falsos positivos. Al elegir un umbral para su proyecto, es importante elegir un umbral basado en sus propios datos. Mi consejo es que primero"
            f" visualice sus datos ('{lbl_vis_files_txt[lang_idx]}') con un umbral bajo para hacerse una idea de los valores de confianza de sus datos. Esto le mostrará lo "
            "seguro que está el modelo sobre sus detecciones y le dará una idea de qué umbral funcionará mejor para usted. Si realmente no lo sabe, 0,2 es "
            "probablemente un umbral conservador para la mayoría de los proyectos.\n\n",
        ][lang_idx],
    )
    help_text.tag_add("feature", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 1
    help_text.tag_add("explanation", f"{str(line_number)}.0", f"{str(line_number)}.end")
    line_number += 2

    # config help_text
    help_text.pack(fill="both", expand=True)
    help_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
    scroll.configure(command=help_text.yview)


write_help_tab()

# about tab
about_scroll = Scrollbar(about_tab)
about_text = Text(about_tab, width=1, height=1, wrap=WORD, yscrollcommand=scroll.set)
about_text.configure(spacing1=2, spacing2=3, spacing3=2)
about_text.tag_config(
    "title",
    font=f"{text_font} {int(15 * text_size_adjustment_factor)} bold",
    foreground=green_primary,
    lmargin1=10,
    lmargin2=10,
)
about_text.tag_config(
    "info",
    font=f"{text_font} {int(13 * text_size_adjustment_factor)} normal",
    lmargin1=20,
    lmargin2=20,
)
about_text.tag_config(
    "citation",
    font=f"{text_font} {int(13 * text_size_adjustment_factor)} normal",
    lmargin1=30,
    lmargin2=50,
)
hyperlink = HyperlinkManager(about_text)
