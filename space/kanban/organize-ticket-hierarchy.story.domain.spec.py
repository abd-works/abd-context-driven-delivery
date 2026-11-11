"""Organize Ticket Hierarchy at the domain tier: the shared scenarios on Ticket itself."""

from space.kanban.session_board_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "organize-ticket-hierarchy"), DomainTier()))
