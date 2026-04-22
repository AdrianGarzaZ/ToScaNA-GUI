from __future__ import annotations

import numpy as np


def getCylVolume(diameter: float = 5.0, height: float = 50.0) -> float:
    """
    Calculate the volume of a cylinder.

    Parameters
    ----------
    diameter : float, optional
        The diameter of the cylinder. Default is 5.0.
    height : float, optional
        The height of the cylinder. Default is 50.0.

    Returns
    -------
    float
        The volume of the cylinder.
    """
    radius = diameter / 2.0
    return float(np.pi * radius**2 * height)
