from __future__ import annotations

from pathlib import Path


def d4creg_log_path() -> Path:
    """
    Return the legacy logfile path and ensure its parent directory exists.

    Legacy uses a fixed relative path: `../logfiles/d4creg.log`.
    """
    log_path = Path("../logfiles/d4creg.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text("# d4creg.log\n\n", encoding="utf-8")
    return log_path
