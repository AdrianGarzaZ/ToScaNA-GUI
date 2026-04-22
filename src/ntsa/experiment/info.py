from __future__ import annotations

from typing import Any, Mapping

import numpy as np

from ntsa.physics.geometry import getCylVolume
from ntsa.physics.properties import (
    AtomicAvg,
    getAtomicDensity,
    getFreeXS,
    getMassNumber,
)
from ntsa.utils.dicts import extractAttr


def setExpInfo(
    Proposal: str = "6-01-000",
    mainProposer: str = "nobody",
    experimenters: str = "nobody",
    LC: str = "Cuello",
    otherUsers: str = "nobody",
    startDate: str = "01/01/2000",
    endDate: str = "02/01/2000",
    environment: str = "A",
    logBook: int = 0,
    logPage: int = 0,
    instrument: str = "D4",
) -> dict[str, Any]:
    """
    Create a dictionary with information about the experiment (legacy behavior).
    """
    experiment: dict[str, Any] = {"Proposal": Proposal}
    experiment["MP"] = mainProposer
    experiment["experimenters"] = experimenters
    experiment["LC"] = LC
    experiment["otherUsers"] = otherUsers
    experiment["instr"] = instrument
    experiment["startDate"] = startDate
    experiment["endDate"] = endDate
    experiment["environment"] = environment
    experiment["logBook"] = logBook
    experiment["logPage"] = logPage

    print(30 * "-")
    print("Experiment")
    print(4 * " ", f"Instrument: {experiment['instr']}")
    print(4 * " ", f"Proposal: {experiment['Proposal']}")
    print(4 * " ", f"Main proposer: {experiment['MP']}")
    print(4 * " ", f"Other users: {experiment['otherUsers']}")
    print(4 * " ", f"On-site users: {experiment['experimenters']}")
    print(4 * " ", f"Local contact: {experiment['LC']}")
    print(
        4 * " ",
        "Starting date: {0} ---->  Ending date: {1}".format(
            experiment["startDate"], experiment["endDate"]
        ),
    )
    print(4 * " ", f"Sample environment: {experiment['environment']}")
    print(
        4 * " ",
        "D4 notebook: {0}  Page: {1}".format(
            experiment["logBook"], experiment["logPage"]
        ),
    )
    print()
    return experiment


def setBeamInfo(
    zeroAngle: float = 0,
    wavelength: float = 0.5,
    LohenSlit: float = 2.5,
    GamsSlit: float = -2.5,
    topFlag: float = 25.0,
    bottomFlag: float = -25.0,
) -> dict[str, Any]:
    """
    Create a dictionary with information about the beam (legacy behavior).
    """
    beam_width = LohenSlit - GamsSlit
    beam_height = topFlag - bottomFlag

    beam: dict[str, Any] = {"zero": zeroAngle}
    beam["wlength"] = wavelength
    beam["LohenSlit"] = LohenSlit
    beam["GamsSlit"] = GamsSlit
    beam["width"] = beam_width
    beam["topFlag"] = topFlag
    beam["botFlag"] = bottomFlag
    beam["height"] = beam_height

    print(30 * "-")
    print("Beam characteristics")
    print(4 * " ", "Wavelength = {:8.6g} A".format(beam["wlength"]))
    print(4 * " ", "Zero angle = {:8.6g} deg".format(beam["zero"]))
    print(
        4 * " ",
        "Dimensions: (Width = {0:.6g} mm)x(Height = {1:.6g} mm)".format(
            beam["width"], beam["height"]
        ),
    )
    print()
    return beam


def setCanInfo(
    material: str = "Vanadium",
    shape: str = "Cylinder",
    outerDiam: float = 5,
    innerDiam: float = 4.8,
    height: float = 60.0,
) -> dict[str, Any]:
    """
    Create a dictionary with information about the container (legacy behavior).
    """
    wall_thickness = (outerDiam - innerDiam) / 2.0

    can: dict[str, Any] = {"material": material}
    can["shape"] = shape
    can["outerDiam"] = outerDiam
    can["innerDiam"] = innerDiam
    can["height"] = height
    can["wallThickness"] = wall_thickness

    print(30 * "-")
    print("Container")
    print(4 * " ", "Type: {0} {1}".format(can["material"], can["shape"]))
    print(4 * " ", f"Outer diameter = {can['outerDiam']} mm")
    print(4 * " ", f"Inner diameter = {can['innerDiam']} mm")
    print(4 * " ", "Wall thickness = {:.3g} mm".format(can["wallThickness"]))
    print(4 * " ", f"Height = {can['height']} mm")
    print()
    return can


def setBinInfo(
    AngularResolution: float = 0.125,
    AMin: float = 0.0,
    AMax: float = 140.0,
    AStep: float = 0.125,
    QMin: float = 0.0,
    QMax: float = 23.5,
    QStep: float = 0.02,
    RMin: float = 0.0,
    RMax: float = 20.0,
    RStep: float = 0.01,
) -> dict[str, Any]:
    """
    Create a dictionary with information about the binnings (legacy behavior).
    """
    Abin = (AMin, AMax, AStep)
    Qbin = (QMin, QMax, QStep)
    Rbin = (RMin, RMax, RStep)

    NbrPointsA = int((Abin[1] - Abin[0]) / Abin[2])
    NbrPointsQ = int((Qbin[1] - Qbin[0]) / Qbin[2])
    NbrPointsR = int((Rbin[1] - Rbin[0]) / Rbin[2])

    binning: dict[str, Any] = {"Ares": AngularResolution}
    binning["Abin"] = Abin
    binning["Qbin"] = Qbin
    binning["Rbin"] = Rbin
    binning["NbrPointsA"] = NbrPointsA
    binning["NbrPointsQ"] = NbrPointsQ
    binning["NbrPointsR"] = NbrPointsR

    print(30 * "-")
    print("Binning")
    print(4 * " ", "Angular channel width = {:.3g} deg".format(binning["Ares"]))
    print(
        4 * " ",
        "In angle: from {0:.3g} deg to {1:.3g} deg, in steps of {2:.3f} deg, thus {3:.5g} points.".format(
            binning["Abin"][0],
            binning["Abin"][1],
            binning["Abin"][2],
            binning["NbrPointsA"],
        ),
    )
    print(
        4 * " ",
        "In Q: from {0:.3g} 1/A to {1:.3g} 1/A, in steps of {2:.3f} 1/A, thus {3:.5g} points.".format(
            binning["Qbin"][0],
            binning["Qbin"][1],
            binning["Qbin"][2],
            binning["NbrPointsQ"],
        ),
    )
    print(
        4 * " ",
        "In R: from {0:.3g} A to {1:.3g} A, in steps of {2:.3f} A, thus {3:.5g} points.".format(
            binning["Rbin"][0],
            binning["Rbin"][1],
            binning["Rbin"][2],
            binning["NbrPointsR"],
        ),
    )
    print()
    return binning


def setNumorInfo(
    totalNumors: tuple[str, int, int] = ("Exp", 0, 1),
    containerNumors: tuple[str, int, int] = ("Can", 0, 1),
    environmentNumors: tuple[str, int, int] = ("Env", 0, 1),
    nickelNumors: tuple[str, int, int] = ("Ni5", 0, 1),
    vanadiumNumors: tuple[str, int, int] = ("Van", 0, 1),
    absorberNumors: tuple[str, int, int] = ("Abs", 0, 1),
    sampleNumors: tuple[str, int, int] = ("S01", 0, 1),
) -> dict[str, Any]:
    """
    Create a dictionary with information about the numors (legacy behavior).
    """
    numors: dict[str, Any] = {
        "experiment": totalNumors,
        "container": containerNumors,
        "environment": environmentNumors,
        "nickel": nickelNumors,
        "vanadium": vanadiumNumors,
        "absorber": absorberNumors,
        "sample": sampleNumors,
    }

    print("Numors")

    if totalNumors[1] != 0:
        print(
            "{}Total {}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["experiment"],
                int(numors["experiment"][2]) - int(numors["experiment"][1]) + 1,
            )
        )
    if containerNumors[1] != 0:
        print(
            "{}{}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["container"],
                int(numors["container"][2]) - int(numors["container"][1]) + 1,
            )
        )
    if environmentNumors[1] != 0:
        print(
            "{}{}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["environment"],
                int(numors["environment"][2]) - int(numors["environment"][1]) + 1,
            )
        )
    if nickelNumors[1] != 0:
        print(
            "{}{}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["nickel"],
                int(numors["nickel"][2]) - int(numors["nickel"][1]) + 1,
            )
        )
    if vanadiumNumors[1] != 0:
        print(
            "{}{}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["vanadium"],
                int(numors["vanadium"][2]) - int(numors["vanadium"][1]) + 1,
            )
        )
    if absorberNumors[1] != 0:
        print(
            "{}{}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["absorber"],
                int(numors["absorber"][2]) - int(numors["absorber"][1]) + 1,
            )
        )
    if sampleNumors[1] != 0:
        print(
            "{}Sample {}: {} -{}, {} numors.".format(
                4 * " ",
                *numors["sample"],
                int(numors["sample"][2]) - int(numors["sample"][1]) + 1,
            )
        )
    return numors


def setVanaInfo(
    IncXS: float = 5.08,
    CohXS: float = 0.0184,
    ScaXS: float = 5.0984,
    AbsXS: float = 5.08,
    CohSL: float = -0.3824,
    molarM: float = 50.9415,
    NAtoms: float = 1.0,
    Diam: float = 6.08,
    Height: float = 50.0,
    density: float = 6.51,
) -> dict[str, Any]:
    """
    Create a dictionary with information about the vanadium (legacy behavior).
    """
    SelfQ0 = IncXS / 4.0 / np.pi
    den_aac = getAtomicDensity(density=density, molarMass=molarM)
    A = getMassNumber(molarMass=molarM)
    FreeIncXS = getFreeXS(BoundXS=IncXS, A=A)
    volume = getCylVolume(diameter=Diam, height=Height) / 1000.0

    vana: dict[str, Any] = {}
    vana["IncXS"] = IncXS
    vana["CohXS"] = CohXS
    vana["ScaXS"] = ScaXS
    vana["AbsXS"] = AbsXS
    vana["CohSL"] = CohSL
    vana["SelfQ0"] = SelfQ0
    vana["diam"] = Diam
    vana["NAtoms"] = NAtoms
    vana["molarM"] = molarM
    vana["den_gcc"] = density
    vana["den_aac"] = den_aac
    vana["A"] = A
    vana["FreeIncXS"] = FreeIncXS
    vana["volume"] = volume

    print(30 * "-")
    print("Standard of vanadium")
    print(
        4 * " ",
        "The standard is a cylinder of {:.3g} mm of diameter.".format(vana["diam"]),
    )
    print(4 * " ", "Volume in the beam = {:.3g} cm3.".format(vana["volume"]))
    print()
    print(
        4 * " ",
        "Bound incoherent cross section {:.6g} barns/atom.".format(vana["IncXS"]),
    )
    print(
        4 * " ",
        "Free incoherent cross section",
        "{:.6g} barns/atom.".format(vana["FreeIncXS"]),
    )
    print()
    print(
        4 * " ",
        "b**2 = sigma/4/pi at Q=0 (self) is",
        "{:.6g} barns/sterad/atom.".format(vana["SelfQ0"]),
    )
    print(
        4 * " ",
        "b**2 = sigma/4/pi at Q=infty is",
        "{:.6g} barns/sterad/atom".format(vana["FreeIncXS"] / 4.0 / np.pi),
    )
    print()
    print(4 * " ", "The molar mass is", "{:.6g} g/mol.".format(vana["molarM"]))
    print(
        4 * " ", "Mass number, A = ", "{:.6g} (= mass/neutron_mass)".format(vana["A"])
    )
    print()
    print(4 * " ", "Density = ", "{:.6g} g/cm3.".format(vana["den_gcc"]))
    print(4 * " ", "Atomic density = {:.6g} atoms/A3.".format(vana["den_aac"]))
    print()
    return vana


def setSampleInfo(
    comp_sample: Mapping[str, float],
    atoms_sample: Mapping[str, float],
    natoms_sample: float,
    elements: Mapping[str, Any],
    c_sample: Mapping[str, float],
    wavelength: float = 0.5,
    beamH: float = 50.0,
    vanavol: float = 1.0,
    vanadens: float = 0.0769591,
    height: float = 60.0,
    diameter: float = 5.0,
    mass: float = 1.0,
    density: float = 1.0,
    title: str = "sample",
) -> dict[str, Any]:
    """
    Create a dictionary with information about the sample (legacy behavior).
    """
    heightInBeam = min(height, beamH)
    volume = getCylVolume(diameter, height) / 1000.0
    volumeInBeam = getCylVolume(diameter=diameter, height=heightInBeam) / 1000.0
    effden_gcc = mass / volume
    packing = effden_gcc / density
    filling = heightInBeam / beamH

    molarM = AtomicAvg(c_sample, extractAttr(elements, "weight"))
    den_aac = getAtomicDensity(density=density, molarMass=molarM)
    effden_aac = getAtomicDensity(density=effden_gcc, molarMass=molarM)

    CohXS = AtomicAvg(c_sample, extractAttr(elements, "sig_coh"))
    IncXS = AtomicAvg(c_sample, extractAttr(elements, "sig_inc"))
    ScaXS = AtomicAvg(c_sample, extractAttr(elements, "sig_sca"))
    AbsXS = AtomicAvg(c_sample, extractAttr(elements, "sig_abs"))
    AbsWW = AbsXS * wavelength / 1.8
    CohSL = AtomicAvg(c_sample, extractAttr(elements, "re_bcoh"))
    A = AtomicAvg(c_sample, extractAttr(elements, "A"))

    FreeCohXS = getFreeXS(BoundXS=CohXS, A=A)
    FreeIncXS = getFreeXS(BoundXS=IncXS, A=A)
    FreeScaXS = getFreeXS(BoundXS=ScaXS, A=A)
    SelfQ0 = IncXS / 4.0 / np.pi

    VolRatioSV = volumeInBeam / vanavol
    DenRatioSV = effden_aac / vanadens

    sample: dict[str, Any] = {"Title": title}
    sample["height"] = height
    sample["heightInBeam"] = heightInBeam
    sample["diam"] = diameter
    sample["mass"] = mass
    sample["NAtoms"] = natoms_sample
    sample["molarM"] = molarM
    sample["volume"] = volume
    sample["volumeInBeam"] = volumeInBeam
    sample["den_gcc"] = density
    sample["effden_gcc"] = effden_gcc
    sample["packing"] = packing
    sample["filling"] = filling
    sample["den_aac"] = den_aac
    sample["effden_aac"] = effden_aac
    sample["CohXS"] = CohXS
    sample["IncXS"] = IncXS
    sample["ScaXS"] = ScaXS
    sample["AbsXS"] = AbsXS
    sample["AbsWW"] = AbsWW
    sample["CohSL"] = CohSL
    sample["A"] = A
    sample["FreeCohXS"] = FreeCohXS
    sample["FreeIncXS"] = FreeIncXS
    sample["FreeScaXS"] = FreeScaXS
    sample["SelfQ0"] = SelfQ0
    sample["VolRatioSV"] = VolRatioSV
    sample["DenRatioSV"] = DenRatioSV

    print(80 * "-")
    print("Sample", sample["Title"])

    text = " "
    print()
    print("Composition:")
    for key, value in comp_sample.items():
        text += "+ " + str(value) + " of " + key + " "
    print(4 * " ", 'A "unit" is', text[3:])

    text = " "
    print()
    print("Atomic composition:")
    for key, value in atoms_sample.items():
        text += "+ " + str(value) + " " + key + " atoms "
    print(4 * " ", 'A "unit" has', text[3:])
    print(4 * " ", "Number of atoms in one unit = {} atoms".format(sample["NAtoms"]))

    print()
    print("Atomic concentrations:")
    for key, value in c_sample.items():
        print(8 * " ", key, "{:.6f}".format(value))

    print()
    print("Average molar mass: {:.6g} g/mol/atom".format(sample["molarM"]))
    print("Mass number: {:.6g} amu".format(sample["A"]))
    print()
    print("Coherent cross section: {:.6g} barns/atom".format(sample["CohXS"]))
    print("Incoherent cross section: {:.6g} barns/atom".format(sample["IncXS"]))
    print("Scattering cross section: {:.6g} barns/atom".format(sample["ScaXS"]))
    print()
    print("Free coherent cross section: {:.6g} barns/atom".format(sample["FreeCohXS"]))
    print(
        "Free incoherent cross section: {:.6g} barns/atom".format(sample["FreeIncXS"])
    )
    print(
        "Free scattering cross section: {:.6g} barns/atom".format(sample["FreeScaXS"])
    )
    print()
    print("Absorption cross section: {:.6g} barns/atom".format(sample["AbsXS"]))
    print(
        "Absorption cross section at {:.6g} A: {:.6g} barns/atom".format(
            wavelength, sample["AbsWW"]
        )
    )
    print()
    print("Coherent scattering length: {:.6g} fm".format(sample["CohSL"]))
    print(
        "Self scattering cross section at Q=0: {:.6g} barns/steradian/atom".format(
            sample["SelfQ0"]
        )
    )
    print()
    print("Density: {:.6g} g/cm3".format(sample["den_gcc"]))
    print("Atomic density: {:.6g} atoms/A3".format(sample["den_aac"]))
    print()
    print("Cylindrical sample")
    print(4 * " ", "Diameter: {:.6g} mm".format(sample["diam"]))
    print(4 * " ", "Height: {:.6g} mm".format(sample["height"]))
    print(4 * " ", "Volume: {:.6g} cm3".format(sample["volume"]))
    print(4 * " ", "Mass: {:.6g} g".format(sample["mass"]))
    print(4 * " ", "Effective density: {:.6g} g/cm3".format(sample["effden_gcc"]))
    print(
        4 * " ",
        "Effective atomic density: {:.6g} atoms/A3".format(sample["effden_aac"]),
    )
    print()
    print(
        4 * " ", "Sample/Vanadium volume fraction: {:.6g}".format(sample["VolRatioSV"])
    )
    print(
        4 * " ", "Sample/Vanadium density fraction: {:.6g}".format(sample["DenRatioSV"])
    )
    print(4 * " ", "Packing fraction: {:.6g}".format(sample["packing"]))
    print(4 * " ", "Filling fraction: {:.6g}".format(sample["filling"]))

    return sample
