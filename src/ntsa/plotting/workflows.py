from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np


def defColors() -> list[str]:  # noqa: N802 (legacy API)
    """
    Define a deterministic list of CSS4 colors (legacy behavior).
    """
    import matplotlib.colors as mcolors

    colors: list[str] = []
    colors.append(str(mcolors.CSS4_COLORS["red"]))  # 0
    colors.append(str(mcolors.CSS4_COLORS["blue"]))  # 1
    colors.append(str(mcolors.CSS4_COLORS["green"]))  # 2
    colors.append(str(mcolors.CSS4_COLORS["black"]))  # 3
    colors.append(str(mcolors.CSS4_COLORS["cyan"]))  # 4
    colors.append(str(mcolors.CSS4_COLORS["magenta"]))  # 5
    colors.append(str(mcolors.CSS4_COLORS["gold"]))  # 6
    colors.append(str(mcolors.CSS4_COLORS["orange"]))  # 7
    colors.append(str(mcolors.CSS4_COLORS["brown"]))  # 8
    colors.append(str(mcolors.CSS4_COLORS["gray"]))  # 9
    colors.append(str(mcolors.CSS4_COLORS["silver"]))  # 10
    colors.append(str(mcolors.CSS4_COLORS["pink"]))  # 11
    colors.append(str(mcolors.CSS4_COLORS["purple"]))  # 12
    colors.append(str(mcolors.CSS4_COLORS["navy"]))  # 13
    colors.append(str(mcolors.CSS4_COLORS["teal"]))  # 14
    colors.append(str(mcolors.CSS4_COLORS["lime"]))  # 15
    colors.append(str(mcolors.CSS4_COLORS["olive"]))  # 16
    colors.append(str(mcolors.CSS4_COLORS["salmon"]))  # 17
    colors.append(str(mcolors.CSS4_COLORS["maroon"]))  # 18
    colors.append(str(mcolors.CSS4_COLORS["chartreuse"]))  # 19
    return colors


def makePlotsA(  # noqa: N802 (legacy API)
    runInfo: Mapping[str, Any],
    diffA: np.ndarray,
    head: Sequence[Mapping[str, Any]],
    numor: np.ndarray,
) -> None:
    """
    Plot angular-scale diffractograms (legacy behavior).
    """
    import matplotlib.pyplot as plt

    colors = defColors()
    plt.figure(figsize=(9, 5))
    plt.title(
        "Individual numors ({} in total) for sample {}".format(
            runInfo["nbrNumors"], runInfo["file"]
        )
    )

    amin, amax = runInfo["angular_scale"][0], runInfo["angular_scale"][1]
    ymin, ymax = 0.9 * np.nanmin(diffA[0, 1, :]), 1.1 * np.nanmax(diffA[0, 1, :])
    plt.axis((amin, amax, ymin, ymax))
    plt.xlabel("Scattering angle (degrees)")
    if runInfo["normalisation"][0] == "monitor":
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][2]) + " monitor counts)")
    else:
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][1]) + " seconds)")
    for i in range(numor.shape[0]):
        plt.plot(numor[i, 0, :], numor[i, 1, :], colors[i % 20], label=head[i]["numor"])
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(9, 6))
    plt.title("Individual detectors for " + runInfo["file"])
    amin, amax = runInfo["angular_scale"][0], runInfo["angular_scale"][1]
    ymin, ymax = 0.9 * np.nanmin(diffA[0, 1, :]), 1.1 * np.nanmax(diffA[0, 1, :])
    plt.axis((amin, amax, ymin, ymax))
    plt.xlabel("Scattering angle (degrees)")
    if runInfo["normalisation"][0] == "monitor":
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][2]) + " monitor counts)")
    else:
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][1]) + " seconds)")
    for i in range(1, 10):
        plt.plot(diffA[i, 0, :], diffA[i, 1, :], colors[i], label="Detector " + str(i))
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()

    plt.figure(figsize=(9, 6))
    plt.title("Diffractogram for " + runInfo["file"])
    amin, amax = runInfo["angular_scale"][0], runInfo["angular_scale"][1]
    ymin, ymax = 0.9 * np.nanmin(diffA[0, 1, :]), 1.1 * np.nanmax(diffA[0, 1, :])
    plt.axis((amin, amax, ymin, ymax))
    plt.xlabel("Scattering angle (degrees)")
    if runInfo["normalisation"][0] == "monitor":
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][2]) + " monitor counts)")
    else:
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][1]) + " seconds)")
    plt.plot(
        diffA[0, 0, :],
        diffA[0, 1, :],
        color=colors[0],
        linestyle="solid",
        label=runInfo["file"],
    )
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()
    return


def makePlotsQ(  # noqa: N802 (legacy API)
    runInfo: Mapping[str, Any],
    diffQbin: np.ndarray,
    head: Sequence[Mapping[str, Any]],
    numor: np.ndarray,
) -> None:
    """
    Plot Q-scale diffractograms (legacy behavior).
    """
    import matplotlib.pyplot as plt

    colors = defColors()
    plt.figure(figsize=(9, 6))
    plt.title("Diffractogram for " + runInfo["file"])
    qmin, qmax = runInfo["q_scale"][0], runInfo["q_scale"][1]
    ymin, ymax = 0.9 * np.nanmin(diffQbin[:, 1]), 1.1 * np.nanmax(diffQbin[:, 1])
    plt.axis((qmin, qmax, ymin, ymax))
    plt.xlabel("Momentum transfer (1/Å)")
    if runInfo["normalisation"][0] == "monitor":
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][2]) + " monitor counts)")
    else:
        plt.ylabel("Counts/(" + str(runInfo["normalisation"][1]) + " seconds)")
    plt.plot(
        diffQbin[:, 0],
        diffQbin[:, 1],
        color=colors[0],
        linestyle="solid",
        label=runInfo["file"],
    )
    plt.legend(loc="best")
    plt.grid(True)
    plt.show()
    return
