##############################################
############# FRONTEND FUNCTIONS #############
##############################################

# open window with model info
def show_download_error_window(model_title, model_dir, model_vars):
    # get dwonload info
    download_info = model_vars["download_info"]
    total_download_size = model_vars["total_download_size"]

    # define functions
    def try_again():
        de_root.destroy()
        download_model(model_dir, skip_ask=True)

    # create window
    de_root = customtkinter.CTkToplevel(root)
    de_root.title(["Download error", "Error de descarga"][lang_idx])
    de_root.geometry("+10+10")
    bring_window_to_top_but_not_for_ever(de_root)

    # main label
    lbl2 = customtkinter.CTkLabel(
        de_root, text=f"{model_title} ({total_download_size})", font=main_label_font
    )
    lbl2.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan=2, sticky="nswe")
    lbl2 = customtkinter.CTkLabel(
        de_root,
        text=[
            "Something went wrong while trying to download the model. This can have "
            "several causes.",
            "Algo salió mal al intentar descargar el modelo. Esto "
            "puede tener varias causas.",
        ][lang_idx],
    )
    lbl2.grid(
        row=1, column=0, padx=PADX, pady=(0, PADY / 2), columnspan=2, sticky="nswe"
    )

    # internet connection frame
    int_frm_1 = customtkinter.CTkFrame(master=de_root)
    int_frm_1.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    int_frm_1.columnconfigure(0, weight=1, minsize=700)
    int_frm_2 = customtkinter.CTkFrame(master=int_frm_1)
    int_frm_2.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    int_frm_2.columnconfigure(0, weight=1, minsize=700)
    int_lbl = customtkinter.CTkLabel(
        int_frm_1,
        text=[" 1. Internet connection", " 1. Conexión a Internet"][lang_idx],
        font=main_label_font,
    )
    int_lbl.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nsw")
    int_txt_1 = customtkinter.CTkTextbox(
        master=int_frm_2,
        corner_radius=10,
        height=55,
        wrap="word",
        fg_color="transparent",
    )
    int_txt_1.grid(row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), sticky="nswe")
    int_txt_1.insert(
        END,
        [
            "Check if you have a stable internet connection. If possible, try again on a fibre internet "
            "connection, or perhaps on a different, stronger, Wi-Fi network. Sometimes connecting to an "
            "open network such as a mobile hotspot can do the trick.",
            "Comprueba si tienes una conexión "
            "a Internet estable. Si es posible, inténtalo de nuevo con una conexión de fibra o quizás con "
            "otra red Wi-Fi más potente. A veces, conectarse a una red abierta, como un hotspot móvil, "
            "puede funcionar.",
        ][lang_idx],
    )

    # protection software frame
    pro_frm_1 = customtkinter.CTkFrame(master=de_root)
    pro_frm_1.grid(row=3, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    pro_frm_1.columnconfigure(0, weight=1, minsize=700)
    pro_frm_2 = customtkinter.CTkFrame(master=pro_frm_1)
    pro_frm_2.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    pro_frm_2.columnconfigure(0, weight=1, minsize=700)
    pro_lbl = customtkinter.CTkLabel(
        pro_frm_1,
        text=[" 2. Protection software", " 2. Software de protección"][lang_idx],
        font=main_label_font,
    )
    pro_lbl.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nsw")
    pro_txt_1 = customtkinter.CTkTextbox(
        master=pro_frm_2,
        corner_radius=10,
        height=55,
        wrap="word",
        fg_color="transparent",
    )
    pro_txt_1.grid(row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), sticky="nswe")
    pro_txt_1.insert(
        END,
        [
            "Some firewall, proxy or VPN settings might block the internet connection. Try again with this "
            "protection software disabled.",
            "Algunas configuraciones de cortafuegos, proxy o VPN podrían "
            "bloquear la conexión a Internet. Inténtalo de nuevo con este software de protección "
            "desactivado.",
        ][lang_idx],
    )

    # try internet connection again
    btns_frm1 = customtkinter.CTkFrame(master=de_root)
    btns_frm1.columnconfigure(0, weight=1, minsize=10)
    btns_frm1.grid(row=4, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    tryag_btn = customtkinter.CTkButton(
        btns_frm1,
        text=[
            "Try internet connection again",
            "Prueba de nuevo la conexión a Internet",
        ][lang_idx],
        command=try_again,
    )
    tryag_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")

    # manual download frame
    pro_frm_1 = customtkinter.CTkFrame(master=de_root)
    pro_frm_1.grid(row=5, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    pro_frm_1.columnconfigure(0, weight=1, minsize=700)
    pro_frm_2 = customtkinter.CTkFrame(master=pro_frm_1)
    pro_frm_2.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    pro_frm_2.columnconfigure(0, weight=1, minsize=700)
    pro_lbl1 = customtkinter.CTkLabel(
        pro_frm_1,
        text=[" 3. Manual download", " 3. Descarga manual"][lang_idx],
        font=main_label_font,
    )
    pro_lbl1.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nsw")
    pro_lbl2 = customtkinter.CTkLabel(
        pro_frm_2,
        text=[
            "If the above suggestions don't work, it might be easiest to manually"
            " download the file(s) and place them in the appropriate folder.",
            "Si las sugerencias anteriores no funcionan, puede que lo más fácil "
            "sea descargar manualmente el archivo o archivos y colocarlos en "
            "la carpeta adecuada.",
        ][lang_idx],
    )
    pro_lbl2.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), sticky="nsw")

    # download instructions are dependent on their host
    step_n = 1
    show_next_steps = True
    pro_lbl5_row = 4
    if model_title == "Namibian Desert - Addax Data Science":
        main_url = download_info[0][0].replace(
            "/resolve/main/namib_desert_v1.pt?download=true", "/tree/main"
        )
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[f" {step_n}. Go to website:", f" {step_n}. Ir al sitio web:"][
                lang_idx
            ],
        )
        step_n += 1
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2, text=main_url, cursor="hand2", font=url_label_font
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind("<Button-1>", lambda e: callback(main_url))
        pro_lbl5 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Download file '{download_info[0][1]}'.",
                f" {step_n}. Descarga el archivo '{download_info[0][1]}'.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl5.grid(row=4, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
    elif download_info[0][0].startswith("https://huggingface.co/Addax-Data-Science/"):
        main_url = download_info[0][0].replace(
            f"/resolve/main/{download_info[0][1]}?download=true", "/tree/main"
        )
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[f" {step_n}. Go to website:", f" {step_n}. Ir al sitio web:"][
                lang_idx
            ],
        )
        step_n += 1
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2, text=main_url, cursor="hand2", font=url_label_font
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind("<Button-1>", lambda e: callback(main_url))
        for download_file in download_info:
            pro_lbl5 = customtkinter.CTkLabel(
                pro_frm_2,
                text=[
                    f" {step_n}. Download file '{download_file[1]}'.",
                    f" {step_n}. Descarga el archivo '{download_file[1]}'.",
                ][lang_idx],
            )
            step_n += 1
            pro_lbl5.grid(
                row=pro_lbl5_row, column=0, padx=PADX, pady=(0, 0), sticky="nsw"
            )
            pro_lbl5_row += 1
    elif download_info[0][0].startswith("https://zenodo.org/records/"):
        main_url = download_info[0][0].replace(
            f"/files/{download_info[0][1]}?download=1", ""
        )
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[f" {step_n}. Go to website:", f" {step_n}. Ir al sitio web:"][
                lang_idx
            ],
        )
        step_n += 1
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2, text=main_url, cursor="hand2", font=url_label_font
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind("<Button-1>", lambda e: callback(main_url))
        pro_lbl5 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Download file '{download_info[0][1]}'.",
                f" {step_n}. Descarga el archivo '{download_info[0][1]}'.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl5.grid(row=4, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
    elif model_title == "Tasmania - University of Tasmania":
        main_url = download_info[1][0].replace(
            "/resolve/main/class_list.yaml?download=true", "/tree/main"
        )
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[f" {step_n}. Go to website:", f" {step_n}. Ir al sitio web:"][
                lang_idx
            ],
        )
        step_n += 1
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2, text=main_url, cursor="hand2", font=url_label_font
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind("<Button-1>", lambda e: callback(main_url))
        pro_lbl5 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Download file '{download_info[0][1]}'.",
                f" {step_n}. Descarga el archivo '{download_info[0][1]}'.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl5.grid(row=4, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl6 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Download file '{download_info[1][1]}'.",
                f" {step_n}. Descarga el archivo '{download_info[1][1]}'.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl6.grid(row=5, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
    elif model_title == "MegaDetector 5a" or model_title == "MegaDetector 5b":
        main_url = "https://github.com/agentmorris/MegaDetector/releases/tag/v5.0"
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[f" {step_n}. Go to website:", f" {step_n}. Ir al sitio web:"][
                lang_idx
            ],
        )
        step_n += 1
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2, text=main_url, cursor="hand2", font=url_label_font
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind("<Button-1>", lambda e: callback(main_url))
        pro_lbl5 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Download file '{download_info[0][1]}'.",
                f" {step_n}. Descarga el archivo '{download_info[0][1]}'.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl5.grid(row=4, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
    elif model_title == "Europe - DeepFaune v1.1":
        main_url = "https://pbil.univ-lyon1.fr/software/download/deepfaune/v1.1"
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[f" {step_n}. Go to website:", f" {step_n}. Ir al sitio web:"][
                lang_idx
            ],
        )
        step_n += 1
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2, text=main_url, cursor="hand2", font=url_label_font
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind("<Button-1>", lambda e: callback(main_url))
        pro_lbl5 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Download file '{download_info[0][1]}'.",
                f" {step_n}. Descarga el archivo '{download_info[0][1]}'.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl5.grid(row=4, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
    else:
        pro_lbl3 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" (!) No manual steps provided. Please take a screenshot of this"
                " window and send an email to",
                f" (!) No se proporcionan pasos "
                "manuales. Por favor, tome una captura de pantalla de esta ventana"
                " y enviar un correo electrónico a",
            ][lang_idx],
        )
        pro_lbl3.grid(row=2, column=0, padx=PADX, pady=(0, 0), sticky="nsw")
        pro_lbl4 = customtkinter.CTkLabel(
            pro_frm_2,
            text="peter@addaxdatascience.com",
            cursor="hand2",
            font=url_label_font,
        )
        pro_lbl4.grid(
            row=3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl4.bind(
            "<Button-1>", lambda e: callback("mailto:peter@addaxdatascience.com")
        )
        show_next_steps = False

    if show_next_steps:
        # general steps
        pro_lbl7 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Make sure you can view hidden files in your file explorer.",
                f" {step_n}. Asegúrate de que puedes ver los archivos ocultos en tu explorador de archivos.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl7.grid(
            row=pro_lbl5_row + 1, column=0, padx=PADX, pady=(0, 0), sticky="nsw"
        )
        pro_lbl8 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Move the downloaded file(s) into the folder:",
                f" {step_n}. Mueva los archivos descargados a la carpeta:",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl8.grid(
            row=pro_lbl5_row + 2, column=0, padx=PADX, pady=(0, 0), sticky="nsw"
        )
        pro_lbl9 = customtkinter.CTkLabel(pro_frm_2, text=f"'{model_dir}'")
        pro_lbl9.grid(
            row=pro_lbl5_row + 3,
            column=0,
            padx=(PADX * 4, PADX),
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )
        pro_lbl10 = customtkinter.CTkLabel(
            pro_frm_2,
            text=[
                f" {step_n}. Close AddaxAI and try again.",
                f" {step_n}. Cierre AddaxAI e inténtelo de nuevo.",
            ][lang_idx],
        )
        step_n += 1
        pro_lbl10.grid(
            row=pro_lbl5_row + 4,
            column=0,
            padx=PADX,
            pady=(PADY / 8, PADY / 8),
            sticky="nsw",
        )

        # close AddaxAI
        btns_frm2 = customtkinter.CTkFrame(master=de_root)
        btns_frm2.columnconfigure(0, weight=1, minsize=10)
        btns_frm2.grid(row=6, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
        close_btn = customtkinter.CTkButton(
            btns_frm2,
            text=["Close AddaxAI", "Cerrar AddaxAI"][lang_idx],
            command=on_toplevel_close,
        )
        close_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")


# open window with env info
def show_download_error_window_env(model_title, model_dir, model_vars):
    # create window
    de_root = customtkinter.CTkToplevel(root)
    de_root.title(["Download error", "Error de descarga"][lang_idx])
    de_root.geometry("+10+10")
    bring_window_to_top_but_not_for_ever(de_root)

    # main label
    lbl2 = customtkinter.CTkLabel(
        de_root, text=f"{model_title.capitalize()} download error", font=main_label_font
    )
    lbl2.grid(row=0, column=0, padx=PADX, pady=(PADY, 0), columnspan=2, sticky="nswe")
    lbl2 = customtkinter.CTkLabel(
        de_root,
        text=[
            "Something went wrong while trying to download the virtual environment. This can have "
            "several causes.",
            "Algo salió mal al intentar descargar el modelo. Esto "
            "puede tener varias causas.",
        ][lang_idx],
    )
    lbl2.grid(
        row=1, column=0, padx=PADX, pady=(0, PADY / 2), columnspan=2, sticky="nswe"
    )

    # internet connection frame
    int_frm_1 = customtkinter.CTkFrame(master=de_root)
    int_frm_1.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    int_frm_1.columnconfigure(0, weight=1, minsize=700)
    int_frm_2 = customtkinter.CTkFrame(master=int_frm_1)
    int_frm_2.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    int_frm_2.columnconfigure(0, weight=1, minsize=700)
    int_lbl = customtkinter.CTkLabel(
        int_frm_1,
        text=[" 1. Internet connection", " 1. Conexión a Internet"][lang_idx],
        font=main_label_font,
    )
    int_lbl.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nsw")
    int_txt_1 = customtkinter.CTkTextbox(
        master=int_frm_2,
        corner_radius=10,
        height=55,
        wrap="word",
        fg_color="transparent",
    )
    int_txt_1.grid(row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), sticky="nswe")
    int_txt_1.insert(
        END,
        [
            "Check if you have a stable internet connection. If possible, try again on a fibre internet "
            "connection, or perhaps on a different, stronger, Wi-Fi network. Sometimes connecting to an "
            "open network such as a mobile hotspot can do the trick.",
            "Comprueba si tienes una conexión "
            "a Internet estable. Si es posible, inténtalo de nuevo con una conexión de fibra o quizás con "
            "otra red Wi-Fi más potente. A veces, conectarse a una red abierta, como un hotspot móvil, "
            "puede funcionar.",
        ][lang_idx],
    )

    # protection software frame
    pro_frm_1 = customtkinter.CTkFrame(master=de_root)
    pro_frm_1.grid(row=3, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    pro_frm_1.columnconfigure(0, weight=1, minsize=700)
    pro_frm_2 = customtkinter.CTkFrame(master=pro_frm_1)
    pro_frm_2.grid(row=2, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    pro_frm_2.columnconfigure(0, weight=1, minsize=700)
    pro_lbl = customtkinter.CTkLabel(
        pro_frm_1,
        text=[" 2. Protection software", " 2. Software de protección"][lang_idx],
        font=main_label_font,
    )
    pro_lbl.grid(row=0, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nsw")
    pro_txt_1 = customtkinter.CTkTextbox(
        master=pro_frm_2,
        corner_radius=10,
        height=55,
        wrap="word",
        fg_color="transparent",
    )
    pro_txt_1.grid(row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), sticky="nswe")
    pro_txt_1.insert(
        END,
        [
            "Some firewall, proxy or VPN settings might block the internet connection. Try again with this "
            "protection software disabled.",
            "Algunas configuraciones de cortafuegos, proxy o VPN podrían "
            "bloquear la conexión a Internet. Inténtalo de nuevo con este software de protección "
            "desactivado.",
        ][lang_idx],
    )


# open frame to select species for advanc mode
def open_species_selection():
    # retrieve model specific variable values
    model_vars = load_model_vars()
    all_classes = model_vars["all_classes"]
    selected_classes = model_vars["selected_classes"]

    # on window closing
    def save():
        selected_classes = scrollable_checkbox_frame.get_checked_items()
        dsp_choose_classes.configure(
            text=f"{len(selected_classes)} of {len(all_classes)}"
        )
        write_model_vars(new_values={"selected_classes": selected_classes})
        model_cls_animal_options(var_cls_model.get())
        ss_root.withdraw()

    # on seleciton change
    def on_selection():
        selected_classes = scrollable_checkbox_frame.get_checked_items()
        lbl2.configure(
            text=f"{['Selected', 'Seleccionadas'][lang_idx]} {len(selected_classes)} {['of', 'de'][lang_idx]} {len(all_classes)}"
        )

    # create window
    ss_root = customtkinter.CTkToplevel(root)
    ss_root.title("Species selection")
    ss_root.geometry("+10+10")
    bring_window_to_top_but_not_for_ever(ss_root)
    spp_frm_1 = customtkinter.CTkFrame(master=ss_root)
    spp_frm_1.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    spp_frm = customtkinter.CTkFrame(master=spp_frm_1, width=1000)
    spp_frm.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    lbl1 = customtkinter.CTkLabel(
        spp_frm,
        text=[
            "Which species are present in your project area?",
            "¿Qué especies están presentes en la zona de su proyecto?",
        ][lang_idx],
        font=main_label_font,
    )
    lbl1.grid(row=0, column=0, padx=2 * PADX, pady=PADY, columnspan=2, sticky="nsw")
    lbl2 = customtkinter.CTkLabel(spp_frm, text="")
    lbl2.grid(row=1, column=0, padx=2 * PADX, pady=0, columnspan=2, sticky="nsw")
    scrollable_checkbox_frame = SpeciesSelectionFrame(
        master=spp_frm,
        command=on_selection,
        height=400,
        width=500,
        all_classes=all_classes,
        selected_classes=selected_classes,
    )
    scrollable_checkbox_frame._scrollbar.configure(height=0)
    scrollable_checkbox_frame.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="ew")

    # toggle selection count with dummy event
    on_selection()

    # catch window close events
    close_button = customtkinter.CTkButton(ss_root, text="OK", command=save)
    close_button.grid(
        row=3, column=0, padx=PADX, pady=(0, PADY), columnspan=2, sticky="nswe"
    )
    ss_root.protocol("WM_DELETE_WINDOW", save)


class MyMainFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        if scale_factor != 1.0:
            self.columnconfigure(
                0, weight=1, minsize=70 * round(scale_factor * 1.35, 2)
            )
            self.columnconfigure(
                1, weight=1, minsize=350 * round(scale_factor * 1.35, 2)
            )
        else:
            self.columnconfigure(0, weight=1, minsize=70)
            self.columnconfigure(1, weight=1, minsize=350)


class MySubFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1, minsize=250)
        self.columnconfigure(1, weight=1, minsize=250)


class MySubSubFrame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


class InfoButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=("#ebebeb", "#333333"),
            hover=False,
            text_color=("grey", "grey"),
            height=1,
            width=1,
        )


def sim_dir_show_info():
    mb.showinfo(
        title=information_txt[lang_idx],
        message=["Select the images to analyse", "Seleccionar las imágenes a analizar"][
            lang_idx
        ],
        detail=[
            "Here you can select a folder containing camera trap images. It will process all images it can find, also in subfolders."
            " Switch to advanced mode for more options.",
            " Aquí puede seleccionar una carpeta que contenga imágenes de cámaras trampa."
            " Procesará todas las imágenes que encuentre, también en las subcarpetas. Cambia al modo avanzado para más opciones.",
        ][lang_idx],
    )


def callback(url):
    webbrowser.open_new(url)


def sim_spp_show_info():
    mb.showinfo(
        title=information_txt[lang_idx],
        message=[
            "Select the species that are present",
            "Seleccione las especies presentes",
        ][lang_idx],
        detail=[
            "Here, you can select and deselect the animals categories that are present in your project"
            " area. If the animal category is not selected, it will be excluded from the results. The "
            "category list will update according to the model selected.",
            "Aquí puede seleccionar y anular"
            " la selección de las categorías de animales presentes en la zona de su proyecto. Si la "
            "categoría de animales no está seleccionada, quedará excluida de los resultados. La lista de "
            "categorías se actualizará según el modelo seleccionado.",
        ][lang_idx],
    )


def on_spp_selection():
    selected_classes = sim_spp_scr.get_checked_items()
    all_classes = sim_spp_scr.get_all_items()
    write_model_vars(new_values={"selected_classes": selected_classes})
    dsp_choose_classes.configure(text=f"{len(selected_classes)} of {len(all_classes)}")


def sim_mdl_show_info():
    if var_cls_model.get() in none_txt:
        mb.showinfo(
            title=information_txt[lang_idx],
            message=[
                "Select the model to identify animals",
                "Seleccione el modelo para identificar animales",
            ][lang_idx],
            detail=[
                "Here, you can choose a model that can identify your target species. If you select ‘None’, it will find vehicles,"
                " people, and animals, but will not further identify them. When a model is selected, press this button again to "
                "read more about the model in question.",
                "Aquí, puede elegir un modelo que pueda identificar su especie objetivo."
                " Si selecciona 'Ninguno', encontrará vehículos, personas y animales, pero no los identificará más. Cuando haya "
                "seleccionado un modelo, vuelva a pulsar este botón para obtener más información sobre el modelo en cuestión.",
            ][lang_idx],
        )
    else:
        show_model_info()


def checkbox_frame_event():
    print(f"checkbox frame modified: {sim_spp_scr.get_checked_items()}")


# class to list species with checkboxes
class SpeciesSelectionFrame(customtkinter.CTkScrollableFrame):
    def __init__(
        self,
        master,
        all_classes=[],
        selected_classes=[],
        command=None,
        dummy_spp=False,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.dummy_spp = dummy_spp
        if dummy_spp:
            all_classes = [
                f"{['Species', 'Especies'][lang_idx]} {i + 1}" for i in range(10)
            ]
        self.command = command
        self.checkbox_list = []
        self.selected_classes = selected_classes
        for item in all_classes:
            self.add_item(item)

    def add_item(self, item):
        checkbox = customtkinter.CTkCheckBox(self, text=item)
        if self.dummy_spp:
            checkbox.configure(state="disabled")
        if item in self.selected_classes:
            checkbox.select()
        if self.command is not None:
            checkbox.configure(command=self.command)
        checkbox.grid(row=len(self.checkbox_list), column=0, pady=PADY, sticky="nsw")
        self.checkbox_list.append(checkbox)

    def get_checked_items(self):
        return [
            checkbox.cget("text")
            for checkbox in self.checkbox_list
            if checkbox.get() == 1
        ]

    def get_all_items(self):
        return [checkbox.cget("text") for checkbox in self.checkbox_list]


def open_nosleep_page():
    webbrowser.open("https://nosleep.page")


# show download and extract progress for environments
class EnvDownloadProgressWindow:
    def __init__(self, env_title, total_size_str):
        self.dm_root = customtkinter.CTkToplevel(root)
        self.dm_root.title("Download progress")
        self.dm_root.geometry("+10+10")
        self.frm = customtkinter.CTkFrame(master=self.dm_root)
        self.frm.grid(row=3, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nswe")
        self.frm.columnconfigure(0, weight=1, minsize=500 * scale_factor)

        self.lbl = customtkinter.CTkLabel(
            self.dm_root,
            text=[
                f"Downloading environment '{env_title}' ({total_size_str})",
                f"Descargar entorno '{env_title}' ({total_size_str})",
            ][lang_idx],
            font=customtkinter.CTkFont(family="CTkFont", size=14, weight="bold"),
        )
        self.lbl.grid(row=0, column=0, padx=PADX, pady=(0, 0), sticky="nsew")

        self.war = customtkinter.CTkLabel(
            self.dm_root,
            text=[
                "Please prevent computer from sleeping during the download.",
                "Por favor, evite que el ordenador se duerma durante la descarga.",
            ][lang_idx],
        )
        self.war.grid(row=1, column=0, padx=PADX, pady=0, sticky="nswe")

        self.but = CancelButton(
            self.dm_root,
            text=[
                "  Prevent sleep with online tool ",
                "  Usar prevención de sueño en línea  ",
            ][lang_idx],
            command=open_nosleep_page,
        )
        self.but.grid(row=2, column=0, padx=PADX, pady=(PADY / 2, 0), sticky="")

        # Label for Downloading Progress
        self.lbl_download = customtkinter.CTkLabel(
            self.frm, text=["Downloading...", "Descargando..."][lang_idx]
        )
        self.lbl_download.grid(row=1, column=0, padx=PADX, pady=(0, 0), sticky="nsew")

        # Progress bar for downloading
        self.pbr_download = customtkinter.CTkProgressBar(
            self.frm, orientation="horizontal", height=22, corner_radius=5, width=1
        )
        self.pbr_download.set(0)
        self.pbr_download.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="nsew")

        self.per_download = customtkinter.CTkLabel(
            self.frm,
            text=f" 0% ",
            height=5,
            fg_color=("#949BA2", "#4B4D50"),
            text_color="white",
        )
        self.per_download.grid(row=2, column=0, padx=PADX, pady=PADY, sticky="")

        # Label for Extraction Progress
        self.lbl_extraction = customtkinter.CTkLabel(
            self.frm, text=["Extracting...", "Extrayendo..."][lang_idx]
        )
        self.lbl_extraction.grid(row=3, column=0, padx=PADX, pady=(0, 0), sticky="nsew")

        # Progress bar for extraction
        self.pbr_extraction = customtkinter.CTkProgressBar(
            self.frm, orientation="horizontal", height=22, corner_radius=5, width=1
        )
        self.pbr_extraction.set(0)
        self.pbr_extraction.grid(row=4, column=0, padx=PADX, pady=PADY, sticky="nsew")

        self.per_extraction = customtkinter.CTkLabel(
            self.frm,
            text=f" 0% ",
            height=5,
            fg_color=("#949BA2", "#4B4D50"),
            text_color="white",
        )
        self.per_extraction.grid(row=4, column=0, padx=PADX, pady=PADY, sticky="")

        self.dm_root.withdraw()

    def open(self):
        self.dm_root.update()
        self.dm_root.deiconify()

    def update_download_progress(self, percentage):
        self.pbr_download.set(percentage)
        self.per_download.configure(text=f" {round(percentage * 100)}% ")
        if percentage > 0.5:
            self.per_download.configure(fg_color=(green_primary, "#1F6BA5"))
        else:
            self.per_download.configure(fg_color=("#949BA2", "#4B4D50"))
        self.dm_root.update()

    def update_extraction_progress(self, percentage):
        self.pbr_extraction.set(percentage)
        self.per_extraction.configure(text=f" {round(percentage * 100)}% ")
        if percentage > 0.5:
            self.per_extraction.configure(fg_color=(green_primary, "#1F6BA5"))
        else:
            self.per_extraction.configure(fg_color=("#949BA2", "#4B4D50"))
        self.dm_root.update()

    def close(self):
        self.dm_root.destroy()


# show download progress for model files
class ModelDownloadProgressWindow:
    def __init__(self, model_title, total_size_str):
        self.dm_root = customtkinter.CTkToplevel(root)
        self.dm_root.title("Download progress")
        self.dm_root.geometry("+10+10")
        self.frm = customtkinter.CTkFrame(master=self.dm_root)
        self.frm.grid(row=3, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nswe")
        self.frm.columnconfigure(0, weight=1, minsize=500 * scale_factor)
        self.lbl = customtkinter.CTkLabel(
            self.dm_root,
            text=[
                f"Downloading model '{model_title}' ({total_size_str})",
                f"Descargar modelo '{model_title}' ({total_size_str})",
            ][lang_idx],
            font=customtkinter.CTkFont(family="CTkFont", size=14, weight="bold"),
        )
        self.lbl.grid(row=0, column=0, padx=PADX, pady=(0, 0), sticky="nsew")
        self.war = customtkinter.CTkLabel(
            self.dm_root,
            text=[
                "Please prevent computer from sleeping during the download.",
                "Por favor, evite que el ordenador se duerma durante la descarga.",
            ][lang_idx],
        )
        self.war.grid(row=1, column=0, padx=PADX, pady=0, sticky="nswe")
        self.but = CancelButton(
            self.dm_root,
            text=[
                "  Prevent sleep with online tool ",
                "  Usar prevención de sueño en línea  ",
            ][lang_idx],
            command=open_nosleep_page,
        )
        self.but.grid(row=2, column=0, padx=PADX, pady=(PADY / 2, 0), sticky="")
        self.pbr = customtkinter.CTkProgressBar(
            self.frm, orientation="horizontal", height=22, corner_radius=5, width=1
        )
        self.pbr.set(0)
        self.pbr.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="nsew")
        self.per = customtkinter.CTkLabel(
            self.frm,
            text=f" 0% ",
            height=5,
            fg_color=("#949BA2", "#4B4D50"),
            text_color="white",
        )
        self.per.grid(row=1, column=0, padx=PADX, pady=PADY, sticky="")
        self.dm_root.withdraw()

    def open(self):
        self.dm_root.update()
        self.dm_root.deiconify()

    def update_progress(self, percentage):
        self.pbr.set(percentage)
        self.per.configure(text=f" {round(percentage * 100)}% ")
        if percentage > 0.5:
            self.per.configure(fg_color=(green_primary, "#1F6BA5"))
        else:
            self.per.configure(fg_color=("#949BA2", "#4B4D50"))
        self.dm_root.update()

    def close(self):
        self.dm_root.destroy()


# make sure the window pops up in front initially, but does not stay on top if the users selects an other window
def bring_window_to_top_but_not_for_ever(master):
    def lift_toplevel():
        master.lift()
        master.attributes("-topmost", False)

    master.attributes("-topmost", True)
    master.after(1000, lift_toplevel)


# bunch of functions to keep track of the number of times the application has been launched
# the donation popup window will show every 5th launch
def load_launch_count():
    if not os.path.exists(launch_count_file):
        with open(launch_count_file, "w") as f:
            json.dump({"count": 0}, f)
    with open(launch_count_file, "r") as f:
        data = json.load(f)
        count = data.get("count", 0)
        print(f"Launch count: {count}")
        return count


def save_launch_count(count):
    with open(launch_count_file, "w") as f:
        json.dump({"count": count}, f)


def check_donation_window_popup():
    launch_count = load_launch_count()
    launch_count += 1
    save_launch_count(launch_count)
    if launch_count % 5 == 0:
        show_donation_popup()


# show donation window
def show_donation_popup():
    # define functions
    def open_link(url):
        webbrowser.open(url)

    # define text variables
    donation_text = [
        "AddaxAI is free and open-source because we believe conservation technology should be available to everyone, regardless of budget. But keeping it that way takes time, effort, and resources—all contributed by volunteers. If you’re using AddaxAI, consider chipping in. Think of it as an honesty box: if every user contributed just $3 per month, we could sustain development, improve features, and keep expanding the model zoo.",
        "AddaxAI es gratuita y de código abierto porque creemos que la tecnología de conservación debe ser accesible para todos. Mantenerlo requiere tiempo y recursos de voluntarios. Si la usas, considera contribuir: con solo $3 al mes, podríamos seguir mejorando y ampliando el modelo de zoológico.",
    ]
    title_text = ["Open-source honesty box", "Caja de la honradez de código abierto"]
    subtitle_text = [
        "Let's keep AddaxAI free and available for everybody!",
        "¡Mantengamos AddaxAI libre y disponible para todos!",
    ]
    questions_text = [
        "Let us know if you have any questions or want to receive an invoice for tax-deduction purposes.",
        "Háganos saber si tiene alguna pregunta o desea recibir una factura para fines de deducción de impuestos.",
    ]
    email_text = "peter@addaxdatascience.com"
    btn_1_txt = ["$3 per month per user", "3$ al mes por usuario"]
    btn_2_txt = ["Choose your own amount", "Elige tu propia cantidad"]

    # create window
    do_root = customtkinter.CTkToplevel(root)
    do_root.title("Model information")
    do_root.geometry("+10+10")
    bring_window_to_top_but_not_for_ever(do_root)

    # title frame
    row_idx = 1
    frm_1 = donation_popup_frame(master=do_root)
    frm_1.grid(row=row_idx, padx=PADX, pady=PADY, sticky="nswe")
    title_lbl_1 = customtkinter.CTkLabel(
        frm_1,
        text=title_text[lang_idx],
        font=customtkinter.CTkFont(family="CTkFont", size=18, weight="bold"),
    )
    title_lbl_1.grid(row=0, padx=PADX, pady=(PADY, PADY / 2), sticky="nswe")
    descr_txt_1 = customtkinter.CTkTextbox(
        master=frm_1, corner_radius=10, height=90, wrap="word", fg_color="transparent"
    )
    descr_txt_1.grid(row=1, padx=PADX, pady=(0, 0), sticky="nswe")
    descr_txt_1.tag_config("center", justify="center")
    descr_txt_1.insert("0.0", donation_text[lang_idx], "center")
    descr_txt_1.configure(state="disabled")
    title_lbl_2 = customtkinter.CTkLabel(
        frm_1, text=subtitle_text[lang_idx], font=main_label_font
    )
    title_lbl_2.grid(row=2, padx=PADX, pady=(0, PADY), sticky="nswe")

    # buttons frame
    btns_frm = customtkinter.CTkFrame(master=do_root)
    btns_frm.columnconfigure(0, weight=1, minsize=400)
    btns_frm.columnconfigure(1, weight=1, minsize=400)
    btns_frm.grid(row=3, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    btn_1 = customtkinter.CTkButton(
        btns_frm,
        text=btn_1_txt[lang_idx],
        command=lambda: open_link("https://buy.stripe.com/00g8xx3aI93lb4c9AI"),
    )
    btn_1.grid(row=1, column=0, padx=PADX, pady=(PADY, PADY / 2), sticky="we")
    btn_2 = customtkinter.CTkButton(
        btns_frm,
        text=btn_2_txt[lang_idx],
        command=lambda: open_link(
            "https://paymentlink.mollie.com/payment/al7x0Z6k2XWvEcdTwB5c7/"
        ),
    )
    btn_2.grid(row=1, column=1, padx=(0, PADX), pady=PADY, sticky="we")
    btn_lbl_2 = customtkinter.CTkLabel(
        btns_frm, text=questions_text[lang_idx], font=italic_label_font
    )
    btn_lbl_2.grid(row=2, columnspan=4, padx=PADX, pady=(PADY / 2, 0), sticky="nswe")
    btn_lbl_4 = customtkinter.CTkLabel(
        btns_frm, text=email_text, cursor="hand2", font=url_label_font
    )
    btn_lbl_4.grid(row=3, columnspan=4, padx=PADX, pady=(0, PADY / 2), sticky="nswe")
    btn_lbl_4.bind(
        "<Button-1>", lambda e: callback("mailto:peter@addaxdatascience.com")
    )


# open window with model info
def show_model_info(title=None, model_dict=None, new_model=False):
    # fetch current selected model if title and model_dict are not supplied
    if title is None:
        title = var_cls_model.get()
    if model_dict is None:
        model_dict = load_model_vars()

    # read vars from json
    description_var = model_dict.get("description", "")
    developer_var = model_dict.get("developer", "")
    owner_var = model_dict.get("owner", "")
    classes_list = model_dict.get("all_classes", [])
    url_var = model_dict.get("info_url", "")
    min_version = model_dict.get("min_version", "1000.1")
    citation = model_dict.get("citation", "")
    citation_present = False if citation == "" else True
    license = model_dict.get("license", "")
    license_present = False if license == "" else True
    needs_EA_update_bool = needs_EA_update(min_version)
    if needs_EA_update_bool:
        update_var = f"Your current AddaxAI version (v{current_AA_version}) will not be able to run this model. An update is required."
    else:
        update_var = f"Current version of AddaxAI (v{current_AA_version}) is able to use this model. No update required."

    # define functions
    def close():
        nm_root.destroy()

    def read_more():
        webbrowser.open(url_var)

    def update():
        webbrowser.open("https://addaxdatascience.com/addaxai/#install")

    def cite():
        webbrowser.open(citation)

    def see_license():
        webbrowser.open(license)

    # create window
    nm_root = customtkinter.CTkToplevel(root)
    nm_root.title("Model information")
    nm_root.geometry("+10+10")
    bring_window_to_top_but_not_for_ever(nm_root)

    # new model label
    if new_model:
        lbl = customtkinter.CTkLabel(
            nm_root, text="New model available!", font=main_label_font
        )
        lbl.grid(
            row=0,
            column=0,
            padx=PADX,
            pady=(PADY, PADY / 4),
            columnspan=2,
            sticky="nswe",
        )

    # title frame
    row_idx = 1
    title_frm_1 = model_info_frame(master=nm_root)
    title_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=PADY, sticky="nswe")
    title_frm_2 = model_info_frame(master=title_frm_1)
    title_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    title_lbl_1 = customtkinter.CTkLabel(
        title_frm_1, text="Title", font=main_label_font
    )
    title_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    title_lbl_2 = customtkinter.CTkLabel(title_frm_2, text=title)
    title_lbl_2.grid(
        row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
    )

    # owner frame
    if owner_var != "":
        row_idx += 1
        owner_frm_1 = model_info_frame(master=nm_root)
        owner_frm_1.grid(
            row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe"
        )
        owner_frm_2 = model_info_frame(master=owner_frm_1)
        owner_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
        owner_lbl_1 = customtkinter.CTkLabel(
            owner_frm_1, text="Owner", font=main_label_font
        )
        owner_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
        owner_lbl_2 = customtkinter.CTkLabel(owner_frm_2, text=owner_var)
        owner_lbl_2.grid(
            row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
        )

    # developer frame
    row_idx += 1
    devop_frm_1 = model_info_frame(master=nm_root)
    devop_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    devop_frm_2 = model_info_frame(master=devop_frm_1)
    devop_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    devop_lbl_1 = customtkinter.CTkLabel(
        devop_frm_1, text="Developer", font=main_label_font
    )
    devop_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    devop_lbl_2 = customtkinter.CTkLabel(devop_frm_2, text=developer_var)
    devop_lbl_2.grid(
        row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
    )

    # description frame
    row_idx += 1
    descr_frm_1 = model_info_frame(master=nm_root)
    descr_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    descr_frm_2 = model_info_frame(master=descr_frm_1)
    descr_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    descr_lbl_1 = customtkinter.CTkLabel(
        descr_frm_1, text="Description", font=main_label_font
    )
    descr_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    descr_txt_1 = customtkinter.CTkTextbox(
        master=descr_frm_2,
        corner_radius=10,
        height=150,
        wrap="word",
        fg_color="transparent",
    )
    descr_txt_1.grid(
        row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), columnspan=2, sticky="nswe"
    )
    descr_txt_1.insert("0.0", description_var)
    descr_txt_1.configure(state="disabled")

    # classes frame
    row_idx += 1
    class_frm_1 = model_info_frame(master=nm_root)
    class_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    class_frm_2 = model_info_frame(master=class_frm_1)
    class_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    class_lbl_1 = customtkinter.CTkLabel(
        class_frm_1, text="Classes", font=main_label_font
    )
    class_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    class_txt_1 = customtkinter.CTkTextbox(
        master=class_frm_2,
        corner_radius=10,
        height=150,
        wrap="word",
        fg_color="transparent",
    )
    class_txt_1.grid(
        row=0, column=0, padx=PADX / 4, pady=(0, PADY / 4), columnspan=2, sticky="nswe"
    )
    for spp_class in classes_list:
        class_txt_1.insert(tk.END, f"• {spp_class}\n")
    class_txt_1.configure(state="disabled")

    # update frame
    row_idx += 1
    updat_frm_1 = model_info_frame(master=nm_root)
    updat_frm_1.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    updat_frm_2 = model_info_frame(master=updat_frm_1)
    updat_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    updat_lbl_1 = customtkinter.CTkLabel(
        updat_frm_1, text="Update", font=main_label_font
    )
    updat_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    updat_lbl_2 = customtkinter.CTkLabel(updat_frm_2, text=update_var)
    updat_lbl_2.grid(
        row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
    )

    # buttons frame
    row_idx += 1
    n_btns = 2
    if needs_EA_update_bool:
        n_btns += 1
    if citation_present:
        n_btns += 1
    if license_present:
        n_btns += 1
    btns_frm = customtkinter.CTkFrame(master=nm_root)
    for col in range(0, n_btns):
        btns_frm.columnconfigure(col, weight=1, minsize=10)
    btns_frm.grid(row=row_idx, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    close_btn = customtkinter.CTkButton(btns_frm, text="Close", command=close)
    close_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    lmore_btn = customtkinter.CTkButton(btns_frm, text="Learn more", command=read_more)
    lmore_btn.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")
    ncol = 2
    if needs_EA_update_bool:
        updat_btn = customtkinter.CTkButton(btns_frm, text="Update", command=update)
        updat_btn.grid(row=0, column=ncol, padx=(0, PADX), pady=PADY, sticky="nwse")
        ncol += 1
    if citation_present:
        citat_btn = customtkinter.CTkButton(btns_frm, text="Cite", command=cite)
        citat_btn.grid(row=0, column=ncol, padx=(0, PADX), pady=PADY, sticky="nwse")
        ncol += 1
    if license_present:
        licen_btn = customtkinter.CTkButton(
            btns_frm, text="License", command=see_license
        )
        licen_btn.grid(row=0, column=ncol, padx=(0, PADX), pady=PADY, sticky="nwse")
        ncol += 1


# class frame for model window
class model_info_frame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1, minsize=120 * scale_factor)
        self.columnconfigure(1, weight=1, minsize=500 * scale_factor)


# class frame for donation window
class donation_popup_frame(customtkinter.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1, minsize=500 * scale_factor)


# make sure the latest updated models also are listed in the dpd menu
def update_model_dropdowns():
    global dpd_options_cls_model
    cls_models = fetch_known_models(CLS_DIR)
    dpd_options_cls_model = [["None"] + cls_models, ["Ninguno"] + cls_models]
    update_dpd_options(
        dpd_cls_model,
        snd_step,
        var_cls_model,
        dpd_options_cls_model,
        model_cls_animal_options,
        row_cls_model,
        lbl_cls_model,
        lang_idx,
    )
    global dpd_options_model
    det_models = fetch_known_models(DET_DIR)
    dpd_options_model = [det_models + ["Custom model"], det_models + ["Otro modelo"]]
    update_dpd_options(
        dpd_model,
        snd_step,
        var_det_model,
        dpd_options_model,
        model_options,
        row_model,
        lbl_model,
        lang_idx,
    )
    model_cls_animal_options(var_cls_model.get())
    global sim_dpd_options_cls_model
    sim_dpd_options_cls_model = [
        [item[0] + suffixes_for_sim_none[i], *item[1:]]
        for i, item in enumerate(dpd_options_cls_model)
    ]
    update_sim_mdl_dpd()
    root.update_idletasks()


# window for quick results info while running simple mode
def show_result_info(file_path):
    # define functions
    def close():
        rs_root.withdraw()

    def more_options():
        switch_mode()
        rs_root.withdraw()

    file_path = os.path.normpath(file_path)

    # read results for xlsx file
    # some combinations of percentages raises a bug: https://github.com/matplotlib/matplotlib/issues/12820
    # hence we're going to try the nicest layout with some different angles, then an OK layout, and no
    # lines as last resort
    try:
        graph_img, table_rows = create_pie_chart(file_path, looks="nice", st_angle=0)
    except ValueError:
        print("ValueError - trying again with different params.")
        try:
            graph_img, table_rows = create_pie_chart(
                file_path, looks="nice", st_angle=23
            )
        except ValueError:
            print("ValueError - trying again with different params.")
            try:
                graph_img, table_rows = create_pie_chart(
                    file_path, looks="nice", st_angle=45
                )
            except ValueError:
                print("ValueError - trying again with different params.")
                try:
                    graph_img, table_rows = create_pie_chart(
                        file_path, looks="nice", st_angle=90
                    )
                except ValueError:
                    print("ValueError - trying again with different params.")
                    try:
                        graph_img, table_rows = create_pie_chart(
                            file_path, looks="simple"
                        )
                    except ValueError:
                        print("ValueError - trying again with different params.")
                        graph_img, table_rows = create_pie_chart(
                            file_path, looks="no-lines"
                        )

    # create window
    rs_root = customtkinter.CTkToplevel(root)
    rs_root.title("Results - quick view")
    rs_root.geometry("+10+10")
    result_bg_image = customtkinter.CTkImage(
        PIL_sidebar, size=(RESULTS_WINDOW_WIDTH, RESULTS_WINDOW_HEIGHT)
    )
    result_bg_image_label = customtkinter.CTkLabel(rs_root, image=result_bg_image)
    result_bg_image_label.grid(row=0, column=0)
    result_main_frame = customtkinter.CTkFrame(
        rs_root, corner_radius=0, fg_color="transparent"
    )
    result_main_frame.grid(row=0, column=0, sticky="ns")

    # label
    lbl1 = customtkinter.CTkLabel(
        result_main_frame,
        text=["The images are processed!", "¡Las imágenes están procesadas!"][lang_idx],
        font=main_label_font,
        height=20,
    )
    lbl1.grid(
        row=0, column=0, padx=PADX, pady=(PADY, PADY / 4), columnspan=2, sticky="nswe"
    )
    lbl2 = customtkinter.CTkLabel(
        result_main_frame,
        text=[
            f"The results and graphs are saved at '{os.path.dirname(file_path)}'.",
            f"Los resultados y gráficos se guardan en '{os.path.dirname(file_path)}'.",
        ][lang_idx],
        height=20,
    )
    lbl2.grid(
        row=1,
        column=0,
        padx=PADX,
        pady=(PADY / 4, PADY / 4),
        columnspan=2,
        sticky="nswe",
    )
    lbl3 = customtkinter.CTkLabel(
        result_main_frame,
        text=[
            f"You can find a quick overview of the results below.",
            f"A continuación encontrará un resumen de los resultados.",
        ][lang_idx],
        height=20,
    )
    lbl3.grid(
        row=2,
        column=0,
        padx=PADX,
        pady=(PADY / 4, PADY / 4),
        columnspan=2,
        sticky="nswe",
    )

    # graph frame
    graph_frm_1 = model_info_frame(master=result_main_frame)
    graph_frm_1.grid(row=3, column=0, padx=PADX, pady=PADY, sticky="nswe")
    graph_frm_2 = model_info_frame(master=graph_frm_1)
    graph_frm_2.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nswe")
    graph_lbl_1 = customtkinter.CTkLabel(
        graph_frm_1, text=["Graph", "Gráfico"][lang_idx], font=main_label_font
    )
    graph_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    graph_img = customtkinter.CTkImage(graph_img, size=(600, 300))
    graph_lbl_2 = customtkinter.CTkLabel(graph_frm_2, text="", image=graph_img)
    graph_lbl_2.grid(
        row=0, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nsw"
    )

    # table frame
    table_frm_1 = model_info_frame(master=result_main_frame)
    table_frm_1.grid(row=4, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    table_lbl_1 = customtkinter.CTkLabel(
        table_frm_1, text=["Table", "Tabla"][lang_idx], font=main_label_font
    )
    table_lbl_1.grid(row=0, column=0, padx=PADX, pady=(0, PADY / 4), sticky="nse")
    table_scr_frm = customtkinter.CTkScrollableFrame(
        table_frm_1, width=RESULTS_TABLE_WIDTH
    )
    table_scr_frm.grid(
        row=0, column=1, columnspan=3, padx=(0, PADX), pady=PADY, sticky="nesw"
    )
    table_header = CTkTable(
        master=table_scr_frm,
        column=3,
        values=[
            [
                ["Species", "Especie"][lang_idx],
                ["Count", "Cuenta"][lang_idx],
                ["Percentage", "Porcentaje"][lang_idx],
            ]
        ],
        font=main_label_font,
        color_phase="horizontal",
        header_color=customtkinter.ThemeManager.theme["CTkFrame"]["top_fg_color"],
        wraplength=130,
    )
    table_header.grid(
        row=0, column=0, padx=PADX, pady=(PADY / 4, 0), columnspan=2, sticky="nesw"
    )
    table_values = CTkTable(
        master=table_scr_frm,
        column=3,
        values=table_rows,
        color_phase="horizontal",
        wraplength=130,
        width=RESULTS_TABLE_WIDTH / 3 - PADX,
    )
    table_values.grid(
        row=1, column=0, padx=PADX, pady=(0, PADY / 4), columnspan=2, sticky="nesw"
    )

    # buttons frame
    btns_frm = customtkinter.CTkFrame(master=result_main_frame)
    btns_frm.grid(row=5, column=0, padx=PADX, pady=(0, PADY), sticky="nswe")
    btns_frm.columnconfigure(0, weight=1, minsize=10)
    btns_frm.columnconfigure(1, weight=1, minsize=10)
    btns_frm.columnconfigure(2, weight=1, minsize=10)
    btns_frm.columnconfigure(3, weight=1, minsize=10)
    close_btn = customtkinter.CTkButton(
        btns_frm, text=["Close window", "Cerrar ventana"][lang_idx], command=close
    )
    close_btn.grid(row=0, column=0, padx=PADX, pady=PADY, sticky="nswe")
    openf_btn = customtkinter.CTkButton(
        btns_frm,
        text=["See results", "Ver resultados"][lang_idx],
        command=lambda: open_file_or_folder(file_path),
    )
    openf_btn.grid(row=0, column=1, padx=(0, PADX), pady=PADY, sticky="nwse")
    seegr_dir_path = os.path.join(os.path.dirname(file_path), "graphs")
    seegr_btn = customtkinter.CTkButton(
        btns_frm,
        text=["See graphs", "Ver gráficos"][lang_idx],
        command=lambda: open_file_or_folder(seegr_dir_path),
    )
    seegr_btn.grid(row=0, column=2, padx=(0, PADX), pady=PADY, sticky="nwse")
    moreo_btn = customtkinter.CTkButton(
        btns_frm,
        text=["More options", "Otras opciones"][lang_idx],
        command=more_options,
    )
    moreo_btn.grid(row=0, column=3, padx=(0, PADX), pady=PADY, sticky="nwse")

    # place in front
    bring_window_to_top_but_not_for_ever(rs_root)


# class for simple question with buttons
class TextButtonWindow:
    def __init__(self, title, text, buttons):
        self.root = customtkinter.CTkToplevel(root)
        self.root.title(title)
        self.root.geometry("+10+10")
        bring_window_to_top_but_not_for_ever(self.root)
        self.root.protocol("WM_DELETE_WINDOW", self.user_close)

        self.text_label = tk.Label(self.root, text=text)
        self.text_label.pack(padx=10, pady=10)

        self.selected_button = None
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(padx=10, pady=10)

        for button_text in buttons:
            button = tk.Button(
                self.button_frame,
                text=button_text,
                command=lambda btn=button_text: self._button_click(btn),
            )
            button.pack(side=tk.LEFT, padx=5)

    def _button_click(self, button_text):
        self.selected_button = button_text
        self.root.quit()

    def open(self):
        self.root.mainloop()

    def user_close(self):
        self.selected_button = "EXIT"
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.open()
        self.root.destroy()
        return self.selected_button


# simple window to show progressbar
class PatienceDialog:
    def __init__(self, total, text):
        self.root = customtkinter.CTkToplevel(root)
        self.root.title("Have patience")
        self.root.geometry("+10+10")
        self.total = total
        self.text = text
        self.label = tk.Label(self.root, text=text)
        self.label.pack(pady=10)
        self.progress = ttk.Progressbar(self.root, mode="determinate", length=200)
        self.progress.pack(pady=10, padx=10)
        self.root.withdraw()

    def open(self):
        self.root.update()
        self.root.deiconify()

    def update_progress(self, current, percentage=False):
        # updating takes considerable time - only do this 100 times
        if current % math.ceil(self.total / 100) == 0:
            self.progress["value"] = (current / self.total) * 100
            if percentage:
                percentage_value = round((current / self.total) * 100)
                self.label.configure(text=f"{self.text}\n{percentage_value}%")
            else:
                self.label.configure(text=f"{self.text}\n{current} of {self.total}")
            self.root.update()

    def close(self):
        self.root.destroy()


# simple window class to pop up and be closed
class CustomWindow:
    def __init__(self, title="", text=""):
        self.title = title
        self.text = text
        self.root = None

    def open(self):
        self.root = customtkinter.CTkToplevel(root)
        self.root.title(self.title)
        self.root.geometry("+10+10")

        label = tk.Label(self.root, text=self.text)
        label.pack(padx=10, pady=10)

        self.root.update_idletasks()
        self.root.update()

    def close(self):
        self.root.destroy()


# disable annotation frame
def disable_ann_frame(row, hitl_ann_selection_frame):
    labelframe = hitl_ann_selection_frame.grid_slaves(row=row, column=3)[0]
    labelframe.configure(relief=SUNKEN)
    for widget in labelframe.winfo_children():
        widget.configure(state=DISABLED)


# enable annotation frame
def enable_ann_frame(row, hitl_ann_selection_frame):
    labelframe = hitl_ann_selection_frame.grid_slaves(row=row, column=3)[0]
    labelframe.configure(relief=RAISED)
    for widget in labelframe.winfo_children():
        widget.configure(state=NORMAL)


# show hide the annotation selection frame in the human-in-the-loop settings window
def toggle_hitl_ann_selection_frame(cmd=None):
    is_vis = hitl_ann_selection_frame.grid_info()
    if cmd == "hide":
        hitl_ann_selection_frame.grid_remove()
    else:
        if is_vis != {}:
            hitl_ann_selection_frame.grid_remove()
        else:
            hitl_ann_selection_frame.grid(column=0, row=2, columnspan=2, sticky="ew")
    hitl_settings_window.update()
    hitl_settings_canvas.configure(scrollregion=hitl_settings_canvas.bbox("all"))


# enable or disable the options in the human-in-the-loop annotation selection frame
def toggle_hitl_ann_selection(rad_ann_var, hitl_ann_selection_frame):
    rad_ann_var = rad_ann_var.get()
    cols, rows = hitl_ann_selection_frame.grid_size()
    if rad_ann_var == 1:
        enable_ann_frame(1, hitl_ann_selection_frame)
        for row in range(2, rows):
            disable_ann_frame(row, hitl_ann_selection_frame)
    elif rad_ann_var == 2:
        disable_ann_frame(1, hitl_ann_selection_frame)
        for row in range(2, rows):
            enable_ann_frame(row, hitl_ann_selection_frame)


# update counts of the subset functions of the human-in-the-loop image selection frame
def enable_amt_per_ent(row):
    global selection_dict
    rad_var = selection_dict[row]["rad_var"].get()
    ent_per = selection_dict[row]["ent_per"]
    ent_amt = selection_dict[row]["ent_amt"]
    if rad_var == 1:
        ent_per.configure(state=DISABLED)
        ent_amt.configure(state=DISABLED)
    if rad_var == 2:
        ent_per.configure(state=NORMAL)
        ent_amt.configure(state=DISABLED)
    if rad_var == 3:
        ent_per.configure(state=DISABLED)
        ent_amt.configure(state=NORMAL)


# show or hide widgets in the human-in-the-loop image selection frame
def enable_selection_widgets(row):
    global selection_dict
    frame = selection_dict[row]["frame"]
    chb_var = selection_dict[row]["chb_var"].get()
    lbl_class = selection_dict[row]["lbl_class"]
    rsl = selection_dict[row]["range_slider_widget"]
    rad_all = selection_dict[row]["rad_all"]
    rad_per = selection_dict[row]["rad_per"]
    rad_amt = selection_dict[row]["rad_amt"]
    lbl_n_img = selection_dict[row]["lbl_n_img"]
    if chb_var:
        frame.configure(relief=RAISED)
        lbl_class.configure(state=NORMAL)
        rsl.grid(row=0, rowspan=3, column=2)
        rad_all.configure(state=NORMAL)
        rad_per.configure(state=NORMAL)
        rad_amt.configure(state=NORMAL)
        lbl_n_img.configure(state=NORMAL)
    else:
        frame.configure(relief=SUNKEN)
        lbl_class.configure(state=DISABLED)
        rsl.grid_remove()
        rad_all.configure(state=DISABLED)
        rad_per.configure(state=DISABLED)
        rad_amt.configure(state=DISABLED)
        lbl_n_img.configure(state=DISABLED)


# front end class for cancel button
class CancelButton(customtkinter.CTkButton):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(
            fg_color=("#ebeaea", "#4B4D50"),
            hover_color=("#939aa2", "#2B2B2B"),
            text_color=("black", "white"),
            height=10,
            width=120,
        )


# open progress window for deploy and postprocess
class ProgressWindow:
    def __init__(self, processes):
        self.progress_top_level_window = customtkinter.CTkToplevel()
        self.progress_top_level_window.title("Analysis progress")
        self.progress_top_level_window.geometry("+10+10")
        lbl_height = 12
        pbr_height = 22
        ttl_font = customtkinter.CTkFont(family="CTkFont", size=13, weight="bold")
        self.pady_progress_window = PADY / 1.5
        self.padx_progress_window = PADX / 1.5

        # language settings
        in_queue_txt = ["In queue", "En cola"]
        checking_fpaths_txt = [
            "Checking file paths",
            "Comprobación de rutas de archivos",
        ]
        processing_image_txt = ["Processing image", "Procesamiento de imágenes"]
        processing_animal_txt = ["Processing animal", "Procesamiento de animales"]
        processing_unknown_txt = ["Processing", "Procesamiento"]
        images_per_second_txt = ["Images per second", "Imágenes por segundo"]
        animals_per_second_txt = ["Animals per second", "Animales por segundo"]
        frames_per_second_txt = ["Frames per second", "Fotogramas por segundo"]
        elapsed_time_txt = ["Elapsed time", "Tiempo transcurrido"]
        remaining_time_txt = ["Remaining time", "Tiempo restante"]
        running_on_txt = ["Running on", "Funcionando en"]

        # clarify titles if both images and videos are being processed
        if "img_det" in processes and "vid_det" in processes:
            img_det_extra_string = [" in images", " en imágenes"][lang_idx]
            vid_det_extra_string = [" in videos", " en vídeos"][lang_idx]
        else:
            img_det_extra_string = ""
            vid_det_extra_string = ""
        if "img_pst" in processes and "vid_pst" in processes:
            img_pst_extra_string = [" images", " de imágenes"][lang_idx]
            vid_pst_extra_string = [" videos", " de vídeos"][lang_idx]
        else:
            img_pst_extra_string = ""
            vid_pst_extra_string = ""

        # initialise image detection process
        if "img_det" in processes:
            self.img_det_frm = customtkinter.CTkFrame(
                master=self.progress_top_level_window
            )
            self.img_det_frm.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            img_det_ttl_txt = [
                f"Locating animals{img_det_extra_string}...",
                f"Localización de animales{img_det_extra_string}...",
            ]
            self.img_det_ttl = customtkinter.CTkLabel(
                self.img_det_frm, text=img_det_ttl_txt[lang_idx], font=ttl_font
            )
            self.img_det_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.img_det_sub_frm = customtkinter.CTkFrame(master=self.img_det_frm)
            self.img_det_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.img_det_sub_frm.columnconfigure(
                0, weight=1, minsize=300 * scale_factor
            )
            self.img_det_pbr = customtkinter.CTkProgressBar(
                self.img_det_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.img_det_pbr.set(0)
            self.img_det_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.img_det_per = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.img_det_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.img_det_wai_lbl = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                height=lbl_height,
                text=checking_fpaths_txt[lang_idx],
            )
            self.img_det_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.img_det_num_lbl = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                height=lbl_height,
                text=f"{processing_image_txt[lang_idx]}:",
            )
            self.img_det_num_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_det_num_lbl.grid_remove()
            self.img_det_num_val = customtkinter.CTkLabel(
                self.img_det_sub_frm, height=lbl_height, text=f""
            )
            self.img_det_num_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_det_num_val.grid_remove()
            self.img_det_ela_lbl = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.img_det_ela_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_det_ela_lbl.grid_remove()
            self.img_det_ela_val = customtkinter.CTkLabel(
                self.img_det_sub_frm, height=lbl_height, text=f""
            )
            self.img_det_ela_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_det_ela_val.grid_remove()
            self.img_det_rem_lbl = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.img_det_rem_lbl.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_det_rem_lbl.grid_remove()
            self.img_det_rem_val = customtkinter.CTkLabel(
                self.img_det_sub_frm, height=lbl_height, text=f""
            )
            self.img_det_rem_val.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_det_rem_val.grid_remove()
            self.img_det_spe_lbl = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                height=lbl_height,
                text=f"{images_per_second_txt[lang_idx]}:",
            )
            self.img_det_spe_lbl.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_det_spe_lbl.grid_remove()
            self.img_det_spe_val = customtkinter.CTkLabel(
                self.img_det_sub_frm, height=lbl_height, text=f""
            )
            self.img_det_spe_val.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_det_spe_val.grid_remove()
            self.img_det_hwa_lbl = customtkinter.CTkLabel(
                self.img_det_sub_frm,
                height=lbl_height,
                text=f"{running_on_txt[lang_idx]}:",
            )
            self.img_det_hwa_lbl.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_det_hwa_lbl.grid_remove()
            self.img_det_hwa_val = customtkinter.CTkLabel(
                self.img_det_sub_frm, height=lbl_height, text=f""
            )
            self.img_det_hwa_val.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_det_hwa_val.grid_remove()
            self.img_det_can_btn = CancelButton(
                master=self.img_det_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.img_det_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.img_det_can_btn.grid_remove()

        # initialise image classification process
        if "img_cls" in processes:
            self.img_cls_frm = customtkinter.CTkFrame(
                master=self.progress_top_level_window
            )
            self.img_cls_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            img_cls_ttl_txt = [
                f"Identifying animals{img_det_extra_string}...",
                f"Identificación de animales{img_det_extra_string}...",
            ]
            self.img_cls_ttl = customtkinter.CTkLabel(
                self.img_cls_frm, text=img_cls_ttl_txt[lang_idx], font=ttl_font
            )
            self.img_cls_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.img_cls_sub_frm = customtkinter.CTkFrame(master=self.img_cls_frm)
            self.img_cls_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.img_cls_sub_frm.columnconfigure(
                0, weight=1, minsize=300 * scale_factor
            )
            self.img_cls_pbr = customtkinter.CTkProgressBar(
                self.img_cls_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.img_cls_pbr.set(0)
            self.img_cls_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.img_cls_per = customtkinter.CTkLabel(
                self.img_cls_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.img_cls_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.img_cls_wai_lbl = customtkinter.CTkLabel(
                self.img_cls_sub_frm, height=lbl_height, text=in_queue_txt[lang_idx]
            )
            self.img_cls_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.img_cls_num_lbl = customtkinter.CTkLabel(
                self.img_cls_sub_frm,
                height=lbl_height,
                text=f"{processing_animal_txt[lang_idx]}:",
            )
            self.img_cls_num_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_cls_num_lbl.grid_remove()
            self.img_cls_num_val = customtkinter.CTkLabel(
                self.img_cls_sub_frm, height=lbl_height, text=f""
            )
            self.img_cls_num_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_cls_num_val.grid_remove()
            self.img_cls_ela_lbl = customtkinter.CTkLabel(
                self.img_cls_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.img_cls_ela_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_cls_ela_lbl.grid_remove()
            self.img_cls_ela_val = customtkinter.CTkLabel(
                self.img_cls_sub_frm, height=lbl_height, text=f""
            )
            self.img_cls_ela_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_cls_ela_val.grid_remove()
            self.img_cls_rem_lbl = customtkinter.CTkLabel(
                self.img_cls_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.img_cls_rem_lbl.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_cls_rem_lbl.grid_remove()
            self.img_cls_rem_val = customtkinter.CTkLabel(
                self.img_cls_sub_frm, height=lbl_height, text=f""
            )
            self.img_cls_rem_val.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_cls_rem_val.grid_remove()
            self.img_cls_spe_lbl = customtkinter.CTkLabel(
                self.img_cls_sub_frm,
                height=lbl_height,
                text=f"{animals_per_second_txt[lang_idx]}:",
            )
            self.img_cls_spe_lbl.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_cls_spe_lbl.grid_remove()
            self.img_cls_spe_val = customtkinter.CTkLabel(
                self.img_cls_sub_frm, height=lbl_height, text=f""
            )
            self.img_cls_spe_val.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_cls_spe_val.grid_remove()
            self.img_cls_hwa_lbl = customtkinter.CTkLabel(
                self.img_cls_sub_frm,
                height=lbl_height,
                text=f"{running_on_txt[lang_idx]}:",
            )
            self.img_cls_hwa_lbl.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_cls_hwa_lbl.grid_remove()
            self.img_cls_hwa_val = customtkinter.CTkLabel(
                self.img_cls_sub_frm, height=lbl_height, text=f""
            )
            self.img_cls_hwa_val.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_cls_hwa_val.grid_remove()
            self.img_cls_can_btn = CancelButton(
                master=self.img_cls_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.img_cls_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.img_cls_can_btn.grid_remove()
