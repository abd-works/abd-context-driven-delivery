# BDD sketch — match active fidelity

Sketch the behavior outline first, then layer on test/implementation detail. Confirm top-level **subjects / states / observable conditions** (never manager, hub, or mechanism names), ordered as a **usage story**, then nest only the **events and conditions that enable** each observation. Only once that scaffold reads cleanly, add call-surface and internals — and only as far as the active fidelity needs.

**Order:** usage-sequence subjects → `that` (event/condition) → `with` (standing condition) → `it should` → public `->` / `expect` → novel internals under calls (development only).

**Naming (explicit):**
- `describe` = plain-English subject (`an action that is annotated with log`) — not `SessionLogHub`, not `@log marker`
- `that …` = enabling event/condition (`that has been logged`, `that is invoked`) — never `when …`
- `with …` = narrower standing condition (`with no session name given`, `with verbose off`) — never `when …`

| Fidelity | Fill |
|---|---|
| **behavior** | Hierarchy plus public call surface (`new`, sets, calls, `expect`) — no internals |
| **development** | Behavior surface plus novel interactions under calls (domain-walk); omit paths already green |

**Notation:** plain indent · `->` at the public surface (behavior) · deeper `->` under a call (development, novel only) · `//` = note. Interleave; code sits under the hierarchy line it realizes. No `beforeEach` / imports / AAA labels.

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
