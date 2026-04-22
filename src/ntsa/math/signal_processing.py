from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def smooth_curve(
    x: ArrayLike, y: ArrayLike, smoothing_factor: float
) -> NDArray[np.float64]:
    """
    Smooths a function using a moving average-window.

    Parameters
    ----------
    x : array_like
        Array of x values.
    y : array_like
        Array of y values.
    smoothing_factor : float
        Smoothing factor between 0 and 1. A smaller smoothing factor results
        in less smoothing, while a larger factor results in more aggressive
        smoothing.

    Returns
    -------
    numpy.ndarray
        Array of smoothed y values.
    """
    y_arr = np.asarray(y)
    window_size = int(smoothing_factor * len(y_arr))
    if window_size == 0:
        return y_arr

    smoothed_y = []
    for i in range(len(y_arr)):
        start = max(0, i - window_size // 2)
        end = min(len(y_arr), i + window_size // 2 + 1)
        smoothed_value = np.mean(y_arr[start:end])
        smoothed_y.append(smoothed_value)
    return np.array(smoothed_y)
