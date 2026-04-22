from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.signal import find_peaks  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def find_minimum_within_range(
    x: ArrayLike, y: ArrayLike, x_min: float, x_max: float
) -> tuple[np.float64, np.float64]:
    """
    Find the (x, y) pair where y is minimal within the specified x range (legacy behavior).
    """
    x_arr: NDArray[np.float64] = np.asarray(x, dtype=np.float64)
    y_arr: NDArray[np.float64] = np.asarray(y, dtype=np.float64)

    mask = (x_arr >= x_min) & (x_arr <= x_max)
    x_range = x_arr[mask]
    y_range = y_arr[mask]

    min_index = int(np.argmin(y_range))
    min_x_position = np.float64(x_range[min_index])
    min_y_value = np.float64(y_range[min_index])

    return min_x_position, min_y_value


def find_peaks_in_range(
    x: ArrayLike, y: ArrayLike, x_min: float, x_max: float
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Find peaks within an x range and return (peak_x, peak_y/ymin) above a threshold.

    Notes
    -----
    Preserves the legacy behavior in `legacy/lib/toscana.py`.
    """
    x_arr: NDArray[np.float64] = np.asarray(x, dtype=np.float64)
    y_arr: NDArray[np.float64] = np.asarray(y, dtype=np.float64)

    mask = (x_arr >= x_min) & (x_arr <= x_max)
    x_range = x_arr[mask]
    y_range = y_arr[mask]

    peaks, _props = find_peaks(y_range)
    _xminr, ymin = find_minimum_within_range(x_arr, y_arr, x_min, x_max)

    peak_x_positions = x_range[peaks]
    peak_maximum_values = y_range[peaks] / ymin

    sel = peak_maximum_values > 3.5
    peak_x = peak_x_positions[sel]
    peak_y = peak_maximum_values[sel]

    return peak_x, peak_y
