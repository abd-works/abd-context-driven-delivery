"""Switch Files App Between Files And Graph at the domain tier: the shared scenarios on the session's graph."""

from space.kanban.session_board_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "switch-files-app-between-files-and-graph"), DomainTier()))
