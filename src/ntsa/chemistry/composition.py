from __future__ import annotations

# Back-compat wrapper: symbols were moved to their canonical locations.
from ..physics.properties import AtomicAvg, getConcentrations, getNofAtoms
from ..utils.dicts import extractAttr, extractDict

__all__ = [
    "AtomicAvg",
    "extractAttr",
    "extractDict",
    "getConcentrations",
    "getNofAtoms",
]
