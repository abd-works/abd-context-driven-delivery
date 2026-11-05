"""Guide Work Through Practices at the domain tier: the shared scenarios on Ticket and Board themselves."""

from harness.kanban.session_board_tiers import DomainTier
from harness.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "guide-work-through-practices"), DomainTier()))
