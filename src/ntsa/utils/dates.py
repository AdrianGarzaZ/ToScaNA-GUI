from __future__ import annotations

import calendar
from datetime import datetime


def getDate() -> str:
    """
    Produce a string with the current date in the legacy format:

        " Dayname DD/MM/YYYY HH:MM:SS"
    """
    now = datetime.now()
    day = " " + calendar.day_name[now.weekday()] + " "
    current_datetime = day + now.strftime("%d/%m/%Y %H:%M:%S")
    return current_datetime
