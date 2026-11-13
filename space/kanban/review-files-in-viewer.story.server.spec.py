"""Review Files In Viewer at the server tier: the shared scenarios through the cdd tools session.read_file,
session.write_file, the file-comments tools and the chat tools, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    "Show a code file in the viewer with its lines numbered",
    "Fold the file's class and its operations",
    "Mark the lines a broken rule names",
    "Mark a comment beside the selection's first line",
    "Save the edited text to the file on disk",
    "Delete a file comment",
    "Send every open comment at once",
    "Clear the processed comments, keeping the rest",
]

globals().update(replay(load_shared(__file__, "review-files-in-viewer"), ServerTier(), only=WIRING))
