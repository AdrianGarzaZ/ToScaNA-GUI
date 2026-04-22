from __future__ import annotations

from typing import Any


def getRunningParams(parfile: str) -> dict[str, Any]:
    """
    Read the parameters file for data treatment notebooks (legacy behavior).

    Notes
    -----
    This is a legacy notebook-oriented parser distinct from `ntsa.io.parameters.readParam`.
    It intentionally preserves the legacy dictionary shape (keys like `<ins>`, `<asc>`, ...).
    """
    shapes = ["cylinder"]
    containers = ["SiO2", "V", "TiZr", "Nb", "None"]
    absorbers = ["B", "None"]
    normalisers = ["V", "None"]
    environments = ["V", "A", "None"]
    Nelements = 0  # Number of elements (or chemical species) in the sample

    inputPar: dict[str, Any] = {}
    inputPar["<par>"] = ("Parameter file   ", parfile)
    with open(parfile, "r") as f:
        lines = f.readlines()

    # Testing the first character of each non-blank line.
    # If this character is not #, ! or <, stops the program.
    for i in range(len(lines)):
        if len(lines[i]) > 1:
            first = (
                (lines[i][0] != "#") and (lines[i][0] != "!") and (lines[i][0] != "<")
            )
            if first:
                print("Wrong input on line: ", i + 1, " in file: ", parfile)
                raise ValueError(f"Wrong input on line {i + 1} in file {parfile}")

    # Loop over all lines in the input file
    for i in range(len(lines)):
        if (lines[i][0] == "#") or (lines[i][0] == "!"):
            pass
        elif len(lines[i]) == 1:
            pass
        elif lines[i][0] == "<":
            line = lines[i].split(" ")

            if line[0] == "<ins>":
                inputPar[line[0]] = ("Instrument:", line[1])

            if line[0] == "<pro>":
                inputPar[line[0]] = ("Proposal:", line[1])

            if line[0] == "<mpr>":
                inputPar[line[0]] = ("Main Proposer:", line[1])

            if line[0] == "<lco>":
                inputPar[line[0]] = ("Local Contact:", line[1])

            if line[0] == "<dte>":
                inputPar[line[0]] = ("Dates:", line[1])
                hyphen = line[1].find("-")
                inputPar["<sta>"] = ("Starting date:", line[1][0:hyphen])
                inputPar["<end>"] = ("Ending date:", line[1][hyphen + 1 :])

            if line[0] == "<cyc>":
                inputPar[line[0]] = ("Cycle:", line[1])

            if line[0] == "<log>":
                inputPar[line[0]] = ("Logbook:", line[1])
                hyphen = line[1].find("-")
                inputPar["<nbk>"] = ("Notebook #:", line[1][0:hyphen])
                inputPar["<pag>"] = ("Page:", line[1][hyphen + 1 :])

            if line[0] == "<env>":
                inputPar[line[0]] = ("Environment:", line[1])

            if line[0] == "<zac>":
                inputPar[line[0]] = ("Zero angle (deg):", float(line[1]))

            if line[0] == "<wle>":
                inputPar[line[0]] = ("Wavelength (Å):", float(line[1]))

            if line[0] == "<sli>":
                inputPar[line[0]] = ("Slits (mm):", line[1])
                inputPar["<lft>"] = ("Left (mm):", float(line[1]))
                inputPar["<rgt>"] = ("Right (mm):", float(line[2]))

            if line[0] == "<fla>":
                inputPar[line[0]] = ("Flags (mm):", line[1])
                inputPar["<top>"] = ("Top (mm):", float(line[1]))
                inputPar["<bot>"] = ("Bottom (mm):", float(line[2]))

            if line[0] == "<apr>":
                inputPar[line[0]] = ("Angular precision (deg):", float(line[1]))

            if line[0] == "<asc>":
                inputPar[line[0]] = (
                    "Angular scale (deg):",
                    float(line[1]),
                    float(line[2]),
                    float(line[3]),
                )

            if line[0] == "<qsc>":
                inputPar[line[0]] = (
                    "Q scale (1/Å):",
                    float(line[1]),
                    float(line[2]),
                    float(line[3]),
                )

            if line[0] == "<rsc>":
                inputPar[line[0]] = (
                    "r scale (Å):",
                    float(line[1]),
                    float(line[2]),
                    float(line[3]),
                )

            if line[0] == "<Cmater>":
                inputPar[line[0]] = ("Container material:", line[1])
                if line[1] in containers:
                    pass
                else:
                    print(
                        "The container {} is not available".format(inputPar[line[0]][1])
                    )

            if line[0] == "<Cshape>":
                inputPar[line[0]] = (
                    "Container shape:",
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                )
                if line[1] in shapes:
                    pass
                else:
                    print("The shape {} is not available".format(inputPar[line[0]][1]))

            if line[0] == "<Amater>":
                inputPar[line[0]] = ("Absorber material:", line[1])
                if line[1] in absorbers:
                    pass
                else:
                    print(
                        "The absorber {} is not available".format(inputPar[line[0]][1])
                    )

            if line[0] == "<Ashape>":
                inputPar[line[0]] = (
                    "Absorber shape:",
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                )
                if line[1] in shapes:
                    pass
                else:
                    print("The shape {} is not available".format(inputPar[line[0]][1]))

            if line[0] == "<Nmater>":
                inputPar[line[0]] = ("Normaliser material:", line[1])
                if line[1] in normalisers:
                    pass
                else:
                    print(
                        "The normaliser {} is not available".format(
                            inputPar[line[0]][1]
                        )
                    )

            if line[0] == "<Nshape>":
                inputPar[line[0]] = (
                    "Normaliser shape:",
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                )
                if line[1] in shapes:
                    pass
                else:
                    print("The shape {} is not available".format(inputPar[line[0]][1]))

            if line[0] == "<Emater>":
                inputPar[line[0]] = ("Environment material:", line[1])
                if line[1] in environments:
                    pass
                else:
                    print(
                        "The environment {} is not available".format(
                            inputPar[line[0]][1]
                        )
                    )

            if line[0] == "<Eshape>":
                inputPar[line[0]] = (
                    "Environment shape:",
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                )
                if line[1] in shapes:
                    pass
                else:
                    print(
                        "The Environment {} is not available".format(
                            inputPar[line[0]][1]
                        )
                    )

            if line[0] == "<Sdescr>":
                description = lines[i][9:]
                hash = description.find("#")
                inputPar[line[0]] = ("Sample description:  ", description[0:hash])

            if line[0] == "<StempK>":
                inputPar[line[0]] = ("Sample temperature:  ", float(line[1]))

            if line[0][0:5] == "<Sato":
                Nelements += 1
                usefulinfo = lines[i][9:]
                hash = usefulinfo.find("#")
                atomdat = (usefulinfo[0:hash].strip()).split(" ")
                atompar = [x for x in atomdat if x != ""]
                inputPar[line[0]] = ("Atom " + str(Nelements).zfill(2) + ": ", *atompar)
                inputPar["<SNelem>"] = ("Number of elements:", Nelements)

            if line[0] == "<Sdegcc>":
                inputPar[line[0]] = ("Sample density:      ", float(line[1]))

            if line[0] == "<Smassc>":
                inputPar[line[0]] = ("Sample mass in can:  ", float(line[1]))

            if line[0] == "<Sshape>":
                inputPar[line[0]] = (
                    "Sample shape:",
                    line[1],
                    line[2],
                    line[3],
                    line[4],
                )
                if line[1] in shapes:
                    pass
                else:
                    print("The shape {} is not available".format(inputPar[line[0]][1]))

            if line[0] == "<Sfulln>":
                inputPar[line[0]] = ("Sample fullness:", float(line[1]))

            if line[0] == "<Stitle>":
                inputPar[line[0]] = ("Sample title:        ", line[1])

            if line[0] == "<CoFile>":
                inputPar[line[0]] = ("Container file:      ", line[1])

            if line[0] == "<AbFile>":
                inputPar[line[0]] = ("Absorber file:       ", line[1])

            if line[0] == "<NoFile>":
                inputPar[line[0]] = ("Vanadium file:       ", line[1])

            if line[0] == "<EnFile>":
                inputPar[line[0]] = ("Environment file:    ", line[1])

            if line[0] == "<SaFile>":
                inputPar[line[0]] = ("Sample file:         ", line[1])
        else:
            print("Input error in line: ", i + 1, " file: ", parfile)
            raise ValueError(f"Input error in line {i + 1} file {parfile}")
    return inputPar
