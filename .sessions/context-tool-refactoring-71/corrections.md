# Corrections — context-tool-refactoring-71

From the markdown-collection / rules-as-toolset / `Guidance.tools` work. Each item is a **category**, not a one-off bug: the original mistake, the better outcome, and the `/clean_engineering` rule that would have changed the result. Mark **new** rules as candidates to add to the practice.

---

## 1. Closest owner is not the owning ancestor

**Mistake.** Move behavior to the nearest object that can see the data. `inject_rules` landed on `Guidance`, then on `PracticeGuidance`. Tool discovery landed on `Guidance.tools`. `glob` / `matches` landed on `MarkdownCollection`. Each move was “closer” than the last host, and still wrong at the base.

**Better.** Walk the inheritance and module chain before writing the method. Ask: which **ancestor type** already has this job for every subtype? `inject_rules` belongs on `RulesCollection`. Property-and-collection discovery belongs on `AgentToolSet`. `glob` / `matches` belong on `RulesCollection`, not on every markdown list.

**Existing.** `put-logic-on-the-owning-resource` — put logic on the object that owns the invariant, not on the caller or the Given subject. `nesting` — put shared behavior on the parent; a child may depend on the parent, not on siblings. `write-interactions` — ask the collaborator that owns the next act; do not steal its job.

**New — `look-up-the-ancestry`.** Closest owner is necessary and not sufficient. Before adding a method on the leaf, walk the type chain and the framework module that already catalogs this kind of member. If a parent (`AgentToolSet`, `MarkdownCollection`, `Destination`) already does this job for every subtype, teach that parent — do not write a parallel walker on the leaf. Closest-owner bias gets things *somewhat* in the right place and fails at reusable behavior.

---

## 2. Fork the walk instead of extending the base

**Mistake.** `Guidance.tools` copied `AgentToolSet.tools` and added property getters plus a rules-collection walk. `instructions` was already `@agent_instructions`. The leaf grew a second catalog.

**Better.** Property getters and “value is a toolset / `ToolSetCollection`” belong on `AgentToolSet`. `Guidance` is `@agent_toolset`. Delete the fork.

**Existing.** `eliminate-duplication` — one canonical function; the copy you miss is the bug. `do-not-invent-parallel-object-models` — do not split the same job into a second type. `general-purpose-surface` — do not shape the seam for one caller (`PracticeGuidance`). `class-not-property-instance-or-subtype` — check subtype / extend before writing a new class or a new catalog.

---

## 3. Parallel file for a type that already has a home

**Mistake.** `markdown-collection-model.py` beside live `markdown.py`. A second Markdown family to keep in step.

**Better.** New members live on `markdown.py`. Mark the locate / coerce spots that must grow. One family, one file.

**Existing.** `one-canonical-model-document` — one canonical artifact; parallel models drift. `do-not-invent-parallel-object-models`. `single-boundary` — do not let another module hold this module’s concept. CE language already: put a class family in one file; split only when a type is independently reused.

---

## 4. Operation on the wrong sibling in the same family

**Mistake.** `Markdown.coerce` switched on list/map. `glob` / `matches` sat on `MarkdownCollection`. Someone offered `Validate` as the home for `inject_rules` because the action was “close.”

**Better.** List/map shape is `MarkdownCollection.coerce`. Path glob is a **rules** concern. `inject_rules` is a hook on the collection that owns `markdown` and `matches`. Near is not owner.

**Existing.** `keep-classes-single-responsibility`. `put-logic-on-the-owning-resource`. `high-cohesion` — same purpose and the same domain concept, or the next feature edits the wrong class. `single-boundary`.

---

## 5. Invented label instead of the object’s name

**Mistake.** `_words_from_slug`, then `rules_label`, so the toast could say something human. The collection already has `parent`; the parent already has `name` or a type name (`code`, `SampleGuidance`).

**Better.** No extra property. `parent.name` or `type(parent).__name__`. Every collection holds `parent` because that is how these objects relate — not so a toast helper can exist.

**Existing.** `do-not-invent-terms`. `use-intention-revealing-names`. `use-property-not-accessor` — do not add a stored label for a name the object already has. `use-explicit-dependencies` — pass `parent` in the constructor; do not recompute identity from slug.

**New — `type-is-enough`.** Do not add an annotation, label property, or slug-word helper when the return type, the class name, or a collaborator the object already holds answers the question. `@rules` does not need a `ToolSetCollection` decorator if `RulesCollection` is already a toolset. A toast does not need `rules_label` if `parent.name` exists.

---

## 6. Banned stand-in names

**Mistake.** `host` as the local for Guidance / toolset / operation / parent. A second noun for the thing that already has a name.

**Better.** Say `parent`, `toolset`, or the type. `host` is banned.

**Existing.** `vocabulary-traces-to-source` — the English term and the code name are the same word. `do-not-invent-terms` — a second noun becomes a second class.

---

## 7. Leftover alias after the seam moves

**Mistake.** Keep `rules_markdown` (and callers) after `collection.markdown` exists. Keep helper wrappers that preserve the old name.

**Better.** One name. Update every caller. Delete the twin.

**Existing.** `no-legacy-api-after-refactor` — no compatibility aliases, re-exports, or thin wrappers that preserve the old name.

---

## 8. Destination mark treated as a special case

**Mistake.** `Guidance.tools` enrolled `_rules` as a one-off flag. `@skill` and `@command` already pair a destination with `@agent_tool` / `@agent_instructions`. Collection tools were re-discovered only on Guidance.

**Better.** `@rules` is a `Destination` like `@skill` / `@command`. Kind mark on the member (`@agent_tool`). Collection tools come from type on `AgentToolSet`, not from a Guidance-only `_rules` walk.

**Existing.** `use-consistent-naming` — one word and one pattern per concept. `general-purpose-surface`. `eliminate-duplication`.

---

## 9. Binding and discovery on the same class

**Mistake.** `Guidance` both bound markdown to `rules` **and** walked members to build `tools`. Discovery leaked into the practice type.

**Better.** Guidance only binds: `@markdownCollection` + `@rules` + `@agent_tool` on `rules`. Discovery is `AgentToolSet`. A leaf that is `@agent_toolset` inherits the catalog.

**Existing.** `keep-classes-single-responsibility`. `keep-operations-single-responsibility`. `abstraction-focus` — the seam names what the module does for callers (bind guidance), not the internal catalog walk.

---

## 10. Framework assumption that only this leaf has the shape

**Mistake.** “Only Practice Guidance would have properties we want to expose.” `inspect.isfunction` only. Property `@agent_instructions` (`instructions`) and collection-typed properties (`rules`) were Guidance-only patches.

**Better.** Property getters and collection-typed members are a core `AgentToolSet` concern. Any toolset may expose them.

**Existing.** `general-purpose-surface`. `nesting` — shared behavior on the parent. Complements **`look-up-the-ancestry`**.

---

## Rule candidates to add to `/clean_engineering`

| Rule | Fidelity | One line |
| --- | --- | --- |
| `look-up-the-ancestry` | model + code | Walk the type chain; put reusable behavior on the ancestor that already owns that job for every subtype. Closest owner is not enough. |
| `type-is-enough` | model + code | Do not invent a label, annotation, or slug helper when the type, class name, or held collaborator already answers. |

`put-logic-on-the-owning-resource` stays. The miss was stopping at the nearest object instead of asking whether that object is a **leaf fork** of a job the base already has.
