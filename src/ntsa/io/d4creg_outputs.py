from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

from ntsa.physics.conversions import ang2q


def getDiffA(  # noqa: N802 (legacy API)
    numor: np.ndarray,
    head: Sequence[Mapping[str, Any]],
    runInfo: Mapping[str, Any],
) -> np.ndarray:
    """
    Create diffractograms in angular scale (legacy behavior).

    Parity-first copy of `legacy/lib/toscana.py::getDiffA`.
    """
    ndet = head[0]["ndet"]  # Number of detectors
    ncell = head[0]["ncell"]  # Number of cells in one detector
    angmin = runInfo["angular_scale"][0]
    angmax = runInfo["angular_scale"][1]
    angstep = runInfo["angular_scale"][2]
    angular_range = runInfo["angular_range_bank"]
    angular_step = angular_range / ncell  # Angular step for 1 cell (in deg)

    if angstep < angular_step:
        print("WARNING: In getDiffA function")
        print("         The angular step should not be smaller than")
        print("         {:6.3f} degrees".format(angular_step))
        print(
            "         Then, it has been changed to {:6.3f} degrees".format(angular_step)
        )
        angstep = angular_step

    # Number of angles in the angular binning
    nangles = int((angmax - angmin) / angstep)

    # Defining the matrix that will contain the 10 diffractograms
    diff = np.zeros((10, 5, nangles))

    # The angular scale is the same for all diffractograms
    for i in range(ndet + 1):
        diff[i, 0, :] = np.arange(angmin, angmax, angstep)

    # The Q-scale is the same for all diffractograms
    for i in range(ndet + 1):
        diff[i, 4, :] = ang2q(diff[i, 0, :], wlength=runInfo["wavelength"])

    # Number of numors to regroup and number of angles in one numor
    nbrNumors = len(numor[:, 0, 0])
    nbrData = len(numor[0, 0, :])

    # This variable will be used for normalisation
    # It is divided by 1000000 just to avoid large numbers
    totalmon = 0
    for num in range(nbrNumors):
        totalmon += head[num]["MonitorCnts"] / 1000000

    for num in range(nbrNumors):
        angle = numor[num, 0, :]
        count = numor[num, 1, :]
        error = numor[num, 2, :]
        cell = numor[num, 4, :]
        mon = head[num]["MonitorCnts"] / 1000000 / totalmon
        for ang in range(nbrData):
            angle1 = angle[ang] - angular_step / 2.0
            ang1 = (angle1 - angmin) / angstep
            a1 = int(ang1)
            angle2 = angle[ang] + angular_step / 2.0
            ang2 = (angle2 - angmin) / angstep
            a2 = int(ang2)
            frac1 = 1.0 - (ang1 - int(ang1))
            frac2 = ang1 - int(ang1)
            if (not np.isnan(count[ang])) and (not np.isnan(error[ang])):
                diff[0, 1, a1] += frac1 * count[ang] * mon
                diff[0, 1, a2] += frac2 * count[ang] * mon
                diff[0, 2, a1] += frac1 * error[ang] * mon
                diff[0, 2, a2] += frac2 * error[ang] * mon
                diff[0, 3, a1] += frac1 * mon
                diff[0, 3, a2] += frac2 * mon
                det = int(cell[ang] / 1000)
                diff[det, 1, a1] += frac1 * count[ang] * mon
                diff[det, 1, a2] += frac2 * count[ang] * mon
                diff[det, 2, a1] += frac1 * error[ang] * mon
                diff[det, 2, a2] += frac2 * error[ang] * mon
                diff[det, 3, a1] += frac1 * mon
                diff[det, 3, a2] += frac2 * mon

    # Normalisation by the weighting factor of each bin
    for det in range(10):
        for i in range(len(diff[0, 1, :])):
            if (not np.isnan(diff[0, 1, i])) and (diff[det, 3, i] > 0):
                diff[det, 1, i] = diff[det, 1, i] / diff[det, 3, i]
                diff[det, 2, i] = diff[det, 2, i] / diff[det, 3, i]
            else:
                diff[det, 1, i] = "NaN"
                diff[det, 2, i] = "NaN"

    return diff


def saveDiffAngle(  # noqa: N802 (legacy API)
    diffA: np.ndarray,
    head: Sequence[Mapping[str, Any]],
    runInfo: Mapping[str, Any],
) -> None:
    """
    Write diffractograms in angle scale to CORRECT + D4 formats (legacy behavior).
    """
    ndata = 0
    for i in range(len(diffA[0, 0, :])):
        count = diffA[0, 1, i]
        error = diffA[0, 2, i]
        if (not np.isnan(count * error)) and (count > 0):
            ndata += 1

    file = runInfo["file"] + runInfo["ext"][1]
    with open(file, "w") as adatfile:
        adatfile.write("# " + file + "\n")
        adatfile.write("#Block  1\n")
        adatfile.write("#========\n")
        adatfile.write("#\n")
        adatfile.write("#Instrument:" + head[0]["label"][0:2] + "\n")
        adatfile.write(
            "#User      :"
            + head[0]["user"].strip(" ")
            + "    exp_"
            + head[0]["proposal"].strip(" ")
            + "/processed"
            + "\n"
        )
        adatfile.write(f"#Run number: {runInfo['numorLst']}\n")
        adatfile.write("#Spectrum  :            1\n")
        adatfile.write("#Title     :" + file + "\n")

        adatfile.write("#Run date  :" + runInfo["runDate"] + "\n")

        mini = runInfo["angular_scale"][0]
        maxi = runInfo["angular_scale"][1]
        step = runInfo["angular_scale"][2]
        bins = int((maxi - mini) / step) + 1
        adatfile.write(
            "#X caption : 2Theta (degrees) binned from {} to {} by {} ({} bins)".format(
                mini, maxi, step, bins
            )
            + "\n"
        )
        adatfile.write("#Y caption : Counts/monitor \n")
        adatfile.write("#Histogram :            F \n")
        adatfile.write("#Points    :         {}   ".format(ndata) + "\n")

        for i in range(len(diffA[0, 0, :])):
            angle = diffA[0, 0, i]
            count = diffA[0, 1, i]
            error = diffA[0, 2, i]
            if (not np.isnan(count * error)) and (count > 0):
                adatfile.write(
                    "{:8.4f}     {:12.8f}     {:12.8f} \n".format(angle, count, error)
                )
    print(
        4 * " "
        + "File "
        + runInfo["file"]
        + runInfo["ext"][1]
        + " (CORRECT format, in angle scale)"
    )

    listNum = " "
    for i in range(len(runInfo["numorLst"])):
        listNum += runInfo["numorLst"][i] + " "

    file = runInfo["file"] + runInfo["ext"][0]
    with open(file, "w") as regfile:
        regfile.write("# " + file + "\n")
        regfile.write("# Equivalent command line: \n")
        regfile.write("#     " + runInfo["d4creg_cl"] + "\n")
        regfile.write("# Efficiency file: " + runInfo["efffile"] + "\n")
        regfile.write("# Shift file: " + runInfo["decfile"] + "\n")
        regfile.write("# Sample: " + head[0]["subtitle"] + "\n")
        regfile.write("# User: " + head[0]["user"].strip(" ") + "\n")
        regfile.write("# Local contact: " + head[0]["LC"].strip(" ") + "\n")
        regfile.write("# Proposal: " + head[0]["proposal"].strip(" ") + "\n")
        regfile.write("# Run date  :" + runInfo["runDate"] + "\n")
        regfile.write(
            "# Requested numors: {}, {} numors included \n".format(
                listNum, runInfo["nbrNumors"]
            )
        )
        regfile.write("# Normalisation type: " + runInfo["normalisation"][0] + "\n")
        regfile.write("# Zero-angle = " + str(runInfo["twotheta0"]) + " deg\n")
        regfile.write("# Wavelength = " + str(runInfo["wavelength"]) + " deg\n")
        regfile.write("# Monitor dead-time = " + str(runInfo["dead_time"][0]) + " s\n")
        regfile.write("# Detector dead-time = " + str(runInfo["dead_time"][1]) + " s\n")
        regfile.write("# 2theta = 2theta.raw - Zero-angle + shifts \n")
        regfile.write(
            "# Binned on angle (from {} to {} in steps of {}, deg), but not on Q \n".format(
                *runInfo["angular_scale"]
            )
        )
        regfile.write(
            "#     Q = 4pi/{}Å * sin(angle/2) \n".format(str(runInfo["wavelength"]))
        )

        for det in range(1, 10):
            regfile.write("# ----------- \n")
            regfile.write("# Detector " + str(det) + "\n")
            regfile.write("# ----------- \n")
            regfile.write("# Angle(deg)     Counts           Error            Q(1/Å)\n")
            for i in range(len(diffA[0, 0, :])):
                angle = diffA[det, 0, i]
                count = diffA[det, 1, i]
                error = diffA[det, 2, i]
                qval = diffA[det, 4, i]
                if (not np.isnan(count * error)) and (count > 0):
                    regfile.write(
                        "{:8.4f}     {:12.8f}     {:12.8f}     {:8.4f} \n".format(
                            angle, count, error, qval
                        )
                    )

    print(
        "    File "
        + runInfo["file"]
        + runInfo["ext"][0]
        + " (D4 format, in angle and Q-scale)"
    )
    return


def saveDiffQ(  # noqa: N802 (legacy API)
    diffQ: np.ndarray,
    head: Sequence[Mapping[str, Any]],
    runInfo: Mapping[str, Any],
) -> None:
    """
    Write diffractograms in Q scale to CORRECT format (legacy behavior).
    """
    ndata = 0
    for i in range(len(diffQ)):
        count = diffQ[i, 1]
        error = diffQ[i, 2]
        if (not np.isnan(count * error)) and (count > 0):
            ndata += 1

    file = runInfo["file"] + runInfo["ext"][2]
    with open(file, "w") as qdatfile:
        qdatfile.write("# " + file + "\n")
        qdatfile.write("#Block  1\n")
        qdatfile.write("#========\n")
        qdatfile.write("#\n")
        qdatfile.write("#Instrument:" + head[0]["label"][0:2] + "\n")
        qdatfile.write(
            "#User      :"
            + head[0]["user"].strip(" ")
            + "    exp_"
            + head[0]["proposal"].strip(" ")
            + "/processed"
            + "\n"
        )
        qdatfile.write(f"#Run number: {runInfo['numorLst']}\n")
        qdatfile.write("#Spectrum  :            1\n")
        qdatfile.write("#Title     :" + file + "\n")
        qdatfile.write("#Run date  :" + runInfo["runDate"] + "\n")
        mini = runInfo["q_scale"][0]
        maxi = runInfo["q_scale"][1]
        step = runInfo["q_scale"][2]
        bins = int((maxi - mini) / step) + 1
        qdatfile.write(
            "#X caption : Q (1/Å) binned from {:4.3f} to {:4.3f} by {:4.3f} ({} bins)".format(
                mini, maxi, step, bins
            )
            + "\n"
        )
        qdatfile.write("#Y caption : Counts/monitor\n")
        qdatfile.write("#Histogram :            F\n")
        qdatfile.write("#Points    :         {}   ".format(ndata) + "\n")

        for i in range(len(diffQ)):
            q = diffQ[i, 0]
            count = diffQ[i, 1]
            error = diffQ[i, 2]
            if (not np.isnan(count * error)) and (count > 0):
                qdatfile.write(
                    "{:8.4f}     {:12.8f}     {:12.8f} \n".format(q, count, error)
                )
    print(
        "    File "
        + runInfo["file"]
        + runInfo["ext"][2]
        + " (CORRECT format, in Q scale)"
    )
    return
