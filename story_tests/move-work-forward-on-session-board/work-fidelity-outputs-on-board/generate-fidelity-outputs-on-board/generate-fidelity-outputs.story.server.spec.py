"""Generate Fidelity Outputs at the server tier: the shared scenarios through the generate.generate prompt, on a cdd
server started on a throwaway project."""

from space.kanban.session_board_tiers import ServerTier
from space.kanban.story_test import load_shared, replay

# FidelityGuidance.output_paths is not a cdd tool of its own: generate.generate folds the paths into its instructions.
NO_TOOL_FOR_OUTPUT_PATHS = "no cdd tool returns a fidelity's output paths on their own; generate.generate writes them into its instructions"

LEFT_OUT = {
    "Put a fidelity's files under its practice's root": NO_TOOL_FOR_OUTPUT_PATHS,
    "Use the practice's root named in session.json": NO_TOOL_FOR_OUTPUT_PATHS,
    "Prefer the fidelity's own root": NO_TOOL_FOR_OUTPUT_PATHS,
    "Rename a single-file output and keep a pattern": NO_TOOL_FOR_OUTPUT_PATHS,
}

# The domain tier proves every scenario's behaviour; this tier proves the cdd tools reach it, so it replays only
# the fewest scenarios that between them call each tool these scenarios use once.
WIRING = [
    'Count a generate line as Generate done',
]

globals().update(replay(load_shared(__file__, "generate-fidelity-outputs"), ServerTier(), LEFT_OUT, only=WIRING))
