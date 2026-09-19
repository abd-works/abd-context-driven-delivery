## Overview

Write **agent BDD specs** — mamba tests that drive a real agent through the `agent(...)` harness and assert on the parsed `RunResponse` plus AI-judged prose.

**Tooling & Idioms:** Refer to [`practices/language-tools.md`](/practices/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

The **`bdd`** generator supplies the underlying test discipline (RED-GREEN, AAA, mocks, minimalism, shared setup). Agent specs layer harness-specific rules on top.

Use MCP tool: `agent-bdd.instructions()`
