# Grill Answers

### Nested install already walks ToolSetCollection

Installer, McpServer, and prompt_echo already do `for child in toolset.nested_toolsets` and enroll each child as its own toolset (`installation/installer.py`, `installation/mcp/mcp_server.py`). GuidanceCollection already subclasses ToolSetCollection; PracticeGuidance aliases `nested_toolsets = fidelities`. The gap is that ToolSetCollection is `dict[str, Any]` reached as `.entries[name]` (see `guidance_spec.py`), not a typed, attribute-accessible nest.

