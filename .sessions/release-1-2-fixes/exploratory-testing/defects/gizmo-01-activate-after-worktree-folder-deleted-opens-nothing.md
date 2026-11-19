# ticket.activate answers success but opens no worktree after the ticket's worktree folder was deleted by hand

- **Charter:** Round 1 - opening, switching and closing sessions and tickets as a person who interrupts flows, to discover leftovers that block the next start
- **Tester:** Gizmo
- **Story:** Move Work Forward on Session Board / Steer Ticket Sessions / Activate Ticket - "Open a ticket again in the worktree it has" (the worktree it "has" is gone); no scenario covers a worktree folder removed outside CDD.
- **Module and class:** `space/kanban/ticket_checkout.py` `TicketCheckout.open` (`if not self.worktree:` is false because git still lists the folder, marked `prunable`); `space/repo/worktree.py` `Worktrees.listing` / `Worktrees.of`, which answer a worktree whose folder does not exist.
- **Severity:** wrong result (and it blocks the next start: the ticket can never get a worktree again through the product until someone runs `git worktree prune`)

## Steps
Sandbox: clone `repo` of a bare origin, cdd server on a throwaway CDD_HOME, chat on `repo`.
1. `ticket.create title="Loyalty points"`, then `ticket.activate ticket="loyalty-points"` - worktree `..\repo-loyalty-points` is made.
2. Delete the folder by hand: `rm -rf ../repo-loyalty-points` (what a person does to "clean up").
3. `ticket.activate ticket="loyalty-points"` again.
4. `git worktree list` in `repo`; `ls ..`.

## Expected
The ticket opens in a worktree again (module-context of space/kanban: "`ticket.open_choices` answers its own worktree while it has none, the only way a ticket opens"), or the call refuses and says the folder is missing.

## Actual
`ticket.activate` answers the ticket in 0.3 s with no error. No folder is made:
```
C:/dev/_et/gizmo/work/repo                c313390 [main]
C:/dev/_et/gizmo/work/repo-loyalty-points 801a649 [loyalty-points] prunable
```
`ls ..` shows only `origin.git repo`. `ticket.close_choices` still offers `delete_worktree` and `commit`/`push` for a checkout that is not there. Every later activate does the same, so the ticket's chat has nowhere to start.

## Tier that should catch it
Heavy (`space/kanban/ticket_work_heavy_spec.py` or `space/repo/worktree_heavy_spec.py`): it needs real git, whose `worktree list` keeps a deleted folder as `prunable`. The heavy specs only remove worktrees through the product.

## Also seen by

## Confirmation (Sparky, round 2)
- Result: confirmed
- What I ran and saw: Run through a sandbox cdd server on a fresh clone (`C:\dev\_et\sparky\confirm\gizmo\gz.py`). After the worktree folder is deleted, `ticket.activate` answers the ticket with no error, `git worktree list` shows `repo-loyalty-points ... [loyalty-points] prunable`, no folder is made, and `ticket.close_choices` still offers `delete_worktree`.
- Cause, if you found it: `space/repo/worktree.py` `Worktrees.of` answers the checkout git lists for the branch without looking whether its folder is there, so `TicketCheckout.open` in `space/kanban/ticket_checkout.py` skips `open_in_worktree`.
- Shares its cause with: gizmo-07 (what git lists and what is on disk disagree, and `Worktrees` trusts the lookup by branch alone)
