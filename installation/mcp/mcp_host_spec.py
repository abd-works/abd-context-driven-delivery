"""BDD spec for MCP host JSON Schema binding of Python parameter types."""
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "practices", "actions", "harness"):
    _path = str(_REPO_ROOT / _cat)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from installation.installer import Installer
from installation.mcp.examples.parameter_types.parameter_types import ParameterTypes
from installation.mcp.mcp_server import McpHost, McpInstallation
from actions.iterate.iterate import Iterate
from harness.guidance.fixtures.agentic_ops.agentic_ops import SampleMcpOps
from installation.mcp.examples.illegitimate_name.illegitimate_name import (
    IllegitimateName,
)


def _sorted_any_of_types(schema: dict) -> list[str]:
    return sorted(variant["type"] for variant in schema["anyOf"])


with description("an MCP host input schema"):

    with context("that has been derived from a ParameterTypes echo operation"):
        with before.each:
            self.schema = McpHost.input_schema_for_callable(ParameterTypes().echo)
            self.properties = self.schema["properties"]

        with context("with a string parameter"):
            with it("should advertise JSON Schema string"):
                expect(self.properties["text"]).to(equal({"type": "string"}))

        with context("with an integer parameter"):
            with it("should advertise JSON Schema integer"):
                expect(self.properties["count"]).to(equal({"type": "integer"}))

        with context("with a float parameter"):
            with it("should advertise JSON Schema number"):
                expect(self.properties["ratio"]).to(equal({"type": "number"}))

        with context("with a boolean parameter"):
            with it("should advertise JSON Schema boolean"):
                expect(self.properties["flag"]).to(equal({"type": "boolean"}))

        with context("with a list of strings parameter"):
            with it("should advertise JSON Schema array of string"):
                expect(self.properties["items"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

        with context("with a dict of string values parameter"):
            with it("should advertise JSON Schema object with string additionalProperties"):
                expect(self.properties["fields"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {"type": "string"},
                        }
                    )
                )

        with context("with an untyped list parameter"):
            with it("should advertise JSON Schema array of string"):
                expect(self.properties["untyped_items"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

        with context("with an untyped dict parameter"):
            with it("should advertise JSON Schema object"):
                expect(self.properties["untyped_fields"]).to(equal({"type": "object"}))

        with context("with a list of integers parameter"):
            with it("should advertise JSON Schema array of integer"):
                expect(self.properties["counted_items"]).to(
                    equal({"type": "array", "items": {"type": "integer"}})
                )

        with context("with a list of booleans parameter"):
            with it("should advertise JSON Schema array of boolean"):
                expect(self.properties["flagged_items"]).to(
                    equal({"type": "array", "items": {"type": "boolean"}})
                )

        with context("with a list of floats parameter"):
            with it("should advertise JSON Schema array of number"):
                expect(self.properties["measured_items"]).to(
                    equal({"type": "array", "items": {"type": "number"}})
                )

        with context("with a nested list parameter"):
            with it("should advertise JSON Schema array of array of string"):
                expect(self.properties["nested_items"]).to(
                    equal(
                        {
                            "type": "array",
                            "items": {"type": "array", "items": {"type": "string"}},
                        }
                    )
                )

        with context("with a list of dicts parameter"):
            with it("should advertise JSON Schema array of object with string additionalProperties"):
                expect(self.properties["record_items"]).to(
                    equal(
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                            },
                        }
                    )
                )

        with context("with a dict of integer values parameter"):
            with it("should advertise JSON Schema object with integer additionalProperties"):
                expect(self.properties["counted_fields"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        }
                    )
                )

        with context("with a dict of list values parameter"):
            with it("should advertise JSON Schema object with array additionalProperties"):
                expect(self.properties["listed_fields"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {
                                "type": "array",
                                "items": {"type": "integer"},
                            },
                        }
                    )
                )

        with context("with an optional string parameter"):
            with it("should advertise anyOf string and null"):
                expect(_sorted_any_of_types(self.properties["optional_text"])).to(
                    equal(["null", "string"])
                )

        with context("with an optional integer parameter"):
            with it("should advertise anyOf integer and null"):
                expect(_sorted_any_of_types(self.properties["optional_count"])).to(
                    equal(["integer", "null"])
                )

        with context("with an optional boolean parameter"):
            with it("should advertise anyOf boolean and null"):
                expect(_sorted_any_of_types(self.properties["optional_flag"])).to(
                    equal(["boolean", "null"])
                )

        with context("with an optional float parameter"):
            with it("should advertise anyOf number and null"):
                expect(_sorted_any_of_types(self.properties["optional_ratio"])).to(
                    equal(["null", "number"])
                )

        with context("with an optional list parameter"):
            with it("should advertise anyOf array and null"):
                expect(
                    sorted(
                        variant["type"]
                        for variant in self.properties["optional_items"]["anyOf"]
                    )
                ).to(equal(["array", "null"]))

        with context("with an optional dict parameter"):
            with it("should advertise anyOf object and null"):
                expect(
                    sorted(
                        variant["type"]
                        for variant in self.properties["optional_fields"]["anyOf"]
                    )
                ).to(equal(["null", "object"]))

        with context("with a string-or-integer union parameter"):
            with it("should advertise anyOf string and integer"):
                expect(_sorted_any_of_types(self.properties["text_or_count"])).to(
                    equal(["integer", "string"])
                )

        with context("with optional parameters that have defaults"):
            with it("should omit optional_text from required"):
                expect("optional_text" in self.schema["required"]).to(equal(False))

            with it("should still require text"):
                expect(self.schema["required"]).to(contain("text"))

            with it("should still require items"):
                expect(self.schema["required"]).to(contain("items"))

            with it("should still require fields"):
                expect(self.schema["required"]).to(contain("fields"))

            with it("should still require flag"):
                expect(self.schema["required"]).to(contain("flag"))

    with context("that has been derived from a ParameterTypes echo_sequence operation"):
        with context("with a Sequence of strings parameter"):
            with it("should advertise JSON Schema array of string"):
                schema = McpHost.input_schema_for_callable(ParameterTypes().echo_sequence)
                expect(schema["properties"]["value"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

    with context("that has been derived from a ParameterTypes echo_mapping operation"):
        with context("with a Mapping of integer values parameter"):
            with it("should advertise JSON Schema object with integer additionalProperties"):
                schema = McpHost.input_schema_for_callable(ParameterTypes().echo_mapping)
                expect(schema["properties"]["value"]).to(
                    equal(
                        {
                            "type": "object",
                            "additionalProperties": {"type": "integer"},
                        }
                    )
                )

    with context("that has been derived from a ParameterTypes echo_unannotated operation"):
        with context("with an unannotated parameter"):
            with it("should advertise JSON Schema string"):
                schema = McpHost.input_schema_for_callable(ParameterTypes().echo_unannotated)
                expect(schema["properties"]["value"]).to(equal({"type": "string"}))

    with context("that has been derived from iterate.iterate"):
        with context("with a tools list parameter"):
            with it("should advertise JSON Schema array of string"):
                schema = McpHost.input_schema_for_callable(Iterate.iterate)
                expect(schema["properties"]["tools"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )


with description("an MCP host") as self:
    with context("that has stood up without a manifest file"):
        with before.each:
            self.host = McpHost.standup(Path("no-such-mcp.json"), repo=_REPO_ROOT)

        with it("should answer ping with pong"):
            expect(self.host.diagnose()["ping"]).to(equal("pong"))

        with it("should include the built-in health-check tool"):
            expect(self.host.diagnose()["tools"]).to(contain("cdd.ping"))

    with context("that has enrolled a turn toolset"):
        with before.each:
            self.host = McpHost.build(
                ("tools.workspace.workspace:Turn",),
                repo=str(_REPO_ROOT),
                project=str(_REPO_ROOT),
            )

        with it("should name the turn operation turn.turn"):
            expect(self.host.diagnose()["tools"]).to(contain("turn.turn"))

        with it("should resolve Cursor underscore aliases to enrolled names"):
            expect(self.host._runtime.resolve_call_name("turn_turn")).to(equal("turn.turn"))

        with it("should advertise MCP tool names Cursor can load"):
            illegal = [
                name
                for name in self.host.diagnose()["tools"]
                if re.fullmatch(r"[A-Za-z0-9_.-]+", name) is None
            ]
            expect(illegal).to(equal([]))

    with context("that has stood up with a published tool whose MCP name is illegitimate"):
        with before.each:
            self.host = McpHost.build(
                (IllegitimateName().registration_name,),
                repo=str(_REPO_ROOT),
                project=str(_REPO_ROOT),
            )

        with it("should still answer ping"):
            expect(self.host.diagnose()["ping"]).to(equal("pong"))

        with it("should omit that tool from advertised tools"):
            expect(self.host.diagnose()["tools"]).not_to(contain("bad name.report"))

        with it("should diagnose the skipped tool as an exception"):
            expect(self.host.diagnose()["exceptions"][0]["tool"]).to(
                equal("bad name.report")
            )

        with it("should keep a chat notice naming the skipped tool"):
            expect(self.host.diagnose()["notice"]).to(contain("bad name.report"))

    with context("that has stood up with a toolset that cannot be loaded"):
        with before.each:
            self.host = McpHost.build(
                (
                    "missing.module:Nope",
                    "harness.guidance.fixtures.agentic_ops.agentic_ops:SampleMcpOps",
                ),
                repo=str(_REPO_ROOT),
                project=str(_REPO_ROOT),
            )

        with it("should still enroll the loadable published operation"):
            expect(self.host.diagnose()["tools"]).to(contain("sample-mcp.generate"))

        with it("should diagnose the skipped toolset as an exception"):
            expect(self.host.diagnose()["exceptions"][0]["tool"]).to(
                equal("missing.module:Nope")
            )

    with context("that has stood up from a written mcp.json"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install([SampleMcpOps()])
            self.host = McpHost.standup(self.tree / "mcp.json", repo=_REPO_ROOT)

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should enroll a published operation from the manifest"):
            expect(self.host.diagnose()["tools"]).to(contain("sample-mcp.generate"))

        with it("should read toolset refs from the written mcp.json"):
            expect(McpHost.refs_from_manifest(self.tree / "mcp.json")).to(
                contain("harness.guidance.fixtures.agentic_ops.agentic_ops:SampleMcpOps")
            )


with description("an MCP host Cursor has stopped spawning") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install([SampleMcpOps()])
        self.mcp = McpInstallation("Cursor", self.tree, repo=_REPO_ROOT)
        nudge = self.tree / "mcp-host-nudge"
        if nudge.is_file():
            nudge.unlink()
        import installation.mcp.mcp_server as mcp_mod

        self._mcp_mod = mcp_mod
        user_mcp = self.tree / "user-mcp.json"
        user_mcp.write_text("{}", encoding="utf-8")
        self._user_mcp = user_mcp
        self._orig_user_mcp = mcp_mod.user_cursor_mcp_json
        mcp_mod.user_cursor_mcp_json = lambda: user_mcp

    with after.each:
        self._mcp_mod.user_cursor_mcp_json = self._orig_user_mcp
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with no live host process"):
        with it("should rewrite mcp.json so Cursor respawns stdio"):
            expect(self.mcp.ensure_cursor_host()).to(equal("nudged"))

        with it("should rewrite the user Cursor mcp.json that owns stdio"):
            self._user_mcp.write_text(
                '{"mcpServers":{"cdd":{"args":["start_host.py"],"env":{}}}}\n',
                encoding="utf-8",
            )
            (self.tree / "mcp-host-nudge").unlink(missing_ok=True)
            expect(self.mcp.ensure_cursor_host()).to(equal("nudged"))
            expect(self._user_mcp.read_text(encoding="utf-8")).to(contain("CDD_HOST_NUDGE"))

    with context("with a live host process"):
        with before.each:
            (self.tree / "mcp-host.pid").write_text(str(os.getpid()), encoding="utf-8")

        with it("should leave the running host alone"):
            expect(self.mcp.ensure_cursor_host()).to(equal("running"))

