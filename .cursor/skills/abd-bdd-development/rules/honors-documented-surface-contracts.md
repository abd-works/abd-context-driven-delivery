### Rule: Generated production code honors any documented surface contract

If the module you are implementing participates in a surface contract that has been declared elsewhere — usually in a mechanism-context file under an `architecture-context.md`, sometimes in a domain specification — the public API you generate must match the contract's method names, parameter shapes, and return types exactly.

This rule sits above the temptations that pull test-first code away from consistency. The specs you are making pass usually exercise one concrete instance at a time. Nothing in a single spec run pushes you to align with sibling instances that are being generated in a different session. The result is silent surface drift: every instance passes its own spec, no instance matches its siblings, and the router that was supposed to call any of them polymorphically has to grow branches.

The correction is boring: before you finalize a class, open the contract that names its slot and confirm every public method matches. If a spec asks for a signature the contract doesn't allow, the spec is wrong — rewrite the spec to construct fixtures the contract's way and call the contracted methods.

**Where contracts live:**

- Mechanism-context files (`architecture-context.md`) that name a slot and its callable surface.
- Domain specifications that fix a type's operations.
- Any file the project has explicitly nominated as the source of truth for a public interface.

**When a contract is silent:**

- If no contract exists yet for the surface you're implementing, prefer the shape already exhibited by the first sibling to ship. Sibling coherence is the pre-contract discipline.
- If neither a contract nor a sibling exists, name the shape you chose in the module's docstring so the next sibling has something to align to.

#### DO

- Read the mechanism/context file that names your slot *before* writing the class signature.

  **Example (pass):** The `Multi-Format Story Rendering` mechanism context declares `parse(external) -> StoryMap`, `render(canonical, previous=None) -> external`, `sync(external, canonical) -> UpdateReport`. Every generated backend (`JsonStoryMap`, `DrawIOStoryMap`, `CodeStoryMap`, …) uses exactly these signatures. A spec that asks for `render()` with no arg is rewritten to construct a canonical fixture and call `render(canonical)`.

- Prefer parameter-and-ignore over omission when a slot the contract mentions doesn't apply to your instance.

  **Example (pass):** Only the code backend uses `previous` for hand-written preservation. The document and diagram backends accept `previous: Optional[str] = None` and ignore it. The surface stays uniform; polymorphic callers still work.

- When a spec forces a signature that violates the contract, revise the spec rather than the signature.

  **Example (pass):** A spec's `before.each` uses `MarkdownStoryMap(story_map).render()` to skip building a canonical. The contract says `render(canonical) -> str`. The spec is rewritten to build the canonical explicitly and call `MarkdownStoryMap().render(canonical)`. The contract wins.

#### DO NOT

- Move a required contract argument onto `self`.

  **Example (fail):** The contract says `render(canonical) -> external`. The generated code stores the canonical in the constructor and exposes `render() -> external` because that reads more nicely in one spec. Every other backend now takes an arg; this one does not. Polymorphic callers break.

- Return a project-internal wrapper where the contract declares the canonical type.

  **Example (fail):** The contract says `parse(external) -> StoryMap`. The generated code returns a helper like `DiagramStoryMap(story_map)` because it's convenient for the round-trip test. Every caller now needs to unwrap for this backend and not for others.

- Add public methods that aren't in the contract because a spec is easier to write with them.

  **Example (fail):** The contract slot declares three methods. The generated backend also exposes `append_epic` and `remove_epic` because the spec's `before.each` uses them to build fixtures. Some backends inherit them; some don't. Callers that discover the extras start depending on them and the drift compounds.

**Source:** Test-driven code can pass a spec while breaking the contract that gives the spec meaning. A quick sanity check against the contract file, before finalizing the class, is enough to catch it.
