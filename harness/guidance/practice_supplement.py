"""PracticeSupplement: guidance that adds to other practices at the fidelities it names, such as TDD on Clean Engineering
code, Stories acceptance_tests, BDD development, and DDD tactics."""
from __future__ import annotations

import functools
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from harness.agent_tools.agent_tools import agent_instructions
from harness.guidance.guidance import PracticeGuidance
from harness.guidance.working_set import WorkingSet
from harness.installation.files import skill
from harness.mcp.mcp_annotations import mcp
from harness.guidance.rule import Rule, RulesCollection
from harness.markdown.front_matter import FrontMatter
from harness.markdown.markdown import MarkdownText

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance

# Its own sections, which every fidelity it supplements reads; every other top section names the fidelities it is for.
_OWN_SECTIONS = ("overview", "guidance", "shared rules")


class UnknownSupplementedFidelity(Exception):
    """A supplement names a practice the set does not have, or a fidelity that practice does not have."""

    def __init__(self, supplement: str, practice_key: str, fidelity_name: str) -> None:
        super().__init__(
            f"the {supplement} supplement names {practice_key}: {fidelity_name}, which no practice of the set has"
        )
        self.supplement = supplement
        self.practice_key = practice_key
        self.fidelity_name = fidelity_name


class SupplementWorkingSet(WorkingSet):
    """A supplement's working set: beside the practices it works with, it reads the fidelities the supplement names
    into the set's own, once it is handed the set."""

    _practice: PracticeSupplement

    def hold(self, practices: Mapping[str, PracticeGuidance], supplements: Sequence[PracticeSupplement] = ()) -> None:
        super().hold(practices)
        self._practice.hold_supplemented(practices)


class PracticeSupplement(PracticeGuidance):
    """Guidance that adds to other practices at the fidelities it names. It is a practice of its own, kept with the
    practices, but it has no stage and no fidelities on the board: it never moves work forward. Its front matter names
    the fidelities it supplements (``supplements:``, practice key to fidelity name) and whether it is on in every
    session (``always_apply``); a practice with several supplemented fidelities names them as a list. Its document keeps the usual Overview and Guidance, then sections headed with the slugs of
    the fidelities they apply to (``## bdd-development``, or ``## stories-acceptance-tests, bdd-development`` for one
    that applies to both), each with its guidance and a ``### Rules`` list. Its Shared rules are the few that apply to
    all work, such as choosing the flow before writing code; every other rule names the fidelities it is for. A subclass that checks graph rules makes its *GraphOverlay* by overriding ``graph_overlay``, which
    every practice declares and answers none for, as a pattern does."""

    working_set_type = SupplementWorkingSet

    def __init__(self, format: str | None = None) -> None:
        super().__init__(format=format, fidelity=None)
        self.supplemented_fidelities: list[FidelityGuidance] = []
        """The fidelities it supplements: the same set's own objects, held once its working set is handed the set."""

    @functools.cached_property
    def _settings(self) -> dict[str, Any]:
        """Its front matter, read once."""
        return yaml.safe_load(FrontMatter(self.document.text).settings) or {}

    @property
    def always_apply(self) -> bool:
        """On for every session without being chosen."""
        return bool(self._settings.get("always_apply"))

    def hold_supplemented(self, practices: Mapping[str, PracticeGuidance]) -> None:
        """Read the front matter's practice and fidelity names into the fidelities of practices, the set's own, once:
        after this nothing holds a practice name or fidelity name as text."""
        self.supplemented_fidelities = [
            self._fidelity_in(practices, key, name)
            for key, names in (self._settings.get("supplements") or {}).items()
            for name in self._names_in(names)
        ]

    def _names_in(self, names: str | list[str]) -> list[str]:
        """The fidelity names front matter gives a practice: one name, such as ``code``, or a list of them, such as
        ``[acceptance_tests, hardening]``, since a practice is named once in the mapping."""
        return [names] if isinstance(names, str) else list(names)

    def _fidelity_in(self, practices: Mapping[str, PracticeGuidance], key: str, name: str) -> FidelityGuidance:
        practice = practices.get(key)
        fidelity = practice.fidelities.called(name) if practice is not None else None
        if fidelity is None:
            raise UnknownSupplementedFidelity(self.key, key, name)
        return fidelity

    @property
    def supplemented_practices(self) -> list[PracticeGuidance]:
        """The practice of each fidelity it supplements, once each."""
        return list(dict.fromkeys(fidelity.practice_guidance for fidelity in self.supplemented_fidelities))

    @property
    def process(self) -> str:
        """Its Overview and Guidance under ``## Supplement: {key}``: the order of work, which comes before any rule, and
        which a reply naming several fidelities it supplements gives once."""
        parts = (f"## Supplement: {self.key}", (self.overview or "").strip(), (self.guidance or "").strip())
        return "\n\n".join(part for part in parts if part)

    def text_for(self, fidelity: FidelityGuidance) -> str:
        """Each of its sections that names fidelity, under ``## Supplement: {key} for {fidelity}``; empty for a fidelity
        it does not supplement. Its process is given apart, once, by ``process``."""
        if fidelity not in self.supplemented_fidelities:
            return ""
        parts = (f"## Supplement: {self.key} for {fidelity.slug}", *self._sections_of(fidelity))
        return "\n\n".join(part for part in parts if part)

    def records_for(self, fidelity: FidelityGuidance, files: list[Path] | None = None) -> str:
        """What it keeps in the session about the files a generate or a render at fidelity writes, and what it leaves
        the agent to decide and record, as text for that action's reply. files are the files just saved; with none it
        reads the files fidelity has in the session. A supplement keeps nothing unless it says so here."""
        return ""

    def rules_for(self, fidelity: FidelityGuidance) -> list[RulesCollection]:
        """The rules of each of its sections that names fidelity; none for a fidelity it does not supplement."""
        if fidelity not in self.supplemented_fidelities:
            return []
        return [
            RulesCollection.from_markdown(MarkdownText(section).slice_heading("Rules"), fidelity.name, self)
            for section in self._sections_of(fidelity)
        ]

    def _sections_of(self, fidelity: FidelityGuidance) -> list[str]:
        """Each of its top sections whose heading names fidelity's slug, alone or among others, in document order."""
        headings = [name for _start, _end, level, name in self.document.headings() if level == 2]
        named = [name for name in headings if fidelity.slug in (slug.strip() for slug in name.split(","))]
        return [self.document.slice_heading(name) for name in named]

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """overview"""
        parts = ((self.overview or "").strip(), (self.guidance or "").strip(), *self._fidelity_sections)
        return "\n\n".join(part for part in parts if part)

    @property
    def checked_rule_collections(self) -> list[RulesCollection]:
        """The rules of every section, each named for the fidelities it applies to: what a validate of the supplement
        itself checks."""
        return [RulesCollection.from_markdown(MarkdownText(section).slice_heading("Rules"), None, self) for section in self._fidelity_sections]

    @property
    def every_rule(self) -> list[Rule]:
        """Every rule of every section it holds."""
        return [rule for collection in self.checked_rule_collections for rule in collection]

    @property
    def _fidelity_sections(self) -> list[str]:
        """Each top section other than its Overview and Guidance: the sections named for the fidelities they apply to."""
        headings = [name for _start, _end, level, name in self.document.headings() if level == 2]
        return [self.document.slice_heading(name) for name in headings if name.casefold() not in _OWN_SECTIONS]
