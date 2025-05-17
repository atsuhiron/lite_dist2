from datetime import datetime, timedelta, timezone

_JST = timezone(timedelta(hours=+9), "JST")
DT = datetime(2025, 4, 27, 20, 36, 10, 0, tzinfo=_JST)
