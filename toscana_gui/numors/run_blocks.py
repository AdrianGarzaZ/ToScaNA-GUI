from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import panel as pn


def update_numors_block_select(shell: Any, options: dict[str, int], value: int) -> None:
    shell._suspend_numors_events = True
    shell.numors_block_select.options = options
    shell.numors_block_select.value = value
    shell._suspend_numors_events = False


def latest_numors_run_blocks(shell: Any) -> list[dict] | None:
    if shell.current_project_state is None:
        return None
    latest_record = next(
        (record for record in reversed(shell.current_project_state.runs) if record.workflow == "numors"),
        None,
    )
    if latest_record is None:
        return None
    payload = getattr(latest_record, "workflow_data", None)
    if not isinstance(payload, dict):
        return None
    blocks = payload.get("run_blocks")
    if not isinstance(blocks, list):
        return None
    return blocks


def latest_selected_numors_plot_files(shell: Any) -> list[str]:
    blocks = latest_numors_run_blocks(shell) or []
    if not blocks:
        return []
    state = shell._get_numors_state()
    block_index = state.get("selected_run_block_index", 0)
    if not isinstance(block_index, int):
        block_index = 0
    block_index = max(0, min(block_index, len(blocks) - 1))
    block = blocks[block_index] if isinstance(blocks[block_index], dict) else {}
    plot_files = block.get("plot_files", [])
    return list(plot_files) if isinstance(plot_files, list) else []


def resolve_numors_block_selection(
    run_blocks: list[dict],
    numors_state: dict,
) -> tuple[int, int, list[str]]:
    block_index_raw = numors_state.get("selected_run_block_index", 0)
    block_index = int(block_index_raw) if isinstance(block_index_raw, int) else 0
    block_index = max(0, min(block_index, max(len(run_blocks) - 1, 0)))

    block = run_blocks[block_index] if run_blocks and isinstance(run_blocks[block_index], dict) else {}
    plot_files = block.get("plot_files", [])
    plot_files = list(plot_files) if isinstance(plot_files, list) else []

    plot_index_raw = numors_state.get("selected_run_block_plot_index", 0)
    plot_index = int(plot_index_raw) if isinstance(plot_index_raw, int) else 0
    plot_index = max(0, min(plot_index, max(len(plot_files) - 1, 0)))

    return block_index, plot_index, plot_files


def refresh_numors_run_blocks_view(shell: Any, latest_record: Any = None) -> None:
    if latest_record is None and shell.current_project_state is not None:
        latest_record = next(
            (record for record in reversed(shell.current_project_state.runs) if record.workflow == "numors"),
            None,
        )

    workflow_data = getattr(latest_record, "workflow_data", None) if latest_record is not None else None
    run_blocks = workflow_data.get("run_blocks") if isinstance(workflow_data, dict) else None

    if not isinstance(run_blocks, list) or not run_blocks:
        shell.numors_run_blocks_card.visible = False
        return

    if latest_record is not None and getattr(latest_record, "run_id", None):
        shell.numors_run_blocks_run_id.object = f"**Run ID:** `{latest_record.run_id}`"
    else:
        shell.numors_run_blocks_run_id.object = ""

    state = shell._get_numors_state()
    block_index, plot_index, plot_files = resolve_numors_block_selection(run_blocks, state)

    if (
        state.get("selected_run_block_index") != block_index
        or state.get("selected_run_block_plot_index") != plot_index
    ):
        state["selected_run_block_index"] = block_index
        state["selected_run_block_plot_index"] = plot_index
        shell._persist_numors_state(state)

    options: dict[str, int] = {}
    for idx, block in enumerate(run_blocks):
        if not isinstance(block, dict):
            continue
        label = str(block.get("label") or f"Block {idx + 1}")
        options[f"{idx + 1}: {label}"] = idx
    if options:
        update_numors_block_select(shell, options, block_index)

    shell.numors_prev_block_button.disabled = shell.operation_in_progress or block_index <= 0
    shell.numors_next_block_button.disabled = (
        shell.operation_in_progress or block_index >= len(run_blocks) - 1
    )
    shell.numors_prev_plot_button.disabled = (
        shell.operation_in_progress or plot_index <= 0 or not plot_files
    )
    shell.numors_next_plot_button.disabled = (
        shell.operation_in_progress or not plot_files or plot_index >= len(plot_files) - 1
    )

    block = run_blocks[block_index] if isinstance(run_blocks[block_index], dict) else {}
    label = str(block.get("label") or f"Block {block_index + 1}")
    status = str(block.get("status") or "unknown")
    file_base = block.get("file_base")
    num_range = block.get("num")
    adat_file = block.get("adat_file")
    qdat_file = block.get("qdat_file")

    shell.numors_block_header.object = f"**{label}**"
    shell.numors_block_info_hover.object = _build_block_info_hovercard_html(
        status=status,
        file_base=file_base,
        num_range=num_range,
        adat_file=adat_file,
        qdat_file=qdat_file,
    )
    shell.numors_block_details.object = (
        f"Viewing `{block_index + 1}` / `{len(run_blocks)}`\n\n"
        f"**Plots:** `{len(plot_files)}`"
    )

    shell.numors_block_plot_container.clear()
    if plot_files:
        shell.numors_block_plot_counter.object = f"Plot `{plot_index + 1}` / `{len(plot_files)}`"
        current_plot = plot_files[plot_index]
        if Path(str(current_plot)).exists():
            shell.numors_block_plot_container.append(
                pn.pane.PNG(
                    current_plot,
                    width=720,
                    height=480,
                    sizing_mode="fixed",
                )
            )
        else:
            shell.numors_block_plot_container.append(
                pn.pane.Markdown(
                    f"Plot file not found: `{current_plot}`",
                    sizing_mode="stretch_width",
                )
            )
    else:
        shell.numors_block_plot_counter.object = "No per-block plots recorded for this run."
        shell.numors_block_plot_container.append(
            pn.pane.Markdown(
                "Rerun d4creg to capture plots per `<run>` block.",
                sizing_mode="stretch_width",
            )
        )

    shell.numors_run_blocks_card.visible = True


def _fmt_path(value: object) -> str:
    raw = str(value).strip() if value is not None else ""
    if not raw:
        return "<em>missing</em>"
    return f"<code>{escape(raw)}</code>"


def _build_block_info_hovercard_html(
    *,
    status: str,
    file_base: object,
    num_range: object,
    adat_file: object,
    qdat_file: object,
) -> str:
    out_html = _fmt_path(file_base)
    num_html = _fmt_path(num_range)
    adat_html = _fmt_path(adat_file)
    qdat_html = _fmt_path(qdat_file)

    return f"""
    <div class="toscana-hovercard toscana-hovercard--open-left" aria-label="Run block details">
      <div class="toscana-hovercard__icon" title="Run block details">ℹ</div>
      <div class="toscana-hovercard__panel">
        <div><strong>Status:</strong> <code>{escape(status)}</code></div>
        <div><strong>out:</strong> {out_html}</div>
        <div><strong>num:</strong> {num_html}</div>
        <div><strong>adat:</strong> {adat_html}</div>
        <div><strong>qdat:</strong> {qdat_html}</div>
      </div>
    </div>
    """.strip()


def on_numors_block_select_change(shell: Any, event: Any) -> None:
    if shell._suspend_numors_events or shell.current_project_state is None:
        return
    if event.new is None:
        return
    try:
        index = int(event.new)
    except (TypeError, ValueError):
        return
    blocks = latest_numors_run_blocks(shell) or []
    if not blocks:
        return
    index = max(0, min(index, len(blocks) - 1))
    state = shell._get_numors_state()
    state["selected_run_block_index"] = index
    state["selected_run_block_plot_index"] = 0
    shell._persist_numors_state(state)
    refresh_numors_run_blocks_view(shell)


def on_numors_prev_run_block(shell: Any, _event: Any = None) -> None:
    if shell.operation_in_progress or shell.current_project_state is None:
        return
    blocks = latest_numors_run_blocks(shell) or []
    if not blocks:
        return
    state = shell._get_numors_state()
    current = int(state.get("selected_run_block_index", 0))
    state["selected_run_block_index"] = max(0, current - 1)
    state["selected_run_block_plot_index"] = 0
    shell._persist_numors_state(state)
    refresh_numors_run_blocks_view(shell)


def on_numors_next_run_block(shell: Any, _event: Any = None) -> None:
    if shell.operation_in_progress or shell.current_project_state is None:
        return
    blocks = latest_numors_run_blocks(shell) or []
    if not blocks:
        return
    state = shell._get_numors_state()
    current = int(state.get("selected_run_block_index", 0))
    state["selected_run_block_index"] = min(len(blocks) - 1, current + 1)
    state["selected_run_block_plot_index"] = 0
    shell._persist_numors_state(state)
    refresh_numors_run_blocks_view(shell)


def on_numors_prev_plot(shell: Any, _event: Any = None) -> None:
    if shell.operation_in_progress or shell.current_project_state is None:
        return
    plots = latest_selected_numors_plot_files(shell)
    if not plots:
        return
    state = shell._get_numors_state()
    current = int(state.get("selected_run_block_plot_index", 0))
    state["selected_run_block_plot_index"] = max(0, current - 1)
    shell._persist_numors_state(state)
    refresh_numors_run_blocks_view(shell)


def on_numors_next_plot(shell: Any, _event: Any = None) -> None:
    if shell.operation_in_progress or shell.current_project_state is None:
        return
    plots = latest_selected_numors_plot_files(shell)
    if not plots:
        return
    state = shell._get_numors_state()
    current = int(state.get("selected_run_block_plot_index", 0))
    state["selected_run_block_plot_index"] = min(len(plots) - 1, current + 1)
    shell._persist_numors_state(state)
    refresh_numors_run_blocks_view(shell)
