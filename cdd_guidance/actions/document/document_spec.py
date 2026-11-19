"""BDD spec for the Document action: the paths it is asked to scan."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, expect, raise_error
from mamba import after, before, context, description, it

from cdd_guidance.actions.document.document import Document
from harness.agent_tools.agent_tools import AgentInstructions
from harness.agent_tools.tool_call import ToolCall
from harness.agent_tools.recipe import RecipeLineFailed
from space.session.throwaway_project import ThrowawayProject
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue

_STORY_MAP = """# (E) Manage Customer Orders

## (E) Place New Order

### (S) Customer --> Browse Product Catalog
"""


with description("Document asked to scan paths, in a session") as self:
    with before.each:
        self.project = ThrowawayProject()
        folder = self.project.root / ".context"
        folder.mkdir()
        (folder / "story-map.md").write_text(_STORY_MAP, encoding="utf-8")
        action = Document().for_call(ToolCall({}, self.project.root))
        document = AgentInstructions.for_callable(Document.document, action)
        self.documented = lambda paths: document.expand({"guidance": "stories-story-map", "paths": paths}).instructions

    with after.each:
        self.project.close()

    with context("that are files under the session's root"):
        with it("should name each file to scan, from the session's root"):
            expect(self.documented([".context/story-map.md"])).to(contain("Scan these paths: .context/story-map.md"))

    with context("one of which is not there"):
        with it("should refuse that path by name, as validate does"):
            expect(lambda: self.documented([".context/story-map.md", "nope/missing.md"])).to(raise_error(RecipeLineFailed, contain("NamedPathNotFoundError: nothing at nope/missing.md")))

    with context("one of which is outside the session's root"):
        with it("should refuse that path by name"):
            outside = Path(tempfile.mkdtemp(prefix="document-outside-")) / "outside.md"
            outside.write_text(_STORY_MAP, encoding="utf-8")
            expect(lambda: self.documented([str(outside)])).to(raise_error(RecipeLineFailed, contain("NamedPathNotFoundError: nothing under the session's root")))
