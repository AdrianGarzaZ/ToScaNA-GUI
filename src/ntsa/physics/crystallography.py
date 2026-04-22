from __future__ import annotations

import numpy as np


def sf_fcc(miller_h: int, miller_k: int, miller_l: int) -> np.complex128:
    """
    Calculate the structure factor for a fcc lattice for a given plane hkl.

    Preserves the legacy implementation from `legacy/lib/toscana.py`.
    """
    result = (
        1.0
        + np.exp(-1j * np.pi * (miller_k + miller_l))
        + np.exp(-1j * np.pi * (miller_h + miller_l))
        + np.exp(-1j * np.pi * (miller_h + miller_k))
    )
    return np.complex128(result)


def sf_bcc(miller_h: int, miller_k: int, miller_l: int) -> np.complex128:
    """
    Calculate the structure factor for a bcc lattice for a given plane hkl.

    Preserves the legacy implementation from `legacy/lib/toscana.py`.
    """
    result = 1.0 + np.exp(-1j * np.pi * (miller_h + miller_k + miller_l))
    return np.complex128(result)


def sf_sc(miller_h: int, miller_k: int, miller_l: int) -> float:
    """
    Calculate the structure factor for a sc lattice for a given plane hkl.

    Legacy behavior: always returns 1.0.
    """
    _ = (miller_h, miller_k, miller_l)
    return 1.0


def reflections_fcc(
    wavelength: float = 0.5, twotheta0: float = 0.0, lattice: float = 3.52024
) -> np.ndarray:
    """
    Produce a list of the angular positions for a fcc lattice (legacy behavior).

    Returns angles in degrees for allowed reflections in the range [0, 180].
    """
    moduleMax = int(2.0 * lattice / wavelength)
    sinus: list[float] = []
    for miller_h in range(moduleMax):
        for miller_k in range(moduleMax):
            for miller_l in range(moduleMax):
                module = float(
                    np.sqrt(
                        miller_h * miller_h + miller_k * miller_k + miller_l * miller_l
                    )
                )
                sf = float(sf_fcc(miller_h, miller_k, miller_l).real)
                if sf * module > 0:
                    sintheta = module * wavelength / 2.0 / lattice
                    if sintheta < 1.0:
                        sinus.append(float(sintheta))
    rad_fcc = 2.0 * np.arcsin(sorted(set(sinus)))
    deg_fcc1 = twotheta0 + np.array(180.0 / np.pi * rad_fcc, dtype=np.float64)
    deg_fcc2 = -twotheta0 + np.array(sorted(180.0 - deg_fcc1), dtype=np.float64)
    deg_fcc = np.concatenate([deg_fcc1, deg_fcc2])
    return np.asarray(deg_fcc, dtype=np.float64)
