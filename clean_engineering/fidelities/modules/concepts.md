## Modules Fidelity — Generate

At this fidelity the **module** is the primary unit of design. Classes exist to serve modules — they fit inside a module, and only the ones that form the public seam are elevated in the module's context file. Everything else about class internals happens at specification and code fidelity.

Produce **class stubs**: typed properties, operation signatures with `...` bodies, named relationships. No implementations. But the emphasis of this fidelity is on the *module context*, not the class stubs — the stubs are scaffolding to prove the seam works; the context file is what the next engineer reads first.

Default output is code (Python). Use `@property` for read-only computed values; no `get_` / `set_` prefixes.

**`physical-folder` (required):** All generated code — class files, helpers, and the module context — lives inside the **module** folder (e.g. `check/check.py`, `check/.context/module-context.md`). A handbook chapter or other organisational parent (e.g. `core_mechanics/`) may contain several modules; that parent is not itself a module unless it has its own `.context/module-context.md`. Do not emit class files beside the module, in a flat dump, or outside the module folder.

**`cohesive-file` (required):** One file per **class family**, not one class per file. A family is the primary type, its subtypes, and tightly connected peers that only make sense together (e.g. `Ability` + `Abilities` in `abilities.py`, `Point` + `PointTotals` in `point_totals.py`). Name the file after the family concept. Split only when a type is reused independently across families or the file becomes unrelated grab-bag.

---

### Modules

Each module is a folder. Put `.context/module-context.md` and every class file for that module inside it. The context file is the single growing description for the module — domain-driven design and other practices will add their own sections over time; do not create separate context files per practice.

At modules fidelity the context file carries:

```markdown
# ModuleName

[Opening paragraph from language fidelity — role, boundary, and collaborating
modules — carried forward as the module's identity statement.]

## Seam

[One or two short paragraphs. Say what the seam is, why it is shaped that
way, and the constraint on callers — in natural language. Use the words
*seam* and *constraint*. No labeled sub-slots ("What the seam is" / "Why" /
"Constraint"). Omit anything that does not earn a sentence.]

## Public API

[For each public class: one or two short sentences — what it does for
callers, how they typically use it, and why it is at the seam. Natural
prose; no Intent / How used / Why labels. Only classes callers depend on;
internals wait for Participants at specification fidelity.]

## Dependencies

[One or two short paragraphs: what this module depends on (and for what),
who depends on it if known, and any deliberate non-dependencies. Natural
prose; no Depends on / Depended on by / No dependency on labels. Edges are
one-way; cycles are a design bug.]

## Mechanism stereotype (optional)

[If this module is a mechanism — a structural pattern the codebase will
instantiate more than once — describe:
- **What pattern is being instantiated** — the recurring shape (e.g. "the
  entity-controller pattern for a downstream service").
- **Why it recurs** — what forces make this pattern show up in more than one
  place.
- **How to build a new instance** — the recipe. Name the classes a new instance
  must inherit from or the constants it must override; name the fixed parts
  that stay identical across instances; describe what the developer has to
  provide and what the mechanism handles for them.
Leave this section out for vanilla modules. Do not force it; pursue it only
when the pattern is genuinely recurring.]
```

#### Module rules

- **`physical-folder`** — Code and context for a module belong in that module's folder only. One folder per module; class files are not written outside it.
- **`cohesive-file`** — Class family in one file (element + collection, type + subtypes, small aggregate + part). Do not emit a separate file per class by default.
- **`complexity-absorption`** — Push configuration, orchestration, and edge-case handling *into* the module's classes; callers pass intent, not step-by-step setup or configuration flags. If an operation's signature would require the caller to pass multiple flags, ordering hints, or setup parameters, that is a signal the module is offloading its own work onto callers — pull that complexity inward.

**Suggestion (not required): sketch two API shapes.** Before locking down operation signatures, consider drafting two radically different public API shapes for the module and comparing them. This is a heuristic, not a rule — use it when the seam is genuinely under-designed. A user may explicitly opt in ("think through what the alternative APIs could be"); otherwise skip.

---

### Classes

Classes at this fidelity are scaffolding that proves the seam works. Only classes that appear in the module's Public API section need serious design attention now — internal classes can be minimal stubs to be fleshed out at specification fidelity. For each class:

1. **Class docstring** — the opening definition paragraph from the language artifact (what the class is, its role, invariants). Bullets about specific properties or operations move down to their members.
2. **Properties** — noun phrases, typed. Docstring **above** the annotation (not below, not a trailing `#` comment).
3. **Operations** — verb phrases, signature only. Docstring **above** the `@abstractmethod` / `def` (at engineering, also as the method body docstring).
4. **Relationships** — target class only. One line each as a typed attribute or constructor parameter. Kind and direction are committed at specification fidelity.
5. **Inheritance** — declare a base class only where a subtype adds or overrides behavior. Record only the delta.
