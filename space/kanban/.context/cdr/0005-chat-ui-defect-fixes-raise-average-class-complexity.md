# 0005: The chat UI defect fixes raise the average class complexity by 0.02

**Status:** accepted, 2026-11-09

**Context.** The chat UI defect fixes (`claude/chat-ui-defects-cef4bc`) were merged after round 9. They add behaviour that the defects needed:
- leaving or closing a ticket whose branch is open in its own worktree commits and pushes in that worktree
- a ticket returns to the default branch after it closes
- the chat bar says which chat to pick when none is chosen

On the merge, the metrics gate against 75f6825c failed on one measure: the average total complexity of a class went from 16.03 to 16.05. No function, class or module was pushed past a limit, and nothing already past one grew.

**Decision.** Accept the rise. The added complexity is the behaviour the defects asked for, and it sits on its owner, `TicketCheckout` (`save_work`, `write_handoff`, `return_to_default_branch`), not on `Ticket`. Taking it back out would undo the fixes.

**Consequence.** The next change to `space/kanban` should bring the average back below 16.03, for example by moving the remaining checkout branching in `TicketCheckout.save_work` into the `Branch` it acts on. See `.context/repo-review/remaining-work-plan.md`.
