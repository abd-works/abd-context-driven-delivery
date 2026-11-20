"""Explore Graph In Files App at the server tier: the shared scenarios through the cdd tools session.graph_trees,
session.graph_branch, session.graph_node_ranges, session.graph_members, session.graph_filter_choices and
ticket.choose_overlays, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only the
# fewest scenarios that between them call each tool these scenarios use, and pass a node filter through, once.
WIRING = [
    "Opening a node shows one level of its children",
    "Selecting a related node opens the related node alone, in its own file",
    "Choosing a node type keeps only those nodes",
    "An overlay taken off leaves the graph view",
    "A call to an operation in another file opens in place",
]

globals().update(replay(load_shared(__file__, "explore-graph-in-files-app"), ServerTier(), only=WIRING))
