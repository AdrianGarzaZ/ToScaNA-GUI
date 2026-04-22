from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


def XS_model(  # noqa: N802 (legacy API)
    Eval: float,
    Eeff: float,
    composition_vec: list[float] | NDArray[np.float64],
    bound_xs_vec: list[float] | NDArray[np.float64],
    A_vec: list[float] | NDArray[np.float64],
) -> float:
    """
    Calculate the neutron total cross section in the epithermal limit (legacy behavior).
    """
    composition_arr = np.array(composition_vec, dtype=np.float64)
    bound_xs_arr = np.array(bound_xs_vec, dtype=np.float64)
    a_arr = np.array(A_vec, dtype=np.float64)

    a_vals = (a_arr / (a_arr + 1.0)) ** 2
    result = np.sum(
        composition_arr
        * bound_xs_arr
        * a_vals
        * (1.0 + float(Eeff) / (2.0 * a_arr * float(Eval)))
    )
    return float(result)


def scattering_probability(  # noqa: N802 (legacy API)
    E0: float,
    scat_xs: float,
    composition_vec: list[float] | NDArray[np.float64],
    abs_xs_vec: list[float] | NDArray[np.float64],
) -> float:
    """
    Calculate the scattering probability for a given neutron incident energy (legacy behavior).
    """
    composition_arr = np.array(composition_vec, dtype=np.float64)
    abs_xs_arr = np.array(abs_xs_vec, dtype=np.float64)

    abs_xs = float(np.dot(composition_arr, abs_xs_arr)) / np.sqrt(float(E0) / 25.3)
    total_xs = abs_xs + float(scat_xs)
    return float(1.0 - abs_xs / total_xs)
