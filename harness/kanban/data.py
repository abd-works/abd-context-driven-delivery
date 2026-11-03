"""The shapes the board's tools return. The language adapter reads these, so they are the only agreement with TypeScript."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class ActionStatesData(TypedDict):
    generate: str
    validate: str
    review: str


class TicketData(TypedDict):
    title: str
    last_activity: str
    name: str
    scope: str
    parent: str
    column: str
    is_done: bool
    next: str | None
    next_action: str
    handoff: str
    reports: dict[str, str]
    violation_counts: dict[str, int]
    practices: dict[str, bool]
    progress: dict[str, str]
    actions: dict[str, ActionStatesData]
    allowed_actions: dict[str, list[str]]


class BacklogItemData(TypedDict):
    title: str
    last_activity: str
    text: str
    path: str


class ColumnData(TypedDict):
    """Backlog sends items; a stage sends the fields of work; Complete sends tickets."""

    name: str
    items: NotRequired[list[BacklogItemData]]
    tickets: NotRequired[list[TicketData]]
    work_required: NotRequired[list[str]]
    formats: NotRequired[dict[str, list[str]]]
    default_formats: NotRequired[dict[str, str]]
    wip_limit: NotRequired[int]
    is_over_limit: NotRequired[bool]
    in_progress: NotRequired[list[TicketData]]
    done: NotRequired[list[TicketData]]


class BoardData(TypedDict):
    project: str
    active: str | None
    columns: list[ColumnData]


class HelpRuleData(TypedDict):
    slug: str
    text: str


class HelpData(TypedDict):
    practice: str
    fidelity: str
    stage: str
    overview: str
    guidance: str
    rules: list[HelpRuleData]
    href: str


class WorkspaceData(TypedDict):
    has_branch: bool
    has_worktree: bool
    leaving_has_branch: bool


class FileEntryData(TypedDict):
    path: str
    exists: bool


class FileTextData(TypedDict):
    path: str
    text: str


class SourceLineData(TypedDict):
    number: int
    text: str


class ViolationData(TypedDict):
    location: str
    line: int | None
    message: str
    source: list[SourceLineData]


class ReportRuleData(TypedDict):
    fidelity: str
    name: str
    description: str
    count: int
    violations: list[ViolationData]


class ReportData(TypedDict):
    path: str
    text: str
    rules: list[ReportRuleData]
    has_saved_graph: bool
