"""Generate Fidelity Outputs In Chat Bar at the domain tier: the shared scenarios on Generate and the session itself."""

from space.kanban.session_board_tiers import DomainTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "generate-fidelity-outputs-in-chat-bar"), DomainTier()))
