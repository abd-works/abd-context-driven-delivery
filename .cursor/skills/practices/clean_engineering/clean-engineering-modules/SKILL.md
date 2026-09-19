#### Overview


**Default format:** markdown  
**Stage:** discovery
**Diagram format:** `drawio` (modules view with blue boxes, public-interface bullets, and one-way dependency arrows; template `templates/modules.drawio`). Programming-language channels are for **model** and later.

**Goal:** Partition a problem into independently understandable units — name each unit, its public seam, and its one-way dependencies.

Each **module** is a named structural boundary that groups closely related classes — and optionally smaller modules — into a single cohesive unit. Modules can be composed of other modules; a highly complex and nested module can be thought of as a sub-system.

Use MCP tool: `clean-engineering-modules()`
