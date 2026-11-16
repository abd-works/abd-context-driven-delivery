"""Organize Ticket Hierarchy at the server tier: the shared scenarios through the cdd tools ticket.* and board.*, on a
cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    'Add a child ticket by hand',
    'Drag a ticket onto a parent',
    'Pull a child out of its parent',
    'Move a pulled-out child like any ticket',
    'Start a Backlog item under a ticket',
]

globals().update(replay(load_shared(__file__, "organize-ticket-hierarchy"), ServerTier(), only=WIRING))
