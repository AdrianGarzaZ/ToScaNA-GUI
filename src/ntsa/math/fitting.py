from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def get_chi(y1: ArrayLike, y2: ArrayLike) -> float:
    """
    Calculates the chi (RMS difference) between 2 sets of y-values.

    Parameters
    ----------
    y1 : array_like
        Array of values of the first set of y-values.
    y2 : array_like
        Array of values of the second set of y-values.

    Returns
    -------
    float
        Value of chi between the 2 sets of y-values.
    """
    return float(np.sqrt(np.mean((np.asarray(y1) - np.asarray(y2)) ** 2)))


def fit_and_find_extremum(
    x: ArrayLike, y: ArrayLike
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Fits a second-degree polynomial to the given points, calculates the derivative,
    and finds the x value where the derivative is 0.

    Parameters
    ----------
    x : array_like
        x values.
    y : array_like
        y values.

    Returns
    -------
    tuple
        (extremum_x, extremum_y, fit_values)
    """
    x_arr: NDArray[np.float64] = np.asarray(x, dtype=np.float64)
    y_arr: NDArray[np.float64] = np.asarray(y, dtype=np.float64)

    # Fit a second-degree polynomial: a*x^2 + b*x + c
    coeffs: NDArray[np.float64] = np.asarray(
        np.polyfit(x_arr, y_arr, 2), dtype=np.float64
    )
    a, b, _c = float(coeffs[0]), float(coeffs[1]), float(coeffs[2])

    # Extremum at derivative zero: 2*a*x + b = 0 -> x = -b/(2*a)
    # (matches `np.poly1d(coeffs).deriv().r` for well-behaved fits, but is easier to type-check)
    extremum_x: NDArray[np.float64] = np.asarray([-b / (2.0 * a)], dtype=np.float64)
    extremum_y: NDArray[np.float64] = np.asarray(
        np.polyval(coeffs, extremum_x), dtype=np.float64
    )
    fit_values: NDArray[np.float64] = np.asarray(
        np.polyval(coeffs, x_arr), dtype=np.float64
    )
    return extremum_x, extremum_y, fit_values


def fittingRange0(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    abcissas: ArrayLike,
    ordinates: ArrayLike,
    errors: ArrayLike,
) -> NDArray[np.float64]:
    """
    Define a subset of points inside a rectangle (legacy behavior).

    Returns a 3-column matrix (x, y, e) with x/y/e shaped as (n, 1) columns.
    """
    x_in = np.asarray(abcissas, dtype=np.float64)
    y_in = np.asarray(ordinates, dtype=np.float64)
    e_in = np.asarray(errors, dtype=np.float64)

    if len(x_in) != len(y_in):
        print(
            "ERROR: Ordinate and abcissa must have the same length in function fittingRange."
        )
    if (xmax < xmin) or (ymax < ymin):
        print(
            "ERROR: The limits of the rectangle are wrong in the function fittingRange."
        )

    x_range: list[float] = []
    y_range: list[float] = []
    e_range: list[float] = []
    for i in range(len(x_in)):
        if (x_in[i] >= xmin) and (x_in[i] <= xmax):
            if (y_in[i] >= ymin) and (y_in[i] <= ymax):
                x_range.append(float(x_in[i]))
                y_range.append(float(y_in[i]))
                e_range.append(float(e_in[i]))

    if len(x_range) < 10:
        print("WARNING: Less than 10 points for the fitting in fittingRange.")
    if len(x_range) == 0:
        print("ERROR: No points for the fitting in fittingRange.")

    x = np.asarray(x_range, dtype=np.float64).reshape(-1, 1)
    y = np.asarray(y_range, dtype=np.float64).reshape(-1, 1)
    e = np.asarray(e_range, dtype=np.float64).reshape(-1, 1)
    limited = np.concatenate((x, y), axis=1)
    limited = np.concatenate((limited, e), axis=1)
    return np.asarray(limited, dtype=np.float64)


def fittingRange(
    xmin: float,
    xmax: float,
    ymin: float,
    ymax: float,
    abcissas: ArrayLike,
    ordinates: ArrayLike,
    errors: ArrayLike,
) -> Tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Define a subset of points inside a rectangle (legacy behavior).

    Returns 3 separate (n, 1) arrays: x, y, e.
    """
    x_in = np.asarray(abcissas, dtype=np.float64)
    y_in = np.asarray(ordinates, dtype=np.float64)
    e_in = np.asarray(errors, dtype=np.float64)

    if len(x_in) != len(y_in):
        print(
            "ERROR: Ordinate and abcissa must have the same length in function fittingRange."
        )
    if (xmax < xmin) or (ymax < ymin):
        print(
            "ERROR: The limits of the rectangle are wrong in the function fittingRange."
        )

    x_range: list[float] = []
    y_range: list[float] = []
    e_range: list[float] = []
    for i in range(len(x_in)):
        if (x_in[i] >= xmin) and (x_in[i] <= xmax):
            if (y_in[i] >= ymin) and (y_in[i] <= ymax):
                x_range.append(float(x_in[i]))
                y_range.append(float(y_in[i]))
                e_range.append(float(e_in[i]))

    if len(x_range) < 10:
        print("WARNING: Less than 10 points for the fitting in fittingRange.")
    if len(x_range) == 0:
        print("ERROR: No points for the fitting in fittingRange.")

    x = np.asarray(x_range, dtype=np.float64).reshape(-1, 1)
    y = np.asarray(y_range, dtype=np.float64).reshape(-1, 1)
    e = np.asarray(e_range, dtype=np.float64).reshape(-1, 1)
    return x, y, e


def fit_range(
    xmin: float, xmax: float, ymin: float, ymax: float, data: ArrayLike
) -> NDArray[np.float64]:
    """
    Define a rectangle in the x,y plane (legacy behavior).

    Parameters
    ----------
    data : array_like
        A 3-column matrix containing x, y, e.
    """
    dat = np.asarray(data, dtype=np.float64)
    x_dat = dat[:, 0]
    y_dat = dat[:, 1]
    e_dat = dat[:, 2]

    if len(x_dat) != len(y_dat):
        print(
            "ERROR: Ordinate and abcissa must have the same length in the function fit_range."
        )
    if (xmax < xmin) or (ymax < ymin):
        print("ERROR: The limits of the rectangle are wrong in the function fit_range.")

    x_range: list[float] = []
    y_range: list[float] = []
    e_range: list[float] = []
    for i in range(len(x_dat)):
        if (x_dat[i] >= xmin) and (x_dat[i] <= xmax):
            if (y_dat[i] >= ymin) and (y_dat[i] <= ymax):
                x_range.append(float(x_dat[i]))
                y_range.append(float(y_dat[i]))
                e_range.append(float(e_dat[i]))

    if (len(x_range) < 10) or (len(y_range) < 0):
        print("WARNING: Less than 10 points for the fitting in the function fit_range.")
    if (len(x_range) == 0) or (len(y_range) == 0):
        print("ERROR: No points for the fitting in the function fit_range.")

    x = np.asarray(x_range, dtype=np.float64).reshape(-1, 1)
    y = np.asarray(y_range, dtype=np.float64).reshape(-1, 1)
    e = np.asarray(e_range, dtype=np.float64).reshape(-1, 1)
    limited = np.concatenate((x, y), axis=1)
    limited = np.concatenate((limited, e), axis=1)
    return np.asarray(limited, dtype=np.float64)
