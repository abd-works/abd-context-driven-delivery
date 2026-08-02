"""MemoryLeakHunt - launch a disciplined diagnosis loop for a suspected memory leak."""
from __future__ import annotations

from utilities.diagnose.diagnose import Diagnose


class MemoryLeakHunt:
    """Dispatch a six-phase Diagnose sub-agent focused on a memory leak in a module."""

    def start(self, module_path: str) -> str:
        """Invoke the diagnose sub-agent to investigate a leak in module_path.

        The sub-agent works through all six phases — build a feedback loop,
        reproduce, hypothesise, instrument, fix with a regression test, then
        clean up and write a post-mortem. It runs non-blocking so the host
        session stays responsive.
        """
        diag = Diagnose()
        return diag.diagnose()
