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


Judge only the checked format's files (python: C:/Users/jeffa/.cdd/runtime-ensure-domain-orientatio/{module}/). The other formats mirror them, so judging those too reports every finding twice.

# Graph rule validation

**Generated:** 2026-11-06 23:20:00 UTC
**Project:** runtime-ensure-domain-orientatio
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\Users\jeffa\.claude\spares\spare-GRHl26\.sessions\ensure-domain-orientation-refactor\edited-graph.json`

## Summary

**Total graph violations:** 53
**Rules with graph hits:** 12
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

Keep one object model. Follow the nouns and verbs the rest of the graph already uses for that concept. A class that joins types the rest of the graph keeps apart is a second model — a big ball of mud — and every rule then has to be written and fixed in both. When data or behavior already belongs to an object, extend that object and hand callers the object itself: `ticket.session.practices["stories"].fidelities["story_map"].files()`, not `ticket.files(["stories-story_map"])`. A second model is rarely a whole class family; more often it is a small copy beside the owner: a dict holding one field from each member (`fidelity_states`, `violation_counts`), a `*_name` copy of a reference (`column_name`), a helper class that does the owner's job (`TicketFiles`), a bag of a few of the owner's answers (`Workspace`), or a `*Model` / `*Entry` family scraped from live objects. A copy hides that the owner is missing the behavior, so the next caller builds another copy and a fix to the owner never reaches it. **Checking it:** this rule spans modules, and the copy looks fine in the file that holds it. For every property, data field, dict, and helper class the changed code adds, name the class that already owns that data and read it; the rule fails when the owner holds it or should, and the change copies it instead of returning or extending the owner. Count the members of a class that delegates: dozens of members on a class that only reads its collaborators means it is copying them.

Evaluate the current context against this rule (do-not-invent-parallel-object-models):

### `hide-inner-details`

Expose behavior through named operations. Do not let callers see how the class stores or arranges its data — once they read the storage directly it becomes a public contract you cannot change. Private fields on the same class hide implementation; you do not need a second class for that. Read-only to callers can mean return a copy or immutable view from a property — it does not require a frozen class or a second type to hold build steps.

Evaluate the current context against this rule (hide-inner-details):

### `keep-operations-small-focused`

Keep each operation short enough to read as one thought — under 20 statements. A multi-line call, list, or string initializer is one statement. When it grows, extract a private helper whose name says why that slice exists.

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L926): Operation `git`: Operation 'git' is 36 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1000): Operation `gh`: Operation 'gh' is 42 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1269): Operation `ensure_issue_type`: Operation 'ensure_issue_type' is 45 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1377): Operation `commit`: Operation 'commit' is 27 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1698): Operation `merge_branch`: Operation 'merge_branch' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Operation `note`: Operation 'note' is 22 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1825): Operation `create_ticket`: Operation 'create_ticket' is 35 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1992): Operation `close_branch`: Operation 'close_branch' is 25 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2020): Operation `switch_worktree`: Operation 'switch_worktree' is 21 lines (max 20).
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2270): Operation `open_in_worktree`: Operation 'open_in_worktree' is 22 lines (max 20).

Evaluate the current context against this rule (keep-operations-small-focused):

### `prefer-instance-operations`

Keep operations on the instance. Do not mark them `@staticmethod` or `@classmethod`. Creation and mapping factories may stay static: `instance`, `create`, `from_*`, camelCase `fromXxx` (e.g. `fromRequest`), `load` / `loadXxx`, plus names in `_STATIC_FACTORY_EXTRA_NAMES` in `operation_checks.py`.

**Graph violations:** 16

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L143): Operation `format`: Operation 'format' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L187): Operation `note_text`: Operation 'note_text' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L205): Operation `backlog`: Operation 'backlog' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L209): Operation `in_progress`: Operation 'in_progress' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L213): Operation `done`: Operation 'done' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L404): Operation `github_ref`: Operation 'github_ref' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L556): Operation `github_status_option`: Operation 'github_status_option' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L571): Operation `github_theme_option`: Operation 'github_theme_option' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L915): Operation `open`: Operation 'open' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L922): Operation `memory`: Operation 'memory' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L926): Operation `git`: Operation 'git' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1000): Operation `gh`: Operation 'gh' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2180): Operation `open`: Operation 'open' is a classmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2188): Operation `cursor_path`: Operation 'cursor_path' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2196): Operation `abbrev_repo_name`: Operation 'abbrev_repo_name' is a staticmethod; prefer an instance operation.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2205): Operation `dirname`: Operation 'dirname' is a staticmethod; prefer an instance operation.

Evaluate the current context against this rule (prefer-instance-operations):

### `keep-operations-single-responsibility`

Give each operation one job. Separate orchestration, from calculation, calculation from I/O and mutation, etc. When an operation does two things, split it or find the missing class. Two jobs mean two reasons to change, often pulling in opposite directions — every change to one can tangle with the other, so the operation breaks for twice as many reasons and stays brittle.

Evaluate the current context against this rule (keep-operations-single-responsibility):

### `simplify-control-flow`

Handle the failing or empty cases first and return. Keep the main path flat. Do not nest more than three levels — deeper than that you cannot tell which conditions hold on a given line without reading back up, and that is where the unhandled branch hides.

Evaluate the current context against this rule (simplify-control-flow):

### `errors-out-of-existence`

For ordinary edges — empty cart, missing optional field, no matches — return an empty result or a quiet no-op. Raise an exception only when something is actually broken. Raising on an ordinary case puts a `try` at every call site to handle something that is not a failure.

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L248): Operation `close`: Operation 'close' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L347): Operation `project_item_id`: Operation 'project_item_id' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L369): Operation `set_status`: Operation 'set_status' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L383): Operation `from_number`: Operation 'from_number' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L915): Operation `open`: Operation 'open' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L926): Operation `git`: Operation 'git' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1000): Operation `gh`: Operation 'gh' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1200): Operation `write_annotated_tag`: Operation 'write_annotated_tag' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1377): Operation `commit`: Operation 'commit' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2044): Operation `close_worktree`: Operation 'close_worktree' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2098): Operation `push_commit`: Operation 'push_commit' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2180): Operation `open`: Operation 'open' raises on an empty or missing value; return a quiet result instead.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2188): Operation `cursor_path`: Operation 'cursor_path' raises on an empty or missing value; return a quiet result instead.

Evaluate the current context against this rule (errors-out-of-existence):

### `no-prototype-swapping`

An object keeps the class it was built as. Do not change it afterwards with `Object.setPrototypeOf`, `__proto__ =`, or `__class__ =`. When a subclass needs to make its own instances, give the base an overridable factory (`blank()`) or build the right class directly. A swapped object skips its constructor, so fields the subclass sets up are missing and nothing tells you.

Evaluate the current context against this rule (no-prototype-swapping):

### `use-intention-revealing-names`

Name each class, property, operation, and parameter so it answers why it exists. Do not abbreviate.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L587): Parameter `value`: Parameter 'value' does not reveal intent.

Evaluate the current context against this rule (use-intention-revealing-names):

### `use-consistent-naming`

Use one word per concept. Pick one verb and use it everywhere (`fetch_`, not a mix of `fetch_`, `get_`, and `retrieve_`). Two words for one concept is how the same logic gets written twice — nobody searching for `fetch_` finds the `retrieve_` that already does the job.

Evaluate the current context against this rule (use-consistent-naming):

### `provide-meaningful-context`

Give a number or literal a name that says why it is there (`SECONDS_PER_DAY`, not `86400`). Do not number variables (`item1`).

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2205): Operation `dirname`: Operation 'dirname' uses the unnamed number 24.

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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2270): Operation `open_in_worktree`: Operation 'open_in_worktree' swallows a caught failure.

Evaluate the current context against this rule (never-swallow-exceptions):

### `limit-comments`

write comment in operations and properties only when the signature cannot say a constraint or explain why the code behaves the way it does. Do not narrate a line that already names what it does.

Evaluate the current context against this rule (limit-comments):

### `avoid-vague-parameter-names`

Do not name parameters `data`, `options`, `info`, or other placeholders that could mean anything. A vague name hides what the caller must supply and what the operation does with it.

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Operation `note`: Parameter 'payload' in 'note' is vague.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1721): Parameter `payload`: Parameter 'payload' is vague. Use a domain-specific name.

Evaluate the current context against this rule (avoid-vague-parameter-names):

### `deep-module`

Keep most classes private (at most **40%** public) in each first-class module. A first-class module is a folder that owns `.context/module-context.md`. Nested folders that also own that file are separate modules — respect them. Nested folders that do not own it roll up to the nearest enclosing module-context folder, or to the folder you are querying if none sits in between. Count classes, not operations: a public method on a hidden class is not a second seam. Every public class is a signature you cannot change without editing every caller, so public classes are much harder to refactor than private ones.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo#L1): Module `repo`: Module 'repo' splits into many tiny classes (18); prefer a deep module with a small public surface.

Evaluate the current context against this rule (deep-module):

### `domain-exception-carries-context`

Use a typed exception for a broken aggregate or repository operation. One exception type may cover that aggregate's operations when it carries the failed operation, the domain object or input already in hand, the user-facing message, and the underlying cause; do not return bare strings or untyped error objects because callers cannot handle them safely..

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2044): Operation `close_worktree`: Operation 'close_worktree' raises NoOpenWorktreeError without context; name the rejected rule.

Evaluate the current context against this rule (domain-exception-carries-context):

### `keep-classes-single-responsibility`

Give each class one reason to change.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L218): OoadClass `ProjectTicket`: Class 'ProjectTicket' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L479): OoadClass `Project`: Class 'Project' exposes 14 public operations (budget ~9). Split responsibilities.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L853): OoadClass `Repo`: Class 'Repo' exposes 65 public operations (budget ~9). Split responsibilities.

Evaluate the current context against this rule (keep-classes-single-responsibility):

### `limit-operation-parameters`

Have callers pass intent, not setup. Prefer 0-3 parameters for domain operations (`self` not counted); when several values form one domain concept, promote them to an object. An external-system operation may accept the explicit record or fields required by its verified contract when combining them would hide that contract. Creation and mapping factories are exempt (`create`, `fromFields`, `fromXxx`, `from_*`, `load` / `loadXxx`, `fromRequest`) — they may take a record or the full field set needed to construct the object.

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L1861): Operation `workflow_commit_message`: Operation 'workflow_commit_message' takes 4 parameters (maximum 3, excluding self).

Evaluate the current context against this rule (limit-operation-parameters):

### `use-explicit-dependencies`

Pass every collaborator through the constructor. Do not reach for a global or construct a collaborator inside construction. A collaborator the class fetches or builds itself cannot be swapped, so the class can only ever run against that one implementation.

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L479): OoadClass `Project`: Class 'Project' constructs 'ProjectTicketState' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L853): OoadClass `Repo`: Class 'Repo' constructs 'Path' inside its constructor.
- [X] **ERROR** **[graph rule]** - [space/repo/repo.py](C:\Users\jeffa\.cdd\runtime-ensure-domain-orientatio\space\repo\repo.py#L2138): OoadClass `Worktree`: Class 'Worktree' constructs 'Path' inside its constructor.

Evaluate the current context against this rule (use-explicit-dependencies):


---

# AI judgment (clean-engineering-code, space/repo)

Graph hits dismissed as false positives:
- `prefer-instance-operations` repo.py:205 `backlog`, :209 `in_progress`, :213 `done`: named constructors of ProjectTicketState. :915 `open`, :922 `memory`, :2180 `Worktree.open`: factories that build a Repo or Worktree.
- `errors-out-of-existence` repo.py:248 `close` (a ticket the repository does not know is a broken invariant), :347 `project_item_id` (GitHub refused to add the item), :383 `from_number` (text that is no issue reference), :915 `open` (not a clone), :926 `git` and :1000 `gh` (tool missing or failing), :1200 `write_annotated_tag` (empty name is a programming error), :1377 `commit` (no paths is a caller error), :2098 `push_commit` (empty message is invalid input), :2180 `Worktree.open`, :2188 `cursor_path`. Each is a real failure, not an ordinary empty case.
- `keep-operations-small-focused` repo.py:1721 `note` (one multi-line call), :1992 `close_branch`, :2020 `switch_worktree`, :2270 `open_in_worktree` (under 20 statements once the docstring is set aside).
- `domain-exception-carries-context` repo.py:2044 `NoOpenWorktreeError`: no domain object is in hand when nothing is open; judged under errors-out-of-existence instead.
- `use-explicit-dependencies` (all three): `ProjectTicketState` and `Path` are values built from arguments, not collaborators.

Graph hits confirmed: `keep-operations-small-focused` repo.py:926, :1000, :1269, :1377, :1698, :1825; `prefer-instance-operations` repo.py:143, :187, :404, :556, :571, :926, :1000, :2188, :2196, :2205; `errors-out-of-existence` repo.py:369, :2044; `use-intention-revealing-names` repo.py:587; `provide-meaningful-context` repo.py:2205; `never-swallow-exceptions` repo.py:2270; `avoid-vague-parameter-names` repo.py:1721; `deep-module` space/repo; `keep-classes-single-responsibility` repo.py:479, :853; `limit-operation-parameters` repo.py:1861. Dismissed `keep-classes-single-responsibility` repo.py:218 `ProjectTicket`: its 14 operations are the ticket's own verbs.

## Judgment — `space/repo/repo.py`

### `do-not-invent-parallel-object-models` — Fail
- repo.py:218 `ProjectTicket`: a second ticket model beside harness/kanban's Ticket, with its own state (`ProjectTicketState` :201), board (`Project` :479), and themes; no production module calls `Repo.ticket`, `create_ticket`, `attach_project`, `ensure_issue_type`, `add_theme` or `ticket_rows` — only repo_heavy_spec.py does. K-F13 is still open in a new form: the per-issue dicts moved onto ProjectTicket, but the family has no production use and duplicates the board's ticket.
- repo.py:519 `ticket_rows`: returns dicts copying ProjectTicket fields (`number`, `title`, `url`, `status`) instead of ProjectTicket objects (:748, :763); it has no caller.
- repo.py:226 `data`: ProjectTicket keeps `closed` as the string `"true"` in a free-form dict (:246, :253, :1834) instead of a field.
- repo.py:1103 `sessions`: Repo is also the registry of sessions (`current_session` :1110, `session_named` :1118, `work_session` :1129, `session_folder` :1140), importing Session inside six operations while Session imports Repo at the top; space/repo and space/session now depend on each other.

### `hold-state-on-the-object-not-in-parameters` — Fail
- repo.py:471 `CliAgentBinding.write_tag`: sets `repo._annotated_tag_target` on the shared Repo for one call and never restores it, so every later `write_annotated_tag` on that Repo tags the last branch instead of HEAD.
- repo.py:1698 `merge_branch`: takes branch names as strings while Branch objects exist; `Branch.merge` (:2311) passes `other.name, self.name` back in. Same for `files_changed_on(branch)` :1181, `cli_agent_tag_name(branch)` :1191, `read_cli_agent_tag(branch)` :1195, `delete_branch(name)` :1440 and `commit` (:2305 hands paths back to Repo).
- repo.py:1861 `workflow_commit_message`: takes `issue_number` though a ProjectTicket would be in hand; it has no caller.

### `hide-inner-details` — Fail
- repo.py:472 `write_tag`: CliAgentBinding writes Repo's private `_annotated_tag_target`.
- repo.py:2302 `head`: Branch reads `Repo._last_commit_message()`, a private operation.

### `keep-classes-single-responsibility` — Fail
- repo.py:853 `Repo`: 65 public operations covering git, GitHub issues and issue types, project boards, git notes and mistakes, annotated cli-agent tags, the session registry, file listing, the MCP branch and worktree tools with their slash-command text, and an in-memory fake. 65 places branch on `self._memory` / `in_memory`, so every operation carries a test double beside its real body; `commits` (:1921), `pushes` (:1927), `_branches` (:1933) and `mark_dirty` (:1350) exist only for that double and raise on a real repository.
- repo.py:479 `Project`: 14 public operations mixing the board's states with raw `gh project` plumbing (field lists, option ids, item ids).

### `keep-operations-small-focused` — Fail
- repo.py:1269 `ensure_issue_type`: 45 lines holding the lookup, the in-memory insert, and the gh POST.
- repo.py:1825 `create_ticket`: 35 lines with an in-memory branch and a gh branch.
- repo.py:1377 `commit`: the merge-in-progress branch repeats the add, diff and commit sequence of the normal path.
- repo.py:1698 `merge_branch`: in-memory fake, worktree lookup and two merge forms in one body.

### `eliminate-duplication` — Fail
- repo.py:926 `git` and :1000 `gh`: each finds its executable through the same Windows fallback loop, wraps timeouts and OSError, and formats the failure message; one process runner would serve both.
- repo.py:190 `note_payload`: parses `Key: value` lines again next to `data` (:173), differing only in whether values are stripped and whether the subject line counts (K-F12 still open).
- repo.py:1118 `session_named` and :1129 `work_session`: one lookup with two behaviours on a missing session (raise against None).

### `prefer-instance-operations` — Fail
- repo.py:926 `git`, :1000 `gh`: classmethods that take the folder to run in; `merge_branch` (:1714) and latest_release.py:86 call them on another folder instead of asking that folder's Repo.
- repo.py:2205 `dirname`, :2196 `abbrev_repo_name`, :2188 `cursor_path`: static helpers; the worktree folder name belongs on Branch or Repo, and `cursor_path` has no caller.
- repo.py:143 `format`, :187 `note_text`, :404 `github_ref`, :556 `github_status_option`, :571 `github_theme_option`: classmethods that compute strings; :114 `theme_slug` and :122 `issue_theme_label` are free functions for the same theme concept.

### `errors-out-of-existence` — Fail
- repo.py:2044 `close_worktree`: raises NoOpenWorktreeError when no worktree is open, an ordinary state; returning "no worktree open" keeps callers free of a try.
- repo.py:373 `set_status`: raises when no project is attached, while `write_project_theme` (:339) returns quietly in the same situation.

### `use-exceptions-properly` — Fail
- repo.py:241 `_require_repo`: raises RuntimeError; also :373, :1353, :1923, :1929, :1935, and ValueError with a message at :505, :650, :677, :679, :691, :746.
- repo.py:1816 `_github_ticket`: decides "not found" by searching the GhConnectError message text.

### `never-swallow-exceptions` — Fail
- repo.py:2286 `open_in_worktree`: `except RepoConnectError: pass` drops a failed fetch without a log line.
- repo.py:2218 `Worktree.fetch_pull`: returns silently when fetch or pull fails, so a worktree can open on stale code with no sign.
- repo.py:787 `theme_option_names`: turns GhConnectError into an empty list, while `status_option_names` (:516) converts the same error to a scope error.

### `use-intention-revealing-names` — Fail
- repo.py:409 `CliAgentBinding`: banned word (binding); the class is the doer and judge CLI agents of a branch. Also `bind_repo` :235.
- repo.py:383 `from_number`: named as a factory but parses a reference into an int.
- repo.py:587 `write_text_field(ticket, value)`: `value` is the Ultimate Parent text.
- repo.py:2196 `abbrev_repo_name`: abbreviated name.

### `provide-meaningful-context` — Fail
- repo.py:2210 `dirname`: unnamed 24 (longest branch part kept in a folder name); also `0x1000` at :459, `"1000"` item limits at :530 and :738, and the hard-coded themes at :784.

### `avoid-vague-parameter-names` — Fail
- repo.py:1724 `note`: `payload` is the note's fields.

### `no-legacy-api-after-refactor` — Fail
- repo.py:2298 `head`: `from space.repo.repo import Commit` inside space/repo/repo.py itself (also :2306, :2312), left from when Branch lived in its own module.
- repo.py:1147 `session_folder`: still searches `LEGACY_SESSIONS_FOLDER`.
- repo.py:1759 `find_mistakes`, :1861 `workflow_commit_message`, :2188 `cursor_path`, :519 `ticket_rows`, :587 `write_text_field`: no production or spec caller (find_mistakes, read_notes, ticket_rows, write_text_field, workflow_commit_message, cursor_path) — dead seams kept in the public surface.

### `limit-operation-parameters` — Fail
- repo.py:1861 `workflow_commit_message`: four parameters; the issue and its workflow state are one concept.

### `deep-module` — Fail
- repo.py:853 `Repo`: the module has 18 classes and space/repo/__init__.py exports 13 names, including CliAgentBinding, Project, ProjectTicket, ProjectTicketState and `issue_theme_label`, none of which a production module imports.

## Judgment — `space/repo/latest_release.py`

### `prefer-instance-operations` — Fail
- latest_release.py:86 `_git`: calls the classmethod `type(self._repository).git(self._repository.root, ...)` instead of an operation on the Repo it holds, because Repo's instance `_git` cannot take an environment or timeout.

Passes on latest_release.py otherwise: operations are small, names are clear, and the constants are named.
