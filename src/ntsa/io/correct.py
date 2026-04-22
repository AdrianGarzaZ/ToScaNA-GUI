from __future__ import annotations

from typing import Any

from ntsa.utils.commands import execute_command_and_write_to_file


def generate_com(
    CORRECT_template: str = "correct_template.com",
    name: str = "prueba",
    rsample: float = 0.5,
    density: float = 0.11,
    MTname: str = "MTBelljar_6mm",
    MTCanname: str = "MTCan_6mm",
    rcan: float = 0,
    Vananame: str = "Vanadium_7mm",
    rvana: float = 0.7,
    beam_width: float = 0.6,
    beam_height: float = 1.6,
) -> None:
    """
    Generate an input file for CORRECT starting from a template (legacy behavior).

    Notes
    -----
    The legacy implementation also attempted to run CORRECT via a placeholder
    command; we preserve the call pattern but keep it non-crashing when the
    executable is missing (handled in `execute_command_and_write_to_file`).
    """
    with open(CORRECT_template, "r") as f:
        text = "".join(f.readlines())

    text = text.replace("{pyfname}", name)
    text = text.replace("{pyradius_cm}", str(rsample))
    text = text.replace("{pydensity_at_AA3}", str(density))
    text = text.replace("{pymtbelljarname}", MTname)
    text = text.replace("{pycanname}", MTCanname)
    text = text.replace("{pyradius_can}", str(rcan))
    text = text.replace("{pyradius_vana}", str(rvana))
    text = text.replace("{pyvanadiumname}", Vananame)
    text = text.replace("{pybeam_w_cm}", str(beam_width))
    text = text.replace("{pybeam_h_cm}", str(beam_height))
    print(text)

    with open(f"{name}.com", "w") as f:
        f.writelines(text)

    # Legacy placeholder "example usage"
    command_to_run = ["executable_name", "arg1"]
    output_file_path = "output.txt"
    execute_command_and_write_to_file(command_to_run, output_file_path)


def saveCORRECT(expt: Any) -> None:  # noqa: N802 (legacy API)
    """
    Write a CORRECT `.com` file from a legacy-style experiment object.

    Parity-first copy of `legacy/lib/toscana.py::saveCORRECT`.
    """
    parfile = expt.sampleTitle + ".com"
    with open(parfile, "w") as f:
        f.write("! " + parfile + "\n")
        f.write("!\n")
        f.write("instr " + expt.instrument + "\n")
        line = 'sample "{}.adat" {} /temperature={} /density={} /packing={:8.6f} /fullness={}'.format(
            expt.sampleTitle,
            expt.sampleOuterRadius / 10.0,
            expt.sampleTemperature,
            expt.sampleDensity,
            expt.samplePackingFraction,
            expt.sampleFullness,
        )
        f.write(line + "\n")
        can = expt.containerFile[0:-5] + ".adat"
        f.write('container "{}" {}\n'.format(can, expt.container[3] / 20.0))
        bckg = expt.environmentFile[0:-5] + ".adat"
        f.write('background "{}" 0.8\n'.format(bckg))
        f.write('! black "absorber.adat" 0.93\n')
        vana = expt.vanadiumFile[0:-5] + ".adat"
        f.write(
            'vanadium "{}" {} /smoothing=1 /multiplier=1.02\n'.format(
                vana, expt.vanadium[3] / 20.0
            )
        )
        f.write('background /vanadium "{}" 0.85\n'.format(bckg))
        f.write("wavelenght {}\n".format(expt.wavelength))
        f.write("! zeroangle = {} already subtracted\n".format(expt.zeroAngle))
        f.write("zeroangle {}\n".format(0.0))
        f.write("beam {} {}\n".format(expt.beamHeight / 10.0, expt.beamWidth / 10.0))
        f.write("! xout angle\n")
        f.write("! output " + expt.sampleTitle + ".corr\n")
        f.write('! title "' + expt.sampleTitle + '.corr (after correct)"\n')
        f.write("xout q\n")
        f.write("output " + expt.sampleTitle + ".corr.q\n")
        f.write('title "' + expt.sampleTitle + '.corr.q (after correct)"\n')
        f.write("spectrum 1\n")
        f.write("execute/nopause\n")
        f.write("quit\n")
    return
