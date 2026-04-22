from __future__ import annotations

import subprocess
from pathlib import Path

import panel as pn

from toscana_gui.numors.controller import NumorsControllerMixin
from toscana_gui.numors.tasks import NUMORS_SOURCE_OPTIONS
from toscana_gui.projects.tasks import WorkspaceTab
from toscana_gui.paths import REPO_ROOT
from toscana_gui.persistence import (
    APP_STATE_FILENAME,
    AppState,
    ProjectState,
    load_app_state,
)
from toscana_gui.projects.controller import ProjectSessionControllerMixin
from toscana_gui.ui.theme import configure_panel
from toscana_gui.ui import runtime as ui_runtime

APP_STATE_PATH = REPO_ROOT / APP_STATE_FILENAME


class ToScaNAShell(ProjectSessionControllerMixin, NumorsControllerMixin):
    def __init__(self) -> None:
        configure_panel()

        self.current_screen = "landing"
        self.workspace_entrypoint = "No action selected yet."
        self.workspace_result: str | None = None
        self.pending_navigation_action: str | None = None
        self.current_project_root: Path | None = None
        self.current_project_file: Path | None = None
        self.current_project_state: ProjectState | None = None
        self.current_project_dirty = False
        self.current_top_level_tab: WorkspaceTab = "project"
        self.operation_in_progress = False
        self._suspend_dirty_tracking = False
        self._suspend_numors_events = False
        self._success_toast_token = 0
        self._numors_run_process: subprocess.Popen | None = None
        self._numors_run_poll = None
        self._numors_active_run_id: str | None = None
        self._numors_result_file: Path | None = None
        self.app_state: AppState = load_app_state(APP_STATE_PATH)

        self.content = pn.Column(sizing_mode="stretch_both")
        self.success_toast = pn.pane.HTML(
            "",
            visible=False,
            sizing_mode="stretch_width",
        )

        self.start_project_button = pn.widgets.Button(
            name="Start New Project",
            button_type="primary",
            sizing_mode="fixed",
            width=360,
            height=60,
        )
        self.continue_project_button = pn.widgets.Button(
            name="Continue Previous Project",
            button_type="default",
            sizing_mode="fixed",
            width=360,
            height=60,
        )
        self.help_button = pn.widgets.Button(
            name="Help (Coming soon)",
            button_type="light",
            disabled=True,
            sizing_mode="fixed",
            width=360,
            height=60,
        )
        self.back_to_menu_button = pn.widgets.Button(
            name="Back to Main Menu",
            button_type="default",
            sizing_mode="fixed",
            width=180,
        )
        self.workspace_buttons: dict[WorkspaceTab, pn.widgets.Button] = {
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
        self.project_name_input = pn.widgets.TextInput(
            name="Project Name",
            placeholder="My D4 Session",
            sizing_mode="stretch_width",
        )
        self.project_folder_input = pn.widgets.TextInput(
            name="Project Folder",
            placeholder=r"D:\ILL\ToScaNA\Projects\my-session",
            sizing_mode="stretch_width",
        )
        self.project_folder_mode = pn.widgets.RadioBoxGroup(
            name="Project Folder Input",
            options=["Enter folder path", "Choose folder"],
            value="Enter folder path",
            inline=True,
            sizing_mode="stretch_width",
        )
        self.project_folder_browser_visible = False
        self._project_folder_candidate: Path | None = None
        self.project_folder_selected_display = pn.widgets.TextInput(
            name="Selected Folder",
            placeholder="No folder selected yet.",
            disabled=True,
            sizing_mode="stretch_width",
        )
        self.project_folder_browse_button = pn.widgets.Button(
            name="Choose Folder...",
            button_type="primary",
            sizing_mode="fixed",
            width=200,
            height=44,
            disabled=False,
        )
        self.project_folder_native_browse_button = pn.widgets.Button(
            name="Choose Folder (Windows)...",
            button_type="light",
            sizing_mode="fixed",
            width=240,
            height=44,
        )
        self.project_folder_confirm_button = pn.widgets.Button(
            name="Use Selected Folder",
            button_type="primary",
            sizing_mode="fixed",
            width=220,
            height=44,
            disabled=True,
        )
        self.project_folder_cancel_button = pn.widgets.Button(
            name="Cancel",
            button_type="light",
            sizing_mode="fixed",
            width=120,
            height=44,
        )
        self.project_folder_file_selector = pn.widgets.FileSelector(
            directory=str(self._default_project_folder_browser_root()),
            only_files=False,
            size=8,
            sizing_mode="stretch_width",
        )
        self.create_project_confirm_button = pn.widgets.Button(
            name="Create Project",
            button_type="primary",
            sizing_mode="fixed",
            width=220,
            height=52,
        )
        self.start_project_message = pn.pane.Alert(
            "Provide a project name and a target folder.",
            alert_type="secondary",
            sizing_mode="stretch_width",
        )
        self.project_editor_name_input = pn.widgets.TextInput(
            name="Project Name",
            sizing_mode="stretch_width",
        )
        self.save_project_button = pn.widgets.Button(
            name="Save Project",
            button_type="primary",
            sizing_mode="fixed",
            width=180,
            height=48,
        )
        self.project_editor_message = pn.pane.Alert(
            "No unsaved changes.",
            alert_type="secondary",
            sizing_mode="stretch_width",
        )
        self.manual_project_file_input = pn.widgets.TextInput(
            name="Project File",
            placeholder=r"D:\ILL\ToScaNA\Projects\my-session\ntsa-project.json",
            sizing_mode="stretch_width",
        )
        self.manual_project_file_mode = pn.widgets.RadioBoxGroup(
            name="Open Project Input",
            options=["Enter file path", "Choose file"],
            value="Enter file path",
            inline=True,
            sizing_mode="stretch_width",
        )
        self.manual_project_file_browser_visible = False
        self._manual_project_file_candidate: Path | None = None
        self.manual_project_file_selected_display = pn.widgets.TextInput(
            name="Selected File",
            placeholder="No file selected yet.",
            disabled=True,
            sizing_mode="stretch_width",
        )
        self.manual_project_file_browse_button = pn.widgets.Button(
            name="Choose File...",
            button_type="primary",
            sizing_mode="fixed",
            width=180,
            height=44,
        )
        self.manual_project_file_native_browse_button = pn.widgets.Button(
            name="Choose File (Windows)...",
            button_type="light",
            sizing_mode="fixed",
            width=220,
            height=44,
        )
        self.manual_project_file_confirm_button = pn.widgets.Button(
            name="Use Selected File",
            button_type="primary",
            sizing_mode="fixed",
            width=200,
            height=44,
            disabled=True,
        )
        self.manual_project_file_cancel_button = pn.widgets.Button(
            name="Cancel",
            button_type="light",
            sizing_mode="fixed",
            width=120,
            height=44,
        )
        self.manual_project_file_selector = pn.widgets.FileSelector(
            directory=str(REPO_ROOT),
            file_pattern="ntsa-project.json",
            only_files=True,
            size=8,
            sizing_mode="stretch_width",
        )
        self.manual_open_button = pn.widgets.Button(
            name="Open Project File",
            button_type="primary",
            sizing_mode="fixed",
            width=220,
            height=52,
        )
        self.continue_project_message = pn.pane.Alert(
            "Choose a recent project or open an `ntsa-project.json` file manually.",
            alert_type="secondary",
            sizing_mode="stretch_width",
        )
        self.workspace_message = pn.pane.Alert(
            "",
            alert_type="warning",
            sizing_mode="stretch_width",
            visible=False,
        )
        self.numors_source_mode = pn.widgets.RadioBoxGroup(
            name="Input Mode",
            inline=False,
            options=list(NUMORS_SOURCE_OPTIONS),
            value=NUMORS_SOURCE_OPTIONS[0],
            sizing_mode="stretch_width",
        )
        self.numors_file_selector = pn.widgets.FileSelector(
            directory=str(REPO_ROOT),
            file_pattern="*.par",
            only_files=True,
            size=8,
            sizing_mode="stretch_width",
        )
        self.numors_manual_path_input = pn.widgets.TextInput(
            name="File Path",
            placeholder=r"D:\ILL\ToScaNA\Project\processed\parfiles\do_name.par",
            sizing_mode="stretch_width",
        )
        self.numors_validate_button = pn.widgets.Button(
            name="Validate File",
            button_type="primary",
            sizing_mode="fixed",
            width=180,
            height=48,
        )
        self.numors_run_button = pn.widgets.Button(
            name="Run d4creg",
            button_type="primary",
            sizing_mode="fixed",
            width=180,
            height=48,
            disabled=True,
        )
        self.numors_block_select = pn.widgets.Select(
            name="Block",
            options={},
            sizing_mode="stretch_width",
        )
        self.numors_prev_block_button = pn.widgets.Button(
            name="◀ Prev Block",
            button_type="light",
            sizing_mode="fixed",
            width=140,
            height=40,
        )
        self.numors_next_block_button = pn.widgets.Button(
            name="Next Block ▶",
            button_type="light",
            sizing_mode="fixed",
            width=140,
            height=40,
        )
        self.numors_prev_plot_button = pn.widgets.Button(
            name="◀ Prev Plot",
            button_type="light",
            sizing_mode="fixed",
            width=140,
            height=40,
        )
        self.numors_next_plot_button = pn.widgets.Button(
            name="Next Plot ▶",
            button_type="light",
            sizing_mode="fixed",
            width=140,
            height=40,
        )
        self.numors_block_header = pn.pane.Markdown("", sizing_mode="stretch_width")
        self.numors_block_details = pn.pane.Markdown("", sizing_mode="stretch_width")
        self.numors_block_plot_counter = pn.pane.Markdown("", sizing_mode="stretch_width")
        self.numors_block_plot_container = pn.Column(sizing_mode="stretch_width")
        self.numors_run_blocks_card = pn.Card(
            self.numors_block_select,
            pn.Row(
                self.numors_prev_block_button,
                self.numors_next_block_button,
                self.numors_block_header,
                sizing_mode="stretch_width",
            ),
            self.numors_block_details,
            pn.Row(
                self.numors_prev_plot_button,
                self.numors_next_plot_button,
                self.numors_block_plot_counter,
                sizing_mode="stretch_width",
            ),
            self.numors_block_plot_container,
            title="Run Blocks",
            sizing_mode="stretch_width",
            visible=False,
        )
        self.numors_message = pn.pane.Alert(
            "Choose a `.par` file and validate it.",
            alert_type="secondary",
            sizing_mode="stretch_width",
        )
        self.numors_plot_warning = pn.pane.Alert(
            (
                "The selected `.par` file enables backend plotting. "
                "This workflow will use the backend plot output in a later slice."
            ),
            alert_type="warning",
            sizing_mode="stretch_width",
            visible=False,
        )
        self.numors_import_prompt = pn.pane.Alert(
            "",
            alert_type="warning",
            sizing_mode="stretch_width",
            visible=False,
        )
        self.numors_import_confirm_button = pn.widgets.Button(
            name="Copy Into Project",
            button_type="primary",
            sizing_mode="fixed",
            width=180,
            height=44,
        )
        self.numors_import_cancel_button = pn.widgets.Button(
            name="Cancel",
            button_type="light",
            sizing_mode="fixed",
            width=120,
            height=44,
        )
        self._pending_numors_import_path: Path | None = None
        self.recent_projects_column = pn.Column(sizing_mode="stretch_width")
        self._selected_recent_project_file: str | None = None
        self.save_and_continue_button = pn.widgets.Button(
            name="Save and Continue",
            button_type="primary",
            width=180,
            height=48,
        )
        self.discard_and_continue_button = pn.widgets.Button(
            name="Discard and Continue",
            button_type="warning",
            width=190,
            height=48,
        )
        self.cancel_navigation_button = pn.widgets.Button(
            name="Cancel",
            button_type="light",
            width=120,
            height=48,
        )

        self.start_project_button.on_click(self._go_to_workspace_from_start)
        self.continue_project_button.on_click(self._go_to_workspace_from_continue)
        self.back_to_menu_button.on_click(self._go_to_landing_page)
        for tab_name, button in self.workspace_buttons.items():
            button.on_click(self._make_workspace_navigation_handler(tab_name))
        self.create_project_confirm_button.on_click(self._create_project)
        self.save_project_button.on_click(self._save_current_project)
        self.manual_open_button.on_click(self._open_project_from_manual_path)
        self.numors_validate_button.on_click(self._validate_numors_selection)
        self.numors_run_button.on_click(self._notify_numors_execution_pending)
        self.numors_prev_block_button.on_click(self._on_numors_prev_run_block)
        self.numors_next_block_button.on_click(self._on_numors_next_run_block)
        self.numors_prev_plot_button.on_click(self._on_numors_prev_plot)
        self.numors_next_plot_button.on_click(self._on_numors_next_plot)
        self.numors_import_confirm_button.on_click(self._copy_numors_file_into_project)
        self.numors_import_cancel_button.on_click(self._cancel_numors_import)
        self.save_and_continue_button.on_click(self._save_and_continue)
        self.discard_and_continue_button.on_click(self._discard_and_continue)
        self.cancel_navigation_button.on_click(self._cancel_pending_navigation)
        self.project_editor_name_input.param.watch(
            self._on_project_editor_name_change,
            "value",
        )
        self.project_folder_mode.param.watch(self._on_project_folder_mode_change, "value")
        self.project_folder_file_selector.param.watch(
            self._on_project_folder_candidate_change,
            "value",
        )
        self.manual_project_file_mode.param.watch(
            self._on_manual_project_file_mode_change,
            "value",
        )
        self.manual_project_file_input.param.watch(
            self._on_manual_project_file_input_change,
            "value",
        )
        self.manual_project_file_selector.param.watch(
            self._on_manual_project_file_candidate_change,
            "value",
        )
        self.numors_source_mode.param.watch(self._on_numors_source_mode_change, "value")
        self.numors_manual_path_input.param.watch(
            self._on_numors_manual_path_change,
            "value",
        )
        self.numors_file_selector.param.watch(
            self._on_numors_file_selector_change,
            "value",
        )
        self.numors_block_select.param.watch(self._on_numors_block_select_change, "value")
        self.project_folder_browse_button.on_click(self._toggle_project_folder_browser)
        self.project_folder_native_browse_button.on_click(
            self._choose_project_folder_native
        )
        self.project_folder_confirm_button.on_click(self._confirm_project_folder_browser)
        self.project_folder_cancel_button.on_click(self._cancel_project_folder_browser)
        self.manual_project_file_browse_button.on_click(
            self._toggle_manual_project_file_browser
        )
        self.manual_project_file_native_browse_button.on_click(
            self._choose_manual_project_file_native
        )
        self.manual_project_file_confirm_button.on_click(
            self._confirm_manual_project_file_browser
        )
        self.manual_project_file_cancel_button.on_click(
            self._cancel_manual_project_file_browser
        )

        self._render_current_screen()

    def _render_current_screen(self) -> None:
        ui_runtime.render_current_screen(self)

    def _refresh_interaction_states(self) -> None:
        ui_runtime.refresh_interaction_states(self)

    def _refresh_workspace_button_states(self) -> None:
        ui_runtime.refresh_workspace_button_states(self)

    def _show_workspace_blocked_message(self) -> None:
        ui_runtime.show_workspace_blocked_message(self)

    def _clear_workspace_message(self) -> None:
        ui_runtime.clear_workspace_message(self)

    def _show_success_toast(self, message: str) -> None:
        ui_runtime.show_success_toast(self, message)

    def _clear_success_toast_if_current(self, token: int) -> None:
        ui_runtime.clear_success_toast_if_current(self, token)

    def build(self) -> pn.template.FastListTemplate:
        return ui_runtime.build_template(self)
