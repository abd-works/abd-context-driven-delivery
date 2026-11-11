# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the saved graph of the session's folder (`.context/graph.json`, which exists only after `graph.load_working_copy` has run on that folder); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Append the judgment to the end of the saved report in exactly this shape. The session board parses it, lists each finding beside the graph's hits, opens the finding's file at its line, and sends a Fix back, so a finding in any other shape is lost:

   ```markdown
   ## Judgment — `space/kanban/.context/story-map.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   - **One `## Judgment — ` section per judged file,** with an em dash, and the file in backticks as a path from the project's root, the way the session names paths. Never an absolute path or another checkout's path, because the board opens the file in this project and cannot open one anywhere else.
   - **One `### ` heading per rule that fails:** the rule slug in backticks, an em dash, then `Fail`. Leave passing rules out of these headings; a table or a Passes paragraph after the judgment may list them.
   - **One bullet per finding,** opening with the judged file's name, a colon, and one line number (`story-map.md:86`), then a space and what breaks the rule. A finding that spans lines takes its first line, and a finding at two places is two bullets, because the board opens each finding at one line.


Judge the graph validate built from the checked format's files (python: C:/dev/abd-cdd-canvas-format-chip/{module}/), saved at C:\dev\abd-context-driven-delivery\.sessions\show-the-design-canvas-format\validation-reports\clean-engineering-code-20261111T172506.json: its classes, operations, parameters, properties, relationships, and dependencies, against each rule. Read a file only to see what a node stands for; whether a model document matches the code is a separate, secondary check.

# Graph rule validation

**Generated:** 2026-11-11 17:25:09 UTC
**Project:** abd-cdd-canvas-format-chip
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\show-the-design-canvas-format\validation-reports\clean-engineering-code-20261111T172506.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `cdd_guidance`
- `cdd_guidance/actions`
- `harness`
- `harness/chat-ui`
- `space/kanban`

## Summary

**Total graph violations:** 44
**Rules with graph hits:** 5
**AI rules in scope:** 20

## Rules

Each rule shows its guidance text, any graph scanner hits (`**[graph rule]**`), then the AI judgment prompt.

### `vocabulary-traces-to-source`

Take every term from the source. The English term and the code name are the same word: *shopping cart* is `ShoppingCart`. When the code says a different word than the domain, every reader keeps a translation in their head, and the two names drift until they mean different things.

Evaluate the current context against this rule (vocabulary-traces-to-source):

### `do-not-invent-terms`

Do not invent a second noun or a parallel vocabulary. A second noun for the same thing becomes a second class, and then the same rule has to be written and fixed in both.

Evaluate the current context against this rule (do-not-invent-terms):

### `do-not-invent-parallel-object-models`

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story-map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `hold-state-on-the-object-not-in-parameters`

Keep what an object knows on the object, and let its operations read it there. A session holds its practices, a practice holds its fidelities and its current fidelity, a fidelity holds its actions and the format it last used, and an action is made for its session: `session.practices.stories.fidelities.story_map.actions.generate(format="drawio")`, not `Generate.commands_for(session, fidelities, formats)`. A value the caller supplies once, such as a format, is saved on the object that owns it, so the next operation on that object reads it instead of being handed it again. The rule fails when an operation takes, as a parameter, state its own object holds or should hold: the same argument handed down through several layers; a session, guidance, or ticket passed to every call on an object made for it; a name or slug passed so the receiver can look up an object the caller already holds; state written into a string (`session=...`) and parsed back; or a field set on a shared object for one call and restored afterwards. Every layer that passes the value is another place to pass the wrong one, and a call started from inside another, which nobody hands the value to, falls back to a global such as the current session and acts on the wrong object.

Evaluate the current context against this rule (hold-state-on-the-object-not-in-parameters):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L591): Property `session_context`: Property 'session_context' is 25 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not annotate them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, `now` (a new value for this moment), and `every` (each value the class allows). A global accessor such as `current` or `shared` is not a factory: it hands every caller the same object from class-level state, so it stays an instance operation on the object that holds that state, or goes.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure. A missing required argument is a broken call, not an ordinary edge: refuse it with a failure the program declares and names (`CommitPathsRequiredError`), which `domain-exception-carries-context` then asks to carry the rejected value.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 12

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate.py](C:\dev\abd-cdd-canvas-format-chip\cdd_guidance\actions\generate\generate.py#L95): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L131): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L163): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L291): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L297): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L310): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L472): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L490): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L494): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L508): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L547): Parameter `item`: Parameter 'item' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L550): Parameter `item`: Parameter 'item' does not reveal intent.

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

Raise a domain exception that names the failure (`CartAlreadyCheckedOut`, not `Error` or a bare string). Catch the specific type you can handle. Do not use a bare `except`, and do not catch `Exception` (or `BaseException`) to return a default or substitute a fallback value: that turns every failure, including a bug, into the ordinary answer. A generic exception cannot be caught selectively, so the caller has to handle everything or nothing.

Evaluate the current context against this rule (use-exceptions-properly):

### `never-swallow-exceptions`

Do not catch and ignore. Log and re-raise, or convert to a domain exception that still names the failure. An `except Exception` that returns, `pass`es, or substitutes a fallback (an empty dict, `None`, the input unchanged) is swallowing too: the caller reads the fallback as a real answer, so a broken invariant reaches the next step unseen.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `source-parses`

Keep every source file valid in its language. A file that does not parse is read into no classes, so every other rule passes it without looking, and its problems stay hidden until it runs.

Evaluate the current context against this rule (source-parses):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 6

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L631): Operation `inject_rules`: Parameter 'payload' in 'inject_rules' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L631): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L641): Operation `_listed_inject_parts`: Parameter 'payload' in '_listed_inject_parts' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L641): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L651): Operation `_payload_is_this_action`: Parameter 'payload' in '_payload_is_this_action' is vague.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L651): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L370): OoadClass `GuidanceAction`: Class 'GuidanceAction' exposes 20 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `use-typed-signatures`

Use typed public signatures. Do not put vanilla `dict`, `Any`, or untyped lists on them — an untyped bag moves every shape error to runtime and leaves the caller guessing which keys are required.

**Graph violations:** 24

- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate.py](C:\dev\abd-cdd-canvas-format-chip\cdd_guidance\actions\generate\generate.py#L69): Parameter `current`: Parameter 'current' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate.py](C:\dev\abd-cdd-canvas-format-chip\cdd_guidance\actions\generate\generate.py#L75): Parameter `fidelity`: Parameter 'fidelity' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/actions/generate/generate.py](C:\dev\abd-cdd-canvas-format-chip\cdd_guidance\actions\generate\generate.py#L95): Parameter `item`: Parameter 'item' is missing a type annotation.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L58): Parameter `guidance`: Parameter 'guidance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L66): Parameter `guidance`: Parameter 'guidance' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L131): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L163): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L220): Parameter `session`: Parameter 'session' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L291): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L297): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L310): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L317): Parameter `raw`: Parameter 'raw' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L334): Parameter `made`: Parameter 'made' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L389): Parameter `session`: Parameter 'session' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L411): Parameter `session`: Parameter 'session' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L472): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L490): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L494): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L508): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L547): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L550): Parameter `item`: Parameter 'item' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L662): Parameter `action`: Parameter 'action' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L666): Parameter `action`: Parameter 'action' needs a domain-specific type, not a generic container.
- [X] **ERROR** **[graph rule]** - [harness/guidance_actions/guidance_actions.py](C:\dev\abd-cdd-canvas-format-chip\harness\guidance_actions\guidance_actions.py#L666): Parameter `fidelity`: Parameter 'fidelity' needs a domain-specific type, not a generic container.

Evaluate the current context against this rule (use-typed-signatures):

## Judgment — `harness/guidance_actions/guidance_actions.py`

### `use-typed-signatures` — Fail
- guidance_actions.py:66 `overlays_named`: its guidance parameter was typed Any; fixed in this pass to GuidanceArg.

Every other graph hit above is on code this pass did not change (the `item` and `payload` parameters, `session_context`, GuidanceAction's size, and Generate's `_fidelity_before` and `_existing_files`). The new `Generate._overlay_rules` and `_overlay_rules_of`, `WorkList.take`'s overlays word, and the chat bar's `overlayArgumentOf` and `pressAction` pass the rules: each does one job, takes typed parameters, and reads the overlays from the session that owns them.
