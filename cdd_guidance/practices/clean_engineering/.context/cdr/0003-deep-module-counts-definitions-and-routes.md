# deep-module counts class definitions, resolves each import, and counts every route out of a module

CDR 0004 of `harness/graph` moved `deep-module`'s counting into facts the build records. Those facts matched classes by name: each folder kept the bare names its files imported (`imported_names_by_file`), and a class was public when any folder outside the module named a class of that name. Two defects followed. A class was public when only its namesake in another module was imported (`Parameter` in the model was public because `inspect.Parameter` is imported; `Segment` in `actions` because the draw.io scanners import geometry's `Segment` alias). And the total counted definitions while the public count counted distinct names, so a duplicated name made the two disagree. The name match also kept a trailing `# noqa` on the last name of an import line, so some real imports named nothing. Then the user rejected `cdd_guidance/actions` reading 3 of 21 classes public: its toolsets leave it by registration with `ACTION_CATALOGUE` and by the installer publishing them, not by being imported.

## Decision

- Each production file records the classes it imports, re-exports, or reaches as `module.Class` with the module it names each from (*ClassReference*: `[source, name]`, a path from the source root without extension, or a package's name as spelled). *ScriptImports* reads Python (`from a.b import C`, relative imports, `import a.b as g` + `g.C`, `from a import b` + `b.C`) and scripts (`import D, { A } from`, `import * as ns`, `export { A } from`, `export * from`) by text, the same way for files read now and files outside an edited-file scope, so a refresh and a fresh build agree. Folders keep them by file (`imported_classes_by_file`); the root keeps the outside files' (`imported_classes_outside`, each with the module that holds the file).
- *ImportedClasses* resolves each reference to the one class definition it names: the class of that name in the file its module is (looked for from the source root, then under each folder above the importer, as an import root makes it), or, when that file re-exports the name (a package `__init__.py`, an `index.ts`, a star re-export), the class the re-export names in turn. A reference it cannot resolve — a standard or third-party module, a TypeScript path alias such as `@cdd/*`, a name the module defines as no class (a function, a constant, a type alias), a star import — names no class of ours.
- A class is public when it leaves its module's subtree by a route: `named` (with the folders), `registered` (with the registry: `PRACTICE_CATALOGUE`, `ACTION_CATALOGUE`, `REGISTERED_PATTERNS`, read from the registries this process filled, by the file and name of each registered class), or `published` (an `@agent_toolset` class, or one with a member published as a tool, unless `@hosted_only` or `@noDeploy`). `public_classes` keys each class by `file:Name` and holds its routes.
- Counts are of definitions: total, public, and private = total − public.
- Each module also records its operations (`operations_total`, `operations_public`, `operations_private`, `seam_operations`) for reading; the rule judges classes only.
- Examples (`examples` folders) and test doubles (`mock_*`, `fake_*`) are left out of the counts and do not name a class, like tests and fixtures (`is_example_code`); other rules still judge them.
- Saved shape 5.

## Considered options

- **Resolve imports through the parsed syntax tree for Python.** Rejected: files outside an edited-file scope are read by text, and two readers would let a scoped build and a whole build disagree.
- **Find registered classes by reading the registering packages' source.** Rejected: `cdd_guidance/actions` and `cdd_guidance/patterns` discover their classes from disk at import, so their text names none; the registries the process filled are the only exact answer.
- **Resolve TypeScript path aliases from `tsconfig.json`.** Not done: `@cdd/*` points at the generated language adapters under `.claude/`, which hold no class of the repository's own.

## Consequences

- On this repository: 6,099 references, 2,212 resolved to a class definition; 1,798 name a module outside the repository, 1,490 a name that is no class there (mostly functions, constants and type aliases), 355 a script package or alias, 241 the `@cdd/*` alias, 3 star imports.
- `deep-module` now fails `cdd_guidance/actions` (11 of 21 public: 9 registered toolsets and 2 named) and `cdd_guidance/builders` (2 of 3, published toolsets), besides `harness/process`.
- The registered route depends on the process having imported the practices, actions and patterns, which every CDD process that builds a graph does.
