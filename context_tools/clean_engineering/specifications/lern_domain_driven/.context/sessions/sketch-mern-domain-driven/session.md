# Session: sketch-mern-domain-driven

## Start

- **date:** 2026-08-03
- **path:** context_tools/engineering_specification/mern_domain_driven
- **goal:** Design mern_domain_driven: implementation-only context tool for the MERN domain-first stack (code + acceptance tests for an already-designed vertical slice), delegating to Stories (acceptance_tests fidelity) and CleanEngineering (code fidelity) via compose-like-normal-code, carrying its own ported scanners/rules/templates from the old-world spec, ux treated as upstream input only.
- **fidelities:** (unset)
- **contexts:** abd-skills/practices/architecture-centric-engineering/specs/mern-domain-first-specification

## Log

- grill: scope, composition, scanners, templates, ux role resolved -> `.context/grill-answers.md`
- sketch: seam, ported rules (18), testing tiers, templates plan, ux hand-off -> `.context/mern-domain-driven-sketch.md`
- grill: `Stories.ce()` format gap -> fix upstream (pass `format=self.format`); `engineering_specification/` confirmed as category folder
- sketch locked; ready to scaffold via create-context-tool on next go-ahead
- implemented (user go-ahead: "implement this using /bdd and /agent-bdd at the development level"):
  - upstream fix landed: `Stories.ce()` passes `format=self.format` when it's a CE code channel (`context_tools/stories/stories.py`); 3 new specs in `stories_spec.py` (21/21 green).
  - `mern_domain_driven.py` + `mern_domain_driven.md` scaffolded: `generate`/`iterate`/`satisfy` each call `super()` then compose `_clean_engineering()` (code, typescript) and `_stories()` (acceptance_tests, typescript); `# Contexts` carries the 18 ported rules grouped by theme, naming table, testing-tier table, ux hand-off note.
  - `templates/` copied verbatim from the old-world spec (32 files).
  - `scanners/mern_scanner_base.py` (MERNScanner + TypeScriptScanner, ported from `mern_scanner.py`/`ts_scanner_base.py` onto `utilities.scanners.Scanner`) + all 18 concrete scanners ported (1 orphan, `naming_convention_scanner.py`, dropped - no rule doc referenced it; slugs corrected against each rule's `scanner:` frontmatter, e.g. `use-domain-language` -> `use-ubiquitous-language`). `ScannerCollection(module_dir=...).discover()` finds exactly the 18 canonical slugs.
  - `examples/examples.md`: recipients/wire-payment worked slice (shared/server/client), ported from the old spec's walkthrough. Running the ported scanners for real against `templates/` surfaced a genuine pre-existing gap: the generic route template called `repo.*` directly, violating `delegate-routes-to-domain-server`.
  - **Fixed** (user go-ahead): added `templates/{domainName}/server/{DomainName}sServer.ts` (server-side domain class), rewrote `{domainName}.routes.ts` to delegate to it exclusively, renamed `{{DomainName}}sRepository` -> `{{DomainName}}RepositoryServer implements {{DomainName}}Repository` in `{domainName}.repository.ts`, updated `index.ts` and `app-server/app.ts`. Re-scanning `templates/` now reports zero `delegate-routes-to-domain-server` violations (only `scaffold-test-scripts` remains, expected for a template source dir with no `scripts/`/config files).
  - `mern_domain_driven_spec.py` (Bdd/regular, development fidelity): construction, companion pinning (`_stories()`/`_clean_engineering()`), contexts prose names all 18 slugs, scanner discovery = exactly 18, end-to-end scan confirms the template gap is closed. 17/17 green.
  - `mern_domain_driven_agent_spec.py` (AgentBdd/agentic, development fidelity, `harness: cli`): real `cursor-agent` CLI session reads the manifest header and drives `generate`; asserts `ok`, `read_context_index`/`record_context_root` tools offered, instructions mention the companions/session_guidance/templates. Ran for real (session `79029756-...`) - 1/1 green.
