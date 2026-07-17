"""BDD spec for manifest-gate hook — scan, run manifests, dispatch to post/pre handlers."""

import io
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_empty, be_true, contain, equal, expect, have_key
from mamba import before, context, description, it

import hooks.manifest_gate as gate


_MANIFEST_FILE = """\
# @toolset-manifest python -m tools manifest ooad.ooad:Ooad
# Agent reading this file: run line 1 manifest, then follow instructions.
# invoke-edit: action satisfy | toolset: bdd.bdd:Bdd
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
        with it("returns additional_context containing manifest output"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_input": {"path": path}}
            with patch.object(gate, "run_manifests", return_value=_FAKE_MANIFEST_OUTPUT):
                result = gate.handle_post_tool_use(data)
            expect(result).to(have_key("additional_context"))
            expect(result["additional_context"]).to(contain("MANIFEST GATE"))
            expect(result["additional_context"]).to(contain(_FAKE_MANIFEST_OUTPUT))

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
                result = gate.handle_post_tool_use(data)
            expect(result).to(have_key("additional_context"))
            expect(result["additional_context"]).to(contain("MANIFEST GATE"))


with description("handle_pre_tool_use (Write hook)"):
    with context("given an existing file with manifest lines"):
        with it("returns permission allow with agent_message containing manifest output"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_MANIFEST_FILE)
                path = f.name
            data = {"tool_input": {"path": path}}
            with patch.object(gate, "run_manifests", return_value=_FAKE_MANIFEST_OUTPUT):
                result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect(result).to(have_key("agent_message"))
            expect(result["agent_message"]).to(contain("MANIFEST GATE"))
            expect(result["agent_message"]).to(contain(_FAKE_MANIFEST_OUTPUT))

    with context("given a file that does not exist (new file creation)"):
        with it("returns permission allow with no agent_message"):
            data = {"tool_input": {"path": "/does/not/exist.py"}}
            result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect("agent_message" not in result).to(be_true)

    with context("given an existing file with no manifest lines"):
        with it("returns permission allow with no agent_message"):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(_PLAIN_FILE)
                path = f.name
            data = {"tool_input": {"path": path}}
            result = gate.handle_pre_tool_use(data)
            expect(result["permission"]).to(equal("allow"))
            expect("agent_message" not in result).to(be_true)


with description("parse_hook_payload — double-BOM regression"):
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
