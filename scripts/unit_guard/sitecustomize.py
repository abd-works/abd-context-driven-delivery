"""The unit tier's time budget. ``scripts/test.ps1 -Suite unit`` puts this folder first on PYTHONPATH, so every spec
process of the unit tier imports it at start-up.

A unit example runs in microseconds to a few milliseconds, so hundreds of them run in seconds. Each example that takes
longer than ``CDD_UNIT_EXAMPLE_BUDGET_MS`` (its before.each and after.each included) is written, with its spec file and
its time, to the log ``CDD_UNIT_GUARD_LOG`` names, and the run fails that file. An example that needs real git, a
process, a server, or a big load to say what it says belongs in a ``*_heavy_spec.py``; otherwise make it fast with a
fake (``MockGit``) or a shared fixture."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mamba.example import Example

MILLISECONDS_PER_SECOND = 1000
_LOG = os.environ.get("CDD_UNIT_GUARD_LOG", "")
_BUDGET_SECONDS = float(os.environ.get("CDD_UNIT_EXAMPLE_BUDGET_MS", "100")) / MILLISECONDS_PER_SECOND


def _spec_file(example: Example) -> str:
    code = getattr(getattr(example, "test", None), "__code__", None)
    return code.co_filename if code is not None else "<unknown spec>"


def _example_path(example: Example) -> str:
    names = []
    node = example
    while node is not None:
        name = getattr(node, "name", "")
        if name:
            names.append(str(name))
        node = getattr(node, "parent", None)
    return " / ".join(reversed(names))


def _record_if_over_budget(example: Example) -> None:
    """Write an example that ran past the budget to the guard's log, with its spec file and its time."""
    seconds = example.elapsed_time.total_seconds()
    if seconds <= _BUDGET_SECONDS:
        return
    with open(_LOG, "a", encoding="utf-8") as log:
        log.write(f"{_spec_file(example)}\t{round(seconds * MILLISECONDS_PER_SECOND)}\t{_example_path(example)}\n")


def _time_examples() -> None:
    try:
        from mamba import example as mamba_example
    except ImportError:
        return
    finish = mamba_example.Example._finish

    def timed_finish(self: Example, reporter: object) -> None:
        finish(self, reporter)
        _record_if_over_budget(self)

    mamba_example.Example._finish = timed_finish


if _LOG:
    _time_examples()
