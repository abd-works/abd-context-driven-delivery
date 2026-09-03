"""BDD spec for LifecycleAction — optional default work session."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import description, it

from workspace.git_repo import NullGitRepo
from workspace.workspace import SessionModel


with description("LifecycleAction"):
    with it("should open the default work session when begin runs without a session name"):
        from lifecycle import LifecycleAction

        tmp = Path(tempfile.mkdtemp(prefix="lifecycle-default-"))
        kit = LifecycleAction(path=str(tmp))
        warning = kit.begin(action="sketch")
        session = kit.workspace.current_work_session
        expect(session).not_to(equal(None))
        expect(session.name).to(equal("default"))
        expect(session.folder).to(equal(tmp / ".context" / "sessions" / "default"))
        expect(warning).to(equal(""))