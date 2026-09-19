---
name: ddd
description: >-
  ## Overview
  
  Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.
  
  **`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`building_blocks`** classifies concepts with stereotypes; **`clean_engineering-code`** implements the seams when **`tactics`** wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and what each concept actually is.
  
  ---
---

## Overview

Build the solution around how the business actually works, in the words the business already uses. When the software mirrors the business, it holds the business's logic and knowledge where that understanding actually lives; when it mirrors a database, a framework, or a screen layout, every business conversation has to be re-translated and what the business knows ends up scattered wherever the technology happened to put it.

**`clean_engineering`** owns OO structure, one skill per fidelity: **`clean_engineering-modules`** shapes the module boundaries and seams when **`bounded_context`** draws the map; **`clean_engineering-model`** types the classes, operations, and relationships when **`building_blocks`** classifies concepts with stereotypes; **`clean_engineering-code`** implements the seams when **`tactics`** wires repositories, events, and factories. Do not restate module or class analysis here. DDD adds the domain layer on top: where the language changes, which clusters protect which rules, and what each concept actually is.

---

bounded_context — Draw where language changes — context boundaries, the aggregates that protect invariants inside each context, and the dependency arcs between contexts — using the experts' words. Names and boundaries are cheap to change here; they are expensive once building blocks, stories, and code hang off them.

Use MCP tool: `ddd-bounded-context()`

building_blocks — Classify each concept on the map — entity, value, repository, event, service — and shape the classes that carry them.

Use MCP tool: `ddd-building-blocks()`

tactics — Decide one implementation pattern for each building block the model uses, then implement the domain against it — preserving every name and boundary from upstream.

Use MCP tool: `ddd-tactics()`
