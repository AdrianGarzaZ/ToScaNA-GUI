from __future__ import annotations

import cmath
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

import numpy as np

from ntsa.io.loading import read_3col
from ntsa.isotopes.core import elemento
from ntsa.physics.properties import getAbsXS, getAtomicDensity

if TYPE_CHECKING:
    from numpy.typing import NDArray


class Measurement:
    """
    Legacy-compatible measurement container.

    Notes
    -----
    This mirrors `legacy/lib/toscana.py::Measurement` (parity-first) and is
    intentionally attribute-heavy to match legacy call sites.
    """

    def __init__(self, inputPar: Mapping[str, Sequence[str]]):
        self.inputPar = inputPar

        self.parfile = inputPar["<par>"][1]
        self.instrument = inputPar["<ins>"][1]
        self.proposal = inputPar["<pro>"][1]
        self.mainProposer = inputPar["<mpr>"][1]
        self.localContact = inputPar["<lco>"][1]
        self.startDate = inputPar["<sta>"][1]
        self.endDate = inputPar["<end>"][1]
        self.cycle = inputPar["<cyc>"][1]
        self.notebook = inputPar["<nbk>"][1]
        self.page = inputPar["<pag>"][1]
        self.envCode = inputPar["<env>"][1]

        self.zeroAngle = float(inputPar["<zac>"][1])
        self.wavelength = float(inputPar["<wle>"][1])

        self.vslits = (float(inputPar["<lft>"][1]), float(inputPar["<rgt>"][1]))
        self.hslits = (float(inputPar["<top>"][1]), float(inputPar["<bot>"][1]))
        self.beamHeight = self.hslits[0] - self.hslits[1]
        self.beamWidth = self.vslits[0] - self.vslits[1]

        self.angularPrecision = float(inputPar["<apr>"][1])
        self.aScale = (
            float(inputPar["<asc>"][1]),
            float(inputPar["<asc>"][2]),
            float(inputPar["<asc>"][3]),
        )
        self.qScale = (
            float(inputPar["<qsc>"][1]),
            float(inputPar["<qsc>"][2]),
            float(inputPar["<qsc>"][3]),
        )
        self.rScale = (
            float(inputPar["<rsc>"][1]),
            float(inputPar["<rsc>"][2]),
            float(inputPar["<rsc>"][3]),
        )

        self.container = (
            inputPar["<Cmater>"][1],
            inputPar["<Cshape>"][1],
            float(inputPar["<Cshape>"][2]),
            float(inputPar["<Cshape>"][3]),
            float(inputPar["<Cshape>"][4]),
        )
        self.normaliser = (
            "Vanadium",
            inputPar["<Nshape>"][1],
            float(inputPar["<Nshape>"][2]),
            float(inputPar["<Nshape>"][3]),
            float(inputPar["<Nshape>"][4]),
        )
        self.absorber = (
            inputPar["<Amater>"][1],
            inputPar["<Ashape>"][1],
            float(inputPar["<Ashape>"][2]),
            float(inputPar["<Ashape>"][3]),
            float(inputPar["<Ashape>"][4]),
        )
        self.environ = (
            inputPar["<Emater>"][1],
            inputPar["<Eshape>"][1],
            float(inputPar["<Eshape>"][2]),
            float(inputPar["<Eshape>"][3]),
            float(inputPar["<Eshape>"][4]),
        )

        self.Description = inputPar["<Sdescr>"][1]
        self.TempK = float(inputPar["<StempK>"][1])
        self.TempC = float(inputPar["<StempK>"][1]) - 273.15

        self.NbrElements = int(inputPar["<SNelem>"][1])
        self.Mass = float(inputPar["<Smassc>"][1])
        self.Density = float(inputPar["<Sdegcc>"][1])
        self.Shape = (
            inputPar["<Sshape>"][1],
            float(inputPar["<Sshape>"][2]),
            float(inputPar["<Sshape>"][3]),
            float(inputPar["<Sshape>"][4]),
        )
        self.Fullness = float(inputPar["<Sfulln>"][1])
        self.Height = self.Shape[3]

        self.InnerDiam = self.Shape[1]
        self.OuterDiam = self.Shape[2]
        self.InnerRadius = self.InnerDiam / 2.0
        self.OuterRadius = self.OuterDiam / 2.0

        # Legacy warning check (keep).
        if float(self.container[2]) != self.OuterDiam:
            print(
                "WARNING! Container inner diameter should be equal",
                "to sample outer diameter",
            )
            msg = "    Container id = {} mm != Sample od = {} mm"
            print(msg.format(float(self.container[2]), self.OuterDiam))

        self.Title = inputPar["<Stitle>"][1]

        # Note: legacy uses (ro - ri)^2 rather than (ro^2 - ri^2); preserve.
        self.Volume = (
            np.pi * self.Height / 1000.0 * (self.OuterRadius - self.InnerRadius) ** 2
        )
        self.EffDensity = self.Mass / float(self.Volume)
        self.PackingFraction = self.EffDensity / self.Density

        self.conFile = inputPar["<CoFile>"][1].strip()
        self.norFile = inputPar["<NoFile>"][1].strip()
        self.envFile = inputPar["<EnFile>"][1].strip()
        self.File = inputPar["<SaFile>"][1].strip()
        self.absFile = inputPar["<AbFile>"][1].strip()

        self.Data: NDArray[np.float64] = read_3col(self.File)
        self.envData: NDArray[np.float64] = read_3col(self.envFile)
        self.conData: NDArray[np.float64] = read_3col(self.conFile)
        self.norData: NDArray[np.float64] = read_3col(self.norFile)
        self.absData: NDArray[np.float64] = read_3col(self.absFile)

        atoms: dict[str, float] = {}
        natoms = 0.0
        for elem_idx in range(self.NbrElements):
            ordatom = str(elem_idx + 1).zfill(2)
            label = "<Sato" + ordatom + ">"
            natoms += float(inputPar[label][2])
            atoms[inputPar[label][1]] = float(inputPar[label][2])

        self.natoms = natoms
        self.atoms = atoms
        self.symbols = list(atoms.keys())

        conc: dict[str, float] = {}
        for symbol in list(atoms.keys()):
            conc[symbol] = atoms[symbol] / natoms
        self.conc = conc

        self.nuclei: dict[str, tuple[object, ...]] = {}
        for symbol in list(atoms.keys()):
            iso = elemento(symbol)
            self.nuclei[symbol] = (
                symbol,
                atoms[symbol],
                conc[symbol],
                iso.weight,
                iso.bcoh,
                iso.binc,
                iso.sig_coh,
                iso.sig_inc,
                iso.sig_sca,
                iso.sig_abs,
            )

        self.molarMass = 0.0
        bcoh_acc: complex = 0j
        binc_acc: complex = 0j
        self.scoh = 0.0
        self.sinc = 0.0
        self.ssca = 0.0
        self.sabs = 0.0
        for symbol in list(atoms.keys()):
            iso = elemento(symbol)
            self.molarMass += iso.weight * conc[symbol]
            bcoh_acc += iso.bcoh * conc[symbol]
            binc_acc += iso.binc * conc[symbol]
            self.scoh += iso.sig_coh * conc[symbol]
            self.sinc += iso.sig_inc * conc[symbol]
            self.ssca += iso.sig_sca * conc[symbol]
            self.sabs += iso.sig_abs * conc[symbol]

        self.bcoh = float(cmath.polar(bcoh_acc)[0])
        self.binc = float(cmath.polar(binc_acc)[0])
        self.free = (
            self.ssca * (self.molarMass / (self.molarMass + elemento("n1").weight)) ** 2
        )
        self.b2lowQ = self.ssca / 4 / np.pi
        self.b2highQ = self.free / 4 / np.pi
        self.sabswl = getAbsXS(self.sabs, self.wavelength)

        self.AtomicDensity = getAtomicDensity(
            density=self.Density, molarMass=self.molarMass
        )
        self.EffAtomicDensity = getAtomicDensity(
            density=self.EffDensity, molarMass=self.molarMass
        )

    def showTable(self, outfile: str | None = None) -> None:  # noqa: N802 (legacy API)
        import sys

        if outfile:
            sys.stdout = open(outfile, "w")

        print(120 * "-")
        print(f"Input parameters from {self.inputPar['<par>'][1]}")
        print("".format())
        print(
            " {:<15} {:<15} {:<20} {:<20} {:<25} {:<20}".format(
                *self.inputPar["<ins>"],
                *self.inputPar["<cyc>"],
                *self.inputPar["<env>"],
            )
        )
        print(
            " {:<15} {:<15} {:<20} {:<20} {:<25} {:<20}".format(
                *self.inputPar["<pro>"],
                *self.inputPar["<mpr>"],
                *self.inputPar["<lco>"],
            )
        )
        print(
            " {:<15} {:<15} {:<20} {:<20} {:<25} {:<20}".format(
                *self.inputPar["<sta>"],
                *self.inputPar["<nbk>"],
                *self.inputPar["<pag>"],
            )
        )
        print(
            " {:<15} {:<15} {:<20} {:<20} {:<25} {:<15}".format(
                *self.inputPar["<wle>"],
                *self.inputPar["<zac>"],
                *self.inputPar["<apr>"],
            )
        )
        print(" {}".format("Beam dimensions:"))
        print(
            " {:<9} {:<5} {:<12} {:<5} | {:<7} {:<5} | {:<10} {:<5} {:<11} {:<5} | {:<7} {:<5}".format(
                *self.inputPar["<top>"],
                *self.inputPar["<bot>"],
                "Height (mm)=  ",
                self.beamHeight,
                *self.inputPar["<lft>"],
                *self.inputPar["<rgt>"],
                "Width (mm)=  ",
                self.beamWidth,
            )
        )
        print("".format())

        if outfile:
            sys.stdout = sys.__stdout__
