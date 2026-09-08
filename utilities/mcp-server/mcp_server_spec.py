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


with description("a toolset operation"):
    with context("that has been annotated as an AI-callable tool"):
        with context("that has been registered by MCP"):
            with it("should be exposed under a dotted MCP name"):
                # BDD: SIGNATURE
                pass

            with it("should derive its parameter schema from the Python callable signature"):
                # BDD: SIGNATURE
                pass

            with it("should register the bound callable without a YAML request document"):
                # BDD: SIGNATURE
                pass

        with context("that has been invoked by MCP"):
            with it("should run the bound Python callable directly"):
                # BDD: SIGNATURE
                pass

    with context("that has been annotated as an instruction"):
        with context("that has been registered by MCP"):
            with it("should expose its docstring as prompt text"):
                # BDD: SIGNATURE
                pass

            with it("should declare the dotted MCP names for each tool(...) reference in its body"):
                # BDD: SIGNATURE
                pass

        with context("that has been invoked by MCP"):
            with it("should run its Python body"):
                # BDD: SIGNATURE
                pass

            with context("with a tool(...) call in its body"):
                with it("should invoke the wrapped AI-callable tool through the same path as a direct MCP tool call"):
                    # BDD: SIGNATURE
                    pass

                with it("should allow the tool return value to contribute to the instruction output"):
                    # BDD: SIGNATURE
                    pass

            with context("with a plain method call that is not wrapped in tool(...)"):
                with it("should run it as ordinary Python without treating it as an MCP tool invocation"):
                    # BDD: SIGNATURE
                    pass


with description("a toolset instance"):
    with context("that has been loaded by MCP"):
        with context("that receives repeated invocations against the same operation"):
            with it("should reuse the same instance"):
                # BDD: SIGNATURE
                pass


with description("an MCP exposed name"):
    with context("for a toolset operation"):
        with it("should use dot notation between toolset slug and operation name"):
            # BDD: SIGNATURE
            pass

        with it("should not use underscore separators"):
            # BDD: SIGNATURE
            pass
