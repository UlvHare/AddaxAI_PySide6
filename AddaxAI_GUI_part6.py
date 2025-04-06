
        # initialise video detection process
        if "vid_det" in processes:
            self.vid_det_frm = customtkinter.CTkFrame(
                master=self.progress_top_level_window
            )
            self.vid_det_frm.grid(
                row=2,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            vid_det_ttl_txt = [
                f"Locating animals{vid_det_extra_string}...",
                f"Localización de animales{vid_det_extra_string}...",
            ]
            self.vid_det_ttl = customtkinter.CTkLabel(
                self.vid_det_frm, text=vid_det_ttl_txt[lang_idx], font=ttl_font
            )
            self.vid_det_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.vid_det_sub_frm = customtkinter.CTkFrame(master=self.vid_det_frm)
            self.vid_det_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.vid_det_sub_frm.columnconfigure(
                0, weight=1, minsize=300 * scale_factor
            )
            self.vid_det_pbr = customtkinter.CTkProgressBar(
                self.vid_det_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.vid_det_pbr.set(0)
            self.vid_det_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.vid_det_per = customtkinter.CTkLabel(
                self.vid_det_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.vid_det_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.vid_det_wai_lbl = customtkinter.CTkLabel(
                self.vid_det_sub_frm, height=lbl_height, text=in_queue_txt[lang_idx]
            )
            self.vid_det_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.vid_det_num_lbl = customtkinter.CTkLabel(
                self.vid_det_sub_frm,
                height=lbl_height,
                text=f"{processing_unknown_txt[lang_idx]}:",
            )
            self.vid_det_num_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_det_num_lbl.grid_remove()
            self.vid_det_num_val = customtkinter.CTkLabel(
                self.vid_det_sub_frm, height=lbl_height, text=f""
            )
            self.vid_det_num_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_det_num_val.grid_remove()
            self.vid_det_ela_lbl = customtkinter.CTkLabel(
                self.vid_det_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.vid_det_ela_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_det_ela_lbl.grid_remove()
            self.vid_det_ela_val = customtkinter.CTkLabel(
                self.vid_det_sub_frm, height=lbl_height, text=f""
            )
            self.vid_det_ela_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_det_ela_val.grid_remove()
            self.vid_det_rem_lbl = customtkinter.CTkLabel(
                self.vid_det_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.vid_det_rem_lbl.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_det_rem_lbl.grid_remove()
            self.vid_det_rem_val = customtkinter.CTkLabel(
                self.vid_det_sub_frm, height=lbl_height, text=f""
            )
            self.vid_det_rem_val.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_det_rem_val.grid_remove()
            self.vid_det_spe_lbl = customtkinter.CTkLabel(
                self.vid_det_sub_frm,
                height=lbl_height,
                text=f"{frames_per_second_txt[lang_idx]}:",
            )
            self.vid_det_spe_lbl.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_det_spe_lbl.grid_remove()
            self.vid_det_spe_val = customtkinter.CTkLabel(
                self.vid_det_sub_frm, height=lbl_height, text=f""
            )
            self.vid_det_spe_val.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_det_spe_val.grid_remove()
            self.vid_det_hwa_lbl = customtkinter.CTkLabel(
                self.vid_det_sub_frm,
                height=lbl_height,
                text=f"{running_on_txt[lang_idx]}:",
            )
            self.vid_det_hwa_lbl.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_det_hwa_lbl.grid_remove()
            self.vid_det_hwa_val = customtkinter.CTkLabel(
                self.vid_det_sub_frm, height=lbl_height, text=f""
            )
            self.vid_det_hwa_val.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_det_hwa_val.grid_remove()
            self.vid_det_can_btn = CancelButton(
                master=self.vid_det_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.vid_det_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.vid_det_can_btn.grid_remove()

        # initialise video classification process
        if "vid_cls" in processes:
            self.vid_cls_frm = customtkinter.CTkFrame(
                master=self.progress_top_level_window
            )
            self.vid_cls_frm.grid(
                row=3,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            vid_cls_ttl_txt = [
                f"Identifying animals{vid_det_extra_string}...",
                f"Identificación de animales{vid_det_extra_string}...",
            ]
            self.vid_cls_ttl = customtkinter.CTkLabel(
                self.vid_cls_frm, text=vid_cls_ttl_txt[lang_idx], font=ttl_font
            )
            self.vid_cls_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.vid_cls_sub_frm = customtkinter.CTkFrame(master=self.vid_cls_frm)
            self.vid_cls_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.vid_cls_sub_frm.columnconfigure(
                0, weight=1, minsize=300 * scale_factor
            )
            self.vid_cls_pbr = customtkinter.CTkProgressBar(
                self.vid_cls_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.vid_cls_pbr.set(0)
            self.vid_cls_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.vid_cls_per = customtkinter.CTkLabel(
                self.vid_cls_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.vid_cls_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.vid_cls_wai_lbl = customtkinter.CTkLabel(
                self.vid_cls_sub_frm, height=lbl_height, text=in_queue_txt[lang_idx]
            )
            self.vid_cls_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.vid_cls_num_lbl = customtkinter.CTkLabel(
                self.vid_cls_sub_frm,
                height=lbl_height,
                text=f"{processing_animal_txt[lang_idx]}:",
            )
            self.vid_cls_num_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_cls_num_lbl.grid_remove()
            self.vid_cls_num_val = customtkinter.CTkLabel(
                self.vid_cls_sub_frm, height=lbl_height, text=f""
            )
            self.vid_cls_num_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_cls_num_val.grid_remove()
            self.vid_cls_ela_lbl = customtkinter.CTkLabel(
                self.vid_cls_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.vid_cls_ela_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_cls_ela_lbl.grid_remove()
            self.vid_cls_ela_val = customtkinter.CTkLabel(
                self.vid_cls_sub_frm, height=lbl_height, text=f""
            )
            self.vid_cls_ela_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_cls_ela_val.grid_remove()
            self.vid_cls_rem_lbl = customtkinter.CTkLabel(
                self.vid_cls_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.vid_cls_rem_lbl.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_cls_rem_lbl.grid_remove()
            self.vid_cls_rem_val = customtkinter.CTkLabel(
                self.vid_cls_sub_frm, height=lbl_height, text=f""
            )
            self.vid_cls_rem_val.grid(
                row=4, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_cls_rem_val.grid_remove()
            self.vid_cls_spe_lbl = customtkinter.CTkLabel(
                self.vid_cls_sub_frm,
                height=lbl_height,
                text=f"{animals_per_second_txt[lang_idx]}:",
            )
            self.vid_cls_spe_lbl.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_cls_spe_lbl.grid_remove()
            self.vid_cls_spe_val = customtkinter.CTkLabel(
                self.vid_cls_sub_frm, height=lbl_height, text=f""
            )
            self.vid_cls_spe_val.grid(
                row=5, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_cls_spe_val.grid_remove()
            self.vid_cls_hwa_lbl = customtkinter.CTkLabel(
                self.vid_cls_sub_frm,
                height=lbl_height,
                text=f"{running_on_txt[lang_idx]}:",
            )
            self.vid_cls_hwa_lbl.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_cls_hwa_lbl.grid_remove()
            self.vid_cls_hwa_val = customtkinter.CTkLabel(
                self.vid_cls_sub_frm, height=lbl_height, text=f""
            )
            self.vid_cls_hwa_val.grid(
                row=6, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_cls_hwa_val.grid_remove()
            self.vid_cls_can_btn = CancelButton(
                master=self.vid_cls_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.vid_cls_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.vid_cls_can_btn.grid_remove()

        # postprocessing for images
        if "img_pst" in processes:
            self.img_pst_frm = customtkinter.CTkFrame(
                master=self.progress_top_level_window
            )
            self.img_pst_frm.grid(
                row=4,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            img_pst_ttl_txt = [
                f"Postprocessing{img_pst_extra_string}...",
                f"Postprocesado{img_pst_extra_string}...",
            ]
            self.img_pst_ttl = customtkinter.CTkLabel(
                self.img_pst_frm, text=img_pst_ttl_txt[lang_idx], font=ttl_font
            )
            self.img_pst_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.img_pst_sub_frm = customtkinter.CTkFrame(master=self.img_pst_frm)
            self.img_pst_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.img_pst_sub_frm.columnconfigure(
                0, weight=1, minsize=300 * scale_factor
            )
            self.img_pst_pbr = customtkinter.CTkProgressBar(
                self.img_pst_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.img_pst_pbr.set(0)
            self.img_pst_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.img_pst_per = customtkinter.CTkLabel(
                self.img_pst_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.img_pst_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.img_pst_wai_lbl = customtkinter.CTkLabel(
                self.img_pst_sub_frm, height=lbl_height, text=in_queue_txt[lang_idx]
            )
            self.img_pst_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.img_pst_ela_lbl = customtkinter.CTkLabel(
                self.img_pst_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.img_pst_ela_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_pst_ela_lbl.grid_remove()
            self.img_pst_ela_val = customtkinter.CTkLabel(
                self.img_pst_sub_frm, height=lbl_height, text=f""
            )
            self.img_pst_ela_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_pst_ela_val.grid_remove()
            self.img_pst_rem_lbl = customtkinter.CTkLabel(
                self.img_pst_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.img_pst_rem_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.img_pst_rem_lbl.grid_remove()
            self.img_pst_rem_val = customtkinter.CTkLabel(
                self.img_pst_sub_frm, height=lbl_height, text=f""
            )
            self.img_pst_rem_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.img_pst_rem_val.grid_remove()
            self.img_pst_can_btn = CancelButton(
                master=self.img_pst_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.img_pst_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.img_pst_can_btn.grid_remove()

        # postprocessing for videos
        if "vid_pst" in processes:
            self.vid_pst_frm = customtkinter.CTkFrame(
                master=self.progress_top_level_window
            )
            self.vid_pst_frm.grid(
                row=5,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            vid_pst_ttl_txt = [
                f"Postprocessing{vid_pst_extra_string}...",
                f"Postprocesado{vid_pst_extra_string}...",
            ]
            self.vid_pst_ttl = customtkinter.CTkLabel(
                self.vid_pst_frm, text=vid_pst_ttl_txt[lang_idx], font=ttl_font
            )
            self.vid_pst_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.vid_pst_sub_frm = customtkinter.CTkFrame(master=self.vid_pst_frm)
            self.vid_pst_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.vid_pst_sub_frm.columnconfigure(
                0, weight=1, minsize=300 * scale_factor
            )
            self.vid_pst_pbr = customtkinter.CTkProgressBar(
                self.vid_pst_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.vid_pst_pbr.set(0)
            self.vid_pst_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.vid_pst_per = customtkinter.CTkLabel(
                self.vid_pst_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.vid_pst_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.vid_pst_wai_lbl = customtkinter.CTkLabel(
                self.vid_pst_sub_frm, height=lbl_height, text=in_queue_txt[lang_idx]
            )
            self.vid_pst_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.vid_pst_ela_lbl = customtkinter.CTkLabel(
                self.vid_pst_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.vid_pst_ela_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_pst_ela_lbl.grid_remove()
            self.vid_pst_ela_val = customtkinter.CTkLabel(
                self.vid_pst_sub_frm, height=lbl_height, text=f""
            )
            self.vid_pst_ela_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_pst_ela_val.grid_remove()
            self.vid_pst_rem_lbl = customtkinter.CTkLabel(
                self.vid_pst_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.vid_pst_rem_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.vid_pst_rem_lbl.grid_remove()
            self.vid_pst_rem_val = customtkinter.CTkLabel(
                self.vid_pst_sub_frm, height=lbl_height, text=f""
            )
            self.vid_pst_rem_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.vid_pst_rem_val.grid_remove()
            self.vid_pst_can_btn = CancelButton(
                master=self.vid_pst_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.vid_pst_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.vid_pst_can_btn.grid_remove()

        # plotting can only be done for images
        if "plt" in processes:
            self.plt_frm = customtkinter.CTkFrame(master=self.progress_top_level_window)
            self.plt_frm.grid(
                row=6,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
            )
            plt_ttl_txt = [f"Creating graphs...", f"Creando gráficos..."]
            self.plt_ttl = customtkinter.CTkLabel(
                self.plt_frm, text=plt_ttl_txt[lang_idx], font=ttl_font
            )
            self.plt_ttl.grid(
                row=0,
                padx=self.padx_progress_window * 2,
                pady=(self.pady_progress_window, 0),
                columnspan=2,
                sticky="nsw",
            )
            self.plt_sub_frm = customtkinter.CTkFrame(master=self.plt_frm)
            self.plt_sub_frm.grid(
                row=1,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nswe",
                ipady=self.pady_progress_window / 2,
            )
            self.plt_sub_frm.columnconfigure(0, weight=1, minsize=300 * scale_factor)
            self.plt_pbr = customtkinter.CTkProgressBar(
                self.plt_sub_frm,
                orientation="horizontal",
                height=pbr_height,
                corner_radius=5,
                width=1,
            )
            self.plt_pbr.set(0)
            self.plt_pbr.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="nsew",
            )
            self.plt_per = customtkinter.CTkLabel(
                self.plt_sub_frm,
                text=f" 0% ",
                height=5,
                fg_color=("#949BA2", "#4B4D50"),
                text_color="white",
            )
            self.plt_per.grid(
                row=0,
                padx=self.padx_progress_window,
                pady=self.pady_progress_window,
                sticky="",
            )
            self.plt_wai_lbl = customtkinter.CTkLabel(
                self.plt_sub_frm, height=lbl_height, text=in_queue_txt[lang_idx]
            )
            self.plt_wai_lbl.grid(
                row=1, padx=self.padx_progress_window, pady=0, sticky="nsew"
            )
            self.plt_ela_lbl = customtkinter.CTkLabel(
                self.plt_sub_frm,
                height=lbl_height,
                text=f"{elapsed_time_txt[lang_idx]}:",
            )
            self.plt_ela_lbl.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.plt_ela_lbl.grid_remove()
            self.plt_ela_val = customtkinter.CTkLabel(
                self.plt_sub_frm, height=lbl_height, text=f""
            )
            self.plt_ela_val.grid(
                row=2, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.plt_ela_val.grid_remove()
            self.plt_rem_lbl = customtkinter.CTkLabel(
                self.plt_sub_frm,
                height=lbl_height,
                text=f"{remaining_time_txt[lang_idx]}:",
            )
            self.plt_rem_lbl.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nsw"
            )
            self.plt_rem_lbl.grid_remove()
            self.plt_rem_val = customtkinter.CTkLabel(
                self.plt_sub_frm, height=lbl_height, text=f""
            )
            self.plt_rem_val.grid(
                row=3, padx=self.padx_progress_window, pady=0, sticky="nse"
            )
            self.plt_rem_val.grid_remove()
            self.plt_can_btn = CancelButton(
                master=self.plt_sub_frm, text="Cancel", command=lambda: print("")
            )
            self.plt_can_btn.grid(
                row=7,
                padx=self.padx_progress_window,
                pady=(self.pady_progress_window, 0),
                sticky="ns",
            )
            self.plt_can_btn.grid_remove()

        self.progress_top_level_window.update()

    def update_values(
        self,
        process,
        status,
        cur_it=1,
        tot_it=1,
        time_ela="",
        time_rem="",
        speed="",
        hware="",
        cancel_func=lambda: print(""),
        extracting_frames_txt=[
            "Extracting frames...     ",
            "Extrayendo fotogramas...     ",
        ],
        frame_video_choice="frame",
    ):
        # language settings
        algorithm_starting_txt = [
            "Algorithm is starting up...",
            "El algoritmo está arrancando...",
        ]
        smoothing_txt = ["Smoothing predictions...", "Suavizar las predicciones..."]
        image_per_second_txt = ["Images per second:", "Imágenes por segundo:"]
        seconds_per_image_txt = ["Seconds per image:", "Segundos por imagen:"]
        animals_per_second_txt = ["Animals per second:", "Animales por segundo:"]
        seconds_per_animal_txt = ["Seconds per animal:", "Segundos por animal:"]
        frames_per_second_txt = ["Frames per second:", "Fotogramas por segundo:"]
        seconds_per_frame_txt = ["Seconds per frame:", "Segundos por fotograma:"]
        videos_per_second_txt = ["Videos per second:", "Vídeos por segundo:"]
        seconds_per_video_txt = ["Seconds per video:", "Segundos por vídeo:"]
        processing_videos_txt = ["Processing video:", "Procesando vídeo:"]
        processing_frames_txt = ["Processing frame:", "Procesando fotograma:"]
        starting_up_txt = ["Starting up...", "Arrancando..."]

        # detection of images
        if process == "img_det":
            if status == "load":
                self.img_det_wai_lbl.configure(text=algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.img_det_wai_lbl.grid_remove()
                    self.img_det_num_lbl.grid()
                    self.img_det_num_val.grid()
                    self.img_det_ela_lbl.grid()
                    self.img_det_ela_val.grid()
                    self.img_det_rem_lbl.grid()
                    self.img_det_rem_val.grid()
                    self.img_det_spe_lbl.grid()
                    self.img_det_spe_val.grid()
                    self.img_det_hwa_lbl.grid()
                    self.img_det_hwa_val.grid()
                    self.img_det_can_btn.grid()
                    self.img_det_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.img_det_pbr.set(percentage)
                self.img_det_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.img_det_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.img_det_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.img_det_num_val.configure(text=f"{cur_it} of {tot_it}")
                self.img_det_ela_val.configure(text=time_ela)
                self.img_det_rem_val.configure(text=time_rem)
                self.img_det_spe_lbl.configure(
                    text=image_per_second_txt[lang_idx]
                    if "it/s" in speed
                    else seconds_per_image_txt[lang_idx]
                )
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.img_det_spe_val.configure(text=parsed_speed)
                self.img_det_hwa_val.configure(text=hware)
            elif status == "done":
                self.img_det_num_lbl.grid_remove()
                self.img_det_num_val.grid_remove()
                self.img_det_rem_lbl.grid_remove()
                self.img_det_rem_val.grid_remove()
                self.img_det_hwa_lbl.grid_remove()
                self.img_det_hwa_val.grid_remove()
                self.img_det_can_btn.grid_remove()
                self.img_det_ela_val.grid_remove()
                self.img_det_ela_lbl.grid_remove()
                self.img_det_spe_lbl.grid_remove()
                self.img_det_spe_val.grid_remove()
                self.img_det_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.img_det_per.grid_configure(pady=(self.pady_progress_window, 0))

        # classification of images
        elif process == "img_cls":
            if status == "load":
                self.img_cls_wai_lbl.configure(text=algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.img_cls_wai_lbl.grid_remove()
                    self.img_cls_num_lbl.grid()
                    self.img_cls_num_val.grid()
                    self.img_cls_ela_lbl.grid()
                    self.img_cls_ela_val.grid()
                    self.img_cls_rem_lbl.grid()
                    self.img_cls_rem_val.grid()
                    self.img_cls_spe_lbl.grid()
                    self.img_cls_spe_val.grid()
                    self.img_cls_hwa_lbl.grid()
                    self.img_cls_hwa_val.grid()
                    self.img_cls_can_btn.grid()
                    self.img_cls_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.img_cls_pbr.set(percentage)
                self.img_cls_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.img_cls_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.img_cls_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.img_cls_num_val.configure(text=f"{cur_it} of {tot_it}")
                self.img_cls_ela_val.configure(text=time_ela)
                self.img_cls_rem_val.configure(text=time_rem)
                self.img_cls_spe_lbl.configure(
                    text=animals_per_second_txt[lang_idx]
                    if "it/s" in speed
                    else seconds_per_animal_txt[lang_idx]
                )
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.img_cls_spe_val.configure(text=parsed_speed)
                self.img_cls_hwa_val.configure(text=hware)
            elif status == "smoothing":
                self.img_cls_num_lbl.grid_remove()
                self.img_cls_num_val.grid_remove()
                self.img_cls_rem_lbl.grid_remove()
                self.img_cls_rem_val.grid_remove()
                self.img_cls_hwa_lbl.grid_remove()
                self.img_cls_hwa_val.grid_remove()
                self.img_cls_can_btn.grid_remove()
                self.img_cls_ela_val.grid_remove()
                self.img_cls_ela_lbl.grid_remove()
                self.img_cls_spe_lbl.grid_remove()
                self.img_cls_spe_val.grid_remove()
                self.img_cls_wai_lbl.grid()
                self.img_cls_wai_lbl.configure(text=smoothing_txt[lang_idx])
            elif status == "done":
                self.img_cls_num_lbl.grid_remove()
                self.img_cls_num_val.grid_remove()
                self.img_cls_rem_lbl.grid_remove()
                self.img_cls_rem_val.grid_remove()
                self.img_cls_hwa_lbl.grid_remove()
                self.img_cls_hwa_val.grid_remove()
                self.img_cls_can_btn.grid_remove()
                self.img_cls_ela_val.grid_remove()
                self.img_cls_ela_lbl.grid_remove()
                self.img_cls_spe_lbl.grid_remove()
                self.img_cls_spe_val.grid_remove()
                self.img_cls_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.img_cls_per.grid_configure(pady=(self.pady_progress_window, 0))

        # detection of videos
        if process == "vid_det":
            if status == "load":
                self.vid_det_wai_lbl.configure(text=algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "extracting frames":
                self.vid_det_wai_lbl.configure(text=extracting_frames_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.vid_det_wai_lbl.grid_remove()
                    self.vid_det_num_lbl.grid()
                    self.vid_det_num_val.grid()
                    self.vid_det_ela_lbl.grid()
                    self.vid_det_ela_val.grid()
                    self.vid_det_rem_lbl.grid()
                    self.vid_det_rem_val.grid()
                    self.vid_det_spe_lbl.grid()
                    self.vid_det_spe_val.grid()
                    self.vid_det_hwa_lbl.grid()
                    self.vid_det_hwa_val.grid()
                    self.vid_det_can_btn.grid()
                    self.vid_det_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.vid_det_pbr.set(percentage)
                self.vid_det_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.vid_det_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.vid_det_per.configure(fg_color=("#949BA2", "#4B4D50"))
                if frame_video_choice == "frame":
                    self.vid_det_num_lbl.configure(text=processing_frames_txt[lang_idx])
                else:
                    self.vid_det_num_lbl.configure(text=processing_videos_txt[lang_idx])
                self.vid_det_num_val.configure(text=f"{cur_it} of {tot_it}")
                self.vid_det_ela_val.configure(text=time_ela)
                self.vid_det_rem_val.configure(text=time_rem)
                if frame_video_choice == "frame":
                    self.vid_det_spe_lbl.configure(
                        text=frames_per_second_txt[lang_idx]
                        if "it/s" in speed
                        else seconds_per_frame_txt[lang_idx]
                    )
                else:
                    self.vid_det_spe_lbl.configure(
                        text=videos_per_second_txt[lang_idx]
                        if "it/s" in speed
                        else seconds_per_video_txt[lang_idx]
                    )
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.vid_det_spe_val.configure(text=parsed_speed)
                self.vid_det_hwa_val.configure(text=hware)
            elif status == "done":
                self.vid_det_num_lbl.grid_remove()
                self.vid_det_num_val.grid_remove()
                self.vid_det_rem_lbl.grid_remove()
                self.vid_det_rem_val.grid_remove()
                self.vid_det_hwa_lbl.grid_remove()
                self.vid_det_hwa_val.grid_remove()
                self.vid_det_ela_val.grid_remove()
                self.vid_det_ela_lbl.grid_remove()
                self.vid_det_spe_lbl.grid_remove()
                self.vid_det_spe_val.grid_remove()
                self.vid_det_can_btn.grid_remove()
                self.vid_det_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.vid_det_per.grid_configure(pady=(self.pady_progress_window, 0))

        # classification of videos
        elif process == "vid_cls":
            if status == "load":
                self.vid_cls_wai_lbl.configure(text=algorithm_starting_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.vid_cls_wai_lbl.grid_remove()
                    self.vid_cls_num_lbl.grid()
                    self.vid_cls_num_val.grid()
                    self.vid_cls_ela_lbl.grid()
                    self.vid_cls_ela_val.grid()
                    self.vid_cls_rem_lbl.grid()
                    self.vid_cls_rem_val.grid()
                    self.vid_cls_spe_lbl.grid()
                    self.vid_cls_spe_val.grid()
                    self.vid_cls_hwa_lbl.grid()
                    self.vid_cls_hwa_val.grid()
                    self.vid_cls_can_btn.grid()
                    self.vid_cls_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.vid_cls_pbr.set(percentage)
                self.vid_cls_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.vid_cls_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.vid_cls_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.vid_cls_num_val.configure(text=f"{cur_it} of {tot_it}")
                self.vid_cls_ela_val.configure(text=time_ela)
                self.vid_cls_rem_val.configure(text=time_rem)
                self.vid_cls_spe_lbl.configure(
                    text=animals_per_second_txt[lang_idx]
                    if "it/s" in speed
                    else seconds_per_animal_txt[lang_idx]
                )
                parsed_speed = speed.replace("it/s", "").replace("s/it", "")
                self.vid_cls_spe_val.configure(text=parsed_speed)
                self.vid_cls_hwa_val.configure(text=hware)
            elif status == "smoothing":
                self.vid_cls_num_lbl.grid_remove()
                self.vid_cls_num_val.grid_remove()
                self.vid_cls_rem_lbl.grid_remove()
                self.vid_cls_rem_val.grid_remove()
                self.vid_cls_hwa_lbl.grid_remove()
                self.vid_cls_hwa_val.grid_remove()
                self.vid_cls_can_btn.grid_remove()
                self.vid_cls_ela_val.grid_remove()
                self.vid_cls_ela_lbl.grid_remove()
                self.vid_cls_spe_lbl.grid_remove()
                self.vid_cls_spe_val.grid_remove()
                self.vid_cls_wai_lbl.grid()
                self.vid_cls_wai_lbl.configure(text=smoothing_txt[lang_idx])
            elif status == "done":
                self.vid_cls_num_lbl.grid_remove()
                self.vid_cls_num_val.grid_remove()
                self.vid_cls_rem_lbl.grid_remove()
                self.vid_cls_rem_val.grid_remove()
                self.vid_cls_hwa_lbl.grid_remove()
                self.vid_cls_hwa_val.grid_remove()
                self.vid_cls_ela_val.grid_remove()
                self.vid_cls_ela_lbl.grid_remove()
                self.vid_cls_spe_lbl.grid_remove()
                self.vid_cls_spe_val.grid_remove()
                self.vid_cls_can_btn.grid_remove()
                self.vid_cls_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.vid_cls_per.grid_configure(pady=(self.pady_progress_window, 0))

        # postprocessing of images
        elif process == "img_pst":
            if status == "load":
                self.img_pst_wai_lbl.configure(text=starting_up_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.img_pst_wai_lbl.grid_remove()
                    self.img_pst_ela_lbl.grid()
                    self.img_pst_ela_val.grid()
                    self.img_pst_rem_lbl.grid()
                    self.img_pst_rem_val.grid()
                    self.img_pst_can_btn.grid()
                    self.img_pst_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.img_pst_pbr.set(percentage)
                self.img_pst_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.img_pst_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.img_pst_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.img_pst_ela_val.configure(text=time_ela)
                self.img_pst_rem_val.configure(text=time_rem)
            elif status == "done":
                self.img_pst_rem_lbl.grid_remove()
                self.img_pst_rem_val.grid_remove()
                self.img_pst_ela_val.grid_remove()
                self.img_pst_ela_lbl.grid_remove()
                self.img_pst_can_btn.grid_remove()
                self.img_pst_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.img_pst_per.grid_configure(pady=(self.pady_progress_window, 0))

        # postprocessing of videos
        elif process == "vid_pst":
            if status == "load":
                self.vid_pst_wai_lbl.configure(text=starting_up_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.vid_pst_wai_lbl.grid_remove()
                    self.vid_pst_ela_lbl.grid()
                    self.vid_pst_ela_val.grid()
                    self.vid_pst_rem_lbl.grid()
                    self.vid_pst_rem_val.grid()
                    self.vid_pst_can_btn.grid()
                    self.vid_pst_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.vid_pst_pbr.set(percentage)
                self.vid_pst_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.vid_pst_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.vid_pst_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.vid_pst_ela_val.configure(text=time_ela)
                self.vid_pst_rem_val.configure(text=time_rem)
            elif status == "done":
                self.vid_pst_rem_lbl.grid_remove()
                self.vid_pst_rem_val.grid_remove()
                self.vid_pst_ela_val.grid_remove()
                self.vid_pst_ela_lbl.grid_remove()
                self.vid_pst_can_btn.grid_remove()
                self.vid_pst_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.vid_pst_per.grid_configure(pady=(self.pady_progress_window, 0))

        # postprocessing of videos
        elif process == "plt":
            if status == "load":
                self.plt_wai_lbl.configure(text=starting_up_txt[lang_idx])
                self.just_shown_load_screen = True
            elif status == "running":
                if self.just_shown_load_screen:
                    self.plt_wai_lbl.grid_remove()
                    self.plt_ela_lbl.grid()
                    self.plt_ela_val.grid()
                    self.plt_rem_lbl.grid()
                    self.plt_rem_val.grid()
                    self.plt_can_btn.grid()
                    self.plt_can_btn.configure(command=cancel_func)
                    self.just_shown_load_screen = False
                percentage = cur_it / tot_it
                self.plt_pbr.set(percentage)
                self.plt_per.configure(text=f" {round(percentage * 100)}% ")
                if percentage > 0.5:
                    self.plt_per.configure(fg_color=(green_primary, "#1F6BA5"))
                else:
                    self.plt_per.configure(fg_color=("#949BA2", "#4B4D50"))
                self.plt_ela_val.configure(text=time_ela)
                self.plt_rem_val.configure(text=time_rem)
            elif status == "done":
                self.plt_rem_lbl.grid_remove()
                self.plt_rem_val.grid_remove()
                self.plt_ela_val.grid_remove()
                self.plt_ela_lbl.grid_remove()
                self.plt_can_btn.grid_remove()
                self.plt_pbr.grid_configure(pady=(self.pady_progress_window, 0))
                self.plt_per.grid_configure(pady=(self.pady_progress_window, 0))

        # update screen
        self.progress_top_level_window.update()

    def open(self):
        self.progress_top_level_window.deiconify()

    def close(self):
        self.progress_top_level_window.destroy()


# refresh dropdown menu options
def update_dpd_options(dpd, master, var, options, cmd, row, lbl, from_lang_idx):
    # recreate new option menu with updated options
    dpd.grid_forget()
    index = options[from_lang_idx].index(var.get())  # get dpd index
    var.set(options[lang_idx][index])  # set to previous index
    if cmd:
        dpd = OptionMenu(master, var, *options[lang_idx], command=cmd)
    else:
        dpd = OptionMenu(master, var, *options[lang_idx])
    dpd.configure(width=1)
    dpd.grid(row=row, column=1, sticky="nesw", padx=5)

    # give it same state as its label
    dpd.configure(state=str(lbl["state"]))


# special refresh function for the model seleciton dropdown in simple mode because customtkinter works a bit different
def update_sim_mdl_dpd():
    global sim_mdl_dpd
    sim_mdl_dpd.grid_forget()
    sim_mdl_dpd = customtkinter.CTkOptionMenu(
        sim_mdl_frm,
        values=sim_dpd_options_cls_model[lang_idx],
        command=sim_mdl_dpd_callback,
        width=1,
    )
    sim_mdl_dpd.set(
        sim_dpd_options_cls_model[lang_idx][
            dpd_options_cls_model[lang_idx].index(var_cls_model.get())
        ]
    )
    sim_mdl_dpd.grid(
        row=1, column=0, padx=PADX, pady=(PADY / 4, PADY), sticky="nswe", columnspan=2
    )


# refresh ent texts
def update_ent_text(var, string):
    if var.get() == "":
        return
    if no_user_input(var):
        original_state = str(var["state"])
        var.configure(state=NORMAL, fg="grey")
        var.delete(0, tk.END)
        var.insert(0, string)
        var.configure(state=original_state)


# check next language to print on button when program starts
def set_lang_buttons(lang_idx):
    from_lang_idx = lang_idx
    to_lang_idx = (
        0 if from_lang_idx + 1 >= len(languages_available) else from_lang_idx + 1
    )
    to_lang = languages_available[to_lang_idx]
    sim_btn_switch_lang.configure(text=f"{to_lang}")
    adv_btn_switch_lang.configure(text=f"{to_lang}")


# change language
def set_language():
    # calculate indeces
    global lang_idx
    from_lang_idx = lang_idx
    to_lang_idx = (
        0 if from_lang_idx + 1 >= len(languages_available) else from_lang_idx + 1
    )
    next_lang_idx = (
        0 if to_lang_idx + 1 >= len(languages_available) else to_lang_idx + 1
    )

    # log
    print(f"EXECUTED : {sys._getframe().f_code.co_name}({locals()})\n")

    # set the global variable to the new language
    lang_idx = to_lang_idx
    write_global_vars({"lang_idx": lang_idx})

    # update tab texts
    tabControl.tab(deploy_tab, text=deploy_tab_text[lang_idx])
    tabControl.tab(help_tab, text=help_tab_text[lang_idx])
    tabControl.tab(about_tab, text=about_tab_text[lang_idx])

    # update texts of deploy tab
    fst_step.configure(text=" " + fst_step_txt[lang_idx] + " ")
    lbl_choose_folder.configure(text=lbl_choose_folder_txt[lang_idx])
    btn_choose_folder.configure(text=browse_txt[lang_idx])
    snd_step.configure(text=" " + snd_step_txt[lang_idx] + " ")
    lbl_model.configure(text=lbl_model_txt[lang_idx])
    update_dpd_options(
        dpd_model,
        snd_step,
        var_det_model,
        dpd_options_model,
        model_options,
        row_model,
        lbl_model,
        from_lang_idx,
    )
    lbl_exclude_subs.configure(text=lbl_exclude_subs_txt[lang_idx])
    lbl_use_custom_img_size_for_deploy.configure(
        text=lbl_use_custom_img_size_for_deploy_txt[lang_idx]
    )
    lbl_image_size_for_deploy.configure(text=lbl_image_size_for_deploy_txt[lang_idx])
    update_ent_text(ent_image_size_for_deploy, f"{eg_txt[lang_idx]}: 640")
    lbl_abs_paths.configure(text=lbl_abs_paths_txt[lang_idx])
    lbl_disable_GPU.configure(text=lbl_disable_GPU_txt[lang_idx])
    lbl_process_img.configure(text=lbl_process_img_txt[lang_idx])
    lbl_cls_model.configure(text=lbl_cls_model_txt[lang_idx])
    update_dpd_options(
        dpd_cls_model,
        snd_step,
        var_cls_model,
        dpd_options_cls_model,
        model_cls_animal_options,
        row_cls_model,
        lbl_cls_model,
        from_lang_idx,
    )
    cls_frame.configure(text=" ↳ " + cls_frame_txt[lang_idx] + " ")
    lbl_model_info.configure(text="     " + lbl_model_info_txt[lang_idx])
    btn_model_info.configure(text=show_txt[lang_idx])
    lbl_choose_classes.configure(text="     " + lbl_choose_classes_txt[lang_idx])
    btn_choose_classes.configure(text=select_txt[lang_idx])
    lbl_cls_detec_thresh.configure(text="     " + lbl_cls_detec_thresh_txt[lang_idx])
    lbl_cls_class_thresh.configure(text="     " + lbl_cls_class_thresh_txt[lang_idx])
    lbl_smooth_cls_animal.configure(text="     " + lbl_smooth_cls_animal_txt[lang_idx])
    img_frame.configure(text=" ↳ " + img_frame_txt[lang_idx] + " ")
    lbl_use_checkpnts.configure(text="     " + lbl_use_checkpnts_txt[lang_idx])
    lbl_checkpoint_freq.configure(text="        ↳ " + lbl_checkpoint_freq_txt[lang_idx])
    update_ent_text(ent_checkpoint_freq, f"{eg_txt[lang_idx]}: 500")
    lbl_cont_checkpnt.configure(text="     " + lbl_cont_checkpnt_txt[lang_idx])
    lbl_process_vid.configure(text=lbl_process_vid_txt[lang_idx])
    vid_frame.configure(text=" ↳ " + vid_frame_txt[lang_idx] + " ")
    lbl_not_all_frames.configure(text="     " + lbl_not_all_frames_txt[lang_idx])
    lbl_nth_frame.configure(text="        ↳ " + lbl_nth_frame_txt[lang_idx])
    update_ent_text(ent_nth_frame, f"{eg_txt[lang_idx]}: 1")
    btn_start_deploy.configure(text=btn_start_deploy_txt[lang_idx])
    trd_step.configure(text=" " + trd_step_txt[lang_idx] + " ")
    lbl_hitl_main.configure(text=lbl_hitl_main_txt[lang_idx])
    btn_hitl_main.configure(text=["Start", "Iniciar"][lang_idx])
    fth_step.configure(text=" " + fth_step_txt[lang_idx] + " ")
    lbl_output_dir.configure(text=lbl_output_dir_txt[lang_idx])
    btn_output_dir.configure(text=browse_txt[lang_idx])
    lbl_separate_files.configure(text=lbl_separate_files_txt[lang_idx])
    sep_frame.configure(text=" ↳ " + sep_frame_txt[lang_idx] + " ")
    lbl_file_placement.configure(text="     " + lbl_file_placement_txt[lang_idx])
    rad_file_placement_move.configure(text=["Copy", "Copiar"][lang_idx])
    rad_file_placement_copy.configure(text=["Move", "Mover"][lang_idx])
    lbl_sep_conf.configure(text="     " + lbl_sep_conf_txt[lang_idx])
    lbl_vis_files.configure(text=lbl_vis_files_txt[lang_idx])
    lbl_crp_files.configure(text=lbl_crp_files_txt[lang_idx])
    lbl_exp.configure(text=lbl_exp_txt[lang_idx])
    exp_frame.configure(text=" ↳ " + exp_frame_txt[lang_idx] + " ")
    vis_frame.configure(text=" ↳ " + vis_frame_txt[lang_idx] + " ")
    lbl_exp_format.configure(text="     " + lbl_exp_format_txt[lang_idx])
    lbl_plt.configure(text=lbl_plt_txt[lang_idx])
    lbl_thresh.configure(text=lbl_thresh_txt[lang_idx])
    btn_start_postprocess.configure(text=btn_start_postprocess_txt[lang_idx])
    lbl_vis_size.configure(text="        ↳ " + lbl_vis_size_txt[lang_idx])
    lbl_vis_bbox.configure(text="     " + lbl_vis_bbox_txt[lang_idx])
    lbl_vis_blur.configure(text="     " + lbl_vis_blur_txt[lang_idx])

    # update texts of help tab
    help_text.configure(state=NORMAL)
    help_text.delete("1.0", END)
    write_help_tab()

    # update texts of about tab
    about_text.configure(state=NORMAL)
    about_text.delete("1.0", END)
    write_about_tab()

    # top buttons
    adv_btn_switch_mode.configure(text=adv_btn_switch_mode_txt[lang_idx])
    sim_btn_switch_mode.configure(text=sim_btn_switch_mode_txt[lang_idx])
    sim_btn_switch_lang.configure(text=languages_available[next_lang_idx])
    adv_btn_switch_lang.configure(text=languages_available[next_lang_idx])
    adv_btn_sponsor.configure(text=adv_btn_sponsor_txt[lang_idx])
    sim_btn_sponsor.configure(text=adv_btn_sponsor_txt[lang_idx])
    adv_btn_reset_values.configure(text=adv_btn_reset_values_txt[lang_idx])
    sim_btn_reset_values.configure(text=adv_btn_reset_values_txt[lang_idx])

    # by addax text
    adv_abo_lbl.configure(text=adv_abo_lbl_txt[lang_idx])
    sim_abo_lbl.configure(text=adv_abo_lbl_txt[lang_idx])

    # simple mode
    sim_dir_lbl.configure(text=sim_dir_lbl_txt[lang_idx])
    sim_dir_btn.configure(text=browse_txt[lang_idx])
    sim_dir_pth.configure(text=sim_dir_pth_txt[lang_idx])
    sim_mdl_lbl.configure(text=sim_mdl_lbl_txt[lang_idx])
    update_sim_mdl_dpd()
    sim_spp_lbl.configure(text=sim_spp_lbl_txt[lang_idx])
    sim_run_btn.configure(text=sim_run_btn_txt[lang_idx])


# update frame states
def update_frame_states():
    # check dir validity
    if var_choose_folder.get() in ["", "/", "\\", ".", "~", ":"] or not os.path.isdir(
        var_choose_folder.get()
    ):
        return
    if var_choose_folder.get() not in ["", "/", "\\", ".", "~", ":"] and os.path.isdir(
        var_choose_folder.get()
    ):
        complete_frame(fst_step)
    else:
        enable_frame(fst_step)

    # check json files
    img_json = False
    path_to_image_json = os.path.join(
        var_choose_folder.get(), "image_recognition_file.json"
    )
    if os.path.isfile(path_to_image_json):
        img_json = True
    vid_json = False
    if os.path.isfile(
        os.path.join(var_choose_folder.get(), "video_recognition_file.json")
    ):
        vid_json = True

    # check if dir is already processed
    if img_json or vid_json:
        complete_frame(snd_step)
        enable_frame(fth_step)
    else:
        enable_frame(snd_step)
        disable_frame(fth_step)

    # check hitl status
    if img_json:
        status = get_hitl_var_in_json(path_to_image_json)
        if status == "never-started":
            enable_frame(trd_step)
            btn_hitl_main.configure(text=["Start", "Iniciar"][lang_idx])
        elif status == "in-progress":
            enable_frame(trd_step)
            btn_hitl_main.configure(text=["Continue", "Continuar"][lang_idx])
        elif status == "done":
            complete_frame(trd_step)
    else:
        disable_frame(trd_step)

    # if in timelapse mode, always disable trd and fth step
    if timelapse_mode:
        disable_frame(trd_step)
        disable_frame(fth_step)

# check if user entered text in entry widget
def no_user_input(var):
    if var.get() == "" or var.get().startswith("E.g.:") or var.get().startswith("Ejem.:"):
        return True
    else:
        return False

# show warning if not valid input
def invalid_value_warning(str, numeric = True):
    string = [f"You either entered an invalid value for the {str}, or none at all.", f"Ingresó un valor no válido para {str} o ninguno."][lang_idx]
    if numeric:
        string += [" You can only enter numeric characters.", " Solo puede ingresar caracteres numéricos."][lang_idx]
    mb.showerror(invalid_value_txt[lang_idx], string)

# disable widgets based on row and col indeces
def disable_widgets_based_on_location(master, rows, cols):
    # list widgets to be removed
    widgets = []
    for row in rows:
        for col in cols:
            l = master.grid_slaves(row, col)
            for i in l:
                widgets.append(i)

    # remove widgets
    for widget in widgets:
        widget.configure(state=DISABLED)

# remove widgets based on row and col indexes
def remove_widgets_based_on_location(master, rows, cols):
    # list widgets to be removed
    widgets = []
    for row in rows:
        for col in cols:
            l = master.grid_slaves(row, col)
            for i in l:
                widgets.append(i)

    # remove widgets
    for widget in widgets:
        widget.grid_forget()

# create hyperlinks (thanks marvin from GitHub)
class HyperlinkManager:
    def __init__(self, text):
        self.text = text
        self.text.tag_config("hyper", foreground=green_primary, underline=1)
        self.text.tag_bind("hyper", "<Enter>", self._enter)
        self.text.tag_bind("hyper", "<Leave>", self._leave)
        self.text.tag_bind("hyper", "<Button-1>", self._click)
        self.reset()

    def reset(self):
        self.links = {}

    def add(self, action):
        tag = "hyper-%d" % len(self.links)
        self.links[tag] = action
        return "hyper", tag

    def _enter(self, event):
        self.text.configure(cursor="hand2")

    def _leave(self, event):
        self.text.configure(cursor="")

    def _click(self, event):
        for tag in self.text.tag_names(CURRENT):
            if tag[:6] == "hyper-":
                self.links[tag]()
                return

# set cancel variable to true
def cancel():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    global cancel_var
    cancel_var = True

# set all children of frame to disabled state
def disable_widgets(frame):
    children = frame.winfo_children()
    for child in children:
        # labelframes have no state
        if child.winfo_class() != "Labelframe":
            child.configure(state=DISABLED)

# set all children of frame to normal state
def enable_widgets(frame):
    children = frame.winfo_children()
    for child in children:
        # labelframes have no state
        if child.winfo_class() != "Labelframe":
            child.configure(state=NORMAL)

# show warning for absolute paths option
shown_abs_paths_warning = True
def abs_paths_warning():
    global shown_abs_paths_warning
    if var_abs_paths.get() and shown_abs_paths_warning:
        mb.showinfo(warning_txt[lang_idx], ["It is not recommended to use absolute paths in the output file. Third party software (such "
                    "as Timelapse) will not be able to read the json file if the paths are absolute. Only enable"
                    " this option if you know what you are doing.",
                    "No se recomienda utilizar rutas absolutas en el archivo de salida. Software de terceros (como Timelapse"
                    ") no podrán leer el archivo json si las rutas son absolutas. Sólo active esta opción si sabe lo"
                    " que está haciendo."][lang_idx])
        shown_abs_paths_warning = False

# toggle image size entry box
def toggle_image_size_for_deploy():
    if var_use_custom_img_size_for_deploy.get():
        lbl_image_size_for_deploy.grid(row=row_image_size_for_deploy, sticky='nesw', pady=2)
        ent_image_size_for_deploy.grid(row=row_image_size_for_deploy, column=1, sticky='nesw', padx=5)
    else:
        lbl_image_size_for_deploy.grid_remove()
        ent_image_size_for_deploy.grid_remove()
    resize_canvas_to_content()

# toggle separation subframe
def toggle_sep_frame():
    if var_separate_files.get():
        sep_frame.grid(row=sep_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(sep_frame)
        sep_frame.configure(fg='black')
    else:
        disable_widgets(sep_frame)
        sep_frame.configure(fg='grey80')
        sep_frame.grid_forget()
    resize_canvas_to_content()

# toggle export subframe
def toggle_exp_frame():
    if var_exp.get() and lbl_exp.cget("state") == "normal":
        exp_frame.grid(row=exp_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(exp_frame)
        exp_frame.configure(fg='black')
    else:
        disable_widgets(exp_frame)
        exp_frame.configure(fg='grey80')
        exp_frame.grid_forget()
    resize_canvas_to_content()

# toggle visualization subframe
def toggle_vis_frame():
    if var_vis_files.get() and lbl_vis_files.cget("state") == "normal":
        vis_frame.grid(row=vis_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(vis_frame)
        vis_frame.configure(fg='black')
    else:
        disable_widgets(vis_frame)
        vis_frame.configure(fg='grey80')
        vis_frame.grid_forget()
    resize_canvas_to_content()

# on checkbox change
def on_chb_smooth_cls_animal_change():
    write_model_vars(new_values={"var_smooth_cls_animal": var_smooth_cls_animal.get()})
    if var_smooth_cls_animal.get():
        mb.showinfo(information_txt[lang_idx], ["This feature averages confidence scores to avoid noise. Note that it assumes a single species per "
                                               "sequence or video and should therefore only be used if multi-species sequences are rare. It does not"
                                               " affect detections of vehicles or people alongside animals.", "Esta función promedia las puntuaciones "
                                               "de confianza para evitar el ruido. Tenga en cuenta que asume una única especie por secuencia o vídeo "
                                               "y, por lo tanto, sólo debe utilizarse si las secuencias multiespecíficas son poco frecuentes. No afecta"
                                               " a las detecciones de vehículos o personas junto a animales."][lang_idx])

# toggle classification subframe
def toggle_cls_frame():
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # check the state of snd_step
    snd_step_enabled = False if snd_step.cget('fg') == 'grey80' else True

    # only enable cls_frame if snd_step is also enabled and user didn't choose None
    if var_cls_model.get() not in none_txt and snd_step_enabled:
        cls_frame.grid(row=cls_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(cls_frame)
        toggle_checkpoint_freq()
        cls_frame.configure(fg='black')
    else:
        disable_widgets(cls_frame)
        cls_frame.configure(fg='grey80')
        cls_frame.grid_forget()
    resize_canvas_to_content()

# toggle image subframe
def toggle_img_frame():
    if var_process_img.get():
        img_frame.grid(row=img_frame_row, column=0, columnspan=2, sticky = 'ew')
        enable_widgets(img_frame)
        toggle_checkpoint_freq()
        img_frame.configure(fg='black')
    else:
        disable_widgets(img_frame)
        img_frame.configure(fg='grey80')
        img_frame.grid_forget()
    resize_canvas_to_content()

# toggle video subframe
def toggle_vid_frame():
    if var_process_vid.get():
        vid_frame.grid(row=vid_frame_row, column=0, columnspan=2, sticky='ew')
        enable_widgets(vid_frame)
        toggle_nth_frame()
        vid_frame.configure(fg='black')
    else:
        disable_widgets(vid_frame)
        vid_frame.configure(fg='grey80')
        vid_frame.grid_forget()
    resize_canvas_to_content()

# convert frame to completed
def complete_frame(frame):
    global check_mark_one_row
    global check_mark_two_rows

    # check which frame
    any_step = frame.cget('text').startswith(f' {step_txt[lang_idx]}')
    fst_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 1')
    snd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 2')
    trd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 3')
    fth_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 4')

    # adjust frames
    frame.configure(relief = 'groove')
    if any_step:
        frame.configure(fg=green_primary)
    if snd_step:
        cls_frame.configure(relief = 'groove')
        img_frame.configure(relief = 'groove')
        vid_frame.configure(relief = 'groove')

    if trd_step or fst_step:
        # add check mark
        lbl_check_mark = Label(frame, image=check_mark_one_row)
        lbl_check_mark.image = check_mark_one_row
        lbl_check_mark.grid(row=0, column=0, rowspan=15, columnspan=2, sticky='nesw')
        if trd_step:
            btn_hitl_main.configure(text=["New session?", "¿Nueva sesión?"][lang_idx], state = NORMAL)
            btn_hitl_main.lift()
        if fst_step:
            btn_choose_folder.configure(text=f"{change_folder_txt[lang_idx]}?", state = NORMAL)
            btn_choose_folder.lift()
            dsp_choose_folder.lift()

    else:
        # the rest
        if not any_step:
            # sub frames of fth_step only
            frame.configure(fg=green_primary)

        # add check mark
        lbl_check_mark = Label(frame, image=check_mark_two_rows)
        lbl_check_mark.image = check_mark_two_rows
        lbl_check_mark.grid(row=0, column=0, rowspan=15, columnspan=2, sticky='nesw')

        # add buttons
        btn_view_results = Button(master=frame, text=view_results_txt[lang_idx], width=1, command=lambda: view_results(frame))
        btn_view_results.grid(row=0, column=1, sticky='nesw', padx = 5)
        btn_uncomplete = Button(master=frame, text=again_txt[lang_idx], width=1, command=lambda: enable_frame(frame))
        btn_uncomplete.grid(row=1, column=1, sticky='nesw', padx = 5)

# enable a frame
def enable_frame(frame):
    uncomplete_frame(frame)
    enable_widgets(frame)

    # check which frame
    any_step = frame.cget('text').startswith(f' {step_txt[lang_idx]}')
    fst_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 1')
    snd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 2')
    trd_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 3')
    fth_step = frame.cget('text').startswith(f' {step_txt[lang_idx]} 4')

    # all frames
    frame.configure(relief = 'solid')
    if any_step:
        frame.configure(fg=green_primary)
    if snd_step:
        toggle_cls_frame()
        cls_frame.configure(relief = 'solid')
        toggle_img_frame()
        img_frame.configure(relief = 'solid')
        toggle_vid_frame()
        vid_frame.configure(relief = 'solid')
        toggle_image_size_for_deploy()
    if fth_step:
        toggle_sep_frame()
        toggle_exp_frame()
        toggle_vis_frame()
        sep_frame.configure(relief = 'solid')
        exp_frame.configure(relief = 'solid')
        vis_frame.configure(relief = 'solid')

# remove checkmarks and complete buttons
def uncomplete_frame(frame):
    if not frame.cget('text').startswith(f' {step_txt[lang_idx]}'):
        # subframes in fth_step only
        frame.configure(fg='black')
    children = frame.winfo_children()
    for child in children:
        if child.winfo_class() == "Button" or child.winfo_class() == "Label":
            if child.cget('text') == again_txt[lang_idx] or child.cget('text') == view_results_txt[lang_idx] or child.cget('image') != "":
                child.grid_remove()

# disable a frame
def disable_frame(frame):
    uncomplete_frame(frame)
    disable_widgets(frame)
    # all frames
    frame.configure(fg='grey80')
    frame.configure(relief = 'flat')
    if frame.cget('text').startswith(f' {step_txt[lang_idx]} 2'):
        # snd_step only
        disable_widgets(cls_frame)
        cls_frame.configure(fg='grey80')
        cls_frame.configure(relief = 'flat')
        disable_widgets(img_frame)
        img_frame.configure(fg='grey80')
        img_frame.configure(relief = 'flat')
        disable_widgets(vid_frame)
        vid_frame.configure(fg='grey80')
        vid_frame.configure(relief = 'flat')
    if frame.cget('text').startswith(f' {step_txt[lang_idx]} 4'):
        # fth_step only
        disable_widgets(sep_frame)
        sep_frame.configure(fg='grey80')
        sep_frame.configure(relief = 'flat')
        disable_widgets(exp_frame)
        exp_frame.configure(fg='grey80')
        exp_frame.configure(relief = 'flat')
        disable_widgets(vis_frame)
        vis_frame.configure(fg='grey80')
        vis_frame.configure(relief = 'flat')


# check if checkpoint is present and set checkbox accordingly
def disable_chb_cont_checkpnt():
    if var_cont_checkpnt.get():
        var_cont_checkpnt.set(check_checkpnt())

# set minimum row size for all rows in a frame
def set_minsize_rows(frame):
    row_count = frame.grid_size()[1]
    for row in range(row_count):
        frame.grid_rowconfigure(row, minsize=minsize_rows)

# toggle state of checkpoint frequency
def toggle_checkpoint_freq():
    if var_use_checkpnts.get():
        lbl_checkpoint_freq.configure(state=NORMAL)
        ent_checkpoint_freq.configure(state=NORMAL)
    else:
        lbl_checkpoint_freq.configure(state=DISABLED)
        ent_checkpoint_freq.configure(state=DISABLED)

# toggle state of nth frame
def toggle_nth_frame():
    if var_not_all_frames.get():
        lbl_nth_frame.configure(state=NORMAL)
        ent_nth_frame.configure(state=NORMAL)
    else:
        lbl_nth_frame.configure(state=DISABLED)
        ent_nth_frame.configure(state=DISABLED)

# check required and maximum size of canvas and resize accordingly
def resize_canvas_to_content():
    root.update_idletasks()
    _, _, _, height_logo = advanc_main_frame.grid_bbox(0, 0)
    _, _, width_step1, height_step1 = deploy_scrollable_frame.grid_bbox(0, 1)
    _, _, _, height_step2 = deploy_scrollable_frame.grid_bbox(0, 2)
    _, _, width_step3, _ = deploy_scrollable_frame.grid_bbox(1, 1)
    canvas_required_height = height_step1 + height_step2
    canvas_required_width  = width_step1 + width_step3
    max_screen_height = root.winfo_screenheight()
    canvas_max_height = max_screen_height - height_logo - 300
    canvas_height = min(canvas_required_height, canvas_max_height, 800)
    deploy_canvas.configure(width = canvas_required_width, height = canvas_height)
    bg_height = (canvas_height + height_logo + ADV_EXTRA_GRADIENT_HEIGHT) * (1 / scale_factor)
    new_advanc_bg_image = customtkinter.CTkImage(PIL_sidebar, size=(ADV_WINDOW_WIDTH, bg_height))
    advanc_bg_image_label.configure(image=new_advanc_bg_image)

# functions to delete the grey text in the entry boxes for the...
# ... image size for deploy
image_size_for_deploy_init = True
def image_size_for_deploy_focus_in(_):
    global image_size_for_deploy_init
    if image_size_for_deploy_init and not var_image_size_for_deploy.get().isdigit():
        ent_image_size_for_deploy.delete(0, tk.END)
        ent_image_size_for_deploy.configure(fg='black')
    image_size_for_deploy_init = False

# ... checkpoint frequency
checkpoint_freq_init = True
def checkpoint_freq_focus_in(_):
    global checkpoint_freq_init
    if checkpoint_freq_init and not var_checkpoint_freq.get().isdigit():
        ent_checkpoint_freq.delete(0, tk.END)
        ent_checkpoint_freq.configure(fg='black')
    checkpoint_freq_init = False

# ... nth frame
nth_frame_init = True
def nth_frame_focus_in(_):
    global nth_frame_init
    if nth_frame_init and not var_nth_frame.get().isdigit():
        ent_nth_frame.delete(0, tk.END)
        ent_nth_frame.configure(fg='black')
    nth_frame_init = False

# check current status, switch to opposite and save
def switch_mode():

    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # load
    advanced_mode = load_global_vars()["advanced_mode"]

    # switch
    if advanced_mode:
        advanc_mode_win.withdraw()
        simple_mode_win.deiconify()
    else:
        advanc_mode_win.deiconify()
        simple_mode_win.withdraw()

    # save
    write_global_vars({
        "advanced_mode": not advanced_mode
    })
