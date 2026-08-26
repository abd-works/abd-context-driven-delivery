"""BDD spec for context_tools/actions/workflow/workflow.py."""

import sys
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

    with it("should kebab-case issue titles for session slugs"):
        w = Workflow()
        expect(w._kebab("Add workflow package #87")).to(equal("add-workflow-package-87"))
