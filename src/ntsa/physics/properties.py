from __future__ import annotations

from typing import Mapping


def getAtomicDensity(density: float = 1.0, molarMass: float = 6.0) -> float:
    """
    Calculate the atomic density (atoms/Å³).

    Given the macroscopic density (g/cm³) and the average atomic molar mass
    (g/mole), this function returns the atomic density (atoms/Å³).

    Atomic density [atom/Å³] =
           density [g/cm³] * NA [atom/mole] / molarM [g/mole] * 10⁻²⁴
    where molarM is the average molar mass per atom and NA = 6.02214076 × 10²³
    atoms/mole is the Avogadro's number.

    If density is less or equal to 0, the function returns water atomic density,
    i.e, 0.1 at/Å³.

    Parameters
    ----------
    density : float, optional
        Macroscopic density in g/cm³. The default is 1.0.
    molarMass : float, optional
        Average molar mass per atom, in g/mole/atom. The default is 6.0.

    Returns
    -------
    float
        Atomic density, in atoms/Å³.
    """
    # NA * 10^-24 = 6.02214076 * 10^23 * 10^-24 = 0.602214076
    avogadro_scaled = 0.602214076

    if density <= 0:
        density = 1.0
        molarMass = 6.0
        # Consider logging this instead of printing in a library context
        print("Attention!")
        print("    Using the water density in getAtomicDensity function.")

    return float(density * avogadro_scaled / molarMass)


def getDensity(atomic_density: float = 0.1, molarM: float = 6.0) -> float:
    """
    Calculate the macroscopic density (g/cmÂ³) from atomic density (atoms/Ã…Â³).

    Notes
    -----
    This function preserves the legacy behavior in `legacy/lib/toscana.py`,
    including printing a warning and returning `1.0` when `atomic_density <= 0`.
    """
    avogadro_scaled = 0.602214076

    result = float(atomic_density / avogadro_scaled * molarM)
    if atomic_density <= 0:
        result = 1.0
        print("Attention! Using the water density in getDensity function.")

    return result


def getMassNumber(molarMass: float = 6.0) -> float:
    """
    Calculate the mass number A = molarMass / neutronMass (legacy convention).

    Parameters
    ----------
    molarMass
        Molar mass in amu.
    """
    neutronMass = 1.0086649  # amu (legacy constant)
    return float(molarMass / neutronMass)


def getFreeXS(BoundXS: float = 5.08, A: float = 50.9415) -> float:
    """
    Calculate the free cross section from the bound cross section (barns).

    Legacy formula:
        sigma_free = sigma_bound * A^2 / (1 + A)^2
    """
    return float(BoundXS * A**2 / (1.0 + A) ** 2)


def getAbsXS(AbsXS: float = 5.08, wavelength: float = 1.8089) -> float:
    """
    Scale absorption cross section (barns) by wavelength (Ã…).

    Legacy formula:
        sigma_abs(lambda) = sigma_thermal * lambda / 1.8089
    """
    return float(AbsXS * wavelength / 1.8089)


def getNofAtoms(atoms: Mapping[str, float]) -> float:
    """
    Calculate the number of atoms in the basic unit (legacy behavior).
    """
    natoms: float = 0.0
    for _key, value in atoms.items():
        natoms += value
    return natoms


def getConcentrations(atoms: Mapping[str, float]) -> dict[str, float]:
    """
    Calculate atomic concentrations for a sample (legacy behavior).

    Notes
    -----
    Preserves legacy behavior including printing an error when `natoms <= 0`.
    When `natoms == 0`, this function will raise `ZeroDivisionError` as legacy does.
    """
    concentration: dict[str, float] = {}
    natoms = float(sum(atoms.values()))
    if natoms <= 0:
        print("---> ERROR! The number of atoms must be positive.")
    for key, value in atoms.items():
        concentration[key] = value / natoms
    return concentration


def AtomicAvg(
    concentration: Mapping[str, float], magnitude: Mapping[str, float]
) -> float:
    """
    Compute an atomic average of a magnitude (legacy behavior).
    """
    average: float = 0.0
    for key, value in concentration.items():
        average += float(value) * float(magnitude[key])
    return average
