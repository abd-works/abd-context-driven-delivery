"""See Work On Session Board at the server tier: the shared scenarios through the cdd tools board.show and
board.set_wip_limit, and the ticket tools, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

LEFT_OUT = {
    "Draw the columns of the board": "board.show always shows every practice: no cdd tool chooses the practices of a board",
}

globals().update(replay(load_shared(__file__, "see-work-on-session-board"), ServerTier(), LEFT_OUT))
