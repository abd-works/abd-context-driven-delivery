---
description: "When the user rejects work you just generated, fix it and append mistake plus correction to corrections.log. Fix agent behaviour in CDD guidance, agent tools and agent instructions, never by writing notes into an AGENTS.md."
alwaysApply: true
---

# Learning From Corrections

When the user rejects **work you just generated in this turn**, fix the artifact that is wrong.

**Fix the agent's behaviour where it comes from, not in an `AGENTS.md`.** When a correction shows an agent did the wrong thing, change the CDD guidance, the agent tools and agent instructions that produced it (the practice and action markdown, the toolset classes and the code behind them), so every agent gets the fix from the next install. Do not create an `AGENTS.md`, or add notes to one, to steer agent behaviour: notes there reach only the agents that happen to read that file, and the guidance keeps teaching the old behaviour. Keeping an existing `AGENTS.md` accurate, such as its layout or its stage table after a stage is added, is ordinary work.

**Create `corrections.log`** in the folder that holds that generated work (create the file if it is missing). Append the mistake and the correction.

Log only a generation miss: you produced an artifact, and the user complains about that output. Do not log a request to change existing work that you did not just generate — an update, rename, or cleanup of something already on disk is ordinary work, not a correction.
