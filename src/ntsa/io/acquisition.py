from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from ..physics.conversions import ang2q
from ._logfiles import d4creg_log_path
from .corrections import (
    getAngles,
    getDec,
    getDTC_dcounts,
    getDTC_mcounts,
    getEff,
    getErrorsNumor,
    getNormalFactors,
    normalise,
)
from .numors import getNumorFiles
from .saving import saveOneNumor

if TYPE_CHECKING:
    from numpy.typing import NDArray


def printRates(  # noqa: N802 (legacy API)
    detector: str, counts: float, time: float, reactor_power: float = 52
) -> None:
    """
    Print out the basic information about counting rates (legacy behavior).

    Notes
    -----
    Legacy writes to `../logfiles/d4creg.log` and does not print to stdout.
    """
    if time <= 0:
        time = 1e-6

    out = "  Counts on {} = {:10.8g}  ===> counting-rate = {:10.8g} c/s".format(
        detector, counts, counts / time
    )
    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write(out + "\n")

    if reactor_power <= 0:
        reactor_power = 52
    out = "  Reactor-power normalised {} counting-rate = {:10.6g} c/s/MW".format(
        detector, counts / time / reactor_power
    )
    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write(out + "\n")
    return


def getRefLines(Lines: list[str]) -> tuple[int, int, int, int, int, int, int]:  # noqa: N802 (legacy API)
    """
    Determine the reference lines in the ASCII numor files (for D4).

    Returns
    -------
    tuple
        `(lineR, lineAL, lineAI, lineFD, lineFS, lineFM, lineSI)` matching legacy.
    """
    FS: list[int] = []
    AS: list[int] = []
    SS: list[int] = []
    lineR = -1

    for i, line in enumerate(Lines):
        if line[0:10] == "RRRRRRRRRR":
            lineR = i
        if line[0:10] == "FFFFFFFFFF":
            FS.append(i)
        if line[0:10] == "AAAAAAAAAA":
            AS.append(i)
        if line[0:10] == "SSSSSSSSSS":
            SS.append(i)

    if lineR < 0 or len(AS) < 2 or len(FS) < 3 or len(SS) < 1:
        raise ValueError(
            "Invalid ASCII numor file: could not locate reference markers."
        )

    return lineR, AS[0], AS[1], FS[0], FS[1], FS[2], SS[0]


def _parse_float_block(
    lines: list[str],
    data: dict[str, Any],
    start_line: int,
    *,
    cdel: int,
) -> None:
    """
    Parse one legacy 'F' float block into `data`.

    The block layout mirrors `legacy/lib/toscana.py::readD4numorASCII`.
    """
    lref = start_line + 3
    col = (lines[start_line + 1].strip(" ")[:-1]).split()
    ldel = int(col[1]) - 1

    for i in range(ldel):
        for j in range(5):
            label = (lines[lref + i][1 + j * cdel : (j + 1) * cdel]).lstrip(" ")
            raw = (lines[lref + ldel + i][1 + j * cdel : (j + 1) * cdel]).lstrip(" ")
            try:
                parameter = float(raw)
            except Exception:
                parameter = float(0.0)
            data[label] = parameter


def readD4numorASCII(  # noqa: N802 (legacy API)
    filename: str,
) -> tuple[dict[str, Any], NDArray[np.float64]]:
    """
    Read one numor in ASCII format (legacy behavior).

    Returns
    -------
    (data, counts)
        `data` is a mixed-type metadata dict; `counts` is an (ndet, ncell) array.
    """
    with open(filename, "r", encoding="utf-8") as rawdata:
        Lines = rawdata.readlines()

    lineR, lineAL, lineAI, lineFD, lineFS, lineFM, lineSI = getRefLines(Lines)
    cdel = 16

    data: dict[str, Any] = {}
    col = (Lines[lineR + 1].strip(" ")[:-1]).split()
    data["numor"] = str(col[0]).zfill(6)
    data["label"] = Lines[lineAL + 2][:-1]
    data["user"] = Lines[lineAI + 2].strip(" ")[20:-1]
    data["LC"] = Lines[lineAI + 3].strip(" ")[20:-1]
    data["title"] = Lines[lineAI + 4][20:-1]
    data["subtitle"] = Lines[lineAI + 5][20:-1]
    data["proposal"] = Lines[lineAI + 6][20:-1]
    data["startTime"] = Lines[lineAI + 7][20:38]
    data["endTime"] = Lines[lineAI + 7][60:79]

    _parse_float_block(Lines, data, lineFD, cdel=cdel)
    _parse_float_block(Lines, data, lineFS, cdel=cdel)
    _parse_float_block(Lines, data, lineFM, cdel=cdel)

    lref = lineSI
    col = (Lines[lineSI + 1].strip(" ")[:-1]).split()
    ndet = int(col[2])
    data["ndet"] = ndet
    ncell = int(Lines[lref + 3].strip(" ")[:-1])
    data["ncell"] = ncell

    counts: NDArray[np.float64] = np.zeros((ndet, ncell), dtype=np.float64)

    for det in range(ndet):
        for j in range(int(ncell / 10)):
            col = (Lines[lref + 4 + j + 11 * det].strip(" ")[:-1]).split()
            for i in range(len(col)):
                counts[det, i + 10 * j] = float(col[i])

        col = (Lines[lref + 4 + int(ncell / 10) + 11 * det].strip(" ")[:-1]).split()
        for i in range(len(col)):
            counts[det, i + 10 * int(ncell / 10)] = float(col[i])

    print("Numor {} loaded without errors.".format(data["numor"]))
    print(2 * " ", data["subtitle"])
    print("  Starts: {}  Ends: {}".format(data["startTime"], data["endTime"]))
    print("  Counting time ={:10.6g} s".format(data["CntTime (sec)"]))
    print("  Angle (1st cell 1st det) ={:10.6g} degrees".format(data["Theta_lue(deg)"]))
    printRates(
        "monitor",
        float(data["MonitorCnts"]),
        float(data["CntTime (sec)"]),
        float(data.get("RtrPower (MW)", 52.0)),
    )
    printRates(
        "detector",
        float(data["TotalCnts"]),
        float(data["CntTime (sec)"]),
        float(data.get("RtrPower (MW)", 52.0)),
    )
    print()

    return data, counts


def load_nxs(  # noqa: N802 (legacy API)
    nxs_path: str, ncell: int = 64
) -> tuple[dict[str, Any], NDArray[np.float64]]:
    """
    Read one numor in Nexus format (legacy behavior).
    """
    try:
        import h5py  # type: ignore[import-untyped]
    except Exception as exc:  # pragma: no cover
        raise ImportError("load_nxs requires h5py to be installed.") from exc

    with h5py.File(nxs_path, "r") as nxs:
        entry0 = nxs["entry0"]

        metadata: dict[str, Any] = {
            "label": "d4 "
            + entry0["user/name"][0].decode("utf-8")
            + entry0["user/namelocalcontact"][0].decode("utf-8")
            + entry0["start_time"][0].decode("utf-8"),
            "user": entry0["user/name"][0].decode("utf-8"),
            "LC": entry0["user/namelocalcontact"][0].decode("utf-8"),
            "proposal": entry0["user/proposal"][0].decode("utf-8"),
            "ndet": 9,
            "ncell": ncell,
            "RtrPower (MW)": 1,
            "numor": str(entry0["run_number"][0]),
            "subtitle": entry0["experiment_identifier"][0].decode("utf-8"),
            "title": entry0["title"][0].decode("utf-8"),
            "startTime": entry0["start_time"][0].decode("utf-8"),
            "endTime": entry0["end_time"][0].decode("utf-8"),
            "MonitorCnts": entry0["monitor/data"][0, 0, 0],
            "CntTime (sec)": entry0["time"][0],
            "TotalSteps": entry0["data_scan/total_steps"][0],
            "Theta_lue(deg)": entry0["instrument/2theta/value"][0],
            "Theta_des(deg)": entry0["instrument/2theta/target_value"][0],
            "Omega(deg)": entry0["instrument/omega/value"][0],
            "A1": entry0["instrument/A1/value"][0],
        }

        for name, datum in zip(
            entry0["data_scan/scanned_variables/variables_names/property"],
            entry0["data_scan/scanned_variables/data"],
        ):
            decoded = name.decode("utf-8")
            if decoded in ("TotalAcquisitionSpy", "TotalCount"):
                decoded = "TotalCnts"
            metadata[decoded] = datum[0]

        counts_raw = entry0["data_scan/detector_data/data"][0]
        counts = (
            np.asarray(counts_raw)
            .squeeze()
            .reshape(metadata["ndet"], metadata["ncell"])
        )

    return metadata, counts.astype(np.float64, copy=False)


def getOneNumor(  # noqa: N802 (legacy API)
    numorfile: str, runInfo: dict[str, Any]
) -> tuple[
    list[float],
    list[float],
    list[float],
    NDArray[np.float64],
    list[float],
    dict[str, Any],
]:
    """
    Read one numor and compute angle/count/error/Q/cell lists (legacy behavior).
    """
    write = int(runInfo["writeNumor"])
    efffile = str(runInfo["efffile"])
    decfile = str(runInfo["decfile"])

    normalisation = runInfo["normalisation"]
    norm_type = str(normalisation[0])
    norm_time = float(normalisation[1])
    norm_mon = float(normalisation[2])

    dtm = float(runInfo["dead_time"][0])
    dtd = float(runInfo["dead_time"][1])
    cell_tol = runInfo["cellTolerance"]

    if str(runInfo["dataFormat"]) == "Nexus":
        head, counts = load_nxs(numorfile + str(runInfo["ext"][4]))
    else:
        head, counts = readD4numorASCII(numorfile)

    angular_range_cell = float(runInfo["angular_range_bank"]) / float(head["ncell"])
    delta_theta = float(
        np.abs(float(head["Theta_lue(deg)"]) - float(head["Theta_des(deg)"]))
    )

    if delta_theta > float(cell_tol[1]) * angular_range_cell:
        msg = (
            "ERROR! Angle differs from requested angle by more than "
            f"{cell_tol[1]} cell (Angle={head['Theta_lue(deg)']}, requested={head['Theta_des(deg)']})"
        )
        with d4creg_log_path().open("a", encoding="utf-8") as file:
            file.write("   ERROR! The angle differs from the requested angle by\n")
            file.write("          more than {} cell\n".format(cell_tol[1]))
            file.write(
                "          Angle = {} deg, requested angle = {} deg\n".format(
                    head["Theta_lue(deg)"], head["Theta_des(deg)"]
                )
            )
        print("   ERROR! The angle differs from the requested angle by")
        print("          more than {} cell".format(cell_tol[1]))
        print(
            "          Angle = {} deg, requested angle = {} deg".format(
                head["Theta_lue(deg)"], head["Theta_des(deg)"]
            )
        )
        raise ValueError(msg)
    if delta_theta > float(cell_tol[0]) * angular_range_cell:
        with d4creg_log_path().open("a", encoding="utf-8") as file:
            file.write("   WARNING! The angle differs from the requested angle by\n")
            file.write("            more than {} cell\n".format(cell_tol[0]))
            file.write(
                "            Angle = {} deg, requested angle = {} deg\n".format(
                    head["Theta_lue(deg)"], head["Theta_des(deg)"]
                )
            )
        print("   WARNING! The angle differs from the requested angle by ")
        print("            more than {} cell".format(cell_tol[0]))
        print(
            "            Angle = {} deg, requested angle = {} deg".format(
                head["Theta_lue(deg)"], head["Theta_des(deg)"]
            )
        )

    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write("Dead-time corrections\n")

    head["MonitorCnts"] = getDTC_mcounts(
        float(head["MonitorCnts"]), float(head["CntTime (sec)"]), dead_time=dtm
    )
    counts, head["TotalCnts"] = getDTC_dcounts(
        counts.astype(np.float64, copy=False),
        float(head["TotalCnts"]),
        float(head["CntTime (sec)"]),
        dead_time=dtd,
    )

    printRates(
        "monitor",
        float(head["MonitorCnts"]),
        float(head["CntTime (sec)"]),
        float(head.get("RtrPower (MW)", 52.0)),
    )
    printRates(
        "detector",
        float(head["TotalCnts"]),
        float(head["CntTime (sec)"]),
        float(head.get("RtrPower (MW)", 52.0)),
    )

    efficiency = getEff(
        filename=efffile, ndet=int(head["ndet"]), ncells=int(head["ncell"])
    )
    counts = counts / efficiency
    errors = getErrorsNumor(counts.astype(np.float64, copy=False))

    normal = getNormalFactors(float(head["MonitorCnts"]), float(head["CntTime (sec)"]))
    counts, errors = normalise(
        counts.astype(np.float64, copy=False),
        errors.astype(np.float64, copy=False),
        normal,
        norm_type=norm_type,
        norm_time=norm_time,
        norm_mon=norm_mon,
    )

    zeros = getDec(filename=decfile, ndet=int(head["ndet"]))
    angles, cells = getAngles(counts, float(head["Theta_lue(deg)"]), zeros)

    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write(80 * "-" + "\n")

    x: list[float] = []
    y: list[float] = []
    e: list[float] = []
    c: list[float] = []
    for det in range(int(head["ndet"])):
        for cell in range(len(counts[0, :])):
            x.append(float(angles[det][cell]))
            y.append(float(counts[det][cell]))
            e.append(float(errors[det][cell]))
            c.append(float(cells[det][cell]))

    ang = np.array(x, dtype=np.float64)
    q = ang2q(ang, wlength=float(runInfo["wavelength"]))
    if write == 1:
        saveOneNumor(x, y, e, q, c, head, runInfo)
    return x, y, e, q, c, head


def getNumors(  # noqa: N802 (legacy API)
    runInfo: dict[str, Any],
) -> tuple[NDArray[np.float64], list[dict[str, Any]]]:
    """
    Read and stack multiple numors into a single 3D matrix (legacy behavior).
    """
    numor_files = getNumorFiles(list(runInfo["numorLst"]))
    if len(numor_files) == 1:
        runInfo["writeNumor"] = 1

    head: list[dict[str, Any]] = []

    numorfile = str(runInfo["path_raw"]) + numor_files[0]
    with d4creg_log_path().open("a", encoding="utf-8") as file:
        file.write(str(runInfo["file"]) + "\n")
        file.write("Numor 1/{}".format(len(numor_files)) + " " + numor_files[0] + "\n")

    angle, count, error, qval, cell, header = getOneNumor(numorfile, runInfo)
    angle_arr = np.array(angle, dtype=np.float64)
    head.append(header)

    numor: NDArray[np.float64] = np.zeros(
        (len(numor_files), 5, len(angle_arr)), dtype=np.float64
    )
    numor[0, 0, :] = angle_arr - float(runInfo["twotheta0"])
    numor[0, 1, :] = np.asarray(count, dtype=np.float64)
    numor[0, 2, :] = np.asarray(error, dtype=np.float64)
    numor[0, 3, :] = np.asarray(qval, dtype=np.float64)
    numor[0, 4, :] = np.asarray(cell, dtype=np.float64)

    for i in range(1, len(numor_files)):
        numorfile = str(runInfo["path_raw"]) + numor_files[i]
        with d4creg_log_path().open("a", encoding="utf-8") as file:
            file.write(
                "Numor {}/{}".format(i + 1, len(numor_files))
                + " "
                + numor_files[i]
                + "\n"
            )

        angle, count, error, qval, cell, header = getOneNumor(numorfile, runInfo)
        angle_arr = np.array(angle, dtype=np.float64)
        head.append(header)

        numor[i, 0, :] = angle_arr - float(runInfo["twotheta0"])
        numor[i, 1, :] = np.asarray(count, dtype=np.float64)
        numor[i, 2, :] = np.asarray(error, dtype=np.float64)
        numor[i, 3, :] = np.asarray(qval, dtype=np.float64)
        numor[i, 4, :] = np.asarray(cell, dtype=np.float64)

    return numor, head
