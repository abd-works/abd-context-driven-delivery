"""The facts that compare a node with the rest of Clean Engineering's graph, recorded once every node is read.

A rule reads a node's facts and compares them with its limit; it never works out across nodes what the graph already
holds. Each read records these facts after it has linked every class it holds, those read now and those a refresh kept,
from their saved facts and the graph's edges: a refresh records them again over the whole practice, so a fact that
depends on another file's imports stays right, and a graph read back from its saved file holds them as saved."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress

from cdd_guidance.practices.clean_engineering.model.class_facts import (
    BuiltCollaborators,
    DomainExtensions,
    Forwarding,
    ParallelModels,
    ResourceShapes,
)
from cdd_guidance.practices.clean_engineering.model.class_graph import ClassGraph
from cdd_guidance.practices.clean_engineering.model.folder_facts import ImportCycleFacts, SiblingFanOut
from cdd_guidance.practices.clean_engineering.model.module_exposure import ModuleExposure
from cdd_guidance.practices.clean_engineering.model.public_routes import PublicRoutes, registered_in_this_process
from cdd_guidance.practices.clean_engineering.model.operation_facts import BodyCopies, FailureMessages

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.model.graph_reading import GraphReading


class ComparedFacts:
    """One recording of the compared facts over the practice the reading holds: its folders', its classes', and its
    operations'."""

    def __init__(self, reading: "GraphReading") -> None:
        self._reading = reading

    def record(self) -> None:
        report_progress("clean_engineering · compared facts")
        in_graph = self._reading.in_graph
        classes = ClassGraph(self._reading)
        for part in (
            ImportCycleFacts(in_graph),
            SiblingFanOut(in_graph),
            ModuleExposure(in_graph, classes, PublicRoutes(registered_in_this_process())),
            ResourceShapes(classes),
            ParallelModels(classes),
            Forwarding(in_graph, classes),
            DomainExtensions(in_graph, classes),
            BuiltCollaborators(in_graph, classes),
            BodyCopies(in_graph),
            FailureMessages(in_graph, classes),
        ):
            part.record()
