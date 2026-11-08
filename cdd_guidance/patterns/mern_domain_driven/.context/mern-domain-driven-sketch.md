# Sketch — mern_domain_driven

Source: `abd-skills/practices/architecture-centric-engineering/specs/mern-domain-first-specification/`
(old-world ABD skill: `archiecture-specification.md`, `rules/*.md` × 18,
`scanners/typescript/*.py` × 18, `templates/`, diagrams).

> **Historical.** This sketch records how the pattern was designed. Where it names an old scanner file, that scanner
> was never ported: the rule is judged by the validating agent. `mern_domain_driven.md` is the pattern as it is.

Decisions below are locked (see `grill-answers.md`).
Where the port plan differed from what was built, the section says what was built.

---

## Purpose

Generate **production TypeScript code + acceptance tests for one vertical
slice** of a domain-module-organized MERN stack (MongoDB / Express / React /
Node), for a story and module design that already exists. It is the
implementation fidelity of the MERN stack — not a design-lifecycle tool.

## Non-goals

- Does not story-map, does not design module boundaries, does not design
  screens/navigation. Those are `stories` (`story_map`), `clean_engineering`
  (`modules`/`model`), and `ux` — run *before* this tool, not by it.
- No `fidelities` progression of its own — it always runs its two companions
  at one fixed point each: `stories` at `acceptance_tests`, `clean_engineering`
  at `code`.

## Seam

`MernDomainDriven` is a `PracticeGuidance` pattern (`pattern = "mern_domain_driven"`)
in TypeScript format. It adds only what is MERN-specific — the naming and layering
rules, the domain-module / app-server / app-client / tests template shape — on top
of its Stories companion. Stories' `acceptance_tests` fidelity names Clean
Engineering `code` as its companion (`clean_engineering: code` in `stories.md`), so
the tests-then-code composition comes from Stories, not from this pattern.

```
cdd_guidance/patterns/mern_domain_driven/
├── mern_domain_driven.py
├── mern_domain_driven.md          # ## Overview, ## Guidance (the rules by theme), ## Shared rules
├── templates/                      # {epicSlug}/ feature package and tests/{epicSlug}/ scaffold
└── _examples/
    ├── examples.md
    └── wires/                      # worked slice: recipients / wire-payment
```

## Public API

```python
@agent_toolset
class MernDomainDriven(PracticeGuidance):
    pattern = "mern_domain_driven"

    def __init__(self) -> None:
        # format="typescript", default_workspace_folder="packages"
```

`generate`, `validate`, and the other actions are the shared actions run on this
guidance; the pattern does not override them.

**Resolved — the format gap.** The draft relied on `Stories.ce()` passing
`format` to Clean Engineering. That operation no longer exists: a fidelity names
its Clean Engineering companion (`FidelityGuidance.clean_engineering`), and
`FidelityGuidance.companion_instructions` adds that companion's instructions
to the guidance's own.

## Rules (ported 1:1 from old `rules/*.md`, same slugs)

Grouped by theme under `## Guidance` and listed again under `## Shared rules` in
`mern_domain_driven.md`. The file name in parentheses is the old scanner the rule came
from; the scanners were not ported, so these rules are judged by the validating
agent rather than by a graph rule.

**Domain module organization**
- `organize-by-domain-module` — `packages/<domain>/{shared,client,server}`; composition roots (`app-server`, `app-client`) present. (`domain_structure_scanner.py`)
- `share-domain-logic` — entities/schemas/business rules defined once in `shared/`. (`share_domain_logic_scanner.py`)
- `maintain-layer-purity` — `shared/` is framework-free; `client/` and `server/` never cross-import. (`layer_purity_scanner.py`)

**Naming / layering**
- `use-ubiquitous-language` — names come from the domain model; no `Manager`/`Handler`/`Helper`/`Domain*`. (`ubiquitous_language_scanner.py` → `naming_convention_scanner.py`)
- `cross-layer-method-naming` — same `{verbNoun}` stem across shared → client → server → route → API. (`cross_layer_naming_scanner.py`)
- `preserve-arg-names-across-layers` — arg names unchanged across layer boundaries; only types narrow. (`arg_naming_scanner.py`)
- `property-casing-transform` — `camelCase` in TS; `snake_case` in JSON/MongoDB docs. (`casing_transform_scanner.py`)
- `consistent-view-naming` — React components end in `View`/`CardView`; no `Page` suffix. (`view_naming_scanner.py`)

**App server / routes**
- `delegate-routes-to-domain-server` — route handlers are thin; no repo calls, no shared logic inline. (`route_delegation_scanner.py`)
- `ensure-type-safe-routes` — route handlers compile without implicit `any`; `req.user` typed. (`type_safety_scanner.py`)
- `standard-mutation-response` — all mutations on the same aggregate return the same response shape. (`mutation_response_scanner.py`)

**Types & entities**
- `implement-domain-entities-correctly` — business rules on domain classes; schema validates at boundaries. (`entity_behavior_scanner.py`)
- `implement-full-interfaces` — every `implements` covers all interface members; no stub no-ops. (`interface_implementation_scanner.py`)

**Packaging**
- `use-valid-package-names` — `package.json` names are valid npm-scoped names derived from the domain. (`package_names_scanner.py`)
- `include-all-external-dependencies` — every import has a declared dependency; project compiles after install. (`dependency_declarations_scanner.py`)

**Testing architecture** (companion to `stories` `acceptance_tests` rules — MERN fixes *tier* = `server | client | e2e`)
- `test-story-driven` — tests mirror the story hierarchy; Given/When/Then helpers at all three tiers. (`test_structure_scanner.py`)
- `scaffold-test-scripts` — `scripts/test.sh` / `test.ps1` / `test-e2e.sh` / `test-e2e.ps1` present. (`test_scripts_scanner.py`)
- `use-thorough-e2e-tests` — E2E tests are independent; no blanket deletes; `app-client` required. (`test_isolation_scanner.py`)

18 rules: the 17 named above map 1:1 to the old `rules/*.md`; the old
`mern_scanner.py` was a shared scanner base, not a rule, and was not ported.

## Testing tiers (this tool's addition to `stories.acceptance_tests`)

`stories.acceptance_tests` is generic (`*_spec.{tier}`, tier unspecified).
This tool pins `tier ∈ {server, client, e2e}` and the stub policy per tier —
ported from the old spec's four-layer testing architecture:

| Tier | Real | Stubbed | Entry point |
|---|---|---|---|
| domain unit (always present, lives beside the class, not under this tool) | shared domain classes | nothing | class method call |
| server | domain + repo + test DB | nothing | Supertest → Express route |
| client | React tree + hooks + client domain | `<<Entity>>Api` via `vi.mock` | Testing Library render |
| e2e | full stack | nothing | Playwright `page.goto` |

Base helper (`<sub-epic>.base.ts`) carries Given/When/Then vocabulary;
tier helpers extend it — same names, different mechanism. This maps onto
CE's **Example factories** modes (`Isolated` = ctor-injected mocks,
`Production` = real collaborators) rather than inventing a parallel concept —
worth confirming server/client/e2e helpers *use* `{Type}ExampleFactory`
rather than hand-rolled fixtures. ?

## Templates

Placeholders unchanged from the old spec (`{{DomainName}}`, `{{domainName}}`,
`{{EpicName}}`, `{{epicSlug}}`, `{{SubEpicName}}`, `{{subEpicSlug}}`):

```
templates/
├── {epicSlug}/            # feature package: app.ts, serve.ts, main.tsx, {EpicName}View.tsx, {domainName}/
├── tests/{epicSlug}/      # test scaffold
├── package.json  vitest.config.ts  README.md
```

`generate` fills these for the touched module(s), then calls the two
companions — the templates are *followed*, not executed by a template
engine; no new templating machinery.

## UX hand-off (upstream input only)

`app-client/<<Feature>>View.tsx`, `<<domain>>/client/<<Entity>>ListView.tsx`,
etc. assume `ux` already produced the site map / screen boxes / layout for
this slice. `generate` cites that artifact under **Sources / context** on
the touched view files — it does not call `ux`.

## Naming / location — resolved

- Class `MernDomainDriven`, module
  `cdd_guidance.patterns.mern_domain_driven.mern_domain_driven:MernDomainDriven`.
  Stack-specific implementation tools live under `cdd_guidance/patterns/`, beside
  `lern_domain_driven`.
