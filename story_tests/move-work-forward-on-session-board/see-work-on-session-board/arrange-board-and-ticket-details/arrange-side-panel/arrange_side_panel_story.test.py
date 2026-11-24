from __future__ import annotations

from story_test import and_, background, but_, given, scenario, story, then, when

# Epic: Move Work Forward On Session Board
# Sub-epic: Arrange Board And Ticket Details
# Map: ../../../../.context/story-map.md#s-person----arrange-side-panel
# Model: ../../../../.context/kanban-model.md
# Realizations: ../../../../.context/session-board-scenario-realization.md

# Story: Arrange Side Panel
# Actor: Person
#
# Acceptance criteria:
# - Resize Side Panel: a drag grip on the panel's left edge sets its width. Observed.
# - Expand Side Panel: one panel is expanded at a time and it takes the board's width less the other open panels. Observed.
# - Close Side Panel: × closes the panel. Observed.
# - Scroll Fixed Columns: columns keep their width and scroll sideways when a panel opens. Observed.
with story("Arrange Side Panel"):
    with scenario("Set a panel's width"):
        # Evidence: observed: side-panel-client.spec 'should set the width a drag asks for', 'should not go narrower than the smallest width'; story-actions.spec 'should set a panel's width on a drag of its left edge'.
        with given("the help panel is open beside the board"):
            pass
        with when("the Person widens the help panel to 700 pixels"):
            # Person -> SidePanelClient.setWidth('help', 700)
            pass
        with then("the help panel is 700 pixels wide"):
            pass
        with when("the Person narrows the help panel to 10 pixels"):
            # Person -> SidePanelClient.setWidth('help', 10)
            pass
        with then("the help panel stops at 360 pixels"):
            pass
    with scenario("Expand one panel at a time"):
        # Evidence: observed: side-panel-client.spec 'should expand one panel at a time'; story-actions.spec 'should let an expanded panel take the board's place, and × close it'.
        with given("the report panel and the help panel are open"):
            pass
        with and_("the report panel is expanded"):
            pass
        with when("the Person expands the help panel"):
            # Person -> SidePanelClient.toggleExpanded('help')
            pass
        with then("the help panel takes the board's width less the other open panels"):
            pass
        with and_("the report panel is no longer expanded"):
            pass
    with scenario("Close a side panel"):
        # Evidence: observed: side-panel-client.spec 'Close Side Panel' — 'should close the panel'.
        with given("checkout-flow's validation report panel is open"):
            pass
        with when("the Person closes the report panel"):
            # Person -> SidePanelClient.close('report')
            pass
        with then("no side panel is open"):
            pass
    with scenario("Keep the columns' width when a panel opens"):
        # Evidence: observed: story-actions.spec 'should keep the columns' width and scroll them sideways when a panel opens'.
        with given("the [board](../../../../.context/kanban-model.md#board) shows its five [columns](../../../../.context/kanban-model.md#column) at their own width"):
            pass
        with when("the Person opens checkout-flow's validation report"):
            # Person -> SidePanelClient.openReport('checkout-flow', its story map)
            pass
        with then("the columns keep their width and scroll sideways beside the report panel"):
            pass
