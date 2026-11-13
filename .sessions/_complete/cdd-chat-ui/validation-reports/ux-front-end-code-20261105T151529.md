# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `harness/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (html: ). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-05 15:15:29 UTC
**Project:** chat-ui
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\cdd-chat-ui\edited-graph.json`

## Summary

**No graph rule violations.** All scanned graph rules passed.
**AI rules in scope:** 8

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `tab-states-are-separate-screens`

N tabs → N screens; chrome shared via `chrome_of` / inactive tabs.

Evaluate the current context against this rule (tab-states-are-separate-screens):

### `screen-story-budget`

~4 user stories per screen; more signals missed decomposition.

Evaluate the current context against this rule (screen-story-budget):

### `screen-names-use-domain-terms`

Screen labels trace to domain language when it exists.

Evaluate the current context against this rule (screen-names-use-domain-terms):

### `ia-named-regions-only`

At IA, regions are named slots; no control detail yet.

Evaluate the current context against this rule (ia-named-regions-only):

### `story-domain-js-imported`

At mockup+, when practices/stories/domain exist, JS modules are present (transform if needed) and imported by the html surface.

Evaluate the current context against this rule (story-domain-js-imported):

### `real-frontend-not-mockup`

Shipping UI is production frontend code, not the greybox Story Demo frame.

Evaluate the current context against this rule (real-frontend-not-mockup):

### `real-backend-wired`

Client talks to real services/persistence (CE **code**); no silent Fake path as the only path.

Evaluate the current context against this rule (real-backend-wired):

### `upstream-decisions-carried`

Layout and domain terms from earlier fidelities stay authoritative.

Evaluate the current context against this rule (upstream-decisions-carried):

## Judgment

Every rule passes. upstream-decisions-carried, the one fail of the 20261105T150222 report, is resolved: session-card-view.tsx starts each fidelity's colour, name, state and folder in its own dot's column and the shown stage's name in that stage icon's column, counting the line's cells as LineView lays them out, and the server health panel stays stacked on top; hovering the session name shows the card, a press pins it. display_session_card_story.test.ts asserts the four columns (18, 20, 22, 30 inside the card's frame). Where the cells really land on a surface is for the surface heavy spec, which is still missing.

Passes: real-frontend-not-mockup, real-backend-wired, upstream-decisions-carried, tab-states-are-separate-screens, screen-story-budget, screen-names-use-domain-terms, ia-named-regions-only, story-domain-js-imported.
