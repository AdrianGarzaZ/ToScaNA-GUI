from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ntsa.math.line_shapes import GaussianA
from ntsa.physics.crystallography import reflections_fcc

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def niPeaks10(
    x: ArrayLike,
    I0: float,
    slope: float,
    quad: float,
    wavelength: float,
    twotheta0: float,
    A0: float,
    A1: float,
    A2: float,
    A3: float,
    A4: float,
    A5: float,
    A6: float,
    A7: float,
    A8: float,
    A9: float,
    G0: float,
    G1: float,
    G2: float,
    G3: float,
    G4: float,
    G5: float,
    G6: float,
    G7: float,
    G8: float,
    G9: float,
    S0: float,
    S1: float,
    S2: float,
    S3: float,
    S4: float,
    S5: float,
    S6: float,
    S7: float,
    S8: float,
    S9: float,
) -> NDArray[np.float64]:
    """
    Evaluate a model with 10 asymmetric Gaussian peaks for Ni fcc reflections (legacy behavior).
    """
    q = np.asarray(x, dtype=np.float64)
    C0, C1, C2, C3, C4, C5, C6, C7, C8, C9 = reflections_fcc(
        wavelength, twotheta0, lattice=3.52024
    )[:10]

    diff = (
        I0
        + slope * q
        + quad * q * q
        + (
            GaussianA(q, A0, C0, S0, G0)
            + GaussianA(q, A1, C1, S1, G1)
            + GaussianA(q, A2, C2, S2, G2)
            + GaussianA(q, A3, C3, S3, G3)
            + GaussianA(q, A4, C4, S4, G4)
            + GaussianA(q, A5, C5, S5, G5)
            + GaussianA(q, A6, C6, S6, G6)
            + GaussianA(q, A7, C7, S7, G7)
            + GaussianA(q, A8, C8, S8, G8)
            + GaussianA(q, A9, C9, S9, G9)
        )
    )
    return np.asarray(diff, dtype=np.float64)
