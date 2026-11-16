"""The unit tier's time budget, as Mamba output formats. ``scripts/test.ps1 -Suite unit`` puts this folder on PYTHONPATH
and runs every spec file with ``--format budget_formatter.BudgetDocumentation`` (``BudgetProgress`` for the quiet re-run),
a custom formatter Mamba builds from that dotted name: Mamba's own extension point for hearing each example's end.

A unit example runs in microseconds to a few milliseconds, so hundreds of them run in seconds. Each example that takes
longer than ``CDD_UNIT_EXAMPLE_BUDGET_MS`` (its before.each and after.each included) is written, with its spec file and
its time, to the log ``CDD_UNIT_GUARD_LOG`` names, and the run fails that file. An example that needs real git, a
process, a server, or a big load to say what it says belongs in a ``*_heavy_spec.py``; otherwise make it fast with a
fake (``MockGit``) or a shared fixture."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from mamba.formatters import DocumentationFormatter, ProgressFormatter

if TYPE_CHECKING:
    from mamba.example import Example
    from mamba.settings import Settings

MILLISECONDS_PER_SECOND = 1000


class UnitBudget:
    """The budget one spec process times its examples against, and the log an example over it is written to."""

    def __init__(self, log: str, budget_ms: float) -> None:
        self.log = log
        self.seconds = budget_ms / MILLISECONDS_PER_SECOND

    @classmethod
    def from_environment(cls) -> UnitBudget:
        return cls(os.environ.get("CDD_UNIT_GUARD_LOG", ""), float(os.environ.get("CDD_UNIT_EXAMPLE_BUDGET_MS", "100")))

    def over_budget_line(self, example: Example) -> str:
        """The log line for an example that ran past the budget: its spec file, its time, and its describe path; empty
        for an example within the budget."""
        seconds = example.elapsed_time.total_seconds()
        if seconds <= self.seconds:
            return ""
        return f"{self._spec_file(example)}\t{round(seconds * MILLISECONDS_PER_SECOND)}\t{self._example_path(example)}\n"

    def record(self, example: Example) -> None:
        """Write an example that ran past the budget to the log; nothing when no log is named."""
        line = self.over_budget_line(example)
        if not self.log or not line:
            return
        with open(self.log, "a", encoding="utf-8") as log:
            log.write(line)

    def _spec_file(self, example: Example) -> str:
        """The spec file that declares the example."""
        code = getattr(getattr(example, "test", None), "__code__", None)
        return code.co_filename if code is not None else "<unknown spec>"

    def _example_path(self, example: Example) -> str:
        """The example's describe path, outermost first."""
        names = []
        node = example
        while node is not None:
            name = getattr(node, "name", "")
            if name:
                names.append(str(name))
            node = getattr(node, "parent", None)
        return " / ".join(reversed(names))


class BudgetTiming:
    """A Mamba output format's part that times each finished example against the unit budget, mixed in ahead of the
    format it reports through."""

    def __init__(self, mamba_settings: Settings) -> None:
        super().__init__(mamba_settings)
        self.budget = UnitBudget.from_environment()

    def example_passed(self, example: Example) -> None:
        super().example_passed(example)
        self.budget.record(example)

    def example_failed(self, example: Example) -> None:
        super().example_failed(example)
        self.budget.record(example)


class BudgetDocumentation(BudgetTiming, DocumentationFormatter):
    """Mamba's documentation output, with each finished example timed against the unit budget."""


class BudgetProgress(BudgetTiming, ProgressFormatter):
    """Mamba's progress output, with each finished example timed against the unit budget."""
