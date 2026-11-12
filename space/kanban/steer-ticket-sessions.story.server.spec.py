"""Steer Ticket Sessions at the server tier: the shared scenarios through the cdd tools ticket.*, backlog-item.*,
and board.*, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "steer-ticket-sessions"), ServerTier()))
