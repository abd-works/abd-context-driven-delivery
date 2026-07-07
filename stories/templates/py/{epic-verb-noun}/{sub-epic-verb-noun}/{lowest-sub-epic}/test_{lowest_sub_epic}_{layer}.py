# ---
# fidelity: [engineering]
# artifact: [tier-file]
# format: py
# section: tier-server
# ---
#
# One tier = one file. Each scenario is its own test method with explicit
# step calls in order — Given, When, Then — so any reader sees exactly what
# runs without knowing how a runner works.
#
# Write-once. If a story adds a new step, add the matching key here.

"""Server-tier tests for {Sub-Epic Name}."""

from __future__ import annotations

from typing import Callable

from {lowest_sub_epic}_stories import STORY_ONE
import {lowest_sub_epic}_helpers as helpers


class {LowestSubEpic}Server:
    """Server-tier step implementations for {Story Name}."""

    def __init__(self) -> None:
        self.given: dict[str, Callable[[], None]] = {
            "<precondition>": lambda: helpers.seed_precondition(),
            "And <continuation precondition>": lambda: helpers.seed_continuation(),
        }
        self.when: dict[str, Callable[[], None]] = {
            "<action>": lambda: helpers.trigger_action(),
        }
        self.then: dict[str, Callable[[], None]] = {
            "<observable outcome>": lambda: helpers.assert_outcome(),
            "And <continuation outcome>": lambda: helpers.assert_continuation(),
        }

    def cleanup(self) -> None:
        helpers.reset_state()


class TestMainFlow:
    def test_run(self) -> None:
        tier = {LowestSubEpic}Server()
        # Given
        tier.given["<precondition>"]()
        tier.given["And <continuation precondition>"]()
        # When
        tier.when["<action>"]()
        # Then
        tier.then["<observable outcome>"]()
        tier.then["And <continuation outcome>"]()
        tier.cleanup()
