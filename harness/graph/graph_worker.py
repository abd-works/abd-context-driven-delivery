"""The worker process that carries out one graph build: ``python -m harness.graph.graph_worker ORDER RESULT CHANGES``.

It reads the *BuildOrder* in ORDER, imports the modules that register the practices and patterns the order names,
carries the order out on a graph of its own, and writes the graph it built to RESULT; for a refresh of the graph its
last answer held, it also writes what the refresh changed to CHANGES, which is all the server reads back. Its progress goes to its stdout,
one report a line, at most four a second, for the server that started it to pass on."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

from harness.agent_tools.progress import reporting_to
from harness.graph.graph import Graph
from harness.graph.graph_build import BuildOrder
from harness.mcp.tool_calls import ThrottledReporter


def _report_line(message: str) -> None:
    print(message.replace("\n", " "), flush=True)


def main(arguments: list[str]) -> None:
    if len(arguments) != 3:
        raise SystemExit("usage: python -m harness.graph.graph_worker ORDER RESULT CHANGES")
    order = BuildOrder.from_text(Path(arguments[0]).read_text(encoding="utf-8"))
    for module in order.modules:
        importlib.import_module(module)
    with reporting_to(ThrottledReporter(_report_line)):
        built = Graph().build.carry_out(order)
    Path(arguments[1]).write_text(built.text, encoding="utf-8")
    changes = order.changes(built)
    if changes is not None:
        Path(arguments[2]).write_text(changes.text, encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1:])
