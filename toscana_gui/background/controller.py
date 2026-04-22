from __future__ import annotations

import json
import os
import pickle
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import panel as pn

from toscana_gui.background.tasks import (
    BACKGROUND_SOURCE_OPTIONS,
    BackgroundExtractionResult,
    BACKGROUND_SUBTRACTION_METHOD_OPTIONS,
    background_par_signature,
    background_sample_key,
    is_par_file_in_processed_parfiles,
    list_sample_par_files,
    normalize_background_state,
    validate_background_par_file,
)
from toscana_gui.paths import REPO_ROOT
from toscana_gui.persistence import OutputPaths, PARIS_TZ, RunRecord, now_iso
from toscana_gui.background.plots import build_direct_subtraction_figure, build_raw_data_figure
from toscana_gui.background.plots import (
    build_linear_combination_chi_figure,
    build_linear_combination_subtraction_figure,
)
from toscana_gui.background.tasks import _working_directory
from ntsa.experiment.measurement import Measurement
from ntsa.math.fitting import fit_and_find_extremum, get_chi
from ntsa.math.operations import binary_sum
from ntsa.math.signal_processing import smooth_curve

BACKGROUND_SUBPROCESS_WORKER = REPO_ROOT / "background_subprocess_worker.py"


class BackgroundControllerMixin:
    def _reset_background_t_controls_ui(self) -> None:
        self._suspend_background_events = True
        try:
            self.background_linear_t_mode.value = "Use computed t"
            self.background_linear_custom_t.value = 0.8
            self.background_linear_custom_t.disabled = True
            self.background_vanadium_t_mode.value = "Use computed t"
            self.background_vanadium_custom_t.value = 0.8
            self.background_vanadium_custom_t.disabled = True
        finally:
            self._suspend_background_events = False

    def _set_background_source_widget_visibility(self) -> None:
        mode = str(getattr(self.background_source_mode, "value", "") or BACKGROUND_SOURCE_OPTIONS[0])
        is_select_mode = mode == "Select File"
        if hasattr(self, "background_par_dropdown"):
            self.background_par_dropdown.visible = is_select_mode
        if hasattr(self, "background_manual_path_input"):
            self.background_manual_path_input.visible = not is_select_mode
        if is_select_mode:
            self._suspend_background_events = True
            try:
                self._refresh_background_par_dropdown_options()
            finally:
                self._suspend_background_events = False

    def _sync_background_method_cards_visibility(self) -> None:
        selected_method = str(getattr(self.background_subtraction_method, "value", "") or "")
        show_linear = selected_method == BACKGROUND_SUBTRACTION_METHOD_OPTIONS[1]
        show_monte_carlo = selected_method == BACKGROUND_SUBTRACTION_METHOD_OPTIONS[2]
        if hasattr(self, "background_linear_controls_card"):
            self.background_linear_controls_card.visible = bool(show_linear)
        if hasattr(self, "background_vanadium_controls_card"):
            self.background_vanadium_controls_card.visible = bool(show_linear)
        if hasattr(self, "background_monte_carlo_card"):
            self.background_monte_carlo_card.visible = bool(show_monte_carlo)

    def _sync_background_import_visibility(self) -> None:
        if hasattr(self, "background_import_card"):
            self.background_import_card.visible = bool(getattr(self.background_import_prompt, "visible", False))

    def _sync_background_linear_controls_from_cache(self, sample_key: str) -> None:
        if self.current_project_state is None:
            return
        state = self._get_background_state()
        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict):
            return
        entry = cached.get(sample_key)
        if not isinstance(entry, dict):
            return

        def _apply_mode_to_widgets(mode_value: str, *, mode_widget, custom_widget) -> None:
            if mode_value == "custom":
                mode_widget.value = "Use custom t"
                custom_widget.disabled = False
            else:
                mode_widget.value = "Use computed t"
                custom_widget.disabled = True

        self._suspend_background_events = True
        try:
            linear = entry.get("linear_combination")
            if isinstance(linear, dict):
                custom_t = linear.get("custom_t")
                if isinstance(custom_t, (int, float)):
                    self.background_linear_custom_t.value = float(custom_t)
                mode_value = str(linear.get("t_mode") or "computed")
                _apply_mode_to_widgets(
                    mode_value,
                    mode_widget=self.background_linear_t_mode,
                    custom_widget=self.background_linear_custom_t,
                )
            else:
                _apply_mode_to_widgets(
                    "computed",
                    mode_widget=self.background_linear_t_mode,
                    custom_widget=self.background_linear_custom_t,
                )

            vanadium = entry.get("vanadium_linear_combination")
            if isinstance(vanadium, dict):
                custom_t = vanadium.get("custom_t")
                if isinstance(custom_t, (int, float)):
                    self.background_vanadium_custom_t.value = float(custom_t)
                mode_value = str(vanadium.get("t_mode") or "computed")
                _apply_mode_to_widgets(
                    mode_value,
                    mode_widget=self.background_vanadium_t_mode,
                    custom_widget=self.background_vanadium_custom_t,
                )
            else:
                _apply_mode_to_widgets(
                    "computed",
                    mode_widget=self.background_vanadium_t_mode,
                    custom_widget=self.background_vanadium_custom_t,
                )
        finally:
            self._suspend_background_events = False

    def _persist_background_vanadium_settings(self) -> None:
        if self.current_project_state is None:
            return
        state = self._get_background_state()
        state["vanadium_linear_settings"] = {
            "t_start": float(self.background_vanadium_t_start.value),
            "t_stop": float(self.background_vanadium_t_stop.value),
            "t_step": float(self.background_vanadium_t_step.value),
            "smoothing_factor": float(self.background_vanadium_smoothing.value),
            "ignore_points": int(self.background_vanadium_ignore_points.value),
        }
        self._persist_background_state(state)

    def _on_background_vanadium_settings_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return
        self._persist_background_vanadium_settings()

    def _apply_background_vanadium_t_override(self) -> None:
        if self.current_project_state is None or self.current_project_root is None:
            return
        par_path_str = getattr(self, "_background_cached_par_path", None)
        if not par_path_str:
            return
        sample_key = background_sample_key(Path(par_path_str), self.current_project_root)
        if not sample_key:
            return
        state = self._get_background_state()
        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict):
            return
        entry = cached.get(sample_key)
        if not isinstance(entry, dict):
            return
        vanadium = entry.get("vanadium_linear_combination")
        if not isinstance(vanadium, dict):
            return

        mode = str(self.background_vanadium_t_mode.value or "Use computed t")
        best_t = vanadium.get("best_t")
        custom_t = float(self.background_vanadium_custom_t.value)
        if mode == "Use custom t":
            vanadium["t_mode"] = "custom"
            vanadium["custom_t"] = custom_t
            vanadium["effective_t"] = custom_t
            self.background_vanadium_message.object = f"Using custom t = {custom_t:.5f}"
            self.background_vanadium_message.alert_type = "warning"
        else:
            vanadium["t_mode"] = "computed"
            if isinstance(best_t, (int, float)):
                vanadium["effective_t"] = float(best_t)
                self.background_vanadium_message.object = f"Using computed t = {float(best_t):.5f}"
                self.background_vanadium_message.alert_type = "success"
            else:
                self.background_vanadium_message.object = (
                    "No computed t is available yet. Click Compute."
                )
                self.background_vanadium_message.alert_type = "danger"

        entry["vanadium_linear_combination"] = vanadium
        cached[sample_key] = entry
        self._persist_background_state(state)
        self._refresh_background_plots()
        self._refresh_interaction_states()

    def _on_background_vanadium_t_selection_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return
        mode = str(self.background_vanadium_t_mode.value or "Use computed t")
        self.background_vanadium_custom_t.disabled = mode != "Use custom t"
        self._apply_background_vanadium_t_override()

    def _compute_background_vanadium_linear_combination(self, _event=None) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return

        measurement = self._load_latest_measurement()
        if measurement is None:
            self.background_vanadium_message.object = "Extract a sample measurement first."
            self.background_vanadium_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        if self.current_project_root is None:
            self.background_vanadium_message.object = "Open a project first."
            self.background_vanadium_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        state = self._get_background_state()
        self._persist_background_vanadium_settings()
        settings = dict(state.get("vanadium_linear_settings") or {})
        try:
            result = self._run_vanadium_linear_combination(measurement, settings=settings)
        except Exception as exc:
            self.background_vanadium_message.object = f"Vanadium background computation failed: {exc}"
            self.background_vanadium_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        par_path_str = getattr(self, "_background_cached_par_path", None)
        if not par_path_str:
            par_path_str = str(state.get("validation", {}).get("selected_par_path") or "").strip()
        sample_key = background_sample_key(Path(par_path_str), self.current_project_root) if par_path_str else None
        if not sample_key:
            self.background_vanadium_message.object = "Could not determine which sample `.par` this result belongs to."
            self.background_vanadium_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict) or sample_key not in cached:
            self.background_vanadium_message.object = "This sample is not present in the extraction cache yet."
            self.background_vanadium_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        cached_entry = cached.get(sample_key, {})
        if not isinstance(cached_entry, dict):
            cached_entry = {}

        best_t = result.get("best_t")
        mode = "computed"
        effective_t = best_t
        custom_t = float(getattr(self.background_vanadium_custom_t, "value", 0.8))
        if isinstance(best_t, float) and (best_t < 0.0 or best_t > 1.0):
            mode = "custom"
            effective_t = custom_t
        result["t_mode"] = mode
        result["custom_t"] = custom_t
        if isinstance(effective_t, (int, float)):
            result["effective_t"] = float(effective_t)

        cached_entry["vanadium_linear_combination"] = result
        cached[sample_key] = cached_entry
        self._persist_background_state(state)

        self._suspend_background_events = True
        if mode == "custom":
            self.background_vanadium_t_mode.value = "Use custom t"
            self.background_vanadium_custom_t.disabled = False
        else:
            self.background_vanadium_t_mode.value = "Use computed t"
            self.background_vanadium_custom_t.disabled = True
        self._suspend_background_events = False

        if isinstance(best_t, float) and mode == "custom":
            self.background_vanadium_message.object = (
                f"Computed best t = {best_t:.5f} (outside [0, 1]). "
                f"Using custom t = {custom_t:.5f} by default."
            )
            self.background_vanadium_message.alert_type = "warning"
        elif isinstance(best_t, float):
            self.background_vanadium_message.object = f"Computed best t = {best_t:.5f}"
            self.background_vanadium_message.alert_type = "success"
        else:
            self.background_vanadium_message.object = "Computed best t."
            self.background_vanadium_message.alert_type = "success"
        self._refresh_interaction_states()

    def _run_vanadium_linear_combination(self, measurement, *, settings: dict) -> dict:
        vanadium = getattr(measurement, "norData", None)
        environment = getattr(measurement, "envData", None)
        if vanadium is None or environment is None:
            raise ValueError("Vanadium and Environment data are required for Vanadium background computation.")

        t_start = float(settings.get("t_start", -1.0))
        t_stop = float(settings.get("t_stop", 2.0))
        t_step = float(settings.get("t_step", 0.05))
        smoothing_factor = float(settings.get("smoothing_factor", 0.01))
        ignore_points = int(settings.get("ignore_points", 25))
        if t_step <= 0:
            raise ValueError("t step must be > 0.")
        if t_stop <= t_start:
            raise ValueError("t stop must be greater than t start.")
        if ignore_points < 0:
            raise ValueError("Ignore points must be >= 0.")

        trans_arr = np.arange(t_start, t_stop, t_step, dtype=float)
        if trans_arr.size < 3:
            raise ValueError("t range must include at least 3 values.")

        x_v = np.asarray(vanadium)[:, 0]
        y_v = np.asarray(vanadium)[:, 1]
        x_env = np.asarray(environment)[:, 0]
        y_env = np.asarray(environment)[:, 1]
        if y_v.shape != y_env.shape:
            raise ValueError("Vanadium and environment arrays must have the same length.")
        if not np.array_equal(x_v, x_env):
            raise ValueError("Vanadium and environment x-grids do not match.")

        chi_values: list[float] = []
        for t in trans_arr.tolist():
            background_y = float(t) * y_env
            y = y_v - background_y
            smooth_y = smooth_curve(x_v, y, smoothing_factor)
            start_idx = min(ignore_points, len(y))
            chi_values.append(get_chi(y[start_idx:], smooth_y[start_idx:]))

        try:
            extremum_x, _extremum_y, fitted = fit_and_find_extremum(trans_arr, chi_values)
            best_t = float(extremum_x[0])
        except Exception:
            fitted = np.asarray([], dtype=float)
            best_t = float(trans_arr[int(np.argmin(np.asarray(chi_values, dtype=float)))])

        if not np.isfinite(best_t):
            best_t = float(trans_arr[int(np.argmin(np.asarray(chi_values, dtype=float)))])

        return {
            "trans": [float(v) for v in trans_arr.tolist()],
            "chi": [float(v) for v in chi_values],
            "fitted": [float(v) for v in fitted.tolist()] if getattr(fitted, "size", 0) else [],
            "best_t": float(best_t),
            "computed_at": now_iso(),
            "settings": {
                "t_start": t_start,
                "t_stop": t_stop,
                "t_step": t_step,
                "smoothing_factor": smoothing_factor,
                "ignore_points": ignore_points,
            },
        }

    def _get_background_state(self) -> dict:
        if self.current_project_state is None:
            return normalize_background_state(None)
        normalized = normalize_background_state(getattr(self.current_project_state, "background", None))
        self.current_project_state.background = normalized
        return normalized

    def _persist_background_state(self, state: dict | None = None) -> None:
        if self.current_project_state is None:
            return
        self.current_project_state.background = normalize_background_state(
            self._get_background_state() if state is None else state
        )
        self.current_project_state.project.updated_at = now_iso()
        self._persist_current_project_state()

    def _refresh_background_par_dropdown_options(self) -> None:
        if self.current_project_root is None:
            self.background_par_dropdown.options = {"Open a project first.": ""}
            self.background_par_dropdown.value = ""
            return

        sample_pars = list_sample_par_files(self.current_project_root)
        if not sample_pars:
            self.background_par_dropdown.options = {"No sample `.par` files found in processed/parfiles/.": ""}
            self.background_par_dropdown.value = ""
            return

        options = {par_path.name: str(par_path.resolve(strict=False)) for par_path in sample_pars}
        self.background_par_dropdown.options = options

        state = self._get_background_state()
        remembered = str(state.get("selected_par_path") or "").strip()
        if remembered and remembered in options.values():
            selected_value = remembered
        else:
            selected_value = next(iter(options.values()))

        self.background_par_dropdown.value = selected_value
        self.background_manual_path_input.value = selected_value
        if selected_value and selected_value != remembered:
            self._set_background_selected_path(selected_value)

    def _load_background_state_into_widgets(self) -> None:
        if self.current_project_state is None:
            return

        state = self._get_background_state()
        self._suspend_background_events = True
        self.background_source_mode.value = state["source_mode"]
        self.background_manual_path_input.value = str(state.get("selected_par_path") or "")
        self.background_error_bars_toggle.value = bool(state.get("error_bars_enabled", False))
        self.background_subtraction_method.value = state.get(
            "subtraction_method",
            BACKGROUND_SUBTRACTION_METHOD_OPTIONS[0],
        )
        linear_settings = state.get("linear_combination") if isinstance(state.get("linear_combination"), dict) else {}
        self.background_linear_t_start.value = float(linear_settings.get("t_start", -1.0))
        self.background_linear_t_stop.value = float(linear_settings.get("t_stop", 2.0))
        self.background_linear_t_step.value = float(linear_settings.get("t_step", 0.05))
        self.background_linear_smoothing.value = float(linear_settings.get("smoothing_factor", 0.01))
        self.background_linear_ignore_points.value = int(linear_settings.get("ignore_points", 25))
        self.background_linear_custom_t.value = 0.8
        self.background_linear_t_mode.value = "Use computed t"
        self.background_linear_custom_t.disabled = True
        vanadium_settings = (
            state.get("vanadium_linear_settings")
            if isinstance(state.get("vanadium_linear_settings"), dict)
            else {}
        )
        self.background_vanadium_t_start.value = float(vanadium_settings.get("t_start", -1.0))
        self.background_vanadium_t_stop.value = float(vanadium_settings.get("t_stop", 2.0))
        self.background_vanadium_t_step.value = float(vanadium_settings.get("t_step", 0.05))
        self.background_vanadium_smoothing.value = float(vanadium_settings.get("smoothing_factor", 0.01))
        self.background_vanadium_ignore_points.value = int(vanadium_settings.get("ignore_points", 25))
        self.background_vanadium_custom_t.value = 0.8
        self.background_vanadium_t_mode.value = "Use computed t"
        self.background_vanadium_custom_t.disabled = True
        self._refresh_background_par_dropdown_options()
        self._suspend_background_events = False
        self._set_background_source_widget_visibility()
        self._sync_background_method_cards_visibility()
        self._sync_background_import_visibility()

        self._pending_background_import_path = None
        self.background_import_prompt.visible = False

        selected = str(self._get_background_state().get("selected_par_path") or "").strip()
        if selected and self.current_project_root is not None:
            self._apply_cached_background_measurement(
                Path(selected),
                update_message=False,
                refresh_plots=False,
            )

        state = self._get_background_state()
        validation_state = state["validation"]
        self.background_extract_button.disabled = not bool(validation_state.get("is_valid", False))

        if validation_state.get("is_valid"):
            self.background_message.object = ""
            self.background_message.alert_type = "secondary"
            self.background_message.visible = False
        elif state.get("selected_par_path"):
            self.background_message.object = (
                validation_state.get("error")
                or "The remembered sample `.par` selection needs validation."
            )
            self.background_message.alert_type = "warning"
            self.background_message.visible = True
        else:
            self.background_message.object = "Select a sample `.par` file to get started."
            self.background_message.alert_type = "secondary"
            self.background_message.visible = True

    def _on_background_subtraction_method_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return

        state = self._get_background_state()
        if event.new in BACKGROUND_SUBTRACTION_METHOD_OPTIONS:
            state["subtraction_method"] = event.new
            self._persist_background_state(state)

        self._refresh_background_plots()
        self._sync_background_method_cards_visibility()
        self._refresh_interaction_states()

    def _on_background_error_bars_toggle(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return
        state = self._get_background_state()
        state["error_bars_enabled"] = bool(event.new)
        self._persist_background_state(state)
        self._refresh_background_plots()

    def _apply_cached_background_measurement(
        self,
        selected_par_path: Path,
        *,
        update_message: bool,
        refresh_plots: bool = True,
    ) -> bool:
        if self.current_project_state is None or self.current_project_root is None:
            return False

        state = self._get_background_state()
        sample_key = background_sample_key(selected_par_path, self.current_project_root)
        if not sample_key:
            return False

        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict):
            return False

        entry = cached.get(sample_key)
        if not isinstance(entry, dict):
            return False

        artifact = entry.get("measurement_artifact")
        if not isinstance(artifact, str) or not artifact.strip():
            return False

        try:
            artifact_path = Path(artifact).expanduser()
        except (TypeError, ValueError):
            return False
        if not artifact_path.is_absolute():
            artifact_path = self.current_project_root / artifact_path
        artifact_path = artifact_path.resolve(strict=False)
        if not artifact_path.exists() or not artifact_path.is_file():
            return False

        stale = False
        signature = background_par_signature(selected_par_path)
        stored_mtime = entry.get("par_mtime")
        stored_size = entry.get("par_size")
        if signature is None:
            stale = True
        elif isinstance(stored_mtime, (int, float)) and isinstance(stored_size, int):
            stale = (float(stored_mtime) != signature[0]) or (int(stored_size) != signature[1])

        try:
            artifact_for_state = artifact_path.relative_to(self.current_project_root).as_posix()
        except Exception:
            artifact_for_state = str(artifact_path)

        state["latest_measurement_artifact"] = artifact_for_state
        state["validation"]["selected_par_path"] = str(selected_par_path.resolve(strict=False))
        if signature is None:
            state["validation"]["file_accessible"] = False
            state["validation"]["is_valid"] = False
            state["validation"]["error"] = "Sample `.par` file is missing."
        else:
            state["validation"]["file_accessible"] = True
            state["validation"]["is_valid"] = True
            state["validation"]["error"] = None
        self._persist_background_state(state)
        self._sync_background_import_visibility()
        self._sync_background_method_cards_visibility()
        if refresh_plots:
            self._refresh_background_plots()
        self.background_extract_button.disabled = signature is None
        self._sync_background_linear_controls_from_cache(sample_key)
        self._refresh_interaction_states()

        if update_message:
            if signature is None:
                self.background_message.object = (
                    "Loaded cached extraction, but the sample `.par` file is missing. "
                    "Re-extract is unavailable until the file is restored."
                )
                self.background_message.alert_type = "warning"
            elif stale:
                self.background_message.object = (
                    "Loaded cached extraction. The `.par` file has changed since extraction; "
                    "re-extract is recommended."
                )
                self.background_message.alert_type = "warning"
            else:
                self.background_message.object = "Loaded cached extraction for this sample."
                self.background_message.alert_type = "success"

        return True

    def _load_latest_measurement(self):
        state = self._get_background_state()
        artifact = state.get("latest_measurement_artifact")
        if not artifact:
            return None
        artifact_str = str(artifact)
        try:
            path = Path(artifact_str).expanduser()
        except (TypeError, ValueError):
            return None
        if not path.is_absolute() and self.current_project_root is not None:
            path = (self.current_project_root / path).resolve(strict=False)
        if not path.exists() or not path.is_file():
            return None

        try:
            mtime = path.stat().st_mtime
        except Exception:
            mtime = None

        cached_path = getattr(self, "_background_cached_artifact_path", None)
        cached_mtime = getattr(self, "_background_cached_artifact_mtime", None)
        cached_measurement = getattr(self, "_background_cached_measurement", None)
        if cached_measurement is not None and cached_path == artifact_str and cached_mtime == mtime:
            return cached_measurement

        measurement = None
        par_filename: str | None = None
        par_path_str: str | None = None
        try:
            if path.suffix.lower() == ".pkl":
                with path.open("rb") as handle:
                    measurement = pickle.load(handle)
            else:
                payload = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(payload, dict):
                    return None
                par_path = None
                try:
                    par_path = payload.get("<par>")[1]
                except Exception:
                    par_path = None
                if par_path:
                    try:
                        par_filename = Path(str(par_path)).name
                        par_path_str = str(par_path)
                    except Exception:
                        par_filename = None
                base_dir = Path(str(par_path)).expanduser().parent if par_path else path.parent
                with _working_directory(base_dir):
                    measurement = Measurement(payload)
        except Exception:
            measurement = None

        self._background_cached_artifact_path = artifact_str
        self._background_cached_artifact_mtime = mtime
        self._background_cached_measurement = measurement
        self._background_cached_par_filename = par_filename
        self._background_cached_par_path = par_path_str
        return measurement

    def _on_background_linear_settings_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return
        self._persist_background_linear_settings()
        self.background_linear_message.object = "Settings updated. Click **Compute Linear Combination** to refresh."
        self.background_linear_message.alert_type = "secondary"
        self._refresh_interaction_states()

    def _on_background_linear_t_selection_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return

        mode = str(self.background_linear_t_mode.value or "Use computed t")
        self.background_linear_custom_t.disabled = mode != "Use custom t"
        self._apply_background_linear_t_override()

    def _persist_background_linear_settings(self) -> None:
        if self.current_project_state is None:
            return
        state = self._get_background_state()
        state["linear_combination"] = {
            "t_start": float(self.background_linear_t_start.value),
            "t_stop": float(self.background_linear_t_stop.value),
            "t_step": float(self.background_linear_t_step.value),
            "smoothing_factor": float(self.background_linear_smoothing.value),
            "ignore_points": int(self.background_linear_ignore_points.value),
        }
        self._persist_background_state(state)

    def _apply_background_linear_t_override(self) -> None:
        if self.current_project_state is None or self.current_project_root is None:
            return
        par_path_str = getattr(self, "_background_cached_par_path", None)
        if not par_path_str:
            return
        sample_key = background_sample_key(Path(par_path_str), self.current_project_root)
        if not sample_key:
            return
        state = self._get_background_state()
        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict):
            return
        entry = cached.get(sample_key)
        if not isinstance(entry, dict):
            return
        linear = entry.get("linear_combination")
        if not isinstance(linear, dict):
            return

        mode = str(self.background_linear_t_mode.value or "Use computed t")
        best_t = linear.get("best_t")
        custom_t = float(self.background_linear_custom_t.value)
        if mode == "Use custom t":
            linear["t_mode"] = "custom"
            linear["custom_t"] = custom_t
            linear["effective_t"] = custom_t
            self.background_linear_message.object = f"Using custom t = {custom_t:.5f}"
            self.background_linear_message.alert_type = "warning"
        else:
            linear["t_mode"] = "computed"
            if isinstance(best_t, (int, float)):
                linear["effective_t"] = float(best_t)
                self.background_linear_message.object = f"Using computed t = {float(best_t):.5f}"
                self.background_linear_message.alert_type = "success"
            else:
                self.background_linear_message.object = "No computed t is available yet. Click Compute."
                self.background_linear_message.alert_type = "danger"

        entry["linear_combination"] = linear
        cached[sample_key] = entry
        self._persist_background_state(state)
        self._refresh_background_plots()
        self._refresh_interaction_states()

    def _compute_background_linear_combination(self, _event=None) -> None:
        if self.operation_in_progress:
            self._show_workspace_blocked_message()
            return
        if self.current_project_state is None or self.current_project_root is None:
            return

        measurement = self._load_latest_measurement()
        if measurement is None:
            self.background_linear_message.object = "Extract a sample measurement first."
            self.background_linear_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        self._persist_background_linear_settings()
        state = self._get_background_state()
        settings = dict(state.get("linear_combination") or {})

        try:
            result = self._run_linear_combination(measurement, settings=settings)
        except Exception as exc:
            self.background_linear_message.object = f"Linear combination failed: {exc}"
            self.background_linear_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        par_path_str = getattr(self, "_background_cached_par_path", None)
        if not par_path_str:
            par_path_str = str(state.get("validation", {}).get("selected_par_path") or "").strip()
        sample_key = background_sample_key(Path(par_path_str), self.current_project_root) if par_path_str else None
        if not sample_key:
            self.background_linear_message.object = "Could not determine which sample `.par` this result belongs to."
            self.background_linear_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict) or sample_key not in cached:
            self.background_linear_message.object = "This sample is not present in the extraction cache yet."
            self.background_linear_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        cached_entry = cached.get(sample_key, {})
        if not isinstance(cached_entry, dict):
            cached_entry = {}

        best_t = result.get("best_t")
        mode = "computed"
        effective_t = best_t
        custom_t = float(getattr(self.background_linear_custom_t, "value", 0.8))
        if isinstance(best_t, float) and (best_t < 0.0 or best_t > 1.0):
            mode = "custom"
            effective_t = custom_t
        result["t_mode"] = mode
        result["custom_t"] = custom_t
        if isinstance(effective_t, (int, float)):
            result["effective_t"] = float(effective_t)

        cached_entry["linear_combination"] = result
        cached[sample_key] = cached_entry
        self._persist_background_state(state)

        self._suspend_background_events = True
        if mode == "custom":
            self.background_linear_t_mode.value = "Use custom t"
            self.background_linear_custom_t.disabled = False
        else:
            self.background_linear_t_mode.value = "Use computed t"
            self.background_linear_custom_t.disabled = True
        self._suspend_background_events = False

        if isinstance(best_t, float) and mode == "custom":
            self.background_linear_message.object = (
                f"Computed best t = {best_t:.5f} (outside [0, 1]). "
                f"Using custom t = {custom_t:.5f} by default."
            )
            self.background_linear_message.alert_type = "warning"
        elif isinstance(best_t, float):
            self.background_linear_message.object = f"Computed best t = {best_t:.5f}"
            self.background_linear_message.alert_type = "success"
        else:
            self.background_linear_message.object = "Computed best t."
            self.background_linear_message.alert_type = "success"
        self._refresh_background_plots()
        self._sync_background_linear_controls_from_cache(sample_key)
        self._refresh_interaction_states()

    def _run_linear_combination(self, measurement, *, settings: dict) -> dict:
        data = getattr(measurement, "Data", None)
        container = getattr(measurement, "conData", None)
        environment = getattr(measurement, "envData", None)
        if data is None or container is None or environment is None:
            raise ValueError("Sample, Container, and Environment data are required for Linear Combination.")

        t_start = float(settings.get("t_start", -1.0))
        t_stop = float(settings.get("t_stop", 2.0))
        t_step = float(settings.get("t_step", 0.05))
        smoothing_factor = float(settings.get("smoothing_factor", 0.01))
        ignore_points = int(settings.get("ignore_points", 25))
        if t_step <= 0:
            raise ValueError("t step must be > 0.")
        if t_stop <= t_start:
            raise ValueError("t stop must be greater than t start.")
        if ignore_points < 0:
            raise ValueError("Ignore points must be >= 0.")

        trans_arr = np.arange(t_start, t_stop, t_step, dtype=float)
        if trans_arr.size < 3:
            raise ValueError("t range must include at least 3 values.")

        x = np.asarray(data)[:, 0]
        y_sample = np.asarray(data)[:, 1]
        y_con = np.asarray(container)[:, 1]
        y_env = np.asarray(environment)[:, 1]
        if y_con.shape != y_env.shape or y_sample.shape != y_con.shape:
            raise ValueError("Sample, container, and environment arrays must have the same length.")

        chi_values: list[float] = []
        for t in trans_arr.tolist():
            background_y = float(t) * y_con + (1.0 - float(t)) * y_env
            y = y_sample - background_y
            smooth_y = smooth_curve(x, y, smoothing_factor)
            start_idx = min(ignore_points, len(y))
            chi_values.append(get_chi(y[start_idx:], smooth_y[start_idx:]))

        try:
            extremum_x, _extremum_y, fitted = fit_and_find_extremum(trans_arr, chi_values)
            best_t = float(extremum_x[0])
        except Exception:
            fitted = np.asarray([], dtype=float)
            best_t = float(trans_arr[int(np.argmin(np.asarray(chi_values, dtype=float)))])

        if not np.isfinite(best_t):
            best_t = float(trans_arr[int(np.argmin(np.asarray(chi_values, dtype=float)))])

        return {
            "trans": [float(v) for v in trans_arr.tolist()],
            "chi": [float(v) for v in chi_values],
            "fitted": [float(v) for v in fitted.tolist()] if getattr(fitted, "size", 0) else [],
            "best_t": float(best_t),
            "computed_at": now_iso(),
            "settings": {
                "t_start": t_start,
                "t_stop": t_stop,
                "t_step": t_step,
                "smoothing_factor": smoothing_factor,
                "ignore_points": ignore_points,
            },
        }

    def _set_background_plot_visibility(
        self,
        *,
        has_measurement: bool,
        show_direct_subtraction: bool,
        show_linear_combination: bool,
        raw_ok: bool,
        subtraction_ok: bool,
    ) -> None:
        self.background_no_data_pane.visible = not has_measurement
        self.background_plot_options_card.visible = has_measurement
        self.background_raw_plot_card.visible = has_measurement and raw_ok
        self.background_raw_plot_alert.visible = has_measurement and not raw_ok
        self.background_subtraction_plot_card.visible = has_measurement and show_direct_subtraction and subtraction_ok
        self.background_subtraction_plot_alert.visible = has_measurement and show_direct_subtraction and not subtraction_ok
        if hasattr(self, "background_linear_chi_plot_pane"):
            self.background_linear_chi_plot_pane.visible = has_measurement and show_linear_combination
        if hasattr(self, "background_linear_subtraction_plot_pane"):
            self.background_linear_subtraction_plot_pane.visible = has_measurement and show_linear_combination

    def _refresh_background_plots(self) -> None:
        if self.current_project_state is None:
            return

        measurement = self._load_latest_measurement()
        if measurement is None:
            self.background_raw_plot_pane.object = None
            self.background_subtraction_plot_pane.object = None
            self.background_raw_plot_alert.object = ""
            self.background_subtraction_plot_alert.object = ""
            self._set_background_plot_visibility(
                has_measurement=False,
                show_direct_subtraction=False,
                show_linear_combination=False,
                raw_ok=False,
                subtraction_ok=False,
            )
            self._sync_background_method_cards_visibility()
            return

        show_error_bars = bool(self.background_error_bars_toggle.value)
        selected_method = str(
            getattr(self, "background_subtraction_method", None).value
            if hasattr(self, "background_subtraction_method")
            else self._get_background_state().get("subtraction_method", BACKGROUND_SUBTRACTION_METHOD_OPTIONS[0])
        )
        show_direct_subtraction = selected_method == BACKGROUND_SUBTRACTION_METHOD_OPTIONS[0]
        show_linear_combination = selected_method == BACKGROUND_SUBTRACTION_METHOD_OPTIONS[1]
        self._sync_background_method_cards_visibility()
        raw_title = getattr(self, "_background_cached_par_filename", None)

        raw_ok = True
        try:
            self.background_raw_plot_pane.object = build_raw_data_figure(
                measurement,
                show_error_bars=show_error_bars,
                title=raw_title,
            )
            self.background_raw_plot_alert.object = ""
        except Exception as exc:
            raw_ok = False
            self.background_raw_plot_pane.object = None
            self.background_raw_plot_alert.object = f"Could not build raw data plot: {exc}"

        subtraction_ok = True
        if show_direct_subtraction:
            try:
                self.background_subtraction_plot_pane.object = build_direct_subtraction_figure(
                    measurement,
                    show_error_bars=show_error_bars,
                )
                self.background_subtraction_plot_alert.object = ""
            except Exception as exc:
                subtraction_ok = False
                self.background_subtraction_plot_pane.object = None
                self.background_subtraction_plot_alert.object = f"Could not build subtraction plot: {exc}"
        else:
            self.background_subtraction_plot_pane.object = None
            self.background_subtraction_plot_alert.object = ""
            subtraction_ok = True

        if show_linear_combination:
            self._refresh_background_linear_combination_plots(measurement, show_error_bars=show_error_bars)
        else:
            self.background_linear_chi_plot_pane.object = None
            self.background_linear_subtraction_plot_pane.object = None

        self._set_background_plot_visibility(
            has_measurement=True,
            show_direct_subtraction=show_direct_subtraction,
            show_linear_combination=show_linear_combination,
            raw_ok=raw_ok,
            subtraction_ok=subtraction_ok,
        )

    def _refresh_background_linear_combination_plots(self, measurement, *, show_error_bars: bool) -> None:
        if self.current_project_state is None or self.current_project_root is None:
            return
        state = self._get_background_state()
        par_path_str = getattr(self, "_background_cached_par_path", None)
        if not par_path_str:
            return
        sample_key = background_sample_key(Path(par_path_str), self.current_project_root)
        if not sample_key:
            return
        cached = state.get("measurements_by_par")
        if not isinstance(cached, dict):
            return
        entry = cached.get(sample_key)
        if not isinstance(entry, dict):
            return
        linear = entry.get("linear_combination")
        if not isinstance(linear, dict):
            self.background_linear_message.object = "No linear-combination result for this sample yet. Click Compute."
            self.background_linear_message.alert_type = "secondary"
            return

        trans = list(linear.get("trans") or [])
        chi = list(linear.get("chi") or [])
        fitted = list(linear.get("fitted") or [])
        best_t = linear.get("best_t")
        best_t_val = float(best_t) if isinstance(best_t, (int, float)) else None
        effective_t_raw = linear.get("effective_t", best_t_val)
        effective_t_val = float(effective_t_raw) if isinstance(effective_t_raw, (int, float)) else None
        t_mode = linear.get("t_mode")
        custom_t_raw = linear.get("custom_t", 0.8)
        custom_t_val = float(custom_t_raw) if isinstance(custom_t_raw, (int, float)) else 0.8

        self._suspend_background_events = True
        if t_mode == "custom":
            self.background_linear_t_mode.value = "Use custom t"
            self.background_linear_custom_t.disabled = False
            self.background_linear_custom_t.value = custom_t_val
        else:
            self.background_linear_t_mode.value = "Use computed t"
            self.background_linear_custom_t.disabled = True
            self.background_linear_custom_t.value = custom_t_val
        self._suspend_background_events = False

        self.background_linear_chi_plot_pane.object = build_linear_combination_chi_figure(
            trans,
            chi,
            fitted,
            best_t=best_t_val,
            effective_t=effective_t_val,
        )

        data = getattr(measurement, "Data", None)
        container = getattr(measurement, "conData", None)
        environment = getattr(measurement, "envData", None)
        if data is None or container is None or environment is None or effective_t_val is None:
            return
        dat = np.asarray(data)
        con = np.asarray(container)
        env = np.asarray(environment)
        if dat.ndim != 2 or con.ndim != 2 or env.ndim != 2:
            return
        if dat.shape[0] != con.shape[0] or dat.shape[0] != env.shape[0]:
            return

        x = dat[:, 0]
        sample_y = dat[:, 1]
        if con.shape[1] >= 2 and env.shape[1] >= 2:
            background_y = effective_t_val * con[:, 1] + (1.0 - effective_t_val) * env[:, 1]
        else:
            return
        subtracted_y = sample_y - background_y
        direct_sub_y = sample_y - con[:, 1]

        error_y = None
        if show_error_bars and dat.shape[1] >= 3 and con.shape[1] >= 3 and env.shape[1] >= 3:
            bckgt = binary_sum(effective_t_val, con, 1.0 - effective_t_val, env)
            subt = binary_sum(1.0, dat, -1.0, bckgt) if bckgt is not None else None
            if subt is not None and subt.shape[1] >= 3:
                subtracted_y = subt[:, 1]
                error_y = subt[:, 2]
            if bckgt is not None:
                background_y = bckgt[:, 1]
            direct = binary_sum(1.0, dat, -1.0, con)
            if direct is not None:
                direct_sub_y = direct[:, 1]

        title = f"Linear Combination (t = {effective_t_val:.2f})"
        self.background_linear_subtraction_plot_pane.object = build_linear_combination_subtraction_figure(
            x=x,
            sample_y=sample_y,
            background_y=background_y,
            subtracted_y=subtracted_y,
            direct_subtracted_y=direct_sub_y,
            title=title,
            error_y=error_y,
        )

    def _set_background_selected_path(self, path: str) -> None:
        if self.current_project_state is None:
            return
        state = self._get_background_state()
        state["selected_par_path"] = str(path or "").strip()
        state["validation"]["is_valid"] = False
        state["validation"]["selected_par_path"] = str(path or "").strip()
        state["validation"]["file_accessible"] = False
        state["validation"]["error"] = None
        self._persist_background_state(state)

    def _on_background_source_mode_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or event.new == event.old:
            return
        self._clear_background_import_prompt()
        state = self._get_background_state()
        state["source_mode"] = event.new
        self._persist_background_state(state)
        self.background_message.object = "Input mode changed. Choose a sample `.par` file."
        self.background_message.alert_type = "secondary"
        self.background_extract_button.disabled = True
        self._set_background_source_widget_visibility()
        self._sync_background_import_visibility()
        self._refresh_interaction_states()

    def _on_background_par_dropdown_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return
        self._clear_background_import_prompt()
        selected_path = str(event.new or "").strip()
        self.background_manual_path_input.value = selected_path
        self._set_background_selected_path(selected_path)
        if selected_path and self._apply_cached_background_measurement(Path(selected_path), update_message=True):
            return
        self._reset_background_t_controls_ui()

        self.background_message.object = "Selection changed. Validate it to continue."
        self.background_message.alert_type = "secondary"
        self.background_extract_button.disabled = True
        self._sync_background_import_visibility()
        self._refresh_interaction_states()

    def _on_background_manual_path_change(self, event) -> None:
        if getattr(self, "_suspend_background_events", False) or self.current_project_state is None:
            return
        if event.new == event.old:
            return
        self._clear_background_import_prompt()
        selected_path = str(event.new or "").strip()
        self._set_background_selected_path(selected_path)
        if selected_path and self.current_project_root is not None:
            if self._apply_cached_background_measurement(Path(selected_path), update_message=True):
                return
        self._reset_background_t_controls_ui()

        self.background_message.object = "Path changed. Validate it to continue."
        self.background_message.alert_type = "secondary"
        self.background_extract_button.disabled = True
        self._sync_background_import_visibility()
        self._refresh_interaction_states()

    def _get_background_candidate_path(self) -> Path | None:
        if self.background_source_mode.value == "Select File":
            candidate = str(self.background_par_dropdown.value or "").strip()
            if not candidate:
                return None
            return Path(candidate).expanduser()

        candidate = str(self.background_manual_path_input.value or "").strip()
        if not candidate:
            return None
        return Path(candidate).expanduser()

    def _validate_background_selection(self, _event=None) -> None:
        if self.operation_in_progress:
            self._show_workspace_blocked_message()
            return
        if self.current_project_root is None or self.current_project_state is None:
            return

        candidate_path = self._get_background_candidate_path()
        if candidate_path is None:
            self.background_message.object = "Select a sample `.par` file path first."
            self.background_message.alert_type = "danger"
            self._refresh_interaction_states()
            return

        self.background_manual_path_input.value = str(candidate_path)
        self._set_background_selected_path(str(candidate_path))

        if not is_par_file_in_processed_parfiles(candidate_path, self.current_project_root):
            self._prompt_background_import(candidate_path)
            self._sync_background_import_visibility()
            self._refresh_interaction_states()
            return

        self._clear_background_import_prompt()
        self._apply_background_validation(candidate_path)
        self._sync_background_import_visibility()
        self._refresh_interaction_states()

    def _apply_background_validation(self, par_file: Path) -> None:
        validation_result = validate_background_par_file(par_file)
        state = self._get_background_state()
        state["selected_par_path"] = str(par_file.resolve(strict=False))
        state["validation"] = validation_result.to_state()
        self._persist_background_state(state)

        self.background_extract_button.disabled = not validation_result.is_valid
        if validation_result.is_valid:
            self.background_message.object = ""
            self.background_message.alert_type = "secondary"
            self.background_message.visible = False
            self._show_success_toast("Selected sample `.par` file is ready to extract.")
            return

        self.background_message.object = validation_result.error or "Validation failed."
        self.background_message.alert_type = "danger"
        self.background_message.visible = True

    def _prompt_background_import(self, candidate_path: Path) -> None:
        self._pending_background_import_path = candidate_path.resolve(strict=False)
        self.background_import_prompt.object = (
            "The selected `.par` file is outside `processed/parfiles/`. "
            "Copy it into `processed/parfiles/` to continue."
        )
        self.background_import_prompt.alert_type = "warning"
        self.background_import_prompt.visible = True
        self._sync_background_import_visibility()
        self.background_message.object = (
            "Copy the selected `.par` file into the project to validate it."
        )
        self.background_message.alert_type = "warning"
        self.background_extract_button.disabled = True

    def _clear_background_import_prompt(self) -> None:
        self._pending_background_import_path = None
        self.background_import_prompt.visible = False
        self.background_import_prompt.object = ""
        self.background_import_prompt.alert_type = "warning"
        self._sync_background_import_visibility()

    def _cancel_background_import(self, _event=None) -> None:
        self._clear_background_import_prompt()
        self.background_message.object = "Import cancelled."
        self.background_message.alert_type = "secondary"
        self._refresh_interaction_states()

    def _copy_background_file_into_project(self, _event=None) -> None:
        if self.operation_in_progress:
            self._show_workspace_blocked_message()
            return
        if self.current_project_root is None or self._pending_background_import_path is None:
            return

        source_path = self._pending_background_import_path
        target_dir = self.current_project_root / "processed" / "parfiles"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / source_path.name
        if target_path.exists():
            self.background_message.object = (
                "A `.par` file with the same name already exists in `processed/parfiles/`. "
                "Rename the source file manually and try again."
            )
            self.background_message.alert_type = "danger"
            self.background_import_prompt.alert_type = "danger"
            self.background_import_prompt.object = (
                "Import blocked because a file with the same name already exists."
            )
            self.background_import_prompt.visible = True
            self._render_current_screen()
            return

        from shutil import copy2

        copy2(source_path, target_path)
        self._clear_background_import_prompt()
        self.background_manual_path_input.value = str(target_path)
        self._set_background_selected_path(str(target_path))
        self._refresh_background_par_dropdown_options()
        self._apply_background_validation(target_path)
        self._show_success_toast("Parameter file copied into the project.")

    def _notify_background_extraction_pending(self, _event=None) -> None:
        if self.operation_in_progress:
            self._show_workspace_blocked_message()
            return
        if self.background_extract_button.disabled:
            return
        self._start_background_extraction()

    def _start_background_extraction(self) -> None:
        if self.current_project_root is None or self.current_project_state is None:
            return

        validation_state = self._get_background_state()["validation"]
        selected_par_path = validation_state.get("selected_par_path")
        if not validation_state.get("is_valid") or not selected_par_path:
            self.background_message.object = "Validate a sample `.par` file before extracting."
            self.background_message.alert_type = "danger"
            self._render_current_screen()
            return

        run_id = self._create_run_id()
        stdout_file = self.current_project_root / "processed" / "logfiles" / f"{run_id}-stdout.txt"
        run_record = RunRecord(
            run_id=run_id,
            workflow="background_extract",
            status="running",
            started_at=now_iso(),
            summary=f"Extracting `{Path(selected_par_path).name}`",
            workflow_data={"par_file": str(Path(selected_par_path).resolve(strict=False))},
            output_paths=OutputPaths(stdout_file=str(stdout_file)),
        )
        self.current_project_state.runs.append(run_record)
        self.current_project_state.project.updated_at = now_iso()
        self._persist_current_project_state()

        self.operation_in_progress = True
        self._background_active_run_id = run_id
        self._background_result_file = (
            self.current_project_root / "processed" / "logfiles" / f"{run_id}-background-result.json"
        )
        self._clear_workspace_message()
        self.background_message.object = (
            "Extracting sample measurement. Workspace interactions are blocked until it finishes."
        )
        self.background_message.alert_type = "warning"

        par_file = Path(selected_par_path)
        if self._background_result_file.exists():
            self._background_result_file.unlink()

        command = [
            sys.executable,
            str(BACKGROUND_SUBPROCESS_WORKER),
            str(par_file),
            str(self.current_project_root),
            run_id,
            str(self._background_result_file),
        ]
        env = os.environ.copy()

        try:
            self._background_run_process = subprocess.Popen(
                command,
                cwd=str(REPO_ROOT),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception as exc:
            failure = self._build_background_failure_result(
                run_id,
                stdout_file,
                f"Could not start the extraction subprocess: {exc}",
            )
            self._background_run_process = None
            self._finalize_background_run(failure)
            return

        self._start_background_run_poll()
        self._render_current_screen()

    def _start_background_run_poll(self) -> None:
        if self._background_run_poll is not None:
            self._background_run_poll.stop()
            self._background_run_poll = None

        if pn.state.curdoc is not None:
            self._background_run_poll = pn.state.add_periodic_callback(
                self._finalize_background_run_if_ready,
                period=500,
                start=True,
            )

    def _finalize_background_run_if_ready(self) -> None:
        if self._background_run_process is None or self._background_run_process.poll() is None:
            return

        if self._background_run_poll is not None:
            self._background_run_poll.stop()
            self._background_run_poll = None

        result = self._load_background_subprocess_result(self._background_run_process.returncode)
        self._background_run_process = None
        self._background_result_file = None
        self._finalize_background_run(result)

    def _load_background_subprocess_result(
        self,
        returncode: int | None,
    ) -> BackgroundExtractionResult:
        if self._background_result_file is None:
            return self._build_background_failure_result(
                self._background_active_run_id or "unknown",
                self._expected_background_stdout_file(),
                "No background result file location was configured.",
            )
        if self._background_result_file.exists():
            try:
                payload = json.loads(self._background_result_file.read_text(encoding="utf-8"))
                return BackgroundExtractionResult(
                    run_id=str(payload["run_id"]),
                    status=str(payload["status"]),
                    stdout_file=str(payload["stdout_file"]),
                    measurement_file=payload.get("measurement_file"),
                    generated_files=list(payload.get("generated_files", [])),
                    summary=str(payload.get("summary", "")),
                    error=payload.get("error"),
                )
            except Exception as exc:
                return self._build_background_failure_result(
                    self._background_active_run_id or "unknown",
                    self._expected_background_stdout_file(),
                    f"Could not read the extraction subprocess result: {exc}",
                )

        return self._build_background_failure_result(
            self._background_active_run_id or "unknown",
            self._expected_background_stdout_file(),
            f"Extraction subprocess exited with code {returncode} without producing a result file.",
        )

    def _expected_background_stdout_file(self) -> str:
        if self.current_project_root is None or self._background_active_run_id is None:
            return ""
        return str(
            self.current_project_root
            / "processed"
            / "logfiles"
            / f"{self._background_active_run_id}-stdout.txt"
        )

    def _build_background_failure_result(
        self,
        run_id: str,
        stdout_file: str | Path,
        error_message: str,
    ) -> BackgroundExtractionResult:
        return BackgroundExtractionResult(
            run_id=run_id,
            status="failed",
            stdout_file=str(stdout_file),
            measurement_file=None,
            generated_files=[],
            summary=f"Processed run `{run_id}`, status: `failed`, error: {error_message}",
            error=error_message,
        )

    def _finalize_background_run(self, result: BackgroundExtractionResult | None) -> None:
        self.operation_in_progress = False
        if self.current_project_state is None or self._background_active_run_id is None:
            self._render_current_screen()
            return

        run_record = next(
            (
                record
                for record in reversed(self.current_project_state.runs)
                if record.run_id == self._background_active_run_id
            ),
            None,
        )
        if run_record is not None and result is not None:
            run_record.status = result.status
            run_record.finished_at = now_iso()
            run_record.summary = result.summary
            run_record.error = result.error
            run_record.output_paths.stdout_file = result.stdout_file
            run_record.output_paths.generated_files = list(result.generated_files)
            self.current_project_state.project.updated_at = now_iso()
            self._persist_current_project_state()

        self._background_active_run_id = None
        if result is None:
            self.background_message.object = "Sample extraction finished without a result payload."
            self.background_message.alert_type = "danger"
            self._render_current_screen()
            return

        if result.status == "succeeded" and result.measurement_file:
            state = self._get_background_state()
            artifact_path = Path(str(result.measurement_file)).expanduser()
            if self.current_project_root is not None:
                try:
                    artifact_for_state = (
                        artifact_path.resolve(strict=False)
                        .relative_to(self.current_project_root.resolve(strict=False))
                        .as_posix()
                    )
                except Exception:
                    artifact_for_state = str(artifact_path)
            else:
                artifact_for_state = str(artifact_path)

            state["latest_measurement_artifact"] = artifact_for_state

            par_path_str = None
            if run_record is not None:
                par_path_str = run_record.workflow_data.get("par_file")
            if isinstance(par_path_str, str) and self.current_project_root is not None:
                par_path = Path(par_path_str).expanduser()
                sample_key = background_sample_key(par_path, self.current_project_root)
                if sample_key:
                    cached = state.get("measurements_by_par")
                    if not isinstance(cached, dict):
                        cached = {}
                        state["measurements_by_par"] = cached
                    signature = background_par_signature(par_path)
                    cached_entry = {
                        "measurement_artifact": artifact_for_state,
                        "run_id": result.run_id,
                        "extracted_at": now_iso(),
                    }
                    if signature is not None:
                        cached_entry["par_mtime"] = signature[0]
                        cached_entry["par_size"] = signature[1]
                    cached[sample_key] = cached_entry

            self._persist_background_state(state)
            self._refresh_background_plots()
            self.background_message.object = "Sample extraction finished successfully."
            self.background_message.alert_type = "success"
            self._show_success_toast("Sample extraction finished successfully.")
        else:
            self.background_message.object = (
                f"Sample extraction finished with errors. {result.error}"
            )
            self.background_message.alert_type = "danger"

        self._render_current_screen()

    def _create_run_id(self) -> str:
        return datetime.now(tz=PARIS_TZ).strftime("%Y%m%d-%H%M%S")
