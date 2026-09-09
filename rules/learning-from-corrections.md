---
description: "Turn corrections to generated work into local guidance that prevents repetition"
alwaysApply: true
---

# Learning From Corrections

Whenever the user corrects work you generated, fix the work and record the lesson where that work is maintained. This applies especially to output produced through a context tool, utility, action, or primitive.

**Add the lesson to the local `AGENTS.md`.** Use the folder containing the corrected work. If that folder has no `AGENTS.md`, create one; if it already exists, update it without replacing its current guidance. Keeping the lesson beside the affected work makes it available to every later agent operating in that scope.

**Write a reusable rule, not a transcript of the mistake.** State the behavior to follow and, where useful, the reason it matters. Remove names, blame, and one-time details. Before adding it, check the local and parent `AGENTS.md` files so the new guideline does not duplicate or contradict an existing rule.

Record the guideline as part of the correction, in the same turn. A correction that changes only the current artifact leaves the same generation path free to repeat the mistake later.
