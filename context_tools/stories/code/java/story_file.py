"""Java runnable story-file renderer — GWT stubs for AI to fill."""

from __future__ import annotations

import re
from typing import List

from context_tools.stories.code.code_story_map import to_pascal
from context_tools.stories.story_model.nodes import Story


def render_story_file(story: Story, *, helper_class: str | None = None) -> str:
    class_name = f"{to_pascal(story.name)}Story"
    actor = (story.users[0] if story.users else "").strip()
    lines: List[str] = [
        f"/** Story: {story.name} (tier-neutral).",
    ]
    if actor:
        lines.append(f" * Actor: {actor}")
    lines.extend(
        [
            " * Wired to ExampleFactory fakes. Assert public I{Type} only.",
            f" * Specs: {class_name}Spec (isolated); {class_name}Spec{{Tier}} (other tiers)",
            " */",
            f"public class {class_name} {{",
            f'  public static void create(String mode) {{',
            f'    // mode: fake | isolated | production',
        ]
    )
    for scenario in getattr(story, "scenarios", []) or []:
        slug = _camel(scenario.name)
        lines.append(f'    // SCENARIO: {scenario.name}')
        lines.append(f"    {slug}(mode);")
    lines.append("  }")
    lines.append("")
    for scenario in getattr(story, "scenarios", []) or []:
        slug = _camel(scenario.name)
        lines.append(f"  static void {slug}(String mode) {{")
        for clause in scenario.given:
            lines.append(f'    // GIVEN: {clause.text}')
        for interaction in scenario.interactions:
            for clause in interaction.when:
                lines.append(f'    // WHEN: {clause.text}')
            for clause in interaction.then:
                lines.append(f'    // THEN: {clause.text}')
        lines.append("    // AI fills: helper → ExampleFactory; assert public interface")
        lines.append("  }")
        lines.append("")
    lines.append("  public static void main(String[] args) {")
    lines.append('    create("fake");')
    lines.append("  }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_tier_spec_file(story: Story, *, tier: str) -> str:
    class_name = f"{to_pascal(story.name)}Story"
    spec = (
        f"{class_name}Spec"
        if tier == "isolated"
        else f"{class_name}Spec{to_pascal(tier)}"
    )
    return "\n".join(
        [
            f"/** Tier: {tier} — same {story.name} story. */",
            f"public class {spec} {{",
            "  @org.junit.jupiter.api.Test",
            "  void runStory() {",
            f'    {class_name}.create("{tier}");',
            "  }",
            "}",
            "",
        ]
    )


def _camel(name: str) -> str:
    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    if not words:
        return "scenario"
    return words[0][:1].lower() + words[0][1:] + "".join(
        w[:1].upper() + w[1:] for w in words[1:]
    )
