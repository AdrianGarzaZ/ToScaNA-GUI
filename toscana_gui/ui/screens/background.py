from __future__ import annotations

import panel as pn


def build_background_section(shell) -> pn.Column:
    if shell.current_project_state is None:
        return pn.Column(
            pn.pane.Markdown(
                "Create or open a project first to configure Sample extraction.",
                sizing_mode="stretch_width",
            ),
            sizing_mode="stretch_width",
        )

    if hasattr(shell, "_set_background_source_widget_visibility"):
        shell._set_background_source_widget_visibility()

    contents: list[object] = [
        pn.Card(
            shell.background_source_mode,
            shell.background_source_stack,
            pn.Row(
                shell.background_validate_button,
                shell.background_extract_button,
                sizing_mode="stretch_width",
            ),
            shell.background_message,
            title="Sample Extraction",
            sizing_mode="stretch_width",
        )
    ]

    contents.append(shell.background_import_card)

    if hasattr(shell, "_refresh_background_plots"):
        shell._refresh_background_plots()

    contents.extend(
        [
            shell.background_no_data_pane,
            shell.background_plot_options_card,
            shell.background_raw_plot_alert,
            shell.background_raw_plot_card,
        ]
    )

    contents.append(
        pn.Card(
            pn.pane.HTML(
                '<div id="toscana-bg-method-anchor"></div>',
                margin=(0, 0, 0, 0),
            ),
            shell.background_subtraction_method,
            title="Background Subtraction Method",
            sizing_mode="stretch_width",
        )
    )

    contents.extend(
        [
            shell.background_subtraction_plot_alert,
            shell.background_subtraction_plot_card,
            shell.background_linear_controls_card,
            shell.background_vanadium_controls_card,
            shell.background_monte_carlo_card,
        ]
    )

    return pn.Column(*contents, sizing_mode="stretch_width")
