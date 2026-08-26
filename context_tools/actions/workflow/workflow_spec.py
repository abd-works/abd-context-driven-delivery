"""BDD spec for context_tools/actions/workflow/workflow.py."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from workflow.workflow import Workflow


with description("Workflow helpers"):
    with it("should kebab-case focus labels"):
        w = Workflow()
        expect(w._kebab("Git Notes On Deploy")).to(equal("git-notes-on-deploy"))

    with it("should resolve backlog destination under repo"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            w = Workflow(workspace=str(root))
            dest = w.backlog_destination("My Idea")
            expect(dest).to(equal(str((root / ".context/sessions/backlog/my-idea").resolve())))

    with it("should allocate sequential ticket ids"):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            w = Workflow(workspace=str(root))
            expect(w.next_ticket_id()).to(equal("CDD-1"))
            w.record_ticket("CDD-1", "first")
            expect(w.next_ticket_id()).to(equal("CDD-2"))
