"""The catalog board's stage columns, and the labels the board's tickets carry."""
from __future__ import annotations

from dataclasses import dataclass

from harness.guidance.stages import DISCOVERY, IMPLEMENTATION, SPECIFICATION, STAGES, ApproachStage, StageScope
from harness.name.name import Name


@dataclass(frozen=True)
class StageColumn:
    """One column of the catalog board: a stage of the approach and the names the catalog gives it.

    The stage's name, title, and scope come from the approach's stages. ``key`` is the column's name in the page
    markup, its styles, and its scripts (discovery, spec, engineer), so they keep working whatever the stage is called.
    ``template_tokens`` are the words a practice template's front matter uses for the stage.
    """

    stage: ApproachStage
    key: str
    template_tokens: tuple[str, ...]

    @property
    def label(self) -> str:
        """The lowercase column heading on the board."""
        return self.stage.title.lower()

    @property
    def scope(self) -> StageScope:
        return self.stage.scope


class StageColumns:
    """The board's columns in the order the approach walks the stages; the one place a stage meets its board key."""

    def __init__(self, columns: tuple[StageColumn, ...]) -> None:
        self._columns = columns

    def __iter__(self):
        return iter(self._columns)

    def of(self, stage: str) -> StageColumn | None:
        """The column that holds fidelities whose stage is ``stage``; none for a stage the board has no column for."""
        return next((column for column in self._columns if column.stage.name == stage), None)

    @property
    def stages(self) -> tuple[str, ...]:
        return tuple(column.stage.name for column in self._columns)


# The catalog's own names for each stage's column, by the stage's name: its key in the page markup, and the words
# practice templates' front matter use for it.
_COLUMN_KEYS = {DISCOVERY: "discovery", SPECIFICATION: "spec", IMPLEMENTATION: "engineer"}
_TEMPLATE_TOKENS = {
    DISCOVERY: ("discovery",),
    SPECIFICATION: ("exploration", "specification", "spec"),
    IMPLEMENTATION: ("engineering", "engineer"),
}
STAGE_COLUMNS = StageColumns(
    tuple(StageColumn(stage, _COLUMN_KEYS[stage.name], _TEMPLATE_TOKENS[stage.name]) for stage in STAGES)
)


class BoardLabel:
    """A name as a board ticket shows it, such as ``story-map`` for the fidelity ``story_map``: the name in kebab case,
    with the board's abbreviations written out, so ``ia`` reads ``information-architecture``. Fidelity, action, and
    utility tickets, and the example files named for a fidelity, all use it, so a ticket and its files agree."""

    _WRITTEN_OUT = {"cdd": "context-driven-delivery", "ia": "information-architecture"}

    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return self._WRITTEN_OUT.get(self._name) or Name(self._name).kebab
