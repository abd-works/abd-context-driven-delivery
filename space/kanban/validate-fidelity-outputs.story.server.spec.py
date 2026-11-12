"""Validate Fidelity Outputs at the server tier: the shared scenarios through the cdd tools ticket.report and
ticket.violations and the validate.validate prompt, on a cdd server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

LEFT_OUT = {
    "Count Validate done only with no graph-rule violations": "Validate writes its validate line from the graph it builds inside the cdd server; no tool writes a line naming chosen violations",
}

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    "Open a fidelity's latest report",
    'Save the report and the graph it checked',
    "Show every fidelity's violations at once",
]

globals().update(replay(load_shared(__file__, "validate-fidelity-outputs"), ServerTier(), LEFT_OUT, only=WIRING))
