"""What a diagnostics probe found: one outcome per MCP operation it probed, and the section of diagnostics.json that holds
one phase's outcomes and owns the colour rule."""

from __future__ import annotations

import json
from typing import Any

_PREVIEW_CHARS = 180
_FAILURE_CHARS = 400


class ProbeOutcome:
    """What probing one MCP operation found: green with a preview of its answer, yellow when the probe skipped it, red
    with what failed."""

    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"

    def __init__(self, mcp: str, color: str, **details: Any) -> None:
        self.mcp = mcp
        self.color = color
        self.details = details

    @classmethod
    def from_answer(cls, mcp: str, answer: Any) -> ProbeOutcome:
        """Green with a preview of what the operation answered; red when it answered nothing."""
        text = answer.strip() if isinstance(answer, str) else "" if answer is None else json.dumps(answer, default=str)
        if not text:
            return cls(mcp, cls.RED, failure="answered nothing", chars=0)
        return cls(mcp, cls.GREEN, chars=len(text), preview=text[:_PREVIEW_CHARS])

    @classmethod
    def from_failure(cls, mcp: str, failure: BaseException) -> ProbeOutcome:
        """Red, naming the failure the call raised."""
        return cls(mcp, cls.RED, failure=f"{type(failure).__name__}: {failure}"[:_FAILURE_CHARS])

    @classmethod
    def from_refusal(cls, mcp: str, reason: str) -> ProbeOutcome:
        """Red, because the probe could not call the operation, such as when it is not published."""
        return cls(mcp, cls.RED, failure=reason[:_FAILURE_CHARS])

    @classmethod
    def from_skip(cls, mcp: str, reason: str) -> ProbeOutcome:
        """Yellow, because the probe leaves this operation alone on purpose."""
        return cls(mcp, cls.YELLOW, skipped=reason)

    def called_on(self, paths: list[str]) -> ProbeOutcome:
        """This outcome, also naming the paths the probe called the operation on."""
        if paths:
            self.details["paths"] = list(paths)
        return self

    @property
    def is_red(self) -> bool:
        return self.color == self.RED

    @property
    def record(self) -> dict[str, Any]:
        """The outcome as diagnostics.json holds it."""
        return {"mcp": self.mcp, "color": self.color, **self.details}


class ProbeSection:
    """One phase of a probe as diagnostics.json records it: red when nothing was probed or any probe failed, yellow
    when the probe skipped every operation, else green."""

    def __init__(self, kind: str, outcomes: list[ProbeOutcome], slugs: list[str] | None = None) -> None:
        self.kind = kind
        self.outcomes = list(outcomes)
        self.slugs = list(slugs or [])

    @property
    def color(self) -> str:
        if not self.outcomes or any(outcome.is_red for outcome in self.outcomes):
            return ProbeOutcome.RED
        if all(outcome.color == ProbeOutcome.YELLOW for outcome in self.outcomes):
            return ProbeOutcome.YELLOW
        return ProbeOutcome.GREEN

    @property
    def report(self) -> str:
        counts = {color: sum(outcome.color == color for outcome in self.outcomes) for color in (ProbeOutcome.GREEN, ProbeOutcome.YELLOW, ProbeOutcome.RED)}
        report = f"{self.kind}: {counts['green']} answered, {counts['yellow']} skipped, {counts['red']} failed"
        return f"{report}, filter {', '.join(self.slugs)}" if self.slugs else report

    @property
    def record(self) -> dict[str, Any]:
        """The section as diagnostics.json holds it."""
        return {"color": self.color, "report": self.report, "items": [outcome.record for outcome in self.outcomes]}

    @property
    def reply(self) -> str:
        """The section as the diagnostics tool answers the agent: its colour first, marked with ``!`` when red."""
        mark = "!" if self.color == ProbeOutcome.RED else ""
        return f"{mark}{self.color}\n{self.report}"
