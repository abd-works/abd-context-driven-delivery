"""Review Fidelity Outputs at the domain tier: the shared scenarios on Ticket itself."""

from harness.kanban.session_board_tiers import DomainTier
from harness.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "review-fidelity-outputs"), DomainTier()))
