"""The name of each fact the CDD web domain access overlay records on a node and its rules read, written once so a writer
and a reader cannot spell one differently."""

# The tools a route or a node tier calls, whether a node tier reaches cdd, extends a generated adapter, and imports a
# store of its own.
TOOL_CALLS = "tool_calls"
REACHES_CDD = "reaches_cdd"
EXTENDS_ADAPTER = "extends_adapter"
STORE_IMPORTS = "store_imports"
# An annotated toolset's MCP operations that answer an open `dict[str, Any]`.
OPEN_RESULTS = "open_results"
