# Sketch — mern_domain_driven

Source: `abd-skills/practices/architecture-centric-engineering/specs/mern-domain-first-specification/`
(old-world ABD skill: `archiecture-specification.md`, `rules/*.md` × 18,
`scanners/typescript/*.py` × 18, `templates/`, diagrams).

Decisions below are locked (see `grill-answers.md`); shapes below are draft —
review before I scaffold with `create-context-tool`.

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

`MernDomainDriven` — thin `BaseContextTool` domain. Its `generate` **inlines**
`Stories` and `CleanEngineering` (compose-like-normal-code) rather than
re-describing what they already do; it contributes only what's MERN-specific
on top: naming/layering rules, the domain-module/app-server/app-client/tests
template shape, and its own scanners.

```
context_tools/engineering_specification/mern_domain_driven/
├── mern_domain_driven.py
├── mern_domain_driven.md          # § Instructions / § Contexts (rules below) / § Generate
├── templates/                      # ported from old templates/ (domain-module, app-server, app-client, tests)
├── scanners/typescript/            # ported scanners, on utilities.scanners.Scanner contract
└── examples/
    └── examples.md                 # worked slice, e.g. recipients / wire-payment
```

## Public API (draft)

```python
class MernDomainDriven(BaseContextTool):
    default_workspace_folder = "packages"
    context_index_key = "mern_domain_driven"

    def __init__(self, path=None, session=None, workspace=None): ...

    def _stories(self) -> Stories:
        """Stories at acceptance_tests fidelity, typescript format."""
        return Stories(fidelity="acceptance_tests", format="typescript",
                        path=self._raw_path, session=self.workspace.name,
                        workspace=self.workspace.workspace_root)

    def _clean_engineering(self) -> CleanEngineering:
        """CleanEngineering at code fidelity, typescript format."""
        return CleanEngineering(fidelity="code", format="typescript",
                                 path=self._raw_path, session=self.workspace.name,
                                 workspace=self.workspace.workspace_root)

    @action
    def generate(self) -> str:
        """1. Fill templates/ for the domain module(s) touched by this slice
        (shared/server/client + app-server/app-client composition roots).
        2. self._clean_engineering().generate() - production code, applying
        the naming/layering rules below on top of CE's own OOAD rules.
        3. self._stories().generate() - *_spec.{tier} for tier in
        (server, client, e2e), applying the testing-architecture rules below.
        4. Run validate (this tool's scan + both companions' validate)."""
```

**Open — `Stories.ce()` format gap:** `Stories.generate()` at
`acceptance_tests` already calls `self.ce().generate()` internally (exactly
the "tests → matching code" composition this tool wants) — but `ce()`
constructs `CleanEngineering(fidelity="code", ...)` **without** passing
`format`, so it always renders Python, never TypeScript. Two ways to close
this gap — pick one before scaffolding:

1. Small upstream fix: `Stories.ce()` passes `format=self.format` (falls
   back to CE's own default when `self.format` isn't a CE channel). Fixes
   this for every TypeScript/Java/JS stack, not just MERN.
2. `MernDomainDriven.generate()` doesn't rely on `Stories.generate()`'s
   internal `ce()` call at all — it sequences `_clean_engineering().generate()`
   then `_stories().generate()` itself, both pinned to `typescript`, and
   accepts the redundant/wrong-format internal call as dead weight.

**Resolved: (1).** `Stories.ce()` will pass `format=self.format` (falling
back to CE's own default when `self.format` isn't a CE channel) — a small
upstream patch to `context_tools/stories/stories.py`, done once, ahead of
scaffolding this tool.

## Contexts (rule bullets — ported 1:1 from old `rules/*.md`, same slugs)

Grouped by theme; each pairs with a scanner in `scanners/typescript/` (last
column = old scanner file, ported into this tool's own `scanners/`).

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

18 rules ported (17 named above map 1:1 to the old `rules/*.md`; the 18th,
`mern_scanner.py`, is the shared scanner base, not a rule — becomes this
tool's `scanners/typescript/mern_scanner.py` base class, not a `§ Contexts`
bullet).

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

## Templates (port `templates/` → this tool's `templates/`)

Same tree as old spec, placeholders unchanged (`{{DomainName}}`,
`{{domainName}}`, `{{EpicName}}`, `{{epicSlug}}`, `{{SubEpicName}}`,
`{{subEpicSlug}}`):

```
templates/
├── {domainName}/{shared,server,client}/   # copy as packages/<domainNames>/
├── app-server/  app-client/                # composition roots
└── tests/{epicSlug}/...                    # test scaffold
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
  `context_tools.engineering_specification.mern_domain_driven.mern_domain_driven:MernDomainDriven`.
- `engineering_specification/` is a **category folder** — `mern_domain_driven`
  is the first of what will likely be several stack-specific implementation
  tools; the category folder owns no code/md of its own, just siblings.

## Next step

Once the two `?` items above are resolved, scaffold for real via
`create-context-tool`: full tree from
`context_tools/create_context_tool/templates/` (folder is currently just
this session — `scaffold-vs-patch` says build the full tree), port
`rules/*.md` prose into `mern_domain_driven.md` § Contexts as written above,
port `scanners/typescript/*.py` onto `utilities.scanners.Scanner` /
`ScannerCollection`, port `templates/`, and write one worked example under
`examples/` (recipients or wire-payment slice, matching the old spec's
worked example).
