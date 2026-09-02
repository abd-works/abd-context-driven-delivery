# BDD sketch — match active fidelity

Sketch the behavior outline first, then layer on test/implementation detail. Confirm top-level **subjects / states / observable conditions** (never manager, hub, or mechanism names), ordered as a **usage story**, then nest only the **events and conditions that enable** each observation. Only once that scaffold reads cleanly, add call-surface and internals — and only as far as the active fidelity needs.

**Order:** usage-sequence subjects → `that` (event/condition) → `with` (standing condition) → `it should` → public `->` / `expect` → novel internals under calls (development only).

**Naming (explicit):**
- `describe` = plain-English subject (`an action that is annotated with log`) — not `SessionLog`, not `@log marker`
- `that …` = enabling event/condition (`that has been logged`, `that is invoked`) — never `when …`
- `with …` = narrower standing condition (`with no session name given`, `with verbose off`) — never `when …`
- `shared_context …` = shared `it should` once; name is reused by `included_context`
- `-> included_context('…')` = route this implementation branch to that shared contract

| Fidelity | Fill |
|---|---|
| **behavior** | Hierarchy plus public call surface (`new`, sets, calls, `expect`) — no internals |
| **development** | Behavior surface plus novel interactions under calls (domain-walk); omit paths already green |

**Notation:** plain indent · `->` at the public surface (behavior) · deeper `->` under a call (development, novel only) · `//` = note. Interleave; code sits under the hierarchy line it realizes. No `beforeEach` / imports / AAA labels.

**Same behavior, different implementations** — `shared_context` once; each `with {Implementation}` names domain state and `-> included_context('…')` (same string). See table below.

| Sketch line | Spec (Mamba) | Meaning |
| --- | --- | --- |
| `shared_context {subject line}` | `with shared_context('{subject line}'):` | Define shared `it should` **once**. Name must match `included_context` exactly. |
| `with {Implementation}` | `with context('with {Implementation}'):` | Domain state for this branch — names the subject (e.g. `with a SubAgent (agentic)`). No `build_*`, no `self.subject`. |
| `-> included_context('{subject line}')` | `with included_context('{subject line}'): pass` | **Route** to the shared examples above under this branch's standing condition. |
| `it should …` under `with {Implementation}` only | ordinary `with it(…)` | Implementation-specific proof — not in `shared_context`. |

**Do not annotate sketch lines** with `# b` / `# d` (or any margin fidelity tags). Declare fidelity once at the top of the file.

---

## Template

```
Fidelity: behavior | development

{subject in plain English}
  -> {subject} = new {Class}()
  that {enabling event or condition}
    with {standing condition}
      -> {subject}.{property} = {value}
        -> {collaborator}.{operation}({args})    // development: novel only
      it should {observable result}
        -> expect({subject}.{observation}).to {matcher}
```

## Template — same behavior, different implementations

```
Fidelity: behavior | development

## {story name}

shared_context {abstract subject — exact string used in included_context}
  it should {shared outcome}
  it should {second shared outcome}

with {Implementation}
  -> included_context('{abstract subject — same string as shared_context}')
  it should {outcome only for this implementation}
    -> expect({observation in domain terms}).to {matcher}

with {second Implementation}
  -> included_context('{abstract subject — same string as shared_context}')
  it should {outcome only for second implementation}
```

Repeat the `with {Implementation}` block per backend. The `included_context` string must match `shared_context` character-for-character.

---

## Example — usage story (preferred shape)

```
Fidelity: behavior

an action that is annotated with log
  that is invoked
    it should record a run event on the session trail
  that has been logged
    with no session name given
      it should use the default session
    with a given session name
      it should keep events under that session
    with verbose off
      it should write a summary line and keep the last payload
```

## Example — domain subject

Scaffold first (subjects → `that`/`with` → confirmations), then details:

```
Fidelity: behavior

a vehicle
  that is temperamental
    it should refuse to start on the first attempt
```

```
Fidelity: development

a vehicle
  -> vehicle = new Car()
  that is temperamental
    -> car.personality = CatPersonality.temperamental
      -> self.attribute_factory.load_attributes(
            personality=CatPersonality.temperamental)
    it should refuse to start on the first attempt
      -> expect(car.start()).to be false
      -> expect(car.message).to equal "No way — I am tired!"
```

## Example — abstract subject, concrete implementations

Shared outcomes live on the abstract subject; each backend adds only its own proof:

```
Fidelity: behavior

a diagram Story Map
  that holds a rendered Story Map with 4 Epics
    it should contain 4 Epic elements on the Epic row in sequential order
    with a fifth Epic appended
      it should contain 5 Epic elements on the Epic row

a DrawIO Story Map
  that holds a rendered diagram Story Map with 4 Epics
    every Epic element
      it should be an mxCell whose style carries the Epic swatch
```
