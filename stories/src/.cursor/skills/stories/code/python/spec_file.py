"""Python spec-file renderer — mirrors the TypeScript reference shape.

Renders one `<story_slug>_stories.py` file per Story:

    from typing import Final

    <STORY_CONSTANT>: Final = {
        "story":        "<Story Name>",
        "actor":        "<Actor Name>",
        "domain_terms": (...),
        "evidence":     (...),

        "<scenario_key>": {
            "name":         "<scenario name>",
            "given":        ("clause 1", "And clause 2"),
            "interactions": (
                {
                    "when": (...),
                    "then": (...),
                },
            ),
        },
    }

Naming convention (per the skill's Python rules):
- Folder names stay kebab-case (`place-new-order/submit-order/`).
- File names are snake_case (`submit_order_stories.py`) because they must be
  importable as modules by tier files and pytest.
- Story constant is SCREAMING_SNAKE from the story name.
- Scenario keys are snake_case from the scenario name.
"""

from __future__ import annotations

import re
from typing import Iterable, List

from stories.src.stories.model.nodes import Story


def render_story_spec_file(story: Story) -> str:
    """Render one Story to a Python spec-file body."""
    constant = _screaming_snake(story.name)
    actor = (story.users[0] if story.users else "").strip()

    lines: List[str] = []
    lines.append('"""Story data — regeneratable. Do not add logic or imports."""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from typing import Final")
    lines.append("")
    lines.append("")
    lines.append(f"{constant}: Final = {{")
    lines.append(f"    \"story\":        {_py_string(story.name)},")
    lines.append(f"    \"actor\":        {_py_string(actor)},")
    lines.append(f"    \"domain_terms\": {_py_string_tuple(story.domain_terms)},")
    lines.append(f"    \"evidence\":     {_py_string_tuple(story.evidence)},")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if scenarios:
        lines.append("")
        for scenario in scenarios:
            lines.extend(_render_scenario_block(scenario))
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_scenario_block(scenario) -> List[str]:
    key = _snake(scenario.name)
    lines: List[str] = []
    lines.append(f"    \"{key}\": {{")
    lines.append(f"        \"name\":         {_py_string(scenario.name)},")
    lines.append(f"        \"given\": (")
    for clause in scenario.given:
        lines.append(f"            {_py_string(clause.text)},")
    lines.append(f"        ),")
    lines.append(f"        \"interactions\": (")
    for interaction in scenario.interactions:
        lines.append("            {")
        lines.append("                \"when\": (")
        for clause in interaction.when:
            lines.append(f"                    {_py_string(clause.text)},")
        lines.append("                ),")
        lines.append("                \"then\": (")
        for clause in interaction.then:
            lines.append(f"                    {_py_string(clause.text)},")
        lines.append("                ),")
        lines.append("            },")
    lines.append("        ),")
    lines.append("    },")
    return lines


_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_BACKTICK = re.compile(r"`([^`]+)`")


def _strip_md_emphasis(value: str) -> str:
    return _BACKTICK.sub(r"\1", _ITALIC.sub(r"\1", _BOLD.sub(r"\1", value)))


def _py_string(value: str) -> str:
    cleaned = _strip_md_emphasis(value)
    escaped = cleaned.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _py_string_tuple(values: Iterable[str]) -> str:
    items = list(values or [])
    if not items:
        return "()"
    if len(items) == 1:
        return f"({_py_string(items[0])},)"
    joined = ", ".join(_py_string(v) for v in items)
    return f"({joined})"


def _screaming_snake(name: str) -> str:
    return _snake(name).upper() or "STORY"


def _snake(name: str) -> str:
    parts = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    return "_".join(p.lower() for p in parts) or "scenario"
