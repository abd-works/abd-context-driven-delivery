"""What the graph's tools answer with, so an application outside Python reads the same shapes the agent does."""

from __future__ import annotations

from typing import Annotated, NotRequired, TypedDict

from harness.installation.destination import SourceFile


class GraphData(TypedDict):
    folder: str
    overlays: list[str]


class LoadData(TypedDict):
    message: str


class SavedData(TypedDict):
    path: str


class RuleHitData(TypedDict):
    message: str
    file: NotRequired[Annotated[str, SourceFile]]
    start: NotRequired[int]
    end: NotRequired[int]


class GraphTreeData(TypedDict):
    type: str
    name: str
    node_id: str
    status: NotRequired[str]
    violation: NotRequired[str]
    violations: NotRequired[list[RuleHitData]]
    children: list[GraphTreeData]


class PracticeInventoryData(TypedDict):
    node_counts: dict[str, int]
    edge_count: int
    node_types: list[str]
    edge_types: list[str]
    rules: list[str]
    tree: GraphTreeData


class InventoryData(TypedDict):
    practices: dict[str, PracticeInventoryData]
    overlays: list[str]
    available_overlays: list[str]


class OverlaysData(InventoryData):
    message: str


class OverlayData(TypedDict):
    overlay: str


class FilterChoicesData(TypedDict):
    node_types: list[str]
    relationships: list[str]
    rules: list[str]


class FilteredNodeData(TypedDict):
    practice: str
    type: str
    name: str
    node_id: str
    ancestors: list[str]
    children: list[str]
    rules: list[GraphTreeData]


class MemberData(TypedDict):
    id: str
    name: str
    kind: str
    owner: str
    text: str
    file: str
    start: int
    end: int


class SourceData(TypedDict):
    node_id: str
    name: str
    type: str
    file: Annotated[str, SourceFile]
    text: str
    start_line: int
    end_line: int
    members: list[MemberData]
