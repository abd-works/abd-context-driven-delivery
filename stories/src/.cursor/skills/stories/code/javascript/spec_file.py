"""JavaScript spec-file renderer.

Mirrors the TS renderer but omits the `import type` line and drops the
`as const satisfies Story` suffix — JS has no static types, so scenarios are
plain objects and the runner validates step-key coverage at runtime.

    /**
     * @type {import('../story-types').Story}
     */
    export const SubmitOrder = {
      story:       'Submit Order',
      actor:       'Customer',
      domainTerms: [...],
      evidence:    [...],

      scenarioKey: {
        name: '...',
        given: [...],
        interactions: [{ when: [...], then: [...] }],
      },
    }
"""

from __future__ import annotations

import re
from typing import Iterable, List

from stories.src.stories.model.nodes import Story


def render_story_spec_file(story: Story, *, relative_types_path: str = "../story-types") -> str:
    constant = _pascal(story.name)
    actor = (story.users[0] if story.users else "").strip()

    lines: List[str] = []
    lines.append("/**")
    lines.append(f" * @type {{import('{relative_types_path}').Story}}")
    lines.append(" */")
    lines.append(f"export const {constant} = {{")
    lines.append(f"  story:       {_js_string(story.name)},")
    lines.append(f"  actor:       {_js_string(actor)},")
    lines.append(f"  domainTerms: {_js_string_array(story.domain_terms)},")
    lines.append(f"  evidence:    {_js_string_array(story.evidence)},")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if scenarios:
        lines.append("")
        for scenario in scenarios:
            lines.extend(_render_scenario_block(scenario))
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_scenario_block(scenario) -> List[str]:
    key = _camel(scenario.name)
    lines: List[str] = []
    lines.append(f"  {key}: {{")
    lines.append(f"    name: {_js_string(scenario.name)},")
    lines.append(f"    given: [")
    for clause in scenario.given:
        lines.append(f"      {_js_string(clause.text)},")
    lines.append(f"    ],")
    lines.append(f"    interactions: [")
    for interaction in scenario.interactions:
        lines.append("      {")
        lines.append("        when: [")
        for clause in interaction.when:
            lines.append(f"          {_js_string(clause.text)},")
        lines.append("        ],")
        lines.append("        then: [")
        for clause in interaction.then:
            lines.append(f"          {_js_string(clause.text)},")
        lines.append("        ],")
        lines.append("      },")
    lines.append("    ],")
    lines.append("  },")
    return lines


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _js_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _js_string_array(values: Iterable[str]) -> str:
    items = list(values or [])
    if not items:
        return "[]"
    joined = ", ".join(_js_string(v) for v in items)
    return f"[{joined}]"


def _pascal(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "".join(w[:1].upper() + w[1:] for w in parts) or "Story"


def _camel(name: str) -> str:
    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    if not words:
        return "scenario"
    head = words[0][:1].lower() + words[0][1:]
    tail = "".join(w[:1].upper() + w[1:] for w in words[1:])
    return head + tail
