"""BDD spec for manifest-gate hook - scan header, run manifests, deliver guidance directly."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_empty, be_true, contain, equal, expect, have_key
from mamba import context, description, it

import utilities.manifest_hook.manifest_gate as gate


_MANIFEST_FILE = """\
# @toolset-manifest python -m tools manifest ooad.ooad:Ooad
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
\"\"\"Some module docstring.\"\"\"
class Foo:
    pass
"""

_PLAIN_FILE = """\
\"\"\"No manifest lines here.\"\"\"
class Bar:
    pass
"""

_FAKE_MANIFEST_OUTPUT = "```yaml\ntype: ooadanalysis\n```"


with description("scan_manifest_lines"):
    with context("given a file with manifest header lines"):
        with it("returns those lines"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            lines = gate.scan_manifest_lines(path)
            expect(any("@toolset-manifest" in l for l in lines)).to(be_true)
            expect(any("invoke-edit" in l for l in lines)).to(be_true)

    with context("given a file with no manifest lines"):
        with it("returns an empty list"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_PLAIN_FILE)
                path = f.name
            lines = gate.scan_manifest_lines(path)
            expect(lines).to(be_empty)

    with context("given a path that does not exist"):
        with it("returns an empty list"):
            lines = gate.scan_manifest_lines("/does/not/exist.py")
            expect(lines).to(be_empty)


with description("handle_post_tool_use (Read hook)"):
    with context("given a file with manifest lines"):
        with it("surfaces manifest output as additional_context, header included verbatim"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_input": {"path": path}}
            with patch.object(gate, "run_manifests", return_value=(_FAKE_MANIFEST_OUTPUT, [])):
                result = gate.handle_post_tool_use(data)
            expect(result).to(have_key("additional_context"))
            expect(result["additional_context"]).to(contain("MANIFEST GATE"))
            expect(result["additional_context"]).to(contain(_FAKE_MANIFEST_OUTPUT))
            expect(result["additional_context"]).to(contain("invoke-edit"))
            expect(result).to(have_key("user_message"))

    with context("given a file with no manifest lines"):
        with it("returns an empty dict"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_PLAIN_FILE)
                path = f.name
            data = {"tool_input": {"path": path}}
            result = gate.handle_post_tool_use(data)
            expect(result).to(equal({}))

    with context("given no path in tool_input"):
        with it("returns an empty dict"):
            result = gate.handle_post_tool_use({"tool_input": {}})
            expect(result).to(equal({}))

    with context("given a file_path at the top level (afterFileEdit payload shape)"):
        with it("returns additional_context using the top-level file_path"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"file_path": path}
            with patch.object(gate, "run_manifests", return_value=(_FAKE_MANIFEST_OUTPUT, [])):
                result = gate.handle_post_tool_use(data)
            expect(result).to(have_key("additional_context"))
            expect(result["additional_context"]).to(contain("MANIFEST GATE"))
            expect(result).to(have_key("user_message"))


with description("handle_pre_tool_use (Write hook)"):
    with context("given a mutating edit on a file with manifest lines"):
        with it("delivers guidance and allows the edit directly - never denies"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_name": "Write", "tool_input": {"path": path, "contents": "x"}}
            with patch.object(gate, "run_manifests", return_value=(_FAKE_MANIFEST_OUTPUT, [])):
                result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect(result["agent_message"]).to(contain("MANIFEST GATE"))
            expect(result["agent_message"]).to(contain(_FAKE_MANIFEST_OUTPUT))
            expect(result).to(have_key("user_message"))

    with context("given the same file touched again in the same run"):
        with it("still allows directly - nothing accumulates that could later deny it"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_name": "Write", "tool_input": {"path": path, "contents": "x"}}
            with patch.object(gate, "run_manifests", return_value=(_FAKE_MANIFEST_OUTPUT, [])):
                first = gate.handle_pre_tool_use(data)
                second = gate.handle_pre_tool_use(data)
            expect(first["permission"]).to(equal("allow"))
            expect(second["permission"]).to(equal("allow"))

    with context("given guidance already delivered earlier in this conversation"):
        with it("does not remanifest or re-inject on a later mutating touch"):
            # #17 — reuse guidance already in context; stay in fidelity-tool format
            # without re-calling manifest. First touch delivers; second must not.
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {
                "conversation_id": "conv-reuse-pre-001",
                "tool_name": "Write",
                "tool_input": {"path": path, "contents": "x"},
            }
            with patch.object(
                gate, "run_manifests", return_value=(_FAKE_MANIFEST_OUTPUT, [])
            ) as mocked:
                first = gate.handle_pre_tool_use(data)
                second = gate.handle_pre_tool_use(data)
            expect(first["permission"]).to(equal("allow"))
            expect(first["agent_message"]).to(contain("MANIFEST GATE"))
            expect(second["permission"]).to(equal("allow"))
            expect("agent_message" not in second).to(be_true)
            expect(mocked.call_count).to(equal(1))

    with context("given the same asset post-touched twice in one conversation"):
        with it("runs the manifest once and skips re-inject on the second post"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {
                "conversation_id": "conv-reuse-post-001",
                "tool_name": "Read",
                "tool_input": {"path": path},
            }
            with patch.object(
                gate, "run_manifests", return_value=(_FAKE_MANIFEST_OUTPUT, [])
            ) as mocked:
                first = gate.handle_post_tool_use(data)
                second = gate.handle_post_tool_use(data)
            expect(first).to(have_key("additional_context"))
            expect(first["additional_context"]).to(contain("MANIFEST GATE"))
            expect(second).to(equal({}))
            expect(mocked.call_count).to(equal(1))

    with context("given a file that does not exist (new file creation)"):
        with it("returns permission allow with no agent_message"):
            data = {
                "tool_name": "Write",
                "tool_input": {"path": "/does/not/exist.py", "contents": "x"},
            }
            result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect("agent_message" not in result).to(be_true)

    with context("given an existing file with no manifest lines"):
        with it("returns permission allow with no agent_message"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_PLAIN_FILE)
                path = f.name
            data = {"tool_name": "Write", "tool_input": {"path": path, "contents": "x"}}
            result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect("agent_message" not in result).to(be_true)

    with context("given a non-mutating tool on a manifest file"):
        with it("allows without running the manifest"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_name": "Read", "tool_input": {"path": path}}
            result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))


with description("parse_hook_payload - double-BOM regression"):
    with context("given raw bytes with a single BOM"):
        with it("parses correctly"):
            payload = {"tool_name": "Read", "tool_input": {"path": "/tmp/x.py"}}
            raw = b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8")
            result = gate.parse_hook_payload(raw)
            expect(result).to(equal(payload))

    with context("given raw bytes with two consecutive BOMs (Cursor format)"):
        with it("strips both BOMs and parses correctly"):
            payload = {"tool_name": "Write", "tool_input": {"file_path": "/tmp/x.py"}}
            raw = b"\xef\xbb\xbf\xef\xbb\xbf" + json.dumps(payload).encode("utf-8")
            result = gate.parse_hook_payload(raw)
            expect(result).to(equal(payload))

    with context("given raw bytes with no BOM"):
        with it("parses correctly"):
            payload = {"tool_input": {}}
            raw = json.dumps(payload).encode("utf-8")
            result = gate.parse_hook_payload(raw)
            expect(result).to(equal(payload))


# Cursor rejects the entire hooks.json if any key is unknown (e.g. Claude Code
# PascalCase PostToolUse/PreToolUse). That disables all project hooks silently.
_CURSOR_HOOK_TYPES = frozenset({
    "beforeShellExecution",
    "beforeMCPExecution",
    "afterShellExecution",
    "afterMCPExecution",
    "beforeReadFile",
    "afterFileEdit",
    "beforeTabFileRead",
    "afterTabFileEdit",
    "stop",
    "beforeSubmitPrompt",
    "afterAgentResponse",
    "afterAgentThought",
    "sessionStart",
    "sessionEnd",
    "preCompact",
    "subagentStart",
    "subagentStop",
    "preToolUse",
    "postToolUse",
    "postToolUseFailure",
    "workspaceOpen",
})


with description("hooks.json Cursor event names"):
    with context("given .cursor/hooks.json"):
        with it("uses only Cursor-valid camelCase hook types"):
            path = _REPO_ROOT / ".cursor" / "hooks.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            unknown = sorted(set(data.get("hooks", {})) - _CURSOR_HOOK_TYPES)
            expect(unknown).to(equal([]))

    with context("given primitives/tools/hooks/manifest-gate.json"):
        with it("uses only Cursor-valid camelCase hook types"):
            path = _REPO_ROOT / "primitives" / "tools" / "hooks" / "manifest-gate.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            unknown = sorted(set(data.get("hooks", {})) - _CURSOR_HOOK_TYPES)
            expect(unknown).to(equal([]))
