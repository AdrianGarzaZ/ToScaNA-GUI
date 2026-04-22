from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from numpy.typing import NDArray


def read_xye(
    filename: str,
) -> tuple[NDArray[np.float64], NDArray[np.float64], NDArray[np.float64]]:
    """
    Legacy `read_xye` implementation.

    Reads an ASCII file with 2 or 3 columns, ignoring lines containing `#`.
    Returns three 1D arrays: (x, y, e).
    """
    with open(filename, "r") as data:
        x: list[float] = []
        y: list[float] = []
        e: list[float] = []

        for dataline in data.readlines():
            if "#" not in dataline:
                row = dataline.strip(" ")[:-1]
                if len(row) > 0:
                    columns = row.split()
                    x.append(float(columns[0]))
                    y.append(float(columns[1]))
                    if len(columns) == 3:
                        if (columns[2] == "i") or (columns[2] == "o"):
                            e.append(float(0.0))
                        else:
                            e.append(float(columns[2]))
                    else:
                        e.append(float(0.0))

    print(
        "The data file {} read with no errors. Number of data = {}".format(
            filename, len(x)
        )
    )

    xa: NDArray[np.float64] = np.asarray(x, dtype=np.float64)
    ya: NDArray[np.float64] = np.asarray(y, dtype=np.float64)
    ea: NDArray[np.float64] = np.asarray(e, dtype=np.float64)
    return xa, ya, ea


def read_3col(filename: str) -> NDArray[np.float64]:
    """
    read_3col function

    Opens a file and read it line by line. This function assumes it is a 3-columns file.
    The lines containig the symbol # are ignored. Be careful, # could be anywhere in the line!
    The empty lines are also ignored.
    As output it produces 3 lists with abcissas, ordinates and errors for the ordinates.

    Parameters
    ----------
    filename : str
        The path to the file to read.

    Returns
    -------
    numpy.ndarray
        A 3-column matrix with x, y, and error.
    """
    with open(filename, "r") as data:
        # Creating the lists that will contain abcissas, ordinates and errors
        x = []
        y = []
        e = []

        # Reading the file line by line
        for dataline in data.readlines():
            if "#" not in dataline:  # Only the lines without # are treated.
                row = dataline.strip(" ")
                # Handle potential \n at the end if not handled by strip
                row = row.strip()
                if len(row) > 0:  # Only the no-empty lines are treated
                    columns = row.split()  # This method split the line using the spaces
                    x.append(float(columns[0]))
                    y.append(float(columns[1]))
                    if len(columns) == 3:
                        if (columns[2] == "i") or (columns[2] == "o"):
                            e.append(float(0.0))
                        else:
                            e.append(float(columns[2]))
                    else:
                        e.append(float(0.0))

    # Converts the lists in arrays
    xa = np.array(x)
    ya = np.array(y)
    ea = np.array(e)
    # Reshapes the arrays as 2D arrays, but with 1 column
    xa = xa.reshape(xa.shape[0], 1)
    ya = ya.reshape(ya.shape[0], 1)
    ea = ea.reshape(ea.shape[0], 1)
    # Concatenates the arrays to have a 3-column matrix
    data_out = np.concatenate((xa, ya), axis=1)
    data_out = np.concatenate((data_out, ea), axis=1)
    return data_out
