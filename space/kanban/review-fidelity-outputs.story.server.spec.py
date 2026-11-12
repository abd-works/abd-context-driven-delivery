"""Review Fidelity Outputs at the server tier: the shared scenarios through the cdd tools ticket.files,
ticket.session_files and ticket.read_file, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    'Open one tab per format, generated or not',
    "Browse the ticket's session folder",
]

globals().update(replay(load_shared(__file__, "review-fidelity-outputs"), ServerTier(), only=WIRING))
