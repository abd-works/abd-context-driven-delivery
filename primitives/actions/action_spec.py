"""BDD: @action with no docstring uses the method name as the instruction label."""
import sys
from pathlib import Path

from expects import be_true, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from primitives.actions.action import _ActionExpander, action
from primitives.actions.action import _ActionRunRequest, _ActionRunner
from tools.tool import Toolset
from tools.tool import _ToolsetLoader

_MARKER = "CUSTOM_STEP_MARKER"
_BASE_TOOLSET = "context_tools.base.base_context_tool:BaseContextTool"


class _PlainHost(Toolset):
    """Non-context toolset - empty-docstring default must still apply."""


_PlainHost._is_toolset = True  # type: ignore[attr-defined]


@action
def custom_step(self) -> str:
    return "done."


@action
def labeled_like_custom_step(self) -> str:
    """custom_step"""
    return "done."


_PlainHost.custom_step = custom_step
_PlainHost.labeled_like_custom_step = labeled_like_custom_step


with description("@action docstring defaults"):
    with context("any @action with no docstring"):
        with before.each:
            self.host = _PlainHost()
            self.expander = _ActionExpander.instance()

        with it("should expand prose using the method name as the instruction label"):
            body = self.expander.parse_body(_PlainHost.custom_step, self.host)
            joined = "\n".join(body.prose_parts)
            expect(_MARKER in joined).to(be_true)

        with it("should match an explicit docstring equal to that same label"):
            no_doc = self.expander.parse_body(_PlainHost.custom_step, self.host)
            with_doc = self.expander.parse_body(
                _PlainHost.labeled_like_custom_step, self.host
            )
            expect(no_doc.prose_parts).to(equal(with_doc.prose_parts))

    with context("a BaseContextTool framework action with no docstring"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_BASE_TOOLSET)
            self.host = cls()
            self.response = _ActionRunner.instance().invoke_action(
                _ActionRunRequest(
                    request={"toolset": _BASE_TOOLSET, "context": {}},
                    toolset_path=_BASE_TOOLSET,
                    action_name="validate",
                    context={},
                    arguments={},
                    instance=self.host,
                )
            )

        with it("should still inline # Validate from base_context_tool.md"):
            expect("# Validate" in self.response["instructions"]).to(be_true)
