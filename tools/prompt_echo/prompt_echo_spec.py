"""BDD specs for prompt echo against MCP and guideline signatures."""
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

from installation.installer import Installer  # noqa: F401 — load Destination before hooks
from tempfile import TemporaryDirectory

from prompt_echo.prompt_echo import PromptEcho, echo
from harness.agent_tools import agent_instructions, agent_tool, agent_toolset

_prompt_echo = PromptEcho()


class SpecFixture:
    def _echo(self, hook_payload: dict) -> str:
        return str(_prompt_echo.handle(hook_payload).get("user_message") or "")


_spec = SpecFixture()


with description("prompt echo detection"):
    with context("that receives an action MCP tool name"):
        with it("should name the action from sketch.sketch"):
            kind, label = _prompt_echo.detect({"tool_name": "sketch.sketch", "tool_input": {}})
            expect(kind).to(equal("action"))
            expect(label).to(equal("sketch"))

        with it("should name the action from generate_generate"):
            kind, label = _prompt_echo.detect({"tool_name": "generate_generate", "tool_input": {}})
            expect(kind).to(equal("action"))
            expect(label).to(equal("generate"))

        with it("should name create-rule from validate.createRule"):
            kind, label = _prompt_echo.detect({"tool_name": "validate.createRule", "tool_input": {}})
            expect(label).to(equal("create-rule"))

    with context("that receives a CallMcpTool wrapper"):
        with it("should read the nested MCP tool name"):
            kind, label = _prompt_echo.detect(
                {
                    "tool_name": "CallMcpTool",
                    "tool_input": {"toolName": "bdd-behavior", "arguments": {}},
                }
            )
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("bdd-behavior"))

    with context("that receives a practice MCP tool name"):
        with it("should name the practice from bdd.instructions"):
            kind, label = _prompt_echo.detect({"tool_name": "bdd.instructions", "tool_input": {}})
            expect(kind).to(equal("practice"))
            expect(label).to(equal("bdd"))

    with context("that receives a fidelity MCP tool name"):
        with it("should name the fidelity from ddd-bounded-context"):
            kind, label = _prompt_echo.detect({"tool_name": "ddd-bounded-context", "tool_input": {}})
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("ddd-bounded-context"))

        with it("should name the fidelity from stories-story-map"):
            kind, label = _prompt_echo.detect({"tool_name": "stories-story-map", "tool_input": {}})
            expect(label).to(equal("stories-story-map"))

    with context("that receives a skill path Read"):
        with it("should name the fidelity from a practice skill folder"):
            kind, label = _prompt_echo.detect(
                {
                    "tool_name": "Read",
                    "tool_input": {
                        "path": str(
                            _REPO_ROOT
                            / ".cursor"
                            / "skills"
                            / "practices"
                            / "bdd"
                            / "bdd-behavior"
                            / "SKILL.md"
                        )
                    },
                }
            )
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("bdd-behavior"))

    with context("that receives a practice rules file"):
        with it("should name the guideline from the rules path"):
            kind, label = _prompt_echo.detect(
                {
                    "tool_name": "Read",
                    "tool_input": {
                        "path": str(
                            _REPO_ROOT / ".cursor" / "rules" / "practices" / "bdd.mdc"
                        )
                    },
                }
            )
            expect(kind).to(equal("guideline"))
            expect(label).to(equal("bdd"))

    with context("that receives a legacy YAML action fence"):
        with it("should name the action from the command text"):
            kind, label = _prompt_echo.detect(
                {
                    "tool_name": "Shell",
                    "tool_input": {"command": "echo action: scan"},
                }
            )
            expect(kind).to(equal("action"))
            expect(label).to(equal("scan"))

    with context("that receives an ordinary source file Read"):
        with it("should not echo"):
            expect(
                _prompt_echo.handle(
                    {
                        "tool_name": "Read",
                        "tool_input": {
                            "path": str(_REPO_ROOT / "harness" / "agent_tools" / "agent_tools.py")
                        },
                    }
                ).get("user_message")
            ).to(equal(None))

    with context("that receives a scan kit source file Read or edit"):
        with it("should not toast the scan action"):
            path = str(_REPO_ROOT / "harness" / "guidance" / "rule.py")
            expect(
                _prompt_echo.handle({"tool_name": "Read", "tool_input": {"path": path}}).get(
                    "user_message"
                )
            ).to(equal(None))
            expect(
                _prompt_echo.handle(
                    {
                        "tool_name": "StrReplace",
                        "tool_input": {"path": path, "old_string": "a", "new_string": "b"},
                    }
                ).get("user_message")
            ).to(equal(None))

    with context("that echoes a detected MCP action"):
        with it("should include the kind and label in the user message"):
            expect(
                _spec._echo({"tool_name": "scan.scan", "tool_input": {"paths": ["src"]}})
            ).to(contain("Action \u2192 scan"))

        with it("should put that echo in the IDE toast notice"):
            expect(
                _prompt_echo.toast_notice(_spec._echo({"tool_name": "scan.scan", "tool_input": {}}))["message"]
            ).to(contain("Action \u2192 scan"))

        with it("should write that echo to the workspace toast notice"):
            with TemporaryDirectory() as tmp:
                _prompt_echo.repo = Path(tmp)
                dest = _prompt_echo.show_ide_toast(
                    _spec._echo({"tool_name": "scan.scan", "tool_input": {}}),
                )
                expect(json.loads(dest.read_text(encoding="utf-8"))["message"]).to(
                    contain("Action \u2192 scan")
                )

        with it("should write the toast notice into every workspace root"):
            with TemporaryDirectory() as tmp:
                repo = Path(tmp) / "cdd"
                other = Path(tmp) / "app"
                repo.mkdir()
                other.mkdir()
                _prompt_echo.repo = repo
                _prompt_echo.toast_roots = [str(other)]
                dest = _prompt_echo.show_ide_toast(
                    "chat edit \u2192 rules : code",
                )
                copied = other / ".cursor" / "prompt-echo-toast.json"
                expect(dest.is_file()).to(equal(True))
                expect(copied.is_file()).to(equal(True))
                expect(json.loads(copied.read_text(encoding="utf-8"))["message"]).to(
                    contain("rules : code")
                )

        with it("should keep both inject toasts from the same burst"):
            with TemporaryDirectory() as tmp:
                repo = Path(tmp)
                _prompt_echo.repo = repo
                _prompt_echo.show_ide_toast(
                    _prompt_echo.inject_rules_toast("chat edit", ["agent bdd"]),
                )
                dest = _prompt_echo.show_ide_toast(
                    _prompt_echo.inject_rules_toast(
                        "chat edit",
                        ["clean engineering code", "ddd tactics"],
                    ),
                )
                message = json.loads(dest.read_text(encoding="utf-8"))["message"]
                expect(message).to(
                    equal(
                        "chat edit \u2192 rules : agent bdd, "
                        "clean engineering code, ddd tactics"
                    )
                )


@agent_toolset
class EchoKit:
    """Kit used to pin @echo on begin and on a method."""

    @echo
    @agent_instructions
    def begin(self, guidance=None, action: str = "") -> str:
        return action

    @agent_tool
    def open_workspace(self, name: str = "") -> str:
        return name

    @agent_instructions
    def enact(self) -> str:
        return "enact"

    @echo
    @agent_instructions
    def spotlight(self) -> str:
        return "spotlight"


@agent_toolset
class EchoPractice:
    """Practice-shaped Guidance with echoed instructions."""

    @echo
    @agent_instructions
    def instructions(self) -> str:
        return "practice"


@agent_toolset
class EchoPracticeChild(EchoPractice):
    @agent_instructions
    def instructions(self) -> str:
        return "child"


with description("prompt echo @echo mark"):
    with context("that inherits @echo on begin"):
        with it("should toast the kit as an action when a recipe runs"):
            kind, label = _prompt_echo.detect_echo(
                {"tool_name": "echo-kit.enact", "tool_input": {}},
                toolsets=[EchoKit()],
            )
            expect(kind).to(equal("action"))
            expect(label).to(equal("echo-kit"))

        with it("should not toast open_workspace from the begin mark"):
            expect(
                _prompt_echo.detect_echo(
                    {"tool_name": "echo-kit.open_workspace", "tool_input": {}},
                    toolsets=[EchoKit()],
                )
            ).to(equal(None))

    with context("that marks a specific recipe"):
        with it("should toast that member when it is invoked"):
            kind, label = _prompt_echo.detect_echo(
                {"tool_name": "echo-kit.spotlight", "tool_input": {}},
                toolsets=[EchoKit()],
            )
            expect(kind).to(equal("action"))
            expect(label).to(equal("spotlight"))

    with context("that marks practice instructions"):
        with it("should toast the practice from the instructions member"):
            kind, label = _prompt_echo.detect_echo(
                {"tool_name": "echo-practice.instructions", "tool_input": {}},
                toolsets=[EchoPractice()],
            )
            expect(kind).to(equal("practice"))
            expect(label).to(equal("echo-practice"))

    with context("that inherits @echo on practice instructions"):
            kind, label = _prompt_echo.detect_echo(
                {"tool_name": "echo-practice-child.instructions", "tool_input": {}},
                toolsets=[EchoPracticeChild()],
            )
            expect(kind).to(equal("practice"))
            expect(label).to(equal("echo-practice-child"))
