"""TypeScript spec-file renderer — the reference-architecture shape.

Renders one `<story-slug>-stories.ts` file per Story:

    export const <VerbNounStory> = {
      story:       '<Story Name>',
      actor:       '<Actor Name>',
      domainTerms: [...],
      evidence:    [...],

      <scenarioKey>: {
        name:         '<scenario name>',
        given:        ['clause 1', 'And clause 2'],
        interactions: [{ when: [...], then: [...] }],
      },
      // ... more scenarios
    } as const satisfies Story

Consumes:
  - `Story` (from stories.story_model.nodes) — carries name, users,
    domain_terms, evidence, and (attached by workspace/loader) scenarios.
  - `Scenario` (from stories.story_model.scenario) — phase-grouped.

Emits:
  - str (the file body).

Note on discipline: this file is FULLY regeneratable. It contains no code —
just literal data. Never include user-authored logic here; tier files own
that (write-once).
"""

from __future__ import annotations

import re
from typing import Iterable, List, Optional

from stories.story_model.nodes import Story


TS_TYPES_MODULE = "story-types"


def render_story_spec_file(
    story: Story,
    *,
    relative_types_path: str = "../story-types",
) -> str:
    """Render one Story to a TS spec-file body.

    - `story` carries `name`, `users`, `domain_terms`, `evidence`, `scenarios`.
    - `relative_types_path` is the import path (without extension) to reach the
      shared `story-types` module from the file being rendered.
    """
    constant = _pascal(story.name)
    actor = (story.users[0] if story.users else "").strip()

    lines: List[str] = []
    lines.append(f"import type {{ Story }} from '{relative_types_path}'")
    lines.append("")
    lines.append(f"export const {constant} = {{")
    lines.append(f"  story:       {_ts_string(story.name)},")
    lines.append(f"  actor:       {_ts_string(actor)},")
    lines.append(f"  domainTerms: {_ts_string_array(story.domain_terms)},")
    lines.append(f"  evidence:    {_ts_string_array(story.evidence)},")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if scenarios:
        lines.append("")
        for scenario in scenarios:
            lines.extend(_render_scenario_block(scenario))
    lines.append("} as const satisfies Story")
    lines.append("")
    return "\n".join(lines)


def _render_scenario_block(scenario) -> List[str]:
    key = _camel(scenario.name)
    lines: List[str] = []
    lines.append(f"  {key}: {{")
    lines.append(f"    name: {_ts_string(scenario.name)},")
    lines.append(f"    given: [")
    for clause in scenario.given:
        lines.append(f"      {_ts_string(clause.text)},")
    lines.append(f"    ],")
    lines.append(f"    interactions: [")
    for interaction in scenario.interactions:
        lines.append("      {")
        lines.append("        when: [")
        for clause in interaction.when:
            lines.append(f"          {_ts_string(clause.text)},")
        lines.append("        ],")
        lines.append("        then: [")
        for clause in interaction.then:
            lines.append(f"          {_ts_string(clause.text)},")
        lines.append("        ],")
        lines.append("      },")
    lines.append("    ],")
    lines.append("  },")
    return lines


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    """Strip markdown bold/italic/backtick markers, keeping the inner text.

    Loader stores the verbatim step string with bold/italic markup preserved
    so scanners can extract concepts and values. Rendered spec files must be
    plain prose — the reference architecture uses no markdown inside step
    strings.
    """
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _ts_string(value: str) -> str:
    """Render a Python string as a TS single-quoted string literal.

    Uses single quotes to match the reference architecture; escapes only
    what a single-quoted TS string requires. Markdown emphasis markers
    from the loader are stripped before escaping.
    """
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def _ts_string_array(values: Iterable[str]) -> str:
    items = list(values or [])
    if not items:
        return "[]"
    joined = ", ".join(_ts_string(v) for v in items)
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
