from __future__ import annotations

from pathlib import Path

import panel as pn

from toscana_gui.background.tasks import BACKGROUND_SOURCE_OPTIONS
from toscana_gui.background.tasks import BACKGROUND_SUBTRACTION_METHOD_OPTIONS
from toscana_gui.numors.tasks import NUMORS_SOURCE_OPTIONS
from toscana_gui.paths import REPO_ROOT
from toscana_gui.projects.tasks import WorkspaceTab


def initialize_shell_widgets(shell) -> None:
    shell.content = pn.Column(sizing_mode="stretch_both")
    shell.toast_duration_ms = 8000
    shell.reset_project_button = pn.widgets.Button(
        name="🗑",
        button_type="light",
        width=48,
        height=44,
    )
    shell.reset_project_prompt = pn.pane.Alert(
        "",
        alert_type="danger",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.reset_project_confirm_button = pn.widgets.Button(
        name="Yes, reset project",
        button_type="danger",
        sizing_mode="fixed",
        width=200,
        height=44,
    )
    shell.reset_project_cancel_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        sizing_mode="fixed",
        width=120,
        height=44,
    )

    shell.start_project_button = pn.widgets.Button(
        name="Start New Project",
        button_type="primary",
        sizing_mode="fixed",
        width=360,
        height=60,
    )
    shell.continue_project_button = pn.widgets.Button(
        name="Continue Previous Project",
        button_type="default",
        sizing_mode="fixed",
        width=360,
        height=60,
    )
    shell.help_button = pn.widgets.Button(
        name="Help (Coming soon)",
        button_type="light",
        disabled=True,
        sizing_mode="fixed",
        width=360,
        height=60,
    )
    shell.back_to_menu_button = pn.widgets.Button(
        name="Back to Main Menu",
        button_type="default",
        sizing_mode="fixed",
        width=180,
    )
    shell.workspace_buttons: dict[WorkspaceTab, pn.widgets.Button] = {
        tab_name: pn.widgets.Button(
            name=title,
            button_type="light",
            sizing_mode="fixed",
            width=150,
        )
        for tab_name, title in (
            ("project", "Project"),
            ("numors", "Numors"),
            ("background", "Background"),
            ("normalization", "Normalization"),
            ("self", "Self"),
            ("ft", "FT"),
            ("bft", "BFT"),
            ("run_history", "Run History"),
            ("help", "Help / About"),
        )
    }
    shell.project_name_input = pn.widgets.TextInput(
        name="Project Name",
        placeholder="My D4 Session",
        sizing_mode="stretch_width",
    )
    projects_root = REPO_ROOT / "Projects"
    shell.project_folder_input = pn.widgets.TextInput(
        name="Project Folder",
        placeholder=str(projects_root / "My-D4-Session"),
        sizing_mode="stretch_width",
    )
    shell.project_folder_input.value = str(projects_root)
    shell._project_folder_autofill_enabled = True
    shell._project_folder_autofill_programmatic = False
    shell._project_folder_autofill_last_value = str(projects_root)
    shell.project_folder_mode = pn.widgets.RadioBoxGroup(
        name="Project Folder Input",
        options=["Enter folder path", "Choose folder"],
        value="Enter folder path",
        inline=True,
        sizing_mode="stretch_width",
    )
    shell.project_folder_browser_visible = False
    shell._project_folder_candidate: Path | None = None
    shell.project_folder_selected_display = pn.widgets.TextInput(
        name="Selected Folder",
        placeholder="No folder selected yet.",
        disabled=True,
        sizing_mode="stretch_width",
    )
    shell.project_folder_browse_button = pn.widgets.Button(
        name="Choose Folder...",
        button_type="primary",
        sizing_mode="fixed",
        width=200,
        height=44,
        disabled=False,
    )
    shell.project_folder_native_browse_button = pn.widgets.Button(
        name="Choose Folder (Windows)...",
        button_type="light",
        sizing_mode="fixed",
        width=240,
        height=44,
    )
    shell.project_folder_confirm_button = pn.widgets.Button(
        name="Use Selected Folder",
        button_type="primary",
        sizing_mode="fixed",
        width=220,
        height=44,
        disabled=True,
    )
    shell.project_folder_cancel_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        sizing_mode="fixed",
        width=120,
        height=44,
    )
    shell.project_folder_file_selector = pn.widgets.FileSelector(
        directory=str(shell._default_project_folder_browser_root()),
        only_files=False,
        size=8,
        sizing_mode="stretch_width",
    )
    shell.create_project_confirm_button = pn.widgets.Button(
        name="Create Project",
        button_type="primary",
        sizing_mode="fixed",
        width=220,
        height=52,
    )
    shell.start_project_message = pn.pane.Alert(
        "Provide a project name and a target folder.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.project_editor_name_input = pn.widgets.TextInput(
        name="Project Name",
        sizing_mode="stretch_width",
    )
    shell.save_project_button = pn.widgets.Button(
        name="Save Project",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=48,
    )
    shell.project_editor_message = pn.pane.Alert(
        "No unsaved changes.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.manual_project_file_input = pn.widgets.TextInput(
        name="Project File",
        placeholder=r"D:\ILL\ToScaNA\Projects\my-session\ntsa-project.json",
        sizing_mode="stretch_width",
    )
    shell.manual_project_file_mode = pn.widgets.RadioBoxGroup(
        name="Open Project Input",
        options=["Enter file path", "Choose file"],
        value="Enter file path",
        inline=True,
        sizing_mode="stretch_width",
    )
    shell.manual_project_file_browser_visible = False
    shell._manual_project_file_candidate: Path | None = None
    shell.manual_project_file_selected_display = pn.widgets.TextInput(
        name="Selected File",
        placeholder="No file selected yet.",
        disabled=True,
        sizing_mode="stretch_width",
    )
    shell.manual_project_file_browse_button = pn.widgets.Button(
        name="Choose File...",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=44,
    )
    shell.manual_project_file_native_browse_button = pn.widgets.Button(
        name="Choose File (Windows)...",
        button_type="light",
        sizing_mode="fixed",
        width=220,
        height=44,
    )
    shell.manual_project_file_confirm_button = pn.widgets.Button(
        name="Use Selected File",
        button_type="primary",
        sizing_mode="fixed",
        width=200,
        height=44,
        disabled=True,
    )
    shell.manual_project_file_cancel_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        sizing_mode="fixed",
        width=120,
        height=44,
    )
    shell.manual_project_file_selector = pn.widgets.FileSelector(
        directory=str(REPO_ROOT),
        file_pattern="ntsa-project.json",
        only_files=True,
        size=8,
        sizing_mode="stretch_width",
    )
    shell.manual_open_button = pn.widgets.Button(
        name="Open Project File",
        button_type="primary",
        sizing_mode="fixed",
        width=220,
        height=52,
    )
    shell.continue_project_message = pn.pane.Alert(
        "Choose a recent project or open an `ntsa-project.json` file manually.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.workspace_message = pn.pane.Alert(
        "",
        alert_type="warning",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.numors_source_mode = pn.widgets.RadioBoxGroup(
        name="Input Mode",
        inline=False,
        options=list(NUMORS_SOURCE_OPTIONS),
        value=NUMORS_SOURCE_OPTIONS[0],
        sizing_mode="stretch_width",
    )
    shell.numors_par_dropdown = pn.widgets.Select(
        name="Numors `.par`",
        options={"Open a project first.": ""},
        value="",
        sizing_mode="stretch_width",
    )
    shell.numors_manual_path_input = pn.widgets.TextInput(
        name="File Path",
        placeholder=r"D:\ILL\ToScaNA\Project\processed\parfiles\do_name.par",
        sizing_mode="stretch_width",
    )
    shell.numors_validate_button = pn.widgets.Button(
        name="Validate File",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=48,
    )
    shell.numors_run_button = pn.widgets.Button(
        name="Run d4creg",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=48,
        disabled=True,
    )
    shell.numors_block_select = pn.widgets.Select(
        name="Block",
        options={},
        sizing_mode="stretch_width",
    )
    shell.numors_prev_block_button = pn.widgets.Button(
        name="Prev Block",
        icon="chevron-left",
        button_type="light",
        sizing_mode="fixed",
        width=140,
        height=40,
    )
    shell.numors_next_block_button = pn.widgets.Button(
        name="Next Block",
        icon="chevron-right",
        button_type="light",
        sizing_mode="fixed",
        width=140,
        height=40,
    )
    shell.numors_prev_plot_button = pn.widgets.Button(
        name="Prev Plot",
        icon="chevron-left",
        button_type="light",
        sizing_mode="fixed",
        width=140,
        height=40,
    )
    shell.numors_next_plot_button = pn.widgets.Button(
        name="Next Plot",
        icon="chevron-right",
        button_type="light",
        sizing_mode="fixed",
        width=140,
        height=40,
    )
    shell.numors_run_blocks_run_id = pn.pane.Markdown("", sizing_mode="stretch_width")
    shell.numors_block_header = pn.pane.Markdown("", sizing_mode="stretch_width")
    shell.numors_block_info_hover = pn.pane.HTML(
        "",
        sizing_mode="fixed",
        width=40,
        margin=(0, 0, 0, 0),
        styles={"overflow": "visible"},
    )
    shell.numors_block_details = pn.pane.Markdown("", sizing_mode="stretch_width")
    shell.numors_block_plot_counter = pn.pane.Markdown("", sizing_mode="stretch_width")
    shell.numors_block_plot_container = pn.Column(sizing_mode="stretch_width")
    shell.numors_run_blocks_card = pn.Card(
        shell.numors_run_blocks_run_id,
        shell.numors_block_select,
        pn.Row(
            shell.numors_prev_block_button,
            shell.numors_next_block_button,
            shell.numors_block_header,
            pn.Spacer(),
            shell.numors_block_info_hover,
            sizing_mode="stretch_width",
        ),
        shell.numors_block_details,
        pn.Row(
            shell.numors_prev_plot_button,
            shell.numors_next_plot_button,
            shell.numors_block_plot_counter,
            sizing_mode="stretch_width",
        ),
        shell.numors_block_plot_container,
        title="Run Blocks",
        sizing_mode="stretch_width",
        visible=False,
        css_classes=["toscana-overflow-visible"],
    )
    shell.numors_message = pn.pane.Alert(
        "Choose a `.par` file and validate it.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.numors_import_prompt = pn.pane.Alert(
        "",
        alert_type="warning",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.numors_import_confirm_button = pn.widgets.Button(
        name="Copy Into Project",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=44,
    )
    shell.numors_import_cancel_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        sizing_mode="fixed",
        width=120,
        height=44,
    )

    shell.background_source_mode = pn.widgets.RadioBoxGroup(
        name="Input Mode",
        inline=False,
        options=list(BACKGROUND_SOURCE_OPTIONS),
        value=BACKGROUND_SOURCE_OPTIONS[0],
        sizing_mode="stretch_width",
    )
    shell.background_par_dropdown = pn.widgets.Select(
        name="Sample `.par`",
        options={"Open a project first.": ""},
        value="",
        sizing_mode="stretch_width",
    )
    shell.background_manual_path_input = pn.widgets.TextInput(
        name="File Path",
        placeholder=r"D:\ILL\ToScaNA\Project\processed\parfiles\sample.par",
        sizing_mode="stretch_width",
    )
    shell.background_source_stack = pn.Column(
        shell.background_par_dropdown,
        shell.background_manual_path_input,
        sizing_mode="stretch_width",
    )
    shell.background_validate_button = pn.widgets.Button(
        name="Validate File",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=48,
    )
    shell.background_extract_button = pn.widgets.Button(
        name="Extract Sample Data",
        button_type="primary",
        sizing_mode="fixed",
        width=220,
        height=48,
        disabled=True,
    )
    shell.background_message = pn.pane.Alert(
        "Select a sample `.par` file to get started.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.background_error_bars_toggle = pn.widgets.Checkbox(
        name="Show error bars",
        value=False,
    )
    shell.background_raw_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_subtraction_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_no_data_pane = pn.pane.Markdown(
        "No extracted sample data yet. Run **Extract Sample Data** to generate interactive plots.",
        sizing_mode="stretch_width",
        visible=True,
    )
    shell.background_plot_options_card = pn.Card(
        pn.Row(shell.background_error_bars_toggle, sizing_mode="stretch_width"),
        title="Plot Options",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_raw_plot_alert = pn.pane.Alert(
        "",
        alert_type="danger",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_raw_plot_card = pn.Card(
        shell.background_raw_plot_pane,
        title="Raw data",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_subtraction_plot_alert = pn.pane.Alert(
        "",
        alert_type="danger",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_subtraction_plot_card = pn.Card(
        shell.background_subtraction_plot_pane,
        title="Direct Sample Subtraction (Sample - Container)",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_import_prompt = pn.pane.Alert(
        "",
        alert_type="warning",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_import_confirm_button = pn.widgets.Button(
        name="Copy into Project",
        button_type="primary",
        sizing_mode="fixed",
        width=200,
        height=44,
        disabled=False,
    )
    shell.background_import_cancel_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        sizing_mode="fixed",
        width=120,
        height=44,
    )
    shell.background_import_card = pn.Card(
        shell.background_import_prompt,
        pn.Row(
            shell.background_import_confirm_button,
            shell.background_import_cancel_button,
        ),
        title="Import Required",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_subtraction_method = pn.widgets.RadioButtonGroup(
        name="Method",
        options=list(BACKGROUND_SUBTRACTION_METHOD_OPTIONS),
        value=BACKGROUND_SUBTRACTION_METHOD_OPTIONS[0],
        button_type="primary",
        sizing_mode="stretch_width",
    )
    shell.background_linear_t_start = pn.widgets.FloatInput(
        name="t start",
        value=-1.0,
        step=0.05,
        sizing_mode="stretch_width",
    )
    shell.background_linear_t_stop = pn.widgets.FloatInput(
        name="t stop",
        value=2.0,
        step=0.05,
        sizing_mode="stretch_width",
    )
    shell.background_linear_t_step = pn.widgets.FloatInput(
        name="t step",
        value=0.05,
        step=0.01,
        start=1e-6,
        sizing_mode="stretch_width",
    )
    shell.background_linear_smoothing = pn.widgets.FloatInput(
        name="Smoothing factor",
        value=0.01,
        step=0.005,
        start=0.0,
        end=1.0,
        sizing_mode="stretch_width",
    )
    shell.background_linear_ignore_points = pn.widgets.IntInput(
        name="Ignore first N points",
        value=25,
        step=1,
        start=0,
        sizing_mode="stretch_width",
    )
    shell.background_linear_t_mode = pn.widgets.RadioButtonGroup(
        name="t selection",
        options=["Use computed t", "Use custom t"],
        value="Use computed t",
        button_type="default",
        sizing_mode="stretch_width",
    )
    shell.background_linear_custom_t = pn.widgets.FloatInput(
        name="Custom t",
        value=0.8,
        step=0.01,
        sizing_mode="stretch_width",
    )
    shell.background_linear_compute_button = pn.widgets.Button(
        name="Compute Linear Combination",
        button_type="primary",
        sizing_mode="fixed",
        width=260,
        height=48,
        disabled=False,
    )
    shell.background_linear_message = pn.pane.Alert(
        "Compute a linear-combination background model to estimate the best t parameter.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_t_start = pn.widgets.FloatInput(
        name="t start",
        value=-1.0,
        step=0.05,
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_t_stop = pn.widgets.FloatInput(
        name="t stop",
        value=2.0,
        step=0.05,
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_t_step = pn.widgets.FloatInput(
        name="t step",
        value=0.05,
        step=0.01,
        start=1e-6,
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_smoothing = pn.widgets.FloatInput(
        name="Smoothing factor",
        value=0.01,
        step=0.005,
        start=0.0,
        end=1.0,
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_ignore_points = pn.widgets.IntInput(
        name="Ignore first N points",
        value=25,
        step=1,
        start=0,
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_t_mode = pn.widgets.RadioButtonGroup(
        name="t selection",
        options=["Use computed t", "Use custom t"],
        value="Use computed t",
        button_type="default",
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_custom_t = pn.widgets.FloatInput(
        name="Custom t",
        value=0.8,
        step=0.01,
        sizing_mode="stretch_width",
        disabled=True,
    )
    shell.background_vanadium_compute_button = pn.widgets.Button(
        name="Compute Linear Combination",
        button_type="primary",
        sizing_mode="fixed",
        width=260,
        height=48,
        disabled=False,
    )
    shell.background_vanadium_message = pn.pane.Alert(
        "Compute a vanadium background model to estimate the best t parameter.",
        alert_type="secondary",
        sizing_mode="stretch_width",
    )
    shell.background_vanadium_controls_card = pn.Card(
        pn.Row(
            shell.background_vanadium_t_start,
            shell.background_vanadium_t_stop,
            shell.background_vanadium_t_step,
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.background_vanadium_smoothing,
            shell.background_vanadium_ignore_points,
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.background_vanadium_compute_button,
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.background_vanadium_t_mode,
            shell.background_vanadium_custom_t,
            sizing_mode="stretch_width",
        ),
        shell.background_vanadium_message,
        title="Normalization (Vanadium)",
        sizing_mode="stretch_width",
        visible=False,
    )

    shell.background_vanadium_chi_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_vanadium_subtraction_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_vanadium_chi_plot_card = pn.Card(
        shell.background_vanadium_chi_plot_pane,
        title="Vanadium: χ vs t",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_vanadium_subtraction_plot_card = pn.Card(
        shell.background_vanadium_subtraction_plot_pane,
        title="Vanadium: Background subtraction",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_final_signals_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_final_signals_plot_card = pn.Card(
        shell.background_final_signals_plot_pane,
        title="Background-subtracted signals",
        sizing_mode="stretch_width",
        visible=False,
    )

    shell.background_export_folder_input = pn.widgets.TextInput(
        name="Export folder",
        value="processed/qspdata",
        placeholder="processed/qspdata",
        sizing_mode="stretch_width",
    )
    shell.background_export_button = pn.widgets.Button(
        name="Export Data",
        button_type="primary",
        sizing_mode="fixed",
        width=180,
        height=48,
        disabled=True,
    )
    shell.background_export_info_hover = pn.pane.HTML(
        "",
        sizing_mode="fixed",
        width=40,
        margin=(0, 0, 0, 0),
        styles={"overflow": "visible"},
    )
    shell.background_export_prompt = pn.pane.Alert(
        "",
        alert_type="warning",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_export_confirm_button = pn.widgets.Button(
        name="Proceed",
        button_type="danger",
        sizing_mode="fixed",
        width=140,
        height=44,
        disabled=False,
    )
    shell.background_export_cancel_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        sizing_mode="fixed",
        width=120,
        height=44,
        disabled=False,
    )
    shell.background_export_prompt_card = pn.Card(
        shell.background_export_prompt,
        pn.Row(
            shell.background_export_confirm_button,
            shell.background_export_cancel_button,
        ),
        title="Confirm Export",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_export_card = pn.Card(
        pn.Column(
            shell.background_export_folder_input,
            pn.Row(
                shell.background_export_button,
                shell.background_export_info_hover,
                sizing_mode="stretch_width",
            ),
            sizing_mode="stretch_width",
        ),
        shell.background_export_prompt_card,
        title="Export Data",
        sizing_mode="stretch_width",
        css_classes=["toscana-overflow-visible"],
        styles={"overflow": "visible", "margin-bottom": "180px"},
        visible=True,
    )
    shell.background_linear_chi_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_linear_subtraction_plot_pane = pn.pane.Plotly(
        None,
        sizing_mode="stretch_width",
        config={"responsive": True},
    )
    shell.background_linear_controls_card = pn.Card(
        pn.Row(
            shell.background_linear_t_start,
            shell.background_linear_t_stop,
            shell.background_linear_t_step,
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.background_linear_smoothing,
            shell.background_linear_ignore_points,
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.background_linear_compute_button,
            sizing_mode="stretch_width",
        ),
        pn.Row(
            shell.background_linear_t_mode,
            shell.background_linear_custom_t,
            sizing_mode="stretch_width",
        ),
        shell.background_linear_message,
        pn.Card(
            shell.background_linear_chi_plot_pane,
            title="Linear Combination: χ vs t",
            sizing_mode="stretch_width",
        ),
        pn.Card(
            shell.background_linear_subtraction_plot_pane,
            title="Linear Combination: Background-subtracted diffractogram",
            sizing_mode="stretch_width",
        ),
        title="Linear Combination",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell.background_monte_carlo_card = pn.Card(
        pn.pane.Markdown(
            "Monte Carlo Simulation will be implemented in a future iteration.",
            sizing_mode="stretch_width",
        ),
        title="Monte Carlo Simulation",
        sizing_mode="stretch_width",
        visible=False,
    )
    shell._pending_numors_import_path: Path | None = None
    shell.recent_projects_column = pn.Column(sizing_mode="stretch_width")
    shell._selected_recent_project_file: str | None = None
    shell.save_and_continue_button = pn.widgets.Button(
        name="Save and Continue",
        button_type="primary",
        width=180,
        height=48,
    )
    shell.discard_and_continue_button = pn.widgets.Button(
        name="Discard and Continue",
        button_type="warning",
        width=190,
        height=48,
    )
    shell.cancel_navigation_button = pn.widgets.Button(
        name="Cancel",
        button_type="light",
        width=120,
        height=48,
    )
