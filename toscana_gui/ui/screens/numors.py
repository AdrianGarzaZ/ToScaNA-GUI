from __future__ import annotations

from html import escape

import panel as pn


def build_numors_section(shell) -> pn.Column:
    numors_state = shell._get_numors_state()
    validation_state = numors_state["validation"]

    if shell.numors_source_mode.value == "Select File":
        shell._suspend_numors_events = True
        shell._refresh_numors_par_dropdown_options()
        shell._suspend_numors_events = False

    source_widget = (
        shell.numors_par_dropdown
        if shell.numors_source_mode.value == "Select File"
        else shell.numors_manual_path_input
    )

    def _go_to_run_history(_event=None) -> None:
        shell._navigate_to_workspace_section("run_history")

    run_history_info_button = pn.widgets.Button(
        name="ℹ Run History",
        button_type="light",
        width=140,
        height=40,
    )
    run_history_info_button.on_click(_go_to_run_history)

    has_numors_run = _has_numors_run(shell)
    validation_hovercard = (
        pn.pane.HTML(
            _build_validation_hovercard_html(validation_state),
            sizing_mode="fixed",
            width=40,
            margin=(0, 0, 0, 0),
            styles={"overflow": "visible"},
        )
        if has_numors_run
        else pn.Spacer(width=0, height=0)
    )

    numors_notice = _maybe_inline_or_toast(
        shell,
        key="numors:message",
        pane=shell.numors_message,
    )

    contents: list[object] = [
        pn.Card(
            shell.numors_source_mode,
            source_widget,
            pn.Row(
                shell.numors_validate_button,
                shell.numors_run_button,
                validation_hovercard,
                sizing_mode="stretch_width",
            ),
            numors_notice,
            title="Numors Input",
            sizing_mode="stretch_width",
            css_classes=["toscana-overflow-visible"],
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

    latest_record = _latest_numors_record(shell)
    shell._refresh_numors_run_blocks_view(latest_record)
    if shell.numors_run_blocks_card.visible:
        contents.append(shell.numors_run_blocks_card)

    contents.append(
        pn.Row(
            pn.pane.Markdown(
                "Need logs or plots? Open the Run History tab.",
                sizing_mode="stretch_width",
                margin=(0, 0, 0, 0),
            ),
            pn.Spacer(),
            run_history_info_button,
            sizing_mode="stretch_width",
        )
    )

    return pn.Column(
        *contents,
        sizing_mode="stretch_width",
    )


def _has_numors_run(shell) -> bool:
    if shell.current_project_state is None:
        return False
    return any(record.workflow == "numors" for record in shell.current_project_state.runs)


def _format_yes_no(value: object) -> str:
    return "Yes" if bool(value) else "No"


def _fmt_path(value: object) -> str:
    raw = str(value).strip() if value is not None else ""
    if not raw:
        return "<em>Not available</em>"
    return f"<code>{escape(raw)}</code>"

def _build_validation_hovercard_html(validation_state: dict) -> str:
    selected_file = _fmt_path(validation_state.get("selected_par_path"))
    accessible = _format_yes_no(validation_state.get("file_accessible"))
    rawdata_path = _fmt_path(validation_state.get("resolved_rawdata_path"))
    eff_path = _fmt_path(validation_state.get("resolved_efffile_path"))
    dec_path = _fmt_path(validation_state.get("resolved_decfile_path"))

    return f"""
    <div class="toscana-hovercard toscana-hovercard--open-right" aria-label="Validation summary">
      <div class="toscana-hovercard__icon" title="Validation summary">ℹ</div>
      <div class="toscana-hovercard__panel">
        <div><strong>Selected file:</strong> {selected_file}</div>
        <div><strong>File accessible:</strong> {escape(accessible)}</div>
        <div><strong>Resolved raw data path:</strong> {rawdata_path}</div>
        <div><strong>Resolved efficiency path:</strong> {eff_path}</div>
        <div><strong>Resolved shifts path:</strong> {dec_path}</div>
      </div>
    </div>
    """.strip()


def _latest_numors_record(shell):
    if shell.current_project_state is None:
        return None

    return next(
        (record for record in reversed(shell.current_project_state.runs) if record.workflow == "numors"),
        None,
    )


def _maybe_inline_or_toast(shell, *, key: str, pane: pn.pane.Alert) -> object:
    message = str(getattr(pane, "object", "") or "").strip()
    alert_type = str(getattr(pane, "alert_type", "secondary") or "secondary")
    if not message:
        return pn.Spacer(height=0)

    level_map = {
        "primary": "info",
        "secondary": "info",
        "success": "success",
        "warning": "warning",
        "danger": "error",
    }
    level = level_map.get(alert_type, "info")
    pane.visible = alert_type == "danger"
    if alert_type != "danger":
        shell._show_toast_once(key, level=level, message=message, persistent=False)
        return pn.Spacer(height=0)

    shell._show_toast_once(key, level=level, message=message, persistent=True)
    return pane
