# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
"""Infrastructure spec — stdio MCP host wired to the CDD runtime."""

import asyncio
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _path = str(_REPO_ROOT / _cat)
    if _path not in sys.path:
        sys.path.insert(0, _path)

from expects import contain, equal, expect
from mamba import context, description, it
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_HOSTING_DEMO = "mcp_server.examples.hosting_demo.hosting_demo:HostingDemo"
_ECHO = "echo.echo:Echo"
_BDD = "context_tools.bdd.bdd:Bdd"
_PARAMETER_TYPES = (
    "mcp_server.examples.parameter_types.parameter_types:ParameterTypes"
)
_ECHO_ARGUMENTS = {
    "text": "parcel",
    "count": 2,
    "ratio": 1.5,
    "flag": True,
    "items": ["a", "b"],
    "fields": {"city": "depot"},
    "untyped_items": ["x"],
    "untyped_fields": {"k": "v"},
    "counted_items": [1, 2],
    "flagged_items": [True, False],
    "measured_items": [0.5],
    "nested_items": [["a"]],
    "record_items": [{"id": "1"}],
    "counted_fields": {"n": 3},
    "listed_fields": {"ns": [1, 2]},
}
_PYTHON = _REPO_ROOT / ".venv" / "Scripts" / "python.exe"
_PYTHONPATH = ";".join(
    [
        str(_REPO_ROOT),
        str(_REPO_ROOT / "utilities"),
        str(_REPO_ROOT / "primitives"),
        str(_REPO_ROOT / "context_tools"),
    ]
)

def _run_async(coro):
    return asyncio.run(coro)

def _host_params(toolsets: str) -> StdioServerParameters:
    return StdioServerParameters(
        command=str(_PYTHON),
        args=["-m", "mcp_server", "--toolsets", toolsets],
        cwd=str(_REPO_ROOT),
        env={**__import__("os").environ, "PYTHONPATH": _PYTHONPATH},
    )

async def _with_session(toolsets: str, action):
    async with stdio_client(_host_params(toolsets)) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            return await action(session)

def _text(result) -> str:
    return result.content[0].text

with description("an MCP host over stdio"):
    with context("that has started with no toolsets loaded"):
        with it("should expose the built-in health-check tool"):
            tools = _run_async(
                _with_session("", lambda session: session.list_tools())
            )
            expect([tool.name for tool in tools.tools]).to(contain("cdd.ping"))

        with it("should answer cdd.ping with pong"):
            result = _run_async(
                _with_session(
                    "",
                    lambda session: session.call_tool("cdd.ping", arguments={}),
                )
            )
            expect(_text(result)).to(equal("pong"))

    with context("that has started with the HostingDemo toolset"):
        with it("should list HostingDemo @agent_tool operations"):
            tools = _run_async(
                _with_session(_HOSTING_DEMO, lambda session: session.list_tools())
            )
            names = [tool.name for tool in tools.tools]
            expect(names).to(contain("hosting_demo.increment"))
            expect(names).to(contain("hosting_demo.read_count"))

        with it("should list @instruction operations in list_prompts"):
            prompts = _run_async(
                _with_session(_HOSTING_DEMO, lambda session: session.list_prompts())
            )
            expect([prompt.name for prompt in prompts.prompts]).to(
                contain("hosting_demo.plan_work")
            )

        with it("should list @instruction operations in list_tools for host invocation"):
            tools = _run_async(
                _with_session(_HOSTING_DEMO, lambda session: session.list_tools())
            )
            expect([tool.name for tool in tools.tools]).to(
                contain("hosting_demo.plan_work")
            )

        with it("should retain toolset state across calls in one process"):
            async def exercise(session):
                await session.call_tool(
                    "hosting_demo.increment", arguments={"step": 4}
                )
                first = await session.call_tool(
                    "hosting_demo.read_count", arguments={}
                )
                await session.call_tool(
                    "hosting_demo.increment", arguments={"step": 1}
                )
                second = await session.call_tool(
                    "hosting_demo.read_count", arguments={}
                )
                return _text(first), _text(second)
            first, second = _run_async(_with_session(_HOSTING_DEMO, exercise))
            expect(first).to(equal("4"))
            expect(second).to(equal("5"))

        with context("with an @instruction that references @agent_tool calls in its body"):
            with it("should run orchestration through tools/call"):
                result = _run_async(
                    _with_session(
                        _HOSTING_DEMO,
                        lambda session: session.call_tool(
                            "hosting_demo.plan_work",
                            arguments={"concept": "widgets"},
                        ),
                    )
                )
                payload = json.loads(_text(result))
                expect(payload["concept"]).to(equal("widgets"))
                expect(payload["count"]).to(equal(2))

            with it("should advance toolset state from orchestrated @agent_tool calls"):
                async def exercise(session):
                    await session.call_tool(
                        "hosting_demo.plan_work",
                        arguments={"concept": "widgets"},
                    )
                    read_count = await session.call_tool(
                        "hosting_demo.read_count", arguments={}
                    )
                    return _text(read_count)
                expect(_run_async(_with_session(_HOSTING_DEMO, exercise))).to(equal("2"))

    with context("that has started with the Echo toolset"):
        with it("should invoke a real @agent_tool through the MCP wire"):
            result = _run_async(
                _with_session(
                    _ECHO,
                    lambda session: session.call_tool(
                        "echo.fence", arguments={"body": "hello mcp"}
                    ),
                )
            )
            expect("hello mcp" in _text(result)).to(equal(True))

    with context("that has started with the Bdd context tool"):
        with it("should list Bdd @agent_tool operations"):
            tools = _run_async(
                _with_session(_BDD, lambda session: session.list_tools())
            )
            names = [tool.name for tool in tools.tools]
            expect(names).to(contain("bdd.transform"))
            expect(names).to(contain("bdd.render"))

        with it("should invoke bdd.transform through the MCP wire"):
            result = _run_async(
                _with_session(
                    _BDD,
                    lambda session: session.call_tool(
                        "bdd.transform",
                        arguments={
                            "source_format": "markdown",
                            "target_format": "markdown",
                            "content": "# hi",
                        },
                    ),
                )
            )
            payload = json.loads(_text(result))
            expect(payload["content"]).to(equal("# hi\n"))

    with context("that has started with the ParameterTypes toolset"):
        with it("should advertise a list parameter as a JSON Schema array"):
            tools = _run_async(
                _with_session(_PARAMETER_TYPES, lambda session: session.list_tools())
            )
            echo = next(tool for tool in tools.tools if tool.name == "parameter_types.echo")
            expect(echo.inputSchema["properties"]["items"]["type"]).to(equal("array"))

        with it("should advertise a dict parameter as a JSON Schema object"):
            tools = _run_async(
                _with_session(_PARAMETER_TYPES, lambda session: session.list_tools())
            )
            echo = next(tool for tool in tools.tools if tool.name == "parameter_types.echo")
            expect(echo.inputSchema["properties"]["fields"]["type"]).to(equal("object"))

        with it("should advertise a boolean parameter as JSON Schema boolean"):
            tools = _run_async(
                _with_session(_PARAMETER_TYPES, lambda session: session.list_tools())
            )
            echo = next(tool for tool in tools.tools if tool.name == "parameter_types.echo")
            expect(echo.inputSchema["properties"]["flag"]["type"]).to(equal("boolean"))

        with it("should return a list argument unchanged"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo", arguments=_ECHO_ARGUMENTS
                    ),
                )
            )
            expect(json.loads(_text(result))["items"]).to(equal(["a", "b"]))

        with it("should return a boolean argument unchanged"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo", arguments=_ECHO_ARGUMENTS
                    ),
                )
            )
            expect(json.loads(_text(result))["flag"]).to(equal(True))

        with it("should return a dict argument unchanged"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo", arguments=_ECHO_ARGUMENTS
                    ),
                )
            )
            expect(json.loads(_text(result))["fields"]).to(equal({"city": "depot"}))

        with it("should return an integer argument unchanged"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo", arguments=_ECHO_ARGUMENTS
                    ),
                )
            )
            expect(json.loads(_text(result))["count"]).to(equal(2))

        with it("should return a float argument unchanged"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo", arguments=_ECHO_ARGUMENTS
                    ),
                )
            )
            expect(json.loads(_text(result))["ratio"]).to(equal(1.5))

        with it("should return a nested list argument unchanged"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo", arguments=_ECHO_ARGUMENTS
                    ),
                )
            )
            expect(json.loads(_text(result))["nested_items"]).to(equal([["a"]]))

        with it("should invoke a Sequence parameter with a JSON array"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo_sequence",
                        arguments={"value": ["stop", "drop"]},
                    ),
                )
            )
            expect(json.loads(_text(result))).to(equal(["stop", "drop"]))

        with it("should invoke a Mapping parameter with a JSON object"):
            result = _run_async(
                _with_session(
                    _PARAMETER_TYPES,
                    lambda session: session.call_tool(
                        "parameter_types.echo_mapping",
                        arguments={"value": {"n": 3}},
                    ),
                )
            )
            expect(json.loads(_text(result))).to(equal({"n": 3}))
