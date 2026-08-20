# Strategy: Context as code, verified by tests

We want to get the most accurate context we can for an existing system so that we can make further changes in an AI augmented mode  with the least amount of drift or hallucination. 

Strategy: Walk each scenario against the **real seam** of the layer you are proving, then lock that confirmation into a **runnable story** that speaks domain language.
That work does three jobs at once:

1. **Prove** the artifacts match the real system.
2. **Lock** that proof into a test so the next person does not re-walk it by hand.
3. **Explore** the full behavior surface (errors, empty states, “this call must not happen”), not only the happy path the sketch named.

We get an **executable domain language** around the app, and a **concise, checkable context for AI** — not a wiki that drifts, but code that fails when the story or the domain model is wrong. We achieve this by:

- capturing how the **running system** actually behaves
- writing that capture as **Given / When / Then** stories that call a **domain model** — operations a business audience and a technical audience can both read
- making those tests executable, in the language of the domain, object-oriented and precise enough for a technical audience
- having tests call **domain operations**, not poke the app directly


Each system uses same story tests. Each system is tested by running a system specific implementations of the **same** domain interfaces. Stories call operations (`rail.submit(payment)`, `account.register()`, `plans.available()`). Config chooses which wrapper runs.

Domain implenentations only talk to the app under test. Outside system use **Stubs** or **mocks**. A **mock** is a stand-in for an outbound call: it proves what went out (method, URL, essential params, or that a call did *not* happen).  A **stub** is a canned neighbor response: it controls what comes back (body, status) so we can see how the app behaves given that data.

For a **frontend** we want to prove the UI: stub the next layer down (the API it calls, and any vendors it talks to directly) and mock that it made the right next-layer call. For a  **backend** we want to prove the API (real HTTP into *it*): stub further downstream (eg vendors) and mock that it made the right vendor call.



---

## Why

**Context as code.** Guidelines, story maps, domain models, and acceptance tests are generated and checked using automated tests. Prose that cannot be validated will drift. Code that has no story will be guessed.

**Capture actual system functionality.** The source of truth is the app under test in a sandbox — not memory, not a vendor PDF, not an inferred happy path. Walk the running app; increments confirm a slice of that surface against the live seam.

**Get a baseline.** A story map outline plus named bounded contexts and aggregates is the baseline. Everything after that is a micro-increment against that outline, not a new invention of the product.

**Verified context, no drift.** Markdown is a view. The story test (and the domain classes it calls) is the check. When an AI changes code, the same tests that encoded the baseline say whether the change still matches the system. That is why automated tests are the safety net for AI work — not a separate QA phase.

**Business-understandable and precise.** Two audiences, one model. Stories speak Given / When / Then in the language of the work. DDD (bounded contexts, aggregates, operations) and Clean Engineering (modules, types, code) make the same facts precise enough to compile and run. If a form is only “readable” or only “technical,” it is the wrong form.

**One language across teams.** Align the domain model across systems so the same operations are what people say — within a team and across groups. Front-end, back-end, and further systems wrap the **same** names, not three local dialects. If each group keeps its own vocabulary, you don't have shared understanding; you have translation.

**Wrap the system, don’t replace it.** The app is already the source of truth. The domain model is a language over that app, not a second implementation. A rewrite invents behavior; a wrap stays answerable by the live seam.

---

## Summary of Steps

- Stand the app up **alone** with [ContextSetup](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/utilities/context_setup).
- Document what it actually does with [Stories](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/context_tools/stories) and [DDD](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/context_tools/ddd) against that isolated app. Scaffold a story map and a bounded-context / aggregate outline. Then, with a human in the loop, take **one micro-increment** at a time — one story (default), or one BDD describe, or one aggregate operation. Write the Given / When / Then, and the required **domain classes and operations**, including underlying application code required to implement the test. Build / extend fixtures (example data) and mocks / stubs required to support the tests. Render a markdown view of both story map / story scenarios as well as the domain model. Allow the human to review for semantic correctness. Run tests until green, repeat until the app is covered. Once you have confidence the system is working, expand the scope to larger slices.

Run each step as **`/stories /ddd /<action>`**. 

Example: `/stories /ddd /document /specification` — one story’s scenarios and the classes, operations, and relationships in a bounded context for that story

---

## Steps

One increment at a time. Green, then the next, until the outline is covered.

### 1 — Set up the sandbox

Isolate the app with [ContextSetup](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/utilities/context_setup). Classify externals, write the **minimum** stubs (canned neighbor bodies) at the outermost boundary, smoke-test, scout pages. Do not stub the seam you are proving. Point it at the **application repository on disk**. That writes `tests/stubs/{system}/` (global) or `domain/{aggregate}/stubs/{system}/` (domain-owned) and `sandbox/extracted-context/app-extraction/` in the **capture repo**. Never a domain folder inside `tests/` or inside `tests/stubs/`.

```
/context-setup /capture_from_live_app
against the application repository on disk, as a web app; write stubs and scout into the capture repo
```

That action always smoke-tests and scouts. It calls `complete_capture` only when the scout has FAIL or WARN pages.

### 2 — Scaffold from the running app

Open a session **in the capture repo**. That is where `session.md`, tests, domain, and the scripts that **point at the application clone** live. Context comes from the running app; you do not open the session in the app repo. Scaffold only — no Given / When / Then, no operations, no classes. This is **discovery**: for Stories an **initial story map** (epics / sub-epics / story names); for DDD an **initial bounded-context / aggregate hierarchy** (names only). Markdown is the default at this fidelity — no format argument required. Capture what the running isolated app shows; do not invent the product. Creates `<capture-repo>/.context/sessions/<name>/session.md`. Same capture repo and run on later calls.

```
/stories /ddd /scaffold  OR /stories /ddd /discovery  more complete
follow [this strategy](acceptance-test-strategy.md) — discovery: scaffold an initial story map from the running isolated app (epics / sub-epics / stories, not scenarios); and an initial bounded-context / aggregate hierarchy from the running isolated app; markdown is the default
```

### 3 — Document Stories and DDD against the running app

The running app is the context. Document Stories and DDD **together**, one small slice — not iterate (no inbound iteration loop). Stories: capture the scenarios for **one** story (what the actor does). DDD: capture the **classes, operations, and relationships** for the aggregates (and associated) **inside a bounded context**. Do not invent depth the isolated app has not shown. When this run should be a markdown view, pass **`format markdown`** on the command.

```
/stories /ddd /document /specification
follow [this strategy](acceptance-test-strategy.md) — capture the scenarios for one story, and the classes, operations, and relationships of its aggregates within a bounded context, from the running isolated app; format markdown
```

### 4 — Write the story and tactical domain as code, execute tests until green

Write this story’s **scenarios as test code** and the **tactical domain** (classes, operations, relationships of the aggregates inside a bounded context) as code. Execute. Fix until they pass. Do not stub away the seam you are proving.

**Stories** live under **`tests/`**, following the story map — one file per story per tier, named for the seam, not for a product:



```
tests/{epic}/{sub-epic}/{story-name}.front-end.ts
tests/{epic}/{sub-epic}/{story-name}.back-end.ts
```

Same Given / When / Then. Different wrappers. Further tiers use the same story name and a suffix for that system (whatever you are proving), not a second story tree.

**Domain** lives under **`domain/`**, following DDD: bounded context, then aggregate. Interface plus one file per tier, in the aggregate’s folder:

```
domain/{bounded-context}/{aggregate}/{class}.ts              ← interface (all tiers implement this)
domain/{bounded-context}/{aggregate}/{class}.front-end.ts    ← UI / browser wrap
domain/{bounded-context}/{aggregate}/{class}.back-end.ts     ← API / message wrap
domain/{bounded-context}/{aggregate}/{class}.{system}.ts     ← any further tier, named after that system
```

`{bounded-context}` is the domain module. `{aggregate}` is the sub-module. Do not dump all interfaces in one folder and all front-end code in another. Stories import the interface; only the matching `.{tier}.ts` file may touch that tier’s seam.

```
/stories /ddd /document /engineering
follow [this strategy](acceptance-test-strategy.md) — write this story's scenarios as tests and the tactical domain (classes, operations, relationships) as code; run them; fix until they pass
```

### 5 — Human reviews

Read the GWT, the named aggregate/operation, and the running app. Reject invented steps, screen-as-class, and replaying a prior story as a Given. Green tests can still encode the wrong story.

this should be logged automatically but if it's not, each time youfind a mistake, [log the mistake](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/utilities/eval/log_mistake.md) **immediately** — once you have landed on a fix you can [log the correction](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/utilities/eval/log_correction.md) with the same `entry_id`.

```
/log_mistake
the wrong file, the failed rule, one line of what was wrong — now, before the fix
```

```
/log_correction please log it now that we have a correct result
```




### 6 — Repeat until the app is covered

Next increment on the outline. Cover distinct behaviors (errors, empty, must-not-call), not only the happy path. Stop when stories + domain + tests fail if the captured behavior changes. Same call as step 4.

AI should have the commands in Context so you can just use natural language.

---

## Where everything lives

```
<cdd-repo>/                         # context-driven delivery tools (Stories, DDD, ContextSetup, eval)
<app-repo>/                         # application under test (step 1); may also be the capture repo
<capture-repo>/                     # open the session here; scripts point at the app
  .github/                          # deploy this capture (workflows)
  .context/sessions/<name>/         # session.md, mistakes/, repairs/
  sandbox/extracted-context/           # ContextSetup scout
  domain/
    shared/                       # Collection, Seedable, seed bases
    browser-session/              # frontend harness
    api-session/                  # backend harness
    {aggregate}/
      {class}.ts                  # interface (shared)
      {class}.front-end.ts          # frontend wrap
      {class}.back-end.ts           # backend wrap
      {class}.{system}.ts           # any further system you choose
      stubs/{system}/             # this aggregate's neighbors, by system
  tests/
    story-test.ts                   # given / when / then DSL
    stubs/
      {system}/                     # global systems only (no owning domain)
    {epic}/
      examples/                     # fixtures shared by stories in this epic
      givens.ts                     # reusable seeds for this epic
      {sub-epic}/
        examples/                   # fixtures shared by stories in this sub-epic
        givens.ts                   # reusable seeds for this sub-epic
        {story}.{tier}.ts           # GWT for this story at this seam
        examples/                   # fixtures used only by this story
```


**the application repository** — the clone ContextSetup pointed at (step 1). The running app; not where capture artifacts land unless it *is* the capture repo.

**the capture repo** — open the session here. Scripts in this repo point at the application clone (step 1). Story-map and BC/aggregate scaffold live here (step 2). Session: `<capture-repo>/.context/sessions/<name>/session.md`. Scout: `sandbox/extracted-context/`. Stubs that belong to a domain go in that aggregate’s folder (`domain/{aggregate}/stubs/{system}/`). `tests/stubs/{system}/` is only for global systems. Never a domain folder inside `tests/`. Mistakes: `mistakes/` until a correction nests them under `repairs/` (step 5).

**`<capture-repo>/tests/{epic}/{sub-epic}/{story-name}.{tier}.ts`** — Given / When / Then per story per seam (step 4). Skip `{sub-epic}/` when the map has none. Fixtures and `givens.ts` sit at the lowest folder that actually shares them — story, sub-epic, or epic. Do not hoist “just in case.”

**`<capture-repo>/domain/{bounded-context}/{aggregate}/{class}.ts`** — domain interface; `{class}.front-end.ts`, `{class}.back-end.ts`, `{class}.{system}.ts` are the wraps (step 4).

---

## Tools

**[ContextSetup](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/utilities/context_setup)** — `/context-setup /capture_from_live_app` (and `smoke_test`, `scout_app`). Isolate the app: stubs, smoke, scout. No session.

**[Stories](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/context_tools/stories)** and **[DDD](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/context_tools/ddd)** — `/stories /ddd /<action>`. Scenarios together with classes, operations, and relationships of aggregates inside a bounded context.

[Eval](https://forge.abdworks.net/abd-context-driven-delivery/src/branch/main/utilities/eval) — `/stories /ddd /log_mistake` then `/log_correction`. Not automatic on a human reject.

Other tools (Clean Engineering, BDD, Diagnose, …) are in the [context-driven delivery docs](https://forge.abdworks.net/abd-context-driven-delivery/).
