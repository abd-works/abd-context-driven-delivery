"""BDD spec for manifest-gate hook - scan, run manifests, deny-until-cleared."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_empty, be_false, be_true, contain, equal, expect, have_key
from mamba import before, context, description, it

import tools.hooks.manifest_gate as gate


_MANIFEST_FILE = """\
# @toolset-manifest python -m tools manifest ooad.ooad:Ooad
# Agent reading this file: run line 1 manifest, then follow instructions.
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
_FAKE_INVOKE_OUTPUT = "ok: true\ninstructions: do the thing"


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


with description("parse_invoke_directive / find_invoke_edit"):
    with context("given action toolset and context segments"):
        with it("parses each segment"):
            parsed = gate.parse_invoke_directive(
                "action satisfy | toolset: a.b:C | context.fidelity modules"
            )
            expect(parsed["action"]).to(equal("satisfy"))
            expect(parsed["toolset"]).to(equal("a.b:C"))
            expect(parsed["context"]["fidelity"]).to(equal("modules"))

    with context("given manifest lines with invoke-edit"):
        with it("returns action and toolset"):
            lines = [
                "# @toolset-manifest python -m tools manifest ooad.ooad:Ooad",
                "# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd",
            ]
            invoke = gate.find_invoke_edit(lines)
            expect(invoke is not None).to(be_true)
            expect(invoke["action"]).to(equal("satisfy"))
            expect(invoke["toolset"]).to(equal("context_tools.bdd.bdd:Bdd"))


with description("handle_post_tool_use (Read hook)"):
    with context("given a file with manifest lines"):
        with it("returns additional_context containing manifest and invoke output"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_input": {"path": path}}
            with patch.object(gate, "run_manifests", return_value=_FAKE_MANIFEST_OUTPUT):
                with patch.object(
                    gate, "run_invoke_edit", return_value=(True, _FAKE_INVOKE_OUTPUT)
                ):
                    result = gate.handle_post_tool_use(data)
            expect(result).to(have_key("additional_context"))
            expect(result["additional_context"]).to(contain("MANIFEST GATE"))
            expect(result["additional_context"]).to(contain(_FAKE_MANIFEST_OUTPUT))
            expect(result["additional_context"]).to(contain("invoke-edit"))
            expect(result).to(have_key("user_message"))
            expect(gate.is_cleared(path)).to(be_true)

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
            with patch.object(gate, "run_manifests", return_value=_FAKE_MANIFEST_OUTPUT):
                with patch.object(
                    gate, "run_invoke_edit", return_value=(True, _FAKE_INVOKE_OUTPUT)
                ):
                    result = gate.handle_post_tool_use(data)
            expect(result).to(have_key("additional_context"))
            expect(result["additional_context"]).to(contain("MANIFEST GATE"))
            expect(result).to(have_key("user_message"))


with description("handle_pre_tool_use (Write hook)"):
    with context("given an existing file with invoke-edit and no clearance"):
        with it("denies when invoke-edit cannot execute"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            # Ensure uncleared
            store = gate._load_clearance()
            store.pop(gate._norm_path(path), None)
            gate._save_clearance(store)
            data = {"tool_name": "Write", "tool_input": {"path": path, "contents": "x"}}
            with patch.object(gate, "run_manifests", return_value=_FAKE_MANIFEST_OUTPUT):
                with patch.object(
                    gate, "run_invoke_edit", return_value=(False, "timeout")
                ):
                    result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("deny"))
            expect(result["agent_message"]).to(contain("EDIT BLOCKED"))
            expect(result["user_message"]).to(contain("blocked"))

    with context("given an existing file with invoke-edit that executes on pre"):
        with it("allows and clears"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            store = gate._load_clearance()
            store.pop(gate._norm_path(path), None)
            gate._save_clearance(store)
            data = {"tool_name": "Write", "tool_input": {"path": path, "contents": "x"}}
            with patch.object(gate, "run_manifests", return_value=_FAKE_MANIFEST_OUTPUT):
                with patch.object(
                    gate, "run_invoke_edit", return_value=(True, _FAKE_INVOKE_OUTPUT)
                ):
                    result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect(gate.is_cleared(path)).to(be_true)

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
        with it("allows without requiring clearance"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            store = gate._load_clearance()
            store.pop(gate._norm_path(path), None)
            gate._save_clearance(store)
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
