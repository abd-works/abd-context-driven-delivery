# Refactor guardrails

Every agent changing code on this branch reads this before writing code and checks its diff against it before committing. Each rule comes from a fix already made here (decision numbers refer to the table at the end of `clean-engineering-validation.md`); reintroducing one of these problems undoes that fix.

## 1. Resource-oriented design: objects hold their collaborators

- **An object holds what it works with.** A collaborator arrives through the constructor or is a part the owner builds once and keeps. A method asks its own fields; it does not take the same object as a parameter on every call. Passing the owner's data back into a helper, or a node back into its own practice (`node.practice.checks_for(node)`), puts logic on the wrong object — ask the owner (`node.rules`).
- **No parameter passing that the object could hold.** If several methods of one class all take the same argument, that argument is a field. If a call passes `project`, `session` or `root` down through three layers, the lowest object should already hold it (decision 18: one `ToolCall` holds the call's project and session).
- **Hold references, never look up by name.** Do not pass a practice, toolset, fidelity, stage or session around as a string and look it up again in a registry. Keep the object (decisions 16, 19, 30, 36).
- **Build once, keep it.** Do not rebuild a part per call from paths, strings or dicts (Repo's Git and Worktrees, Session's Repo and Handoffs, Markdown's text, a Format built from a string).
- **One owner per file.** A file is read and written by the one object that owns it; others ask that object (decision 34: one owner chain for a practice's folder; decision 31: one `SavedGraph`).
- **No global "current" objects** (decision 18).

## 2. No duplicated shapes

- **One class per concept.** Before adding a class, search for one that already models it; extend or reuse it. Fixed here: five rule-hit shapes became one `Violation` (17); three saved-graph shapes became one `SavedGraph` (31); a second ticket model was deleted (2); `SourceText` exists twice and must become one.
- **No parallel object models.** A format adapter subclasses or reads the domain model; it does not copy it into a second set of classes.
- **One registry per kind.** `PracticeCatalogue` for practices, `ActionCatalogue` for actions (14). Do not add another list, dict or registry of the same things.
- **One definition of each stage** in `stages.py` (15).

## 3. No duplicated functionality

- **One way to do each job.** Before writing a function, search for an existing one that does it (grep the verb and the noun). Call it, or move it onto its owner and call it from both places.
- **No legacy API after a refactor.** Delete the old name; update every caller, spec, doc and card in the same change. No aliases, wrappers or shims (`.claude/rules/coding.md`).
- **No use → delete.** Code kept alive only by its own spec is deleted with that spec (11).
- **The framework does not know the practices.** `harness/` imports nothing from `space/`, `tools/` or `cdd_guidance/`; they register with it (16, 22, 32).

## Before you commit

Read your own diff and answer, in your final report, for each new or changed class and method:
1. Does it take a parameter its object could hold? (If yes, make it a field.)
2. Does a class or function that does the same job already exist? (Name the grep you ran.)
3. Did you look anything up by a name string that you could have held as a reference?
4. Is any old name still alive?
