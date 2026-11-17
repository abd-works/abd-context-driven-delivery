"""Review Graph Violations In Files App in a real browser: the Violations switch and a broken rule opening its lines, on
the Files app served for real (files_app_browser.FilesStack), walked by hand in the Files app first.

Scenarios: review_graph_violations_in_files_app_story.test.md. The Python tiers replay the rest from
review-graph-violations-in-files-app.story.shared.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from expects import equal, expect
from mamba import after, before, context, description, it

from files_app_browser import GRAPH_READ_MILLISECONDS, REVIEW_MAP, SHOWN_MILLISECONDS, STORY_REVIEW, FilesStack, graph_view, line, open_branches, settled

FIDELITIES = "stories-story-map"
# Interaction: the stories the graph view keeps with the Violations switch on: the two that open with a generic verb.
VIOLATING_STORIES = ["Story Handle Ticket Deletion", "Story Process Ticket Archive"]


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
                story.locator('button.graph-node[title^="Rule verb-noun-format:"]').click()
                line(self.page, "(S) Person --> Process Ticket Archive").wait_for(timeout=SHOWN_MILLISECONDS)

            with it("Then the story map opens at Process Ticket Archive's line"):
                expect(self.page.locator("section.open-file").evaluate_all("files => files.map(file => file.getAttribute('aria-label'))")).to(equal([REVIEW_MAP]))
