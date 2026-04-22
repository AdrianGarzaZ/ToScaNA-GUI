from __future__ import annotations

from typing import Optional, Protocol, Sequence


class PlotLike(Protocol):
    def title(self, label: Optional[str] = ...) -> object: ...

    def xlabel(self, label: Optional[str] = ...) -> object: ...

    def ylabel(self, label: Optional[str] = ...) -> object: ...

    def axis(self, limits: Sequence[Optional[float]]) -> object: ...

    def grid(self, visible: bool = ...) -> object: ...

    def legend(self, loc: str = ...) -> object: ...


def plotQ(
    plt: PlotLike,
    title: Optional[str] = None,
    xmin: float = 0,
    xmax: float = 25,
    ymin: Optional[float] = None,
    ymax: Optional[float] = None,
    ylabel: str = "Intensity (arb. units)",
) -> None:
    plt.title(title)
    plt.xlabel(r"$Q ({\rm \AA}^{-1}$)")
    plt.ylabel(ylabel)
    plt.axis([xmin, xmax, ymin, ymax])
    plt.grid(True)
    plt.legend(loc="best")


def plotA(
    plt: PlotLike,
    title: Optional[str] = None,
    xmin: float = 0,
    xmax: float = 140,
    ymin: Optional[float] = None,
    ymax: Optional[float] = None,
    ylabel: str = "Intensity (arb. units)",
) -> None:
    plt.title(title)
    plt.xlabel(r"$2\theta$ ($^o$)")
    plt.ylabel(ylabel)
    plt.axis([xmin, xmax, ymin, ymax])
    plt.grid(True)
    plt.legend(loc="best")


def plotR(
    plt: PlotLike,
    title: Optional[str] = None,
    xmin: float = 0,
    xmax: float = 20,
    ymin: Optional[float] = None,
    ymax: Optional[float] = None,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
) -> None:
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.axis([xmin, xmax, ymin, ymax])
    plt.grid(True)
    plt.legend(loc="best")
