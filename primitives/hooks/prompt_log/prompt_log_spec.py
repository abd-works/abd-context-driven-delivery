# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""BDD development specs for the prompt_log audit hook."""
import json
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "primitives/hooks", "primitives/hooks/prompt_log"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import context, description, it

import prompt_log as pl  # noqa: E402

_CURSOR = _REPO_ROOT / ".cursor"
_RULE = _CURSOR / "rules" / "character-driven-development.mdc"
_SKILL = _CURSOR / "skills" / "context_tools" / "bdd" / "bdd-behavior" / "SKILL.md"
_AGENT = _CURSOR / "agents" / "engineer.md"
_BEHAVIOR_RULE = _CURSOR / "rules" / "context_tools" / "bdd" / "behavior.mdc"


with description("a path classifier for prompt audit"):

    with context("that receives a project rule under .cursor/rules"):
        with it("should label it rule"):
            expect(pl.classify_path(str(_RULE))).to(equal("rule"))

    with context("that receives a skill SKILL.md under .cursor/skills"):
        with it("should label it skill"):
            expect(pl.classify_path(str(_SKILL))).to(equal("skill"))

    with context("that receives a subagent definition under .cursor/agents"):
        with it("should label it agent"):
            expect(pl.classify_path(str(_AGENT))).to(equal("agent"))

    with context("that receives an ordinary source file"):
        with it("should label it file"):
            expect(pl.classify_path(str(_REPO_ROOT / "pyproject.toml"))).to(equal("file"))


with description("a prompt log hook"):

    with context("that handles a beforeSubmitPrompt with rule and skill attachments"):
        with it("should record both attachment kinds in the log"):
            with tempfile.TemporaryDirectory() as tmp:
                log_file = Path(tmp) / "prompt-log.txt"
                payload = {
                    "hook_event_name": "beforeSubmitPrompt",
                    "conversation_id": "conv-test-001",
                    "generation_id": "gen-test-001",
                    "model": "composer-2.5",
                    "prompt": "run /bdd-behavior on the hook",
                    "attachments": [
                        {"type": "rule", "file_path": str(_BEHAVIOR_RULE)},
                        {"type": "file", "file_path": str(_SKILL)},
                    ],
                }
                out = pl.handle(payload, target=log_file)
                text = log_file.read_text(encoding="utf-8")
                expect(out).to(equal({"continue": True}))
                expect(text).to(contain("beforeSubmitPrompt"))
                expect(text).to(contain("[rule]"))
                expect(text).to(contain("behavior.mdc"))
                expect(text).to(contain("[skill]"))
                expect(text).to(contain("SKILL.md"))

    with context("that handles a beforeReadFile for a rule file"):
        with it("should record the rule path and content size"):
            with tempfile.TemporaryDirectory() as tmp:
                log_file = Path(tmp) / "prompt-log.txt"
                content = _BEHAVIOR_RULE.read_text(encoding="utf-8")
                payload = {
                    "hook_event_name": "beforeReadFile",
                    "conversation_id": "conv-test-002",
                    "generation_id": "gen-test-002",
                    "model": "composer-2.5",
                    "file_path": str(_BEHAVIOR_RULE),
                    "content": content,
                    "attachments": [
                        {"type": "rule", "file_path": str(_BEHAVIOR_RULE)},
                    ],
                }
                out = pl.handle(payload, target=log_file)
                text = log_file.read_text(encoding="utf-8")
                expect(out).to(equal({"permission": "allow"}))
                expect(text).to(contain("beforeReadFile"))
                expect(text).to(contain("READ [rule]"))
                expect(text).to(contain("behavior.mdc"))
                expect(text).to(contain(f"size: {len(content)} chars"))

    with context("that handles a preToolUse Read of a skill file"):
        with it("should record the skill path"):
            with tempfile.TemporaryDirectory() as tmp:
                log_file = Path(tmp) / "prompt-log.txt"
                payload = {
                    "hook_event_name": "preToolUse",
                    "conversation_id": "conv-test-003",
                    "generation_id": "gen-test-003",
                    "model": "composer-2.5",
                    "tool_name": "Read",
                    "tool_input": {"path": str(_SKILL)},
                }
                out = pl.handle(payload, target=log_file)
                text = log_file.read_text(encoding="utf-8")
                expect(out).to(equal({"permission": "allow"}))
                expect(text).to(contain("preToolUse:Read"))
                expect(text).to(contain("read [skill]"))
                expect(text).to(contain("bdd-behavior"))

    with context("that handles a preToolUse Task with a subagent prompt"):
        with it("should record the task prompt text"):
            with tempfile.TemporaryDirectory() as tmp:
                log_file = Path(tmp) / "prompt-log.txt"
                payload = {
                    "hook_event_name": "preToolUse",
                    "conversation_id": "conv-test-004",
                    "generation_id": "gen-test-004",
                    "model": "composer-2.5",
                    "tool_name": "Task",
                    "tool_input": {
                        "description": "Explore hooks",
                        "prompt": "Find all hook scripts under primitives/hooks",
                        "subagent_type": "explore",
                    },
                }
                out = pl.handle(payload, target=log_file)
                text = log_file.read_text(encoding="utf-8")
                expect(out).to(equal({"permission": "allow"}))
                expect(text).to(contain("preToolUse:Task"))
                expect(text).to(contain("primitives/hooks"))

    with context("that handles a subagentStart event"):
        with it("should record the subagent task"):
            with tempfile.TemporaryDirectory() as tmp:
                log_file = Path(tmp) / "prompt-log.txt"
                payload = {
                    "hook_event_name": "subagentStart",
                    "conversation_id": "conv-test-005",
                    "generation_id": "gen-test-005",
                    "model": "composer-2.5",
                    "subagent_type": "engineer",
                    "subagent_model": "composer-2.5",
                    "task": "Review prompt_log.py for clean engineering",
                }
                out = pl.handle(payload, target=log_file)
                text = log_file.read_text(encoding="utf-8")
                expect(out).to(equal({"permission": "allow"}))
                expect(text).to(contain("subagentStart"))
                expect(text).to(contain("prompt_log.py"))

    with context("that is invoked from stdin like Cursor does"):
        with it("should parse BOM-prefixed JSON and allow the action"):
            with tempfile.TemporaryDirectory() as tmp:
                log_file = Path(tmp) / "prompt-log.txt"
                payload = {
                    "hook_event_name": "beforeSubmitPrompt",
                    "conversation_id": "conv-test-006",
                    "generation_id": "gen-test-006",
                    "model": "composer-2.5",
                    "prompt": "test",
                    "attachments": [
                        {"type": "rule", "file_path": str(_AGENT)},
                    ],
                }
                raw = b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8")
                parsed = pl.parse_hook_payload(raw)
                out = pl.handle(parsed, target=log_file)
                expect(out).to(equal({"continue": True}))
                expect(log_file.read_text(encoding="utf-8")).to(contain("engineer.md"))
