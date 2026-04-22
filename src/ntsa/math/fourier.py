from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy import integrate  # type: ignore[import-untyped]

from .line_shapes import step
from .windows import Lorch, LorchN

if TYPE_CHECKING:
    from numpy.typing import NDArray


def getSineIntegral(x: float) -> float:  # noqa: N802 (legacy API)
    """
    Evaluate the Sine Integral function via numerical integration (legacy behavior).
    """
    npoints = 10000
    si: list[float] = []
    t: list[float] = []
    t.append(0.0)
    si.append(1.0)
    for i in range(1, npoints):
        t.append(i * x / float(npoints))
        si.append(float(np.sin(t[i]) / t[i]))
    result = integrate.simpson(si, t)
    return float(result)


def getSineFT(  # noqa: N802 (legacy API)
    vvec: NDArray[np.float64],
    yvec: NDArray[np.float64],
    uvec: NDArray[np.float64],
    vmax: float = 0,
    c: float = 1.0,
    s: float = 1.0,
    w: int = 0,
) -> NDArray[np.float64] | None:
    """
    Calculate a sine Fourier transform (legacy behavior).
    """
    nbr_v = len(vvec)
    nbr_y = len(yvec)
    if nbr_v != nbr_y:
        print("ERROR: abcissa and ordinate do not have the same dimension")
        print("       in the Fourier Transform function (getSineFT).")
        return None

    if (vmax <= 0) or (vmax > vvec[-1]):
        vmax = float(vvec[-1])

    win: NDArray[np.float64] = np.ones(nbr_v, dtype=np.float64)
    if w == 1:
        win = LorchN(vvec, vmax)

    stf: NDArray[np.float64] = np.zeros(len(uvec), dtype=np.float64)
    for i in range(len(uvec)):
        integ = (yvec - s) * vvec * np.sin(vvec * uvec[i]) * win
        stf[i] = 2.0 / np.pi * c * integrate.simpson(integ, vvec)
    return stf


def sineFT(  # noqa: N802 (legacy API)
    StrFactor: NDArray[np.float64],
    nr: NDArray[np.float64],
    qmax: float = 23.5,
    density: float = 0.1,
    constant: float = 1.0,
    selfsca: float = 1.0,
    window: int = 0,
) -> NDArray[np.float64]:
    """
    Perform the sine Fourier transform of the structure factor (legacy behavior).
    """
    soq = StrFactor[:, 1]
    q = StrFactor[:, 0]

    pcf: list[float] = []
    pdf: list[float] = []
    rdf: list[float] = []
    tor: list[float] = []
    run: list[float] = []

    win: list[float] = []
    if window == 0:
        for qu in q:
            win.append(float(step(float(qu), qmax)))
    else:
        for qu in q:
            win.append(float(Lorch(float(qu), qmax)))
        integral_lorch = integrate.simpson(win, q)
        for i in range(len(win)):
            win[i] = win[i] * qmax / float(integral_lorch)

    delta_r = float(nr[1] - nr[0])
    for r in nr:
        integ = (soq - selfsca) * q * np.sin(q * r) * win
        result = 2.0 / np.pi * constant * integrate.simpson(integ, q)
        pcf.append(float(result))
        if r <= 0:
            pdf.append(0.0)
        else:
            pdf.append(float(result / 4.0 / np.pi / float(r) / density + 1.0))
        rdf.append(float(result * float(r) + 4.0 * np.pi * density * float(r) ** 2))
        tor.append(float(result + 4.0 * np.pi * density * float(r)))

    for r in nr:
        ind = 1 + int(float(r) / delta_r)
        xr = nr[0:ind]
        integ = np.array(rdf)[0:ind]
        result = integrate.simpson(integ, xr)
        run.append(float(result))

    rrr = np.array(nr, dtype=np.float64)
    pcf_arr = np.array(pcf, dtype=np.float64)
    pdf_arr = np.array(pdf, dtype=np.float64)
    rdf_arr = np.array(rdf, dtype=np.float64)
    tor_arr = np.array(tor, dtype=np.float64)
    run_arr = np.array(run, dtype=np.float64)

    rrr = rrr.reshape(rrr.shape[0], 1)
    pcf_arr = pcf_arr.reshape(pcf_arr.shape[0], 1)
    pdf_arr = pdf_arr.reshape(pdf_arr.shape[0], 1)
    rdf_arr = rdf_arr.reshape(rdf_arr.shape[0], 1)
    tor_arr = tor_arr.reshape(tor_arr.shape[0], 1)
    run_arr = run_arr.reshape(run_arr.shape[0], 1)

    fou = np.concatenate((rrr, pcf_arr), axis=1)
    fou = np.concatenate((fou, pdf_arr), axis=1)
    fou = np.concatenate((fou, rdf_arr), axis=1)
    fou = np.concatenate((fou, tor_arr), axis=1)
    fou = np.concatenate((fou, run_arr), axis=1)
    return fou


def backFT(  # noqa: N802 (legacy API)
    qu: NDArray[np.float64],
    ar: NDArray[np.float64],
    pdf: NDArray[np.float64],
    density: float,
    cut: list[float],
) -> tuple[
    NDArray[np.float64],
    NDArray[np.float64] | None,
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
    NDArray[np.float64],
]:
    """
    Back Fourier transform of a PDF (legacy behavior).
    """
    pdf_cut = pdf.copy()
    if len(cut) == 1 and cut[0] == -1:
        for i in range(len(pdf) - 1, 0, -1):
            if pdf[i] < 0:
                break
        for j in range(i + 1):
            pdf_cut[j] = 0.0
    elif len(cut) == 1 and cut[0] > 0.0:
        for i in range(len(pdf)):
            if ar[i] < cut[0]:
                pdf_cut[i] = 0.0
    elif len(cut) == 3:
        for i in range(len(pdf)):
            if ar[i] < cut[0] or (cut[1] < ar[i] and ar[i] < cut[2]):
                pdf_cut[i] = 0.0
    elif len(cut) == 5:
        for i in range(len(pdf)):
            if (
                ar[i] < cut[0]
                or (cut[1] < ar[i] and ar[i] < cut[2])
                or (cut[3] < ar[i] and ar[i] < cut[4])
            ):
                pdf_cut[i] = 0.0
    elif len(cut) == 7:
        for i in range(len(pdf)):
            if (
                ar[i] < cut[0]
                or (cut[1] < ar[i] and ar[i] < cut[2])
                or (cut[3] < ar[i] and ar[i] < cut[4])
                or (cut[5] < ar[i] and ar[i] < cut[6])
            ):
                pdf_cut[i] = 0.0
    elif len(cut) == 9:
        for i in range(len(pdf)):
            if (
                ar[i] < cut[0]
                or (cut[1] < ar[i] and ar[i] < cut[2])
                or (cut[3] < ar[i] and ar[i] < cut[4])
                or (cut[5] < ar[i] and ar[i] < cut[6])
                or (cut[7] < ar[i] and ar[i] < cut[8])
            ):
                pdf_cut[i] = 0.0
    elif len(cut) == 11:
        for i in range(len(pdf)):
            if (
                ar[i] < cut[0]
                or (cut[1] < ar[i] and ar[i] < cut[2])
                or (cut[3] < ar[i] and ar[i] < cut[4])
                or (cut[5] < ar[i] and ar[i] < cut[6])
                or (cut[7] < ar[i] and ar[i] < cut[8])
                or (cut[9] < ar[i] and ar[i] < cut[10])
            ):
                pdf_cut[i] = 0.0
    elif len(cut) == 13:
        for i in range(len(pdf)):
            if (
                ar[i] < cut[0]
                or (cut[1] < ar[i] and ar[i] < cut[2])
                or (cut[3] < ar[i] and ar[i] < cut[4])
                or (cut[5] < ar[i] and ar[i] < cut[6])
                or (cut[7] < ar[i] and ar[i] < cut[8])
                or (cut[9] < ar[i] and ar[i] < cut[10])
                or (cut[11] < ar[i] and ar[i] < cut[12])
            ):
                pdf_cut[i] = 0.0

    stf = getSineFT(ar, pdf_cut, qu, w=0)
    if stf is None:
        raise ValueError("backFT: getSineFT returned None (dimension mismatch).")

    soq = 1 + 2.0 * np.pi**2 * density / qu * stf
    pcf = getSineFT(qu, soq, ar, w=0)
    if pcf is None:
        raise ValueError("backFT: getSineFT returned None (dimension mismatch).")

    pdf_new = 1 + pcf / 4.0 / np.pi / density / ar
    rdf = 4.0 * np.pi * density * ar * ar * pdf_new
    tor = rdf / ar

    run = np.zeros(len(ar), dtype=np.float64)
    for i in range(1, len(ar)):
        run[i] = integrate.simpson(rdf[0:i], ar[0:i])

    return (
        np.asarray(soq, dtype=np.float64),
        np.asarray(pcf, dtype=np.float64),
        np.asarray(pdf_new, dtype=np.float64),
        np.asarray(rdf, dtype=np.float64),
        np.asarray(tor, dtype=np.float64),
        np.asarray(run, dtype=np.float64),
    )
