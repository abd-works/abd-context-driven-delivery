"""BDD specs for prompt echo against MCP and guideline signatures."""
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import context, description, it

from installation.installer import Installer  # noqa: F401 — load Destination before hooks
from tempfile import TemporaryDirectory

from installation.hooks.prompt_echo.prompt_echo import (
    detect,
    handle,
    show_ide_toast,
    toast_notice,
)


def _echo(payload: dict) -> str:
    return str(handle(payload).get("user_message") or "")


with description("prompt echo detection"):
    with context("that receives an action MCP tool name"):
        with it("should name the action from sketch.sketch"):
            kind, label = detect({"tool_name": "sketch.sketch", "tool_input": {}})
            expect(kind).to(equal("action"))
            expect(label).to(equal("sketch"))

        with it("should name the action from generate_generate"):
            kind, label = detect({"tool_name": "generate_generate", "tool_input": {}})
            expect(kind).to(equal("action"))
            expect(label).to(equal("generate"))

        with it("should name create-rule from validate.createRule"):
            kind, label = detect({"tool_name": "validate.createRule", "tool_input": {}})
            expect(label).to(equal("create-rule"))

    with context("that receives a CallMcpTool wrapper"):
        with it("should read the nested MCP tool name"):
            kind, label = detect(
                {
                    "tool_name": "CallMcpTool",
                    "tool_input": {"toolName": "bdd-behavior", "arguments": {}},
                }
            )
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("bdd-behavior"))

    with context("that receives a practice MCP tool name"):
        with it("should name the practice from bdd.instructions"):
            kind, label = detect({"tool_name": "bdd.instructions", "tool_input": {}})
            expect(kind).to(equal("practice"))
            expect(label).to(equal("bdd"))

    with context("that receives a fidelity MCP tool name"):
        with it("should name the fidelity from ddd-bounded-context"):
            kind, label = detect({"tool_name": "ddd-bounded-context", "tool_input": {}})
            expect(kind).to(equal("fidelity"))
            expect(label).to(equal("ddd-bounded-context"))

        with it("should name the fidelity from stories-story-map"):
            kind, label = detect({"tool_name": "stories-story-map", "tool_input": {}})
            expect(label).to(equal("stories-story-map"))

    with context("that receives a skill path Read"):
        with it("should name the fidelity from a practice skill folder"):
            kind, label = detect(
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
            kind, label = detect(
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
            kind, label = detect(
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
                handle(
                    {
                        "tool_name": "Read",
                        "tool_input": {
                            "path": str(_REPO_ROOT / "harness" / "agent_tools" / "agent_tools.py")
                        },
                    }
                ).get("user_message")
            ).to(equal(None))

    with context("that echoes a detected MCP action"):
        with it("should include the kind and label in the user message"):
            expect(
                _echo({"tool_name": "scan.scan", "tool_input": {"paths": ["src"]}})
            ).to(contain("Action \u2192 scan"))

        with it("should put that echo in the IDE toast notice"):
            expect(
                toast_notice(_echo({"tool_name": "scan.scan", "tool_input": {}}))["message"]
            ).to(contain("Action \u2192 scan"))

        with it("should write that echo to the workspace toast notice"):
            with TemporaryDirectory() as tmp:
                dest = show_ide_toast(
                    _echo({"tool_name": "scan.scan", "tool_input": {}}),
                    repo=Path(tmp),
                )
                expect(json.loads(dest.read_text(encoding="utf-8"))["message"]).to(
                    contain("Action \u2192 scan")
                )
