from __future__ import annotations


def bind_shell_callbacks(shell) -> None:
    shell.start_project_button.on_click(shell._go_to_workspace_from_start)
    shell.continue_project_button.on_click(shell._go_to_workspace_from_continue)
    shell.back_to_menu_button.on_click(shell._go_to_landing_page)
    shell.reset_project_button.on_click(shell._prompt_reset_project)
    for tab_name, button in shell.workspace_buttons.items():
        button.on_click(shell._make_workspace_navigation_handler(tab_name))
    shell.create_project_confirm_button.on_click(shell._create_project)
    shell.save_project_button.on_click(shell._save_current_project)
    shell.manual_open_button.on_click(shell._open_project_from_manual_path)
    shell.numors_validate_button.on_click(shell._validate_numors_selection)
    shell.numors_run_button.on_click(shell._notify_numors_execution_pending)
    shell.numors_prev_block_button.on_click(shell._on_numors_prev_run_block)
    shell.numors_next_block_button.on_click(shell._on_numors_next_run_block)
    shell.numors_prev_plot_button.on_click(shell._on_numors_prev_plot)
    shell.numors_next_plot_button.on_click(shell._on_numors_next_plot)
    shell.numors_import_confirm_button.on_click(shell._copy_numors_file_into_project)
    shell.numors_import_cancel_button.on_click(shell._cancel_numors_import)
    shell.background_validate_button.on_click(shell._validate_background_selection)
    shell.background_extract_button.on_click(shell._notify_background_extraction_pending)
    shell.background_import_confirm_button.on_click(shell._copy_background_file_into_project)
    shell.background_import_cancel_button.on_click(shell._cancel_background_import)
    shell.background_linear_compute_button.on_click(shell._compute_background_linear_combination)
    shell.background_vanadium_compute_button.on_click(shell._compute_background_vanadium_linear_combination)
    shell.background_export_button.on_click(shell._prompt_background_export)
    shell.background_export_confirm_button.on_click(shell._confirm_background_export)
    shell.background_export_cancel_button.on_click(shell._cancel_background_export)
    shell.reset_project_confirm_button.on_click(shell._confirm_reset_project)
    shell.reset_project_cancel_button.on_click(shell._cancel_reset_project)
    shell.save_and_continue_button.on_click(shell._save_and_continue)
    shell.discard_and_continue_button.on_click(shell._discard_and_continue)
    shell.cancel_navigation_button.on_click(shell._cancel_pending_navigation)
    shell.project_editor_name_input.param.watch(
        shell._on_project_editor_name_change,
        "value",
    )
    shell.project_name_input.param.watch(shell._on_project_name_input_change, "value")
    shell.project_folder_input.param.watch(shell._on_project_folder_input_change, "value")
    shell.project_folder_mode.param.watch(shell._on_project_folder_mode_change, "value")
    shell.project_folder_file_selector.param.watch(
        shell._on_project_folder_candidate_change,
        "value",
    )
    shell.manual_project_file_mode.param.watch(
        shell._on_manual_project_file_mode_change,
        "value",
    )
    shell.manual_project_file_input.param.watch(
        shell._on_manual_project_file_input_change,
        "value",
    )
    shell.manual_project_file_selector.param.watch(
        shell._on_manual_project_file_candidate_change,
        "value",
    )
    shell.numors_source_mode.param.watch(shell._on_numors_source_mode_change, "value")
    shell.background_source_mode.param.watch(shell._on_background_source_mode_change, "value")
    shell.numors_manual_path_input.param.watch(
        shell._on_numors_manual_path_change,
        "value",
    )
    shell.background_manual_path_input.param.watch(shell._on_background_manual_path_change, "value")
    shell.numors_par_dropdown.param.watch(shell._on_numors_par_dropdown_change, "value")
    shell.background_par_dropdown.param.watch(shell._on_background_par_dropdown_change, "value")
    shell.background_error_bars_toggle.param.watch(shell._on_background_error_bars_toggle, "value")
    shell.background_subtraction_method.param.watch(
        shell._on_background_subtraction_method_change,
        "value",
    )
    shell.background_linear_t_start.param.watch(shell._on_background_linear_settings_change, "value")
    shell.background_linear_t_stop.param.watch(shell._on_background_linear_settings_change, "value")
    shell.background_linear_t_step.param.watch(shell._on_background_linear_settings_change, "value")
    shell.background_linear_smoothing.param.watch(shell._on_background_linear_settings_change, "value")
    shell.background_linear_ignore_points.param.watch(shell._on_background_linear_settings_change, "value")
    shell.background_linear_t_mode.param.watch(shell._on_background_linear_t_selection_change, "value")
    shell.background_linear_custom_t.param.watch(shell._on_background_linear_t_selection_change, "value")
    shell.background_vanadium_t_start.param.watch(shell._on_background_vanadium_settings_change, "value")
    shell.background_vanadium_t_stop.param.watch(shell._on_background_vanadium_settings_change, "value")
    shell.background_vanadium_t_step.param.watch(shell._on_background_vanadium_settings_change, "value")
    shell.background_vanadium_smoothing.param.watch(shell._on_background_vanadium_settings_change, "value")
    shell.background_vanadium_ignore_points.param.watch(shell._on_background_vanadium_settings_change, "value")
    shell.background_vanadium_t_mode.param.watch(shell._on_background_vanadium_t_selection_change, "value")
    shell.background_vanadium_custom_t.param.watch(shell._on_background_vanadium_t_selection_change, "value")
    shell.background_export_folder_input.param.watch(shell._on_background_export_folder_change, "value")
    shell.numors_block_select.param.watch(shell._on_numors_block_select_change, "value")
    shell.project_folder_browse_button.on_click(shell._toggle_project_folder_browser)
    shell.project_folder_native_browse_button.on_click(shell._choose_project_folder_native)
    shell.project_folder_confirm_button.on_click(shell._confirm_project_folder_browser)
    shell.project_folder_cancel_button.on_click(shell._cancel_project_folder_browser)
    shell.manual_project_file_browse_button.on_click(
        shell._toggle_manual_project_file_browser
    )
    shell.manual_project_file_native_browse_button.on_click(
        shell._choose_manual_project_file_native
    )
    shell.manual_project_file_confirm_button.on_click(
        shell._confirm_manual_project_file_browser
    )
    shell.manual_project_file_cancel_button.on_click(
        shell._cancel_manual_project_file_browser
    )
