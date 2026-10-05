# BDD sketch — match active fidelity

Sketch the behavior outline first, then layer on test/implementation detail. Confirm top-level **subjects / states / observable conditions** (never manager, hub, or mechanism names), ordered as a **usage story**, then nest only the **events and conditions that enable** each observation. Only once that scaffold reads cleanly, add call-surface and internals — and only as far as the active fidelity needs.

**Order:** usage-sequence subjects → `that` (event/condition) → `with` (standing condition) → `it should` → public `->` / `expect` → novel internals under calls (development only).

**Naming (explicit):**
- `describe` = plain-English subject (`an action that is annotated with log`) — not `SessionLog`, not `@log marker`
- `that …` = enabling event/condition (`that has been logged`, `that is invoked`) — never `when …`
- `with …` = narrower standing condition (`with no session name given`, `with verbose off`) — never `when …`

| Fidelity | Fill |
|---|---|
| **behavior** | Hierarchy plus public call surface (`new`, sets, calls, `expect`) — no internals |
| **development** | Behavior surface plus novel interactions under calls (domain-walk); omit paths already green |

## Notation — headings carry the hierarchy

Subjects and their enabling conditions nest through markdown headings, so each folds on its own. `## behavior driven development:` is the section heading; the tree starts one level below it.

| Heading | Holds |
|---|---|
| `### {subject in plain English}` | the subject under description |
| `#### that {enabling event or condition}` | an event or condition that unlocks the observations below |
| `##### with {standing condition}` | a narrower standing condition |

Under the deepest heading, a fenced block holds the `it should …` observations and the `->` call surface. Interleave: code sits under the hierarchy line it realizes. `->` at the public surface (behavior), deeper `->` under a call (development, novel only), `//` = note. No `beforeEach` / imports / AAA labels.

**Do not annotate sketch lines** with `# b` / `# d` (or any margin fidelity tags). Declare fidelity once at the top of the file.

This template is the BDD notation for a section of the engagement sketch. When sketched with another practice in the same session (clean-engineering-model / object model), keep that notation in `{slug}-sketch.md` so the model and behaviors stay paired; do not write `{slug}-bdd-sketch.md`.

---

## Template

~~~markdown
Fidelity: behavior | development

### {subject in plain English}

```
-> {subject} = new {Class}()
```

#### that {enabling event or condition}

##### with {standing condition}

```
-> {subject}.{property} = {value}
  -> {collaborator}.{operation}({args})    // development: novel only
it should {observable result}
  -> expect({subject}.{observation}).to {matcher}
```
~~~

---

## Example — usage story (preferred shape)

~~~markdown
Fidelity: behavior

### an action that is annotated with log

#### that is invoked

```
it should record a run event on the session trail
```

#### that has been logged

##### with no session name given

```
it should use the default session
```

##### with a given session name

```
it should keep events under that session
```

##### with verbose off

```
it should write a summary line and keep the last payload
```
~~~

## Example — domain subject

Scaffold first (subjects → `that`/`with` → confirmations), then details:

~~~markdown
Fidelity: behavior

### a vehicle

#### that is temperamental

```
it should refuse to start on the first attempt
```
~~~

~~~markdown
Fidelity: development

### a vehicle

```
-> vehicle = new Car()
```

#### that is temperamental

```
-> car.personality = CatPersonality.temperamental
  -> self.attribute_factory.load_attributes(
        personality=CatPersonality.temperamental)
it should refuse to start on the first attempt
  -> expect(car.start()).to be false
  -> expect(car.message).to equal "No way — I am tired!"
```
~~~
