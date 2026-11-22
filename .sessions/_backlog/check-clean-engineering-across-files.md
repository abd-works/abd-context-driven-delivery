# Check Clean Engineering Across Files

Analysis and planning: the stories here are not built yet. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epic, feature and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** Clean Engineering's validation finds the problems that only show across files, as graph rules where the graph can answer and as one AI-judged pass over the codebase where it cannot.

## Notes from the backlog

From the codebase-wide checker backlog ("Checker that reads the whole codebase for reuse and shadow object models"):

> Validate judges one folder at a time, so the problems that only show across files slip through unless an agent runs a separate cross-file pass by hand. Make these checks part of Clean Engineering's validation, as graph rules where the graph can answer them and as AI-judge rules where it cannot.
>
> ## Every class is used or uses something
>
> Every production class must be reached somehow: it uses another class, another class uses it, or something outside the code's own calls reaches it, in whatever ways the project's frameworks and build reach classes. A class reached by none of these has no reason to exist: report it as **no use — delete**, and delete it with its specs. Check every way it can be reached before calling it unused: a class that others use but that uses nothing itself is in use.
>
> ## A runtime dependency must earn its place
>
> For every runtime relationship (one class calling, creating or reading another), ask why it is not an owned, connected relationship. A dependency is right when the two objects are genuinely independent and one asks the other to act through its public operation (an external system, a collaborator passed in, a registry it registers with). It is wrong when the caller builds the other object per call from strings or dicts, re-reads a file another object already holds, or passes the owner's data into a helper: that object should be a part (composition) or a held collaborator (association) of the object that owns the data. Report each wrong one with the owner and the relationship it should be.
>
> ## Disconnected classes
>
> A class connected only by inheritance, or not at all, is either a relationship the model missed or code that is not resource-oriented (a helper or value callers hand data to instead of an object held by its owner, such as `FrontMatter` and `Format` built from strings instead of owned by `Markdown` and the fidelity). Report which, with the owner and redesign.
>
> ## One-class packages
>
> A package holding one class is either unused (delete), part of a bigger package (merge), or not fully modelled. A package is a group of cohesive classes, not a folder per class.
>
> ## Other cross-file checks the manual passes kept finding
>
> Second object models (a dict, `*_name` copy or helper class that copies an owner's data), the same behaviour written in several files, second registries of practices, actions or stages, global or ambient state, state passed as parameters the object already holds, legacy names and dead code, and swallowed failures. See `.sessions/ensure-domain-orientation-refactor/validation-reports/cross-file-round3.md` and `cross-file-round4.md` for what each looks like, and `.context/repo-runtime.md` and `.context/repo-model-disconnected.md` for the first full run of the relationship checks.

## Epic: Map Work Into Knowledge Graph

### Feature: Check Nodes Against Graph Rules → Check Clean Engineering Code Through The Graph

Validate at Clean Engineering's modules, model and code fidelities checks what one file at a time cannot see. The other half of this feature is [Measure Code On The Model](measure-code-on-the-model.md).

#### Story: Report Unused Class For Deletion

- Every production class is reached somehow: it uses another class, another class uses it, or something outside the code's own calls reaches it. That last way differs from one project to the next: a framework that finds classes by a decorator, an annotation or a naming convention; a registry or plugin list; dependency injection; an entry point declared in the project's configuration; reflection or serialization by name; a build step that generates code or an adapter from it.
- Each project says in its configuration which of these ways it uses, so the rule fits any language and framework rather than one codebase's.
- A class reached by none of these is reported as **no use — delete**, to be deleted with its specs.
- Check every way it can be reached before calling it unused: a class that others use but that uses nothing itself is in use.

#### Story: Report Runtime Dependency That Should Be Owned

- For every runtime relationship (one class calling, creating or reading another), ask why it is not an owned, connected relationship.
- Right: the two objects are independent and one asks the other to act through its public operation (an external system, a collaborator passed in, a registry it registers with).
- Wrong: the caller builds the other object per call from strings or dicts, re-reads a file another object already holds, or passes the owner's data into a helper. That object should be a part (composition) or a held collaborator (association) of the object that owns the data.
- Report each wrong one with the owner and the relationship it should be.

#### Story: Report Disconnected Class

- A class connected only by inheritance, or not at all, is either a relationship the model missed or code that is not resource-oriented (a helper or value callers hand data to, such as `FrontMatter` and `Format` built from strings instead of owned by `Markdown` and the fidelity).
- Report which, with the owner and redesign.

#### Story: Report One-Class Package

- A package holding one class is unused (delete), part of a bigger package (merge), or not fully modelled. A package is a group of cohesive classes, not a folder per class.

#### Story: Judge Clean Engineering Rules Across Files

- Validate judges one folder at a time today; this pass judges the whole codebase, as AI-judge rules where the graph cannot answer.
- What it looks for: second object models (a dict, `*_name` copy or helper class that copies an owner's data), the same behaviour written in several files, second registries of practices, actions or stages, global or ambient state, state passed as parameters the object already holds, legacy names and dead code, and swallowed failures.
- Examples of each: `.sessions/ensure-domain-orientation-refactor/validation-reports/cross-file-round3.md` and `cross-file-round4.md`; the first full run of the relationship checks: `.context/repo-runtime.md` and `.context/repo-model-disconnected.md`.

## Implementation plan (2026-11-22)

### What it has to catch: what the judges found by hand

The seven design judgments of release 1.2 (`.sessions/release-1-2-fixes/validation-reports/judgment-*.md`) read every production file against the Clean Engineering rules, under four themes: module boundaries, the same work in different shapes, resource orientation, and domain orientation. Their most frequent findings, and how this item takes each over so the next validate finds it without a judge reading every file:

| What the judges found | How often | Checked by the graph | Judged on the graph's candidates |
|---|---|---|---|
| The same behaviour written in several files (`eliminate-duplication`) | 31 | Operations whose bodies match once names are set aside, in different files | Whether the copies are one behaviour that needs one home |
| State handed down as parameters the object already holds (`hold-state-on-the-object-not-in-parameters`) | 19 | A parameter passed on unchanged through two or more calls, or a session, ticket or name passed to every operation of an object made for it | Which object should hold it |
| A module that is not one boundary (`single-boundary`, `high-cohesion`, `low-coupling`, `one-way-deps`, `deep-module`) | about 30 | Module measures: import loops, modules imported and importing, seam share | Where the boundary should move |
| Logic that belongs on its owner, classes not shaped around resources (`put-logic-on-the-owning-resource`, `shape-classes-around-resources`, `use-explicit-dependencies`) | about 17 | Dependencies reached per call from strings or by name (story 2); disconnected classes (story 3) | The owner, and the relationship it should be |
| A second object model (`do-not-invent-parallel-object-models`) | 4 | A field or dict copying a property its owner already has; a second registry | Whether it is a copy |
| Names that disagree or do not reveal intent (`use-consistent-naming`, `use-intention-revealing-names`) | 16 | Two verbs used for one operation across classes (`get_` / `fetch_` / `read_` with the same target) | The one name to use |
| A module card whose seam or dependencies no longer match the code (`seam-names-current-code`, `public-seam-only`) | 5 | The card's seam terms and dependencies against the module's public classes and module imports the graph records | Whether the card or the code is behind |
| Simplifications: dead code, nested operations, static operations, internal operations left public | many, in every report | Unused class and unused operation; operations public but used only inside their module; static operations not on the allowed factory list | — |

The checked rules raise violations. The judged rules raise candidates, which the report, the board and the graph tree show apart from violations, and the validation report's Fix button hands each candidate to the agent with the rule's text.

### Steps

0. **A graph that can be counted on.** Every class-to-class edge from code (inheritance, composition, aggregation, association, dependency), with how a dependency is reached: created per call, created in the constructor, looked up by name, held, or handed in. Calls joined to the operation they really reach, not to every operation of that name (defect e1e1c23c67a2). Until one thing is one node, these rules run on the code fidelity only, so each class is counted once.
1. **One shared list of the ways a project reaches code**, moved out of TDD's `called_by_name.py` so the coverage rule and the unused rules read the same list, and named for each project in `.context/config.json`.
2. **The rules**, each as scenario, then a failing and a repaired example, then the rule: unused class and operation, dependency that should be owned, disconnected class, one-class package, duplicated behaviour, state passed down, second object model, two names for one concept, and the judged pass over what the graph cannot find.
3. **Calibration on this repository:** run every rule and compare with the seven judgment reports and `.context/model/repo-model-disconnected.md`. Each finding the judges made by hand that no rule lists means the graph is still blind there, and becomes a defect.
4. **Where it runs:** validate given the whole graph, at the modules, model and code fidelities. The checked rules run every time; the judged pass runs on the candidates only.

### Decided by the person on 2026-11-22

- The ways a project reaches code are named in the project's `.context/config.json`, beside the code measures.
- A graph rule can have scope "all": validate runs it on the whole repository, not only the paths it was given. The cross-file rules have that scope.
- The checked rules run on every validate; the judged pass over the whole repository runs only when validate is asked for it.
- Building started the same day: step 0 (the graph's class-to-class edges) and step 1 (the shared list and scope "all") first, then the rules of step 2.
