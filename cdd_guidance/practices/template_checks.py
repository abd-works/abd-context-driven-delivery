"""Spec support: each practice's templates read through its own graph rules, and each checked rule's example pair.

A template is what an author copies, so a template its own fidelity's rule fails teaches the shape the rule rejects,
and every file written from it is then reported. *TemplateCheck* places each template where its fidelity declares its
files, beside the practice's other markdown templates, reads the folder as a live load reads a working copy, and
answers what the graph rules report on it. *RuleExamples* answers, for one practice, which checked graph rules have no
failing and repaired example in the practice's ``rules/rule_examples.py`` (``EXAMPLE_PAIRS``), and which pairs fail.
"""

from __future__ import annotations

import importlib
import re
from typing import TYPE_CHECKING, Callable

from harness.graph.rule_fixture import RuleFixture
from harness.graph.saved_graph import SavedGraph
from harness.markdown.format import Format
from harness.markdown.markdown import Markdown, MarkdownScope

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance

# The name every named part of a declared path takes in a template's fixture, such as the epic's folder.
_EXAMPLE_NAME = "example-cart"
# The format groups whose templates are text a practice's graph reading reads.
_READ_GROUPS = ("markdown", "code")
_MARKDOWN = "markdown"
# A marker for a value the practice's code holds, named with a dot: ``{{child_band.sub_epic}}``.
_VALUE_MARKER = re.compile(r"\{\{\w+\.[\w.]+\}\}")
# How templates write a placeholder: ``{{Name}}``, `` `<name>` `` and ``{Name}``, each holding words on one line.
_PLACEHOLDERS = (
    re.compile(r"\{\{([^{}\n]+)\}\}"),
    re.compile(r"`<([^<>`\n]+)>`"),
    re.compile(r"\{([A-Za-z][\w .-]*)\}"),
)


class TemplateCheck:
    """One practice's templates through its own graph rules, each read where its fidelity declares its files."""

    def __init__(self, practice: PracticeGuidance) -> None:
        self._practice = practice

    def findings(self) -> dict[str, list[str]]:
        """What the practice's graph rules report on each template that fails one, by ``fidelity format``: each as its
        rule and what it said. A template no rule reports on is left out."""
        read = {name: self._read(fidelity, format) for name, fidelity, format in self._templates()}
        return {name: found for name, (nodes, found) in read.items() if found}

    def unread(self) -> list[str]:
        """The templates the practice reads no node from, by ``fidelity format``: no rule ran on them, so they are
        neither passed nor failed."""
        return [name for name, fidelity, format in self._templates() if not self._read(fidelity, format)[0]]

    def unfilled_markers(self) -> list[str]:
        """The markers for a value the practice's code holds (``{{child_band.sub_epic}}``) that its document or a
        template still carries once read: a marker whose name the practice hands no value for, such as a misspelt one,
        which an author would be handed as written."""
        read = [self._practice.document.text, *(self._raw(fidelity, format) for _name, fidelity, format in self._templates())]
        return sorted({marker for text in read for marker in _VALUE_MARKER.findall(text)})

    def checked(self) -> list[str]:
        """Every template there is to check, by ``fidelity format``."""
        return [name for name, _fidelity, _format in self._templates()]

    def _templates(self) -> list[tuple[str, FidelityGuidance, Format]]:
        """Each fidelity's template in each format it declares a file of, that has text."""
        found = []
        for fidelity in self._practice.fidelities:
            for label in fidelity.outputs:
                format = Format(label)
                if format.is_offered and format.group in _READ_GROUPS and self._placed(fidelity, format) and self._text(fidelity, format).strip():
                    found.append((f"{fidelity.slug} {format.name}", fidelity, format))
        return found

    def _read(self, fidelity: FidelityGuidance, format: Format) -> tuple[int, list[str]]:
        """How many nodes the practice reads from the template, and what its rules report on it."""
        own = self._placed(fidelity, format)
        beside = {
            self._placed(other, Format(_MARKDOWN)): self._text(other, Format(_MARKDOWN))
            for other in self._practice.fidelities
            if other is not fidelity and self._placed(other, Format(_MARKDOWN)) and self._text(other, Format(_MARKDOWN)).strip()
        }
        fixture = RuleFixture(type(self._practice), {**beside, own: self._text(fidelity, format)})
        saved = SavedGraph.from_graph(fixture.practice.reading.graph).practices[self._practice.key]
        nodes = [node for node in saved.nodes if node.file == own]
        found = [f"{violation.rule}: {violation.message}" for violation in saved.violations if violation.location == own]
        return len(nodes), sorted(found)

    def _text(self, fidelity: FidelityGuidance, format: Format) -> str:
        """The fidelity's template in format with its placeholders filled in; nothing when it has none in that format."""
        return self._filled(self._raw(fidelity, format))

    def _raw(self, fidelity: FidelityGuidance, format: Format) -> str:
        """The fidelity's template in format, as an author is handed it; nothing when it has none in that format."""
        located = Markdown.from_label(fidelity, "templates", MarkdownScope.of(fidelity).at(format.name))
        path = located.location.path
        return located.extract() if path is not None and path.suffix == format.extension else ""

    def _filled(self, template: str) -> str:
        """template with each placeholder written as the words it holds, as an author fills it in: ``{{Root}}``,
        ``{DomainEntity}`` and `` `<ConceptA>` `` become ``Root``, ``DomainEntity`` and ``ConceptA``. A placeholder's
        own braces are no name a reader can resolve, so left in they fail rules the filled file would pass."""
        for placeholder in _PLACEHOLDERS:
            template = placeholder.sub(lambda found: found.group(1), template)
        return template

    def _placed(self, fidelity: FidelityGuidance, format: Format) -> str:
        """Where the fidelity declares its file in format, each named part filled with the example's name; nothing for
        a format it declares no single file of."""
        declared = fidelity.outputs.get(format.name)
        first = declared if isinstance(declared, str) else (declared[0] if declared else "")
        if not first or first.endswith("/"):
            return ""
        snake = re.sub(r"\{[^{}/]*snake[^{}/]*\}", _EXAMPLE_NAME.replace("-", "_"), first)
        return re.sub(r"\{[^{}/]+\}", _EXAMPLE_NAME, snake).replace("**/", "").replace("*", _EXAMPLE_NAME.replace("-", "_"))


class RuleExamples:
    """One practice's checked graph rules against the example pairs its ``rules/rule_examples.py`` holds
    (``EXAMPLE_PAIRS``: each rule's slug with what proves the rule flags its failing example and passes its repaired
    one)."""

    def __init__(self, practice_key: str) -> None:
        package = f"cdd_guidance.practices.{practice_key}.rules"
        self._rules: dict[str, object] = dict(importlib.import_module(package).BY_SLUG)
        self._pairs: dict[str, Callable[[], None]] = dict(getattr(importlib.import_module(f"{package}.rule_examples"), "EXAMPLE_PAIRS"))

    def without_a_pair(self) -> list[str]:
        """The checked rules that have no failing and repaired example."""
        return sorted(slug for slug in self._rules if slug not in self._pairs)

    def failing_pairs(self) -> list[str]:
        """Each pair that does not hold, with why: the rule passed its failing example, or flagged its repaired one."""
        failed = []
        for slug, proves in sorted(self._pairs.items()):
            try:
                proves()
            except AssertionError as failure:
                failed.append(f"{slug}: {failure}")
        return failed
