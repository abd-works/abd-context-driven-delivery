"""Java runnable story-file renderer (scenario fidelity - no tier suffix).

Declares a package-private `{Story}Helper` interface with one method per
distinct Given/When/Then clause, and a public `{Story}Story.create(h)` that
calls only `h.<method>()` per scenario - no assertions, no tier mechanism
here. Java's file-name-matches-public-class-name rule means the tier suffix
cannot use a literal `.{tier}.java` (a dot is not a legal identifier
character), so the Java exception to the `{story}_test_helper.{tier}.<ext>`
convention concatenates the tier PascalCase onto the class name instead:
`{Story}TestHelper{Tier}.java` (mirrors the existing `{Story}Spec{Tier}.java`
tier-suffix convention already used by this backend).

    interface SubmitOrderHelper {
      void givenACartWithItems() throws Exception;
      void whenTheCustomerSubmitsTheOrder() throws Exception;
      void thenTheOrderIsConfirmed() throws Exception;
    }

    public final class SubmitOrderStory {
      private SubmitOrderStory() {}

      public static void create(SubmitOrderHelper h) throws Exception {
        mainFlow(h);
      }

      private static void mainFlow(SubmitOrderHelper h) throws Exception {
        h.givenACartWithItems();
        h.whenTheCustomerSubmitsTheOrder();
        h.thenTheOrderIsConfirmed();
      }
    }

Every tier's `{Story}TestHelper{Tier}.java` implements `SubmitOrderHelper` and
calls `SubmitOrderStory.create(this)` from a `@Test` method.
"""

from __future__ import annotations

from typing import List

from context_tools.stories.code.code_story_map import to_pascal
from context_tools.stories.code.helper_interface import build_helper_seam
from context_tools.stories.story_model.nodes import Story


def render_story_file(story: Story) -> str:
    class_name = f"{to_pascal(story.name)}Story"
    helper_iface = f"{to_pascal(story.name)}Helper"
    actor = (story.users[0] if story.users else "").strip()
    methods, method_for = build_helper_seam(story)

    lines: List[str] = [f"/** Story: {story.name} (scenario fidelity - tier-neutral)."]
    if actor:
        lines.append(f" * Actor: {actor}")
    lines.append(
        " * Calls helper-interface methods only - no assertions, no tier mechanism here."
    )
    lines.append(
        f" * Tiers: {class_name}TestHelper{{Tier}}.java implements {helper_iface}."
    )
    lines.append(" */")
    lines.append(f"interface {helper_iface} {{")
    for method in methods:
        lines.append(f"  void {method.name}() throws Exception;")
    lines.append("}")
    lines.append("")
    lines.append(f"public final class {class_name} {{")
    lines.append(f"  private {class_name}() {{}}")
    lines.append("")
    lines.append(f"  public static void create({helper_iface} h) throws Exception {{")

    scenarios = list(getattr(story, "scenarios", []) or [])
    if not scenarios:
        lines.append("    // TODO: add main-flow scenario")
    for scenario in scenarios:
        lines.append(f"    {_camel(scenario.name)}(h);")
    lines.append("  }")

    for scenario in scenarios:
        lines.append("")
        lines.append(
            f"  private static void {_camel(scenario.name)}({helper_iface} h) throws Exception {{"
        )
        lines.append(f"    // SCENARIO: {scenario.name}")
        for clause in scenario.given:
            method = method_for("given", clause.text)
            lines.append(f"    h.{method.name}();  // GIVEN: {method.display_text}")
        for interaction in scenario.interactions:
            for clause in interaction.when:
                method = method_for("when", clause.text)
                lines.append(f"    h.{method.name}();  // WHEN: {method.display_text}")
            for clause in interaction.then:
                method = method_for("then", clause.text)
                lines.append(f"    h.{method.name}();  // THEN: {method.display_text}")
        lines.append("  }")

    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def render_test_helper_file(story: Story, *, tier: str) -> str:
    """Write-once skeleton for `{Story}TestHelper{Tier}.java`.

    Scaffolds a class implementing the story's helper interface with
    `UnsupportedOperationException` stub bodies (code path). The AI/human path
    fills each stub with that tier's real mechanism.
    """
    story_class = f"{to_pascal(story.name)}Story"
    helper_iface = f"{to_pascal(story.name)}Helper"
    tier_class = f"{story_class}TestHelper{to_pascal(tier)}"
    methods, _ = build_helper_seam(story)

    lines: List[str] = [
        f"/** Tier: {tier} - implements {helper_iface} for {story.name}. */",
        f"public class {tier_class} implements {helper_iface} {{",
    ]
    for method in methods:
        lines.append(f"  @Override public void {method.name}() throws Exception {{")
        lines.append(
            f'    throw new UnsupportedOperationException("not implemented: {method.name}");'
        )
        lines.append("  }")
        lines.append("")
    lines.append("  @org.junit.jupiter.api.Test")
    lines.append("  void runStory() throws Exception {")
    lines.append(f"    {story_class}.create(this);")
    lines.append("  }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _camel(name: str) -> str:
    import re

    words = [w for w in re.split(r"[^0-9A-Za-z]+", name) if w]
    if not words:
        return "scenario"
    head = words[0][:1].lower() + words[0][1:]
    tail = "".join(w[:1].upper() + w[1:] for w in words[1:])
    return head + tail
