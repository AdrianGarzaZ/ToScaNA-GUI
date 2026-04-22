from __future__ import annotations


def getNumorFiles(numorLst: list[str]) -> list[str]:  # noqa: N802 (legacy API)
    """
    Expand a short syntax list of numors into a detailed list.

    Notes
    -----
    This matches the legacy happy-path behavior and tightens error handling:
    invalid entries raise `ValueError` instead of printing/logging and continuing.
    """
    numor_files: list[str] = []
    len_numor = 6

    for entry in numorLst:
        if len(entry) == len_numor:
            numor_files.append(entry)
            continue

        if len(entry) == 2 * len_numor + 1:
            first_num = int(entry[0:len_numor])
            last_num = int(entry[len_numor + 1 : 2 * len_numor + 1])
            if first_num > last_num:
                raise ValueError(
                    f"Invalid numor range {entry}: last numor must be >= first numor."
                )
            for num in range(first_num, last_num + 1):
                numor_files.append(str(num).zfill(len_numor))
            continue

        raise ValueError(
            "Invalid numor entry (getNumorFiles): expected 6-digit numor or '111111-222222' range."
        )

    return numor_files
