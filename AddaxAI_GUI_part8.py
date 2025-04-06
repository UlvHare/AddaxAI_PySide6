# function to write text which can be called when user changes language settings
def write_about_tab():
    global about_text
    text_line_number = 1

    # contact
    about_text.insert(END, ["Contact\n", "Contacto\n"][lang_idx])
    about_text.insert(
        END,
        [
            "Please also help me to keep improving AddaxAI and let me know about any improvements, bugs, or new features so that I can keep it up-to-date. You can "
            "contact me at ",
            "Por favor, ayúdame también a seguir mejorando AddaxAI e infórmame de cualquier mejora, error o nueva función para que pueda mantenerlo actualizado. "
            "Puedes ponerte en contacto conmigo en ",
        ][lang_idx],
    )
    about_text.insert(
        INSERT,
        "peter@addaxdatascience.com",
        hyperlink.add(partial(webbrowser.open, "mailto:peter@addaxdatascience.com")),
    )
    about_text.insert(
        END, [" or raise an issue on the ", " o plantear un problema en "][lang_idx]
    )
    about_text.insert(
        INSERT,
        ["GitHub page", "la página de GitHub"][lang_idx],
        hyperlink.add(
            partial(
                webbrowser.open, "https://github.com/PetervanLunteren/AddaxAI/issues"
            )
        ),
    )
    about_text.insert(END, ".\n\n")
    about_text.tag_add(
        "title", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 1
    about_text.tag_add(
        "info", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 2

    # addaxai citation
    about_text.insert(END, ["AddaxAI citation\n", "Citar AddaxAI\n"][lang_idx])
    about_text.insert(
        END,
        [
            "If you used AddaxAI in your research, please use the following citations. The AddaxAI software was previously called 'EcoAssist'.\n",
            "Si ha utilizado AddaxAI en su investigación, utilice la siguiente citas. AddaxAI se llamaba antes 'EcoAssist'.\n",
        ][lang_idx],
    )
    about_text.insert(
        END,
        "- van Lunteren, P., (2023). AddaxAI: A no-code platform to train and deploy custom YOLOv5 object detection models. Journal of Open Source Software, 8(88), 5581, https://doi.org/10.21105/joss.05581",
    )
    about_text.insert(
        INSERT,
        "https://doi.org/10.21105/joss.05581",
        hyperlink.add(partial(webbrowser.open, "https://doi.org/10.21105/joss.05581")),
    )
    about_text.insert(END, ".\n")
    about_text.insert(
        END,
        [
            "- Plus the citation of the models used.\n\n",
            "- Más la cita de los modelos utilizados.\n\n",
        ][lang_idx],
    )
    about_text.tag_add(
        "title", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 1
    about_text.tag_add(
        "info", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 1
    about_text.tag_add(
        "citation", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 1
    about_text.tag_add(
        "citation", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 2

    # development credits
    about_text.insert(END, ["Development\n", "Desarrollo\n"][lang_idx])
    about_text.insert(
        END, ["AddaxAI is developed by ", "AddaxAI ha sido desarrollado por "][lang_idx]
    )
    about_text.insert(
        INSERT,
        "Addax Data Science",
        hyperlink.add(partial(webbrowser.open, "https://addaxdatascience.com/")),
    )
    about_text.insert(
        END, [" in collaboration with ", " en colaboración con "][lang_idx]
    )
    about_text.insert(
        INSERT,
        "Smart Parks",
        hyperlink.add(partial(webbrowser.open, "https://www.smartparks.org/")),
    )
    about_text.insert(END, ".\n\n")
    about_text.tag_add(
        "title", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 1
    about_text.tag_add(
        "info", str(text_line_number) + ".0", str(text_line_number) + ".end"
    )
    text_line_number += 2

    # config about_text
    about_text.pack(fill="both", expand=True)
    about_text.configure(font=(text_font, 11, "bold"), state=DISABLED)
    scroll.configure(command=about_text.yview)


write_about_tab()

# SIMPLE MODE WINDOW
dir_image = customtkinter.CTkImage(PIL_dir_image, size=(ICON_SIZE, ICON_SIZE))
mdl_image = customtkinter.CTkImage(PIL_mdl_image, size=(ICON_SIZE, ICON_SIZE))
spp_image = customtkinter.CTkImage(PIL_spp_image, size=(ICON_SIZE, ICON_SIZE))
run_image = customtkinter.CTkImage(PIL_run_image, size=(ICON_SIZE, ICON_SIZE))

# set the global appearance for the app
customtkinter.set_appearance_mode("light")
customtkinter.set_default_color_theme(
    os.path.join(AddaxAI_files, "AddaxAI", "themes", "addaxai.json")
)

# set up window
simple_mode_win = customtkinter.CTkToplevel(root)
simple_mode_win.title(f"AddaxAI v{current_AA_version} - Simple mode")
simple_mode_win.geometry("+20+20")
simple_mode_win.protocol("WM_DELETE_WINDOW", on_toplevel_close)
simple_mode_win.columnconfigure(0, weight=1, minsize=500)
main_label_font = customtkinter.CTkFont(family="CTkFont", size=14, weight="bold")
simple_bg_image = customtkinter.CTkImage(
    PIL_sidebar, size=(SIM_WINDOW_WIDTH, SIM_WINDOW_HEIGHT)
)
simple_bg_image_label = customtkinter.CTkLabel(simple_mode_win, image=simple_bg_image)
simple_bg_image_label.grid(row=0, column=0)
simple_main_frame = customtkinter.CTkFrame(
    simple_mode_win, corner_radius=0, fg_color="transparent"
)
simple_main_frame.grid(row=0, column=0, sticky="ns")
simple_mode_win.withdraw()  # only show when all widgets are loaded

# logo
sim_top_banner = customtkinter.CTkImage(
    PIL_logo_incl_text, size=(LOGO_WIDTH, LOGO_HEIGHT)
)
customtkinter.CTkLabel(simple_main_frame, text="", image=sim_top_banner).grid(
    column=0, row=0, columnspan=2, sticky="ew", pady=(PADY, 0), padx=0
)

# top buttons
sim_btn_switch_mode_txt = ["To advanced mode", "Al modo avanzado"]
sim_btn_switch_mode = GreyTopButton(
    master=simple_main_frame,
    text=sim_btn_switch_mode_txt[lang_idx],
    command=switch_mode,
)
sim_btn_switch_mode.grid(
    row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan=2, sticky="nw"
)
sim_btn_switch_lang = GreyTopButton(
    master=simple_main_frame, text="Switch language", command=set_language
)
sim_btn_switch_lang.grid(
    row=0, column=0, padx=PADX, pady=(0, 0), columnspan=2, sticky="sw"
)
sim_btn_sponsor = GreyTopButton(
    master=simple_main_frame,
    text=adv_btn_sponsor_txt[lang_idx],
    command=sponsor_project,
)
sim_btn_sponsor.grid(
    row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan=2, sticky="ne"
)
sim_btn_reset_values = GreyTopButton(
    master=simple_main_frame,
    text=adv_btn_reset_values_txt[lang_idx],
    command=reset_values,
)
sim_btn_reset_values.grid(
    row=0, column=0, padx=PADX, pady=(0, 0), columnspan=2, sticky="se"
)

# choose folder
sim_dir_frm_1 = MyMainFrame(master=simple_main_frame)
sim_dir_frm_1.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_dir_img_widget = customtkinter.CTkLabel(
    sim_dir_frm_1, text="", image=dir_image, compound="left"
)
sim_dir_img_widget.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_dir_frm = MySubFrame(master=sim_dir_frm_1)
sim_dir_frm.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_dir_lbl_txt = [
    "Which folder do you want to analyse?",
    "¿Qué carpeta quieres analizar?",
]
sim_dir_lbl = customtkinter.CTkLabel(
    sim_dir_frm, text=sim_dir_lbl_txt[lang_idx], font=main_label_font
)
sim_dir_lbl.grid(
    row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
)
sim_dir_inf = InfoButton(master=sim_dir_frm, text="?", command=sim_dir_show_info)
sim_dir_inf.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e", columnspan=2)
sim_dir_btn = customtkinter.CTkButton(
    sim_dir_frm,
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
sim_dir_btn.grid(row=1, column=0, padx=(PADX, PADX / 2), pady=(0, PADY), sticky="nswe")
sim_dir_pth_frm = MySubSubFrame(master=sim_dir_frm)
sim_dir_pth_frm.grid(
    row=1, column=1, padx=(PADX / 2, PADX), pady=(0, PADY), sticky="nesw"
)
sim_dir_pth_txt = ["no folder selected", "no hay carpeta seleccionada"]
sim_dir_pth = customtkinter.CTkLabel(
    sim_dir_pth_frm, text=sim_dir_pth_txt[lang_idx], text_color="grey"
)
sim_dir_pth.pack()

# choose model
sim_mdl_frm_1 = MyMainFrame(master=simple_main_frame)
sim_mdl_frm_1.grid(row=3, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
sim_mdl_img_widget = customtkinter.CTkLabel(
    sim_mdl_frm_1, text="", image=mdl_image, compound="left"
)
sim_mdl_img_widget.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_mdl_frm = MySubFrame(master=sim_mdl_frm_1)
sim_mdl_frm.grid(row=1, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_mdl_lbl_txt = [
    "Which species identification model do you want to use?",
    "¿Qué modelo de identificación de especies quiere utilizar?",
]
sim_mdl_lbl = customtkinter.CTkLabel(
    sim_mdl_frm, text=sim_mdl_lbl_txt[lang_idx], font=main_label_font
)
sim_mdl_lbl.grid(
    row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
)
sim_mdl_inf = InfoButton(master=sim_mdl_frm, text="?", command=sim_mdl_show_info)
sim_mdl_inf.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e", columnspan=2)
# convert to more elaborate dpd value for the 'None' simple mode option
sim_dpd_options_cls_model = [
    [item[0] + suffixes_for_sim_none[i], *item[1:]]
    for i, item in enumerate(dpd_options_cls_model)
]
sim_mdl_dpd = customtkinter.CTkOptionMenu(
    sim_mdl_frm,
    values=sim_dpd_options_cls_model[lang_idx],
    command=sim_mdl_dpd_callback,
    width=1,
)
sim_mdl_dpd.set(
    sim_dpd_options_cls_model[lang_idx][global_vars["var_cls_model_idx"]]
)  # take idx instead of string
sim_mdl_dpd.grid(
    row=1, column=0, padx=PADX, pady=(PADY / 4, PADY), sticky="nswe", columnspan=2
)

# select animals
sim_spp_frm_1 = MyMainFrame(master=simple_main_frame)
sim_spp_frm_1.grid(row=4, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
sim_spp_img_widget = customtkinter.CTkLabel(
    sim_spp_frm_1, text="", image=spp_image, compound="left"
)
sim_spp_img_widget.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_spp_frm = MySubFrame(master=sim_spp_frm_1, width=1000)
sim_spp_frm.grid(row=2, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_spp_lbl_txt = [
    "Which species are present in your project area?",
    "¿Qué especies están presentes en la zona de su proyecto?",
]
sim_spp_lbl = customtkinter.CTkLabel(
    sim_spp_frm, text=sim_spp_lbl_txt[lang_idx], font=main_label_font, text_color="grey"
)
sim_spp_lbl.grid(
    row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
)
sim_spp_inf = InfoButton(master=sim_spp_frm, text="?", command=sim_spp_show_info)
sim_spp_inf.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="e", columnspan=2)
sim_spp_scr_height = 238
sim_spp_scr = SpeciesSelectionFrame(
    master=sim_spp_frm, height=sim_spp_scr_height, dummy_spp=True
)
sim_spp_scr._scrollbar.configure(height=0)
sim_spp_scr.grid(
    row=1, column=0, padx=PADX, pady=(PADY / 4, PADY), sticky="ew", columnspan=2
)

# deploy button
sim_run_frm_1 = MyMainFrame(master=simple_main_frame)
sim_run_frm_1.grid(row=5, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
sim_run_img_widget = customtkinter.CTkLabel(
    sim_run_frm_1, text="", image=run_image, compound="left"
)
sim_run_img_widget.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="nswe")
sim_run_frm = MySubFrame(master=sim_run_frm_1, width=1000)
sim_run_frm.grid(row=3, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
sim_run_btn_txt = ["Start processing", "Empezar a procesar"]
sim_run_btn = customtkinter.CTkButton(
    sim_run_frm,
    text=sim_run_btn_txt[lang_idx],
    command=lambda: start_deploy(simple_mode=True),
)
sim_run_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe", columnspan=2)

# about
sim_abo_lbl = tk.Label(
    simple_main_frame,
    text=adv_abo_lbl_txt[lang_idx],
    font=Font(size=ADDAX_TXT_SIZE),
    fg="black",
    bg=yellow_primary,
)
sim_abo_lbl.grid(row=6, column=0, columnspan=2, sticky="")
sim_abo_lbl_link = tk.Label(
    simple_main_frame,
    text="addaxdatascience.com",
    cursor="hand2",
    font=Font(size=ADDAX_TXT_SIZE, underline=1),
    fg=green_primary,
    bg=yellow_primary,
)
sim_abo_lbl_link.grid(row=7, column=0, columnspan=2, sticky="", pady=(0, PADY))
sim_abo_lbl_link.bind("<Button-1>", lambda e: callback("http://addaxdatascience.com"))

# resize deploy tab to content
resize_canvas_to_content()


# main function
def main():
    # check if user calls this script from Timelapse
    parser = argparse.ArgumentParser(description="AddaxAI GUI")
    parser.add_argument(
        "--timelapse-path", type=str, help="Path to the timelapse folder"
    )
    args = parser.parse_args()
    global timelapse_mode
    global timelapse_path
    timelapse_mode = False
    timelapse_path = ""
    if args.timelapse_path:
        timelapse_mode = True
        timelapse_path = os.path.normpath(args.timelapse_path)
        var_choose_folder.set(timelapse_path)
        dsp_timelapse_path = shorten_path(timelapse_path, 25)
        sim_dir_pth.configure(text=dsp_timelapse_path, text_color="black")
        var_choose_folder_short.set(dsp_timelapse_path)
        dsp_choose_folder.grid(column=0, row=row_choose_folder, sticky="w")

    # try to download the model info json to check if there are new models
    fetch_latest_model_info()

    # show donation popup if user has launched the app a certain number of times
    check_donation_window_popup()

    # initialise start screen
    enable_frame(fst_step)
    disable_frame(snd_step)
    disable_frame(trd_step)
    disable_frame(fth_step)
    set_lang_buttons(lang_idx)

    # super weird but apparently necessary, otherwise script halts at first root.update()
    switch_mode()
    switch_mode()

    # update frame states if we already have a timelapse path
    if timelapse_mode:
        update_frame_states()

    if scale_factor != 1.0:
        if not global_vars["var_scale_warning_shown"]:
            mb.showwarning(
                [
                    f"Scale set to {int(scale_factor * 100)}%",
                    f"Escala fijada en {int(scale_factor * 100)}%",
                ][lang_idx],
                [
                    f"The user interface of AddaxAI is designed for a scale setting of 100%. However, your screen settings are set to {int(scale_factor * 100)}%. We've worked to maintain a consistent look across different scale settings, but it may still affect the appearance of the application, causing some elements (like checkboxes or windows) to appear disproportionately large or small. Note that these visual differences won't impact the functionality of the application.\n\nThis warning will only appear once.",
                    f"La interfaz de usuario de AddaxAI está diseñada para un ajuste de escala del 100%. Sin embargo, su configuración de pantalla está establecida en {int(scale_factor * 100)}%. Hemos trabajado para mantener una apariencia consistente a través de diferentes configuraciones de escala, pero aún puede afectar la apariencia de la aplicación, causando que algunos elementos (como casillas de verificación o ventanas) aparezcan desproporcionadamente grandes o pequeñas. Tenga en cuenta que estas diferencias visuales no afectarán a la funcionalidad de la aplicación.\n\nEste aviso sólo aparecerá una vez.",
                ][lang_idx],
            )
        write_global_vars({"var_scale_warning_shown": True})

    # run
    root.mainloop()


# executable as script
if __name__ == "__main__":
    main()
