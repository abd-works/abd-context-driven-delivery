# Question: ticket.close with only delete_worktree chosen still commits and pushes the worktree's uncommitted and untracked files

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Close Active Session - "Offer to commit a branch open in its worktree" (commit and push are choices); Delete Ticket Branch - "Delete the branch and the worktree that has it".
- **Module and class:** `space/repo/worktree.py` `Worktree.close(commit_message)`; `space/kanban/ticket_checkout.py`.
- **Severity:** answered question

## Steps
1. Activate loyalty-points; in its worktree change `src/points.py` and add `untracked-notes.txt`.
2. `ticket.close ticket="loyalty-points" leaving=["delete_worktree"]` (no commit, no push).

## Expected
Unclear: the work is kept either way (good), but commit and push were not chosen.

## Actual
A commit "loyalty-points: leave session" holding both files is made on the branch and pushed to origin, then the worktree is removed. Nothing is lost; the person's unchosen commit and push happen without being said in the answer.

## Tier that should catch it
Heavy (`ticket_work_heavy_spec.py`), once decided.

## Also seen by

## Answer (2026-11-23)

A close does only what was picked: deleting the worktree or branch commits and pushes nothing, ticket.close_choices warns (`unsaved_work`, `warning`) that the uncommitted work will be lost, and the closed ticket's `dropped_work` names what went. Built in space/kanban/ticket_checkout.py, space/kanban/ticket.py and space/repo/repo.py (`Branch.push`); tested by space/kanban/ticket_work_heavy_spec.py 'that a ticket is closed with only its worktree deleted while that worktree holds work nobody committed'; scenario "Warn that deleting a worktree without a commit loses its work" in story_tests/move-work-forward-on-session-board/steer-ticket-sessions/steer_ticket_sessions_story.test.md.
