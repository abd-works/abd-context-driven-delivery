---
description: "When the user rejects work you just generated, fix it and append mistake plus correction to corrections.log. Never write AGENTS.md."
alwaysApply: true
---

# Learning From Corrections

When the user rejects **work you just generated in this turn**, fix the artifact that is wrong.

**Never create or update `AGENTS.md`** (any path, including `harness/**/AGENTS.md`). Put agent workflow notes in the kit markdown the installer loads (e.g. `harness/installation/installer.md`) or the installed skill — not `AGENTS.md`.

**Create `corrections.log`** in the folder that holds that generated work (create the file if it is missing). Append the mistake and the correction.

Log only a generation miss: you produced an artifact, and the user complains about that output. Do not log a request to change existing work that you did not just generate — an update, rename, or cleanup of something already on disk is ordinary work, not a correction.
