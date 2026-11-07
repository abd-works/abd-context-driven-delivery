"""Review Fidelity Outputs at the server tier: the shared scenarios through the cdd tools ticket.files,
ticket.session_files, ticket.read_file, and ticket.finish_review, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "review-fidelity-outputs"), ServerTier()))
