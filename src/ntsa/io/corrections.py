from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ._logfiles import d4creg_log_path

if TYPE_CHECKING:
    from numpy.typing import NDArray


def getDTC_mcounts(  # noqa: N802 (legacy API)
    monitor: float, time: float, dead_time: float = 2.4e-6
) -> float:
    """
    Calculate the dead-time corrected monitor counts (legacy behavior).
    """
    if time <= 0:
        time = 1e-6
    nu_meas = monitor / time
    correction = 1.0 - nu_meas * dead_time
    if correction > 0:
        factor = 1.0 / correction
        nu = nu_meas * factor
        with d4creg_log_path().open("a", encoding="utf-8") as file:
            file.write(
                "  Monitor DT = {:4.2e} s. Correction factor = {:10.6f} \n".format(
                    dead_time, factor
                )
            )
        return float(nu * time)

    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write("--- ERROR in Function getDTC_mcounts: correction factor < 0 \n")
    raise ValueError("getDTC_mcounts: correction factor < 0")


def getDTC_dcounts(  # noqa: N802 (legacy API)
    counts: NDArray[np.float64],
    total_counts: float,
    time: float,
    dead_time: float = 7e-6,
) -> tuple[NDArray[np.float64], float]:
    """
    Calculate the dead-time corrected detector counts (legacy behavior).
    """
    if time <= 0:
        time = 1e-6
    nu_meas = counts / time
    correction = 1.0 - nu_meas * dead_time

    # NOTE: legacy uses `(correction.all()) > 0`, which does not actually test positivity.
    if (correction.all()) > 0:  # noqa: PLR2004 (parity with legacy)
        factor = 1.0 / correction
        nu = nu_meas * factor
        with d4creg_log_path().open("a", encoding="utf-8") as file:
            file.write(
                "  Monitor DT = {:4.2e} s. Correction factor = {:10.6f}".format(
                    dead_time, float(factor[0][0])
                )
                + " (1st detector cell)\n"
            )
        return (nu * time).astype(np.float64, copy=False), float(
            total_counts * float(factor[0][0])
        )

    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write("--- ERROR in Function getDTC_dcounts: correction factor < 0 \n")
    raise ValueError("getDTC_dcounts: correction factor < 0")


def getEff(  # noqa: N802 (legacy API)
    filename: str = "effd4c.eff", ndet: int = 9, ncells: int = 64
) -> NDArray[np.float64]:
    """
    Generate the relative efficiencies (legacy behavior).
    """
    efficiencies: NDArray[np.float64] = np.ones((ndet, ncells), dtype=np.float64)
    if filename == "ones":
        print("No relative efficiencies")
        return efficiencies

    with open(filename, "r") as shifts:
        lines = shifts.readlines()

    for line in lines:
        if "#" in line:
            continue
        row = (line.strip(" "))[0:-1]
        if len(row) == 0:
            continue
        col = row.split()
        if float(col[2]) <= 0:
            col[2] = "nan"
        efficiencies[int(col[0]) - 1, int(col[1]) - 1] = float(col[2])

    return efficiencies


def getDec(filename: str = "dec.dec", ndet: int = 9) -> NDArray[np.float64]:  # noqa: N802 (legacy API)
    """
    Read the angular shifts for each detection bank (legacy behavior).
    """
    if filename == "zeros":
        print("No angular shifts")
        return np.zeros(ndet, dtype=np.float64)
    if filename == "manual":
        print("Built-in shifts:")
        return np.array(
            [0.000, -0.027, -0.026, -0.087, -0.125, -0.160, -0.220, -0.250, -0.340],
            dtype=np.float64,
        )

    zero = np.zeros(ndet, dtype=np.float64)
    with open(filename, "r") as shifts:
        lines = shifts.readlines()
    for line in lines:
        if "#" in line:
            continue
        row = (line.strip(" "))[0:-1]
        if len(row) == 0:
            continue
        columns = row.split()
        zero[int(columns[0]) - 1] = float(columns[1])
    return zero


def getErrorsNumor(counts: NDArray[np.float64]) -> NDArray[np.float64]:  # noqa: N802 (legacy API)
    """
    Calculate Poisson errors for detector counts (legacy behavior).
    """
    errors = np.zeros((counts.shape[0], counts.shape[1]), dtype=np.float64)
    errors = np.sqrt(counts)
    return errors.astype(np.float64, copy=False)


def getNormalFactors(monitor: float, time: float) -> NDArray[np.float64]:  # noqa: N802 (legacy API)
    """
    Define normalisation factors (legacy behavior).
    """
    normal = np.zeros((2, 2), dtype=np.float64)
    normal[0][0] = monitor
    normal[0][1] = np.sqrt(monitor)
    normal[1][0] = time
    normal[1][1] = 0.01
    return normal


def normalise(  # noqa: N802 (legacy API)
    counts: NDArray[np.float64],
    errors: NDArray[np.float64],
    normal: NDArray[np.float64],
    norm_type: str = "monitor",
    norm_time: float = 120,
    norm_mon: float = 1_000_000,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Normalise counts and errors by monitor counts or counting time (legacy behavior).
    """
    norm = [norm_mon, norm_time]
    ntype = 0
    if norm_type == "time":
        ntype = 1
    counts = (norm[ntype] * counts / normal[ntype][0]).astype(np.float64, copy=False)
    relative_error = np.sqrt(
        (errors / counts) ** 2 + (normal[ntype][1] / normal[ntype][0]) ** 2
    )
    errors = (counts * relative_error).astype(np.float64, copy=False)
    return counts, errors


def getAngles(  # noqa: N802 (legacy API)
    counts: NDArray[np.float64],
    ttheta_ref: float,
    zeros: NDArray[np.float64],
    cell_step: float = 0.125,
    det_step: float = 15.0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Determine angles and cell identifiers for each detector/cell (legacy behavior).
    """
    angles = np.zeros((counts.shape[0], counts.shape[1]), dtype=np.float64)
    cells = np.zeros((counts.shape[0], counts.shape[1]), dtype=np.float64)
    ndet = counts.shape[0]
    ncel = counts.shape[1]
    for det in range(ndet):
        for cel in range(ncel):
            angles[det][cel] = (
                ttheta_ref + zeros[det] + (det * det_step + cel * cell_step)
            )
            cells[det][cel] = (det + 1) * 1000 + cel + 1
    return angles, cells
