"""TypeScript runnable story-file renderer — mirrors JavaScript GWT stubs."""

from __future__ import annotations

import re
from typing import List

from context_tools.stories.code.code_story_map import to_pascal
from context_tools.stories.story_model.nodes import Story


def render_story_file(
    story: Story,
    *,
    relative_story_test_path: str = "../../story-test",
    relative_helper_path: str | None = None,
    helper_class: str | None = None,
) -> str:
    fn = f"create{to_pascal(story.name)}Story"
    actor = (story.users[0] if story.users else "").strip()
    lines: List[str] = [
        "/**",
        f" * Story: {story.name} (tier-neutral).",
    ]
    if actor:
        lines.append(f" * Actor: {actor}")
    lines.extend(
        [
            " * Wired to ExampleFactory fakes — not a tier test.",
            " * Assert the public interface of I{Type} only.",
            f" * Specs: {_snake(story.name)}_spec.ts (isolated); "
            f"{_snake(story.name)}_spec.{{tier}}.ts (other tiers)",
            " */",
            "",
            f'import {{ scenario, story }} from "{relative_story_test_path}";',
        ]
    )
    if relative_helper_path and helper_class:
        lines.append(f'import {{ {helper_class} }} from "{relative_helper_path}";')
        lines.append("")
        lines.append(f"const helper = new {helper_class}();")
    lines.append("")
    lines.append(f"export function {fn}(mode: string): void {{")
    lines.append(f"  story({_qs(story.name)}, () => {{")
    for scenario in getattr(story, "scenarios", []) or []:
        lines.extend(_render_scenario(scenario))
    lines.append("  });")
    lines.append("}")
    lines.append("")
    lines.append(f'// Entry: fake when this file is the test entry')
    lines.append(f'{fn}("fake");')
    lines.append("")
    return "\n".join(lines)


def render_tier_spec_file(story: Story, *, tier: str) -> str:
    fn = f"create{to_pascal(story.name)}Story"
    return "\n".join(
        [
            "/**",
            f" * Tier: {tier} — same {story.name} story.",
            " */",
            "",
            f'import {{ {fn} }} from "./{_snake(story.name)}_story";',
            "",
            f'describe("tier: {tier}", () => {{',
            f'  {fn}("{tier}");',
            "});",
            "",
        ]
    )


def _render_scenario(scenario) -> List[str]:
    lines = [f"    scenario({_qs(scenario.name)}, ({{ given, when, then }}) => {{"]
    for clause in scenario.given:
        lines.append(f"      given({_qs(clause.text)}, () => {{")
        lines.append("        // helper.given…({ mode }) — AI fills")
        lines.append("      });")
    for interaction in scenario.interactions:
        for clause in interaction.when:
            lines.append(f"      when({_qs(clause.text)}, () => {{")
            lines.append("        // public operations — AI fills")
            lines.append("      });")
        for clause in interaction.then:
            lines.append(f"      then({_qs(clause.text)}, () => {{")
            lines.append("        // assert public interface — AI fills")
            lines.append("      });")
    lines.append("    });")
    lines.append("")
    return lines


def _qs(value: str) -> str:
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    return "'" + cleaned.replace("\\", "\\\\").replace("'", "\\'") + "'"


def _snake(name: str) -> str:
    return re.sub(r"[^0-9a-z]+", "_", name.strip().lower()).strip("_") or "story"
