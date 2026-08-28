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
#                  treat-a-missing-manifest-as-exceptional/
#                  recover-from-a-manifest-that-wont-load/
#   Story file  -> recover_from_a_manifest_that_wont_load_story.py
#   Tier files  -> recover_from_a_manifest_that_wont_load_test_helper.{tier}.py
#                  (tier: domain - no client/server/e2e tier applies; the
#                  manifest gate is a local hook script, not a networked
#                  service)
#
# Source: primitives/tools/hooks/.context/manifest-gate-stories-sketch.md
#   Sub-Epic: Treat A Missing Manifest As Exceptional
#   Story:    Recover From A Manifest That Won't Load

"""Story: Recover From A Manifest That Won't Load (scenario fidelity - tier-neutral)."""

from __future__ import annotations

from typing import Protocol


class RecoverFromAManifestThatWontLoadHelper(Protocol):
    def given_manifest_errors_on_first_run(self) -> None: ...
    def when_gate_retries_up_to_two_times(self) -> None: ...
    def then_manifest_succeeds_within_retries(self) -> None: ...
    def given_manifest_still_fails_after_two_retries(self) -> None: ...
    def when_gate_gives_up_retrying(self) -> None: ...
    def then_gate_raises_all_caps_failure_notification(self) -> None: ...


def create_recover_from_a_manifest_that_wont_load_story(
    h: "RecoverFromAManifestThatWontLoadHelper",
) -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn}
    for the tier file to bind at module scope.
    """
    tests = {}

    def test_manifest_succeeds_on_retry() -> None:
        """SCENARIO: a correctly configured manifest succeeds on retry"""
        h.given_manifest_errors_on_first_run()
        h.when_gate_retries_up_to_two_times()
        h.then_manifest_succeeds_within_retries()

    def test_every_retry_failing_raises_notification() -> None:
        """SCENARIO: every retry failing raises one unmistakable failure notification"""
        h.given_manifest_still_fails_after_two_retries()
        h.when_gate_gives_up_retrying()
        h.then_gate_raises_all_caps_failure_notification()

    tests["test_manifest_succeeds_on_retry"] = test_manifest_succeeds_on_retry
    tests["test_every_retry_failing_raises_notification"] = (
        test_every_retry_failing_raises_notification
    )
    return tests
