from __future__ import annotations

from pathlib import Path

import panel as pn


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

                parts = [f"[{idx}] `{status}` â€” {label}"]
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

            prev_block = pn.widgets.Button(name="â—€ Prev Block", button_type="light", width=140)
            next_block = pn.widgets.Button(name="Next Block â–¶", button_type="light", width=140)
            prev_plot = pn.widgets.Button(name="â—€ Prev Plot", button_type="light", width=140)
            next_plot = pn.widgets.Button(name="Next Plot â–¶", button_type="light", width=140)

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
                viewer_state["block_index"] = max(
                    0,
                    min(viewer_state["block_index"], len(run_blocks) - 1),
                )
                block = (
                    run_blocks[viewer_state["block_index"]]
                    if isinstance(run_blocks[viewer_state["block_index"]], dict)
                    else {}
                )
                plots = block.get("plot_files", [])
                plots = plots if isinstance(plots, list) else []
                max_plot = max(len(plots) - 1, 0)
                viewer_state["plot_index"] = max(
                    0,
                    min(viewer_state["plot_index"], max_plot),
                )

            def _render_viewer() -> None:
                _clamp_state()
                block = (
                    run_blocks[viewer_state["block_index"]]
                    if isinstance(run_blocks[viewer_state["block_index"]], dict)
                    else {}
                )
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
                (
                    "run blocks",
                    pn.pane.Markdown("\n".join(block_lines), sizing_mode="stretch_width"),
                ),
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
