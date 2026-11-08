"""BDD spec — a call to any tool of a guidance action toasts as that action, through the Toast its inherited begin
carries, though no recipe runs begin."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import description, it

from harness.installation.installer import Installer  # noqa: F401 - load Destination before hooks
from harness.hooks.hook_server import HookPayload
from cdd_guidance.actions.generate.generate import Generate
from cdd_guidance.actions.sketch.sketch import Sketch
from tools.prompt_notify.prompt_notify import PromptNotify


def _toast(tool_name: str, action) -> tuple[str, str] | None:
    return PromptNotify().detect_echo(HookPayload({"tool_name": tool_name, "tool_input": {}}), toolsets=[action])


with description("a guidance action's tool call, as the prompt-notify hook sees it"):
    with it("should toast its recipe as the action"):
        expect(_toast("generate.generate", Generate())).to(equal(("action", "generate")))

    with it("should toast one of its tools as the action that publishes it"):
        expect(_toast("sketch.save_sketch", Sketch())).to(equal(("action", "sketch")))
