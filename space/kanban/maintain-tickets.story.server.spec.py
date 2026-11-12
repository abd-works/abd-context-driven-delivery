"""Maintain Tickets at the server tier: the shared scenarios through the cdd tools ticket.*, backlog-item.*, and
board.*, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    "Edit a ticket's text",
    "Edit a backlog item's text",
    'Keep a ticket where it was moved in its column',
    'Keep a backlog item where it was moved',
    'Delete a ticket and its session folder',
    "Tag a ticket's session",
]

globals().update(replay(load_shared(__file__, "maintain-tickets"), ServerTier(), only=WIRING))
