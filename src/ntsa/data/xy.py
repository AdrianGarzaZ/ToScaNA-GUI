from __future__ import annotations

import os
import statistics as st
from typing import TYPE_CHECKING

import numpy as np

from ntsa.math.peak_finding import find_minimum_within_range, find_peaks_in_range

if TYPE_CHECKING:
    from numpy.typing import NDArray


class DataXYE:
    """
    Read ASCII data files with 2 (X Y) or 3 (X Y E) columns (legacy behavior).

    Notes
    -----
    This mirrors the final `DataXYE` definition in `legacy/lib/toscana.py`, which
    is the effective one at runtime (the legacy file defines `DataXYE` twice).
    """

    filename: str
    basename: str
    ext: str
    x: NDArray[np.float64]
    y: NDArray[np.float64]
    e: NDArray[np.float64]
    head: list[str]

    xave: float
    xmin: float
    xmax: float
    yave: float
    ymin: float
    ymax: float
    eave: float
    emin: float
    emax: float

    peaks_x: NDArray[np.float64]
    peaks_y: NDArray[np.float64]
    xminr: np.float64
    yminr: np.float64

    def __init__(self, filename: str):
        self.filename = filename
        self.basename = os.path.splitext(filename)[0]
        self.ext = os.path.splitext(filename)[1][1:]

        x_list: list[float] = []
        y_list: list[float] = []
        e_list: list[float] = []
        head: list[str] = []

        with open(self.filename, "r") as data:
            for dataline in data.readlines():
                row = dataline.strip(" ").strip()
                if not row:
                    continue
                if row[0] in {"#", "!"}:
                    head.append(row)
                    continue

                columns = row.split()
                if len(columns) == 2:
                    x_list.append(float(columns[0]))
                    y_list.append(float(columns[1]))
                    e_list.append(-1.0)
                elif len(columns) == 3:
                    x_list.append(float(columns[0]))
                    y_list.append(float(columns[1]))
                    e_list.append(float(columns[2]))
                else:
                    # Legacy prints and exits; prefer CI-safe exception behavior.
                    raise ValueError("Wrong file format: expected 2 or 3 columns.")

        self.head = head
        self.x = np.asarray(x_list, dtype=np.float64)
        self.y = np.asarray(y_list, dtype=np.float64)
        self.e = np.asarray(e_list, dtype=np.float64)

        self.xave = float(st.mean(self.x))
        self.xmin = float(min(self.x))
        self.xmax = float(max(self.x))

        self.yave = float(st.mean(self.y))
        self.ymin = float(min(self.y))
        self.ymax = float(max(self.y))

        self.eave = float(st.mean(self.e))
        self.emin = float(min(self.e))
        self.emax = float(max(self.e))

        self.peaks_x, self.peaks_y = find_peaks_in_range(self.x, self.y, 5.0, 40.0)
        self.xminr, self.yminr = find_minimum_within_range(self.x, self.y, 5.0, 40.0)

    def plot(
        self,
        file_format: str | int = 0,
        xmin: float | None = None,
        xmax: float | None = None,
        ymin: float | None = None,
        ymax: float | None = None,
    ) -> None:
        # Lazy import so using the data model doesn't require matplotlib at import time.
        import matplotlib.pyplot as plt

        a_ext = ["adat", "Adat", "reg"]
        q_ext = ["qdat", "Qdat", "Qreg", "soq", "SoQ"]
        r_ext = ["pcf", "pdf", "tor", "rdf", "run"]

        plt.figure(figsize=(9, 6))
        plt.plot(self.x, self.y, "r-+", label=self.filename)

        plt.legend(loc="best")
        plt.title("Data in " + self.filename)
        plt.xlabel("Abscissa")
        if self.ext in a_ext:
            plt.xlabel(r"$2\theta$ (˚)")
        elif self.ext in q_ext:
            plt.xlabel(r"$Q$ (Å$^{-1}$)")
        elif self.ext in r_ext:
            plt.xlabel("$R$ (Å)")
        plt.ylabel("Intensity (arb. units)")
        plt.axis([xmin, xmax, ymin, ymax])  # type: ignore[arg-type]
        plt.grid(True)
        plt.tight_layout()
        plt.show()

        if file_format in ["png", "pdf", "jpg", "tiff", "svg", "jpeg", "ps", "eps"]:
            file_fig = "../regdata/" + self.basename + "." + str(file_format)
            plt.savefig(file_fig, format=str(file_format))
            print(f"Figure saved on {file_fig}")

    def show(self) -> None:
        a_ext = ["adat", "Adat", "reg"]
        q_ext = ["qdat", "Qdat", "Qreg", "soq", "SoQ"]
        r_ext = ["pcf", "pdf", "tor", "rdf", "run"]

        if self.ext in a_ext:
            print(f"{'Ang':>6}{'Intensity':>12}{'Error':>12}")
        elif self.ext in q_ext:
            print(f"{'Q':>6}{'Intensity':>12}{'Error':>12}")
        elif self.ext in r_ext:
            print(f"{'R':>6}{'Intensity':>12}{'Ignore':>12}")
        else:
            print(f"{'x':>6}{'y':>12}{'e':>12}")

        for i in range(len(self.x)):
            print(f"{self.x[i]:>6}{self.y[i]:>12}{self.e[i]:>12}")

    def header(self, lines: int = 1000) -> None:
        for i in range(min(lines, len(self.head))):
            print(f"{i + 1:>3} {self.head[i]}")


class DataXYE_old(DataXYE):
    """
    Legacy-compatible alias of `DataXYE_old` (kept for parity with legacy API).
    """


class DataXYE2:
    def __init__(self, file: str):
        self.data: NDArray[np.float64] = np.loadtxt(file, dtype=np.float64)
        self.file = file
        # Legacy uses `self.filename` in `plot()` but only sets `self.file`.
        # Defining both keeps behavior predictable.
        self.filename = file

        self.title = "Plotting " + self.file
        self.labelx = "Axis X"
        self.labely = "Axis Y"
        self.color = "blue"
        self.curve = "-"
        self.scale = "a"
        self.superplot = False

    def plot(
        self,
        scale: str = "a",
        superplot: bool = False,
        title: str | None = None,
        labelx: str | None = None,
        labely: str | None = None,
        color: str | None = None,
        curve: str | None = None,
    ) -> None:
        import matplotlib.pyplot as plt

        title = title if title is not None else self.title
        labelx = labelx if labelx is not None else self.labelx
        labely = labely if labely is not None else self.labely
        color = color if color is not None else self.color
        curve = curve if curve is not None else self.curve

        if not superplot:
            plt.figure(figsize=(9, 6))

        plt.plot(
            self.data[:, 0],
            self.data[:, 1],
            color=color,
            linestyle=curve,
            label=self.filename,
        )

        plt.legend(loc="best")
        plt.title("Data in " + self.file if title is None else title)
        plt.ylabel("Intensity (arb. units)")
        if scale == "Q" or scale == "q":
            plt.xlabel(r"$Q$ (Å$^{-1}$)")
        elif scale == "A" or scale == "a":
            plt.xlabel(r"$2\theta$ (˚)")
        elif scale == "R" or scale == "r":
            plt.xlabel("$R$ (Å)")
        else:
            plt.xlabel(labelx)
            plt.ylabel(labely)

        x_range = np.ptp(self.data[:, 0])
        y_range = np.ptp(self.data[:, 1])

        plt.axis(
            [  # type: ignore[arg-type]
                float(np.min(self.data[:, 0]) - 0.1 * x_range),
                float(np.max(self.data[:, 0]) + 0.1 * x_range),
                float(np.min(self.data[:, 1]) - 0.1 * y_range),
                float(np.max(self.data[:, 1]) + 0.1 * y_range),
            ]
        )
        plt.grid(True)
        plt.tight_layout()
        if not superplot:
            plt.show()


class DataXYE0:
    def __init__(
        self,
        filename: str,
        symbol: str = "r-+",
        save: bool = False,  # noqa: FBT001 (legacy API)
        scale: str = "a",
        superplot: bool = False,  # noqa: FBT001 (legacy API)
        xmin: float | None = None,
        xmax: float | None = None,
        ymin: float | None = None,
        ymax: float | None = None,
    ):
        self.data: NDArray[np.float64] = np.loadtxt(filename, dtype=np.float64)
        self.filename = filename
        self.ext = os.path.splitext(filename)[1][1:]
        self.x = self.data[:, 0]
        self.y = self.data[:, 1]
        self.e = self.data[:, 2]

        self.xave = float(st.mean(self.x))
        self.xmin = float(min(self.x))
        self.xmax = float(max(self.x))
        self.yave = float(st.mean(self.y))
        self.ymin = float(min(self.y))
        self.ymax = float(max(self.y))
        self.eave = float(st.mean(self.e))
        self.emin = float(min(self.e))
        self.emax = float(max(self.e))

        self.scale = scale
        self.symbol = symbol
        self.minx = xmin
        self.maxx = xmax
        self.miny = ymin
        self.maxy = ymax

        # Preserve legacy "save" parameter (no side effects implemented here).
        _ = save
        _ = superplot

    def plot(
        self,
        symbol: str,
        superplot: bool = False,  # noqa: FBT001 (legacy API)
        xmin: float | None = None,
        xmax: float | None = None,
        ymin: float | None = None,
        ymax: float | None = None,
    ) -> None:
        import matplotlib.pyplot as plt

        if not superplot:
            plt.figure(figsize=(9, 6))
        _ = symbol  # legacy arg is unused (self.symbol is used instead)

        print("***", self.symbol)
        plt.plot(self.x, self.y, self.symbol, label=self.filename)

        plt.legend(loc="best")
        plt.title("Data in " + self.filename)
        if self.scale == "Q" or self.scale == "q":
            plt.xlabel(r"$Q$ (Å$^{-1}$)")
        elif self.scale == "A" or self.scale == "a":
            plt.xlabel(r"$2\theta$ (˚)")
        elif self.scale == "R" or self.scale == "r":
            plt.xlabel("$R$ (Å)")
        else:
            plt.xlabel("Abscissa")
        plt.ylabel("Intensity (arb. units)")
        plt.axis([xmin, xmax, ymin, ymax])  # type: ignore[arg-type]
        plt.grid(True)
        plt.tight_layout()

        if not superplot:
            plt.show()

    def show(self) -> None:
        for i in range(len(self.x)):
            print(f"{self.x[i]:>6}{self.y[i]:>12}{self.e[i]:>12}")

    def save(self, filename: str) -> None:
        x = self.data[:, 0]
        y = self.data[:, 1]
        e = self.data[:, 2]
        with open(filename, "w") as datafile:
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
