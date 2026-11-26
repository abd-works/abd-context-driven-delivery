"""LogTimestamp — the one way every log the framework keeps stamps its times, and the stamp a report's name ends with."""

from __future__ import annotations

from datetime import datetime, timezone

_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# The second, in UTC, that the name of a validation report or a handoff ends with, written so names sort by time:
# ``clean-engineering-code-20261116T075749.md``.
REPORT_DATE_FORMAT = "%Y%m%dT%H%M%S"


class LogTimestamp:
    """The time a session log line, a hook log entry, or a toast is stamped with: a moment in UTC, to the second, such
    as ``2026-11-07T17:30:05Z``. Every log a session keeps writes its times this one way, so their lines sort and compare
    alike."""

    def __init__(self, moment: datetime) -> None:
        self.moment = moment.astimezone(timezone.utc).replace(microsecond=0)

    @classmethod
    def now(cls) -> LogTimestamp:
        return cls(datetime.now(timezone.utc))

    @classmethod
    def read(cls, text: str) -> LogTimestamp:
        """The timestamp text names, as a log wrote it; raises ``ValueError`` for text that names no time."""
        return cls(datetime.strptime(text.strip(), _TIMESTAMP_FORMAT).replace(tzinfo=timezone.utc))

    def __str__(self) -> str:
        return self.moment.strftime(_TIMESTAMP_FORMAT)
