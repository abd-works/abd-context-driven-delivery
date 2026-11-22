"""The facts that compare a node with the rest of Clean Engineering's graph, recorded once every node is read.

A rule reads a node's facts and compares them with its limit; it never works out across nodes what the graph already
holds. Each read records these facts after it has linked every class it holds, those read now and those a refresh kept,
from their saved facts and the graph's edges: a refresh records them again over the whole practice, so a fact that
depends on another file's imports stays right, and a graph read back from its saved file holds them as saved."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress

from cdd_guidance.practices.clean_engineering.reading.class_facts import (
    BuiltCollaborators,
    DomainExtensions,
    CopiedModels,
    PassThroughClasses,
    ServicesTakingDataBags,
)
from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClasses
from cdd_guidance.practices.clean_engineering.reading.folder_facts import FolderImportCycles, ModuleImports, SiblingFanOut
from cdd_guidance.practices.clean_engineering.reading.module_exposure import ModuleExposure
from cdd_guidance.practices.clean_engineering.reading.public_routes import PublicRoutes, registered_in_this_process
from cdd_guidance.practices.clean_engineering.reading.operation_facts import BodyCopies, FailureMessages

if TYPE_CHECKING:
    from cdd_guidance.practices.clean_engineering.reading.graph_reading import GraphReading


class ComparedFacts:
    """One recording of the compared facts over the practice the reading holds: its folders', its classes', and its
    operations'."""

    def __init__(self, reading: "GraphReading") -> None:
        self._reading = reading

    def record(self) -> None:
        report_progress("clean_engineering · compared facts")
        in_graph = self._reading.in_graph
        classes = ProductionClasses(self._reading)
        for part in (
            FolderImportCycles(in_graph),
            ModuleImports(in_graph),
            SiblingFanOut(in_graph),
            ModuleExposure(in_graph, classes, PublicRoutes(registered_in_this_process())),
            ServicesTakingDataBags(classes),
            CopiedModels(classes),
            PassThroughClasses(in_graph, classes),
            DomainExtensions(classes),
            BuiltCollaborators(classes),
            BodyCopies(in_graph),
            FailureMessages(in_graph, classes),
        ):
            part.record()
