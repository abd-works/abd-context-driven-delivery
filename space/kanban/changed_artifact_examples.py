"""The examples the Check Graph Rules When An Artifact Changes story shares: a throwaway project holding the checkout-flow
session, whose board the cdd server's tools read, and the story maps its agent edits.

Scenarios: story_tests/connect-sessions-across-channels-and-apps/check-work-in-generate/check_work_in_generate_story.test.md
"""
from __future__ import annotations

from space.kanban.board_tools_examples import ProjectTools, ticket_of, violation_counts_of
from space.session import Sessions
from space.session.session import Session

# Seed: the ticket whose session the agent edits in, and the line its log holds once its story map was generated.
CHECKOUT_FLOW = "checkout-flow"
STORY_MAP_GENERATED = "2026-11-20T01:00:00Z generate /work stories story_map markdown stories no-chat"
# Interaction: the files the agent edits, from the project's root.
STORY_MAP = ".context/story-map.md"
README = "README.md"
# Interaction: the story map with one sub-epic under its epic, which breaks child-count-fits-layer.
ONE_SUB_EPIC_MAP = """# Story Map

# (E) Manage Customer Orders

## (E) Place New Order

### (S) Customer --> Browse Product Catalog

### (S) Customer --> Add Item To Cart

### (S) Customer --> Enter Shipping Address

### (S) Customer --> Submit Order
"""
# Interaction: the same stories straight under the epic Place New Order, which breaks no graph rule.
PLACE_ORDER_MAP = """# Story Map

# (E) Place New Order

### (S) Customer --> Browse Product Catalog

### (S) Customer --> Add Item To Cart

### (S) Customer --> Enter Shipping Address

### (S) Customer --> Submit Order
"""


def seed_checkout_flow() -> ProjectTools:
    """A project of its own holding checkout-flow, whose log says its story map was generated and no validate ran."""
    project = ProjectTools()
    project.ticket(CHECKOUT_FLOW, STORY_MAP_GENERATED, title="Checkout flow")
    return project


def edit(project: ProjectTools, path: str, text: str) -> None:
    """The agent's edit: path in project now holds text."""
    file = project.root / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8")


def checkout_flow_of(project: ProjectTools) -> Session:
    """checkout-flow's session in project, as the cdd server holds it."""
    return Sessions.of_project(project.root).named(CHECKOUT_FLOW)


def chat_bar_counts(project: ProjectTools) -> dict[str, int]:
    """The violations checkout-flow's ticket counts by fidelity on the board the chat bar draws its counts from."""
    return violation_counts_of(ticket_of(project.call("board.show"), CHECKOUT_FLOW))


def reports_written(project: ProjectTools) -> list[str]:
    """The validation reports in checkout-flow's session folder."""
    folder = project.sessions / CHECKOUT_FLOW / "validation-reports"
    return sorted(report.name for report in folder.glob("*.md")) if folder.is_dir() else []
