"""Steer Ticket Sessions at the server tier: the shared scenarios through the cdd tools ticket.*, backlog-item.*,
and board.*, on a cdd server started on a throwaway project. Heavy, because these scenarios run real git through the
server's own process: worktrees, merges, and pushes to an origin. The domain tier replays them on a repository held in
memory, which the quick suite runs; this spec is where real git proves them."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "steer-ticket-sessions"), ServerTier()))
