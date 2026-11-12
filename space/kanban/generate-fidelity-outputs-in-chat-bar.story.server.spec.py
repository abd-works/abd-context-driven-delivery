"""Generate Fidelity Outputs In Chat Bar at the server tier: the shared scenarios through the cdd tools generate prompt,
on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    'Choose the overlays a command names',
    "Judge each overlay's shared rules when validating",
]

globals().update(replay(load_shared(__file__, "generate-fidelity-outputs-in-chat-bar"), ServerTier(), only=WIRING))
