from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def ang2q(x: ArrayLike, wlength: float = 0.5) -> NDArray[np.float64]:
    """
    Convert scattering angle (2θ, degrees) to momentum transfer Q (1/Å).

    Uses Bragg law:
        Q = 4π/λ * sin((2θ)/2 * π/180)

    Parameters
    ----------
    x
        Scattering angle(s) 2θ in degrees.
    wlength
        Wavelength λ in Å. Must be positive.

    Returns
    -------
    numpy.ndarray
        Q value(s) in 1/Å.
    """
    if wlength <= 0:
        raise ValueError("Wrong wavelength in ang2q function")
    x_arr: NDArray[np.float64] = np.asarray(x, dtype=np.float64)
    return (4.0 * np.pi / wlength) * np.sin(x_arr / 2.0 * np.pi / 180.0)


def q2ang(x: ArrayLike, wlength: float = 0.5) -> NDArray[np.float64]:
    """
    Convert momentum transfer Q (1/Å) to scattering angle (2θ, degrees).

    Uses Bragg law:
        2θ = 360/π * arcsin(Q * λ / 4π)

    Parameters
    ----------
    x
        Q value(s) in 1/Å.
    wlength
        Wavelength λ in Å. Must be positive.

    Returns
    -------
    numpy.ndarray
        Scattering angle(s) 2θ in degrees.
    """
    if wlength <= 0:
        raise ValueError("Wrong wavelength in q2ang function")
    x_arr: NDArray[np.float64] = np.asarray(x, dtype=np.float64)
    return (360.0 / np.pi) * np.arcsin(x_arr * wlength / 4.0 / np.pi)
