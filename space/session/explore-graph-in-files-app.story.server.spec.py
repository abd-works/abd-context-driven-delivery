"""Explore Graph In Files App at the server tier: the shared scenarios through the cdd tools session.graph_branch and
session.graph_members, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays every
# scenario, since each calls a tool the other does not.
globals().update(replay(load_shared(__file__, "explore-graph-in-files-app"), ServerTier()))
