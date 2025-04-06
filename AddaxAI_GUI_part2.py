# function to produce graphs and maps
def produce_plots(results_dir):
    # update internal progressbar via a tmdq stats
    def update_pbar_plt():
        pbar.update(1)
        tqdm_stats = pbar.format_dict
        progress_window.update_values(
            process="plt",
            status="running",
            cur_it=tqdm_stats["n"],
            tot_it=tqdm_stats["total"],
            time_ela=str(datetime.timedelta(seconds=round(tqdm_stats["elapsed"]))),
            time_rem=str(
                datetime.timedelta(
                    seconds=round(
                        (tqdm_stats["total"] - tqdm_stats["n"])
                        / tqdm_stats["n"]
                        * tqdm_stats["elapsed"]
                        if tqdm_stats["n"]
                        else 0
                    )
                )
            ),
            cancel_func=cancel,
        )

    # create all time plots
    def create_time_plots(data, save_path_base, temporal_units, pbar, counts_df):
        # maximum number of ticks per x axis
        max_n_ticks = 50

        # define specific functions per plot type
        def plot_obs_over_time_total_static(time_unit):
            plt.figure(figsize=(10, 6))
            combined_data = (
                grouped_data.sum(axis=0)
                .resample(time_format_mapping[time_unit]["freq"])
                .sum()
            )
            plt.bar(
                combined_data.index.strftime(
                    time_format_mapping[time_unit]["time_format"]
                ),
                combined_data,
                width=0.9,
            )
            plt.suptitle("")
            plt.title(
                f"Total observations (grouped per {time_unit}, n = {counts_df['count'].sum()})"
            )
            plt.ylabel("Count")
            plt.xlabel(time_unit)
            plt.xticks(rotation=90)
            x_vals = np.arange(len(combined_data))
            tick_step = max(len(combined_data) // max_n_ticks, 1)
            selected_ticks = x_vals[::tick_step]
            while_iteration = 0
            while len(selected_ticks) >= max_n_ticks:
                tick_step += 1
                while_iteration += 1
                selected_ticks = x_vals[::tick_step]
                if while_iteration > 100:
                    break
            selected_labels = combined_data.index.strftime(
                time_format_mapping[time_unit]["time_format"]
            )[::tick_step]
            plt.xticks(selected_ticks, selected_labels)
            plt.tight_layout()
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "bar-charts",
                time_format_mapping[time_unit]["dir"],
                "combined-single-layer.png",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            update_pbar_plt()

        def plot_obs_over_time_total_interactive(time_unit):
            combined_data = (
                grouped_data.sum(axis=0)
                .resample(time_format_mapping[time_unit]["freq"])
                .sum()
            )
            hover_text = [
                f"Period: {date}<br>Count: {count}<extra></extra>"
                for date, count in zip(
                    combined_data.index.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    ),
                    combined_data,
                )
            ]
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=combined_data.index.strftime(
                            time_format_mapping[time_unit]["time_format"]
                        ),
                        y=combined_data,
                        hovertext=hover_text,
                        hoverinfo="text",
                    )
                ]
            )
            fig.update_traces(hovertemplate="%{hovertext}")
            fig.update_layout(
                title=f"Total observations (grouped per {time_unit})",
                xaxis_title="Period",
                yaxis_title="Count",
                xaxis_tickangle=90,
            )
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "bar-charts",
                time_format_mapping[time_unit]["dir"],
                "combined-single-layer.html",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        def plot_obs_over_time_combined_static(time_unit):
            plt.figure(figsize=(10, 6))
            for label in grouped_data.index:
                grouped_data_indexed = (
                    grouped_data.loc[label]
                    .resample(time_format_mapping[time_unit]["freq"])
                    .sum()
                )
                plt.plot(
                    grouped_data_indexed.index.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    ),
                    grouped_data_indexed,
                    label=label,
                )
            plt.suptitle("")
            plt.title(
                f"Observations over time (grouped per {time_unit}, n = {counts_df['count'].sum()})"
            )
            plt.ylabel("Count")
            plt.xticks(rotation=90)
            plt.xlabel(time_unit)
            plt.legend(loc="upper right")
            x_vals = np.arange(len(grouped_data_indexed))
            tick_step = max(len(grouped_data_indexed) // max_n_ticks, 1)
            selected_ticks = x_vals[::tick_step]
            while_iteration = 0
            while len(selected_ticks) >= max_n_ticks:
                tick_step += 1
                while_iteration += 1
                selected_ticks = x_vals[::tick_step]
                if while_iteration > 100:
                    break
            selected_labels = grouped_data_indexed.index.strftime(
                time_format_mapping[time_unit]["time_format"]
            )[::tick_step]
            plt.xticks(selected_ticks, selected_labels)
            plt.tight_layout()
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "bar-charts",
                time_format_mapping[time_unit]["dir"],
                "combined-multi-layer.png",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            update_pbar_plt()

        def plot_obs_over_time_combined_interactive(time_unit):
            fig = go.Figure()
            for label in grouped_data.index:
                grouped_data_indexed = (
                    grouped_data.loc[label]
                    .resample(time_format_mapping[time_unit]["freq"])
                    .sum()
                )
                fig.add_trace(
                    go.Scatter(
                        x=grouped_data_indexed.index.strftime(
                            time_format_mapping[time_unit]["time_format"]
                        ),
                        y=grouped_data_indexed,
                        mode="lines",
                        name=label,
                    )
                )
            fig.update_layout(
                title=f"Observations over time (grouped per {time_unit})",
                xaxis_title="Period",
                yaxis_title="Count",
                xaxis_tickangle=90,
                legend=dict(x=0, y=1.0),
            )
            fig.update_layout(hovermode="x unified")
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "bar-charts",
                time_format_mapping[time_unit]["dir"],
                "combined-multi-layer.html",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        def plot_obs_over_time_separate_static(label, time_unit):
            plt.figure(figsize=(10, 6))
            grouped_data_indexed = (
                grouped_data.loc[label]
                .resample(time_format_mapping[time_unit]["freq"])
                .sum()
            )
            plt.bar(
                grouped_data_indexed.index.strftime(
                    time_format_mapping[time_unit]["time_format"]
                ),
                grouped_data_indexed,
                label=label,
                width=0.9,
            )
            plt.suptitle("")
            plt.title(
                f"Observations over time for {label} (grouped per {time_unit}, n = {counts_df[counts_df['label'] == label]['count'].values[0]})"
            )
            plt.ylabel("Count")
            plt.xticks(rotation=90)
            plt.xlabel(time_unit)
            x_vals = np.arange(len(grouped_data_indexed))
            tick_step = max(len(grouped_data_indexed) // max_n_ticks, 1)
            selected_ticks = x_vals[::tick_step]
            while_iteration = 0
            while len(selected_ticks) >= max_n_ticks:
                tick_step += 1
                while_iteration += 1
                selected_ticks = x_vals[::tick_step]
                if while_iteration > 100:
                    break
            selected_labels = grouped_data_indexed.index.strftime(
                time_format_mapping[time_unit]["time_format"]
            )[::tick_step]
            plt.xticks(selected_ticks, selected_labels)
            plt.tight_layout()
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "bar-charts",
                time_format_mapping[time_unit]["dir"],
                "class-specific",
                f"{label}.png",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            update_pbar_plt()

        def plot_obs_over_time_separate_interactive(label, time_unit):
            grouped_data_indexed = (
                grouped_data.loc[label]
                .resample(time_format_mapping[time_unit]["freq"])
                .sum()
            )
            hover_text = [
                f"Period: {date}<br>Count: {count}<extra></extra>"
                for date, count in zip(
                    grouped_data_indexed.index.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    ),
                    grouped_data_indexed,
                )
            ]
            fig = go.Figure(
                go.Bar(
                    x=grouped_data_indexed.index.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    ),
                    y=grouped_data_indexed,
                    hovertext=hover_text,
                    hoverinfo="text",
                )
            )
            fig.update_traces(hovertemplate="%{hovertext}")
            fig.update_layout(
                title=f"Observations over time for {label} (grouped per {time_unit})",
                xaxis_title="Period",
                yaxis_title="Count",
                xaxis_tickangle=90,
            )
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "bar-charts",
                time_format_mapping[time_unit]["dir"],
                "class-specific",
                f"{label}.html",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        def plot_obs_over_time_heatmap_static_absolute(time_unit):
            data["Period"] = data["DateTimeOriginal"].dt.strftime(
                time_format_mapping[time_unit]["time_format"]
            )
            time_range = pd.Series(
                pd.date_range(
                    data["DateTimeOriginal"].min(),
                    data["DateTimeOriginal"].max(),
                    freq=time_format_mapping[time_unit]["freq"],
                )
            )
            df_time = pd.DataFrame(
                {
                    time_unit: time_range.dt.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    )
                }
            )
            heatmap_data = (
                data.groupby(["Period", "label"]).size().unstack(fill_value=0)
            )
            merged_data = pd.merge(
                df_time, heatmap_data, left_on=time_unit, right_index=True, how="left"
            ).fillna(0)
            merged_data.set_index(time_unit, inplace=True)
            merged_data = merged_data.sort_index()
            plt.figure(figsize=(14, 8))
            ax = sns.heatmap(merged_data, cmap="Blues")
            sorted_labels = sorted(merged_data.columns)
            ax.set_xticks([i + 0.5 for i in range(len(sorted_labels))])
            ax.set_xticklabels(sorted_labels)
            plt.title(
                f"Temporal heatmap (absolute values, grouped per {time_unit}, n = {counts_df['count'].sum()})"
            )
            plt.tight_layout()
            legend_text = "Number of observations"
            ax.collections[0].colorbar.set_label(legend_text)
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "temporal-heatmaps",
                time_format_mapping[time_unit]["dir"],
                "absolute",
                "temporal-heatmap.png",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            update_pbar_plt()

        def plot_obs_over_time_heatmap_static_relative(time_unit):
            data["Period"] = data["DateTimeOriginal"].dt.strftime(
                time_format_mapping[time_unit]["time_format"]
            )
            time_range = pd.Series(
                pd.date_range(
                    data["DateTimeOriginal"].min(),
                    data["DateTimeOriginal"].max(),
                    freq=time_format_mapping[time_unit]["freq"],
                )
            )
            df_time = pd.DataFrame(
                {
                    time_unit: time_range.dt.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    )
                }
            )
            heatmap_data = (
                data.groupby(["Period", "label"]).size().unstack(fill_value=0)
            )
            normalized_data = heatmap_data.div(heatmap_data.sum(axis=0), axis=1)
            merged_data = pd.merge(
                df_time,
                normalized_data,
                left_on=time_unit,
                right_index=True,
                how="left",
            ).fillna(0)
            merged_data.set_index(time_unit, inplace=True)
            merged_data = merged_data.sort_index()
            plt.figure(figsize=(14, 8))
            ax = sns.heatmap(merged_data, cmap="Blues")
            sorted_labels = sorted(normalized_data.columns)
            ax.set_xticks([i + 0.5 for i in range(len(sorted_labels))])
            ax.set_xticklabels(sorted_labels)
            plt.title(
                f"Temporal heatmap (relative values, grouped per {time_unit}, n = {counts_df['count'].sum()})"
            )
            plt.tight_layout()
            legend_text = "Number of observations normalized per label"
            ax.collections[0].colorbar.set_label(legend_text)
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "temporal-heatmaps",
                time_format_mapping[time_unit]["dir"],
                "relative",
                "temporal-heatmap.png",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            update_pbar_plt()

        def plot_obs_over_time_heatmap_interactive_absolute(time_unit):
            data["Period"] = data["DateTimeOriginal"].dt.strftime(
                time_format_mapping[time_unit]["time_format"]
            )
            time_range = pd.Series(
                pd.date_range(
                    data["DateTimeOriginal"].min(),
                    data["DateTimeOriginal"].max(),
                    freq=time_format_mapping[time_unit]["freq"],
                )
            )
            df_time = pd.DataFrame(
                {
                    time_unit: time_range.dt.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    )
                }
            )
            heatmap_data = (
                data.groupby(["Period", "label"]).size().unstack(fill_value=0)
            )
            merged_data = pd.merge(
                df_time, heatmap_data, left_on=time_unit, right_index=True, how="left"
            ).fillna(0)
            merged_data.set_index(time_unit, inplace=True)
            heatmap_trace = go.Heatmap(
                z=merged_data.values,
                x=merged_data.columns,
                y=merged_data.index,
                customdata=merged_data.stack().reset_index().values.tolist(),
                colorscale="Blues",
                hovertemplate="Class: %{x}<br>Period: %{y}<br>Count: %{z}<extra></extra>",
                colorbar=dict(title="Number of<br>observations"),
            )
            fig = go.Figure(data=heatmap_trace)
            fig.update_layout(
                title=f"Temporal heatmap (absolute values, grouped per {time_unit}, n = {counts_df['count'].sum()})",
                xaxis_title="Label",
                yaxis_title="Period",
                yaxis={"autorange": "reversed"},
            )
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "temporal-heatmaps",
                time_format_mapping[time_unit]["dir"],
                "absolute",
                "temporal-heatmap.html",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        def plot_obs_over_time_heatmap_interactive_relative(time_unit):
            data["Period"] = data["DateTimeOriginal"].dt.strftime(
                time_format_mapping[time_unit]["time_format"]
            )
            time_range = pd.date_range(
                data["DateTimeOriginal"].min(),
                data["DateTimeOriginal"].max(),
                freq=time_format_mapping[time_unit]["freq"],
            )
            df_time = pd.DataFrame(
                {
                    time_unit: time_range.strftime(
                        time_format_mapping[time_unit]["time_format"]
                    )
                }
            )
            heatmap_data = (
                data.groupby(["Period", "label"]).size().unstack(fill_value=0)
            )
            merged_data = pd.merge(
                df_time, heatmap_data, left_on=time_unit, right_index=True, how="left"
            ).fillna(0)
            merged_data.set_index(time_unit, inplace=True)
            normalized_data = merged_data.div(merged_data.sum(axis=0), axis=1)
            heatmap_trace = go.Heatmap(
                z=normalized_data.values,
                x=normalized_data.columns,
                y=normalized_data.index,
                customdata=normalized_data.stack().reset_index().values.tolist(),
                colorscale="Blues",
                hovertemplate="Class: %{x}<br>Period: %{y}<br>Normalized count: %{z}<extra></extra>",
                colorbar=dict(
                    title="Number of<br>observations<br>normalized<br>per label"
                ),
            )
            fig = go.Figure(data=heatmap_trace)
            fig.update_layout(
                title=f"Temporal heatmap (relative values, grouped per {time_unit}, n = {counts_df['count'].sum()}))",
                xaxis_title="Label",
                yaxis_title="Period",
                yaxis={"autorange": "reversed"},
            )
            save_path = os.path.join(
                save_path_base,
                "graphs",
                "temporal-heatmaps",
                time_format_mapping[time_unit]["dir"],
                "relative",
                "temporal-heatmap.html",
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        # init vars
        time_format_mapping = {
            "year": {"freq": "Y", "time_format": "%Y", "dir": "grouped-by-year"},
            "month": {"freq": "M", "time_format": "%Y-%m", "dir": "grouped-by-month"},
            "week": {"freq": "W", "time_format": "%Y-wk %U", "dir": "grouped-by-week"},
            "day": {"freq": "D", "time_format": "%Y-%m-%d", "dir": "grouped-by-day"},
        }

        # group data per label
        grouped_data = (
            data.groupby(["label", pd.Grouper(key="DateTimeOriginal", freq=f"1D")])
            .size()
            .unstack(fill_value=0)
        )

        # create plots
        for time_unit in temporal_units:
            plot_obs_over_time_total_static(time_unit)
            plt.close("all")
            plot_obs_over_time_total_interactive(time_unit)
            plt.close("all")
            plot_obs_over_time_combined_static(time_unit)
            plt.close("all")
            plot_obs_over_time_combined_interactive(time_unit)
            plt.close("all")
            plot_obs_over_time_heatmap_static_absolute(time_unit)
            plt.close("all")
            plot_obs_over_time_heatmap_static_relative(time_unit)
            plt.close("all")
            plot_obs_over_time_heatmap_interactive_absolute(time_unit)
            plt.close("all")
            plot_obs_over_time_heatmap_interactive_relative(time_unit)
            plt.close("all")
            for label in grouped_data.index:
                plot_obs_over_time_separate_static(label, time_unit)
                plt.close("all")
                plot_obs_over_time_separate_interactive(label, time_unit)
                plt.close("all")

    # activity plots
    def create_activity_patterns(df, save_path_base, pbar):
        # format df
        df["DateTimeOriginal"] = pd.to_datetime(df["DateTimeOriginal"])
        grouped_data = (
            df.groupby(["label", pd.Grouper(key="DateTimeOriginal", freq=f"1D")])
            .size()
            .unstack(fill_value=0)
        )
        df["Hour"] = df["DateTimeOriginal"].dt.hour
        hourly_df = df.groupby(["label", "Hour"]).size().reset_index(name="count")
        df["Month"] = df["DateTimeOriginal"].dt.month
        monthly_df = df.groupby(["label", "Month"]).size().reset_index(name="count")

        # for static activity plots
        def plot_static_activity_pattern(df, unit, label=""):
            if label != "":
                df = df[df["label"] == label]
            total_observations = df["count"].sum()
            plt.figure(figsize=(10, 6))

            if unit == "Hour":
                x_ticks = range(24)
                x_tick_labels = [f"{x:02}-{(x + 1) % 24:02}" for x in x_ticks]
            else:
                x_ticks = range(1, 13)
                x_tick_labels = [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ]
            plt.bar(df[unit], df["count"], width=0.9, align="center")
            plt.xlabel(unit)
            plt.ylabel("Number of observations")
            plt.title(
                f"Activity pattern of {label if label != '' else 'all animals combined'} by {'hour of the day' if unit == 'Hour' else 'month of the year'} (n = {total_observations})"
            )
            plt.xticks(x_ticks, x_tick_labels, rotation=90)
            plt.tight_layout()
            if label != "":
                save_path = os.path.join(
                    save_path_base,
                    "graphs",
                    "activity-patterns",
                    "hour-of-day" if unit == "Hour" else "month-of-year",
                    "class-specific",
                    f"{label}.png",
                )
            else:
                save_path = os.path.join(
                    save_path_base,
                    "graphs",
                    "activity-patterns",
                    "hour-of-day" if unit == "Hour" else "month-of-year",
                    f"combined.png",
                )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            update_pbar_plt()

        # for dynamic activity plots
        def plot_dynamic_activity_pattern(df, unit, label=""):
            if label != "":
                df = df[df["label"] == label]
            n_ticks = 24 if unit == "Hour" else 12
            if unit == "Hour":
                x_ticks = list(range(24))
                x_tick_labels = [f"{x:02}-{(x + 1) % 24:02}" for x in x_ticks]
            else:
                x_ticks = list(range(12))
                x_tick_labels = [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                    "Jul",
                    "Aug",
                    "Sep",
                    "Oct",
                    "Nov",
                    "Dec",
                ]
                df.loc[:, "Month"] = df["Month"].map(
                    {i: calendar.month_abbr[i] for i in range(1, 13)}
                )
            df = df.groupby(unit, as_index=False)["count"].sum()
            if unit == "Month":
                all_months = pd.DataFrame(
                    {
                        "Month": [
                            "Jan",
                            "Feb",
                            "Mar",
                            "Apr",
                            "May",
                            "Jun",
                            "Jul",
                            "Aug",
                            "Sep",
                            "Oct",
                            "Nov",
                            "Dec",
                        ]
                    }
                )
                merged_df = all_months.merge(df, on="Month", how="left")
                merged_df["count"] = merged_df["count"].fillna(0)
                merged_df["count"] = merged_df["count"].astype(int)
                df = merged_df
            else:
                df = (
                    df.set_index(unit)
                    .reindex(range(n_ticks), fill_value=0)
                    .reset_index()
                )
            total_observations = df["count"].sum()
            fig = px.bar(
                df,
                x=unit,
                y="count",
                title=f"Activity pattern of {label if label != '' else 'all animals combined'} by {'hour of the day' if unit == 'Hour' else 'month of the year'} (n = {total_observations})",
            ).update_traces(width=0.7)
            fig.update_layout(
                xaxis=dict(tickmode="array", tickvals=x_ticks, ticktext=x_tick_labels),
                xaxis_title=unit,
                yaxis_title="Count",
                bargap=0.1,
            )
            if label != "":
                save_path = os.path.join(
                    save_path_base,
                    "graphs",
                    "activity-patterns",
                    "hour-of-day" if unit == "Hour" else "month-of-year",
                    "class-specific",
                    f"{label}.html",
                )
            else:
                save_path = os.path.join(
                    save_path_base,
                    "graphs",
                    "activity-patterns",
                    "hour-of-day" if unit == "Hour" else "month-of-year",
                    f"combined.html",
                )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            pbar.update(1)

        # run class-specific
        for label in grouped_data.index:
            plot_static_activity_pattern(hourly_df, "Hour", label)
            plt.close("all")
            plot_static_activity_pattern(monthly_df, "Month", label)
            plt.close("all")
            plot_dynamic_activity_pattern(hourly_df, "Hour", label)
            plt.close("all")
            plot_dynamic_activity_pattern(monthly_df, "Month", label)
            plt.close("all")

        # run combined
        plot_static_activity_pattern(hourly_df, "Hour", "")
        plt.close("all")
        plot_static_activity_pattern(monthly_df, "Month", "")
        plt.close("all")
        plot_dynamic_activity_pattern(hourly_df, "Hour", "")
        plt.close("all")
        plot_dynamic_activity_pattern(monthly_df, "Month", "")
        plt.close("all")

    # heatmaps and markers
    def create_geo_plots(data, save_path_base, pbar):
        # define specific functions per plot type
        def create_combined_multi_layer_clustermap(data, save_path_base):
            if len(data) == 0:
                return
            map_path = os.path.join(save_path_base, "graphs", "maps")
            unique_labels = data["label"].unique()
            checkboxes = {
                label: folium.plugins.MarkerCluster(name=label)
                for label in unique_labels
            }
            for label in unique_labels:
                label_data = data[data["label"] == label]
                max_lat, min_lat = (
                    label_data["Latitude"].max(),
                    label_data["Latitude"].min(),
                )
                max_lon, min_lon = (
                    label_data["Longitude"].max(),
                    label_data["Longitude"].min(),
                )
                center_lat, center_lon = (
                    label_data["Latitude"].mean(),
                    label_data["Longitude"].mean(),
                )
                m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
                m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
                for _, row in label_data.iterrows():
                    folium.Marker(location=[row["Latitude"], row["Longitude"]]).add_to(
                        checkboxes[label]
                    )
                folium.TileLayer("openstreetmap").add_to(m)
                folium.LayerControl().add_to(m)
                Draw(export=True).add_to(m)
            max_lat, min_lat = data["Latitude"].max(), data["Latitude"].min()
            max_lon, min_lon = data["Longitude"].max(), data["Longitude"].min()
            center_lat, center_lon = data["Latitude"].mean(), data["Longitude"].mean()
            m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
            for label, marker_cluster in checkboxes.items():
                marker_cluster.add_to(m)
            folium.LayerControl(collapsed=False).add_to(m)
            Draw(export=True).add_to(m)
            combined_multi_layer_file = os.path.join(
                map_path, "combined-multi-layer.html"
            )
            Path(os.path.dirname(combined_multi_layer_file)).mkdir(
                parents=True, exist_ok=True
            )
            m.save(combined_multi_layer_file)
            update_pbar_plt()

        # this creates a heatmap layer and a clustermarker layer which can be dynamically enabled
        def create_obs_over_geo_both_heat_and_mark(data, save_path_base, category=""):
            if category != "":
                data = data[data["label"] == category]
            data = data.dropna(subset=["Latitude", "Longitude"])
            if len(data) == 0:
                return
            map_path = os.path.join(save_path_base, "graphs", "maps")
            max_lat, min_lat = data["Latitude"].max(), data["Latitude"].min()
            max_lon, min_lon = data["Longitude"].max(), data["Longitude"].min()
            center_lat, center_lon = data["Latitude"].mean(), data["Longitude"].mean()
            m = folium.Map(location=[center_lat, center_lon], zoom_start=10)
            m.fit_bounds([(min_lat, min_lon), (max_lat, max_lon)])
            folium.TileLayer("OpenStreetMap", overlay=False).add_to(m)
            Draw(export=True).add_to(m)
            heatmap_layer = folium.FeatureGroup(
                name="Heatmap", show=True, overlay=True
            ).add_to(m)
            cluster_layer = MarkerCluster(
                name="Markers", show=False, overlay=True
            ).add_to(m)
            HeatMap(data[["Latitude", "Longitude"]]).add_to(heatmap_layer)
            for _, row in data.iterrows():
                folium.Marker(location=[row["Latitude"], row["Longitude"]]).add_to(
                    cluster_layer
                )
            folium.LayerControl(collapsed=False).add_to(m)
            if category != "":
                map_file = os.path.join(map_path, "class-specific", f"{category}.html")
            else:
                map_file = os.path.join(map_path, "combined-single-layer.html")
            Path(os.path.dirname(map_file)).mkdir(parents=True, exist_ok=True)
            m.save(map_file)
            update_pbar_plt()

        # create plots
        create_obs_over_geo_both_heat_and_mark(data, save_path_base)
        plt.close("all")
        create_combined_multi_layer_clustermap(data, save_path_base)
        plt.close("all")
        for label in data["label"].unique():
            create_obs_over_geo_both_heat_and_mark(data, save_path_base, label)
            plt.close("all")

    # create pie charts with distributions
    def create_pie_plots_detections(df, results_dir, pbar):
        # def nested function
        def create_pie_chart_detections_static():
            label_counts = df["label"].value_counts()
            total_count = len(df["label"])
            percentages = label_counts / total_count * 100
            hidden_categories = list(percentages[percentages < 0].index)
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            wedges, _, autotexts = ax1.pie(label_counts, autopct="", startangle=140)
            ax1.axis("equal")
            for i, autotext in enumerate(autotexts):
                if label_counts.index[i] in hidden_categories:
                    autotext.set_visible(False)
            legend_labels = [
                "%s (n = %s, %.1f%%)"
                % (label, count, (float(count) / len(df["label"])) * 100)
                for label, count in zip(label_counts.index, label_counts)
            ]
            ax2.legend(wedges, legend_labels, loc="center", fontsize="medium")
            ax2.axis("off")
            for autotext in autotexts:
                autotext.set_bbox(
                    dict(
                        facecolor="white", edgecolor="black", boxstyle="square,pad=0.2"
                    )
                )
            fig.suptitle(
                f"Distribution of detections (n = {total_count})", fontsize=16, y=0.95
            )
            plt.subplots_adjust(wspace=0.1)
            plt.tight_layout()
            save_path = os.path.join(
                results_dir, "graphs", "pie-charts", "distribution-detections.png"
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path)
            update_pbar_plt()

        def create_pie_chart_detections_interactive():
            grouped_df = df.groupby("label").size().reset_index(name="count")
            total_count = grouped_df["count"].sum()
            grouped_df["percentage"] = (grouped_df["count"] / total_count) * 100
            grouped_df["percentage"] = (
                grouped_df["percentage"].round(2).astype(str) + "%"
            )
            fig = px.pie(
                grouped_df,
                names="label",
                values="count",
                title=f"Distribution of detections (n = {total_count})",
                hover_data={"percentage"},
            )
            fig.update_traces(textinfo="label")
            save_path = os.path.join(
                results_dir, "graphs", "pie-charts", "distribution-detections.html"
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        # run
        create_pie_chart_detections_static()
        plt.close("all")
        create_pie_chart_detections_interactive()
        plt.close("all")

    # create pie charts with distributions
    def create_pie_plots_files(df, results_dir, pbar):
        # def nested function
        def create_pie_chart_files_static():
            df["label"] = df["n_detections"].apply(
                lambda x: "detection" if x >= 1 else "empty"
            )
            label_counts = df["label"].value_counts()
            total_count = len(df["label"])
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

            def autopct_func(pct):
                if pct > 0:
                    return f"{pct:.1f}%"
                else:
                    return ""

            labels = [label for label in label_counts.index]
            wedges, texts, autotexts = ax1.pie(
                label_counts, labels=labels, autopct=autopct_func, startangle=140
            )
            ax1.axis("equal")
            legend_labels = [
                "%s (n = %s, %.1f%%)"
                % (label, count, (float(count) / len(df["label"])) * 100)
                for label, count in zip(label_counts.index, label_counts)
            ]
            ax2.legend(wedges, legend_labels, loc="center", fontsize="medium")
            ax2.axis("off")
            for autotext in autotexts:
                autotext.set_bbox(
                    dict(
                        facecolor="white", edgecolor="black", boxstyle="square,pad=0.2"
                    )
                )
            fig.suptitle(
                f"Distribution of files (n = {total_count})", fontsize=16, y=0.95
            )
            plt.subplots_adjust(wspace=0.5)
            save_path = os.path.join(
                results_dir, "graphs", "pie-charts", "distribution-files.png"
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.savefig(save_path)
            update_pbar_plt()

        def create_pie_chart_files_interactive():
            df["label"] = df["n_detections"].apply(
                lambda x: "detection" if x >= 1 else "empty"
            )
            grouped_df = df.groupby("label").size().reset_index(name="count")
            total_count = grouped_df["count"].sum()
            grouped_df["percentage"] = (grouped_df["count"] / total_count) * 100
            grouped_df["percentage"] = (
                grouped_df["percentage"].round(2).astype(str) + "%"
            )
            fig = px.pie(
                grouped_df,
                names="label",
                values="count",
                title=f"Distribution of files (n = {total_count})",
                hover_data={"percentage"},
            )
            fig.update_traces(textinfo="label")
            save_path = os.path.join(
                results_dir, "graphs", "pie-charts", "distribution-files.html"
            )
            Path(os.path.dirname(save_path)).mkdir(parents=True, exist_ok=True)
            fig.write_html(save_path)
            update_pbar_plt()

        # run
        create_pie_chart_files_static()
        plt.close("all")
        create_pie_chart_files_interactive()
        plt.close("all")

    # overlay logo
    def overlay_logo(image_path, logo):
        main_image = Image.open(image_path)
        main_width, main_height = main_image.size
        logo_width, logo_height = logo.size
        position = (main_width - logo_width - 10, 10)
        main_image.paste(logo, position, logo)
        main_image.save(image_path)

    # check the time difference in the dataset
    def calculate_time_span(df):
        any_dates_present = df["DateTimeOriginal"].notnull().any()
        if not any_dates_present:
            return 0, 0, 0, 0
        first_date = df["DateTimeOriginal"].min()
        last_date = df["DateTimeOriginal"].max()
        time_difference = last_date - first_date
        days = time_difference.days
        years = int(days / 365)
        months = int(days / 30)
        weeks = int(days / 7)
        return years, months, weeks, days

    # main code to plot graphs
    results_dir = os.path.normpath(results_dir)
    plots_dir = os.path.join(results_dir, "graphs")
    det_df = pd.read_csv(os.path.join(results_dir, "results_detections.csv"))
    fil_df = pd.read_csv(os.path.join(results_dir, "results_files.csv"))

    # for the temporal plots we need to check the number of units
    det_df["DateTimeOriginal"] = pd.to_datetime(
        det_df["DateTimeOriginal"], format="%d/%m/%y %H:%M:%S"
    )
    n_years, n_months, n_weeks, n_days = calculate_time_span(det_df)

    # to limit unnecessary computing only plot units if they have a minimum of 2 and a maximum of *max_units* units
    temporal_units = []
    max_units = 100
    if n_years > 1:
        temporal_units.append("year")
    if 1 < n_months <= max_units:
        temporal_units.append("month")
    if 1 < n_weeks <= max_units:
        temporal_units.append("week")
    if 1 < n_days <= max_units:
        temporal_units.append("day")
    print(f"Years: {n_years}, Months: {n_months}, Weeks: {n_weeks}, Days: {n_days}")
    print(f"temporal_units : {temporal_units}")

    # check if we have geo tags in the data
    det_df_geo = det_df[
        (det_df["Latitude"].notnull()) & (det_df["Longitude"].notnull())
    ]
    if len(det_df_geo) > 0:
        data_permits_map_creation = True
        n_categories_geo = len(det_df_geo["label"].unique())
    else:
        data_permits_map_creation = False
        n_categories_geo = 0

    # calculate the number of plots to be created
    any_dates_present = det_df["DateTimeOriginal"].notnull().any()
    n_categories_with_timestamps = len(
        det_df[det_df["DateTimeOriginal"].notnull()]["label"].unique()
    )
    n_obs_per_label_with_timestamps = (
        det_df[det_df["DateTimeOriginal"].notnull()]
        .groupby("label")
        .size()
        .reset_index(name="count")
    )
    activity_patterns_n_plots = (
        (((n_categories_with_timestamps * 2) + 2) * 2) if any_dates_present else 0
    )
    bar_charts_n_plots = (
        (((n_categories_with_timestamps * 2) + 4) * len(temporal_units))
        if any_dates_present
        else 0
    )
    maps_n_plots = (n_categories_geo + 2) if data_permits_map_creation else 0
    pie_charts_n_plots = 4
    temporal_heatmaps_n_plots = (4 * len(temporal_units)) if any_dates_present else 0
    n_plots = (
        activity_patterns_n_plots
        + bar_charts_n_plots
        + maps_n_plots
        + pie_charts_n_plots
        + temporal_heatmaps_n_plots
    )

    # create plots
    with tqdm(total=n_plots, disable=False) as pbar:
        progress_window.update_values(process=f"plt", status="load")
        if any_dates_present:
            create_time_plots(
                det_df,
                results_dir,
                temporal_units,
                pbar,
                n_obs_per_label_with_timestamps,
            )
            plt.close("all")
        if cancel_var:
            return
        if data_permits_map_creation:
            create_geo_plots(det_df_geo, results_dir, pbar)
            plt.close("all")
        if cancel_var:
            return
        create_pie_plots_detections(det_df, results_dir, pbar)
        plt.close("all")
        if cancel_var:
            return
        create_pie_plots_files(fil_df, results_dir, pbar)
        plt.close("all")
        if cancel_var:
            return
        if any_dates_present:
            create_activity_patterns(det_df, results_dir, pbar)
            plt.close("all")
        if cancel_var:
            return

    # add addaxai logo
    logo_for_graphs = PIL_logo_incl_text.resize(
        (int(LOGO_WIDTH / 1.2), int(LOGO_HEIGHT / 1.2))
    )
    for root, dirs, files in os.walk(plots_dir):
        for file in files:
            if file.endswith(".png"):
                image_path = os.path.join(root, file)
                overlay_logo(image_path, logo_for_graphs)

    # end pbar
    progress_window.update_values(process=f"plt", status="done")


# open human-in-the-loop verification windows
def open_annotation_windows(recognition_file, class_list_txt, file_list_txt, label_map):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # check if file list exists
    if not os.path.isfile(file_list_txt):
        mb.showerror(
            ["No images to verify", "No hay imágenes para verificar"][lang_idx],
            [
                "There are no images to verify with the selected criteria. Use the 'Update counts' button to see how many "
                "images you need to verify with the selected criteria.",
                "No hay imágenes para verificar con los criterios "
                "seleccionados. Utilice el botón 'Actualizar recuentos' para ver cuántas imágenes necesita verificar con "
                "los criterios seleccionados.",
            ][lang_idx],
        )
        return

    # check number of images to verify
    total_n_files = 0
    with open(file_list_txt) as f:
        for line in f:
            total_n_files += 1
    if total_n_files == 0:
        mb.showerror(
            ["No images to verify", "No hay imágenes para verificar"][lang_idx],
            [
                "There are no images to verify with the selected criteria. Use the 'Update counts' button to see how many "
                "images you need to verify with the selected criteria.",
                "No hay imágenes para verificar con los criterios "
                "seleccionados. Utilice el botón 'Actualizar recuentos' para ver cuántas imágenes necesita verificar con "
                "los criterios seleccionados.",
            ][lang_idx],
        )
        return

    # check corrupted images
    corrupted_images = check_images(file_list_txt)

    # fix images
    if len(corrupted_images) > 0:
        if mb.askyesno(
            ["Corrupted images found", "Imágenes corruptas encontradas"][lang_idx],
            [
                f"There are {len(corrupted_images)} images corrupted. Do you want to repair?",
                f"Hay {len(corrupted_images)} imágenes corruptas. Quieres repararlas?",
            ][lang_idx],
        ):
            fix_images(corrupted_images)

    # read label map from json
    label_map = fetch_label_map_from_json(recognition_file)
    inverted_label_map = {v: k for k, v in label_map.items()}

    # count n verified files and locate images that need converting
    n_verified_files = 0
    if get_hitl_var_in_json(recognition_file) != "never-started":
        init_dialog = PatienceDialog(
            total=total_n_files, text=["Initializing...", "Inicializando..."][lang_idx]
        )
        init_dialog.open()
        init_current = 1
        imgs_needing_converting = []
        with open(file_list_txt) as f:
            for line in f:
                img = line.rstrip()
                annotation = return_xml_path(img)

                # check which need converting to json
                if check_if_img_needs_converting(img):
                    imgs_needing_converting.append(img)

                # check how many are verified
                if verification_status(annotation):
                    n_verified_files += 1

                # update progress window
                init_dialog.update_progress(current=init_current, percentage=True)
                init_current += 1
        init_dialog.close()

    # track hitl progress in json
    change_hitl_var_in_json(recognition_file, "in-progress")

    # close settings window if open
    try:
        hitl_settings_window.destroy()
    except NameError:
        print("hitl_settings_window not defined -> nothing to destroy()")

    # init window
    hitl_progress_window = customtkinter.CTkToplevel(root)
    hitl_progress_window.title(
        ["Manual check overview", "Verificación manual"][lang_idx]
    )
    hitl_progress_window.geometry("+10+10")

    # explanation frame
    hitl_explanation_frame = LabelFrame(
        hitl_progress_window,
        text=[" Explanation ", " Explicación "][lang_idx],
        pady=2,
        padx=5,
        relief="solid",
        highlightthickness=5,
        font=100,
        fg=green_primary,
    )
    hitl_explanation_frame.configure(font=(text_font, 15, "bold"))
    hitl_explanation_frame.grid(column=0, row=1, columnspan=2, sticky="ew")
    hitl_explanation_frame.columnconfigure(0, weight=3, minsize=115)
    hitl_explanation_frame.columnconfigure(1, weight=1, minsize=115)

    # explanation text
    text_hitl_explanation_frame = Text(
        master=hitl_explanation_frame,
        wrap=WORD,
        width=1,
        height=15 * explanation_text_box_height_factor,
    )
    text_hitl_explanation_frame.grid(
        column=0, row=0, columnspan=5, padx=5, pady=5, sticky="ew"
    )
    text_hitl_explanation_frame.tag_config(
        "explanation",
        font=f"{text_font} {int(13 * text_size_adjustment_factor)} normal",
        lmargin1=10,
        lmargin2=10,
    )
    text_hitl_explanation_frame.insert(
        END,
        [
            "This is where you do the actual verification. You'll have to make sure that all objects in all images are correctly "
            "labeled. That also includes classes that you did not select but are on the image by chance. If an image is verified, "
            "you'll have to let AddaxAI know by pressing the space bar. If all images are verified and up-to-date, you can close "
            "the window. AddaxAI will prompt you for the final step. You can also close the window and continue at a later moment.",
            "Deberá asegurarse de que todos los objetos en todas las imágenes estén "
            "etiquetados correctamente. Eso también incluye clases que no seleccionaste pero que están en la imagen por casualidad. "
            "Si se verifica una imagen, deberá informar a AddaxAI presionando la barra espaciadora. Si todas las imágenes están "
            "verificadas y actualizadas, puede cerrar la ventana. AddaxAI le indicará el paso final. También puedes cerrar la "
            "ventana y continuar en otro momento.",
        ][lang_idx],
    )
    text_hitl_explanation_frame.tag_add("explanation", "1.0", "1.end")

    # shortcuts frame
    hitl_shortcuts_frame = LabelFrame(
        hitl_progress_window,
        text=[" Shortcuts ", " Atajos "][lang_idx],
        pady=2,
        padx=5,
        relief="solid",
        highlightthickness=5,
        font=100,
        fg=green_primary,
    )
    hitl_shortcuts_frame.configure(font=(text_font, 15, "bold"))
    hitl_shortcuts_frame.grid(column=0, row=2, columnspan=2, sticky="ew")
    hitl_shortcuts_frame.columnconfigure(0, weight=3, minsize=115)
    hitl_shortcuts_frame.columnconfigure(1, weight=1, minsize=115)

    # shortcuts label
    shortcut_labels = [
        [
            "Next image:",
            "Previous image:",
            "Create box:",
            "Edit box:",
            "Delete box:",
            "Verify, save, and next image:",
        ],
        [
            "Imagen siguiente:",
            "Imagen anterior:",
            "Crear cuadro:",
            "Editar cuadro:",
            "Eliminar cuadro:",
            "Verificar, guardar, y siguiente imagen:",
        ],
    ][lang_idx]
    shortcut_values = ["d", "a", "w", "s", "del", ["space", "espacio"][lang_idx]]
    for i in range(len(shortcut_labels)):
        ttk.Label(master=hitl_shortcuts_frame, text=shortcut_labels[i]).grid(
            column=0, row=i, columnspan=1, sticky="w"
        )
        ttk.Label(master=hitl_shortcuts_frame, text=shortcut_values[i]).grid(
            column=1, row=i, columnspan=1, sticky="e"
        )

    # numbers frame
    hitl_stats_frame = LabelFrame(
        hitl_progress_window,
        text=[" Progress ", " Progreso "][lang_idx],
        pady=2,
        padx=5,
        relief="solid",
        highlightthickness=5,
        font=100,
        fg=green_primary,
    )
    hitl_stats_frame.configure(font=(text_font, 15, "bold"))
    hitl_stats_frame.grid(column=0, row=3, columnspan=2, sticky="ew")
    hitl_stats_frame.columnconfigure(0, weight=3, minsize=115)
    hitl_stats_frame.columnconfigure(1, weight=1, minsize=115)

    # progress bar
    hitl_progbar = ttk.Progressbar(
        master=hitl_stats_frame, orient="horizontal", mode="determinate", length=280
    )
    hitl_progbar.grid(column=0, row=0, columnspan=2, padx=5, pady=(3, 0))

    # percentage done
    lbl_hitl_stats_percentage = ttk.Label(
        master=hitl_stats_frame,
        text=["Percentage done:", "Porcentaje realizado:"][lang_idx],
    )
    lbl_hitl_stats_percentage.grid(column=0, row=1, columnspan=1, sticky="w")
    value_hitl_stats_percentage = ttk.Label(master=hitl_stats_frame, text="")
    value_hitl_stats_percentage.grid(column=1, row=1, columnspan=1, sticky="e")

    # total n images to verify
    lbl_hitl_stats_verified = ttk.Label(
        master=hitl_stats_frame,
        text=["Files verified:", "Archivos verificados:"][lang_idx],
    )
    lbl_hitl_stats_verified.grid(column=0, row=2, columnspan=1, sticky="w")
    value_hitl_stats_verified = ttk.Label(master=hitl_stats_frame, text="")
    value_hitl_stats_verified.grid(column=1, row=2, columnspan=1, sticky="e")

    # show window
    percentage = round((n_verified_files / total_n_files) * 100)
    hitl_progbar["value"] = percentage
    value_hitl_stats_percentage.configure(text=f"{percentage}%")
    value_hitl_stats_verified.configure(text=f"{n_verified_files}/{total_n_files}")
    hitl_progress_window.update_idletasks()
    hitl_progress_window.update()

    # init paths
    labelImg_dir = os.path.join(AddaxAI_files, "Human-in-the-loop")
    labelImg_script = os.path.join(labelImg_dir, "labelImg.py")
    python_executable = get_python_interprator("base")

    # create command
    command_args = []
    command_args.append(python_executable)
    command_args.append(labelImg_script)
    command_args.append(class_list_txt)
    command_args.append(file_list_txt)

    # adjust command for unix OS
    if os.name != "nt":
        command_args = "'" + "' '".join(command_args) + "'"

    # prepend os-specific commands
    platform_name = platform.system().lower()
    if platform_name == "darwin" and "arm64" in platform.machine():
        print("This is an Apple Silicon system.")
        command_args = "arch -arm64 " + command_args

    # log command
    print(command_args)

    # run command
    p = Popen(
        command_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        shell=True,
        universal_newlines=True,
    )

    # read the output
    for line in p.stdout:
        print(line, end="")

        if "<EA>" in line:
            ver_diff = re.search("<EA>(.)<EA>", line).group().replace("<EA>", "")

            # adjust verification count
            if ver_diff == "+":
                n_verified_files += 1
            elif ver_diff == "-":
                n_verified_files -= 1

            # update labels
            percentage = round((n_verified_files / total_n_files) * 100)
            hitl_progbar["value"] = percentage
            value_hitl_stats_percentage.configure(text=f"{percentage}%")
            value_hitl_stats_verified.configure(
                text=f"{n_verified_files}/{total_n_files}"
            )

            # show window
            hitl_progress_window.update()

        # set save status
        try:
            hitl_progress_window.update_idletasks()
            hitl_progress_window.update()

        # python can throw a TclError if user closes the window because the widgets are destroyed - nothing to worry about
        except Exception as error:
            print(
                "\nWhen closing the annotation window, there was an error. python can throw a TclError if user closes "
                "the window because the widgets are destroyed - nothing to worry about."
            )
            print(
                "ERROR:\n"
                + str(error)
                + "\n\nDETAILS:\n"
                + str(traceback.format_exc())
                + "\n\n"
            )

    # close accompanying window
    hitl_progress_window.destroy()
    bind_scroll_to_deploy_canvas()

    # update frames of root
    update_frame_states()

    # check if the json has relative paths
    if check_json_paths(recognition_file) == "relative":
        json_paths_are_relative = True
    else:
        json_paths_are_relative = False

    # open patience window
    converting_patience_dialog = PatienceDialog(
        total=1,
        text=["Running verification...", "Verificación de funcionamiento..."][lang_idx],
    )
    converting_patience_dialog.open()

    # check which images need converting
    imgs_needing_converting = []
    with open(file_list_txt) as f:
        for line in f:
            img = line.rstrip()
            annotation = return_xml_path(img)
            if check_if_img_needs_converting(img):
                imgs_needing_converting.append(img)
    converting_patience_dialog.update_progress(current=1)
    converting_patience_dialog.close()

    # open json
    with open(recognition_file, "r") as image_recognition_file_content:
        n_img_in_json = len(json.load(image_recognition_file_content)["images"])

    # open patience window
    patience_dialog = PatienceDialog(
        total=len(imgs_needing_converting) + n_img_in_json,
        text=["Checking results...", "Comprobando resultados"][lang_idx],
    )
    patience_dialog.open()
    current = 1

    # convert
    update_json_from_img_list(
        imgs_needing_converting,
        inverted_label_map,
        recognition_file,
        patience_dialog,
        current,
    )
    current += len(imgs_needing_converting)

    # open json
    with open(recognition_file, "r") as image_recognition_file_content:
        data = json.load(image_recognition_file_content)

    # check if there are images that the user first verified and then un-verified
    for image in data["images"]:
        image_path = image["file"]
        patience_dialog.update_progress(current=current, percentage=True)
        current += 1
        if json_paths_are_relative:
            image_path = os.path.join(os.path.dirname(recognition_file), image_path)
        if "manually_checked" in image:
            if image["manually_checked"]:
                # image has been manually checked in json ...
                xml_path = return_xml_path(image_path)
                if os.path.isfile(xml_path):
                    # ... but not anymore in xml
                    if not verification_status(xml_path):
                        # set check flag in json
                        image["manually_checked"] = False
                        # reset confidence from 1.0 to arbitrary value
                        if "detections" in image:
                            for detection in image["detections"]:
                                detection["conf"] = 0.7

    # write json
    image_recognition_file_content.close()
    with open(recognition_file, "w") as json_file:
        json.dump(data, json_file, indent=1)
    image_recognition_file_content.close()
    patience_dialog.close()

    # finalise things if all images are verified
    if n_verified_files == total_n_files:
        if mb.askyesno(
            title=["Are you done?", "¿Ya terminaste?"][lang_idx],
            message=[
                "All images are verified and the 'image_recognition_file.json' is up-to-date.\n\nDo you want to close this "
                "verification session and proceed to the final step?",
                "Todas las imágenes están verificadas y "
                "'image_recognition_file.json' está actualizado.\n\n¿Quieres cerrar esta sesión de verificación"
                " y continuar con el paso final?",
            ][lang_idx],
        ):
            # close window
            hitl_progress_window.destroy()
            bind_scroll_to_deploy_canvas()

            # get plot from xml files
            fig = produce_graph(file_list_txt=file_list_txt)

            # init window
            hitl_final_window = customtkinter.CTkToplevel(root)
            hitl_final_window.title("Overview")
            hitl_final_window.geometry("+10+10")

            # add plot
            chart_type = FigureCanvasTkAgg(fig, hitl_final_window)
            chart_type.get_tk_widget().grid(row=0, column=0)

            # button frame
            hitl_final_actions_frame = LabelFrame(
                hitl_final_window,
                text=[
                    " Do you want to export these verified images as training data? ",
                    " ¿Quieres exportar estas imágenes verificadas como datos de entrenamiento? ",
                ][lang_idx],
                pady=2,
                padx=5,
                relief="solid",
                highlightthickness=5,
                font=100,
                fg=green_primary,
                labelanchor="n",
            )
            hitl_final_actions_frame.configure(font=(text_font, 15, "bold"))
            hitl_final_actions_frame.grid(column=0, row=3, columnspan=2, sticky="ew")
            hitl_final_actions_frame.columnconfigure(0, weight=1, minsize=115)
            hitl_final_actions_frame.columnconfigure(1, weight=1, minsize=115)

            # buttons
            btn_hitl_final_export_y = Button(
                master=hitl_final_actions_frame,
                text=[
                    "Yes - choose folder and create training data",
                    "Sí - elija la carpeta y crear datos de entrenamiento",
                ][lang_idx],
                width=1,
                command=lambda: [
                    uniquify_and_move_img_and_xml_from_filelist(
                        file_list_txt=file_list_txt,
                        recognition_file=recognition_file,
                        hitl_final_window=hitl_final_window,
                    ),
                    update_frame_states(),
                ],
            )
            btn_hitl_final_export_y.grid(
                row=0, column=0, rowspan=1, sticky="nesw", padx=5
            )

            btn_hitl_final_export_n = Button(
                master=hitl_final_actions_frame,
                text=[
                    "No - go back to the main AddaxAI window",
                    "No - regrese a la ventana principal de AddaxAI",
                ][lang_idx],
                width=1,
                command=lambda: [
                    delete_temp_folder(file_list_txt),
                    hitl_final_window.destroy(),
                    change_hitl_var_in_json(recognition_file, "done"),
                    update_frame_states(),
                ],
            )
            btn_hitl_final_export_n.grid(
                row=0, column=1, rowspan=1, sticky="nesw", padx=5
            )


# os dependent python executables
def get_python_interprator(env_name):
    if platform.system() == "Windows":
        return os.path.join(AddaxAI_files, "envs", f"env-{env_name}", "python.exe")
    else:
        return os.path.join(AddaxAI_files, "envs", f"env-{env_name}", "bin", "python")


# get the images and xmls from annotation session and store them with unique filename
def uniquify_and_move_img_and_xml_from_filelist(
    file_list_txt, recognition_file, hitl_final_window
):
    # log
    print(f"EXECUTED: {sys._getframe().f_code.co_name}({locals()})\n")

    # choose destination
    dst_dir = filedialog.askdirectory()

    # ask to move or copy
    window = TextButtonWindow(
        ["Method of file placement", "Método de colocación de archivos"][lang_idx],
        [
            f"Do you want to copy or move the images to\n'{dst_dir}'?",
            f"¿Quieres copiar o mover las imágenes a\n'{dst_dir}'?",
        ][lang_idx],
        [
            ["Move", "Mover"][lang_idx],
            ["Copy", "Copiar"][lang_idx],
            ["Cancel", "Cancelar"][lang_idx],
        ],
    )
    user_input = window.run()
    if user_input == "Cancel" or user_input == "Cancelar":
        return
    else:
        if user_input == "Move" or user_input == "Mover":
            copy_or_move = "Move"
        if user_input == "Copy" or user_input == "Copiar":
            copy_or_move = "Copy"

    # init vars
    src_dir = os.path.normpath(var_choose_folder.get())

    # loop through the images
    with open(file_list_txt) as f:
        # count total number of images without loading to memory
        n_imgs = 0
        for i in f:
            n_imgs += 1

        # reset file index
        f.seek(0)

        # open patience window
        patience_dialog = PatienceDialog(
            total=n_imgs, text=["Writing files...", "Escribir archivos..."][lang_idx]
        )
        patience_dialog.open()
        current = 1

        # loop
        for img in f:
            # get relative path
            img_rel_path = os.path.relpath(img.rstrip(), src_dir)

            # uniquify image
            src_img = os.path.join(src_dir, img_rel_path)
            dst_img = os.path.join(dst_dir, img_rel_path)
            Path(os.path.dirname(dst_img)).mkdir(parents=True, exist_ok=True)
            if copy_or_move == "Move":
                shutil.move(src_img, dst_img)
            elif copy_or_move == "Copy":
                shutil.copy2(src_img, dst_img)

            # uniquify annotation
            ann_rel_path = os.path.splitext(img_rel_path)[0] + ".xml"
            src_ann = return_xml_path(os.path.join(src_dir, img_rel_path))
            dst_ann = os.path.join(dst_dir, ann_rel_path)
            Path(os.path.dirname(dst_ann)).mkdir(parents=True, exist_ok=True)
            shutil.move(src_ann, dst_ann)

            # update dialog
            patience_dialog.update_progress(current)
            current += 1
        f.close()

    # finalize
    patience_dialog.close()
    delete_temp_folder(file_list_txt)
    hitl_final_window.destroy()
    change_hitl_var_in_json(recognition_file, "done")


# check if input can be converted to float
def is_valid_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


# get size of file in appropriate unit
def get_size(path):
    size = os.path.getsize(path)
    if size < 1024:
        return f"{size} bytes"
    elif size < pow(1024, 2):
        return f"{round(size / 1024, 2)} KB"
    elif size < pow(1024, 3):
        return f"{round(size / (pow(1024, 2)), 2)} MB"
    elif size < pow(1024, 4):
        return f"{round(size / (pow(1024, 3)), 2)} GB"


# check if the user is already in progress of verifying, otherwise start new session
def start_or_continue_hitl():
    # early exit if only video json
    selected_dir = var_choose_folder.get()
    path_to_image_json = os.path.join(selected_dir, "image_recognition_file.json")

    # warn user if the json file is very large
    json_size = os.path.getsize(path_to_image_json)
    if json_size > 500000:
        mb.showwarning(
            warning_txt[lang_idx],
            [
                f"The JSON file is very large ({get_size(path_to_image_json)}). This can cause the verification"
                " step to perform very slow. It will work, but you'll have to have patience. ",
                "El archivo "
                f"JSON es muy grande ({get_size(path_to_image_json)}). Esto puede hacer que el paso de verificación"
                " funcione muy lentamente. Funcionará, pero tendrás que tener paciencia. ",
            ][lang_idx],
        )

    # check requirements
    check_json_presence_and_warn_user(
        ["verify", "verificar"][lang_idx],
        ["verifying", "verificando"][lang_idx],
        ["verification", "verificación"][lang_idx],
    )
    if not os.path.isfile(path_to_image_json):
        return

    # check hitl status
    status = get_hitl_var_in_json(path_to_image_json)

    # start first session
    if status == "never-started":
        # open window to select criteria
        open_hitl_settings_window()

    # continue previous session
    elif status == "in-progress":
        # read selection criteria from last time
        annotation_arguments_pkl = os.path.join(
            selected_dir, "temp-folder", "annotation_information.pkl"
        )
        with open(annotation_arguments_pkl, "rb") as fp:
            annotation_arguments = pickle.load(fp)

        # update class_txt_file from json in case user added classes last time
        class_list_txt = annotation_arguments["class_list_txt"]
        label_map = fetch_label_map_from_json(
            os.path.join(var_choose_folder.get(), "image_recognition_file.json")
        )
        if os.path.isfile(class_list_txt):
            os.remove(class_list_txt)
        with open(class_list_txt, "a") as f:
            for k, v in label_map.items():
                f.write(f"{v}\n")
            f.close()

        # ask user
        if not mb.askyesno(
            ["Verification session in progress", "Sesión de verificación en curso"][
                lang_idx
            ],
            [
                "Do you want to continue with the previous verification session? If you press 'No', you will start a new session.",
                "¿Quieres continuar con la sesión de verificación anterior? Si presiona 'No', iniciará una nueva sesión.",
            ][lang_idx],
        ):
            delete_temp_folder(annotation_arguments["file_list_txt"])
            change_hitl_var_in_json(
                path_to_image_json, "never-started"
            )  # if user closes window, it can start fresh next time
            open_hitl_settings_window()

        # start human in the loop process and skip selection window
        else:
            try:
                open_annotation_windows(
                    recognition_file=annotation_arguments["recognition_file"],
                    class_list_txt=annotation_arguments["class_list_txt"],
                    file_list_txt=annotation_arguments["file_list_txt"],
                    label_map=annotation_arguments["label_map"],
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

    # start new session
    elif status == "done":
        if mb.askyesno(
            ["Previous session is done", "Sesión anterior terminada."][lang_idx],
            [
                "It seems like you have completed the previous manual "
                "verification session. Do you want to start a new session?",
                "Parece que has completado la sesión de verificación manual "
                "anterior. ¿Quieres iniciar una nueva sesión?",
            ][lang_idx],
        ):
            open_hitl_settings_window()


# open xml and check if the data is already in the json
def check_if_img_needs_converting(img_file):
    # open xml
    root = ET.parse(return_xml_path(img_file)).getroot()

    # read verification status
    try:
        verification_status = True if root.attrib["verified"] == "yes" else False
    except:
        verification_status = False

    # read json update status
    try:
        json_update_status = True if root.attrib["json_updated"] == "yes" else False
    except:
        json_update_status = False

    # return whether or not it needs converting to json
    if verification_status == True and json_update_status == False:
        return True
    else:
        return False


# converts individual xml to coco
def convert_xml_to_coco(xml_path, inverted_label_map):
    # open
    tree = ET.parse(xml_path)
    root = tree.getroot()
    try:
        verification_status = True if root.attrib["verified"] == "yes" else False
    except:
        verification_status = False
    path = root.findtext("path")
    size = root.find("size")
    im_width = int(size.findtext("width"))
    im_height = int(size.findtext("height"))

    # fetch objects
    verified_detections = []
    new_class = False
    for obj in root.findall("object"):
        name = obj.findtext("name")

        # check if new class
        if name not in inverted_label_map:
            new_class = True
            highest_index = 0
            for key, value in inverted_label_map.items():
                value = int(value)
                if value > highest_index:
                    highest_index = value
            inverted_label_map[name] = str(highest_index + 1)
        category = inverted_label_map[name]

        # read
        bndbox = obj.find("bndbox")
        xmin = int(float(bndbox.findtext("xmin")))
        ymin = int(float(bndbox.findtext("ymin")))
        xmax = int(float(bndbox.findtext("xmax")))
        ymax = int(float(bndbox.findtext("ymax")))

        # convert
        w_box = round(abs(xmax - xmin) / im_width, 5)
        h_box = round(abs(ymax - ymin) / im_height, 5)
        xo = round(xmin / im_width, 5)
        yo = round(ymin / im_height, 5)
        bbox = [xo, yo, w_box, h_box]

        # compile
        verified_detection = {"category": category, "conf": 1.0, "bbox": bbox}
        verified_detections.append(verified_detection)

    verified_image = {"file": path, "detections": verified_detections}

    # return
    return [verified_image, verification_status, new_class, inverted_label_map]
