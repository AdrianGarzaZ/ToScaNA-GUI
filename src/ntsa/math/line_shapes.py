from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import ArrayLike, NDArray


def sigmoidal(
    Q: ArrayLike,
    lowQ: float = 0.4,
    highQ: float = 0.2,
    Q0: float = 7.0,
    dQ: float = 2.4,
) -> NDArray[np.float64]:
    """
    Calculate a sigmoidal-like function, preserving legacy behavior.

    Notes
    -----
    The legacy implementation uses:
        delta = exp((Q - Q0) / dQ)
        return delta*lowQ + (1-delta)*highQ
    which is not a standard logistic form, but we preserve it for parity.
    """
    q = np.asarray(Q, dtype=np.float64)
    delta = np.exp((q - Q0) / dQ)
    return delta * lowQ + (1.0 - delta) * highQ


def siglin(
    Q: ArrayLike,
    lowQ: float = 0.4,
    highQ: float = 0.2,
    Q0: float = 7.0,
    dQ: float = 2.4,
    a1: float = 0.001,
) -> NDArray[np.float64]:
    """
    Calculate a sigmoidal-like function with an (unused) linear term (legacy behavior).

    Notes
    -----
    The legacy implementation ignores `a1` and returns the same expression as `sigmoidal`.
    We preserve that behavior for parity.
    """
    _ = a1
    return sigmoidal(Q, lowQ=lowQ, highQ=highQ, Q0=Q0, dQ=dQ)


def step(q: float, qmax: float = 23.5) -> float:
    """
    Evaluate the Step function (legacy behavior).

    Returns 1.0 for 0 <= q < qmax, 0.0 otherwise.
    If qmax <= 0, prints an error and returns -999.
    """
    if qmax <= 0:
        print("ERROR: Non positive value for qmax in step function.")
        return -999

    if (q < 0.0) or (q >= qmax):
        return 0.0
    return 1.0


def Lorentzian_error(
    x: ArrayLike,
    A: float = 1,
    x0: float = 0,
    gamma: float = 1,
    bckg: float = 0,
    e_A: float = 0,
    e_x0: float = 0,
    e_gamma: float = 0,
    e_bckg: float = 0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Evaluate a Lorentzian and its propagated error (legacy behavior).

    Notes
    -----
    Preserves the legacy error expression, including the `e_x0*22` term.
    """
    q = np.asarray(x, dtype=np.float64)
    gam2 = gamma / 2.0
    lor = A * gam2**2 / ((q - x0) ** 2 + gam2**2) + bckg
    peak = (lor - bckg) / A
    error = e_bckg**2 + peak**2 * e_A**2
    error += (A / gam2 * peak) ** 2 * (1 - peak) ** 2 * e_gamma**2
    error += (2 * A * (q - x0) / gam2**2) ** 2 * peak**2 * e_x0 * 22
    error = np.sqrt(error)
    return np.asarray(lor, dtype=np.float64), np.asarray(error, dtype=np.float64)


def Gaussian_error(
    x: ArrayLike,
    A: float = 1,
    x0: float = 0,
    sigma: float = 1,
    bckg: float = 0,
    e_A: float = 0,
    e_x0: float = 0,
    e_sigma: float = 0,
    e_bckg: float = 0,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Evaluate a Gaussian and its propagated error (legacy behavior).
    """
    q = np.asarray(x, dtype=np.float64)
    gau = (
        A / np.sqrt(2 * np.pi) / sigma * np.exp(-((q - x0) ** 2) / 2.0 / sigma**2)
        + bckg
    )
    peak = (gau - bckg) / A
    error = e_bckg**2 + peak**2 * e_A**2
    error += (
        peak**2 * (A / sigma) ** 2 * (((q - x0) ** 2) / sigma**2 - 1) ** 2 * e_sigma**2
    )
    error += peak**2 * (A / sigma**2 * (q - x0)) ** 2 * e_x0**2
    error = np.sqrt(error)
    return np.asarray(gau, dtype=np.float64), np.asarray(error, dtype=np.float64)


def LorGau(
    x: ArrayLike,
    f0: float = 1.0,
    eta: float = 0.5,
    sigma: float = 2.0,
    gamma: float = 2.0,
    bckg: float = 0.0,
) -> NDArray[np.float64]:
    """
    Evaluate a Gaussian/Lorentzian mixture peak centered at 0 (legacy behavior).
    """
    q = np.asarray(x, dtype=np.float64)
    lor = gamma * gamma / 4.0 / (q * q + gamma * gamma / 4.0)
    gau = np.exp(-1.0 * q * q / 2.0 / sigma / sigma)
    return np.asarray(f0 * (eta * gau + (1.0 - eta) * lor) + bckg, dtype=np.float64)


def LorGau_error(
    x: ArrayLike,
    f0: tuple[float, float] = (1.0, 0.0),
    eta: tuple[float, float] = (0.5, 0.0),
    sigma: tuple[float, float] = (2.0, 0.0),
    gamma: tuple[float, float] = (2.0, 0.0),
    bckg: tuple[float, float] = (0.0, 0.0),
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """
    Evaluate a LorGau mixture peak and its propagated error (legacy behavior).
    """
    lor, lorerr = Lorentzian_error(
        x,
        A=1,
        x0=0,
        gamma=gamma[0],
        bckg=0,
        e_A=0,
        e_x0=0,
        e_gamma=gamma[1],
        e_bckg=0,
    )
    gau, gauerr = Gaussian_error(
        x,
        A=1,
        x0=0,
        sigma=sigma[0],
        bckg=0,
        e_A=0,
        e_x0=0,
        e_sigma=sigma[1],
        e_bckg=0,
    )
    lorgau = bckg[0] + f0[0] * (eta[0] * gau + (1.0 - eta[0]) * lor)
    error = bckg[1] ** 2 + (gau - lor) ** 2 * eta[1] ** 2
    error += ((lorgau - bckg[0]) / f0[0]) ** 2 * f0[1] ** 2
    error += eta[0] ** 2 * gauerr**2 + (1 - eta[0]) ** 2 * lorerr**2
    error = np.sqrt(error)
    return np.asarray(lorgau, dtype=np.float64), np.asarray(error, dtype=np.float64)


def Lorentzian(
    x: ArrayLike, A: float, x0: float, gamma: float, bckg: float
) -> NDArray[np.float64]:
    """
    Evaluate a Lorentzian line-shape, preserving legacy behavior.
    """
    q = np.asarray(x, dtype=np.float64)
    lor = A * gamma * gamma / 4.0 / ((q - x0) * (q - x0) + gamma * gamma / 4.0) + bckg
    return lor


def Gaussian(
    x: ArrayLike, A: float, x0: float, sigma: float, bckg: float
) -> NDArray[np.float64]:
    """
    Evaluate a normalized Gaussian line-shape, preserving legacy behavior.
    """
    q = np.asarray(x, dtype=np.float64)
    gau = (
        A / np.sqrt(2 * np.pi) / sigma * np.exp(-((q - x0) ** 2) / 2.0 / sigma**2)
        + bckg
    )
    return np.asarray(gau, dtype=np.float64)


def GaussianA(
    x: ArrayLike, A: float, x0: float, sigma: float, asym: float = 0
) -> NDArray[np.float64]:
    """
    Evaluate an asymmetric Gaussian (exponential asymmetry), preserving legacy behavior.
    """
    q = np.asarray(x, dtype=np.float64)
    result = (
        A
        / np.sqrt(2 * np.pi)
        / sigma
        * np.exp(-((q - x0) ** 2) / 2.0 / sigma**2)
        * np.exp(-asym * (q - x0))
    )
    return np.asarray(result, dtype=np.float64)
