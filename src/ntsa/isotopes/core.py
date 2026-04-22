from __future__ import annotations

import math
from typing import Any, Callable, Dict, List

import numpy as np

from ntsa.isotopes.database import ISOTOPE_DICT, NOMBRES, UNITS


def Positive(key: str, number: Any) -> None:
    if not (float(number) > 0):
        print(f" WARNING. {key} parameter must have a positive value")


def Negative(key: str, number: Any) -> None:
    if not (float(number) < 0):
        print(f" WARNING. {key} parameter must have a negative value")


def SemiWhole(key: str, number: Any) -> None:
    # Handle 'NULL' or non-numeric strings that might have been passed
    try:
        val = float(number)
        if (val % (1 / 2)) != 0:
            print(f" WARNING. {key} parameter must be semi-whole")
    except (ValueError, TypeError):
        pass


def Top(key: str, value: Any) -> None:
    top = 0.0
    if key == "weight":
        top = 248.072
    elif key == "abundance":
        top = 100.0
    elif key == "Z":
        top = 96.0

    if float(value) > top:
        print(f" WARNING. {key} parameter can't be bigger than {top}")


def Int(key: str, value: Any) -> None:
    if not float(value).is_integer():
        print(f" WARNING. {key} parameter has to be a whole number")


def String(key: str, value: Any) -> None:
    if not isinstance(value, str):
        print(f" WARNING. {key} parameter has to be a string")


def Complex(key: str, value: Any) -> None:
    if not isinstance(value, complex):
        print(f" WARNING. {key} parameter has to be a complex number")


def dummyOk(key: str, value: Any) -> None:
    return


def getFree(isot: Elemento, key: complex) -> complex:
    s = complex(
        round(math.pow((isot.A / (isot.A + 1)), 2) * key.real, 4),
        round(math.pow((isot.A / (isot.A + 1)), 2) * key.imag, 4),
    )
    return s


Validator = Callable[[str, Any], None]

myCorr: Dict[str, List[Validator]] = {
    "symbol": [String],
    "iso": [String],
    "name": [String],
    "A": [Int, Positive],
    "Z": [Int, Positive],
    "weight": [Top, Positive],
    "spin": [SemiWhole],
    "abundance": [Top, Positive],
    "life": [Positive, String],
    "re_bcoh": [dummyOk],
    "neut": [Int, Positive],
    "bcoh": [Complex],
    "binc": [Complex],
    "scoh_bound": [Complex],
    "sinc_bound": [Complex],
}


class Elemento:
    """
    Class that stores nuclear values for an isotope or element.

    Nuclear values are sourced from "Bound Scattering Lengths and Cross Sections
    of the Elements and Their Isotopes" in Appendix 2 of Neutron Scattering
    Fundamentals, volume 44.
    """

    # Commonly accessed fields (explicit for `mypy --strict`).
    symbol: str
    iso: str
    name: str
    A: int
    Z: int
    weight: float
    excess: float
    spin: str
    parity: str
    abundance: float
    life: str
    re_bcoh: float
    im_bcoh: float
    bplus: float
    bminus: float
    re_binc: float
    im_binc: float
    sig_coh: float
    sig_inc: float
    sig_sca: float
    sig_abs: float
    contrast: float
    neut: int
    bcoh: complex
    binc: complex
    scoh_bound: complex
    sinc_bound: complex

    def __init__(self, iso_name: str, table: int = 0, **kwargs: Any):
        """
        Initialize an Elemento object.

        Parameters
        ----------
        iso_name : str
            Name of the isotope (e.g., 'Li', 'Li6', 'Li7').
        table : int, optional
            0: no display, 1: display table for isotope, 2: display all isotopes
            of the same element. Default is 0.
        **kwargs : Any
            Override default values from ISOTOPE_DICT.
        """
        if iso_name not in ISOTOPE_DICT:
            print("\n The isotope you wrote does not exist in this dictionary")
            return

        # Load data from dictionary
        data_tuple = ISOTOPE_DICT[iso_name]
        self.data: Dict[str, Any] = dict(zip(NOMBRES, data_tuple))

        # Replace 'NULL' with 0 and initialize derived fields
        for key in self.data:
            if self.data[key] == "NULL":
                self.data[key] = 0

        self.data.update(
            {"bcoh": 0j, "binc": 0j, "scoh_bound": 0j, "sinc_bound": 0j, "neut": 0}
        )

        # Apply overrides from kwargs and validate
        for key, value in kwargs.items():
            if key in myCorr:
                for func in myCorr[key]:
                    try:
                        func(key, value)
                    except (ValueError, TypeError):
                        pass
            if key in self.data:
                self.data[key] = value

        # Calculate derived physical properties
        bcoh = complex(
            float(self.data.get("re_bcoh", 0)), float(self.data.get("im_bcoh", 0))
        )
        binc = complex(
            float(self.data.get("re_binc", 0)), float(self.data.get("im_binc", 0))
        )

        # Allow overrides for complex Scattering Lengths
        if "bcoh" in kwargs:
            bcoh = kwargs["bcoh"]
        if "binc" in kwargs:
            binc = kwargs["binc"]

        self.data["bcoh"] = bcoh
        self.data["binc"] = binc

        scoh_bound = 4 * np.pi * bcoh * bcoh.conjugate()
        sinc_bound = 4 * np.pi * binc * binc.conjugate()

        # Rounding logic from legacy content
        self.data["scoh_bound"] = complex(
            round(scoh_bound.real, 4), round(scoh_bound.imag, 4)
        )
        self.data["sinc_bound"] = complex(
            round(sinc_bound.real, 4), round(sinc_bound.imag, 4)
        )

        # Number of neutrons = A - Z
        try:
            self.data["neut"] = int(self.data["A"]) - int(self.data["Z"])
        except (ValueError, TypeError):
            self.data["neut"] = 0

        # Handle second pass of overrides for properties like s_bound (though not in NOMBRES)
        # For legacy compatibility, we keep this pattern if needed, but here we just map to attributes.

        # Map internal dictionary to object attributes for easy access (e.g., element.sig_sca)
        for key, value in self.data.items():
            setattr(self, key, value)

        # Ensure a typed view for commonly-used attributes (legacy data can contain mixed types).
        def _as_int(value: Any) -> int:
            try:
                return int(value)
            except (TypeError, ValueError):
                try:
                    return int(float(value))
                except (TypeError, ValueError):
                    return 0

        def _as_float(value: Any) -> float:
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        self.symbol = str(self.data.get("symbol", ""))
        self.iso = str(self.data.get("iso", ""))
        self.name = str(self.data.get("name", ""))
        self.A = _as_int(self.data.get("A", 0))
        self.Z = _as_int(self.data.get("Z", 0))
        self.weight = _as_float(self.data.get("weight", 0.0))
        self.excess = _as_float(self.data.get("excess", 0.0))
        self.spin = str(self.data.get("spin", ""))
        self.parity = str(self.data.get("parity", ""))
        self.abundance = _as_float(self.data.get("abundance", 0.0))
        self.life = str(self.data.get("life", ""))
        self.re_bcoh = _as_float(self.data.get("re_bcoh", 0.0))
        self.im_bcoh = _as_float(self.data.get("im_bcoh", 0.0))
        self.bplus = _as_float(self.data.get("bplus", 0.0))
        self.bminus = _as_float(self.data.get("bminus", 0.0))
        self.re_binc = _as_float(self.data.get("re_binc", 0.0))
        self.im_binc = _as_float(self.data.get("im_binc", 0.0))
        self.sig_coh = _as_float(self.data.get("sig_coh", 0.0))
        self.sig_inc = _as_float(self.data.get("sig_inc", 0.0))
        self.sig_sca = _as_float(self.data.get("sig_sca", 0.0))
        self.sig_abs = _as_float(self.data.get("sig_abs", 0.0))
        self.contrast = _as_float(self.data.get("contrast", 0.0))
        self.neut = _as_int(self.data.get("neut", 0))
        self.bcoh = complex(self.data.get("bcoh", 0j))
        self.binc = complex(self.data.get("binc", 0j))
        self.scoh_bound = complex(self.data.get("scoh_bound", 0j))
        self.sinc_bound = complex(self.data.get("sinc_bound", 0j))

        # Table display logic
        if table == 1:
            print("{:<15}".format(iso_name))
            print("{:<10} {:<10} {:<10}".format("PARAMETER", "VALUE", "UNITS"))
            for key in self.data:
                val = self.data[key]
                unit = UNITS.get(key, "-")
                print("{:<10} {:<10} {:<10}".format(key, str(val), unit))

        if table == 2:
            symbol = self.data["symbol"]
            for key in ISOTOPE_DICT:
                if ISOTOPE_DICT[key][0] == symbol:
                    iso_obj = Elemento(key)
                    print("\n")
                    print("{:<15}".format(key.upper()))
                    print("\n")
                    print("{:<10} {:<10} {:<10}".format("PARAMETER", "VALUE", "UNITS"))
                    for k in iso_obj.data:
                        val = iso_obj.data[k]
                        unit = UNITS.get(k, "-")
                        print("{:<10} {:<10} {:<10}".format(k, str(val), unit))

    @classmethod
    def getIsotope(cls, iso_name: str) -> List[str]:
        lista = []
        if iso_name == "All":
            xName = ""
            # Sort by name to match legacy behavior of tracking name changes
            # Though ISOTOPE_DICT is already somewhat ordered
            for key in ISOTOPE_DICT:
                name = ISOTOPE_DICT[key][2]
                if name != xName:
                    lista.append(name)
                xName = name
        else:
            for key in ISOTOPE_DICT:
                if ISOTOPE_DICT[key][2] == iso_name:
                    if ISOTOPE_DICT[key][1] == "nat":
                        lista.append(ISOTOPE_DICT[key][0])
                    else:
                        lista.append(ISOTOPE_DICT[key][0] + ISOTOPE_DICT[key][1])
        return lista

    def __repr__(self) -> str:
        return f"Elemento('{self.symbol}', iso='{self.iso}', name='{self.name}')"


# Alias for legacy compatibility
elemento = Elemento
