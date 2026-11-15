# Maybe Later

Work set aside for now: complicated, and not needed yet. Picked up only when asked. This is the last increment of the thin slice, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md).

**Outcome:** none until it is picked up.

**Slicing notes:** the person, 2026-11-11, on the story explorer: "this is complicated, I don't want to do it; add to backlog 'maybe later' ticket".

## Epic: Move Work Forward On Session Board

### Feature: Organize Ticket Hierarchy

#### Story: Nest Child Branch And Session

*Claude Code*. Intended (`.sessions/session-board/ticket-enhancements.md` "Nest branches and sessions for tickets in a hierarchy"): a child ticket's branch and session nest under its parent's, so the hierarchy holds in git and in `.sessions/` as on the board. Taken out of Maintain Tickets On Board on 2026-11-11. Its scenario, with the open question of how to name a nested branch (git cannot hold `checkout-flow/enter-card-details` beside `checkout-flow`), is in `harness/.context/stories/move-work-forward-on-session-board/organize-ticket-hierarchy/organize_ticket_hierarchy_story.test.md`.

## Epic: Deliver Work With Context Guidance

### Feature: Deliver Work With Overlays

#### Item: Move BDD's Process Rules Into TDD Guidance

*Decision deferred.* From the person, 2026-11-15, on the TDD overlay sketch (`.sessions/tdd-practice/tdd-overlay-sketch.md`, open decision 2): BDD development's `red-then-green`, `minimum-green` and `one-signature-at-a-time` describe process, not output, so a validate run cannot check them. The question is whether to take them out of BDD's `#### Rules` and make them steps in the TDD overlay's Guidance. "Leave it for now." They stay in BDD until this is picked up.
