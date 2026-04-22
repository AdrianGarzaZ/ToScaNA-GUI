from __future__ import annotations

from pathlib import Path

import panel as pn

from toscana_gui.numors.tasks import build_numors_summary_markdown
from toscana_gui.projects.tasks import WORKSPACE_TAB_TITLES
from toscana_gui.ui.theme import APP_TITLE, LOGO_PATH


def build_landing_page(shell) -> pn.Column:
    logo_pane = pn.pane.PNG(
        LOGO_PATH,
        width=280,
        sizing_mode="fixed",
        margin=(0, 0, 0, 0),
    )

    center_column = pn.Column(
        pn.Column(
            logo_pane,
            width=280,
            align="center",
            styles={"margin": "0 auto"},
        ),
        pn.Spacer(height=12),
        pn.pane.HTML(
            f"""
            <div style="text-align: center; width: 100%;">
              <h1 style="
                margin: 0;
                font-size: 2.4rem;
                letter-spacing: 0.03em;
                font-family: 'IBM Plex Sans', sans-serif;
              ">{APP_TITLE}</h1>
            </div>
            """,
            sizing_mode="stretch_width",
        ),
        pn.Spacer(height=8),
        pn.pane.Markdown(
            "Choose how you want to begin your ToScaNA session.",
            sizing_mode="stretch_width",
            styles={
                "text-align": "center",
                "font-family": "'IBM Plex Sans', sans-serif",
            },
        ),
        pn.Spacer(height=22),
        build_pending_navigation_prompt(shell),
        pn.Spacer(height=14),
        pn.Column(
            shell.start_project_button,
            shell.continue_project_button,
            shell.help_button,
            width=360,
            align="center",
            styles={"margin": "0 auto"},
        ),
        sizing_mode="stretch_width",
        styles={
            "max-width": "760px",
            "margin": "0 auto",
        },
    )
    return pn.Column(
        pn.Spacer(height=28),
        center_column,
        sizing_mode="stretch_both",
    )


def build_pending_navigation_prompt(shell) -> object:
    if shell.pending_navigation_action is None:
        return pn.Spacer(height=0)
    return pn.Card(
        pn.pane.Markdown(
            "You have unsaved changes in the currently loaded project. "
            "Choose how to proceed before switching projects.",
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.save_and_continue_button,
            shell.discard_and_continue_button,
            shell.cancel_navigation_button,
        ),
        title="Unsaved Changes",
        sizing_mode="stretch_width",
    )


def build_start_project_layout(shell) -> list[object]:
    if shell.workspace_result != "created" or shell.current_project_state is None:
        folder_widget = (
            shell.project_folder_input
            if shell.project_folder_mode.value == "Enter folder path"
            else pn.Column(
                shell.project_folder_selected_display,
                pn.Row(
                    shell.project_folder_browse_button,
                    shell.project_folder_native_browse_button,
                ),
                (
                    pn.Card(
                        shell.project_folder_file_selector,
                        pn.Row(
                            shell.project_folder_confirm_button,
                            shell.project_folder_cancel_button,
                        ),
                        title="Choose Project Folder",
                        sizing_mode="stretch_width",
                    )
                    if shell.project_folder_browser_visible
                    else pn.Spacer(height=0)
                ),
                sizing_mode="stretch_width",
            )
        )
        return [
            pn.pane.Alert(
                "Define the basic project information below. "
                "The target folder may be created if it does not exist yet. "
                "If it already exists, it must be empty.",
                alert_type="primary",
                sizing_mode="stretch_width",
            ),
            pn.Card(
                shell.project_name_input,
                shell.project_folder_mode,
                folder_widget,
                pn.Row(shell.create_project_confirm_button),
                shell.start_project_message,
                title="Start New Project",
                sizing_mode="stretch_width",
            ),
        ]

    return build_loaded_project_layout(shell)


def build_continue_project_layout(shell) -> list[object]:
    if shell.workspace_result == "opened" and shell.current_project_state is not None:
        return build_loaded_project_layout(shell)

    shell._refresh_recent_projects_view()
    manual_selected = bool(shell.manual_project_file_input.value.strip()) or bool(
        shell.manual_project_file_selected_display.value.strip()
    ) or shell.manual_project_file_browser_visible
    active_card_styles = {
        "border": "2px solid #0B6FA4",
        "box-shadow": "0 10px 26px rgba(0, 0, 0, 0.10)",
    }
    inactive_card_styles = {
        "border": "1px solid rgba(0, 0, 0, 0.08)",
    }
    manual_file_widget = (
        shell.manual_project_file_input
        if shell.manual_project_file_mode.value == "Enter file path"
        else pn.Column(
            shell.manual_project_file_selected_display,
            pn.Row(
                shell.manual_project_file_browse_button,
                shell.manual_project_file_native_browse_button,
            ),
            (
                pn.Card(
                    shell.manual_project_file_selector,
                    pn.Row(
                        shell.manual_project_file_confirm_button,
                        shell.manual_project_file_cancel_button,
                    ),
                    title="Choose Project File",
                    sizing_mode="stretch_width",
                )
                if shell.manual_project_file_browser_visible
                else pn.Spacer(height=0)
            ),
            sizing_mode="stretch_width",
        )
    )
    return [
        pn.pane.Alert(
            "Continue a previous session by choosing a recent project or opening "
            "an `ntsa-project.json` file directly.",
            alert_type="primary",
            sizing_mode="stretch_width",
        ),
        pn.FlexBox(
            pn.Card(
                shell.recent_projects_column,
                title="Recent Projects",
                sizing_mode="stretch_width",
                min_width=420,
                styles={
                    "flex": "1 1 520px",
                    **(inactive_card_styles if manual_selected else active_card_styles),
                },
            ),
            pn.Card(
                shell.manual_project_file_mode,
                manual_file_widget,
                pn.Row(shell.manual_open_button),
                shell.continue_project_message,
                title="Open Project File",
                sizing_mode="stretch_width",
                min_width=420,
                styles={
                    "flex": "1 1 520px",
                    **(active_card_styles if manual_selected else inactive_card_styles),
                },
            ),
            gap="18px",
            flex_wrap="wrap",
            sizing_mode="stretch_width",
        ),
    ]


def build_loaded_project_layout(shell) -> list[object]:
    contents: list[object] = [build_workspace_navigation(shell)]
    warning = build_static_plot_warning(shell)
    if warning is not None:
        contents.append(warning)
    if shell.workspace_message.visible:
        contents.append(shell.workspace_message)
    contents.append(build_workspace_section_content(shell, shell.current_top_level_tab))
    return contents


def build_static_plot_warning(shell) -> pn.pane.Alert | None:
    if (
        shell.current_project_state is None
        or not shell.current_project_state.resume.has_static_plot_warning
        or not shell.current_project_state.resume.static_plot_warning
    ):
        return None
    return pn.pane.Alert(
        shell.current_project_state.resume.static_plot_warning,
        alert_type="warning",
        sizing_mode="stretch_width",
    )


def build_workspace_navigation(shell) -> pn.FlexBox:
    return pn.FlexBox(
        shell.back_to_menu_button,
        *[shell.workspace_buttons[tab_name] for tab_name in shell.workspace_buttons],
        gap="10px",
        flex_wrap="wrap",
        sizing_mode="stretch_width",
    )


def build_workspace_section_content(shell, tab_name: str) -> object:
    if tab_name == "project":
        return build_project_section(shell)
    if tab_name == "numors":
        return build_numors_section(shell)
    if tab_name in {"background", "normalization", "self", "ft", "bft"}:
        return build_placeholder_section(tab_name)
    if tab_name == "run_history":
        return build_run_history_section(shell)
    return build_help_section()


def build_project_section(shell) -> pn.Column:
    return pn.Column(
        pn.Card(
            pn.pane.Markdown(
                "\n".join(
                    [
                        f"**Project name:** {shell.current_project_state.project.name}",
                        f"**Project folder:** `{shell.current_project_root}`",
                        f"**Project file:** `{shell.current_project_file}`",
                        f"**Restored top-level tab:** `{shell.current_top_level_tab}`",
                    ]
                ),
                sizing_mode="stretch_width",
            ),
            title="Project Summary",
            sizing_mode="stretch_width",
        ),
        pn.Card(
            shell.project_editor_name_input,
            pn.Row(shell.save_project_button),
            shell.project_editor_message,
            title="Project Editor",
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    )


def build_numors_section(shell) -> pn.Column:
    numors_state = shell._get_numors_state()
    validation_state = numors_state["validation"]
    source_widget = (
        shell.numors_file_selector
        if shell.numors_source_mode.value == "File Explorer"
        else shell.numors_manual_path_input
    )
    contents: list[object] = [
        pn.Card(
            shell.numors_source_mode,
            source_widget,
            pn.Row(shell.numors_validate_button, shell.numors_run_button),
            shell.numors_message,
            title="Numors Input",
            sizing_mode="stretch_width",
        )
    ]

    if shell.numors_import_prompt.visible:
        contents.append(
            pn.Card(
                shell.numors_import_prompt,
                pn.Row(
                    shell.numors_import_confirm_button,
                    shell.numors_import_cancel_button,
                ),
                title="Import Required",
                sizing_mode="stretch_width",
            )
        )

    if shell.numors_plot_warning.visible:
        contents.append(shell.numors_plot_warning)

    if validation_state.get("selected_par_path"):
        contents.append(
            pn.Card(
                pn.pane.Markdown(
                    build_numors_summary_markdown(validation_state),
                    sizing_mode="stretch_width",
                ),
                title="Validation Summary",
                sizing_mode="stretch_width",
            )
        )

    contents.append(build_latest_numors_outputs(shell))

    return pn.Column(
        *contents,
        sizing_mode="stretch_width",
    )


def _read_tail_text(path: str | None, *, max_bytes: int = 20_000) -> str:
    if not path:
        return "No file recorded."
    try:
        file_path = Path(path)
        if not file_path.exists():
            return f"File not found: {file_path}"
        with file_path.open("rb") as handle:
            try:
                handle.seek(-max_bytes, 2)
                truncated = True
            except OSError:
                handle.seek(0)
                truncated = False
            payload = handle.read()
        text = payload.decode("utf-8", errors="replace")
        if truncated:
            return f"... (showing last {max_bytes} bytes)\n\n{text}"
        return text
    except Exception as exc:
        return f"Could not read file: {exc}"


def build_latest_numors_outputs(shell) -> object:
    if shell.current_project_state is None:
        return pn.Spacer(height=0)

    latest_record = next(
        (record for record in reversed(shell.current_project_state.runs) if record.workflow == "numors"),
        None,
    )
    if latest_record is None:
        return pn.Spacer(height=0)

    if latest_record.status == "running":
        return pn.Card(
            pn.pane.Markdown(
                f"Latest run `{latest_record.run_id}` is still running. Outputs will appear once it finishes.",
                sizing_mode="stretch_width",
            ),
            title="Latest Run Outputs",
            sizing_mode="stretch_width",
        )

    summary_lines = [
        f"**Run ID:** `{latest_record.run_id}`",
        f"**Status:** `{latest_record.status}`",
    ]
    if latest_record.started_at:
        summary_lines.append(f"**Started:** {latest_record.started_at}")
    if latest_record.finished_at:
        summary_lines.append(f"**Finished:** {latest_record.finished_at}")
    if latest_record.summary:
        summary_lines.append(f"**Summary:** {latest_record.summary}")
    if latest_record.error:
        summary_lines.append(f"**Error:** {latest_record.error}")

    output_lines: list[str] = []
    output_paths = latest_record.output_paths
    if output_paths.stdout_file:
        output_lines.append(f"**stdout:** `{output_paths.stdout_file}`")
    if output_paths.logfile:
        output_lines.append(f"**logfile:** `{output_paths.logfile}`")
    if output_paths.generated_files:
        output_lines.append(f"**Generated files:** `{len(output_paths.generated_files)}`")
        output_lines.extend(
            f"**output:** `{generated_file}`" for generated_file in output_paths.generated_files
        )
    else:
        if output_paths.reg_file:
            output_lines.append(f"**reg:** `{output_paths.reg_file}`")
        if output_paths.adat_file:
            output_lines.append(f"**adat:** `{output_paths.adat_file}`")
        if output_paths.qdat_file:
            output_lines.append(f"**qdat:** `{output_paths.qdat_file}`")

    stdout_tail = _read_tail_text(output_paths.stdout_file)
    logfile_tail = _read_tail_text(output_paths.logfile)

    shell._refresh_numors_run_blocks_view(latest_record)
    run_blocks_panel: object = (
        shell.numors_run_blocks_card if shell.numors_run_blocks_card.visible else pn.Spacer(height=0)
    )

    plots_dir = None
    plot_panes: list[object] = []
    plot_note = ""
    if shell.current_project_root is not None:
        plots_dir = Path(shell.current_project_root) / "processed" / "logfiles" / "plots" / latest_record.run_id
        if plots_dir.exists():
            png_paths = sorted(plots_dir.glob("*.png"))
            for png_path in png_paths[:12]:
                plot_panes.append(
                    pn.pane.PNG(
                        str(png_path),
                        width=360,
                        height=240,
                        sizing_mode="fixed",
                    )
                )
            if png_paths and len(png_paths) > 12:
                plot_note = f"Showing first 12 of {len(png_paths)} plots in `{plots_dir}`."
            elif not png_paths:
                plot_note = f"No plots found in `{plots_dir}`."
        else:
            plot_note = f"No plots folder found for `{latest_record.run_id}`."

    plots_section = pn.Column(
        pn.pane.Markdown(plot_note, sizing_mode="stretch_width") if plot_note else pn.Spacer(height=0),
        pn.FlexBox(*plot_panes, sizing_mode="stretch_width") if plot_panes else pn.Spacer(height=0),
        sizing_mode="stretch_width",
    )

    accordion = pn.Accordion(
        ("stdout (tail)", pn.widgets.TextAreaInput(value=stdout_tail, disabled=True, height=260, sizing_mode="stretch_width")),
        ("logfile (tail)", pn.widgets.TextAreaInput(value=logfile_tail, disabled=True, height=260, sizing_mode="stretch_width")),
        ("plots", plots_section),
        sizing_mode="stretch_width",
    )

    return pn.Card(
        pn.pane.Markdown("\n".join(summary_lines), sizing_mode="stretch_width"),
        pn.pane.Markdown("\n".join(output_lines), sizing_mode="stretch_width") if output_lines else pn.Spacer(height=0),
        run_blocks_panel,
        accordion,
        title="Latest Run Outputs",
        sizing_mode="stretch_width",
    )


def build_placeholder_section(tab_name: str) -> pn.Column:
    return pn.Column(
        pn.pane.Markdown(
            f"{WORKSPACE_TAB_TITLES[tab_name]} content will be added in a later slice.",
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    )


def build_run_history_section(shell) -> pn.Column:
    if shell.current_project_state is None or not shell.current_project_state.runs:
        return pn.Column(
            pn.pane.Markdown("No recorded runs yet.", sizing_mode="stretch_width"),
            sizing_mode="stretch_width",
        )

    cards: list[object] = []
    for record in shell.current_project_state.runs:
        lines = [
            f"**Run ID:** {record.run_id}",
            f"**Workflow:** {record.workflow}",
            f"**Status:** {record.status}",
            f"**Started:** {record.started_at}",
        ]
        if record.finished_at:
            lines.append(f"**Finished:** {record.finished_at}")
        if record.summary:
            lines.append(f"**Summary:** {record.summary}")
        if record.error:
            lines.append(f"**Error:** {record.error}")
        if record.output_paths.stdout_file:
            lines.append(f"**stdout:** `{record.output_paths.stdout_file}`")
        if record.output_paths.logfile:
            lines.append(f"**logfile:** `{record.output_paths.logfile}`")
        if record.output_paths.generated_files:
            lines.append(f"**Generated files:** `{len(record.output_paths.generated_files)}`")
            lines.extend(
                f"**output:** `{generated_file}`"
                for generated_file in record.output_paths.generated_files
            )
        else:
            if record.output_paths.reg_file:
                lines.append(f"**reg:** `{record.output_paths.reg_file}`")
            if record.output_paths.adat_file:
                lines.append(f"**adat:** `{record.output_paths.adat_file}`")
            if record.output_paths.qdat_file:
                lines.append(f"**qdat:** `{record.output_paths.qdat_file}`")

        extra_sections: list[object] = []
        workflow_data = getattr(record, "workflow_data", None)
        run_blocks = workflow_data.get("run_blocks") if isinstance(workflow_data, dict) else None
        if record.workflow == "numors" and isinstance(run_blocks, list) and run_blocks:
            succeeded_blocks = 0
            failed_blocks = 0
            block_lines: list[str] = []
            for idx, block in enumerate(run_blocks, start=1):
                if not isinstance(block, dict):
                    continue
                status = str(block.get("status") or "unknown")
                if status == "succeeded":
                    succeeded_blocks += 1
                elif status == "failed":
                    failed_blocks += 1

                label = str(block.get("label") or f"Block {idx}")
                file_base = block.get("file_base")
                num_range = block.get("num")
                adat_file = block.get("adat_file")
                qdat_file = block.get("qdat_file")
                plot_files = block.get("plot_files", [])
                plot_count = len(plot_files) if isinstance(plot_files, list) else 0

                parts = [f"[{idx}] `{status}` — {label}"]
                if file_base:
                    parts.append(f"out=`{file_base}`")
                if num_range:
                    parts.append(f"num=`{num_range}`")
                parts.append("adat=missing" if not adat_file else f"adat=`{adat_file}`")
                parts.append("qdat=missing" if not qdat_file else f"qdat=`{qdat_file}`")
                parts.append(f"plots=`{plot_count}`")
                block_lines.append("- " + ", ".join(parts))

            lines.append(
                f"**Run blocks:** `{len(run_blocks)}` (succeeded: `{succeeded_blocks}`, failed: `{failed_blocks}`)"
            )

            viewer_state = {"block_index": 0, "plot_index": 0}
            details_pane = pn.pane.Markdown("", sizing_mode="stretch_width")
            plot_container = pn.Column(sizing_mode="stretch_width")

            prev_block = pn.widgets.Button(name="◀ Prev Block", button_type="light", width=140)
            next_block = pn.widgets.Button(name="Next Block ▶", button_type="light", width=140)
            prev_plot = pn.widgets.Button(name="◀ Prev Plot", button_type="light", width=140)
            next_plot = pn.widgets.Button(name="Next Plot ▶", button_type="light", width=140)

            block_select = pn.widgets.Select(
                name="Block",
                options={
                    f"{idx}: {str(block.get('label') or f'Block {idx}')}": idx - 1
                    for idx, block in enumerate(run_blocks, start=1)
                    if isinstance(block, dict)
                },
                value=0,
                sizing_mode="stretch_width",
            )

            def _clamp_state() -> None:
                viewer_state["block_index"] = max(0, min(viewer_state["block_index"], len(run_blocks) - 1))
                block = run_blocks[viewer_state["block_index"]] if isinstance(run_blocks[viewer_state["block_index"]], dict) else {}
                plots = block.get("plot_files", [])
                plots = plots if isinstance(plots, list) else []
                max_plot = max(len(plots) - 1, 0)
                viewer_state["plot_index"] = max(0, min(viewer_state["plot_index"], max_plot))

            def _render_viewer() -> None:
                _clamp_state()
                block = run_blocks[viewer_state["block_index"]] if isinstance(run_blocks[viewer_state["block_index"]], dict) else {}
                label = str(block.get("label") or f"Block {viewer_state['block_index'] + 1}")
                status = str(block.get("status") or "unknown")
                file_base = block.get("file_base")
                num_range = block.get("num")
                adat_file = block.get("adat_file")
                qdat_file = block.get("qdat_file")
                plots = block.get("plot_files", [])
                plots = list(plots) if isinstance(plots, list) else []

                details_lines = [
                    f"**Block:** `{viewer_state['block_index'] + 1}` / `{len(run_blocks)}`",
                    f"**Title:** {label}",
                    f"**Status:** `{status}`",
                ]
                if file_base:
                    details_lines.append(f"**out:** `{file_base}`")
                if num_range:
                    details_lines.append(f"**num:** `{num_range}`")
                details_lines.append(f"**adat:** `{adat_file}`" if adat_file else "**adat:** missing")
                details_lines.append(f"**qdat:** `{qdat_file}`" if qdat_file else "**qdat:** missing")
                details_lines.append(f"**plots:** `{len(plots)}`")
                details_pane.object = "\n".join(details_lines)

                prev_block.disabled = viewer_state["block_index"] <= 0
                next_block.disabled = viewer_state["block_index"] >= len(run_blocks) - 1
                prev_plot.disabled = not plots or viewer_state["plot_index"] <= 0
                next_plot.disabled = not plots or viewer_state["plot_index"] >= len(plots) - 1

                plot_container.clear()
                if plots:
                    current_plot = plots[viewer_state["plot_index"]]
                    plot_container.append(
                        pn.pane.Markdown(
                            f"Plot `{viewer_state['plot_index'] + 1}` / `{len(plots)}`",
                            sizing_mode="stretch_width",
                        )
                    )
                    if Path(str(current_plot)).exists():
                        plot_container.append(
                            pn.pane.PNG(
                                current_plot,
                                width=720,
                                height=480,
                                sizing_mode="fixed",
                            )
                        )
                    else:
                        plot_container.append(
                            pn.pane.Markdown(
                                f"Plot file not found: `{current_plot}`",
                                sizing_mode="stretch_width",
                            )
                        )
                else:
                    plot_container.append(
                        pn.pane.Markdown(
                            "No per-block plots recorded for this run.",
                            sizing_mode="stretch_width",
                        )
                    )

            def _set_block_index(value: int) -> None:
                viewer_state["block_index"] = value
                viewer_state["plot_index"] = 0
                _render_viewer()

            def _on_prev_block(_event=None) -> None:
                _set_block_index(viewer_state["block_index"] - 1)

            def _on_next_block(_event=None) -> None:
                _set_block_index(viewer_state["block_index"] + 1)

            def _on_prev_plot(_event=None) -> None:
                viewer_state["plot_index"] = max(0, viewer_state["plot_index"] - 1)
                _render_viewer()

            def _on_next_plot(_event=None) -> None:
                viewer_state["plot_index"] = viewer_state["plot_index"] + 1
                _render_viewer()

            def _on_block_select(event) -> None:
                if event.new is None:
                    return
                try:
                    _set_block_index(int(event.new))
                except (TypeError, ValueError):
                    return

            prev_block.on_click(_on_prev_block)
            next_block.on_click(_on_next_block)
            prev_plot.on_click(_on_prev_plot)
            next_plot.on_click(_on_next_plot)
            block_select.param.watch(_on_block_select, "value")
            _render_viewer()

            viewer = pn.Column(
                block_select,
                pn.Row(prev_block, next_block, sizing_mode="stretch_width"),
                details_pane,
                pn.Row(prev_plot, next_plot, sizing_mode="stretch_width"),
                plot_container,
                sizing_mode="stretch_width",
            )

            accordion = pn.Accordion(
                ("run blocks", pn.pane.Markdown("\n".join(block_lines), sizing_mode="stretch_width")),
                ("viewer", viewer),
                active=[],
                sizing_mode="stretch_width",
            )
            extra_sections.append(accordion)

        cards.append(
            pn.Card(
                pn.pane.Markdown("\n".join(lines), sizing_mode="stretch_width"),
                *extra_sections,
                title=f"Run {record.run_id}",
                sizing_mode="stretch_width",
            )
        )
    return pn.Column(*cards, sizing_mode="stretch_width")


def build_help_section() -> pn.Column:
    return pn.Column(
        pn.pane.Markdown(
            "Help and About content will be added in a later slice.",
            sizing_mode="stretch_width",
        ),
        sizing_mode="stretch_width",
    )


def build_workspace_placeholder_layout() -> list[object]:
    return [
        pn.pane.Alert(
            "This workspace shell is intentionally minimal. "
            "Project loading flows will be implemented in later slices.",
            alert_type="primary",
            sizing_mode="stretch_width",
        ),
        pn.Row(
            pn.Card(
                pn.pane.Markdown("Project area placeholder"),
                title="Project",
                sizing_mode="stretch_width",
            ),
            pn.Card(
                pn.pane.Markdown("Workflow area placeholder"),
                title="Workspace Content",
                sizing_mode="stretch_width",
            ),
        ),
    ]


def build_workspace_page(shell) -> pn.Column:
    return pn.Column(
        *[
            pn.pane.Markdown(
                "# Workspace",
                sizing_mode="stretch_width",
            ),
            pn.pane.Markdown(
                f"**Entered from:** {shell.workspace_entrypoint}",
                sizing_mode="stretch_width",
            ),
        ],
        *(
            build_start_project_layout(shell)
            if shell.workspace_entrypoint == "Start New Project"
            else (
                build_continue_project_layout(shell)
                if shell.workspace_entrypoint == "Continue Previous Project"
                else build_workspace_placeholder_layout()
            )
        ),
        sizing_mode="stretch_both",
    )


def _latest_run_summary(shell) -> str:
    if shell.current_project_state is None or not shell.current_project_state.runs:
        return "No saved outputs or logs are associated with this project yet."

    latest_run = shell.current_project_state.runs[-1]
    output_paths = latest_run.output_paths
    lines = [
        f"Latest recorded run: `{latest_run.run_id}`",
        f"Status: `{latest_run.status}`",
    ]
    if output_paths.stdout_file:
        lines.append(f"stdout: `{output_paths.stdout_file}`")
    if output_paths.logfile:
        lines.append(f"logfile: `{output_paths.logfile}`")
    if output_paths.generated_files:
        lines.append(f"generated files: `{len(output_paths.generated_files)}`")
    else:
        if output_paths.reg_file:
            lines.append(f"reg: `{output_paths.reg_file}`")
        if output_paths.adat_file:
            lines.append(f"adat: `{output_paths.adat_file}`")
        if output_paths.qdat_file:
            lines.append(f"qdat: `{output_paths.qdat_file}`")
    return "\n".join(lines)
