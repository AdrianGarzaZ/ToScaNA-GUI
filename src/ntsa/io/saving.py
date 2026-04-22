from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np


def saveFile_xye(  # noqa: N802 (legacy API)
    filename: str,
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    e: Sequence[float] | np.ndarray,
    heading: Sequence[str],
) -> None:
    """
    Create a 3-column ASCII file with x, y, error (legacy behavior).

    Notes
    -----
    Parity-first copy of `legacy/lib/toscana.py::saveFile_xye`, including
    formatting and print message.
    """
    with open(filename, "w") as datafile:
        datafile.write("# " + filename + "\n")
        for i in range(len(heading)):
            datafile.write("# " + heading[i] + "\n")
        for i in range(len(x)):
            datafile.write(
                "{: 9.3f}".format(x[i])
                + " "
                + "{:18.6f}".format(y[i])
                + " "
                + "{:18.6f}".format(e[i])
                + "\n"
            )
        print("File " + filename + " saved")
    return


def saveFile_3col(  # noqa: N802 (legacy API)
    filename: str,
    data: np.ndarray,
    heading: Sequence[str],
) -> None:
    """
    Create a 3-column ASCII file with x, y, error from a Nx3 array (legacy behavior).
    """
    x = data[:, 0]
    y = data[:, 1]
    e = data[:, 2]
    with open(filename, "w") as datafile:
        datafile.write("# " + filename + "\n")
        for i in range(len(heading)):
            datafile.write("# " + heading[i] + "\n")
        for i in range(len(x)):
            datafile.write(
                "{: 9.3f}".format(x[i])
                + " "
                + "{:18.6f}".format(y[i])
                + " "
                + "{:18.6f}".format(e[i])
                + "\n"
            )
        print("File " + filename + " saved")
    return


def saveCorrelations(  # noqa: N802 (legacy API)
    filename: str,
    ar: Sequence[float] | np.ndarray,
    pcf: Sequence[float] | np.ndarray,
    pdf: Sequence[float] | np.ndarray,
    rdf: Sequence[float] | np.ndarray,
    tor: Sequence[float] | np.ndarray,
    run: Sequence[float] | np.ndarray,
    heading: Sequence[str],
) -> None:
    """
    Create a 6-column ASCII file with real-space correlation functions (legacy behavior).
    """
    with open(filename, "w") as datafile:
        datafile.write("# " + filename + "\n")
        datafile.writelines("# " + line + "\n" for line in heading)
        for vals in zip(ar, pcf, pdf, rdf, tor, run):
            datafile.write(
                "{:9.3f} {:12.6f} {:12.6f} {:12.6f} {:12.6f} {:12.6f}\n".format(*vals)
            )
    print("File " + filename + " saved")
    return


def saveOneNumor(  # noqa: N802 (legacy API)
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    e: Sequence[float] | np.ndarray,
    q: Sequence[float] | np.ndarray,
    c: Sequence[float] | np.ndarray,
    head: dict[str, Any],
    runInfo: dict[str, Any],
) -> None:
    """
    Save an individual file for a single numor (legacy behavior).

    Notes
    -----
    Writes `{head["numor"]}{runInfo["ext"][3]}` in the current working directory.
    """
    filename = str(head["numor"]) + str(runInfo["ext"][3])
    # Legacy uses the platform default encoding; preserve for byte-level parity.
    with open(filename, "w") as datafile:
        datafile.write("# {} \n".format(filename))
        datafile.write("# Sample: {}\n".format(head["subtitle"]))
        datafile.write(
            "# Starts: {}  Ends: {} \n".format(head["startTime"], head["endTime"])
        )
        datafile.write("# Counting time: {:8.4f} s\n".format(head["CntTime (sec)"]))
        datafile.write(
            "# Monitor: {:10.2f} counts ({:8.2f} c/s)\n".format(
                head["MonitorCnts"], head["MonitorCnts"] / head["CntTime (sec)"]
            )
        )
        datafile.write(
            "# Detector: {:10.2f} counts ({:8.2f} c/s)\n".format(
                head["TotalCnts"], head["TotalCnts"] / head["CntTime (sec)"]
            )
        )
        datafile.write("#" + 80 * "-" + "\n")
        datafile.write(
            "# Angle(deg)"
            + 6 * " "
            + "Counts"
            + 14 * " "
            + "Error"
            + 8 * " "
            + "Q(1/Å)"
            + 6 * " "
            + "Cell \n"
        )
        for i in range(len(x)):
            datafile.write(
                "{: 9.3f} {:18.6f} {:18.6f} {:9.3f} {:9.0f}".format(
                    x[i], y[i], e[i], q[i], c[i]
                )
                + "\n"
            )
        print("File {} saved.".format(filename))
    return


def saveRSCF(  # noqa: N802 (legacy API)
    filename: str,
    fou: Sequence[Sequence[float]] | np.ndarray,
    heading: Sequence[str],
) -> None:
    """
    Create a 6-column ASCII file from a Nx6 array `fou` (legacy behavior).
    """
    with open(filename, "w") as datafile:
        datafile.write("# " + filename + "\n")
        for i in range(len(heading)):
            datafile.write("# " + heading[i] + "\n")
        for i in range(len(fou)):
            row: Any = fou[i]
            datafile.write(
                "{: 9.3f}".format(row[0])
                + " "
                + "{:12.6f}".format(row[1])
                + " "
                + "{:12.6f}".format(row[2])
                + " "
                + "{:12.6f}".format(row[3])
                + " "
                + "{:12.6f}".format(row[4])
                + " "
                + "{:12.6f}".format(row[5])
                + "\n"
            )
        print("File " + filename + " saved")
    return
