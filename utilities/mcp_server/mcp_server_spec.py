# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""BDD spec for utilities/mcp_server/mcp_server.py."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect, raise_error
from mamba import before, context, description, it

from mcp_server import McpPrompt, McpServer, McpTool, McpToolset
from mcp_server.examples.hosting_demo.hosting_demo import HostingDemo

def _build_server() -> McpServer:
    return McpServer()

with description("an MCP tool"):
    with context("that is discovered from an @agent_tool on a toolset instance"):
        with before.each:
            self.instance = HostingDemo()

        with it("should derive its mcp_name from the toolset name and method name"):
            tool = McpTool(self.instance.increment)
            expect(tool.mcp_name).to(equal("hosting_demo.increment"))

        with it("should keep underscores inside the method name"):
            tool = McpTool(self.instance.read_count)
            expect(tool.mcp_name).to(equal("hosting_demo.read_count"))

        with it("should reject an undecorated method"):
            expect(lambda: McpTool(self.instance._ordinary_helper)).to(raise_error(TypeError))

        with it("should return the operation result when invoked"):
            tool = McpTool(self.instance.increment)
            expect(tool.invoke({"step": 3})).to(equal(3))

        with it("should advertise invocable parameters for an operation that declares them"):
            tool = McpTool(self.instance.increment)
            expect("step" in tool.invocable_parameters()).to(equal(True))

        with context("with an operation that declares no invocable parameters"):
            with it("should advertise an empty parameter list"):
                tool = McpTool(self.instance.read_count)
                expect(tool.invocable_parameters()).to(equal(()))

with description("an MCP prompt"):
    with context("that is discovered from an @instruction on a toolset instance"):
        with before.each:
            self.instance = HostingDemo()

        with it("should expose prompt text from the method docstring"):
            prompt = McpPrompt(self.instance.plan_work)
            expect(prompt.prompt_text).to(contain("Think about the concept"))

        with it("should list @agent_tool names referenced by tool(...) in the orchestration body"):
            prompt = McpPrompt(self.instance.plan_work)
            expect(prompt.referenced_tool_names).to(equal(("increment",)))

        with it("should reject an undecorated method"):
            expect(lambda: McpPrompt(self.instance._ordinary_helper)).to(raise_error(TypeError))

    with context("with an @instruction that references @agent_tool calls in its body"):
        with before.each:
            self.instance = HostingDemo()

        with it("should list referenced @agent_tool names for an @instruction that mixes tool(...) and ordinary code"):
            prompt = McpPrompt(self.instance.orchestrate_with_plain)
            expect(prompt.referenced_tool_names).to(equal(("increment",)))

    with context("with an @instruction that orchestrates no @agent_tool references"):
        with before.each:
            self.instance = HostingDemo()

        with it("should expose its prompt text from the method docstring"):
            prompt = McpPrompt(self.instance.guidance_only)
            expect(prompt.prompt_text).to(contain("Guidance with no orchestrated AI tools"))

        with it("should list no referenced tool names"):
            prompt = McpPrompt(self.instance.guidance_only)
            expect(prompt.referenced_tool_names).to(equal(()))

with description("an MCP toolset"):
    with context("that wraps a loaded CDD toolset instance"):
        with before.each:
            self.toolset = McpToolset(HostingDemo())

        with it("should discover @agent_tool operations"):
            expect(tuple(self.toolset.tools)).to(contain("hosting_demo.increment"))

        with it("should discover @instruction operations as prompts"):
            expect(tuple(self.toolset.prompts)).to(contain("hosting_demo.plan_work"))

        with it("should expose invocable parameters on a discovered tool"):
            tool = self.toolset.tools["hosting_demo.increment"]
            expect("step" in tool.invocable_parameters()).to(equal(True))

        with it("should expose prompt text on a discovered prompt"):
            prompt = self.toolset.prompts["hosting_demo.plan_work"]
            expect(prompt.prompt_text).to(contain("Think about the concept"))

        with context("that has registered on an MCP server"):
            with before.each:
                self.server = _build_server()
                self.toolset.register_on(self.server)

            with it("should enroll its tools on the server"):
                expect(self.server.list_tools()).to(contain("hosting_demo.increment"))

            with it("should enroll its prompts on the server"):
                expect(self.server.list_prompts()).to(contain("hosting_demo.plan_work"))

with description("an MCP server"):
    with context("that has been built"):
        with before.each:
            self.server = _build_server()

        with context("that has called start with an annotated @toolset class reference"):
            with before.each:
                self.server.start((f"{HostingDemo.__module__}:{HostingDemo.__name__}",))

            with it("should report itself as started"):
                expect(self.server.started).to(equal(True))

            with it("should keep the enrolled MCP toolset"):
                expect("hosting_demo" in self.server.toolsets).to(equal(True))

            with context("with @agent_tool operations on the loaded toolset"):
                with context("that has discovered them"):
                    with it("should include a registered @agent_tool in list_tools"):
                        expect(self.server.list_tools()).to(contain("hosting_demo.increment"))

                    with it("should include another registered @agent_tool in list_tools"):
                        expect(self.server.list_tools()).to(contain("hosting_demo.read_count"))

                with context("that has invoked one through invoke_tool"):
                    with it("should return the operation result to the host"):
                        result = self.server.invoke_tool("hosting_demo.increment", {"step": 3})
                        expect(result).to(equal(3))

                with context("that receives a second invoke_tool call on the same loaded toolset instance"):
                    with it("should preserve toolset state from the first call"):
                        self.server.invoke_tool("hosting_demo.increment", {"step": 4})
                        expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(4))

                    with it("should accumulate state from a second call on the same instance"):
                        self.server.invoke_tool("hosting_demo.increment", {"step": 4})
                        self.server.invoke_tool("hosting_demo.increment", {"step": 1})
                        expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(5))

                with context("that is asked for an unknown MCP tool name"):
                    with it("should raise KeyError from invoke_tool"):
                        expect(lambda: self.server.invoke_tool("hosting_demo.missing", {})).to(
                            raise_error(KeyError)
                        )

            with context("with @instruction operations on the loaded toolset"):
                with context("that has discovered them"):
                    with it("should include a registered @instruction in list_prompts"):
                        expect(self.server.list_prompts()).to(contain("hosting_demo.plan_work"))

                with context("with an @instruction that references @agent_tool calls in its body"):
                    with context("that has invoked it through invoke_prompt"):
                        with it("should return the orchestration result to the host"):
                            result = self.server.invoke_prompt(
                                "hosting_demo.plan_work", {"concept": "widgets"}
                            )
                            expect(result["concept"]).to(equal("widgets"))

                        with it("should run the referenced @agent_tool as part of the invocation"):
                            self.server.invoke_prompt(
                                "hosting_demo.plan_work", {"concept": "widgets"}
                            )
                            expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(2))

                        with it("should return the value from a tool(...) call in the instruction result"):
                            result = self.server.invoke_prompt(
                                "hosting_demo.plan_work", {"concept": "widgets"}
                            )
                            expect(result["count"]).to(equal(2))

                with context("with an @instruction that orchestrates no @agent_tool references"):
                    with context("that has invoked it through invoke_prompt"):
                        with it("should return the guidance text to the host"):
                            result = self.server.invoke_prompt("hosting_demo.guidance_only", {})
                            expect(result).to(equal("guidance-text"))

                with context("with an @instruction mixing tool(...) calls and ordinary code"):
                    with context("that has invoked it through invoke_prompt"):
                        with it("should return ordinary code values in the instruction result"):
                            result = self.server.invoke_prompt(
                                "hosting_demo.orchestrate_with_plain", {}
                            )
                            expect(result["plain"]).to(equal("plain-result"))

                        with it("should not advance state beyond what the orchestrated @agent_tool caused"):
                            self.server.invoke_prompt("hosting_demo.orchestrate_with_plain", {})
                            expect(self.server.invoke_tool("hosting_demo.read_count", {})).to(equal(1))

                with context("that is asked for an unknown MCP prompt name"):
                    with it("should raise KeyError from invoke_prompt"):
                        expect(lambda: self.server.invoke_prompt("hosting_demo.missing", {})).to(
                            raise_error(KeyError)
                        )
