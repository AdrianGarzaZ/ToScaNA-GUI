from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Sequence

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


def binary_sum(
    w1: float, data1: NDArray[np.float64], w2: float, data2: NDArray[np.float64]
) -> Optional[NDArray[np.float64]]:
    """
    Sum (or subtract) two sets of values (y and error), preserving legacy behavior.

    Notes
    -----
    This function intentionally preserves the legacy error propagation used in
    `legacy/lib/toscana.py` for numerical parity. See `KNOWN__DIVERGENCES.md`.

    Parameters
    ----------
    w1 : float
        Weight for the first set of data.
    data1 : numpy.ndarray
        First set of data (x, y, error).
    w2 : float
        Weight for the second set of data.
    data2 : numpy.ndarray
        Second set of data (x, y, error).

    Returns
    -------
    numpy.ndarray
        The summed data (x, y, error).
    """
    if data1.shape != data2.shape:
        print("--- Error in the binary sum (binary_sum).")
        print("--- The input data have not the same shape.")
        return None

    data3 = np.copy(data1)
    data3[:, 1] = w1 * data1[:, 1] + w2 * data2[:, 1]
    data3[:, 2] = np.sqrt(w1**2 * data1[:, 2] + w2**2 * data2[:, 2])
    return data3


def ratio(
    y1: Sequence[float], e1: Sequence[float], y2: Sequence[float], e2: Sequence[float]
) -> tuple[list[float], list[float]]:
    """
    Calculate the ratio between two sets of values, preserving legacy behavior.

    Notes
    -----
    The legacy implementation uses `zip(...)` and therefore truncates to the
    shortest input length. This function preserves that behavior.
    """
    y_rat: list[float] = []
    e_rat: list[float] = []

    for y1_val, e1_val, y2_val, e2_val in zip(y1, e1, y2, e2):
        if y2_val != 0:
            r = y1_val / y2_val
            err = float(
                np.sqrt((y2_val * e1_val) ** 2 + (y1_val * e2_val) ** 2) / y2_val**2
            )
        else:
            r = 0.0
            err = 0.0

        y_rat.append(float(r))
        e_rat.append(float(err))

    return y_rat, e_rat


def wsum2(
    w1: float,
    data1: NDArray[np.float64],
    w2: float,
    data2: NDArray[np.float64],
) -> Optional[NDArray[np.float64]]:
    """
    Weighted sum (or subtraction) of two 3-column datasets, preserving legacy behavior.

    Parameters
    ----------
    w1, data1
        Weight and (x,y,e) matrix for set 1.
    w2, data2
        Weight and (x,y,e) matrix for set 2.
    """
    x1 = data1[:, 0]
    y1 = data1[:, 1]
    e1 = data1[:, 2]
    y2 = data2[:, 1]
    e2 = data2[:, 2]

    if len(y1) != len(y2):
        print("--- Error in the binary sum (wsum2).")
        print("--- The input vectors have not the same length.")
        return None

    length = len(y1)
    ysum: list[float] = []
    esum: list[float] = []

    if (w1 == 0) and (w2 == 0):
        for i in range(length):
            w = 0.0
            sqerr = e1[i] ** 2 + e2[i] ** 2
            if sqerr != 0:
                w = float(e2[i] ** 2 / sqerr)
            ysum.append(float(w * y1[i] + (1 - w) * y2[i]))
            esum.append(float(np.sqrt(w**2 * e1[i] ** 2 + (1.0 - w) ** 2 * e2[i] ** 2)))
    elif w1 == 0:
        for i in range(length):
            ysum.append(float(w2 * y2[i]))
            esum.append(float(w2 * e2[i]))
    elif w2 == 0:
        if (w1 > 0) and (w1 <= 1):
            for i in range(length):
                ysum.append(float(w1 * y1[i] + (1 - w1) * y2[i]))
                esum.append(
                    float(np.sqrt(w1**2 * e1[i] ** 2 + (1.0 - w1) ** 2 * e2[i] ** 2))
                )
        else:
            print("--- Error in the binary sum (wsum2).")
            print("--- The the weight of first set of data should be between 0 and 1.")
    else:
        for i in range(length):
            ysum.append(float(w1 * y1[i] + w2 * y2[i]))
            esum.append(float(np.sqrt(w1**2 * e1[i] ** 2 + w2**2 * e2[i] ** 2)))

    ysum_arr: NDArray[np.float64] = np.array(ysum, dtype=np.float64)
    esum_arr: NDArray[np.float64] = np.array(esum, dtype=np.float64)

    x1_col = x1.reshape(x1.shape[0], 1)
    ysum_col = ysum_arr.reshape(ysum_arr.shape[0], 1)
    esum_col = esum_arr.reshape(esum_arr.shape[0], 1)

    summed = np.concatenate((x1_col, ysum_col), axis=1)
    summed = np.concatenate((summed, esum_col), axis=1)
    return summed
