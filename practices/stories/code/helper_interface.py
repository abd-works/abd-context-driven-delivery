"""Shared helper-interface seam for the story / test_helper file pair.

Every language backend's `{story}_story.<ext>` file (scenario fidelity, no tier
suffix - GWT + step text only) declares one interface/protocol method per
distinct Given/When/Then clause across a Story's scenarios, and calls those
methods instead of inlining assertions. Every tier's
`{story}_test_helper.{tier}.<ext>` file (acceptance_tests fidelity) implements
that interface with the tier's real mechanism (domain class call, Supertest
route, Testing Library render, Playwright page, ...).

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
from typing import Callable, Dict, List, NamedTuple, Tuple

_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")
_CONTINUATION = re.compile(r"^(And|But)\s+", re.IGNORECASE)


def strip_md_emphasis(value: str) -> str:
    """Strip markdown bold/italic/backtick markers, keeping the inner text."""
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def display_clause_text(text: str) -> str:
    """Text for a given()/when()/then() call - strips the And/But continuation
    marker (the call site is already scoped to its phase) and markdown."""
    return strip_md_emphasis(_CONTINUATION.sub("", text)).strip()


class HelperMethod(NamedTuple):
    name: str
    phase: str  # "given" | "when" | "then"
    display_text: str  # cleaned step text for the given/when/then() call


def clause_method_name(phase: str, text: str) -> str:
    """Mechanical method name: phase + PascalCase(every word in the clause)."""
    cleaned = display_clause_text(text)
    words = [w for w in re.split(r"[^0-9A-Za-z]+", cleaned) if w]
    tail = "".join(w[:1].upper() + w[1:].lower() for w in words)
    return f"{phase}{tail}" if tail else phase


MethodLookup = Callable[[str, str], HelperMethod]


def build_helper_seam(story) -> Tuple[List[HelperMethod], MethodLookup]:
    """One HelperMethod per distinct clause across every scenario on `story`,
    in first-seen order (scenario by scenario, given -> when -> then).
    Duplicate clause text (same phase + display text, case-insensitive) reuses
    the same method - two scenarios that share a Given both call it.

    Returns `(methods, method_for)`. `methods` is the declaration order for the
    interface. `method_for(phase, text)` resolves the same clause back to its
    HelperMethod at a given/when/then call site.
    """
    seen: Dict[Tuple[str, str], HelperMethod] = {}
    ordered: List[HelperMethod] = []

    for scenario in getattr(story, "scenarios", None) or []:
        for clause in scenario.given:
            _add(seen, ordered, "given", clause.text)
        for interaction in scenario.interactions:
            for clause in interaction.when:
                _add(seen, ordered, "when", clause.text)
            for clause in interaction.then:
                _add(seen, ordered, "then", clause.text)

    def method_for(phase: str, text: str) -> HelperMethod:
        key = (phase, display_clause_text(text).lower())
        return seen[key]

    return ordered, method_for


def _add(
    seen: Dict[Tuple[str, str], HelperMethod],
    ordered: List[HelperMethod],
    phase: str,
    text: str,
) -> None:
    display = display_clause_text(text)
    key = (phase, display.lower())
    if key in seen:
        return
    method = HelperMethod(
        name=clause_method_name(phase, text), phase=phase, display_text=display
    )
    seen[key] = method
    ordered.append(method)
