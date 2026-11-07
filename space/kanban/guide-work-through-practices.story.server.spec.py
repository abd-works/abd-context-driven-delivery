"""Guide Work Through Practices at the server tier: the shared scenarios through the cdd tools ticket.* and
board.help, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "guide-work-through-practices"), ServerTier()))
