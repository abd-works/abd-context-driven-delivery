"""Practice Guidance — model fidelity (Python channel).

Stubs only. Same types as practice-guidance-model.md. Does not replace
harness/guidance/guidance.py.
"""
from __future__ import annotations

from typing import Any


class FidelityGuidance:
    """One fidelity of a practice — stage, default format, optional CE companion."""

    # must carry default_format from the fidelity markdown, never from a practice dict
    # never requires a Clean Engineering companion

    def __init__(
        self,
        name: str = "",
        stage: str = "",
        default_format: str = "",
        practice_guidance: PracticeGuidance | None = None,
        clean_engineering: FidelityGuidance | None = None,
    ) -> None:
        ...

    @property
    def name(self) -> str:
        ...

    @property
    def stage(self) -> str:
        ...

    @property
    def default_format(self) -> str:
        ...

    @property
    def practice_guidance(self) -> PracticeGuidance | None:
        ...

    @property
    def fidelity(self) -> str:
        ...

    @property
    def clean_engineering(self) -> FidelityGuidance | None:
        # null → skip; set → a FidelityGuidance owned by CleanEngineering
        ...


class PracticeGuidance:
    """A practice: fidelities from markdown, one render loop, format folders under model/."""

    # never _fidelity_format_defaults
    # never ce()
    # constructor format overrides FidelityGuidance.default_format
    # omitted format → current fidelity default_format
    # format folders live at {practice}/model/{format}/; never document/ diagram/ code/ web/

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: Any = None,
        fidelity: str | None = None,
        stage: str | None = None,
    ) -> None:
        ...

    @property
    def fidelities(self) -> Any:
        ...

    @property
    def format(self) -> str:
        ...

    @property
    def formats(self) -> dict[str, Any]:
        # keyed by format name; parse/render type in model/{format}/
        # empty on BDD and DDD
        ...

    def load_fidelities_from_markdown(self) -> None:
        # -> Markdown.fidelity_blocks
        # -> Markdown.fidelity_stage
        # -> Markdown.fidelity_format
        # -> Markdown.fidelity_clean_engineering
        # resolve companion name against CleanEngineering.fidelities; miss or empty → null
        ...

    def guidance(self) -> str:
        # -> fidelities.current
        # if current.clean_engineering is null, skip
        # -> current.clean_engineering.instructions
        ...

    def render(self, format: str, content: str, source: str | None = None) -> dict:
        # before: if formats is empty and current.clean_engineering is set
        # -> current.clean_engineering.practice_guidance.render
        # -> formats[source or self.format].parse
        # -> formats[format].render
        ...


class Markdown:
    """Extract fidelity fields from practice markdown — same pattern as Stage."""

    def fidelity_blocks(self, text: str) -> list[tuple[str, str]]:
        ...

    def fidelity_stage(self, body: str) -> str:
        ...

    def fidelity_format(self, body: str) -> str:
        # **Default format:** ; first token is the channel name
        ...

    def fidelity_clean_engineering(self, body: str) -> str:
        # **Clean Engineering:** {modules|model|code}; omit or empty → ""
        ...


class Render:
    """Caller-facing convert: each host’s PracticeGuidance.render."""

    def render(self, guidance: Any, format: str, content: str = "") -> list:
        # -> PracticeGuidance.render format content
        ...
