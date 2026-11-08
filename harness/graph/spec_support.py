"""Spec support for the graph: counting the graphs code makes, so a spec can say an operation reads no graph back
and builds none of its own."""

from __future__ import annotations

from harness.graph.graph import Graph


class GraphsMade:
    """Counts the graphs made while it is open."""

    def __init__(self) -> None:
        self.made = 0
        self._init = Graph.__init__

    def __enter__(self) -> GraphsMade:
        counter = self

        def counted(graph, *arguments, **keywords):
            counter.made += 1
            counter._init(graph, *arguments, **keywords)

        Graph.__init__ = counted
        return self

    def __exit__(self, *_exc) -> None:
        Graph.__init__ = self._init
