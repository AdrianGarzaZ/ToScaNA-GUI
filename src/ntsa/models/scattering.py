"""
Scattering models for total scattering data analysis.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ntsa.math.polynomials import polyQ2


def inelastic(
    x: ArrayLike, A: float = 51.0, lowQ: float = 0.4, Q0: float = 7.0, dQ: float = 2.4
) -> NDArray[np.float64]:
    """
    Calculate the inelastic behaviour using a sigmoidal function.

    The inelasticity is modeled as:
        inelastic(x) = lowQ * [1 + (A/(1+A))² * delta] / (1 + delta)
    where delta = exp[(x - Q0) / dQ]

    Note that:
        - inelastic(0) ≈ lowQ
        - inelastic(∞) = lowQ * (A / (1+A))²
        i.e. sigma_free = sigma_bound * (A / (1+A))²

    Parameters
    ----------
    x : array_like
        The range of abscissas, usually the Q-scale (momentum transfer).
    A : float, optional
        The mass number (mass/neutron mass). Default is 51.0 (Vanadium).
    lowQ : float, optional
        The limiting value of the function at Q -> 0. Default is 0.4.
    Q0 : float, optional
        Position of the inflexion point of the sigmoidal function. Default is 7.0.
    dQ : float, optional
        Width of the transition of the sigmoidal function. Default is 2.4.

    Returns
    -------
    numpy.ndarray
        The values of the inelastic function corresponding to the given abscissas.
    """
    q = np.asarray(x, dtype=np.float64)
    delta = np.exp((q - Q0) / dQ)
    ratio = (A / (1.0 + A)) ** 2
    return lowQ * (1.0 + ratio * delta) / (1.0 + delta)


def self024(x: ArrayLike, self0: float, q2: float, q4: float) -> NDArray[np.float64]:
    """
    Curve fitting function for self-scattering: self0 + q2*x² + q4*x⁴.

    Parameters
    ----------
    x : array_like
        The range of abscissas.
    self0 : float
        Constant term (Q=0).
    q2 : float
        Coefficient for the x² term.
    q4 : float
        Coefficient for the x⁴ term.

    Returns
    -------
    numpy.ndarray
        The evaluated function.
    """
    q = np.asarray(x, dtype=np.float64)
    q2_val = q**2
    return self0 + (q2 + q4 * q2_val) * q2_val


def vanaQdep(
    x: ArrayLike,
    a0: float,
    a1: float,
    a2: float,
    A: float = 51.0,
    lowQ: float = 0.4,
    Q0: float = 7.4,
    dQ: float = 2.4,
) -> NDArray[np.float64]:
    """
    Function describing the general behaviour of incoherent Vanadium signal.

    It combines a 2nd-degree polynomial (instrument resolution effects)
    with a sigmoidal function (inelasticity effect).

    vanadium(Q) = polyQ2(Q, a0, a1, a2) * inelastic(Q, A, lowQ, Q0, dQ)

    Parameters
    ----------
    x : array_like
        The range of abscissas (Q-scale).
    a0, a1, a2 : float
        Polynomial coefficients for polyQ2.
    A : float, optional
        Mass number for inelasticity. Default is 51.0.
    lowQ : float, optional
        Limiting value at Q -> 0. Default is 0.4.
    Q0 : float, optional
        Inflexion point. Default is 7.4.
    dQ : float, optional
        Transition width. Default is 2.4.

    Returns
    -------
    numpy.ndarray
        The evaluated Vanadium Q-dependence.
    """
    q = np.asarray(x, dtype=np.float64)
    polynomial = polyQ2(q, a0, a1, a2)
    sigmoidal = inelastic(q, A=A, lowQ=lowQ, Q0=Q0, dQ=dQ)
    return sigmoidal * polynomial
