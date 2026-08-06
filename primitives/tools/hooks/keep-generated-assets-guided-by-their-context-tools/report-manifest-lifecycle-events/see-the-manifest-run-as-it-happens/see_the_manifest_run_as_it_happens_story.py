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
#                  report-manifest-lifecycle-events/
#                  see-the-manifest-run-as-it-happens/
#   Story file  -> see_the_manifest_run_as_it_happens_story.py
#   Tier files  -> see_the_manifest_run_as_it_happens_test_helper.{tier}.py
#                  (tier: domain - no client/server/e2e tier applies)
#
# Source: primitives/tools/hooks/.context/manifest-gate-stories-sketch.md
#   Sub-Epic: Report Manifest Lifecycle Events
#   Story:    See The Manifest Run As It Happens

"""Story: See The Manifest Run As It Happens (scenario fidelity - tier-neutral)."""

from __future__ import annotations

from typing import Protocol


class SeeTheManifestRunAsItHappensHelper(Protocol):
    def given_normal_mode_active(self) -> None: ...
    def when_manifest_runs_via_hook(self) -> None: ...
    def then_one_message_confirms_the_run(self) -> None: ...
    def when_manifest_runs_via_direct_cli_call(self) -> None: ...
    def then_cli_confirmation_still_appears(self) -> None: ...
    def given_verbose_mode_active(self) -> None: ...
    def when_governed_asset_touched(self) -> None: ...
    def then_hook_firing_reported(self) -> None: ...
    def then_manifest_executing_reported(self) -> None: ...
    def then_manifest_loaded_reported(self) -> None: ...


def create_see_the_manifest_run_as_it_happens_story(
    h: "SeeTheManifestRunAsItHappensHelper",
) -> dict:
    """Build one pytest test function per scenario. Returns {test_name: fn}
    for the tier file to bind at module scope.
    """
    tests = {}

    def test_normal_mode_confirms_hook_triggered_run() -> None:
        """SCENARIO: normal mode confirms a hook-triggered manifest run"""
        h.given_normal_mode_active()
        h.when_manifest_runs_via_hook()
        h.then_one_message_confirms_the_run()

    def test_normal_mode_confirms_direct_cli_run() -> None:
        """SCENARIO: normal mode confirms a direct CLI-triggered manifest run too"""
        h.given_normal_mode_active()
        h.when_manifest_runs_via_direct_cli_call()
        h.then_cli_confirmation_still_appears()

    def test_verbose_mode_reports_hook_firing() -> None:
        """SCENARIO: verbose mode narrates each step of a hook-triggered manifest run (hook fired)"""
        h.given_verbose_mode_active()
        h.when_governed_asset_touched()
        h.then_hook_firing_reported()

    def test_verbose_mode_reports_manifest_executing() -> None:
        """SCENARIO: verbose mode narrates each step of a hook-triggered manifest run (executing)"""
        h.given_verbose_mode_active()
        h.when_governed_asset_touched()
        h.then_manifest_executing_reported()

    def test_verbose_mode_reports_manifest_loaded() -> None:
        """SCENARIO: verbose mode narrates each step of a hook-triggered manifest run (loaded)"""
        h.given_verbose_mode_active()
        h.when_governed_asset_touched()
        h.then_manifest_loaded_reported()

    tests["test_normal_mode_confirms_hook_triggered_run"] = test_normal_mode_confirms_hook_triggered_run
    tests["test_normal_mode_confirms_direct_cli_run"] = test_normal_mode_confirms_direct_cli_run
    tests["test_verbose_mode_reports_hook_firing"] = test_verbose_mode_reports_hook_firing
    tests["test_verbose_mode_reports_manifest_executing"] = test_verbose_mode_reports_manifest_executing
    tests["test_verbose_mode_reports_manifest_loaded"] = test_verbose_mode_reports_manifest_loaded
    return tests
