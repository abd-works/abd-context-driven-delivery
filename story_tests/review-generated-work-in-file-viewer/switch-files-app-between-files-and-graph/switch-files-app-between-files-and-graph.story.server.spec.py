"""Switch Files App Between Files And Graph at the server tier: the shared scenarios through the cdd tools
session.graph_trees, session.graph_branch, session.graph_node_ranges and session.file with the file view's filters, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only the
# fewest scenarios that between them call each tool these scenarios use once.
WIRING = ["Selecting a folder's node opens every listed file below it", "A connector left out of the node filter leaves out what a step reaches by it"]

globals().update(replay(load_shared(__file__, "switch-files-app-between-files-and-graph"), ServerTier(), only=WIRING))
