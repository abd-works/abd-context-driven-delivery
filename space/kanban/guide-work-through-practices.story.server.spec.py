"""Guide Work Through Practices at the server tier: the shared scenarios through the cdd tools ticket.* and
board.help, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    'Turn a practice off for a ticket',
    "Open a practice's help",
    'Mark a ticket done in its stage',
    'Mark a ticket back in progress',
    "Open a fidelity's help",
    'Open the report while violations hold the ticket',
]

globals().update(replay(load_shared(__file__, "guide-work-through-practices"), ServerTier(), only=WIRING))
