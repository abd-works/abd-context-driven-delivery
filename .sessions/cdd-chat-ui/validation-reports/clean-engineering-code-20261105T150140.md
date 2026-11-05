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


Judge only the checked format's files (python: C:/dev/abd-cdd-chat-ui/harness/chat-ui/{module}/). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-05 15:01:40 UTC
**Project:** chat-ui
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\cdd-chat-ui\edited-graph.json`

## Summary

**Total graph violations:** 6
**Rules with graph hits:** 2
**AI rules in scope:** 18

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. Wrap or extend the live objects and name a wrapper after the type it represents; do not scrape the same data into a second `*Model` or `*Entry` family.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [pane/hooks/health/server-health-view.tsx](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\hooks\health\server-health-view.tsx#L136): Operation `ExpandedView`: Operation 'ExpandedView' is 27 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

Evaluate the current context against this rule (provide-meaningful-context):

### `eliminate-duplication`

Give repeated logic one canonical function. Every copy is another place the fix has to be repeated, and the copy you miss is the bug.

Evaluate the current context against this rule (eliminate-duplication):

### `no-legacy-api-after-refactor`

When you rename or reshape a public seam, update every caller — tests, dependencies, and adjacent modules — to the new API. Do not keep compatibility aliases, re-exports, or thin wrappers that preserve the old name.

Evaluate the current context against this rule (no-legacy-api-after-refactor):

### `use-exceptions-properly`

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. A `pass` in `except` hides a broken invariant.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [pane/hooks/board-chat/board-chat-client.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\hooks\board-chat\board-chat-client.ts#L1): OoadClass `_module`: Class '_module' exposes 13 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-client.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-client.ts#L1): OoadClass `_module`: Class '_module' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/chat-bar-view.tsx](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\chat-bar-view.tsx#L1): OoadClass `_module`: Class '_module' exposes 15 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/chat-bar/fidelity-client.ts](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\hooks\chat-bar\fidelity-client.ts#L1): OoadClass `_module`: Class '_module' exposes 10 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [pane/hooks/health/server-health-view.tsx](C:\dev\abd-cdd-chat-ui\harness\chat-ui\pane\hooks\health\server-health-view.tsx#L1): OoadClass `_module`: Class '_module' exposes 13 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/chat-bar-view.tsx`

### `keep-classes-single-responsibility` — Fail
- chat-bar-view.tsx:1 `chat-bar-view`: one module draws the line, the action picker, the session list, the activation and close dialogs and the session card (15 functions); the dialogs change with the board's dialogs, the line with the canvas, so the session list and dialogs belong in their own view file beside session-dialogs-client.ts.

### `eliminate-duplication` — Fail
- chat-bar-view.tsx:25 `BRAND`: the canvas colours are written again in fidelity-files-view.tsx:9 and server-health-view.tsx:9; one shared palette module would keep the three views from drifting.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/fidelity-files-view.tsx`

### `eliminate-duplication` — Fail
- fidelity-files-view.tsx:9 `BRAND`: a copy of four of chat-bar-view.tsx's canvas colours.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/chat-bar-client.ts`

### `keep-classes-single-responsibility` — Fail
- chat-bar-client.ts:1 `chat-bar-client`: 10 public operations against a budget of ~9 (graph); the session actions activate, create and close could sit with the session list and dialogs they open, leaving the chat bar's own line here.

### `vocabulary-traces-to-source` — Fail
- chat-bar-client.ts:129 `agentBrief`: the pattern calls this the agent context (`agent-context-comes-from-the-client`) and the module context calls it the active ticket section of the system prompt; `brief` is a third word for it.

## Judgment — `harness/chat-ui/pane/hooks/chat-bar/fidelity-client.ts`

### `keep-classes-single-responsibility` — Fail
- fidelity-client.ts:1 `fidelity-client`: 10 public operations against ~9 (graph); the action picker's atom and toggle are view state like session-dialogs-client.ts, apart from the fidelity's own actions.

## Judgment — `harness/chat-ui/pane/hooks/board-chat/board-chat-client.ts`

### `keep-classes-single-responsibility` — Fail
- board-chat-client.ts:1 `board-chat-client`: 13 functions against ~9 (graph); naming the chat (readName, typedText, SUMMARY_OPENINGS) changes for a different reason than relaying board messages and could be its own file.

## Judgment — `harness/chat-ui/pane/hooks/health/server-health-view.tsx`

### `keep-classes-single-responsibility` — Fail
- server-health-view.tsx:1 `server-health-view`: 13 functions against ~9 (graph); the headline, details and install-line wording (headlineOf, detailsOf, installLineOf, partsOf) is display shaping that belongs on ServerHealthClient.

### `keep-operations-small-focused` — Fail
- server-health-view.tsx:136 `ExpandedView`: 27 lines (graph); the headline row is a sub-view of its own.

Passes: do-not-invent-terms, do-not-invent-parallel-object-models, hide-inner-details (ChatBarClient no longer hands out TicketData; register.ts reads statusLine, agentBrief and hasSession), prefer-instance-operations, keep-operations-single-responsibility, simplify-control-flow, errors-out-of-existence, no-prototype-swapping, use-intention-revealing-names (chatBar throughout), use-consistent-naming, provide-meaningful-context, no-legacy-api-after-refactor, use-exceptions-properly (CddToolFailed), never-swallow-exceptions (register.ts logs each failure it rides over; board-server.ts isBoardUp turns a failed fetch into "not up", an answer, not a swallowed fault), limit-comments. register.ts, failure.ts, chat-command.ts, board.ts, board-server.ts, session-dialogs-client.ts, fidelity-files-client.ts and stage-client.ts pass every rule. Of the 24 earlier judged fails on this fidelity, every one is resolved; the fails above are new or were graph-only before.
