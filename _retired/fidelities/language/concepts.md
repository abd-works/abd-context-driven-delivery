## Language Fidelity — Generate

Produce  classes with a single class-level docstring that holds all natural language content. No types, no implementations, no relationship kinds. The docstring is the artifact — it travels downstream and gets distributed to individual members as fidelity increases.


---

### Module structure

At this fidelity establish the **module structure** (`physical-folder`): each module gets its own folder. All class files and the module's `.context/` live inside that folder — never beside it or in a separate code root. A source chapter may map to several modules under an organisational parent folder; that parent is not a module.

The module description is written once and placed depending on format:

- **Markdown format** — the module description appears as a top-level `# ModuleName` section at the head of the output file, before the class sections. At this format the description expands beyond the summary sentence: it explains the classes the module contains, how they relate to each other, and how they work together to fulfil the module's responsibility.
- **Code format** (Python, Java, TypeScript, etc.) — the module description goes into `.context/module-context.md` inside the module folder, using the compact summary shape below.

**Module description shape:**

```markdown
# ModuleName

*ModuleName* is [what this module is]. Document what it is uniquely responsible for [role], what it owns [boundary — what belongs here and what doesn't], the other modules it collaborates with [related modules], what it publicly enforces [the rules that must always hold], what its named public surface is [seam — the classes and operations callers depend on], and what callers must do or must not do at that surface [constraint].
```

The seam and constraint are the caller-facing side of the boundary. The seam names the public surface; the constraint says what using it obligates the caller to do or forbids them from doing elsewhere. Both belong in the module description from the start — they are part of the module's identity, not implementation detail. See `named-seam-and-constraint` and `deep-module` in `clean-engineering.md`.

Classes in the module follow the standard class shape below.
 
---

### Class shape

```python
class ClassName:
    """
    *ClassName* is [definition — what it owns, what unique role it plays, what it is
    responsible for, how it relates to other classes, what must always be true.
    Weave naturally. Every domain term is *italicized*.]

    - [bullet telling part of the class's story — what it holds, what it does,
      who it depends on, what it produces. Every domain term is *italicized*.]
    - **Invariant:** [rule that must always hold — only when one exists]
    """
```

---

### Module rules

- **`abstraction-focus`** — Design the module so that its description names *what* the module does at a higher conceptual level than the classes inside it. Operations named in the description are verbs the caller cares about, not internal steps. The public method signatures the description previews must not mirror internal database schemas, data structures, or storage layouts.
- **`layer-separation`** — Design the module so that its description states the conceptual level it operates at and where it sits relative to the modules it collaborates with. Adjacent modules must operate at different levels of abstraction. If neighbouring modules operate at the same level — or one passes data through unchanged, adding no new meaning or structure — collapse it or give it a real job.

### Class rules

- The class docstring holds only the **identity sentence** — what the class *is*. One sentence.
- Every sentence that speaks to a specific property, operation, or relationship belongs **on that member**, not in the class docstring. Place it as a docstring **above** the property or operation.
- An operation's sentence describes what the class *does* or *produces* — not a method signature.
- A property's sentence describes what the class *holds* or *remembers* — and why.
- A relationship's sentence describes what the class *depends on*, *owns*, *collects*, or *collaborates with* — alongside that property.
- Invariants are explicit — `**Invariant:**` on the member they constrain.
- Do not commit to *composition* / *aggregation* / *association* at this fidelity — use plain English.
- No method stubs at this fidelity. Members have only their docstring; bodies come at model fidelity.

Default output is **code (Python)**. Member docstrings carry forward to model, specification, and engineering unchanged.
