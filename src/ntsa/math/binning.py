from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


def get_xlim(
    xmin: float, xmax: float, dbin: float
) -> tuple[int, list[float], list[float]]:
    """
    Calculate limits and centers of bins for a histogram (legacy behavior).

    Returns
    -------
    nb : int
        Number of bins.
    x_lim : list[float]
        Limiting values for each bin (length nb+1).
    x_bin : list[float]
        Bin centers (length nb).
    """
    xini = xmin - dbin / 2.0
    xfin = xmax + dbin / 2.0
    nb = int((xfin - xini) / dbin)

    x_lim = [xmin - dbin / 2.0 + i * dbin for i in range(nb + 1)]
    x_bin = [xmin + i * dbin for i in range(nb)]
    return nb, x_lim, x_bin


def get_bins(
    x: float, xdel: float, x_lim: list[float]
) -> tuple[list[int], list[float]]:
    """
    Determine bins covered by a rectangle and its fractional coverage (legacy behavior).
    """
    bins: list[int] = []
    frac: list[float] = []

    dbin = x_lim[1] - x_lim[0]

    x1 = x - xdel / 2.0
    x2 = x + xdel / 2.0

    b1 = int((x1 - x_lim[0]) / dbin)
    b2 = int((x2 - x_lim[0]) / dbin)
    if b1 < 0 or b2 >= len(x_lim):
        return bins, frac

    deltab = b2 - b1
    if deltab == 0:
        bins.append(b1)
        frac.append(1.0)
    elif deltab == 1:
        f1 = (x_lim[b1 + 1] - x1) / xdel
        bins.append(b1)
        frac.append(f1)
        bins.append(b1 + 1)
        frac.append(1.0 - f1)
    elif deltab > 1:
        f1 = (x_lim[b1 + 1] - x1) / xdel
        bins.append(b1)
        frac.append(f1)
        for i in range(1, deltab):
            bins.append(b1 + i)
            frac.append(dbin / xdel)
        f2 = (x2 - x_lim[b2]) / xdel
        bins.append(b2)
        frac.append(f2)
    else:
        print("ERROR in get_bins")

    return bins, frac


def rebin(  # noqa: N802 (legacy API)
    xdel: float,
    wlength: float,
    data: NDArray[np.float64],
    xmin: float,
    xmax: float,
    dbin: float,
) -> NDArray[np.float64]:
    """
    Rebin experimental data in angle or Q scale (legacy behavior).

    Notes
    -----
    Parity-first copy of `legacy/lib/toscana.py::rebin`.
    """
    x_dat = data[:, 0]
    y_dat = data[:, 1]
    e_dat = data[:, 2]
    print("0 ", len(x_dat), len(y_dat), len(e_dat))

    nbins, x_lim, x_bin = get_xlim(xmin, xmax, dbin)

    y_bin: list[float] = []
    e_bin: list[float] = []
    f_bin: list[float] = []

    for _ in range(nbins + 1):
        y_bin.append(0.0)
        e_bin.append(0.0)
        f_bin.append(0.0)

    if wlength <= 0:
        for i in range(len(x_dat)):
            if (np.isnan(y_dat[i]) == False) and (np.isnan(e_dat[i]) == False):  # noqa: E712
                bins, frac = get_bins(float(x_dat[i]), xdel, x_lim)
                for j in range(len(bins)):
                    y_bin[bins[j]] += frac[j] * float(y_dat[i])
                    e_bin[bins[j]] += frac[j] * float(e_dat[i])
                    f_bin[bins[j]] += frac[j]
    else:
        for i in range(len(x_dat)):
            if (np.isnan(y_dat[i]) == False) and (np.isnan(e_dat[i]) == False):  # noqa: E712
                qdel = (
                    2.0
                    * np.pi
                    / wlength
                    * np.sqrt(1.0 - (float(x_dat[i]) * wlength / 4.0 / np.pi) ** 2)
                )
                qdel *= xdel * np.pi / 180.0
                bins, frac = get_bins(float(x_dat[i]), float(qdel), x_lim)
                for j in range(len(bins)):
                    y_bin[bins[j]] += frac[j] * float(y_dat[i])
                    e_bin[bins[j]] += frac[j] * float(e_dat[i])
                    f_bin[bins[j]] += frac[j]

    for i in range(nbins + 1):
        if f_bin[i] != 0:
            y_bin[i] /= f_bin[i]
            e_bin[i] /= f_bin[i]

    x_bin_arr: NDArray[np.float64] = np.array(x_bin, dtype=np.float64)
    y_bin_arr: NDArray[np.float64] = np.array(y_bin[0:-1], dtype=np.float64)
    e_bin_arr: NDArray[np.float64] = np.array(e_bin[0:-1], dtype=np.float64)

    x_bin_arr = x_bin_arr.reshape(x_bin_arr.shape[0], 1)
    y_bin_arr = y_bin_arr.reshape(y_bin_arr.shape[0], 1)
    e_bin_arr = e_bin_arr.reshape(e_bin_arr.shape[0], 1)

    binned = np.concatenate((x_bin_arr, y_bin_arr), axis=1)
    binned = np.concatenate((binned, e_bin_arr), axis=1)
    return binned
