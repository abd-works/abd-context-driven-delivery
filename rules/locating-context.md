---
description: "Where to find durable project context and temporary work-session context"
alwaysApply: true
---

# Locating Context

Always search `.context/` first for durable facts: how the code works, what the requirements are, why decisions were made, and how the system or its tools are used.

**Start from the working area and search outward.** Look in the nearest `.context/` first, then work upward to the repository root. If the answer is not there, search across the repository and then in other related repositories. Starting near the work preserves its local meaning; widening only when necessary avoids applying another module's or repository's decisions to the current one.

**When no working area is known, search top down.** Inspect the top level and root `.context/` of each available repository first, identify the repository most likely to own the subject, and then work inward through its modules and folders.

Use the repository-root `.sessions/` for temporary work context: the latest handoff, what needs to happen next, and what was done most recently. All work sessions live under that root folder. Find the session related to the current work or question, then read its handoff and recent artifacts before using an unrelated session.

Use `.context/` for facts intended to remain true across sessions and `.sessions/` for the state of work at a particular point in time. This distinction prevents temporary plans from being treated as requirements and keeps durable decisions from being overlooked in old session history.
