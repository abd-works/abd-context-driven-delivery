"""Pattern: what every stack pattern CDD ships is, the guidance and rules for one kind of solution laid over the
practices."""

from __future__ import annotations

from functools import cached_property

from harness.annotations.class_folder import class_folder
from harness.graph.pattern_overlays import GraphOverlay
from harness.guidance.guidance import PracticeGuidance


class Pattern(PracticeGuidance):
    """A pattern's guidance, written in TypeScript, named by the folder it is defined in (``pattern``), the name a graph
    applies it by, and the overlay it gives the graph (``graph_overlay``): the rules it adds to each practice, with no
    nodes of its own unless the pattern reads some. A class that only holds what several patterns share names itself
    no pattern (``pattern = ""``)."""

    pattern = ""

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if "pattern" not in cls.__dict__:
            cls.pattern = class_folder(cls).name

    def __init__(self) -> None:
        super().__init__(format="typescript")

    @cached_property
    def graph_overlay(self) -> GraphOverlay:
        """What this pattern gives the knowledge graph on top of the practices: the rules it adds to each practice, and
        no nodes. Made once and kept."""
        return GraphOverlay(self)
