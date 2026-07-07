---
description: Any reference to another markdown file must be preceded by an explicit read instruction.
globs: **/*.md
---

When an instruction refers another markdown file, always preface the reference with an explicit read directive so the agent reads it in full before acting on it.

**Pattern:**

> Read `<path>` in full, then follow its instructions.

Never write a bare reference like "see `file.md`" or "follow `file.md`" without first telling the agent to read it. A reference without a read instruction will be skipped or summarised from memory.
