from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import numpy as np

from ntsa.io.acquisition import getNumors
from ntsa.io.d4creg_outputs import getDiffA, saveDiffAngle, saveDiffQ
from ntsa.math.binning import rebin
from ntsa.physics.conversions import ang2q
from ntsa.plotting.workflows import makePlotsA, makePlotsQ
from ntsa.utils.dates import getDate


def d4creg(runInfo: dict[str, Any] | Mapping[str, Any]) -> None:  # noqa: N802 (legacy API)
    """
    End-to-end D4 reduction workflow (legacy behavior).

    Notes
    -----
    This is a parity-first copy of `legacy/lib/toscana.py::d4creg`.
    """
    if not isinstance(runInfo, dict):
        # Legacy mutates runInfo; require a dict to preserve semantics.
        runInfo = dict(runInfo)

    runInfo["runDate"] = getDate()

    numor, head = getNumors(runInfo)
    runInfo["nbrNumors"] = len(head)

    d4creg_cl = "d4creg"
    d4creg_cl += " -x " + str(runInfo["angular_scale"][0]) + " "
    d4creg_cl += str(runInfo["angular_scale"][1]) + " "
    d4creg_cl += str(runInfo["angular_scale"][2])
    d4creg_cl += " -z " + str(runInfo["twotheta0"])
    d4creg_cl += " -w " + str(runInfo["wavelength"])
    d4creg_cl += " -o " + str(runInfo["file"]) + ".reg "
    d4creg_cl += str(head[0]["numor"]) + " " + str(head[-1]["numor"])
    runInfo["d4creg_cl"] = d4creg_cl

    print()
    print("Equivalent d4creg command line")
    print(d4creg_cl)
    print()
    print(" - Efficiency: ", runInfo["efffile"])
    print(" - Det shifts: ", runInfo["decfile"])
    if runInfo["normalisation"][0] == "monitor":
        print(
            " - Normalisation to {1} of {0} counts".format(
                runInfo["normalisation"][0], runInfo["normalisation"][2]
            )
        )
    else:
        print(
            " - Normalisation to {1} s of counting {0}".format(
                runInfo["normalisation"][0], runInfo["normalisation"][1]
            )
        )
    print(" - Number of numors: ", runInfo["nbrNumors"])

    diffA = getDiffA(numor, head, runInfo)

    print()
    print("Output:")
    saveDiffAngle(diffA, head, runInfo)

    if int(runInfo.get("plotDiff", 0)) == 1:
        makePlotsA(runInfo, diffA, head, numor)

    qmin = float(runInfo["q_scale"][0])
    qmax = float(runInfo["q_scale"][1])
    qstep = float(runInfo["q_scale"][2])

    dataQ = np.zeros((diffA.shape[2], 3), dtype=np.float64)
    ang = diffA[0, 0, :]
    dataQ[:, 0] = ang2q(ang, wlength=float(runInfo["wavelength"]))
    for i in range(diffA.shape[2]):
        for j in range(1, 3):
            dataQ[i, j] = diffA[0, j, i]

    diffQbin = rebin(0.125, float(runInfo["wavelength"]), dataQ, qmin, qmax, qstep)

    for i in range(len(diffQbin)):
        if diffQbin[i, 1] <= 0.0:
            for j in range(3):
                diffQbin[i, j] = np.nan
                diffQbin[i - 1, j] = np.nan

    saveDiffQ(diffQbin, head, runInfo)

    if int(runInfo.get("plotDiff", 0)) == 1:
        makePlotsQ(runInfo, diffQbin, head, numor)

    current_file_path = "../logfiles/d4creg.log"
    new_file_name = "../logfiles/" + str(runInfo["logfile"]) + ".log"
    try:
        os.rename(current_file_path, new_file_name)
        print(f"File '{current_file_path}' renamed to '{new_file_name}' successfully.")
    except FileNotFoundError:
        print(f"File '{current_file_path}' not found.")
    except Exception as e:  # pragma: no cover
        print(f"An error occurred: {str(e)}")
    return
