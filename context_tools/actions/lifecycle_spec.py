"""BDD spec for LifecycleAction — optional default work session."""

import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_foreign = str(
    Path.home()
    / "OneDrive - abd.works"
    / "personal"
    / "paradise-mobile"
    / "abd-context-driven-delivery"
)
_root = str(_REPO_ROOT)
sys.path[:] = [
    p
    for p in sys.path
    if not (
        p.replace("/", "\\").lower().startswith(_foreign.lower())
        and ".venv" not in p.lower()
    )
]
if _root in sys.path:
    sys.path.remove(_root)
sys.path.insert(0, _root)
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
sys.path.insert(0, _root)
for _name in list(sys.modules):
    if (
        _name in {"primitives", "scan", "lifecycle", "workspace", "context_tools", "tools"}
        or _name.startswith("primitives.")
        or _name.startswith("scan.")
        or _name.startswith("context_tools.")
        or _name.startswith("tools.")
        or _name.startswith("workspace.")
    ):
        del sys.modules[_name]

from expects import equal, expect
from mamba import description, it


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
