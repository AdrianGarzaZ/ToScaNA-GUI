from __future__ import annotations

from typing import Any, Mapping, TypeVar

T = TypeVar("T")


def extractDict(dictionary: Mapping[str, Mapping[str, T]], key: str) -> dict[str, T]:
    """
    Extract a sub-dictionary from a dictionary of dictionaries (legacy behavior).
    """
    result: dict[str, T] = {}
    for key1, _value in dictionary.items():
        result[key1] = dictionary[key1][key]
    return result


def extractAttr(Dict: Mapping[str, Any], attr: str) -> dict[str, Any]:
    """
    Extract an attribute from a dictionary containing class instances (legacy behavior).

    Preserves legacy printing when an attribute is missing.
    """
    result: dict[str, Any] = {}
    for key, val in Dict.items():
        if hasattr(val, attr):
            result[key] = getattr(val, attr)
        else:
            print(f"Attribute {attr} not found in {val}.")
    return result
