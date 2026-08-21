"""Example: expose a background analysis task as a non-blocking sub-agent tool."""

from __future__ import annotations

from sub_agent.sub_agent import sub_agent
from tools.tool import tool, toolset


@toolset
class ParallelRunner:
    """Toolset that routes heavy analysis work as a non-blocking sub-agent launch.

    The ``run_analysis`` method is decorated with ``@sub_agent`` on top of
    ``@tool``.  Standard tool discovery skips it; ``discover_sub_agent_tools``
    surfaces it with ``kind: sub_agent / launch: non_blocking`` in the manifest
    so the calling agent knows to spawn a background sub-agent rather than
    running the work inline.
    """

    @sub_agent
    @tool
    def run_analysis(self, target: str) -> str:
        """Analyse *target* as a background sub-agent.

        Scan *target* for clean-engineering violations and produce a
        structured report.  Because this method is marked ``@sub_agent``,
        the calling agent launches it as a non-blocking background task
        and continues without waiting for the result.
        """
        return f"analysed:{target}"
