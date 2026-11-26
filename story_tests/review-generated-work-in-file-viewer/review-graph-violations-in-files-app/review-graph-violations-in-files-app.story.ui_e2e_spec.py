"""Review Graph Violations In Files App in a real browser: the Violations switch, a broken rule opening its lines, and the
graph view's Fix this one, Fix rule and Fix all filling the prompt of the chat that opened the page, on the Files app
served for real (files_app_browser.FilesStack), walked by hand in the Files app first. No Claude chat runs here: the
fill the chat takes as it checks in is what its chat bar would put in its prompt.

Scenarios: review_graph_violations_in_files_app_story.test.md. The Python tiers replay the rest from
review-graph-violations-in-files-app.story.shared.py."""

import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import GRAPH_READ_MILLISECONDS, all_session_files, REVIEW_MAP, SHOWN_MILLISECONDS, STORY_REVIEW, FilesStack, graph_view, line, open_branches, settled
from harness.mcp.spec_support import SpecChat

FIDELITIES = "stories-story-map"
# Interaction: the stories the graph view keeps with the Violations switch on: the two that open with a generic verb.
VIOLATING_STORIES = ["Story Handle Ticket Deletion", "Story Process Ticket Archive"]


# Seed: the chat that opened the Files app, checked in with the cdd server as its chat bar checks in.
REVIEW_CHAT = "review-chat"
STORY_NAME_RULE = "story-name-captures-system-mechanic"


def opened_from_chat(stack: FilesStack):
    """The Files app on story-review's story map files, opened by review-chat."""
    page = stack.browser.new_page(viewport={"width": 1600, "height": 900})
    named = {"files": STORY_REVIEW, "fidelity": FIDELITIES, "project": str(stack.project), "chat": REVIEW_CHAT}
    page.goto(f"http://127.0.0.1:{stack.port}/?{urllib.parse.urlencode(named)}")
    return page


def filled(stack: FilesStack) -> list[str]:
    """The fills review-chat takes as it checks in, as its chat bar does every second. The browser holds this thread's
    event loop, so the chat calls the cdd server from a thread of its own."""
    chat = SpecChat(stack.cdd, stack.project, REVIEW_CHAT)
    with ThreadPoolExecutor(1) as pool:
        taken = pool.submit(chat.answer, "chat.check_in", chat=REVIEW_CHAT, is_busy=False, name="Review", folder=str(stack.project)).result()
    return [command["text"] for command in taken if command["kind"] == "fill"]


def fixed(within, test_id: str) -> None:
    """Press the Fix button test_id within a part of the page and wait for it to say it was sent to the chat."""
    within.get_by_test_id(test_id).click()
    within.get_by_test_id(f"{test_id}-outcome").and_(within.locator(".is-sent")).wait_for(timeout=GRAPH_READ_MILLISECONDS)


def story_titles(page) -> list[str]:
    return sorted(page.locator('button.graph-node[title^="Story "]').evaluate_all("nodes => nodes.map(node => node.title)"))


with description("Review Graph Violations In Files App, in a real browser") as self:
    with before.all:
        self.stack = FilesStack()
        self.page = self.stack.open(STORY_REVIEW, FIDELITIES)
        chosen = self.page.locator('.format-toggle[aria-pressed="true"]')
        chosen.first.wait_for(timeout=SHOWN_MILLISECONDS)
        chosen.first.click()
        graph_view(self.page)

    with after.all:
        self.page.close()
        self.stack.close()

    with context("Given the Files app shows story-review's graph, whose story map holds Process Ticket Archive, Handle Ticket Deletion and Delete Ticket"):
        with context("Story: Show Only Violating Nodes In Files App, Scenario: The Violations switch keeps only nodes that break a rule"):
            with before.all:
                self.page.locator(".graph-filters-toggle").click()
                self.page.get_by_role("button", name="Violations").click()
                self.page.locator('button.graph-node[title="Practice stories"]').wait_for(timeout=GRAPH_READ_MILLISECONDS)
                open_branches(self.page, "stories", "Remove Tickets", "Retire Tickets")

            with it("Then the graph view keeps Process Ticket Archive and Handle Ticket Deletion, and not Delete Ticket"):
                expect(settled(lambda: story_titles(self.page), lambda shown: shown == VIOLATING_STORIES)).to(equal(VIOLATING_STORIES))

        with context("Story: Open Violation In Files App Source, Scenario: Selecting a broken rule opens its lines unfolded"):
            with before.all:
                open_branches(self.page, "Process Ticket Archive")
                story = self.page.locator('li.graph-entry:has(> .tree-row button.graph-node[title="Story Process Ticket Archive"])')
                story.get_by_role("button", name="Open rules", exact=True).first.click()
                story.locator('button.graph-node[title^="Rule story-name-captures-system-mechanic:"]').click()
                line(self.page, "(S) Person --> Process Ticket Archive").wait_for(timeout=SHOWN_MILLISECONDS)

            with it("Then the story map opens at Process Ticket Archive's line"):
                expect(self.page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")).to(equal([REVIEW_MAP]))


with description("Fix Graph Violations From Files App, in a real browser") as self:
    with before.all:
        self.stack = FilesStack()
        filled(self.stack)

    with after.all:
        self.stack.close()

    with context("Given the Files app shows story-review's violating stories in the graph view, opened from review-chat"):
        with before.all:
            self.page = opened_from_chat(self.stack)
            chosen = self.page.locator('.format-toggle[aria-pressed="true"]')
            chosen.first.wait_for(timeout=SHOWN_MILLISECONDS)
            chosen.first.click()
            graph_view(self.page)
            self.page.locator(".graph-filters-toggle").click()
            self.page.get_by_role("button", name="Violations").click()
            self.page.locator('button.graph-node[title="Practice stories"]').wait_for(timeout=GRAPH_READ_MILLISECONDS)
            open_branches(self.page, "stories", "Remove Tickets", "Retire Tickets", "Process Ticket Archive")
            story = self.page.locator('li.graph-entry:has(> .tree-row button.graph-node[title="Story Process Ticket Archive"])')
            story.get_by_role("button", name="Open rules", exact=True).first.click()
            self.rule_row = story.locator(f'.tree-row:has(button.graph-node[title^="Rule {STORY_NAME_RULE}:"])').first
            filled(self.stack)

        with after.all:
            self.page.close()

        with context("Story: Fix Graph Violations From Files App, Scenario: Fixing one violation sends it alone to the chat"):
            with it("Then review-chat is filled with the fix for Process Ticket Archive alone"):
                fixed(self.rule_row, "graph-fix-one")
                fills = filled(self.stack)
                expect([len(fills), "Node: Process Ticket Archive (Story)" in fills[0], "Handle Ticket Deletion" in fills[0]]).to(equal([1, True, False]))

        with context("Story: Fix Graph Violations From Files App, Scenario: Fixing a rule sends every violation of it"):
            with it("Then review-chat is filled with one fix for Process Ticket Archive and Handle Ticket Deletion"):
                fixed(self.rule_row, "graph-fix-rule")
                fills = filled(self.stack)
                expect([len(fills), "Node: Process Ticket Archive (Story)" in fills[0], "Node: Handle Ticket Deletion (Story)" in fills[0]]).to(equal([1, True, True]))

        with context("Story: Fix Graph Violations From Files App, Scenario: Fixing all sends every violation the graph view shows"):
            with it("Then review-chat is filled with one fix naming both stories"):
                fixed(self.page, "graph-fix-all")
                fills = filled(self.stack)
                expect([len(fills), fills[0].startswith("Fix these"), "Node: Handle Ticket Deletion (Story)" in fills[0]]).to(equal([1, True, True]))

    with context("Given the Files app shows story-review's story map with its rules in the file view, opened from review-chat"):
        with before.all:
            self.page = opened_from_chat(self.stack)
            all_session_files(self.page)
            self.page.get_by_role("button", name="List", exact=True).click()
            rules = self.page.get_by_role("button", name="Rules", exact=True)
            if rules.get_attribute("aria-pressed") != "true":
                rules.click()
            self.page.locator(f'button.file-entry[title^="{REVIEW_MAP}"]').first.click()
            self.page.get_by_role("button", name="Source", exact=True).click()
            self.page.locator(f'button.source-rule:has-text("{STORY_NAME_RULE}")').click()
            self.banner = self.page.get_by_test_id("violation-banner")
            self.banner.get_by_test_id("violation-fix-one").nth(1).wait_for(timeout=GRAPH_READ_MILLISECONDS)
            filled(self.stack)

        with after.all:
            self.page.close()

        with context("Story: Fix Graph Violations From Files App, Scenario: Fixing a rule in the file view comments on each place it breaks"):
            with it("Then review-chat is filled with one fix comment on each of Process Ticket Archive's and Handle Ticket Deletion's lines"):
                fixed(self.banner, "violation-fix-rule")
                fills = filled(self.stack)
                expect([len(fills), fills[0].count(f"Rule: {STORY_NAME_RULE}")]).to(equal([1, 2]))

        with context("Story: Fix Graph Violations From Files App, Scenario: Fixing one place in the file view sends it alone"):
            with it("Then review-chat is filled with the fix comment on Handle Ticket Deletion's line alone"):
                place = self.banner.get_by_test_id("violation-place").nth(1)
                fixed(place, "violation-fix-one")
                fills = filled(self.stack)
                expect([len(fills), fills[0].count(f"Rule: {STORY_NAME_RULE}"), "Handle Ticket Deletion" in fills[0]]).to(equal([1, 1, True]))

        with context("Story: Fix Graph Violations From Files App, Scenario: Fixing all in the file view sends every broken place"):
            with it("Then review-chat is filled with one prompt holding a fix comment for every broken place of the story map"):
                fixed(self.page.locator(".file-source-bar"), "file-fix-all")
                fills = filled(self.stack)
                expect([len(fills), fills[0].count(f"Rule: {STORY_NAME_RULE}") >= 2]).to(equal([1, True]))
