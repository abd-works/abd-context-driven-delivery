"""Dotted MCP name formatting."""


class _McpNameFormatter:
    """Derives stable dotted MCP names from CDD toolset identity."""

    def format(self, toolset_slug: str, method_name: str) -> str:
        return f"{toolset_slug}.{method_name}"
