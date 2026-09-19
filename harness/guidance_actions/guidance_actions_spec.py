"""BDD spec for GuidanceAction — optional default work session."""

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
for _cat in ("harness", "tools", "practices", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)
sys.path.insert(0, _root)
for _name in list(sys.modules):
    if (
        _name in {"harness", "scan", "lifecycle", "guidance_actions", "workspace", "practices", "tools"}
        or _name.startswith("harness.")
        or _name.startswith("scan.")
        or _name.startswith("guidance_actions.")
        or _name.startswith("practices.")
        or _name.startswith("tools.")
        or _name.startswith("workspace.")
    ):
        del sys.modules[_name]

from expects import equal, expect
from mamba import description, it


with description("GuidanceAction"):
    with it("should open the default work session when begin runs without a session name"):
        from guidance_actions import GuidanceAction

        tmp = Path(tempfile.mkdtemp(prefix="guidance-action-default-"))
        kit = GuidanceAction(path=str(tmp))
        warning = kit.begin(action="sketch")
        session = kit.workspace.current_work_session
        expect(session).not_to(equal(None))
        expect(session.name).to(equal("default"))
        expect(session.folder).to(equal(tmp / ".sessions" / "default"))
        expect(warning).to(equal(""))

    with it("should run the passed operation once when guidance is a string"):
        from guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-run-"))))
        seen: list = []
        kit.run("just this text", seen.append, action="generate")
        expect(seen).to(equal(["just this text"]))

    with it("should run the passed operation on each host when guidance is a list"):
        from guidance_actions import GuidanceAction

        kit = GuidanceAction(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-run-"))))
        first, second = object(), object()
        seen: list = []
        kit.run([first, second], seen.append, action="generate")
        expect(seen).to(equal([first, second]))

    with it("should inject listed hosts rules markdown after this action returns"):
        from generate.generate import Generate
        from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleGuidance

        kit = Generate(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-inject-"))))
        result = kit.inject_rules(
            {
                "tool_name": "generate.generate",
                "tool_input": {"guidance": [SampleGuidance(format="markdown")]},
            }
        )
        expect("sample rule one" in (result.get("additional_context") or "")).to(equal(True))
        expect(getattr(type(kit).inject_rules, "_echo", False)).to(equal(True))

    with it("should skip inject_rules for document"):
        from document.document import Document
        from harness.guidance.fixtures.sample_tool.sample_tool_host import SampleGuidance

        kit = Document(path=str(Path(tempfile.mkdtemp(prefix="guidance-action-doc-"))))
        result = kit.inject_rules(
            {
                "tool_name": "document.document",
                "tool_input": {"guidance": [SampleGuidance(format="markdown")]},
            }
        )
        expect(result).to(equal({}))
