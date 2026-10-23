"""BDD spec for MCP host JSON Schema binding of Python parameter types."""
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _path = str(_REPO_ROOT / _cat)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.installer import Installer
from harness.mcp._examples.parameter_types.parameter_types import ParameterTypes
from harness.mcp.mcp_server import HostPid, McpHost, McpInstallation
from cdd_guidance.actions.iterate.iterate import Iterate
from harness.guidance.fixtures.agentic_ops.agentic_ops import SampleMcpOps
from harness.mcp._examples.illegitimate_name.illegitimate_name import (
    IllegitimateName,
)
from space.session import Session


class JsonSchemaAnyOf:
    def sorted_types(self, schema: dict) -> list[str]:
        return sorted(variant["type"] for variant in schema["anyOf"])


with description("an MCP host input schema"):

    with before.each:
        self.host = McpHost.from_refs((), repo=str(_REPO_ROOT), project=str(_REPO_ROOT))

    with context("that has been derived from a ParameterTypes echo operation"):
        with before.each:
            self.schema = self.host.input_schema_for_callable(ParameterTypes().echo)
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

        with context("with a dict of unrestricted values parameter"):
            with it("should leave additionalProperties unrestricted"):
                schema = self.host.input_schema_for_callable(ParameterTypes().echo_open)
                expect(schema["properties"]["fields"]).to(
                    equal({"type": "object", "additionalProperties": {}})
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
                expect(JsonSchemaAnyOf().sorted_types(self.properties["optional_text"])).to(
                    equal(["null", "string"])
                )

        with context("with an optional integer parameter"):
            with it("should advertise anyOf integer and null"):
                expect(JsonSchemaAnyOf().sorted_types(self.properties["optional_count"])).to(
                    equal(["integer", "null"])
                )

        with context("with an optional boolean parameter"):
            with it("should advertise anyOf boolean and null"):
                expect(JsonSchemaAnyOf().sorted_types(self.properties["optional_flag"])).to(
                    equal(["boolean", "null"])
                )

        with context("with an optional float parameter"):
            with it("should advertise anyOf number and null"):
                expect(JsonSchemaAnyOf().sorted_types(self.properties["optional_ratio"])).to(
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
                expect(JsonSchemaAnyOf().sorted_types(self.properties["text_or_count"])).to(
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
                schema = self.host.input_schema_for_callable(ParameterTypes().echo_sequence)
                expect(schema["properties"]["value"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

    with context("that has been derived from a ParameterTypes echo_mapping operation"):
        with context("with a Mapping of integer values parameter"):
            with it("should advertise JSON Schema object with integer additionalProperties"):
                schema = self.host.input_schema_for_callable(ParameterTypes().echo_mapping)
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
                schema = self.host.input_schema_for_callable(ParameterTypes().echo_unannotated)
                expect(schema["properties"]["value"]).to(equal({"type": "string"}))

    with context("that has been derived from a ParameterTypes echo_record operation"):
        with context("with a named record parameter"):
            with it("should advertise the record fields and require toolset"):
                schema = self.host.input_schema_for_callable(ParameterTypes().echo_record)
                expect(schema["properties"]["record"]).to(
                    equal(
                        {
                            "type": "object",
                            "properties": {
                                "toolset": {"type": "string"},
                                "fidelity": {"type": "string"},
                            },
                            "required": ["toolset"],
                            "additionalProperties": False,
                        }
                    )
                )

    with context("that has been derived from generate.generate"):
        with context("with a guidance parameter"):
            with it("should advertise a toolset object instead of an open object"):
                from cdd_guidance.actions.generate.generate import Generate

                schema = self.host.input_schema_for_callable(Generate.generate)
                guidance = schema["properties"]["guidance"]
                object_form = next(
                    variant
                    for variant in guidance["anyOf"]
                    if variant.get("type") == "object" and "properties" in variant
                )
                expect(object_form).to(
                    equal(
                        {
                            "type": "object",
                            "properties": {
                                "toolset": {"type": "string"},
                                "fidelity": {"type": "string"},
                                "context": {
                                    "type": "object",
                                    "additionalProperties": {},
                                },
                            },
                            "required": ["toolset"],
                            "additionalProperties": False,
                        }
                    )
                )

    with context("that has been derived from iterate.iterate"):
        with context("with a tools list parameter"):
            with it("should advertise JSON Schema array of string"):
                schema = self.host.input_schema_for_callable(Iterate.iterate)
                expect(schema["properties"]["tools"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )


with description("an MCP host tool result") as self:
    with context("that is a named session"):
        with before.each:
            Session._current = None
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Session.new("alpha", self.work, self.repo)
            self.host = McpHost.from_refs((), repo=str(self.repo), project=str(self.repo))
            self.blocks = self.host._content_blocks(Session.current())
            self.payload = json.loads(self.blocks[0].text)

        with after.each:
            Session._current = None

        with it("should expose the session name as JSON"):
            expect(self.payload["name"]).to(equal("alpha"))

        with it("should expose practice root folder paths"):
            expect("stories" in self.payload["practice_roots"]).to(equal(True))
            expect(self.payload["practice_roots"]["stories"][0][0]).to(
                equal(str((self.work / "tests").resolve()))
            )


with description("an MCP host") as self:
    with context("that has stood up without a manifest file"):
        with before.each:
            self.host = McpHost.standup(Path("no-such-mcp.json"), repo=_REPO_ROOT)

        with it("should answer ping with pong"):
            expect(self.host.diagnose()["ping"]).to(equal("pong"))

        with it("should include the built-in health-check tool"):
            expect(self.host.diagnose()["tools"]).to(contain("cdd.ping"))

    with context("that has enrolled the repo toolset"):
        with before.each:
            self.host = McpHost.from_refs(
                ("space.repo.repo:Repo",),
                repo=str(_REPO_ROOT),
                project=str(_REPO_ROOT),
            )

        with it("should expose branch lifecycle and push_commit"):
            tools = self.host.diagnose()["tools"]
            expect(tools).to(contain("repo.branch"))
            expect(tools).to(contain("repo.worktree"))
            expect(tools).to(contain("repo.switch_branch"))
            expect(tools).to(contain("repo.new_branch"))
            expect(tools).to(contain("repo.close_branch"))
            expect(tools).to(contain("repo.push_commit"))
            expect("repo.push" in tools).to(equal(False))

        with it("should resolve Cursor underscore aliases to enrolled names"):
            expect(self.host._runtime.resolve_call_name("repo_push_commit")).to(
                equal("repo.push_commit")
            )

        with it("should run repo.new_branch through MCP dispatch"):
            result = self.host.dispatch(
                "repo.new_branch",
                {"name": "mcp-host-spec-branch", "switch": False},
            )
            expect(str(result)).to(contain("mcp-host-spec-branch"))

    with context("that has enrolled the session toolset"):
        with before.each:
            self.host = McpHost.from_refs(
                ("space.session.session:Session",),
                repo=str(_REPO_ROOT),
                project=str(_REPO_ROOT),
            )

        with it("should expose session.session and the open_named alias"):
            tools = self.host.diagnose()["tools"]
            expect(tools).to(contain("session.session"))
            expect(tools).to(contain("session.open_named"))

        with it("should resolve session_open_named to session.session"):
            expect(self.host._runtime.resolve_call_name("session_open_named")).to(
                equal("session.session")
            )

        with it("should run session.session with string repo_path"):
            result = self.host.dispatch(
                "session.session",
                {
                    "name": "mcp-host-spec-session",
                    "repo_path": str(_REPO_ROOT),
                },
            )
            expect(str(result)).not_to(equal(""))

    with context("that has stood up with a published tool whose MCP name is illegitimate"):
        with before.each:
            self.host = McpHost.from_refs(
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
            self.host = McpHost.from_refs(
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

        with it("should enroll published operations by collecting the repo"):
            expect(self.host.diagnose()["tools"]).to(contain("generate.generate"))

        with it("should not bake toolset refs into mcp.json"):
            expect(self.host.refs_from_manifest(self.tree / "mcp.json")).to(equal(()))


with description("an MCP host tool ping") as self:
    with before.each:
        self.host = McpHost.from_refs(
            ("harness.mcp._examples.hosting_demo.hosting_demo:HostingDemo",),
            repo=str(_REPO_ROOT),
            project=str(_REPO_ROOT),
        )

    with it("should answer ping for an enrolled tool without running it"):
        reply = self.host.dispatch(
            "hosting-demo.increment", {"ping": True, "step": 5}
        )
        expect(reply).to(equal({"ping": "pong", "tool": "hosting-demo.increment"}))
        expect(self.host.dispatch("hosting-demo.read_count", {})).to(equal(0))

    with it("should leave ping out of the tool schema"):
        schema = self.host.input_schema_for_callable(
            self.host._runtime.tools["hosting-demo.increment"].callable
        )
        expect("ping" in schema["properties"]).to(equal(False))

    with it("should still run a tool when ping is absent"):
        expect(self.host.dispatch("hosting-demo.increment", {"step": 1})).to(equal(1))


with description("an MCP host Cursor has stopped spawning") as self:
    with before.each:
        self._user_mcp = Path.home() / ".cursor" / "mcp.json"
        self._user_mcp_before = (
            self._user_mcp.read_text(encoding="utf-8") if self._user_mcp.is_file() else None
        )
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Installer(ide="Cursor", path=self.tree, repo=_REPO_ROOT).install([SampleMcpOps()])
        self.mcp = McpInstallation("Cursor", self.tree, repo=_REPO_ROOT)
        nudge = self.tree / "mcp-host-nudge"
        if nudge.is_file():
            nudge.unlink()

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with no live host process"):
        with it("should rewrite mcp.json so Cursor respawns stdio"):
            expect(self.mcp.ensure_cursor_host()).to(equal("nudged"))

        with it("should bump the project mcp.json Cursor reads from the repo"):
            self.mcp.ensure_cursor_host()
            expect((self.tree / "mcp.json").read_text(encoding="utf-8")).to(
                contain("CDD_HOST_NUDGE")
            )

        with it("should leave the user Cursor mcp.json unchanged"):
            self.mcp.ensure_cursor_host()
            after = (
                self._user_mcp.read_text(encoding="utf-8")
                if self._user_mcp.is_file()
                else None
            )
            expect(after).to(equal(self._user_mcp_before))

    with context("with a live host process"):
        with before.each:
            (self.tree / "mcp-host.pid").write_text(str(os.getpid()), encoding="utf-8")

        with it("should leave the running host alone"):
            expect(self.mcp.ensure_cursor_host()).to(equal("running"))


with description("the MCP host pid file") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that names the process reading it"):
        with before.each:
            (self.tree / "mcp-host.pid").write_text(str(os.getpid()), encoding="utf-8")

        with it("should report that reader as the host itself"):
            expect(HostPid.from_ide(self.tree).is_this_process).to(equal(True))

    with context("that names a different process"):
        with before.each:
            (self.tree / "mcp-host.pid").write_text(str(os.getppid()), encoding="utf-8")

        with it("should report the reader as a process other than the host"):
            expect(HostPid.from_ide(self.tree).is_this_process).to(equal(False))

    with context("that already names a live host when another host claims it"):
        with before.each:
            (self.tree / "mcp-host.pid").write_text(str(os.getppid()), encoding="utf-8")
            HostPid.from_ide(self.tree).claim()

        with after.each:
            os.environ.pop("CDD_MCP_HOST_PID", None)

        with it("should keep naming the host that was already serving"):
            recorded = (self.tree / "mcp-host.pid").read_text(encoding="utf-8").strip()
            expect(recorded).to(equal(str(os.getppid())))

    with context("that a sibling host has deleted after this process claimed it"):
        with before.each:
            self.host_pid = HostPid.from_ide(self.tree)
            self.host_pid.claim()
            (self.tree / "mcp-host.pid").unlink()

        with after.each:
            os.environ.pop("CDD_MCP_HOST_PID", None)

        with it("should still report the claiming process as the host itself"):
            expect(self.host_pid.is_this_process).to(equal(True))

    with context("that claimed the host after a sibling deleted its pid file"):
        with before.each:
            self.mcp = McpInstallation("Cursor", self.tree, repo=_REPO_ROOT)
            HostPid.from_ide(self.tree).claim()
            (self.tree / "mcp-host.pid").unlink()

        with after.each:
            os.environ.pop("CDD_MCP_HOST_PID", None)

        with it("should report the MCP host as running for install standup"):
            expect(self.mcp.cursor_host_is_running()).to(equal(True))

