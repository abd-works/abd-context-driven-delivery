"""BDD spec for MCP host JSON Schema of Python parameter types."""
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

from expects import contain, equal, expect, raise_error
from mamba import after, before, context, description, it

from harness.agent_tools.parameter_schema import ParameterSchema
from harness.installation.installer import Installer
from harness.mcp._examples.parameter_types.parameter_types import ParameterTypes
from harness.mcp.cdd_home import CddHome
from harness.mcp.mcp_daemon import McpDaemon
from harness.mcp.mcp_server import McpHost, McpInstallation
from harness.mcp.spec_support import UserHome
from harness.graph.graph import Graph
from harness.guidance.fixtures.agentic_ops.agentic_ops import SampleMcpOps
from harness.mcp._examples.illegitimate_name.illegitimate_name import (
    IllegitimateName,
)
from harness.installation.ide_layout import IdeLayout
from space.repo.repo import Commit, DefaultBranchError
from space.session import Sessions
from space.work_state import WorkState


def _moved(stage: "str", done: "bool" = False) -> "ImportedOnlyForTypeChecking":
    """An operation whose return type names a class its module imports only for type checking, as a circular import
    needs, in a module whose annotations are text (`from __future__ import annotations`)."""


class JsonSchemaAnyOf:
    def sorted_types(self, schema: dict) -> list[str]:
        return sorted(variant["type"] for variant in schema["anyOf"])


with description("an MCP host input schema"):

    with before.each:
        self.host = McpHost.from_refs((), repo=str(_REPO_ROOT), project=str(_REPO_ROOT))

    with context("that has been derived from an operation whose return type cannot be resolved"):
        with it("should still advertise its boolean parameter as JSON Schema boolean"):
            expect(ParameterSchema(_moved).json_schema["properties"]["done"]).to(equal({"type": "boolean"}))

    with context("that has been derived from a ParameterTypes echo operation"):
        with before.each:
            self.schema = ParameterSchema(ParameterTypes().echo).json_schema
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
                schema = ParameterSchema(ParameterTypes().echo_open).json_schema
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
                schema = ParameterSchema(ParameterTypes().echo_sequence).json_schema
                expect(schema["properties"]["value"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )

    with context("that has been derived from a ParameterTypes echo_mapping operation"):
        with context("with a Mapping of integer values parameter"):
            with it("should advertise JSON Schema object with integer additionalProperties"):
                schema = ParameterSchema(ParameterTypes().echo_mapping).json_schema
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
                schema = ParameterSchema(ParameterTypes().echo_unannotated).json_schema
                expect(schema["properties"]["value"]).to(equal({"type": "string"}))

    with context("that has been derived from a ParameterTypes echo_record operation"):
        with context("with a named record parameter"):
            with it("should advertise the record fields and require toolset"):
                schema = ParameterSchema(ParameterTypes().echo_record).json_schema
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

                schema = ParameterSchema(Generate.generate).json_schema
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

    with context("that has been derived from the graph's set_overlays operation"):
        with context("with an overlays list parameter"):
            with it("should advertise JSON Schema array of string"):
                schema = ParameterSchema(Graph.set_overlays).json_schema
                expect(schema["properties"]["overlays"]).to(
                    equal({"type": "array", "items": {"type": "string"}})
                )


with description("an MCP host tool result") as self:
    with context("that is a named session"):
        with before.each:
            self.repo = Path(tempfile.mkdtemp())
            self.work = self.repo / "work"
            self.work.mkdir()
            Sessions(self.repo).switch("alpha", self.work)
            self.host = McpHost.from_refs((), repo=str(self.repo), project=str(self.repo))
            self.blocks = self.host._content_blocks(Sessions(self.repo).current())
            self.payload = json.loads(self.blocks[0].text)

        with after.each:
            shutil.rmtree(self.repo, ignore_errors=True)

        with it("should expose the session name as JSON"):
            expect(self.payload["name"]).to(equal("alpha"))

        with it("should expose each practice's root folder as a path from the project"):
            expect(self.payload["practices"]["stories"]["root"]).to(equal("work/tests"))

    with context("that is a commit"):
        with before.each:
            self.host = McpHost.from_refs((), repo=str(_REPO_ROOT), project=str(_REPO_ROOT))
            commit = Commit("abc123", "push: checkpoint\nReviewed-By: human")
            self.payload = json.loads(self.host._content_blocks(commit)[0].text)

        with it("should expose the commit sha as JSON"):
            expect(self.payload["sha"]).to(equal("abc123"))

        with it("should expose the commit subject as JSON"):
            expect(self.payload["subject"]).to(equal("push: checkpoint"))

        with it("should expose the full commit message as JSON"):
            expect(self.payload["message"]).to(equal("push: checkpoint\nReviewed-By: human"))

        with it("should expose the commit trailers as JSON"):
            expect(self.payload["trailers"]).to(equal({"Reviewed-By": "human"}))


with description("an MCP host") as self:
    with context("that has stood up over this checkout's toolsets"):
        with before.each:
            self.host = McpHost.from_repo(_REPO_ROOT)

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
            expect(tools).to(contain("repo.switch_branch"))
            expect(tools).to(contain("repo.close_branch"))
            expect(tools).to(contain("repo.switch_worktree"))
            expect(tools).to(contain("repo.close_worktree"))
            expect(tools).to(contain("repo.push_commit"))
            expect("repo.push" in tools).to(equal(False))

        with it("should resolve Cursor underscore aliases to enrolled names"):
            expect(self.host.checkout_server.resolve_call_name("repo_push_commit")).to(
                equal("repo.push_commit")
            )

        with it("should refuse repo.close_branch on main through MCP dispatch"):
            expect(
                lambda: self.host.dispatch("repo.close_branch", {"name": "main"})
            ).to(raise_error(DefaultBranchError))

    with context("that has enrolled the sessions toolset on a project"):
        with before.each:
            self.project = Path(tempfile.mkdtemp())
            self.host = McpHost.from_refs(
                ("space.session.sessions:Sessions",),
                repo=str(_REPO_ROOT),
                project=str(self.project),
            )

        with after.each:
            shutil.rmtree(self.project, ignore_errors=True)

        with it("should expose sessions.switch as the one way to open a session"):
            tools = self.host.diagnose()["tools"]
            expect(tools).to(contain("sessions.switch"))

        with it("should open the named session in that project through sessions.switch"):
            self.host.dispatch("sessions.switch", {"name": "mcp-host-spec-session"}, project=self.project)
            expect(WorkState(self.project).session).to(equal("mcp-host-spec-session"))

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
            expect(self.host.diagnose()["tools"]).not_to(contain("illegitimate-name.résumé"))

        with it("should diagnose the skipped tool as an exception"):
            expect(self.host.diagnose()["exceptions"][0]["tool"]).to(
                equal("illegitimate-name.résumé")
            )

        with it("should keep a chat notice naming the skipped tool"):
            expect(self.host.diagnose()["notice"]).to(contain("illegitimate-name.résumé"))

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
            self.host = McpHost.from_repo(_REPO_ROOT)

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should enroll published operations by collecting the repo"):
            expect(self.host.diagnose()["tools"]).to(contain("generate.generate"))

        with it("should name the server by its URL, with no command or toolsets to start"):
            entry = json.loads((self.tree / "mcp.json").read_text(encoding="utf-8"))["mcpServers"]["cdd"]
            expect(sorted(entry)).to(equal(["headers", "url"]))

    with context("that is serving two projects"):
        with before.each:
            self.host = McpHost.from_refs(
                ("harness.mcp._examples.hosting_demo.hosting_demo:HostingDemo",),
                repo=str(_REPO_ROOT),
                project=str(_REPO_ROOT),
            )
            self.first = Path(tempfile.mkdtemp(prefix="mcp-host-first-"))
            self.second = Path(tempfile.mkdtemp(prefix="mcp-host-second-"))
            self.host.dispatch("hosting-demo.increment", {"step": 3}, self.first)

        with after.each:
            shutil.rmtree(self.first, ignore_errors=True)
            shutil.rmtree(self.second, ignore_errors=True)

        with it("should keep one project's toolset state for that project"):
            expect(self.host.dispatch("hosting-demo.read_count", {}, self.first)).to(equal(3))

        with it("should start the other project's toolsets fresh"):
            expect(self.host.dispatch("hosting-demo.read_count", {}, self.second)).to(equal(0))

        with context("that has been restarted"):
            with before.each:
                self.host.dispatch("cdd.restart", {})

            with it("should start every project's toolsets again on the code as it is now"):
                expect(self.host.dispatch("hosting-demo.read_count", {}, self.first)).to(equal(0))


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
        schema = self.host.checkout_server.tools["hosting-demo.increment"].input_schema
        expect("ping" in schema["properties"]).to(equal(False))

    with it("should still run a tool when ping is absent"):
        expect(self.host.dispatch("hosting-demo.increment", {"step": 1})).to(equal(1))


def _user_level_installation(ide: str) -> McpInstallation:
    installation = McpInstallation(IdeLayout(ide), _REPO_ROOT / ".cursor", repo=_REPO_ROOT)
    installation._is_temp_path = lambda path: False
    for tool in SampleMcpOps().tools.values():
        installation.record_operation(tool)
    return installation


with description("an MCP install that deploys to the IDE's user-level config") as self:
    with before.each:
        self.home = UserHome()
        self.root = self.home.enter()

    with after.each:
        self.home.leave()

    with context("for Cursor"):
        with before.each:
            self.config = self.root / ".cursor" / "mcp.json"
            self.config.parent.mkdir(parents=True)
            self.config.write_text(json.dumps({"mcpServers": {"miro-mcp": {"url": "https://example"}}}), encoding="utf-8")
            self.installation = _user_level_installation("Cursor")
            self.installation.write_mcp_manifest()
            self.servers = json.loads(self.config.read_text(encoding="utf-8"))["mcpServers"]

        with it("should write the cdd server into ~/.cursor/mcp.json"):
            expect(self.installation.manifest_path).to(equal(self.config))
            expect("cdd" in self.servers).to(equal(True))

        with it("should keep the user's other servers"):
            expect("miro-mcp" in self.servers).to(equal(True))

        with it("should point at the one cdd server"):
            expect(self.servers["cdd"]["url"]).to(equal(McpDaemon(CddHome()).url))

        with it("should name the open project on every request"):
            expect(self.servers["cdd"]["headers"]).to(equal({"X-CDD-Project": "${workspaceFolder}"}))

    with context("for Claude Code"):
        with before.each:
            self.config = self.root / ".claude.json"
            old_entry = {"type": "http", "url": McpDaemon(CddHome()).url, "headersHelper": "python connect.py"}
            self.config.write_text(
                json.dumps({"projects": {"x": {}}, "mcpServers": {"cdd": old_entry, "miro-mcp": {"url": "https://example"}}}),
                encoding="utf-8",
            )
            self.installation = _user_level_installation("Claude")
            self.installation.write_mcp_manifest()
            self.data = json.loads(self.config.read_text(encoding="utf-8"))
            self.plugin = self.root / ".cdd" / "claude-plugins"
            self.server = json.loads((self.plugin / "cdd" / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["cdd"]

        with it("should take the cdd server out of ~/.claude.json, where every chat would name ~/.claude"):
            expect("cdd" in self.data["mcpServers"]).to(equal(False))

        with it("should keep the user's other servers in that file"):
            expect("miro-mcp" in self.data["mcpServers"]).to(equal(True))

        with it("should keep Claude Code's own state in that file"):
            expect(self.data["projects"]).to(equal({"x": {}}))

        with it("should list the cdd plugin in the marketplace under ~/.cdd"):
            marketplace = json.loads((self.plugin / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
            expect([plugin["name"] for plugin in marketplace["plugins"]]).to(equal(["cdd"]))

        with it("should point the plugin's cdd server at the one cdd server over HTTP"):
            expect(self.server["url"]).to(equal(McpDaemon(CddHome()).url))

        with it("should run the connect script in ~/.cdd"):
            expect(self.server["headersHelper"]).to(contain(str(self.root / ".cdd" / "connect.py")))

        with it("should pass the chat's folder to the connect script"):
            expect(self.server["headersHelper"]).to(contain('"${CLAUDE_PROJECT_DIR}"'))

        with context("that is installed again from another checkout"):
            with before.each:
                self.written = self.config.read_text(encoding="utf-8")
                again = McpInstallation(IdeLayout("Claude"), self.root / "other" / ".claude", repo=self.root / "other")
                again._is_temp_path = lambda path: False
                for tool in SampleMcpOps().tools.values():
                    again.record_operation(tool)
                again.write_mcp_manifest()

            with it("should leave ~/.claude.json as it was, so open chats keep their connection"):
                expect(self.config.read_text(encoding="utf-8")).to(equal(self.written))

        with context("with a cdd server in the project's .mcp.json"):
            with before.each:
                self.project = self.root / "project"
                (self.project / ".claude").mkdir(parents=True)
                self.project_config = self.project / ".mcp.json"
                self.installation = McpInstallation(IdeLayout("Claude"), self.project / ".claude", repo=_REPO_ROOT)
                self.installation._is_temp_path = lambda path: False
                for tool in SampleMcpOps().tools.values():
                    self.installation.record_operation(tool)

            with it("should remove the file when cdd was its only server"):
                self.project_config.write_text(json.dumps({"mcpServers": {"cdd": {}}}), encoding="utf-8")
                self.installation.write_mcp_manifest()
                expect(self.project_config.exists()).to(equal(False))

            with it("should keep the project's other servers"):
                self.project_config.write_text(
                    json.dumps({"mcpServers": {"cdd": {}, "other": {"command": "other"}}}), encoding="utf-8"
                )
                self.installation.write_mcp_manifest()
                saved = json.loads(self.project_config.read_text(encoding="utf-8"))
                expect(saved).to(equal({"mcpServers": {"other": {"command": "other"}}}))

        with it("should allow the cdd tools in ~/.claude/settings.json"):
            settings = json.loads((self.root / ".claude" / "settings.json").read_text(encoding="utf-8"))
            expect(settings["permissions"]["allow"]).to(equal(["mcp__plugin_cdd_cdd"]))

        with context("with settings the user already has"):
            with before.each:
                self.settings = self.root / ".claude" / "settings.json"
                self.settings.write_text(
                    json.dumps({"model": "x", "permissions": {"allow": ["Read", "mcp__plugin_cdd_cdd"]}}), encoding="utf-8"
                )
                self.installation.write_mcp_manifest()
                self.saved = json.loads(self.settings.read_text(encoding="utf-8"))

            with it("should keep the user's settings and not repeat the entry"):
                expect(self.saved).to(equal({"model": "x", "permissions": {"allow": ["Read", "mcp__plugin_cdd_cdd"]}}))

    with context("for VS Code"):
        with before.each:
            self.installation = _user_level_installation("VS Code")
            self.installation.write_mcp_manifest()
            self.config = self.root / "AppData" / "Roaming" / "Code" / "User" / "mcp.json"
            if sys.platform == "darwin":
                self.config = self.root / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
            elif sys.platform != "win32":
                self.config = Path(os.environ.get("XDG_CONFIG_HOME") or self.root / ".config") / "Code" / "User" / "mcp.json"

        with it("should write the cdd server under servers in the user mcp.json"):
            expect(self.installation.manifest_path).to(equal(self.config))
            servers = json.loads(self.config.read_text(encoding="utf-8"))["servers"]
            expect(servers["cdd"]["headers"]).to(equal({"X-CDD-Project": "${workspaceFolder}"}))

    with context("into a temp install tree"):
        with before.each:
            self.tree = Path(tempfile.mkdtemp())
            self.installation = McpInstallation(IdeLayout("Cursor"), self.tree, repo=_REPO_ROOT)
            for tool in SampleMcpOps().tools.values():
                self.installation.record_operation(tool)
            self.installation.write_mcp_manifest()

        with after.each:
            shutil.rmtree(self.tree, ignore_errors=True)

        with it("should keep mcp.json in that tree"):
            expect(self.installation.manifest_path).to(equal(self.tree / "mcp.json"))

        with it("should name that tree as the project"):
            entry = json.loads((self.tree / "mcp.json").read_text(encoding="utf-8"))["mcpServers"]["cdd"]
            expect(entry["headers"]).to(equal({"X-CDD-Project": str(self.tree.resolve())}))
