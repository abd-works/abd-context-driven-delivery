"""Choose Session Practices And Overlays In Chat Bar at the domain tier: the shared scenarios on Ticket itself."""

from space.kanban.session_board_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "choose-session-practices-and-overlays-in-chat-bar"), DomainTier()))
