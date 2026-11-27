# Hardening report — ui-fixes-as-i-use-it

Card 7651c123c132, `/actions-generate stories-hardening` with the cdd_claude_mod and cdd_web_domain_access overlays. Scope: what branch `ui-fixes-as-i-use-it` changed since `main`, in the four themes of [coverage-themes.md](coverage-themes.md), which the person named on the card.

## Exploratory testing

Four themes, four charters ([charters.md](charters.md)), one tester robot each, each in its own sandbox and throwaway `CDD_HOME`:

| Theme | Robot | Report | Defects |
|---|---|---|---|
| T1 Chat bar format chips and board sends | Pip | [report-pip.md](report-pip.md) | pip-1 to pip-7 |
| T2 Queue band: robot rows, themes, + then send, send to another chat | Rivet | [report-rivet.md](report-rivet.md) | rivet-1 to rivet-7 |
| T3 Files app right-click menu and All files | Gizmo | [report-gizmo.md](report-gizmo.md) | gizmo-1 to gizmo-9 |
| T4 Diagrams, story explorer and the scenario reader | Widget | [report-widget.md](report-widget.md) | widget-1 to widget-8 |

The supervisor (Bolt) added bolt-1 while checking the testers' isolation, and the regression run found bolt-2 and bolt-3.

Every defect was triaged by a fixing robot other than its reporter (Cue for the queue, Hinge for the Files app's files, Latch for the guidance selection, Relay for chat sends and board links, Prism for the story readers and explorer, Quill for the class model readers); bolt-2 and bolt-3 were found after the testers closed and triaged by Bolt.

### Defects by module

| Module | Defect | Status | Severity | Fix commit |
|---|---|---|---|---|
| `space/session/files` | gizmo-1 delete through a junction deletes its target | confirmed | data loss | d64447e5d |
| | gizmo-2 All files lists through junctions | confirmed | wrong result | d64447e5d |
| | gizmo-3 deleting a folder that holds a root | confirmed | data loss | d64447e5d |
| | gizmo-6 a file added to a practice can never be deleted | confirmed (message); question (taking a root back) | misleading message | d64447e5d |
| | gizmo-8 folder delete stops half-way, reaches a nested `.git` | confirmed | data loss | d64447e5d |
| | gizmo-9 ignored root listed or not | question for the person | — | 4fd201721 (triage) |
| `space/session/practices` | gizmo-4 `.git` taken as a root breaks All files | confirmed | blocks work | 4fd201721 |
| | gizmo-5 project's top folder added as a root named "" | confirmed; question (deleting another session's record) | wrong result | 4fd201721 |
| | gizmo-7 adding an existing root says "added" | confirmed | misleading message | 4fd201721 |
| | pip-1 two format toggles at once lose one | confirmed | wrong result | 3bce303c5 |
| | pip-2 `toggle_guidance` accepts unknown names | confirmed | misleading message | d83f3cc3e |
| | pip-3 code chip selected before any press | question for the person | — | eb7d00c21 (triage) |
| | pip-4 a chip press leaves a fidelity no format | confirmed | wrong result | d49d6b15c |
| `harness/chat` | pip-5 two sends at once overwrite one message | confirmed | wrong result | 195acb87f |
| | pip-7 resend while taken delivers twice | confirmed | wrong result | 0bb38fc26 |
| `cdd_guidance/actions/render`, `harness/files_app` | pip-6 a board link may be any text and is sent as the person | confirmed | wrong result | f241d5596 |
| `harness/files_app` | bolt-2 a format press made while the list is read again is dropped | confirmed | wrong result | ebcf85741 |
| | bolt-3 the only chosen chip promises "every format" and the press is refused | question for the person | wrong hint | — |
| `tools/prompt_queue` | rivet-1 a sent card loses its theme on another spelling | confirmed | wrong result | 415297355 |
| | rivet-2 + stays armed after its hint is cleared | confirmed | wrong result | a97cc772d |
| | rivet-3 a task sent after + keeps the viewer's state, drops files | confirmed | wrong result | 87a5aeeb4 |
| | rivet-4 a multi-line card splits in a sent message | confirmed | wrong result | 3feb838d2 |
| | rivet-5 a send that fails after delivery leaves the card twice | confirmed | wrong result | a91a2c5fd |
| | rivet-6 `set_theme` takes an empty robot and several lines | confirmed | cosmetic | 71590096f |
| | rivet-7 sending the running card | question for the person | — | 02e8a6cf0 (triage) |
| `harness/mcp` | bolt-1 a spec's cdd server writes into the real chats folder | confirmed | wrong result | b8654fe6d |
| Clean Engineering model readers | widget-1 domain model round trip moves language to "Kept" | confirmed | wrong result | dfe41aa2a |
| | widget-5 CE render reads context headings as classes | confirmed | wrong result | dfe41aa2a |
| | widget-8 a repository block merged into its root class | confirmed | wrong result | dfe41aa2a |
| Stories readers | widget-2 a renamed scenario held twice | question for the person | — | 1675de946 (triage) |
| | widget-3 a step loses its code body when counts differ | confirmed | wrong result | 19af5c5c9 |
| | widget-4 a drawn story links only to a file named after it | confirmed | wrong result | e108205fe |
| UX story explorer | widget-6 code scenarios open at line 0 or the wrong file | confirmed | wrong result | a636cba08 |
| | widget-7 a class card shows markdown marks | confirmed | cosmetic | 865e408ef |

widget-1, 5 and 8 share one commit: one reader change (Clean Engineering reads a domain model written after the DDD model template) fixed all three, so they could not be split.

### Defects by story

Every confirmed defect has a scenario under its story, added with its fix or in f2e18a7f4 (widget-1, 5, 8 under Take Class Model To Another Format And Back; widget-7 under Open A Step's Domain Term As Its Class Card), and a test seen failing first; each defect file names both.

### Questions waiting on the person

- **pip-3 and bolt-3:** a format chip is used as a filter of the file list, but a press changes which formats each fidelity writes. Since pip-4's fix, pressing a fidelity's only chosen format is refused, while the chip still says "press to show every format". Recommendation in bolt-3: change the hint now; split the chip into a filter and a written format as its own story if wanted.
- **rivet-7:** whether sending the card being worked to another chat is refused or warned.
- **widget-2:** whether a scenario renamed in markdown but not in its story test is reported.
- **gizmo-5, gizmo-6, gizmo-9:** deleting another session's record, taking a root back, and whether an ignored folder added as a root is listed.

### Still at risk, from the testers

- Shared files read, changed and written without being held the whole time (pip-1, pip-5 fixed; others may exist), and the server queueing every press as a new message (pip).
- + then send has no run test (rivet).
- Projects in pml-web's own model layout, code-written scenarios in the explorer and links, and merging markdown and code scenarios by words then position (widget).
- File deletes now check what they remove; links and nested repositories were the gap (gizmo).

## Regression

Run after every exploratory defect was fixed and committed, on `ui-fixes-as-i-use-it` from 2026-11-26 19:46 to 22:40 local, heavy and e2e side by side as the person asked (queue card 2b6d5c0dc80e). Bolt's first regression run (18:00 to 19:03) stopped when its robots met a billing error; this run picked it up from the uncommitted fix the robot Spline had left.

### Tiers

| Tier | Result | Notes |
|---|---|---|
| Unit | 501 of 501 files | Run again after the last code change; one earlier run had a 172 ms example over its 100 ms budget while heavy ran beside it, which runs in budget alone |
| Heavy | 86 of 86 files | 85 in the tier run; `graph_build_heavy_spec` held the tier past 30 minutes (bolt-4) and passed alone once fixed (15 examples, 1 pending by design, 637 s); the graph and file heavy specs ran again after the last graph change and passed |
| E2E, Python browser specs | 11 of 11 files, with the queue plugin spec apart | `switch-files-app-between-files-and-graph` looped without end in the tier run (pressing off the only chosen format is refused) and passes twice alone once its helper presses formats on instead; the four Files app specs that failed in Bolt's run were stale specs (three) and bolt-2 |
| E2E, board Playwright suite | 241 of 241 | 240 in the tier run; maintain-tickets › Delete a child backlog item failed with EPERM on its fixture folder while heavy specs ran beside it, and passes alone |
| E2E, queue plugin (headless Claude Code chat) | not verified | The headless Claude Code CLI answers every prompt with 403, "Claude Code can't use your Claude subscription, usually because a payment is past due"; the spec half passed on a chat that did nothing, and now stops on the agent's error and names it (every example, 8 s). Run it again once the subscription works |
| Agentic BDD (`*_agent_spec.py`) | not run | `-SkipAgents`: they drive a real agent, which was failing on a billing error earlier in the session |

### Defects the regression run found

| Defect | Module | Severity | Fix commit |
|---|---|---|---|
| bolt-2 a format press made while the list is read again is dropped | `harness/files_app` | wrong result | ebcf85741 |
| bolt-3 the only chosen chip promises "every format" and the press is refused | `harness/files_app`, `space/session/practices` | question for the person | — |
| bolt-4 a property named for its class's property group is its own parent, and a validate's save never ends | `harness/graph` | blocks work | 8cfa4f875 |
| bolt-5 every e2e-review tool is refused on a pinned runtime, saying only Node's version | `harness/e2e_review` | blocks work | db0db2a58 |

Found and fixed with them, each with its own commit: a graph refresh holds what a fresh build holds (e966e6ee6, from Spline's work, graph_incremental_heavy_spec 13 failing to 0); saving a checked graph asks each node once whether it is written in the saved files (ad0a10ac0, 44474bf29); and the e2e specs that still expected behaviour the release changed on purpose: a design canvas named by its published title, a whiteboard opening its board in Claude (72c42992b, d1bf4a8bf).

### Screens against the last release

No sub-epic has an accepted run (`baseline.json`) for v1.2.1 or any release before it, so there is nothing to compare this run's screens with: every step is new, and `changed_pairs` lists none. The e2e tier recorded step screens for three board sub-epics, all passing:

| Sub-epic | Run | Steps |
|---|---|---|
| move-work-forward-on-session-board/maintain-tickets | `.sessions/local/e2e-test-results/.../maintain-tickets/2026-11-27-03-09-12` | 72 |
| move-work-forward-on-session-board/steer-ticket-sessions | `.../steer-ticket-sessions/2026-11-27-03-09-12` | 5 |
| move-work-forward-on-session-board/work-fidelity-outputs-on-board | `.../work-fidelity-outputs-on-board/2026-11-27-03-09-12` | 14 |

The other five board story tests and the Python browser specs record no step screens, so `every-story-run-at-e2e` holds for their assertions but not for their screens: a screen there can break where no assertion looks.

**Waiting on the person:** accepting these three runs makes them the first baselines (`e2e-review.accept`, which only the person does), so the next release is compared with them.

### Still at risk

- A graph worker outlives a server stopped by force: one left from Bolt's stopped run spun a core from 17:45 to 21:20. A worker that checks its parent is alive would end it.
- The board's Playwright suite can fail on a locked fixture folder when other tiers run beside it on Windows.
- Five board sub-epics and every Python browser spec take no step screenshots.
