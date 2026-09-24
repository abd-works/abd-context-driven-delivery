"""Shared helper-interface seam for the story / test_helper file pair.

Every language backend's `{story}_story.test.<ext>` file declares one interface/protocol method per
distinct Given/When/Then clause across a Story's scenarios, and calls those
methods instead of inlining assertions. Do not emit a front-end / back-end / e2e
file per story.

This module derives the one deterministic method name every backend agrees on
from clause phase + text, so the interface declared in the story file, the
call sites inside it, and every tier implementation stay in lock-step. Names
are mechanical (every word in the clause, PascalCased) - a scaffold starting
point. The AI/human path is expected to shorten these to a concise paraphrase
(as already done by hand in story-ui's helper interfaces) while keeping the
interface declaration, the story wiring, and every tier implementation
renamed together.
"""

from __future__ import annotations

import re
from typing import Callable, Dict, List, Tuple

MethodLookup = Callable[[str, str], "HelperMethod"]

_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")
_CONTINUATION = re.compile(r"^(And|But)\s+", re.IGNORECASE)


class HelperMethod:
    def __init__(self, name: str, phase: str, display_text: str) -> None:
        self.name = name
        self.phase = phase
        self.display_text = display_text
        self._seen: Dict[Tuple[str, str], HelperMethod] = {}
        self._ordered: List[HelperMethod] = []

    def strip_md_emphasis(self, value: str) -> str:
        """Strip markdown bold/italic/backtick markers, keeping the inner text."""
        return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))

    def display_clause_text(self, text: str) -> str:
        """Text for a given()/when()/then() call - strips the And/But continuation
        marker (the call site is already scoped to its phase) and markdown."""
        return self.strip_md_emphasis(_CONTINUATION.sub("", text)).strip()

    def clause_method_name(self, phase: str, text: str) -> str:
        """Mechanical method name: phase + PascalCase(every word in the clause)."""
        cleaned = self.display_clause_text(text)
        words = [w for w in re.split(r"[^0-9A-Za-z]+", cleaned) if w]
        tail = "".join(w[:1].upper() + w[1:].lower() for w in words)
        return f"{phase}{tail}" if tail else phase

    def seam_for_story(self, story) -> Tuple[List["HelperMethod"], MethodLookup]:
        """One HelperMethod per distinct clause across every scenario on `story`."""
        self._seen = {}
        self._ordered = []
        for scenario in getattr(story, "scenarios", None) or []:
            for clause in scenario.given:
                self._add("given", clause.text)
            for interaction in scenario.interactions:
                for clause in interaction.when:
                    self._add("when", clause.text)
                for clause in interaction.then:
                    self._add("then", clause.text)

        def method_for(phase: str, text: str) -> HelperMethod:
            key = (phase, self.display_clause_text(text).lower())
            return self._seen[key]

        return self._ordered, method_for

    def _add(self, phase: str, text: str) -> None:
        display = self.display_clause_text(text)
        key = (phase, display.lower())
        if key in self._seen:
            return
        method = HelperMethod(
            name=self.clause_method_name(phase, text),
            phase=phase,
            display_text=display,
        )
        self._seen[key] = method
        self._ordered.append(method)


    @classmethod
    def from_story(cls, story) -> Tuple[List["HelperMethod"], MethodLookup]:
        return cls("", "", "").seam_for_story(story)
