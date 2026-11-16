"""Steer Ticket Sessions at the server tier: the shared scenarios through the cdd tools ticket.*, backlog-item.*,
and board.*, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    'Complete the active ticket with its work committed',
    'Start a backlog item in a chosen folder',
    "Choose one practice's root and go back to its default",
    'Add an idea to the Backlog',
    'Open a new ticket',
    'Move a ticket on to the next column',
    "Drag a ticket into a stage's Done whatever its work",
    'Move a ticket back to the previous column',
    'Archive a ticket off the board',
    'Show the latest handoff',
    "Choose a ticket's root",
    'Close a session whose work is on main',
    'Return to main whatever is chosen',
]

globals().update(replay(load_shared(__file__, "steer-ticket-sessions"), ServerTier(), only=WIRING))
