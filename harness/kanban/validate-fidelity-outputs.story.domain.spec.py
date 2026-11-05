"""Validate Fidelity Outputs at the domain tier: the shared scenarios on Ticket, Session, and the Validate action
themselves."""

from harness.kanban.session_board_tiers import DomainTier
from harness.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "validate-fidelity-outputs"), DomainTier()))
