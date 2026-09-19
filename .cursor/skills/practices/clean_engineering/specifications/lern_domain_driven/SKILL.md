## Overview

Implementation fidelity for a **domain-module-organized LERN stack** ([lowdb](https://github.com/typicode/lowdb)
JSON files / Express / React / Node, TypeScript everywhere) on an already-designed
vertical slice — story map, module boundaries, and screens all exist before this
tool runs. `generate` calls `self._stories()` at `acceptance_tests` /
`typescript` — specs first, then Stories' own `ce()` wires matching
production TypeScript. The rules below are additive on top of what Stories
and CleanEngineering already enforce, not a restatement of them.

**No fidelity progression of its own.** Every run pins `stories` at
`acceptance_tests` with `format="typescript"`; production code arrives via
Stories' `ce()` companion at `code` / `typescript`.

Use MCP tool: `lern-domain-driven.instructions()`
