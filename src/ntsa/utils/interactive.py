from __future__ import annotations

import sys


def stop(message: str) -> None:
    """
    Legacy interactive stop helper.

    Divergence vs legacy:
    - In non-interactive environments (`sys.stdin.isatty() == False`), raises
      `RuntimeError` instead of prompting, to avoid CI hangs.
    """
    print()
    print(30 * "<>")
    print(message)

    if not (hasattr(sys.stdin, "isatty") and sys.stdin.isatty()):
        raise RuntimeError("stop() called in non-interactive mode")

    answer = input("Do you want to continue? (y/n) :")
    if answer == "n":
        raise SystemExit("You stopped the program. Bye!")
    return None
