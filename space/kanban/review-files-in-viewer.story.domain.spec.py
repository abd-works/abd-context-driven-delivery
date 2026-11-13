"""Review Files In Viewer at the domain tier: the shared scenarios on the session, its file comments, and the chat."""

from space.kanban.session_board_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "review-files-in-viewer"), DomainTier()))
