from __future__ import annotations

from pathlib import Path
from ntsa.workflows.d4creg import d4creg


def readParam(parametersFile: str) -> dict[str, object]:  # noqa: N802 (legacy API)
    runInfo: dict[str, object] = {}

    angular_range_bank = 8.0
    dead_time: tuple[float, float] = (2.4e-6, 7.0e-6)
    cell_tolerance: tuple[float, float] = (0.1, 1.0)
    data_format = "Nexus"

    path_raw = "rawdata/"
    ext: tuple[str, str, str, str, str, str] = (
        ".reg",
        ".adat",
        ".qdat",
        ".cdat",
        ".nxs",
        ".log",
    )
    efffile = "effd4c.eff"
    decfile = "dec.dec"
    logfile = "d4creg" + ext[5]

    normalisation: tuple[str, float, float] = ("monitor", 80.0, 1000000.0)
    write_numor = 0
    plot_diff = 0
    twotheta0 = -0.1013
    wavelength = 0.49857
    angular_scale: tuple[float, float, float] = (0.0, 140.0, 0.125)
    q_scale: tuple[float, float, float] = (0.0, 23.8, 0.02)

    file_base = "vanadium"
    numor_lst: list[str] = ["387229-387288"]

    runInfo["angular_range_bank"] = angular_range_bank
    runInfo["dead_time"] = dead_time
    runInfo["cellTolerance"] = cell_tolerance
    runInfo["dataFormat"] = data_format

    runInfo["path_raw"] = path_raw
    runInfo["ext"] = ext
    runInfo["efffile"] = efffile
    runInfo["decfile"] = decfile
    runInfo["logfile"] = logfile

    runInfo["normalisation"] = normalisation
    runInfo["writeNumor"] = write_numor
    runInfo["plotDiff"] = plot_diff
    runInfo["twotheta0"] = twotheta0
    runInfo["wavelength"] = wavelength
    runInfo["angular_scale"] = angular_scale
    runInfo["q_scale"] = q_scale

    runInfo["file"] = file_base
    runInfo["numorLst"] = numor_lst

    # Legacy writes a logfile in a fixed relative location.
    log_path = Path("../logfiles/d4creg.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("# d4creg.log\n\n", encoding="utf-8")

    lines = Path(parametersFile).read_text(encoding="utf-8").splitlines(keepends=True)

    for i, line in enumerate(lines):
        if len(line) > 1:
            first = (line[0] != "#") and (line[0] != "!") and (line[0] != "<")
            if first:
                raise ValueError(f"Wrong input in line: {i + 1} file: {parametersFile}")

    for i, raw in enumerate(lines):
        if (raw[0] == "#") or (raw[0] == "!"):
            continue
        if len(raw) == 1:
            continue
        if (raw[0] == "<") and (raw[4] == ">"):
            parts = raw.split(" ")
            tag = parts[0]

            if tag == "<tol>":
                cell_tolerance = (float(parts[1]), float(parts[2]))
                runInfo["cellTolerance"] = cell_tolerance
                print(
                    "Cell tolerance: {} cells for warning, {} cells for error".format(
                        *cell_tolerance
                    )
                )
            if tag == "<tau>":
                dead_time = (float(parts[1]), float(parts[2]))
                runInfo["dead_time"] = dead_time
                print(
                    "Dead times: {} s for monitor, {} s for detector".format(*dead_time)
                )
            if tag == "<ext>":
                ext = (
                    parts[1],
                    parts[2],
                    parts[3],
                    parts[4],
                    parts[5],
                    parts[6],
                )
                runInfo["ext"] = ext
                print("Extensions: {}, {}, {}, {}, {}, {}".format(*ext))
            if tag == "<eff>":
                efffile = parts[1]
                runInfo["efffile"] = efffile
                print("Efficiency file: {}".format(efffile))
            if tag == "<dec>":
                decfile = parts[1]
                runInfo["decfile"] = decfile
                print("Shifts file: {}".format(decfile))
            if tag == "<log>":
                logfile = parts[1]
                runInfo["logfile"] = logfile
                # Legacy prints decfile here (bug); preserve message.
                print("Shifts file: {}".format(decfile))
            if tag == "<fmt>":
                data_format = parts[1]
                runInfo["dataFormat"] = data_format
                print("Data format: {}".format(data_format))
            if tag == "<asc>":
                angular_scale = (float(parts[1]), float(parts[2]), float(parts[3]))
                runInfo["angular_scale"] = angular_scale
                print(
                    "Angular scale: from {} deg to {} deg in steps of {} deg".format(
                        *angular_scale
                    )
                )
            if tag == "<qsc>":
                q_scale = (float(parts[1]), float(parts[2]), float(parts[3]))
                runInfo["q_scale"] = q_scale
                delta_a = angular_scale[1] - angular_scale[0]
                delta_q = q_scale[1] - q_scale[0]
                recommended_dq = angular_scale[2] / delta_a * delta_q
                print(f"Recommended dQ for the user is : {recommended_dq:.4f} 1/A")
                print(
                    "Q scale: from {} 1/A to {} 1/A in steps of {} 1/A".format(*q_scale)
                )
            if tag == "<wri>":
                write_numor = 1 if parts[1] == "True" else 0
                runInfo["writeNumor"] = write_numor
                print(
                    "Write individual files for each numor: {} {}".format(
                        parts[1], write_numor
                    )
                )
            if tag == "<plo>":
                plot_diff = 1 if parts[1] == "True" else 0
                runInfo["plotDiff"] = plot_diff
                print("Plot diffractograms: {} {}".format(parts[1], plot_diff))
            if tag == "<wle>":
                wavelength = float(parts[1])
                runInfo["wavelength"] = wavelength
                print("Incident wavelength: {} A".format(wavelength))
            if tag == "<zac>":
                twotheta0 = float(parts[1])
                runInfo["twotheta0"] = twotheta0
                print("Zero-angle: {} deg".format(twotheta0))
            if tag == "<rdp>":
                path_raw = parts[1]
                runInfo["path_raw"] = path_raw
                print("Relative path for rawdata: {}".format(path_raw))
            if tag == "<nor>":
                normalisation = (parts[1], float(parts[2]), float(parts[3]))
                runInfo["normalisation"] = normalisation
                print("Normalisation mode: {}".format(normalisation[0]))
                print(
                    "Normalisation constants: {1} s or {2} monitor counts".format(
                        *normalisation
                    )
                )
            if tag == "<out>":
                file_base = parts[1]
                runInfo["file"] = file_base
                print("Base name for output files: {}".format(file_base))
            if tag == "<num>":
                numor_lst = [parts[1]]
                runInfo["numorLst"] = numor_lst
                print("List of numors: {}".format(numor_lst))
            if tag == "<add>":
                numor_lst.append(parts[1])
                runInfo["numorLst"] = numor_lst
                print("List of numors: {}".format(numor_lst))
            elif tag == "<run>":
                print("Calling d4creg...")
                d4creg(runInfo)
        else:
            raise ValueError(f"Input error in line: {i + 1} file: {parametersFile}")

    return runInfo
