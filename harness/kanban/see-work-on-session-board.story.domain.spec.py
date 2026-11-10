"""See Work On Session Board at the domain tier: the shared scenarios on Board, Ticket, and BacklogItem themselves."""

from harness.kanban.session_board_tiers import DomainTier
from harness.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "see-work-on-session-board"), DomainTier()))
