"""BDD spec for tools/granola/granola.py — Granola toolset."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, equal, expect
from mamba import context, description, it

from granola.granola import Granola
from harness.agent_tools.agent_tools import AgentInstructions


def _expanded(action: str) -> str:
    toolset = Granola()
    body = AgentInstructions.for_callable(getattr(type(toolset), action), toolset)
    return "\n".join(body.prompt)


with description("a Granola toolset"):
    with context("whose format_filing_plan is given notes for two folders"):
        with it("should group notes under each folder and mark new folders"):
            plan = json.dumps([
                {"note_id": "a", "title": "Inventory", "date": "2026-08-25", "folder": "Paradise", "new_folder": True},
                {"note_id": "b", "title": "New note", "date": "2026-09-30", "folder": ""},
            ])
            rendered = Granola().format_filing_plan(plan)
            expect("## Paradise (new)" in rendered).to(be_true)
            expect("## Review Before Filing" in rendered).to(be_true)
            expect("2 notes into 2 folders" in rendered).to(be_true)

    with context("whose write_note_context writes a note into a folder"):
        with it("should write a Granola-marked file that list_note_context then finds"):
            with tempfile.TemporaryDirectory() as root:
                granola = Granola(path=root)
                written = granola.write_note_context(
                    "src/inventory", "abc-123", "Inventory and payment systems", "2026-08-31",
                    "https://notes.granola.ai/d/abc-123", "## Summary\nStock moves.",
                )
                stored = Path(written).read_text(encoding="utf-8")
                expect("source: granola" in stored).to(be_true)
                expect("note_id: abc-123" in stored).to(be_true)
                expect(Path(written).name).to(equal("2026-08-31-inventory-and-payment-systems.md"))
                expect(granola.list_note_context("src/inventory")).to(equal(written))

    with context("whose organize action is expanded"):
        with it("should ask for confirmation before creating or moving anything"):
            expect("Create and move nothing until the user confirms" in _expanded("organize")).to(be_true)

    with context("whose context action is expanded"):
        with it("should write one file per note"):
            expect("once per note" in _expanded("context")).to(be_true)
