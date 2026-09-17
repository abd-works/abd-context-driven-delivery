"""BDD spec — HookDeployment output."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from primitives.guidance.fixtures.agentic_ops.agentic_ops import SampleAgenticOps
from primitives.guidance.fixtures.agentic_ops.hook_ops import SampleHookOps
from primitives.harness import Harness


with description("a Cursor hooks config") as self:
    with context("that has been deployed with hook sources in the walk"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Harness(ide="Cursor", path=self.tree).write_deploy([SampleHookOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write hooks manifest entries for each registered hook event"):
            text = (self.tree / "hooks.json").read_text(encoding="utf-8")
            expect(text).to(contain("stop"))

        with it("should write hook skill files for hook-published agent-instructions operations"):
            expect((self.tree / "skills" / "hook-auto_turn" / "SKILL.md").is_file()).to(equal(True))

    with context("that has been partially deployed with no hook sources emitted"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            prior = self.tree / "hooks.json"
            prior.write_text('{"hooks": [{"event": "stop"}]}\n', encoding="utf-8")
            Harness(ide="Cursor", path=self.tree).write_deploy([SampleAgenticOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should leave hooks manifest unchanged from a prior full deploy"):
            text = (self.tree / "hooks.json").read_text(encoding="utf-8")
            expect(text).to(contain("stop"))
