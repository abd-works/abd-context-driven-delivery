from __future__ import annotations

from expects import equal, expect

from space.kanban.changed_artifact_examples import (
    ONE_SUB_EPIC_MAP,
    PLACE_ORDER_MAP,
    README,
    STORY_MAP,
    chat_bar_counts,
    checkout_flow_of,
    edit,
    reports_written,
    seed_checkout_flow,
)
from story_test import and_, given, scenario, story, then, when

# Epic: Connect Sessions Across Channels And Apps
# Sub-epic: Check Work In Generate
# Map: ../../../.context/story-map.md#e-check-work-in-generate
# Scenarios: check_work_in_generate_story.test.md#story-check-graph-rules-when-an-artifact-changes
# The chat bar's own part, calling session.check_changed_artifact after an edit that went through and reading the board
# again, is tested through the mounted pane in harness/chat-ui/pane/hooks/chat-bar/changed-artifact.test.ts.

# Story: Check Graph Rules When An Artifact Changes
# Actor: Claude Code
with story("Check Graph Rules When An Artifact Changes"):
    with scenario("An edited story map's broken rule is counted on the chat bar"):
        with given("checkout-flow works on Stories, its story map generated"):
            self.project = seed_checkout_flow()
            self.session = checkout_flow_of(self.project)
        with and_("no validate has run on it"):
            expect(chat_bar_counts(self.project)).to(equal({}))
        with when("the Agent edits .context/story-map.md into the one sub-epic map"):
            # Chat bar -> Session.check_changed_artifact -> ChangedArtifact.check -> Validate.validate(paths)
            edit(self.project, STORY_MAP, ONE_SUB_EPIC_MAP)
            self.checked = self.session.check_changed_artifact(STORY_MAP)
        with then("the graph rules run on .context/story-map.md for stories-story-map, with no explicit validate"):
            expect(self.checked.checked).to(equal(["stories-story-map"]))
        with and_("the chat bar counts 1 violation on stories-story-map"):
            expect(chat_bar_counts(self.project)).to(equal({"stories-story-map": 1}))
            self.project.close()
    with scenario("A fixed story map leaves the chat bar's count"):
        with given("checkout-flow's story map is the one sub-epic map, its 1 violation counted on the chat bar"):
            self.project = seed_checkout_flow()
            self.session = checkout_flow_of(self.project)
            edit(self.project, STORY_MAP, ONE_SUB_EPIC_MAP)
            self.session.check_changed_artifact(STORY_MAP)
        with when("the Agent edits .context/story-map.md into the place order map"):
            edit(self.project, STORY_MAP, PLACE_ORDER_MAP)
            self.checked = self.session.check_changed_artifact(STORY_MAP)
        with then("the graph rules run on .context/story-map.md again"):
            expect(self.checked.checked).to(equal(["stories-story-map"]))
        with and_("the chat bar counts no violation on stories-story-map"):
            expect(chat_bar_counts(self.project)).to(equal({}))
            self.project.close()
    with scenario("A file no fidelity the chat bar shows declares is not checked"):
        with given("checkout-flow works on Stories"):
            self.project = seed_checkout_flow()
            self.session = checkout_flow_of(self.project)
        with when("the Agent edits README.md"):
            edit(self.project, README, "# Shop\n")
            self.checked = self.session.check_changed_artifact(README)
        with then("no graph rule runs on README.md"):
            expect(self.checked.checked).to(equal([]))
        with and_("no validation report is written"):
            expect(reports_written(self.project)).to(equal([]))
            self.project.close()
