## Overview

Structure the problem into independent modules with small public interfaces, substantial hidden functionality, and one-way dependencies. Implement those modules with rigorous object-oriented and clean-code practices. When boundaries hold, a change stays inside one module; when they blur, callers depend on internal decisions and must change with them.

modules — Partition a problem into independently understandable units — name each unit, its public seam, and its one-way dependencies.

Use MCP tool: `clean-engineering-modules()`

model — Design the object model — the classes, what they remember and do, and how they relate.

Use MCP tool: `clean-engineering-model()`

code — Write working production code — real persistence, services, and UI behind the public seams.

Use MCP tool: `clean-engineering-code()`
