"""BDD specs for prompt echo against MCP and rule signatures."""
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_tools = str(_REPO_ROOT / "tools")
if _tools not in sys.path:
    sys.path.insert(0, _tools)

from expects import contain, equal, expect
from mamba import context, description, it

from harness.installation.installer import Installer  # noqa: F401 — load Destination before hooks
from tempfile import TemporaryDirectory

from harness.hooks.hook_server import rules_toast
from harness.annotations.annotation import Toast
from tools.prompt_notify.prompt_notify import PromptNotify
from harness.agent_tools import agent_instructions, agent_tool, agent_toolset
from harness.hooks.hook_server import HookPayload

_prompt_notify = PromptNotify()


class SpecFixture:
    def _echo(self, payload: HookPayload) -> str:
        return str(_prompt_notify.handle(payload).get("user_message") or "")


_spec = SpecFixture()


with description("prompt echo detection"):
    with context("that receives an action MCP tool name"):
        with it("should name the action from sketch.sketch"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "sketch.sketch", "tool_input": {}}))
            expect(kind).to(equal("action"))
            expect(label).to(equal("sketch"))

        with it("should name the action from generate_generate"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "generate_generate", "tool_input": {}}))
            expect(kind).to(equal("action"))
            expect(label).to(equal("generate"))

        with it("should name verify-fix from the operation the improvement action publishes"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "improvement.verify_fix", "tool_input": {}}))
            expect(label).to(equal("verify-fix"))

        with it("should name repair from the operation the improvement action publishes"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "improvement.repair", "tool_input": {}}))
            expect(label).to(equal("repair"))

    with context("that receives the name of an action no action folder publishes"):
        with it("should name no action"):
            expect(_prompt_notify.detect(HookPayload({"tool_name": "scan.scan", "tool_input": {}}))).to(equal(None))

    with context("that receives a CallMcpTool wrapper"):
        with it("should read the nested MCP tool name"):
            kind, label = _prompt_notify.detect(
                HookPayload({
                    "tool_name": "CallMcpTool",
                    "tool_input": {"toolName": "bdd-behavior", "arguments": {}},
                })
            )
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("bdd-behavior"))

    with context("that receives a practice MCP tool name"):
        with it("should name the practice from bdd.instructions"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "bdd.instructions", "tool_input": {}}))
            expect(kind).to(equal("practice"))
            expect(label).to(equal("bdd"))

    with context("that receives a fidelity MCP tool name"):
        with it("should name the fidelity from ddd-bounded-context"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "ddd-bounded-context", "tool_input": {}}))
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("ddd-bounded-context"))

        with it("should name the fidelity from stories-story-map"):
            kind, label = _prompt_notify.detect(HookPayload({"tool_name": "stories-story-map", "tool_input": {}}))
            expect(label).to(equal("stories-story-map"))

    with context("that receives a skill path Read"):
        with it("should name the fidelity from a practice skill folder"):
            kind, label = _prompt_notify.detect(
                HookPayload({
                    "tool_name": "Read",
                    "tool_input": {
                        "path": str(
                            _REPO_ROOT
                            / ".claude"
                            / "skills"
                            / "practices-bdd-bdd-behavior"
                            / "SKILL.md"
                        )
                    },
                })
            )
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("bdd-behavior"))

    with context("that receives a practice rules file"):
        with it("should name the rule from the rules path"):
            kind, label = _prompt_notify.detect(
                HookPayload({
                    "tool_name": "Read",
                    "tool_input": {
                        "path": str(
                            _REPO_ROOT / ".claude" / "rules" / "practices" / "bdd.md"
                        )
                    },
                })
            )
            expect(kind).to(equal("rule"))
            expect(label).to(equal("bdd"))

    with context("that receives a source file whose path names a practice"):
        with it("should not toast a practice"):
            expect(
                _prompt_notify.handle(
                    HookPayload({
                        "tool_name": "Read",
                        "tool_input": {
                            "path": str(_REPO_ROOT / "cdd_guidance" / "practices" / "ddd" / "ddd.md")
                        },
                    })
                ).get("user_message")
            ).to(equal(None))

        with it("should not toast a practice from a command that mentions one"):
            expect(
                _prompt_notify.handle(
                    HookPayload({
                        "tool_name": "Shell",
                        "tool_input": {"command": "rg stories practices/stories"},
                    })
                ).get("user_message")
            ).to(equal(None))

    with context("that receives an ordinary source file Read"):
        with it("should not echo"):
            expect(
                _prompt_notify.handle(
                    HookPayload({
                        "tool_name": "Read",
                        "tool_input": {
                            "path": str(_REPO_ROOT / "harness" / "agent_tools" / "agent_tools.py")
                        },
                    })
                ).get("user_message")
            ).to(equal(None))

    with context("that receives a guidance source file Read or edit"):
        with it("should not toast an action"):
            path = str(_REPO_ROOT / "harness" / "guidance" / "rule.py")
            expect(
                _prompt_notify.handle(HookPayload({"tool_name": "Read", "tool_input": {"path": path}})).get(
                    "user_message"
                )
            ).to(equal(None))
            expect(
                _prompt_notify.handle(
                    HookPayload({
                        "tool_name": "StrReplace",
                        "tool_input": {"path": path, "old_string": "a", "new_string": "b"},
                    })
                ).get("user_message")
            ).to(equal(None))

    with context("that echoes a detected MCP action"):
        with it("should include the kind and label in the user message"):
            expect(
                _spec._echo(HookPayload({"tool_name": "validate.validate", "tool_input": {"paths": ["src"]}}))
            ).to(contain("Action \u2192 validate"))

        with it("should write that echo to the workspace toast notice"):
            with TemporaryDirectory() as tmp:
                [dest] = _prompt_notify.show_ide_toast(
                    _spec._echo(HookPayload({"tool_name": "validate.validate", "tool_input": {}})), [Path(tmp)]
                )
                expect(json.loads(dest.read_text(encoding="utf-8"))["message"]).to(
                    contain("Action \u2192 validate")
                )

        with it("should write the toast notice into every workspace root"):
            with TemporaryDirectory() as tmp:
                repo = Path(tmp) / "cdd"
                other = Path(tmp) / "app"
                repo.mkdir()
                other.mkdir()
                _prompt_notify.show_ide_toast("chat edit \u2192 rules : code", [repo, str(other)])
                copied = other / ".cursor" / "prompt-notify-toast.json"
                expect((repo / ".cursor" / "prompt-notify-toast.json").is_file()).to(equal(True))
                expect(copied.is_file()).to(equal(True))
                expect(json.loads(copied.read_text(encoding="utf-8"))["message"]).to(
                    contain("rules : code")
                )

        with it("should write the toast when Cursor sends a slash-drive workspace root"):
            with TemporaryDirectory() as tmp:
                repo = Path(tmp) / "cdd"
                other = Path(tmp) / "app"
                repo.mkdir()
                other.mkdir()
                resolved = other.resolve()
                rest = resolved.as_posix().split(":", 1)[1]
                slash_drive = f"/{resolved.drive[0].lower()}:{rest}"
                _prompt_notify.show_ide_toast("chat edit \u2192 rules : code", [slash_drive])
                copied = other / ".cursor" / "prompt-notify-toast.json"
                expect(copied.is_file()).to(equal(True))

        with it("should not rewrite practice echoes into a rules toast"):
            with TemporaryDirectory() as tmp:
                _prompt_notify.show_ide_toast("Practice \u2192 ddd", [Path(tmp)])
                [dest] = _prompt_notify.show_ide_toast("Practice \u2192 stories", [Path(tmp)])
                expect(json.loads(dest.read_text(encoding="utf-8"))["message"]).to(
                    equal("Practice \u2192 ddd; Practice \u2192 stories")
                )

        with it("should stack rules notices from the same burst"):
            with TemporaryDirectory() as tmp:
                _prompt_notify.show_ide_toast(
                    "rules injected for clean-engineering-code\n"
                    "rules injected for clean-engineering-modules",
                    [Path(tmp)],
                )
                [dest] = _prompt_notify.show_ide_toast(
                    "rules injected for ddd-tactics\nrules injected for ddd-bounded-context", [Path(tmp)]
                )
                message = json.loads(dest.read_text(encoding="utf-8"))["message"]
                expect(message).to(
                    equal(
                        "rules injected for clean-engineering-code\n"
                        "rules injected for clean-engineering-modules\n\n"
                        "rules injected for ddd-tactics\n"
                        "rules injected for ddd-bounded-context"
                    )
                )

        with it("should keep both inject toasts from the same burst"):
            with TemporaryDirectory() as tmp:
                _prompt_notify.show_ide_toast(rules_toast("chat edit", ["agent bdd"]), [Path(tmp)])
                [dest] = _prompt_notify.show_ide_toast(
                    rules_toast("chat edit", ["clean engineering code", "ddd tactics"]), [Path(tmp)]
                )
                message = json.loads(dest.read_text(encoding="utf-8"))["message"]
                expect(message).to(
                    equal(
                        "chat edit \u2192 rules : agent bdd, "
                        "clean engineering code, ddd tactics"
                    )
                )


@agent_toolset
class EchoAction:
    """An action that pins @Toast on begin and on a method."""

    @Toast
    @agent_instructions
    def begin(self, guidance=None, action: str = "") -> str:
        return action

    @agent_tool
    def open_workspace(self, name: str = "") -> str:
        return name

    @agent_instructions
    def enact(self) -> str:
        return "enact"

    @Toast
    @agent_instructions
    def spotlight(self) -> str:
        return "spotlight"


@agent_toolset
class EchoPractice:
    """Practice-shaped Guidance with echoed instructions."""

    @Toast
    @agent_instructions
    def instructions(self) -> str:
        return "practice"


@agent_toolset
class EchoPracticeChild(EchoPractice):
    @agent_instructions
    def instructions(self) -> str:
        return "child"


with description("prompt echo @Toast annotation"):
    with context("that inherits @Toast on begin"):
        with it("should toast the action by its name when a recipe runs"):
            kind, label = _prompt_notify.detect_echo(
                HookPayload({"tool_name": "echo-action.enact", "tool_input": {}}),
                toolsets=[EchoAction()],
            )
            expect(kind).to(equal("action"))
            expect(label).to(equal("echo-action"))

        with it("should not toast open_workspace from the begin annotation"):
            expect(
                _prompt_notify.detect_echo(
                    HookPayload({"tool_name": "echo-action.open_workspace", "tool_input": {}}),
                    toolsets=[EchoAction()],
                )
            ).to(equal(None))

    with context("that annotates a specific recipe"):
        with it("should toast that member when it is invoked"):
            kind, label = _prompt_notify.detect_echo(
                HookPayload({"tool_name": "echo-action.spotlight", "tool_input": {}}),
                toolsets=[EchoAction()],
            )
            expect(kind).to(equal("action"))
            expect(label).to(equal("spotlight"))

    with context("that annotates practice instructions"):
        with it("should toast the practice from the instructions member"):
            kind, label = _prompt_notify.detect_echo(
                HookPayload({"tool_name": "echo-practice.instructions", "tool_input": {}}),
                toolsets=[EchoPractice()],
            )
            expect(kind).to(equal("practice"))
            expect(label).to(equal("echo-practice"))

    with context("that inherits @Toast on practice instructions"):
            kind, label = _prompt_notify.detect_echo(
                HookPayload({"tool_name": "echo-practice-child.instructions", "tool_input": {}}),
                toolsets=[EchoPracticeChild()],
            )
            expect(kind).to(equal("practice"))
            expect(label).to(equal("echo-practice-child"))
