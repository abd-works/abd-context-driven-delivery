---
name: bdd
description: >-
  ## Overview
  
  Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).
  
  **Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns.
---

## Overview

Behavior-driven development turns domain vocabulary into passing tests. Every BDD artifact is an indented hierarchy. Sketch that shape first (`templates/bdd-sketch.md`).

**Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns.

behavior — Define BDD signatures — describe/it names for every observation, no test bodies.

Use MCP tool: `bdd-behavior()`

development — Implement BDD tests with production code.

Use MCP tool: `bdd-development()`
