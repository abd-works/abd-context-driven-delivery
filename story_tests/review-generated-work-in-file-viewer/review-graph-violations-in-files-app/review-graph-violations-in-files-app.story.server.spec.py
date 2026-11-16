"""Review Graph Violations In Files App at the server tier: the shared scenarios through the cdd tools
session.graph_trees and session.graph_branch, a node filter passed through, on a cdd server started on a throwaway
project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

globals().update(replay(load_shared(__file__, "review-graph-violations-in-files-app"), ServerTier()))
