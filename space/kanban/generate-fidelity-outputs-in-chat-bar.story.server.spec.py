"""Generate Fidelity Outputs In Chat Bar at the server tier: the shared scenarios through the cdd tools generate prompt,
on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "generate-fidelity-outputs-in-chat-bar"), ServerTier()))
