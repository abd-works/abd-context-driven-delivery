"""BDD behavior spec for utilities/mcp-server — MCP-native CDD runtime."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("utilities", "primitives", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mamba import context, description, it


with description("an MCP server"):
    with context("that has started against a checkout"):
        with context("with annotated toolsets loaded"):
            with it("should expose each @tool under a dotted MCP name"):
                # BDD: SIGNATURE
                pass

            with it("should invoke the bound Python callable when a tool is called"):
                # BDD: SIGNATURE
                pass

            with it("should retain loaded toolset instances across repeated tool calls"):
                # BDD: SIGNATURE
                pass

        with context("with @instruction methods on those toolsets"):
            with it("should expose each instruction prompt text from its docstring"):
                # BDD: SIGNATURE
                pass

            with it("should declare the MCP tool names referenced by tool(...) in the instruction body"):
                # BDD: SIGNATURE
                pass

            with it("should not execute the instruction body as orchestration"):
                # BDD: SIGNATURE
                pass

    with context("that lists its registered surface"):
        with it("should return tool names separately from instruction prompt names"):
            # BDD: SIGNATURE
            pass


with description("an MCP tool name"):
    with context("that is derived from a CDD toolset identity"):
        with it("should use dot notation between toolset slug and method name"):
            # BDD: SIGNATURE
            pass

        with it("should not use underscore separators"):
            # BDD: SIGNATURE
            pass


with description("MCP tool registration"):
    with context("that discovers annotated @tool methods"):
        with it("should register bound callables without YAML request documents"):
            # BDD: SIGNATURE
            pass

        with it("should derive parameter schema from the Python callable signature"):
            # BDD: SIGNATURE
            pass


with description("an instruction binding"):
    with context("that is collected from an @instruction method"):
        with it("should resolve tool(...) references to the same dotted names used at registration"):
            # BDD: SIGNATURE
            pass

        with it("should ignore ordinary method calls that are not wrapped in tool(...)"):
            # BDD: SIGNATURE
            pass
