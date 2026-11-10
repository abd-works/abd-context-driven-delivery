# Check Clean Engineering Across Files

Analysis and planning: the stories here are not built yet. This is one increment of the thin slice, which sets the order of the increments, [harness/.context/stories/thin-slice.md](../../harness/.context/stories/thin-slice.md); its epic, feature and stories are on the story map, [harness/.context/stories/story-map.md](../../harness/.context/stories/story-map.md). Each requirement sits under the story it belongs to.

**Outcome:** Clean Engineering's validation finds the problems that only show across files, as graph rules where the graph can answer and as one AI-judged pass over the codebase where it cannot.

## Notes from the backlog

From the codebase-wide checker backlog ("Checker that reads the whole codebase for reuse and shadow object models"):

> Validate judges one folder at a time, so the problems that only show across files slip through unless an agent runs a separate cross-file pass by hand. Make these checks part of Clean Engineering's validation, as graph rules where the graph can answer them and as AI-judge rules where it cannot.
>
> ## Every class is used or uses something
>
> Every production class must have at least one relationship: it uses another class (calls, creates, holds, reads), something uses it, or something builds, reads or installs it at build time (an annotation kind the installer reads, a toolset the installer publishes, a registration at import, a TypeScript adapter generated from it). A class with none of these has no reason to exist: report it as **no use — delete**, and delete it with its specs. Check every way it can be used before calling it unused: a class that others use but that uses nothing (`Name`, `Git`) is in use.
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

- Every production class has at least one relationship: it uses another class (calls, creates, holds, reads), something uses it, or something builds, reads or installs it at build time (an annotation kind the installer reads, a toolset the installer publishes, a registration at import, a TypeScript adapter generated from it).
- A class with none is reported as **no use — delete**, to be deleted with its specs.
- Check every way it can be used first: a class that others use but that uses nothing (`Name`, `Git`) is in use.

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
