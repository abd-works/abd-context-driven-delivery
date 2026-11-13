# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
1b. **Stories in the session's scope.** A session's ticket names its stories (its `Story:` headings); they are the increment. Every one of them is generated and validated with the patterns its content is generated with: generate uses the session's overlays and records them in `.context/patterns.md` at the root of each folder it writes, with the roles the folder holds of a pattern whose layers sit in several folders; validate reads that file. Stories the ticket does not name belong to other increments: leave them alone, and do not judge or report them. **Measure the scope, not the repository:** the graph report keeps only the findings inside the work's scope, on those stories and everything under them (their scenarios, steps, and examples) and in the files the call names; name, as paths, exactly the modules and tests the work changed. Judge only those too.
1c. **Patterns used in part.** The graph checks content against every applied pattern's schema and rules mechanically (`conforms-to-schema` and each pattern's rules), so a pattern used only in part reports members its content never meant to have. Judge each such finding against the patterns' own instructions and the patterns the content was generated with (`.context/patterns.md`, with the roles a folder holds): when another applied pattern supplies that member in its own way, the finding is noise; say so in the judgment and name the pattern that covers it (LERN overlaid with cdd_web_domain_access has its domain in Python behind MCP, so LERN's TypeScript domain, node tier, routes and lowdb store are not expected). Every other finding stands.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the session's graph (`graph.json` in the session's own folder, created for the session); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `harness/.context/stories/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge only the checked format's files (markdown: stories/story-map.md). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-13 00:45:12 UTC
**Project:** .context
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-review-work-in-board-fil\.sessions\review-work-in-board-files\validation-reports\stories-story-map-20261113T004434.json`

**The session's graph also held, and practice-wide rules compared against:**
- `author-story-maps/author-story-changes-with-ai`
- `author-story-maps/save-and-share-changes`
- `author-story-maps/view-story-map`
- `build-design-canvas-screens/publish-and-release-a-canvas-version`
- `connect-sessions-across-channels-and-apps/check-work-in-generate`
- `connect-sessions-across-channels-and-apps/connect-chat-bar-board-and-story-ui`
- `connect-sessions-across-channels-and-apps/read-graph-violations-in-chat-bar`
- `connect-sessions-across-channels-and-apps/read-graph-violations-on-board`
- `explore-stories-in-story-ui/frame-design-canvas-screens-in-explorer`
- `explore-stories-in-story-ui/navigate-the-story-tree`
- `explore-stories-in-story-ui/play-stories-in-the-explorer`
- `explore-stories-in-story-ui/show-screen-frames-in-story-ui`
- `map-work-into-knowledge-graph/review-violations-in-graph-app`
- `move-work-forward-from-chat-bar/capture-session-knowledge`
- `move-work-forward-from-chat-bar/enter-cdd-commands-faster`
- `move-work-forward-from-chat-bar/generate-fidelity-outputs-in-chat-bar`
- `move-work-forward-from-chat-bar/guide-work-through-practices`
- `move-work-forward-from-chat-bar/integrate-practice-content-editor-apps-in-chat-bar`
- `move-work-forward-from-chat-bar/see-work-in-chat-bar`
- `move-work-forward-from-chat-bar/steer-sessions`
- `move-work-forward-on-session-board/guide-work-through-practices-on-board`
- `move-work-forward-on-session-board/integrate-practice-content-editor-apps-on-board`
- `move-work-forward-on-session-board/maintain-tickets`
- `move-work-forward-on-session-board/organize-ticket-hierarchy`
- `move-work-forward-on-session-board/see-work-on-session-board`
- `move-work-forward-on-session-board/steer-ticket-sessions`
- `move-work-forward-on-session-board/work-fidelity-outputs-on-board`
- `stories/author-story-maps`
- `stories/build-design-canvas-screens`
- `stories/connect-sessions-across-channels-and-apps`
- `stories/explore-stories-in-story-ui`
- `stories/map-work-into-knowledge-graph`
- `stories/move-work-forward-from-chat-bar`
- `stories/move-work-forward-on-session-board`

## Summary

**Total graph violations:** 1
**Rules with graph hits:** 1
**AI rules in scope:** 12

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-domain-source`

Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-requirements`

Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.

Evaluate the current context against this rule (do-not-invent-requirements):

### `verb-noun-format`

Name every Epic, Sub-Epic, and Story with a base-form verb and noun. Epics and Sub-Epics name goals rather than an actor's activity or a supporting system call, because grammar alone does not preserve the right level of abstraction.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [stories/story-map.md](C:\dev\abd-cdd-review-work-in-board-fil\harness\.context\stories\story-map.md#L571): Story `Comment On File Selection`: Story 'Comment On File Selection': name should start with a verb (got nominalisation).

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, and restructure at 3 or fewer or 10 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-at-most-seven`

A story holds at most 7 code scenarios. More than 7 and the story is huge — split it, because one story should be one interaction a reader can test in a few examples. A story with no scenarios passes: its scenarios are simply not written yet.

Evaluate the current context against this rule (story-scenarios-at-most-seven):

### `branch-on-mechanical-uniqueness`

Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.

Evaluate the current context against this rule (branch-on-mechanical-uniqueness):

### `right-size-story-nodes`

Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.

Evaluate the current context against this rule (right-size-story-nodes):

### `behaviours-not-one-time-tasks`

Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

Evaluate the current context against this rule (behaviours-not-one-time-tasks):

### `kebab-case-paths`

Name every epic, sub-epic, and story folder in lowercase kebab-case (`onboard-a-customer/`) and every story file in lowercase (`create_customer_story.test.ts`, `create-customer.story.shared.ts`), never CamelCase (`HandleRequest_story.test.ts`), because the folders mirror the story map and a reader finds a story's file from its name only when one case holds everywhere.

Evaluate the current context against this rule (kebab-case-paths):

### `story-map-links-to-markdown`

Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

Evaluate the current context against this rule (story-map-links-to-markdown):


Judge the work against these overlaid patterns' rules too, as you judge the practices' rules.

## Stories in this session

This session's increment is these stories, named in its ticket. Generate and validate every one of them with the patterns its content is generated with (none). Stories outside this list belong to other increments: do not generate, judge, or report them.

- List Ticket Context Files
- Open Session Files From Details
- View Files In Rich Viewer
- Save Edited File
- Comment On File Selection
- Send File Comments To Chat
- Show AI Changes As Diff
## Judgment — `harness/.context/stories/story-map.md`

### `verb-noun-format` — Fail
- story-map.md:571 `Comment On File Selection`: the graph reads "Comment" as a noun, so the story does not open with a base-form verb; rename it to Add Comment To File Selection.

Passes: `four-to-nine-children` (Review Fidelity Outputs On Board and Review Files In Viewer hold 5 stories each; Work Fidelity Outputs On Board holds 5 sub-epics), `story-map-links-to-markdown` (the new stories have no files yet and stay plain text), `do-not-invent-requirements` (Save Edited File and Send File Comments To Chat quote the person's 2026-11-12 request), `right-size-story-nodes`, `branch-on-mechanical-uniqueness`, `behaviours-not-one-time-tasks`, `story-name-captures-system-mechanic`, `kebab-case-paths`, `vocabulary-traces-to-domain-source`, `read-all-source-context-in-full`, `story-scenarios-at-most-seven`.
