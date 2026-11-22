"""The worker process that draws one render: ``python -m cdd_guidance.actions.render.render_worker ORDER ANSWER``.

It reads the *RenderOrder* in ORDER, imports the module that registers the order's practice, makes the fidelity the
order names as an action in no session makes it, renders the order's text there, and writes the result to ANSWER. Its
progress goes to its stdout, one report a line, at most four a second, for the server that started it to pass on."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

from cdd_guidance.actions.render.render_order import RenderOrder
from harness.agent_tools.progress import reporting_to
from harness.guidance_actions import GuidanceCommand, WorkList
from harness.installation.data_class import data_of

from harness.mcp.tool_calls import ThrottledReporter


def _report_line(message: str) -> None:
    print(message.replace("\n", " "), flush=True)


def _fidelity_of(order: RenderOrder):
    """The fidelity the order renders at, made in no session from its practice's catalogue."""
    importlib.import_module(order.module)
    work = WorkList(None)
    work.take(GuidanceCommand.from_guidance(order.fidelity))
    return work.each(lambda worked: worked)[0]


def main(arguments: list[str]) -> None:
    if len(arguments) != 2:
        raise SystemExit("usage: python -m cdd_guidance.actions.render.render_worker ORDER ANSWER")
    order = RenderOrder.from_text(Path(arguments[0]).read_text(encoding="utf-8"))
    with reporting_to(ThrottledReporter(_report_line)):
        rendered = order.request_at(_fidelity_of(order)).render()
    Path(arguments[1]).write_text(json.dumps(data_of(rendered)), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
