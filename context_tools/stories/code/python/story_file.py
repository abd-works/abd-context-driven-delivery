"""Python runnable story-file renderer (explore / specification).

Emits a mode-parameterized story function with GWT stubs for AI to fill:

    def create_submit_order_story(mode: str = "fake") -> None:
        def test_main_flow() -> None:
            # given / when / then stubs → helper → ExampleFactory
            ...
        # register tests...

    if __name__ == "__main__" or collected as entry:
        create_submit_order_story("fake")
"""

from __future__ import annotations

import re
from typing import List

from context_tools.stories.code.code_story_map import to_pascal, to_snake
from context_tools.stories.story_model.nodes import Story


def render_story_file(
    story: Story,
    *,
    relative_helper_module: str | None = None,
    helper_class: str | None = None,
) -> str:
    fn = f"create_{to_snake(story.name)}_story"
    actor = (story.users[0] if story.users else "").strip()
    domain = list(getattr(story, "domain_terms", None) or [])
    evidence = list(getattr(story, "evidence", None) or [])

    lines: List[str] = []
    lines.append('"""')
    lines.append(f"Story: {story.name} (tier-neutral).")
    if actor:
        lines.append(f"Actor: {actor}")
    if domain:
        lines.append(f"Domain terms: {', '.join(domain)}")
    if evidence:
        lines.append(f"Evidence: {', '.join(evidence)}")
    lines.append("Wired to ExampleFactory fakes — not a tier test.")
    lines.append("Assert the public interface of I{Type} only.")
    lines.append(
        f"Specs: {to_snake(story.name)}_spec.py (isolated); "
        f"{to_snake(story.name)}_spec.{{tier}}.py (other tiers)"
    )
    lines.append('"""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    if relative_helper_module and helper_class:
        lines.append(f"from {relative_helper_module} import {helper_class}")
        lines.append("")
        lines.append(f"helper = {helper_class}()")
        lines.append("")
    lines.append(f"def {fn}(mode: str = \"fake\") -> None:")
    lines.append(
        '    """Register scenarios. Story entry uses fake; tier specs pass isolated|production."""'
    )
    lines.append("")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if not scenarios:
        lines.append("    # TODO: add main-flow scenario")
        lines.append("    pass")
    for scenario in scenarios:
        lines.extend(_render_scenario(scenario, indent="    "))

    lines.append("")
    lines.append("# Story path — fake when this module is the pytest/entry module")
    lines.append(f'{fn}("fake")')
    lines.append("")
    return "\n".join(lines)


def render_tier_spec_file(story: Story, *, tier: str) -> str:
    fn = f"create_{to_snake(story.name)}_story"
    module = f"{to_snake(story.name)}_story"
    lines = [
        '"""',
        f"Tier: {tier} — same {story.name} story.",
        "ExampleFactory builds types with injected deps (isolated) or real collaborators.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        f"from {module} import {fn}",
        "",
        f'{fn}("{tier}")',
        "",
    ]
    return "\n".join(lines)


def _render_scenario(scenario, *, indent: str) -> List[str]:
    slug = to_snake(scenario.name)
    lines: List[str] = []
    lines.append(f"{indent}def test_{slug}() -> None:")
    lines.append(f'{indent}    """')
    lines.append(f"{indent}    SCENARIO: {scenario.name}")
    for clause in scenario.given:
        lines.append(f"{indent}    GIVEN: {clause.text}")
    for interaction in scenario.interactions:
        for clause in interaction.when:
            lines.append(f"{indent}    WHEN: {clause.text}")
        for clause in interaction.then:
            lines.append(f"{indent}    THEN: {clause.text}")
    example_rows = list(getattr(scenario, "example_rows", None) or [])
    if example_rows:
        lines.append(f"{indent}    EXAMPLES: see ExampleFactory / markdown examples table")
    lines.append(f'{indent}    """')
    lines.append(f"{indent}    # given — helper.given_…(mode=mode) → fake I{{Type}}")
    lines.append(f"{indent}    # when — exercise public operations")
    lines.append(f"{indent}    # then — assert public interface only (AI fills)")
    lines.append(f"{indent}    assert True  # replace with public-seam assertion")
    lines.append("")
    return lines
