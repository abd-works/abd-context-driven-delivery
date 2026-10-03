# Rules fix

Replace scanners with language-and-fidelity CodeQL. `validate` runs on the **rule collection** in one CodeQL batch (pack `rules.ql`), not a per-rule loop.

Each remaining task is executed with:

- `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code`
- `/bdd-development`

---

## Accomplished

### A. Rule query metadata

Rule `.ql` files (not loaders) carry `@practice`, `@fidelity`, `@node`, `@id {practice}/{fidelity}/name`, and `@connection` when the rule crosses practices. Blank ` *` lines were stripped from those comment blocks. `@problem.severity` was dropped so CodeQL does not require `@kind problem`.

### B. Language-specific packs

Queries live at `{practice}/model/{language}/codeql/{loaders,rules}` for `python`, `javascript`, and `typescript`. JavaScript and TypeScript share the javascript extractor; packs differ by file globs. Layout helpers: `harness/knowledge_graph/model/codeql_layout.py`.

### C. Harness path wiring

- Populate facts from `clean_engineering/model/{language}/codeql/loaders/`.
- `GraphRule.graphQuery` resolves `.../codeql/rules/{slug}.ql`.
- `detect_language` returns `python` | `javascript` | `typescript`; database create uses `--language=` of the extractor (`typescript` → `javascript`).
- Subject filter writes at the pack root (not `loaders/` or `rules/`).
- Practice `codeql_model_spec` / `model_spec` `_PACK` paths point at the language pack.
- `assert_pack_hits` looks in `rules/`.

### D. Language-shaped matches (partial)

Stories, DDD, and BDD JavaScript/TypeScript queries use `CallExpr` / `ClassDefinition` / `MethodDefinition`. Python stories use `Call` / `With`. Clean Engineering **loaders** on JS/TS use the javascript AST. Clean Engineering **rule** `model.qll` on JS/TS is still Python-shaped and needs a later port (task 8).

### E. Pack parity spec

`harness/knowledge_graph/model/codeql_layout_spec.py` asserts the same loader and rule stems exist for all three languages on every practice.

---

## Remaining tasks

Each task is independent enough to start from this plan plus the files it names. Do not mix scanner removal with the Validate action change in one commit.

### 1. Drop scanners from `Rule`

**Why.** Scanners are gone. `Rule` still has `scanner`, `bind_scanner`, and `validate()` text that says to run a scanner.

**Do.**

- Remove `scanner`, `bind_scanner`, and scanner sentences from `Rule.validate` in `harness/guidance/rule.py`.
- Stop markdown collection from calling `bind_scanner` (`harness/markdown/markdown.py`).
- Rewrite `harness/guidance/rule_spec.py` (no scanner on the rule; validate is AI/markdown for a **base** `Rule`).
- Reword `Validate.createRule` so it writes a CodeQL query, not a scanner (`actions/validate/validate.py`).

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

### 2. Align `validate` signatures

**Why.** `Rule.validate`, `GraphRule.validate`, `RulesCollection.validate` (`@collect`), and `Validate.validate` all mean different things. GraphRule’s `validate` currently calls `super().validate()` twice.

**Do.** Same name, same job per type:

| Type | `validate` means |
|---|---|
| `Rule` | Instructions to judge the artifact against **this rule’s markdown body** (no CodeQL, no scanner). |
| `RulesCollection` | Join those instruction texts for **base** rules only (`@collect` stays valid here). |
| `GraphRule` | Does not run CodeQL alone. Either unused, or returns the same instruction shape as `Rule` for the prompt channel. Hits come from the collection. |
| `GraphRulesCollection` / `RuleRegistry` | One CodeQL run for the pack(s): `rules.ql` + requested slugs, language from `CodeQL.detect_language()`, fidelity from the `.ql` header (`@fidelity`). Writes violations onto graph nodes. |
| `Validate.validate` | Calls **`item.rules.validate`** (the collection). Optional single `Rule` stays an instruction-only path for a base rule. |

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

### 3. `GraphRulesCollection.validate` runs the pack once

**Why.** Integrated evaluation already exists on `PracticeGraph._evaluate_graph_rules` / `_rule_rows` / `CodeQL.run_rules(pack/rules.ql, slugs)`. `GraphRule.evaluate` still calls `run_rules(..., [self.slug])` when hits are missing. Collection `@collect` walks every child `validate`.

**Do.**

- Add `GraphRulesCollection` (or give `RuleRegistry` a real `validate`) that: pick language pack → `run_rules` on `rules.ql` for **all** runnable slugs in that pack → map hits with `refine_rows` / `evaluate(..., hits=batch[slug])`.
- Stop `GraphRule.evaluate` from issuing its own CodeQL process when the collection already has a batch.
- Select the pack with `codeql_pack(practice, detect_language())`. Read `@fidelity` / `@practice` from the query file when markdown fidelity is empty.

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

### 4. Validate action uses the collection, not a per-rule loop

**Why.** `Validate.validate` already prefers `item.rules.validate` when `rule` is omitted. That property is `@collect` on `RulesCollection`, which **joins every child’s `validate()`**. For graph-backed practices that walks every `GraphRule` independently and never hits the pack `rules.ql` batch.

**Do.**

- In `actions/validate/validate.py`, keep one call: `item.rules.validate` (no extra for-loop over slugs).
- Override `validate` on the **graph** rules collection so `@collect` is not used for GraphRules. Base `RulesCollection.validate` may keep `@collect`.
- Update `actions/validate/validate.md` and specs: collection validate = CodeQL batch + report; single base `Rule` = instruction text only.
- Confirm `satisfy` still calls `Validate().validate(item)` and gets collection-level results.

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

### 5. Bind GraphRule from QL metadata, not scanners or markdown-only fidelity

**Why.** Fidelity and node kind live on the rule `.ql` (`@fidelity`, `@node`, `@id`). `GraphRule.from_markdown` / `has_graph_query` still treat markdown as the source of truth.

**Do.**

- Parse the query header when wrapping a `GraphRule`.
- Prefer `@fidelity` from the language pack that matches the workspace.
- Keep markdown body as the human rule text.
- Specs: a `.ql` with `@fidelity scenarios` binds that fidelity even if the bullet sat in another section.

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

### 6. Markdown and install stop looking for scanners

**Why.** After task 1, leftover `*_scanner.py` binds, installer copy, and create-rule prompts will still mention scanners.

**Do.** Grep `bind_scanner`, `scanners/`, “matching scanner” under `harness/`, `actions/validate/`, `installation/`. Remove or rewrite each call site. Leave practice `model/drawio/scanners` alone unless a spec still binds them through `Rule.bind_scanner`.

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

### 7. Port Clean Engineering JS/TS rule `model.qll`

**Why.** Packs exist for parity. JS/TS **rules** still import a Python AST `model.qll`. Collection validate on a TypeScript tree will fail those queries until this port exists.

**Do.** Rewrite `practices/clean_engineering/model/javascript/codeql/model.qll` (and copy/adapt to `typescript`) using `ClassDefinition`, `MethodDefinition`, `CallExpr`, `FieldDefinition`. Keep the same predicate names the `.ql` files already call. Run `assert_pack_hits` only after JS examples exist, or keep Python `codeql_model_spec` as the CE pack test.

**Skills.** `/abd-context-driven-delivery/practices/clean-engineering/clean-engineering-code` and `/bdd-development`.

---

## Suggested order

1 → 6 (scanners gone) → 2 (signatures) → 3 (collection CodeQL) → 4 (Validate action) → 5 (QL metadata bind). Task 7 can proceed in parallel once packs are stable; it is required before collection validate is useful on JS/TS Clean Engineering trees.
