from __future__ import annotations

import subprocess
from typing import Sequence


def execute_command_and_write_to_file(command: Sequence[str], output_file: str) -> None:
    """
    Run a command and write stdout to a file (legacy behavior).

    Divergence vs legacy:
    - also catches `OSError` (e.g. `FileNotFoundError`) so missing executables
      do not crash tests/CI.
    """
    try:
        with open(output_file, "w") as file:
            result = subprocess.run(
                command,
                check=True,
                text=True,
                stdout=file,
                stderr=subprocess.PIPE,
            )
            print("Return Code:", result.returncode)
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Command failed with return code", e.returncode)
        print("Error output:", e.stderr)
    except OSError as e:
        print("Error:", e)
