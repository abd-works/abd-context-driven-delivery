from __future__ import annotations

from typing import Any


class Violation:
    def __init__(
        self,
        rule: str,
        message: str,
        *,
        location: str = "",
        line: int | None = None,
        severity: str = "error",
    ) -> None:
        self.rule = rule
        self.message = message
        self.location = location
        self.line = line
        self.severity = severity

    def to_dict(self) -> dict[str, Any]:
        return {
            "rule": self.rule,
            "violation_message": self.message,
            "severity": self.severity,
            "line_number": self.line,
            "location": self.location,
        }
