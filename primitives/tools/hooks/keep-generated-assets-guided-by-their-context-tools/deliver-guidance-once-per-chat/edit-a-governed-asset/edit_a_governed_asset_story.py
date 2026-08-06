# ---
# fidelity: [exploration, specification]
# artifact: [story-file]
# format: py
# section: leaf-story-file
# ---
#
# Runnable story (scenario fidelity - tier-neutral). Calls helper-protocol
# methods only - no assertions, no tier mechanism here.
#
#   Folder tree -> keep-generated-assets-guided-by-their-context-tools/
#                  deliver-guidance-once-per-chat/
#                  edit-a-governed-asset/
#   Story file  -> edit_a_governed_asset_story.py
#   Tier files  -> edit_a_governed_asset_test_helper.{tier}.py
#                  (tier: agent - all scenarios require a live agent session)
#
# Source: primitives/tools/hooks/.context/manifest-gate-stories-sketch.md
#   Sub-Epic: Deliver Guidance Once Per Chat, Then Reuse It
#   Story:    Edit A Governed Asset

"""Story: Edit A Governed Asset (scenario fidelity - tier-neutral)."""

from __future__ import annotations

from typing import Protocol


class EditAGovernedAssetHelper(Protocol):
    # scenario 1: first touch delivers guidance
    def given_a_governed_asset_not_yet_touched_this_chat(self) -> None: ...
    def when_agent_reads_the_asset(self) -> None: ...
    def then_governing_toolset_guidance_is_delivered(self) -> None: ...

    # scenario 2: edit proceeds directly on the same touch
    def when_agent_edits_the_asset(self) -> None: ...
    def then_edit_proceeds_directly_without_a_compliance_step(self) -> None: ...

    # scenario 3: repeat touch refers back to guidance already in context
    def given_the_same_asset_with_guidance_already_in_context(self) -> None: ...
    def when_agent_touches_the_asset_again(self) -> None: ...
    def then_edit_still_proceeds_directly(self) -> None: ...

    # scenario 4: a governing tool's own source is itself a governed asset
    def given_a_context_tools_own_source_file(self) -> None: ...
    def when_agent_reads_that_context_tools_source(self) -> None: ...
    def then_gate_delivers_that_tools_own_governing_guidance(self) -> None: ...

    # scenario 5: the recursion has no floor - base primitives are governed too
    def given_a_base_primitives_own_source_file(self) -> None: ...
    def when_agent_reads_that_base_primitive(self) -> None: ...
    def then_gate_still_delivers_its_governing_guidance(self) -> None: ...


def create_edit_a_governed_asset_story(h: "EditAGovernedAssetHelper") -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn}
    for the tier file to bind at module scope.
    """
    tests = {}

    def test_first_touch_delivers_governing_toolset_guidance() -> None:
        """SCENARIO: touching a governed asset for the first time delivers its governing tool's guidance"""
        h.given_a_governed_asset_not_yet_touched_this_chat()
        h.when_agent_reads_the_asset()
        h.then_governing_toolset_guidance_is_delivered()

    def test_edit_proceeds_directly_on_first_touch() -> None:
        """SCENARIO: the edit proceeds directly on that same touch"""
        h.given_a_governed_asset_not_yet_touched_this_chat()
        h.when_agent_edits_the_asset()
        h.then_edit_proceeds_directly_without_a_compliance_step()

    def test_repeat_touch_still_allows_direct_edit() -> None:
        """SCENARIO: touching the same asset again this chat just refers back to guidance already delivered"""
        h.given_the_same_asset_with_guidance_already_in_context()
        h.when_agent_touches_the_asset_again()
        h.then_edit_still_proceeds_directly()

    def test_context_tools_own_source_is_a_governed_asset() -> None:
        """SCENARIO: a governing tool's own source is itself a governed asset"""
        h.given_a_context_tools_own_source_file()
        h.when_agent_reads_that_context_tools_source()
        h.then_gate_delivers_that_tools_own_governing_guidance()

    def test_base_primitive_source_is_governed_too() -> None:
        """SCENARIO: the recursion has no floor - base primitives are governed too"""
        h.given_a_base_primitives_own_source_file()
        h.when_agent_reads_that_base_primitive()
        h.then_gate_still_delivers_its_governing_guidance()

    tests["test_first_touch_delivers_governing_toolset_guidance"] = (
        test_first_touch_delivers_governing_toolset_guidance
    )
    tests["test_edit_proceeds_directly_on_first_touch"] = (
        test_edit_proceeds_directly_on_first_touch
    )
    tests["test_repeat_touch_still_allows_direct_edit"] = (
        test_repeat_touch_still_allows_direct_edit
    )
    tests["test_context_tools_own_source_is_a_governed_asset"] = (
        test_context_tools_own_source_is_a_governed_asset
    )
    tests["test_base_primitive_source_is_governed_too"] = (
        test_base_primitive_source_is_governed_too
    )
    return tests
