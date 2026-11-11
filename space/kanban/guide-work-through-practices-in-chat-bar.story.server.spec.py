"""Guide Work Through Practices In Chat Bar at the server tier: the shared scenarios through the cdd tools
ticket.overlay_choices and ticket.choose_overlays, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

LEFT_OUT = {
    "Apply the chosen overlays to the session's graph": "the cdd tools hand back the ticket's answers, never its session's graph object",
}

globals().update(replay(load_shared(__file__, "guide-work-through-practices-in-chat-bar"), ServerTier(), LEFT_OUT))
