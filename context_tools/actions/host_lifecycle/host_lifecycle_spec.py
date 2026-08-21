# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BDD spec for HostLifecycle toolset."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("host_lifecycle", None)

from expects import be_true, equal, expect
from mamba import context, description, it

from host_lifecycle.host_lifecycle import HostLifecycle


class _ContextTool:
    def __init__(self, steps: list[str]) -> None:
        self.steps = steps

    def generate(self) -> str:
        self.steps.append("generate")
        return "ok"

    def validate(self) -> str:
        self.steps.append("validate")
        return "ok"

    def document(self, paths: list[str]) -> str:
        self.steps.append(f"document:{paths}")
        return "ok"

    def satisfy(self) -> str:
        self.steps.append("satisfy")
        return "ok"


with description("a HostLifecycle toolset"):
    with context("generate action"):
        with it("should run generate once per context tool"):
            steps: list[str] = []
            HostLifecycle().generate(tools=[_ContextTool(steps), _ContextTool(steps)])
            expect(steps).to(equal(["generate", "generate"]))

    with context("validate action"):
        with it("should run validate once per context tool"):
            steps: list[str] = []
            HostLifecycle().validate(tools=[_ContextTool(steps)])
            expect(steps).to(equal(["validate"]))

    with context("document action"):
        with it("should run document with paths once per context tool"):
            steps: list[str] = []
            HostLifecycle().document(tools=[_ContextTool(steps)], paths=["a.py"])
            expect(steps).to(equal(["document:['a.py']"]))

    with context("satisfy action"):
        with it("should run satisfy once per context tool"):
            steps: list[str] = []
            HostLifecycle().satisfy(tools=[_ContextTool(steps)])
            expect(steps).to(equal(["satisfy"]))


with description("a BaseContextTool host lifecycle"):
    with it("should keep full generate on the host for kits to delegate to"):
        import inspect

        from context_tools.base.base_context_tool import BaseContextTool

        source = inspect.getsource(BaseContextTool.generate)
        expect("generate_output" in source).to(equal(True))
