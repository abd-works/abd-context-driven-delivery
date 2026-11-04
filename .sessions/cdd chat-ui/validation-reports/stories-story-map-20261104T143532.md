# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Write the judgment in this shape, because the session board reads it and lists each finding beside the graph's hits, with a Fix that sends it back:

   ```markdown
   ## Judgment — `path/of/the/judged/file.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   One `###` heading per rule that fails, with Fail after the dash. One bullet per finding, opening with the judged file's name and the line, so a person can open the finding at that line. Leave passing rules out of these headings; a table or a Passes paragraph may list them.


# Graph rule validation

**Generated:** 2026-11-04 14:35:31 UTC
**Project:** abd-cdd-session-board
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\cdd chat-ui\edited-graph.json`

## Summary

**Total graph violations:** 138
**Rules with graph hits:** 6
**AI rules in scope:** 11

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

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): SubEpic `Document Behavior Slice`: SubEpic 'Document Behavior Slice': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Run Install Command`: Story 'Run Install Command': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Document Specification Slice`: Story 'Document Specification Slice': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Document Engineering Slice`: Story 'Document Engineering Slice': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Run Story Tests`: Story 'Run Story Tests': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Advance Coverage Increment`: Story 'Advance Coverage Increment': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L93): Story `Partition Selected Context`: Story 'Partition Selected Context': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L147): Story `Document Specification Slice`: Story 'Document Specification Slice': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L171): Story `Document Engineering Slice`: Story 'Document Engineering Slice': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L196): Story `Run Story Tests`: Story 'Run Story Tests': name should start with a verb (got generic-verb).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L253): Story `Advance Coverage Increment`: Story 'Advance Coverage Increment': name should start with a verb (got nominalisation).

Evaluate the current context against this rule (verb-noun-format):

### `story-name-captures-system-mechanic`

At Story level, use a verb that names the operation and a noun that names the record or concept it acts on. Replace vague names such as `Handle Request`, `Process Data`, or `Manage Record`, because they hide what the system does.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Run Install Command`: Story 'Run Install Command' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Run Story Tests`: Story 'Run Story Tests' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L196): Story `Run Story Tests`: Story 'Run Story Tests' names a generic handler; use the system mechanic (e.g. 'Submit Order').

Evaluate the current context against this rule (story-name-captures-system-mechanic):

### `four-to-nine-children`

Keep 4-9 direct children on an epic or sub-epic, and restructure at 3 or fewer or 10 or more, because readers cannot reason easily about shallow chains or crowded nodes. Do not apply this band to the scenarios under a story.

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L24): Epic `Install CDD Tools`: epic 'Install CDD Tools': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L25): SubEpic `Install Agent Toolset`: sub-epic 'Install Agent Toolset': 16 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L48): SubEpic `Install Action Classes`: sub-epic 'Install Action Classes': 2 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L81): SubEpic `Open Practice Catalog`: sub-epic 'Open Practice Catalog': 1 children (target 4-9)

Evaluate the current context against this rule (four-to-nine-children):

### `story-scenarios-one-to-four`

A story's code scenarios number 1 to 7. More than 7 and the story is huge — split it. A story with no scenarios is not a story yet.

**Graph violations:** 117

- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Run Install Command`: story 'Run Install Command': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Publish Markdown Installation`: story 'Publish Markdown Installation': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Publish Mcp Manifest`: story 'Publish Mcp Manifest': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Publish Hooks Manifest`: story 'Publish Hooks Manifest': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Open Practice Catalog`: story 'Open Practice Catalog': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Capture Live Application`: story 'Capture Live Application': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Classify External Dependencies`: story 'Classify External Dependencies': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Write Boundary Stubs`: story 'Write Boundary Stubs': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Smoke Test Application`: story 'Smoke Test Application': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Scout Application Pages`: story 'Scout Application Pages': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Complete Capture Pages`: story 'Complete Capture Pages': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Open Capture Session`: story 'Open Capture Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Request Discovery Scaffold`: story 'Request Discovery Scaffold': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Confirm Practice Lenses`: story 'Confirm Practice Lenses': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Name Journey Stories`: story 'Name Journey Stories': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Name Context Aggregates`: story 'Name Context Aggregates': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Document Specification Slice`: story 'Document Specification Slice': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Capture Story Scenarios`: story 'Capture Story Scenarios': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Capture Aggregate Operations`: story 'Capture Aggregate Operations': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Document Engineering Slice`: story 'Document Engineering Slice': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Write Story Tests`: story 'Write Story Tests': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Write Domain Wraps`: story 'Write Domain Wraps': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Run Story Tests`: story 'Run Story Tests': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Review Story Meaning`: story 'Review Story Meaning': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Accept Stage View`: story 'Accept Stage View': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Log Behavior Mistake`: story 'Log Behavior Mistake': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Record Mistake Entry`: story 'Record Mistake Entry': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Log Behavior Correction`: story 'Log Behavior Correction': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Nest Correction Repair`: story 'Nest Correction Repair': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Advance Coverage Increment`: story 'Advance Coverage Increment': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Cover Distinct Behaviors`: story 'Cover Distinct Behaviors': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Request Session Handoff`: story 'Request Session Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.drawio](C:\dev\abd-cdd-session-board\.context\story-map.drawio#L2): Story `Write Handoff Document`: story 'Write Handoff Document': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L26): Story `Generate Installer Skill`: story 'Generate Installer Skill': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L27): Story `Generate skills and commands from Agent Toolset`: story 'Generate skills and commands from Agent Toolset': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L28): Story `Generate Skills and Commands With MCP Calls`: story 'Generate Skills and Commands With MCP Calls': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L29): Story `Enroll Agent Toolset as MCP Tools`: story 'Enroll Agent Toolset as MCP Tools': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L30): Story `Configure and Start MCP Host Session`: story 'Configure and Start MCP Host Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L31): Story `Register Agent Toolsets as Cursor hooks`: story 'Register Agent Toolsets as Cursor hooks': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L33): Story `Deploy Guidance Instructions`: story 'Deploy Guidance Instructions': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L34): Story `Deploy Guidance Rules`: story 'Deploy Guidance Rules': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L35): Story `Clean previously installed skills`: story 'Clean previously installed skills': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L36): Story `Install While preserving skills from prior installed Skills`: story 'Install While preserving skills from prior installed Skills': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L37): Story `Install While preserving skills from other sources`: story 'Install While preserving skills from other sources': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L38): Story `Cleanse previously installed MCP tools`: story 'Cleanse previously installed MCP tools': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L39): Story `Install MCP to User Project Specific Location`: story 'Install MCP to User Project Specific Location': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L40): Story `Raise Error on Install Failure`: story 'Raise Error on Install Failure': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L41): Story `Diagnose the finished install`: story 'Diagnose the finished install': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L43): Story `Deploy Practice guidance instructions`: story 'Deploy Practice guidance instructions': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L44): Story `Deploy Practice guidance rules`: story 'Deploy Practice guidance rules': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L45): Story `Deploy Practice guidance fidelities`: story 'Deploy Practice guidance fidelities': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L46): Story `Deploy Practice guidance fidelity instructions`: story 'Deploy Practice guidance fidelity instructions': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L47): Story `Deploy Practice guidance fidelity rules`: story 'Deploy Practice guidance fidelity rules': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L49): Story `Install Lifecycle actions`: story 'Install Lifecycle actions': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L50): Story `Install Lifecycle actions as several tools`: story 'Install Lifecycle actions as several tools': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L53): Story `Open New Session`: story 'Open New Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L54): Story `Select Existing Session`: story 'Select Existing Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L55): Story `Open Session Loop`: story 'Open Session Loop': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L56): Story `Remember Practice Folders`: story 'Remember Practice Folders': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L58): Story `Record Session Action`: story 'Record Session Action': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L59): Story `Record Validation Run`: story 'Record Validation Run': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L60): Story `Attach Action Chat`: story 'Attach Action Chat': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L61): Story `Record Session Error`: story 'Record Session Error': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L63): Story `Load Practice Guideline`: story 'Load Practice Guideline': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L64): Story `Reset Process Session`: story 'Reset Process Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L65): Story `Persist Hook Session`: story 'Persist Hook Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L66): Story `Hold Mcp Session`: story 'Hold Mcp Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L68): Story `Switch Branch`: story 'Switch Branch': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L69): Story `Create Branch`: story 'Create Branch': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L70): Story `Close Branch`: story 'Close Branch': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L71): Story `Merge Branch`: story 'Merge Branch': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L72): Story `Commit Branch`: story 'Commit Branch': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L73): Story `Push Branch`: story 'Push Branch': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L75): Story `List Worktree`: story 'List Worktree': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L76): Story `Open Worktree`: story 'Open Worktree': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L77): Story `Reuse Worktree`: story 'Reuse Worktree': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L78): Story `Remove Worktree`: story 'Remove Worktree': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L79): Story `Fetch Worktree`: story 'Fetch Worktree': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L82): Story `Open Practice Catalog`: story 'Open Practice Catalog': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L90): Story `Convert Documents To Markdown`: story 'Convert Documents To Markdown': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L91): Story `Review Document Structure`: story 'Review Document Structure': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L92): Story `Choose Indexer Practices`: story 'Choose Indexer Practices': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L93): Story `Partition Selected Context`: story 'Partition Selected Context': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L94): Story `Embed Segment Files`: story 'Embed Segment Files': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L95): Story `Search Ranked Chunks`: story 'Search Ranked Chunks': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L96): Story `Answer Question With Citations`: story 'Answer Question With Citations': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L98): Story `Capture Live Application`: story 'Capture Live Application': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L99): Story `Classify External Dependencies`: story 'Classify External Dependencies': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L100): Story `Write Stub Focus Documents`: story 'Write Stub Focus Documents': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L101): Story `Write Boundary Stubs`: story 'Write Boundary Stubs': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L102): Story `Smoke Test Application`: story 'Smoke Test Application': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L103): Story `Smoke Test Desktop Process`: story 'Smoke Test Desktop Process': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L104): Story `Scout Application Pages`: story 'Scout Application Pages': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L105): Story `Review Capture Verdicts`: story 'Review Capture Verdicts': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L106): Story `Complete Capture Pages`: story 'Complete Capture Pages': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L108): Story `Open Capture Session`: story 'Open Capture Session': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L111): Story `Request Discovery Scaffold`: story 'Request Discovery Scaffold': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L114): Story `Confirm Practice Lenses`: story 'Confirm Practice Lenses': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L140): Story `Name Journey Stories`: story 'Name Journey Stories': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L143): Story `Name Context Aggregates`: story 'Name Context Aggregates': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L147): Story `Document Specification Slice`: story 'Document Specification Slice': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L164): Story `Capture Story Scenarios`: story 'Capture Story Scenarios': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L167): Story `Capture Aggregate Operations`: story 'Capture Aggregate Operations': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L171): Story `Document Engineering Slice`: story 'Document Engineering Slice': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L174): Story `Write Story Tests`: story 'Write Story Tests': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L186): Story `Write Domain Wraps`: story 'Write Domain Wraps': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L196): Story `Run Story Tests`: story 'Run Story Tests': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L200): Story `Review Story Meaning`: story 'Review Story Meaning': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L215): Story `Accept Stage View`: story 'Accept Stage View': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L225): Story `Log Behavior Mistake`: story 'Log Behavior Mistake': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L236): Story `Record Mistake Entry`: story 'Record Mistake Entry': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L241): Story `Log Behavior Correction`: story 'Log Behavior Correction': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L244): Story `Nest Correction Repair`: story 'Nest Correction Repair': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L253): Story `Advance Coverage Increment`: story 'Advance Coverage Increment': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L262): Story `Cover Distinct Behaviors`: story 'Cover Distinct Behaviors': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L265): Story `Request Session Handoff`: story 'Request Session Handoff': 0 scenarios (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L268): Story `Write Handoff Document`: story 'Write Handoff Document': 0 scenarios (target 1-7)

Evaluate the current context against this rule (story-scenarios-one-to-four):

### `branch-on-mechanical-uniqueness`

Create separate Stories for distinct mechanics and use Scenarios or examples when several source entries share one mechanic, because one Story per source entry duplicates behaviour while one Story for different mechanics hides work.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L42): SubEpic `Install Practice Guidance Class`: Stories under 'Install Practice Guidance Class' share the same verb 'deploy'; split by distinct mechanics or merge.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L48): SubEpic `Install Action Classes`: Stories under 'Install Action Classes' share the same verb 'install'; split by distinct mechanics or merge.

Evaluate the current context against this rule (branch-on-mechanical-uniqueness):

### `right-size-story-nodes`

Put one observable interaction at one system boundary in each Story. Keep the caller's request, response, and translation together; give the callee its own boundary Story; keep display-only and forwarding-only work as outcomes, because splitting every internal call or interface step obscures the interaction being tested.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-session-board\.context\story-map.md#L30): Story `Configure and Start MCP Host Session`: Story 'Configure and Start MCP Host Session' is too similar to another story on the same map node.

Evaluate the current context against this rule (right-size-story-nodes):

### `behaviours-not-one-time-tasks`

Use Stories for repeatable stakeholder or system interactions that can be expressed as GWT more than once. Keep one-time renames, migrations, and repository changes in plans or tasks, because completed maintenance is not recurring product behaviour.

Evaluate the current context against this rule (behaviours-not-one-time-tasks):

### `story-map-links-to-markdown`

Link every Epic, Sub-Epic, and Story on the map to its entry in `story-map.md`, and link a Story to its own markdown file when one exists. Anchor an entry link at the node's heading (`story-map.md#e-get-sim`); in drawio, put the link on the cell's `link`. Never indent a heading: write each at column 0 and let the `#` count carry the depth. Write plain text when the target file does not exist, because a reader should move from a map node to the behaviour it names without searching, and a link to a missing file misleads.

Evaluate the current context against this rule (story-map-links-to-markdown):
