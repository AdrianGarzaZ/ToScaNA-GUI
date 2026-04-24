from __future__ import annotations

from html import escape as html_escape

import panel as pn

from toscana_gui.ui.screens import build_landing_page, build_workspace_page
from toscana_gui.ui.notifications import ToastLevel


def render_current_screen(shell) -> None:
    shell._refresh_workspace_button_states()
    shell._refresh_interaction_states()
    if shell.current_screen == "landing":
        shell.content[:] = [build_landing_page(shell)]
    else:
        shell.content[:] = [build_workspace_page(shell)]


def refresh_interaction_states(shell) -> None:
    disabled = shell.operation_in_progress
    shell.reset_project_button.disabled = disabled or shell.current_project_state is None
    shell.reset_project_confirm_button.disabled = disabled
    shell.reset_project_cancel_button.disabled = disabled
    shell.project_editor_name_input.disabled = disabled
    shell.save_project_button.disabled = disabled
    shell.numors_source_mode.disabled = disabled
    numors_picker_mode = shell.numors_source_mode.value == "Select File"
    shell.numors_par_dropdown.disabled = disabled or not numors_picker_mode
    shell.numors_manual_path_input.disabled = disabled or numors_picker_mode
    shell.numors_validate_button.disabled = disabled
    shell.numors_block_select.disabled = disabled
    shell.numors_import_confirm_button.disabled = disabled
    shell.numors_import_cancel_button.disabled = disabled
    shell.background_source_mode.disabled = disabled
    background_picker_mode = shell.background_source_mode.value == "Select File"
    shell.background_par_dropdown.disabled = disabled or not background_picker_mode
    shell.background_manual_path_input.disabled = disabled or background_picker_mode
    shell.background_validate_button.disabled = disabled
    shell.background_extract_button.disabled = disabled or not shell._get_background_state()[
        "validation"
    ].get("is_valid", False)
    shell.background_subtraction_method.disabled = disabled
    shell.background_linear_t_start.disabled = disabled
    shell.background_linear_t_stop.disabled = disabled
    shell.background_linear_t_step.disabled = disabled
    shell.background_linear_smoothing.disabled = disabled
    shell.background_linear_ignore_points.disabled = disabled
    shell.background_linear_compute_button.disabled = disabled
    shell.background_linear_t_mode.disabled = disabled
    shell.background_linear_custom_t.disabled = disabled or shell.background_linear_t_mode.value != "Use custom t"
    shell.background_vanadium_t_start.disabled = disabled
    shell.background_vanadium_t_stop.disabled = disabled
    shell.background_vanadium_t_step.disabled = disabled
    shell.background_vanadium_smoothing.disabled = disabled
    shell.background_vanadium_ignore_points.disabled = disabled
    shell.background_vanadium_compute_button.disabled = disabled
    shell.background_vanadium_t_mode.disabled = disabled
    shell.background_vanadium_custom_t.disabled = disabled or shell.background_vanadium_t_mode.value != "Use custom t"
    shell.background_error_bars_toggle.disabled = disabled
    shell.background_import_confirm_button.disabled = disabled
    shell.background_import_cancel_button.disabled = disabled
    shell.background_export_folder_input.disabled = disabled
    export_ready = shell._background_export_is_ready() if hasattr(shell, "_background_export_is_ready") else False
    shell.background_export_button.disabled = disabled or not export_ready
    shell.background_export_confirm_button.disabled = disabled
    shell.background_export_cancel_button.disabled = disabled
    shell.manual_project_file_mode.disabled = disabled
    manual_picker_mode = shell.manual_project_file_mode.value == "Choose file"
    shell.manual_project_file_input.disabled = disabled or manual_picker_mode
    shell.manual_project_file_browse_button.disabled = disabled or not manual_picker_mode
    shell.manual_project_file_native_browse_button.disabled = disabled or not manual_picker_mode
    shell.manual_project_file_confirm_button.disabled = (
        disabled or not manual_picker_mode or shell._manual_project_file_candidate is None
    )
    shell.manual_project_file_cancel_button.disabled = disabled or not manual_picker_mode
    shell.manual_project_file_selector.disabled = disabled or not manual_picker_mode
    shell.manual_open_button.disabled = disabled or not shell.manual_project_file_input.value.strip()
    shell.project_folder_mode.disabled = disabled
    folder_is_picker_mode = shell.project_folder_mode.value == "Choose folder"
    selected_folder_value = shell.project_folder_selected_display.value.strip()
    shell.project_folder_browse_button.disabled = disabled or not folder_is_picker_mode
    shell.project_folder_native_browse_button.disabled = disabled or not folder_is_picker_mode
    shell.project_folder_confirm_button.disabled = (
        disabled or not folder_is_picker_mode or shell._project_folder_candidate is None
    )
    shell.project_folder_cancel_button.disabled = disabled or not folder_is_picker_mode
    shell.project_folder_file_selector.disabled = disabled or not folder_is_picker_mode
    shell.create_project_confirm_button.disabled = (
        disabled or (folder_is_picker_mode and not selected_folder_value)
    )
    shell.project_name_input.disabled = disabled
    shell.project_folder_input.disabled = disabled or folder_is_picker_mode
    shell.numors_run_button.disabled = disabled or not shell._get_numors_state()["validation"].get(
        "is_valid",
        False,
    )
    shell.numors_prev_block_button.disabled = disabled
    shell.numors_next_block_button.disabled = disabled
    shell.numors_prev_plot_button.disabled = disabled
    shell.numors_next_plot_button.disabled = disabled

    if hasattr(shell, "_refresh_background_export_hovercard"):
        shell._refresh_background_export_hovercard()
    if hasattr(shell, "_sync_background_export_prompt_visibility"):
        shell._sync_background_export_prompt_visibility()


def refresh_workspace_button_states(shell) -> None:
    for tab_name, button in shell.workspace_buttons.items():
        button.button_type = "primary" if tab_name == shell.current_top_level_tab else "light"


def show_workspace_blocked_message(shell) -> None:
    shell.workspace_message.object = (
        "An operation is in progress. This action is blocked until it finishes."
    )
    shell.workspace_message.alert_type = "warning"
    shell.workspace_message.visible = True
    if shell.current_screen == "workspace":
        shell._render_current_screen()


def clear_workspace_message(shell) -> None:
    shell.workspace_message.object = ""
    shell.workspace_message.visible = False


def show_toast(
    shell,
    *,
    level: ToastLevel,
    message: str,
    persistent: bool | None = None,
) -> None:
    if persistent is None:
        persistent = level == "error"

    duration_ms = 0 if persistent else int(getattr(shell, "toast_duration_ms", 8000))
    area = pn.state.notifications
    if area is None:
        return
    try:
        area.max_notifications = 2
        area.position = "top-right"
    except Exception:
        pass
    if level == "success":
        area.success(message, duration=duration_ms)
    elif level == "warning":
        area.warning(message, duration=duration_ms)
    elif level == "error":
        area.error(message, duration=duration_ms)
    else:
        area.info(message, duration=duration_ms)


def show_success_toast(shell, message: str) -> None:
    show_toast(shell, level="success", message=message, persistent=False)


def show_info_toast(shell, message: str) -> None:
    show_toast(shell, level="info", message=message, persistent=False)


def show_warning_toast(shell, message: str) -> None:
    show_toast(shell, level="warning", message=message, persistent=False)


def show_error_toast(shell, message: str) -> None:
    show_toast(shell, level="error", message=message, persistent=True)


def clear_success_toast_if_current(shell, _token: int) -> None:
    return


def build_template(shell) -> pn.template.FastListTemplate:
    return pn.template.FastListTemplate(
        title="ToScaNA",
        main=[shell.content],
        header=[
            pn.Spacer(),
            pn.Spacer(),
            shell.reset_project_button,
        ],
    )
