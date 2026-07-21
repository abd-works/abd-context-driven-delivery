# Rethinking clean_engineering Fidelity + Process

Working doc — captures a grill-session about three intertwined ideas raised while iterating on the clean_engineering generator. Not a decision record; a live exploration.

## What triggered this

The current clean_engineering generator has:

- **Structure guidance** — `clean-engineering.md` names the primitives (class, property, operation, relationship, subtype, invariant, interaction) and their canonical shapes.
- **Fidelity slots** — three tiers: `language`, `model`, `specification`. Each has a `domain-generate.md` describing what output looks like at that tier.
- **Format templates** — `formats/{markdown,python}/clean_engineering-template.{md,py}` show the notation per fidelity.

Three concerns raised:

1. **Process/thinking is buried inside structure.** The docs tell an agent *what* an clean_engineering artifact looks like, not *how to think* while producing one. Some thinking guidance is embedded (e.g. "ask *hold something, do something, or both?*") but it's mixed with shape rules.
2. **Fidelity feels too formal even at the lowest tier.** "Language fidelity" is prose but still structured (numbered sections, Properties/Operations/Relationships/Interactions). There's a rougher tier upstream — a **sketch** — that isn't captured. Proposed reframe: **sketch → fleshing it out → formal**.
3. **Sketching as a core mode of the grill-with-generator flow.** Rather than emitting a full artifact into chat, the flow should be: ask a question, sketch a rough shape, ask more, refine. Sketching is dialogue, not output.

Concrete sketch notation the user offered as illustration:

```
thing : base thing
  simple thing or thing not explored or thing defined elsewhere
  thing that has no id outside of parent 
       sub thing
       sub thing
       sub operation
  thing operation thing thing        <-- should relate to things above
  associatedThing 

  ----
 associatedThing
      thing
      thing operation thing
       -> _interaction_with_internal_important_enough_to_show
       -> thing.interaction_with_a_thing thing thing
```

Observations about this notation:

- Indent-based — no headings, no tables, no keywords.
- `thing : base thing` = subtype relation, terse.
- Nested indents = subordinate concepts / properties / operations under a class.
- `associatedThing` (unindented under separator) = related class, sketched in a peer block.
- `----` = separator between primary class and an associated class.
- `->` = interaction, either to an internal `_helper` or to another class's operation.
- Zero formal syntax — everything is a "thing" until it earns a name.

## Open questions to grill

- **Q1 — fidelity axis** — does *sketch / fleshing out / formal* **replace** the current three tiers, or does *sketch* slot in **upstream** as a new fourth tier?
- **Q2 — process vs structure** — how should "how to think" guidance be separated from "what output looks like"? Sibling files per fidelity? A single `clean_engineering-process.md`? Woven into the sketch tier only?
- **Q3 — sketch notation** — is the notation above canonical (adopt as-is) or exemplary (one of several sketches, don't over-formalise)?
- **Q4 — grill-with-generator flow** — is this a new skill (`grill-with-generator`) or a mode on the existing `grill-context`? Where does the sketch live during the dialogue — in chat, in a scratch file, in `.context/`?
- **Q5 — where does this all fit** — is "sketch" an clean_engineering concern only, or a cross-generator concept (DDD, architecture, tests would also sketch first)?

## Grill log

_Insights land here as they resolve — dated, one per resolved question._

### Insight — Sketch is an activity, not a fidelity tier

_Resolves Q1 (and reshapes Q2–Q5)._

**Sketch is not a fidelity level.** It is an interactive activity — a working mode — that can happen at *any* fidelity (language, model, specification). The output of a sketch is a rough, informal artifact produced during a grill-with-context dialogue; the output of a *generate* is the formal per-fidelity artifact.

Restated:

- **Fidelity** — an axis: language → model → specification. Unchanged. Governs how formal the *generated* artifact is.
- **Sketch (activity)** — an interactive grill loop at the current fidelity. Produces a scratch artifact that captures the shape without committing to the full template.
- **Generate (activity)** — non-interactive; emits the formal artifact per the fidelity's template.

**Sketch persists alongside the formal artifact across fidelity levels until the formal artifact at some higher fidelity fully absorbs it.** Sketches lead or lag the formal; they are the working memory of the grill.

**Consequence** — `grill-with-context` becomes embedded inside a new `sketch` action on the clean_engineering generator. The action is: *run a grill loop at the current fidelity → materialise the sketch → keep it beside the formal artifact until it's superseded.*

Reshapes the remaining questions:

- **Q2 (process vs structure)** — process guidance lives in the sketch action, not in the structure doc. Structure remains "what the formal output looks like." Sketching is "how to think while getting there."
- **Q3 (sketch notation)** — the terse indent notation is *one* sketch shape. Sketch outputs are informal; multiple shapes are fine as long as the grill produced them and they survive as scratch.
- **Q4 (grill flow)** — not a new skill and not a mode on grill-context. It is `sketch` as an action on the generator, wrapping `grill-with-context` internally.
- **Q5 (where it fits)** — cross-generator. Any generator that produces a formal artifact per fidelity can have a `sketch` action that runs grill-with-context at the current fidelity and keeps the scratch alongside. clean_engineering is just the first user.

### Insight — Sketch is a standalone action; the generator is a typed parameter

_Refines Q2′ and Q4._

`sketch` is **not** a peer method on each generator. It is a **standalone action** — one action, callable against any generator — that takes the generator as a **parameter**. The AI passes the generator at call time; the toolchain enforces type safety once inside.

```
sketch(generator: Generator, ...)
```

The **sketch shape is guided by the generator, not by the sketch action**:

- If the generator supplies **sketch guidance** (an optional instruction slot, e.g. `sketch.md` per fidelity or generator-wide), the sketch action loads it and shapes the interactive grill + output accordingly.
- If the generator supplies **no sketch guidance**, the sketch action falls back — the sketcher (the AI running the loop) has to invent a sketch format on the spot. That is a fallback, not the ideal path.

**Consequences:**

- Sketch is polymorphic on generator — one action, many domains. Same shape for clean_engineering, DDD, architecture, tests.
- Each generator opts into sketch by authoring its own sketch guidance. clean_engineering would ship (per fidelity) something like:
  - `contexts/clean_engineering/fidelities/language-sketch.md`
  - `contexts/clean_engineering/fidelities/model-sketch.md`
  - `contexts/clean_engineering/fidelities/specification-sketch.md`
- Sketch guidance is *thinking-first*, not shape-first — it tells the sketcher which questions to ask, what to elicit, and what compact notation to record (e.g. the terse indent notation the user offered would live in `language-sketch.md` as the recommended shape at that fidelity).
- `generate` remains a peer action on the generator; `sketch` sits outside.
- Structure docs (`clean-engineering.md`, templates) describe the *formal* artifact. Sketch guidance describes *how to think* to get there.

**clean_engineering's default sketch notation candidate** (from the user's example) — terse, indent-based, minimal syntax. Would live in `contexts/clean_engineering/fidelities/language-sketch.md` and possibly reused/tightened at the higher fidelities:

```
thing : base thing
  simple thing or thing not explored or thing defined elsewhere
  thing that has no id outside of parent 
       sub thing
       sub thing
       sub operation
  thing operation thing thing        <-- should relate to things above
  associatedThing 

  ----
 associatedThing
      thing
      thing operation thing
       -> _interaction_with_internal_important_enough_to_show
       -> thing.interaction_with_a_thing thing thing
```

Legend implicit in the notation:

| Symbol | Meaning |
|---|---|
| `thing` | any concept — class, property, operation, whatever hasn't earned a distinct name yet |
| `thing : base thing` | subtype of |
| indent | nested / owned / belongs-to |
| `----` | separator between a class block and an associated class block |
| `-> _internal_name` | interaction with an internal (private) helper |
| `-> other.operation` | interaction with another class's operation |

### Insight — Sketch is a decorator, not an action; action chaining is the real primitive

_Refines the previous insight; broader architectural claim._

The right primitive isn't a `sketch` action bound to `Generator`. It's **action chaining via decorators**. `sketch` is one decorator among several that wrap and compose behaviour around any action or agent.

**Signature (conceptual):**

```
@action
def sketch(context, template):
    "sketch the solution in note form and present to user before proceeding.
     use an interactive flow to sketch out ideas until the user confirms —
     same shape as grill-me."
```

`sketch` takes only `context` and (optionally) a `template`. It is completely generic — it does not know about clean_engineering, DDD, generators, or anything else. To decide *how* to sketch, it looks at:

1. **the `template` argument** — an explicit sketch shape passed in
2. **the `context`** — attachments, upstream sketches, generator metadata, examples
3. **fallback** — if it finds no example, the sketcher (the running AI) invents a sketch format for the domain at hand

This decoupling means `sketch` is portable across every agent and action in the system.

**Decorator composition on agents.** Instead of building `sketch` into `Generator`, decorate:

```
clean_engineering
  @context     ← implements the base chained action (generate)
  @sketch        ← wraps that base with sketch behaviour in a standard way
```

Decorators stack:

```
@sketch
@grill-context
class clean_engineering: ...
```

The runtime layers wrappers around the base action so that invoking clean_engineering's action fires the sketch loop → grill loop → base generate, or any subset the caller opts into.

**Wrap flow for `@sketch`:**

```
@sketch wraps <method>
  1. get sketch instructions from the wrapped thing (or from context)
  2. sketcher.sketch(context, template)   ← interactive, produces sketch
  3. invoke the chained method            ← the underlying action runs
```

**Consequences that reshape earlier insights:**

- Sketch guidance no longer lives *inside* clean_engineering as a special clean_engineering concept. clean_engineering exposes sketch guidance the same way any other decorated agent does — as context/template the `@sketch` decorator can pick up.
- The generator no longer needs sketch-specific instruction slots. It just needs to ship a sketch template/example that the generic sketcher can find.
- Grill-with-context is *also* just a decorator (`@grill-context`), not a bespoke skill. Same composition mechanism.
- The `@sketch` + `@grill-context` combo becomes a first-class idiom: "before doing X, sketch it with the user via a grill loop, then do X."
- clean_engineering's concrete opt-in reduces to: (a) apply `@sketch` decorator, (b) ship an example/template sketch (like the terse indent notation above) somewhere the sketcher can find it, (c) that's it.

**Open sub-questions this raises:**

- **Q7 — decorator invocation model** — do decorators auto-fire on the wrapped method call, or does the AI explicitly choose the chain per call?
- **Q8 — template discovery** — how does `@sketch` locate the wrapped agent's sketch template? Convention (`{agent_root}/sketch-template.*`)? Explicit registration (`@sketch(template="…")`)? Search of context files?
- **Q9 — composition order** — with `@sketch @grill-context @context`, does sketch wrap grill wraps generate (outer→inner), or reversed? What happens when the user says "no" mid-loop — does the whole chain abort?
- **Q10 — decorator implementation** — is this a Python decorator on the class, a manifest annotation, or a runtime action registration?

### Insight — Decorators fire in declaration order (top-down)

_Resolves Q7 and largely Q9._

**Rule:** decorators fire in the **order they are declared on the class**, top-down. First-declared runs first; the base action (from `@context` or equivalent) runs last.

```
@sketch          ← fires 1st
@grill-context   ← fires 2nd
@context       ← base action fires 3rd (last)
class clean_engineering: ...
```

This is not Python's usual bottom-up decorator convention. This is an explicit, declaration-order semantic — the reader sees the invocation order by reading top-down.

**Consequences:**

- **No ambiguity about opt-in vs auto-fire.** Decorators auto-fire. To skip one, don't annotate it. There is no per-call chain selection; the class defines the chain.
- **No manifest routing needed** — the class declaration IS the routing.
- **Predictable composition** — `@sketch @grill-context` always means "sketch then grill", not the reverse. Swap the annotations to change the order.
- **Base action always terminates the chain** — `@context` (or whatever produces the actual work) sits at the bottom; everything above wraps it.
- **Q9 partially answered:** composition order is declaration order. What happens on abort mid-chain (e.g. user rejects a sketch) is still open — probably "abort propagates upward, no base action runs."

**Remaining sub-questions:**

- Q8 (template discovery) — how `@sketch` finds the wrapped agent's sketch template.
- Q9 residual — abort semantics mid-chain.
- Q10 — technical realisation of the decorators (Python decorator on class → manifest registration → tools run wrapper?).

### Insight — Template discovery: context first, convention fallback, sketcher invents

_Resolves Q8._

Direct restatement of the user's earlier framing ("it should look at context and other attachments provided to see if it can find an example of how to sketch"). Three-tier lookup, in order:

1. **Session context / attachments** — if the current invocation carries sketch examples (user-provided attachment, upstream artifact, an active sketch already in the workspace), use those. User-provided context always wins.
2. **Convention on the wrapped agent** — `{agent_module_dir}/sketch-template.*` (mirrors how `@context` resolves `formats/{format}/{slug}-template.*`). Zero registration required by the agent; folder shape is the contract.
3. **Sketcher invents** — if neither of the above yields a template, the sketcher (the running AI) invents a sketch shape for the domain at hand. Explicitly a fallback, not a design target.

**Consequences:**

- Agent authors have one job to opt into `@sketch`: drop a `sketch-template.*` next to the module. No registration, no manifest slot to fill.
- Session-level context always overrides — a user pasting an example in chat immediately shapes the sketch, no matter what the agent ships.
- The convention keeps `@sketch` as a pure decorator (no arguments, no configuration) — annotation-only.

**Concrete for clean_engineering:** ship `contexts/clean_engineering/sketch-template.md` (or per-fidelity `contexts/clean_engineering/fidelities/{fidelity}-sketch-template.md` if the shape should vary) with the terse indent notation as the canonical shape. Then annotate `@sketch` on `clean_engineering` and the decorator picks it up automatically.

---

### Insight — Annotate the action, not the class; `sketch` extends `Action` the same way `generate` does

_Resolves Q10 and corrects the earlier class-level framing._

The right primitive isn't a class-level decorator stack. It's **method-level (action-level) decorators**, because `sketch`, `grill-with-context`, and `generate` are all **actions** — they all extend the same `Action` base. Chainability is a property of actions, not of classes.

```python
class clean_engineering:
    @sketch
    @grill_with_context
    def generate(self, ...):
        ...
```

Reading top-down: on any invocation of `generate`, first `sketch` fires, then `grill_with_context`, then the base `generate` body runs. Declaration order = execution order (per Q7).

**Consequences that correct earlier framing:**

- **Annotate the action, not the class.** The class no longer carries `@sketch` / `@grill-context`. The specific action that should be chainable does.
- **An agent can chain different actions differently.** `generate` might be `@sketch @grill_with_context`; `validate` might have no chain; `transform` might be just `@grill_with_context`. The class doesn't dictate one chain for everything.
- **`sketch`, `grill_with_context`, `generate` all extend the base `Action`.** `Action` is the primitive. Chainable actions are the composition mechanism.
- **`@context` (or `@concept_class_annotation`) stays as class-level** — it declares "this class is a generator" (an agent kind) and registers its methods. It is NOT a chained decorator; it is a class marker.
- **Runtime realisation** mirrors the existing pattern in `primitives/`: `@instruction` and `@tool` already decorate methods and register manifest entries via `_instruction_filter_key` etc. `@sketch` and `@grill_with_context` follow the same pattern — Python method decorators that register the chain in the manifest so `python -m tools run` wraps the base action at call time.
- **Chain discovery for tooling:** the manifest exposes each chained action's stack so external callers (AI, CLI) can see the flow before invoking.

## Still open (deferred to implementation)

- **Q9 residual — abort semantics.** If a user rejects a sketch or grill mid-loop, does the whole chain abort silently or does the base action still run with a "no sketch" flag? Current expectation: abort propagates upward, no base action runs. Confirm at implementation time.
- **Persistence lifecycle for produced sketches.** Where sketches live on disk and when they retire. Natural convention: `.context/sketches/{slug}-{fidelity}.sketch.md` alongside `.context/domain-context.md`, retire when the higher-fidelity formal artifact absorbs them.

## Recap — where the design has landed

- **Fidelity axis stays** — language / model / specification unchanged. Not renamed. Not augmented.
- **Sketch is an activity, not a fidelity.** Happens at any fidelity via the generic `sketch` action.
- **The primitive is chainable actions.** `sketch`, `grill_with_context`, `generate` all extend `Action`. Chaining is composition of actions.
- **Decorators annotate the action, not the class.** Different methods on the same class can have different chains.
- **Declaration order = execution order.** Top-down on the method definition; base action body runs last.
- **Template discovery** — session context first, convention second (`{agent_dir}/sketch-template.*`), sketcher invention as fallback.
- **`@sketch` and `@grill_with_context` implementation** — Python method decorators registering in the manifest, matching the existing `@instruction` / `@tool` pattern in `primitives/`.
- **clean_engineering's concrete opt-in:** decorate `generate` with `@sketch` (and `@grill_with_context` when wanted), ship a canonical `contexts/clean_engineering/sketch-template.md` (the terse indent notation). Done.

## Implementation status

### Shipped — `sketch/` module

Landed 2026-07-13. All under `C:\dev\abd-context-driven-delivery\sketch\`:

- **`sketch.py`** — `Sketcher` toolset with three tools (`find_template`, `save_sketch`, `list_sketches`) and one standalone `sketch_session` action. Callable today via `python -m tools manifest sketch.sketch:Sketcher`.
- **`_decorator.py`** — `@sketch` decorator. Marks an `@action` method with `_sketch_wrapped = True` and a `_sketch_preamble` string. Raises `TypeError` when applied to a non-action.
- **`sketch.md`** — canonical philosophy / behavior contract (loop, tiered discovery, persistence lifecycle, composition rules).
- **`sketch-template.md`** — default terse-indent template (fallback in tiered discovery).
- **`__init__.py`** — exports `sketch` and `Sketcher`. Import order is deliberate: `Sketcher` first, `sketch` decorator last, so `from sketch import sketch` binds to the decorator function and not the shadowing submodule.
- **`.context/sketch-behavior.md`** — maintainer narrative pointing at this design record as the source of truth.

Verified working:

- `python -m tools manifest sketch.sketch:Sketcher` returns a full YAML manifest with all tools and the `sketch_session` action.
- `from sketch import sketch, Sketcher` resolves to the decorator function and the class.
- `@sketch` on top of `@action` sets both markers; `@sketch` on a bare function raises with a helpful message.

### Shipped — Slice 1: ActionExpander integration

Landed 2026-07-13. Made the mechanism slightly more generic than sketch-only:

- **`actions/action.py`** — added `_action_preambles(action_func)` helper that reads a `_action_preambles` list attribute on any action function. Both `_parse_body_static` and `_parse_body_resolved` now prepend the returned strings to the expanded prose.
- **`sketch/_decorator.py`** — `@sketch` now prepends its preamble to `_action_preambles` on the wrapped function (in addition to keeping the existing `_sketch_wrapped` / `_sketch_preamble` marker attributes for introspection).
- **Why prepend, not append** — Python applies decorators inner-first (bottom-to-top). Prepending means the top-declared decorator's preamble ends up FIRST in the list, so declaration order still equals execution order at expansion time. When `@grill_context` lands, both decorators stack cleanly with no ordering fixup.

### Shipped — Slice 4 (partial): BDD specs

Landed 2026-07-13 at `sketch/sketch_spec.py` — 10 examples, all passing:

- `@sketch` decorator: sets `_sketch_wrapped` / `_sketch_preamble` markers, contributes to `_action_preambles`, guards against non-@action targets.
- ActionExpander integration: preamble appears first in expanded prose, original docstring preserved, original tool steps preserved.
- Sketcher toolset: manifest signature exposes 3 tools + 1 action, `find_template` falls back to the default, `save_sketch` writes to the expected `.context/sketches/{slug}-{fidelity}.sketch.md` path.

Supporting file: `sketch/examples/demo.py` — a real `.py` module with a minimal `@sketch @action` combo (needed because `inspect.getsource` can't read string-eval'd classes).

**Regression check:** 111/111 specs pass (101 pre-existing + 10 new sketch specs). No changes needed elsewhere. Pre-existing failures in `action_agent_spec.py` (`'ToolAgentBlock' object has no attribute 'instruct_run'` in `before_all`) are unrelated to this work.

### Shipped — Slice 2: `@grill_with_context` decorator

Landed 2026-07-13. `grill_context/` now exports both a standalone toolset and a chainable-action decorator:

- **`grill_context/_decorator.py`** — `@grill_with_context` decorator. Guards non-`@action` targets. Sets `_grill_wrapped` / `_grill_preamble` markers for introspection. Contributes to the wrapping chain via `add_action_wrapper(func, name="grill_with_context", preamble=…)`.
- **`grill_context/__init__.py`** — re-exports `grill_with_context` (decorator) and `GrillContext` (toolset). Deliberate import order: toolset first, decorator last, so `from grill_context import grill_with_context` binds to the decorator function (matches the `@sketch` package convention).
- **`grill_context/grill_context.py`** — untouched. The standalone `GrillContext.grill_with_context` action still runs the interactive loop directly.

### Shipped — Slice 3: Wire clean_engineering

Landed 2026-07-13. `contexts/clean_engineering/ooad.py` now overrides `generate` with `@sketch @grill_with_context @action` — top-down declaration order becomes top-down execution order. The base action body is duplicated from `Generator.generate` (small copy, worth the decorator-clarity trade-off).

- **`contexts/clean_engineering/sketch-template.md`** — clean_engineering-flavoured terse-indent template. Tiered discovery: `Sketcher.find_template(agent_dir="clean_engineering")` picks this up before falling back to `sketch/sketch-template.md`. Vocabulary tightened to clean_engineering (class, property, operation, subtype, composition, aggregation, association) instead of the generic `thing` placeholder.

### Shipped — Slice 4: Manifest surface for chained actions

Landed 2026-07-13. The `chain` field is now first-class in the action manifest:

- **`actions/action.py`** — generalised the framework hook. Added `add_action_wrapper(func, name, preamble)` helper that decorators call to contribute both a **name** (into `_action_wrappers`, exposed as `chain` in the manifest) and a **preamble** (into `_action_preambles`, injected first in the expanded prose). `Action.signature_entry` now emits `chain: [...]` when any wrappers are registered. `action_wrapper_names(func)` returns the ordered names for external callers.
- **`sketch/_decorator.py`** and **`grill_context/_decorator.py`** — both decorators use the shared helper, no ad-hoc list manipulation.
- **Verification:** `python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering` shows `generate` with `chain: [sketch, grill_with_context]` — the AI sees the full stack before calling.

### Regression status

Full sweep: **120/120 specs pass** across `action`, `sketch`, `grill_context`, `primitives`, `generator`, `clean_engineering`, `tools`. New coverage lives in `grill_context/grill_context_decorator_spec.py` (10 examples) — asserts wrapper markers, wrapper-name registration, preamble prepending, decorator stacking (`@sketch` + `@grill_with_context` at once), and the manifest `chain` field (present when wrapped, absent otherwise).

