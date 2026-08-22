"""Python runnable story-file renderer (scenario fidelity - no tier suffix).

Declares a `typing.Protocol` with one method per distinct Given/When/Then
clause, and a `create_{story}_story(h)` factory that builds one pytest test
function per scenario, each calling only `h.<method>()` - no assertions, no
tier mechanism here:

    class SubmitOrderHelper(Protocol):
        def given_a_cart_with_items(self) -> None: ...
        def when_the_customer_submits_the_order(self) -> None: ...
        def then_the_order_is_confirmed(self) -> None: ...

    def create_submit_order_story(h: "SubmitOrderHelper") -> dict:
        def test_main_flow() -> None:
            h.given_a_cart_with_items()
            h.when_the_customer_submits_the_order()
            h.then_the_order_is_confirmed()
        return {"test_main_flow": test_main_flow}

Every tier's `{story}_test_helper.{tier}.py` implements the Protocol and binds
`create_submit_order_story(TierHelper())` at module scope so pytest discovers
the returned test functions.
"""

from __future__ import annotations

from typing import List

from context_tools.stories.code.code_story_map import to_pascal, to_snake
from context_tools.stories.code.helper_interface import build_helper_seam
from context_tools.stories.story_model.nodes import Story


def render_story_file(story: Story) -> str:
    fn = f"create_{to_snake(story.name)}_story"
    helper_iface = f"{to_pascal(story.name)}Helper"
    actor = (story.users[0] if story.users else "").strip()
    methods, method_for = build_helper_seam(story)

    lines: List[str] = []
    lines.append('"""')
    lines.append(f"Story: {story.name} (scenario fidelity - tier-neutral).")
    if actor:
        lines.append(f"Actor: {actor}")
    lines.append("Calls helper-protocol methods only - no assertions, no tier mechanism here.")
    lines.append(
        f"Tiers: {to_snake(story.name)}_test_helper.{{tier}}.py implements {helper_iface}."
    )
    lines.append('"""')
    lines.append("")
    lines.append("from __future__ import annotations")
    lines.append("")
    lines.append("from typing import Protocol")
    lines.append("")
    lines.append("")
    lines.append(f"class {helper_iface}(Protocol):")
    if methods:
        for method in methods:
            lines.append(f"    def {method.name}(self) -> None: ...")
    else:
        lines.append("    ...")
    lines.append("")
    lines.append("")
    lines.append(f'def {fn}(h: "{helper_iface}") -> dict:')
    lines.append(
        '    """Build one pytest test function per scenario. Returns {test_name: fn}'
        " for the tier file to bind at module scope."
    )
    lines.append('    """')
    lines.append("    tests = {}")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if not scenarios:
        lines.append("    # TODO: add main-flow scenario")
    for scenario in scenarios:
        lines.extend(_render_scenario(scenario, method_for))

    lines.append("    return tests")
    lines.append("")
    return "\n".join(lines)


def render_test_helper_file(story: Story, *, tier: str) -> str:
    """Write-once skeleton for `{story}_test_helper.{tier}.py`.

    Scaffolds a class with `NotImplementedError` stub methods (code path) and
    binds the story's generated tests at module scope so pytest discovers
    them. The AI/human path fills each stub with that tier's real mechanism.
    """
    fn = f"create_{to_snake(story.name)}_story"
    module = to_snake(story.name) + "_story"
    tier_class = f"{to_pascal(tier)}Helper"
    methods, _ = build_helper_seam(story)

    lines: List[str] = [
        '"""',
        f"Tier: {tier} - implements {to_pascal(story.name)}Helper for {story.name}.",
        '"""',
        "",
        "from __future__ import annotations", 
        "",
        f"from {module} import {fn}",
        "",
        "",
        f"class {tier_class}:",
    ]
    for method in methods:
        lines.append(f"    def {method.name}(self) -> None:")
        lines.append(f'        raise NotImplementedError("not implemented: {method.name}")')
        lines.append("")
    if not methods:
        lines.append("    pass")
        lines.append("")
    lines.append("")
    lines.append(f"globals().update({fn}({tier_class}()))")
    lines.append("")
    return "\n".join(lines)


def _render_scenario(scenario, method_for) -> List[str]:
    slug = to_snake(scenario.name)
    test_name = f"test_{slug}"
    lines: List[str] = [f"    def {test_name}() -> None:"]
    lines.append(f'        """SCENARIO: {scenario.name}"""')
    for clause in scenario.given:
        method = method_for("given", clause.text)
        lines.append(f"        h.{method.name}()  # GIVEN: {method.display_text}")
    for interaction in scenario.interactions:
        for clause in interaction.when:
            method = method_for("when", clause.text)
            lines.append(f"        h.{method.name}()  # WHEN: {method.display_text}")
        for clause in interaction.then:
            method = method_for("then", clause.text)
            lines.append(f"        h.{method.name}()  # THEN: {method.display_text}")
    lines.append(f"    tests[{test_name!r}] = {test_name}")
    lines.append("")
    return lines
