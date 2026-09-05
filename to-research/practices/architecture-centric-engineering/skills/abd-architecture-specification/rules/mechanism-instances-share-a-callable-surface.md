### Rule: A mechanism's instances share a callable surface

When a mechanism defines a slot contract that its instances implement, every instance must expose the same *callable surface* for those slots: identical public method names, identical parameter shapes (same names and same roles), identical return types. Internal helpers and private state may vary freely; the surface a caller sees must not.

This rule sits alongside pattern coherence, not inside it. Pattern coherence (same files, same wiring, same extension steps) helps a new engineer *add* an instance. Surface coherence is what lets a caller *use* the instances polymorphically. A router that dispatches to an instance based on a name — a CLI, a plugin registry, a strategy selector — collapses into a two-line lookup only if every instance answers the same way. If one instance takes a canonical object as an argument and another reads it from `self`, or one returns the canonical type and another returns a wrapper, the router degenerates into per-instance branching and the coordination the mechanism was supposed to absorb bubbles back up into every caller.

**Where to look for a surface break:**

- An instance's constructor takes stateful data that other instances take as a method argument.
- Two instances name the "same" operation with different parameter counts, different keyword names, or different return types.
- The public method of one instance returns a project-internal wrapper (`DiagramView`, `CodeTree`, `RequestContext`) while others return the plain canonical type.
- A caller has an `if isinstance(instance, X):` branch — that branch is the surface break made visible.

**When surface variation is legitimate:**

- The *external type* the operation reads or writes differs by domain (some backends serialize to `str`, others to `Dict[str, str]`, others to `bytes`). Keep the type variable in the signature (`external: Format`) but keep the *shape* of the signature identical: `parse(external)`, `render(canonical, previous=None) -> external`. The caller still calls the same method with the same argument roles.
- One instance ignores a parameter another uses (e.g., only one backend needs `previous` for hand-written preservation). Accepting-and-ignoring is fine; omitting the parameter is not.

#### DO

- Declare the callable surface explicitly in the mechanism's context file, next to the slot contract.

  **Example (pass):** The `Multi-Format Story Rendering` mechanism context names not only the four slots but the exact public methods each slot ships with: `parse(external) -> StoryMap`, `render(canonical: StoryMap, previous: Optional[External] = None) -> external`, `sync(external, canonical: StoryMap) -> UpdateReport`. All five backends (json, markdown, drawio, miro, code) match these signatures verbatim; the CLI router calls them by name with no branching.

- Push instance-specific state into internal collaborators, not into constructor arguments that vary by instance.

  **Example (pass):** DrawIO needs geometry math (via an internal `DiagramLayout` helper) to position cells. Instead of exposing that in the constructor (`DrawIOStoryMap(diagram=...)`), the backend instantiates the helper internally at the start of `render(canonical, ...)`. The constructor stays parameter-free like every other backend.

- List "callable surface" as a passable check in the mechanism's Rules section.

  **Example (pass):** *"Every backend exposes exactly `parse`, `render`, `sync` with the signatures declared above. No public method beyond these three. No stateful constructor."*

#### DO NOT

- Let instances diverge on public method signatures.

  **Example (fail):** `JsonStoryMap.render(story_map) -> str` alongside `DrawIOStoryMap.render() -> str` (reads from `self._diagram`) alongside `CodeStoryMap.render(previous_tree=None) -> Dict[str, str]` (reads from `self._story_map`). Three shapes for one slot. Any caller must know which backend it holds. The mechanism has no callable surface — it has three surfaces sharing a name.

- Hide state on `self` for some instances but not others.

  **Example (fail):** One backend requires `Backend(canonical)` at construction and exposes `render() -> str`; another exposes `render(canonical) -> str`. A caller cannot polymorphically hand any backend a canonical and get output — it must know which construction path applies to which backend. The state-carrying constructor is the surface break in disguise.

- Wrap the canonical type on the return of `parse` in some instances but not others.

  **Example (fail):** `JsonStoryMap.parse(text) -> StoryMap` versus `DrawIOStoryMap.parse(text) -> DiagramStoryMap`. The `DiagramStoryMap` wrapper is a legitimate internal collaborator; leaking it through the public seam forces the router to unwrap-or-not per backend.

- Expose extra public methods on some instances that others don't have, just because a spec used them for fixture setup.

  **Example (fail):** Two backends expose `parse`, `render`, `sync` per the contract. A third also exposes `append_epic` and `remove_epic` because its `before.each` used them to build fixtures. Callers that discover the extras start relying on them and the drift compounds.

**Source:** A mechanism collapses coordination into a single pattern. If the callable surface varies across instances, the coordination the mechanism was supposed to absorb bubbles back up into every caller.
