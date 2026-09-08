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
    with context("that has started against a repository working tree"):
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
            with it("should expose each instruction prompt text from its docstring at discovery"):
                # BDD: SIGNATURE
                pass

            with it("should declare the MCP tool names referenced by tool(...) in the instruction body at discovery"):
                # BDD: SIGNATURE
                pass

            with it("should run the instruction body when the instruction is invoked"):
                # BDD: SIGNATURE
                pass

            with it("should invoke each tool(...) call through the registered @tool callable"):
                # BDD: SIGNATURE
                pass

            with it("should allow tool return values to contribute to the instruction output"):
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


with description("an instruction invocation"):
    with context("that reaches a tool(...) call in the instruction body"):
        with it("should run the wrapped @tool like a direct MCP tool invocation"):
            # BDD: SIGNATURE
            pass

        with it("should not treat a plain self.method(...) call as an AI tool invocation"):
            # BDD: SIGNATURE
            pass


with description("an instruction binding"):
    with context("that is collected from an @instruction method"):
        with it("should resolve tool(...) references to the same dotted names used at registration"):
            # BDD: SIGNATURE
            pass
