from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy import integrate  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from numpy.typing import NDArray


def Lorch(q: float, qmax: float = 23.5) -> float:  # noqa: N802 (legacy API)
    """
    Evaluate the Lorch window function (legacy behavior).

    Notes
    -----
    This is the scalar version used by legacy `sineFT`.
    """
    if qmax <= 0:
        print("ERROR: Non positive value for qmax in Lorch function.")
        return -999

    if (q < 0.0) or (q >= qmax):
        return 0.0
    if q == 0.0:
        return 1.0

    a = q * np.pi / qmax
    return float(np.sin(a) / a)


def LorchN(Q: NDArray[np.float64], Qmax: float = 0) -> NDArray[np.float64]:  # noqa: N802 (legacy API)
    """
    Evaluate the normalised Lorch function over an array (legacy behavior).
    """
    if (Qmax <= 0) or (Qmax > Q[-1]):
        Qmax = float(Q[-1])

    lorch: NDArray[np.float64] = np.ones(len(Q), dtype=np.float64)
    for i in range(len(Q)):
        if (Q[i] < 0.0) or (Q[i] >= Qmax):
            lorch[i] = 0.0
        elif Q[i] != 0.0:
            a = float(Q[i]) * np.pi / Qmax
            lorch[i] = float(np.sin(a) / a)
        else:
            lorch[i] = 1.0

    integral_lorch = integrate.simpson(lorch, Q)
    for i in range(len(Q)):
        lorch[i] *= Qmax / float(integral_lorch)
    return lorch
