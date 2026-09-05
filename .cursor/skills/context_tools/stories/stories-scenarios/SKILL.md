---
name: stories-scenarios
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-scenarios

Use stories guidance at `scenarios` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-story_map
@stories-scaffold

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | typescript | Main-flow scenarios per story (single or multiple); optional variations; `examples/` + `givens.ts`. Pass `format markdown` when the strategy asks for a markdown view. |
| **acceptance_tests** | typescript | `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam (`front-end`, `back-end`, or another system name). No story folder. Fixtures: `examples/` + `givens.ts`. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.ts` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## scenarios

**Default format:** typescript

**Goal:** Main-flow scenarios per story (single or multiple) with optional variations.

**Produce:** Same `{story}.{tier}.ts` tree as acceptance_tests. Pass `format markdown` only when the strategy command names it.

### Rules

- **`behavioral-observable-outcomes`** — Name and Then in domain-observable terms; never internals.
- **`explore-full-interaction-surface`** — Scenarios are not complete when only the main-flow GWT from the sketch is written. Before locking scenarios (and again before acceptance_tests), walk the real UI and model **every distinct user-visible behavior**: inline rule checklists and how they change while typing, field-level validation errors clearing as input conforms, cross-field rules (confirm password, paste mismatch), submit-button gating, and server-side error surfaces. A story that only codifies the happy path when the screen has rich client-side validation is a **defect** — branch into additional scenarios (or scenario outlines with examples) per mechanical variation, not one paragraph that mentions "validation" in passing.
- **`gwt-steps-trace-to-domain-operations`** — Every Given / When / Then maps to a named domain operation or property. If a step cannot be traced, that is a modelling gap — add the operation or property; do not gloss over it. A hop to the next step is a named operation on the arriving aggregate (`prospect.verifyIdentity()`), not a route, `waitForCompletion()`, or driving the next concern through the previous aggregate.
- **`reconcile-live-immediately`** — The running app wins. When a walk-through disagrees with the sketch, fix the sketch in that increment before locking the test.
- **`explain-deep-link-arrival`** — A scenario that navigates to a parameterized route (`/sign-up/:planId`) must say how a user actually arrives: in-app navigation, marketing/external deep-link, or a wizard step with no URL change. Do not write `When they navigate to X` as if it were a button.
- **`given-only-what-the-system-checks`** — Given states conditions the **running system actually uses** for the behaviour under test. Do not Given a field the code never reads for that decision (`metadata.verified` when routing actually keys off `customer.billing.id`).
- **`when-holds-the-operation`** — When holds the domain operation being exercised. An empty When with a comment, or the operation called inside Then, is a defect. Then only asserts on what When already produced — no I/O in Then.
- **`then-and-chaining`** — The first outcome uses `then()`; every later outcome on the same interaction chains `.and()`. Repeated `then()` calls break the Gherkin narrative. Markdown `And` stays `And`.
- **`extract-assertion-helper`** — The same assertion shape more than twice becomes a named helper that takes a data bag. Call sites pass only the concrete values.
- **`infrastructure-in-lifecycle-hooks`** — Browser boot, app wiring, and `initialize` live in `beforeAll` / `afterAll`. `given(` is domain state only.
- **`load-with-identity-in-hand`** — `load` takes the identity already in hand. Do not assume a browser session. Load once at the highest Given that needs the aggregate and reuse the variable. A cart has no identity outside its prospect — reach it through the owner, not `cartRepository().current()`.
- **`seed-prior-story-as-given`** — A later story's Given is seeded from prior-story fixtures (`givens.ts` / `examples/`), not a replay of that story's When.
- **`reuse-owning-aggregate-stubs`** — For a non-core aggregate, take stubs from **that aggregate's folder / source repository** (`domain/{bounded-context}/{aggregate}/stubs/{system}/`). Do not invent a test-local stub. Do not stub the seam you are proving.

---

## Templates

### markdown

## components/evidence-table.md

---
fidelity: [exploration, specification]
artifact: [story-scenarios]
format: md
section: footer
---

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | `<source>` | `<location>` |


## components/story-header.md

---
fidelity: [exploration, specification]
artifact: [story-scenarios]
format: md
section: header
---
## Story: `<Verb–Noun Title>`

**Story type:** user | system | technical

**Sources / context:** `<pointer to domain source, AC, or conversation>`

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).


## scenario-inline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

## Behaviors

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Scenario 1: `<outcome-oriented scenario name>`

*Given* a ++`<ConceptA>`++ *`<value>`*  
  *And* that ++`<ConceptA>`++ *`<value>`* has a ++`<ConceptB>`++ *`<value>`*  
*When* the ++`<ConceptA>`++ *`<value>`* `<triggering action>`  
    using ++`<ConceptB>`++ *`<value>`*  
*Then* the ++`<observed concept>`++ is `<observable outcome>`  
  *And* the ++`<related concept>`++ is `<additional outcome>`  
  *But* no ++`<concept>`++ is `<what does not happen>`

### Scenario 2: `<alternate outcome-oriented scenario name>`

*Given* `<alternate setup state>`  
*When* `<alternate triggering action>`  
*Then* `<alternate observable outcome>`  
  *And* `<additional outcome>`


## scenario-main-flow.md

---
fidelity: [exploration]
artifact: [story-scenarios]
format: md
section: body
---

### Domain terms

- ++`<Concept>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

## Behaviors

### Scenario Outline: `<main-flow outcome name>`

*Given* a ++`<Concept>`++ from `helper.given<Concept…>({ mode: "fake" })`  
  *And* that ++`<Concept>`++ {`<concept_field>`}  
*When* the **`<Actor>`** `<triggering action>`  
*Then* `<observable outcome on the public interface of I{Concept}>`  
  *And* `<additional observable outcome>`

### Examples

| scenario   | `<concept_field>` | `<result_field>` |
|------------|-------------------|------------------|
| ++Scenario 1++ | `<value>`         | `<value>`        |

> Examples table documents the representative row. Code loads the same values from ExampleFactory (AI fills stubs).


## scenario-outline.md

---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

### Domain terms

- ++`<ConceptA>`++ — `<plain-language gloss>`
- ++`<ConceptB>`++ — `<plain-language gloss>`

> In steps: underline examples and domain terms (`++<Concept>++`, `++<example>++`). Italic concrete values (`*<value>*`).

### Evidence

| Source | Note |
|--------|------|
| `<pointer>` | `<why it matters>` |

### Background

*Given* a ++`<ConceptX>`++ from `helper.given<ConceptX…>({ mode: "fake" })`  
  *And* that ++`<ConceptX>`++ exposes `<public property / operation>`  

---

### Behaviors

#### Scenario Outline: `<outcome-oriented name>`

*Given* a ++`<ConceptA>`++ with {`<field_1>`}  
  *And* the ++`<ConceptB>`++ for that ++`<ConceptA>`++ is {`<field_2>`}  
*When* the **`<Actor>`** `<action>`  
*Then* the ++`<result concept>`++ `<outcome>` is visible on the public interface  
  *And* a ++`<related concept>`++ shows {`<field_3>`}

### Examples

| scenario   | `<field_1>` | `<field_2>` | `<field_3>` |
|------------|-------------|-------------|-------------|
| ++Scenario 1++ | `<value>`   | `<value>`   | `<value>`   |
| ++Scenario 2++ | `<value>`   | `<value>`   | `<value>`   |

> Markdown keeps examples tables for documentation. Code wires values via `{Type}ExampleFactory` (AI fills helper/story method bodies). Do not copy inventable `examples: [{ … }]` literals into code story files.

#### Scenario: `<variation — delta from main flow>`

*Given* … (only the delta from the main flow)  
*When* …  
*Then* …

### python

## scenario-template.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# # Params — fill before writing code
# epic:       {epic-verb-noun}           # kebab folder under tests/
# sub_epic:   {sub-epic-verb-noun}       # kebab folder under epic/ (omit level if story hangs off epic)
# story:      {story-verb-noun}          # Verb Noun title from the story map
# story_file: {story_snake_slug}         # snake file slug, e.g. sign_up_create_account
# tier:       e2e | front-end | back-end | {system}
#
# # Artifact layout (artifacts-mirror-story-hierarchy)
# tests/
#   {epic-verb-noun}/
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story_snake_slug}.{tier}.py     # one GWT file per story per tier
#
# # Machinery (copy once per tests/ tree — full source inlined below)
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: normal code inline under each with — same steps as scenario-template.ts.

from __future__ import annotations

from expects import be_above, be_none, equal, expect
from mamba import after, before

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        self.{app_camel} = {AppPascal}E2e.initialize(config)

    with after.all:
        if self.{app_camel}:
            self.{app_camel}.close()

    with background.each:
        with given("{background given step}"):
            self.{app_camel}.{background_operation}()

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with then("{observable surface outcome}"):
                self.{aggregate_camel}.{field} = ""
                self.{aggregate_camel}.validate()
                expect(len(self.{aggregate_camel}.errors.{field})).to(be_above(0))

        with scenario("{validation branch while typing}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with and_("{follow-on when step}"):
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()

            with then("{validation message on domain object}"):
                expect(self.{aggregate_camel}.errors.{field}).to(
                    equal({ERROR_CONSTANT}_MESSAGE)
                )

        with scenario("{validation clears when input conforms}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with and_("{prior invalid state}"):
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()

            with when("{corrective action}"):
                self.{aggregate_camel}.{field} = {valid_value}
                self.{aggregate_camel}.validate()

            with then("{error cleared on domain object}"):
                expect(self.{aggregate_camel}.errors.{field}).to(be_none)

        with scenario("{main-flow outcome}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with when("{submit operation on domain object}"):
                self.{aggregate_camel}.{field} = {valid_aggregate_value}
                self.{aggregate_camel}.{operation}()

            with then("{post-condition on loaded aggregate}"):
                loaded = (
                    self.{app_camel}
                    .{repository}()
                    .load(self.{aggregate_camel})
                )
                expect(loaded.is_at_{state}("{StateName}")).to(equal(True))


## story_test.py

# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Given / When / Then on Mamba — copy to tests/story_test.py once per tests/ tree.
#
# ```
# file: tests/story_test.py
# ```
#
# Stubs for `with story / background / scenario / given / when / then / and_` blocks.
# StoryNodeTransformer (below) compiles them into Mamba example groups at load time.

from __future__ import annotations

import ast
import os
import re
import sys
import types
from typing import Iterator

from mamba import nodetransformers
from mamba.example_collector import ExampleCollector

# Stubs — replaced by AST transform when Mamba loads the spec (same as mamba.description / mamba.it).
def story(_name: str) -> None:
    pass


class _Background:
    all = None
    each = None


background = _Background()


def scenario(_name: str) -> None:
    pass


def given(_name: str) -> None:
    pass


def when(_name: str) -> None:
    pass


def then(_name: str) -> None:
    pass


def and_(_name: str) -> None:
    pass


def _slug(value: str) -> str:
    slug = re.sub(r"[^0-9a-z]+", "_", value.strip().lower()).strip("_")
    return slug or "step"


class StoryNodeTransformer(nodetransformers.TransformToSpecsNodeTransformer):
    STORY = frozenset({"story"})
    STRUCTURE = frozenset({"background", "scenario"})
    STEPS = frozenset({"given", "when", "then", "and_"})

    def visit_With(self, node: ast.With) -> ast.AST:
        name = self._get_name(node)
        if name in self.STORY:
            return self._transform_story(node)
        if name in self.STRUCTURE or name in self.STEPS:
            return node
        node = super(StoryNodeTransformer, self).generic_visit(node)  # type: ignore[attr-defined]
        return super().visit_With(node)

    def _background_scope(self, node: ast.With) -> str:
        context_expr = self._context_expr_for(node)
        if isinstance(context_expr, ast.Attribute) and isinstance(
            context_expr.value, ast.Name
        ):
            if context_expr.value.id == "background" and context_expr.attr in (
                "all",
                "each",
            ):
                return context_expr.attr
        return "each"

    def _is_background_with(self, node: ast.With) -> bool:
        return self._get_name(node) == "background"

    def visit_Module(self, node: ast.Module) -> ast.Module:
        node = super().visit_Module(node)
        expanded: list[ast.stmt] = []
        for stmt in node.body:
            if isinstance(stmt, ast.With) and self._is_background_with(stmt):
                _story_givens, scenarios = self._expand_background(stmt)
                expanded.extend(scenarios)
                continue
            if isinstance(stmt, ast.With) and self._get_name(stmt) == "scenario":
                expanded.append(self._transform_scenario(stmt, []))
                continue
            expanded.append(stmt)
        node.body = expanded
        return node

    def _transform_story(self, node: ast.With) -> ast.ClassDef:
        context_expr = self._context_expr_for(node)
        story_name = self._human_readable_context_expr(context_expr)
        body: list[ast.stmt] = []
        story_givens: list[list[ast.stmt]] = []

        for stmt in node.body:
            if isinstance(stmt, ast.With) and self._is_background_with(stmt):
                scope = self._background_scope(stmt)
                bg_story_givens, scenarios = self._expand_background(stmt)
                if scope == "all":
                    story_givens.extend(bg_story_givens)
                body.extend(scenarios)
            else:
                transformed = self.visit(stmt)
                if isinstance(transformed, ast.stmt):
                    body.append(transformed)

        if story_givens:
            body = self._inject_story_givens(body, story_givens, node)

        return ast.copy_location(
            ast.ClassDef(
                name=self._prefix_with_sequence(f"Story_{_slug(story_name)}"),
                bases=[],
                keywords=[],
                body=body,
                decorator_list=[
                    self._set_attribute("_example_group", True),
                    self._set_attribute("_example_name", story_name),
                    self._set_attribute("_tags", []),
                    self._set_attribute("_pending", False),
                    self._set_attribute("_shared", False),
                ],
            ),
            node,
        )

    def _expand_background(
        self, node: ast.With
    ) -> tuple[list[list[ast.stmt]], list[ast.ClassDef]]:
        scope = self._background_scope(node)
        background_givens: list[list[ast.stmt]] = []
        scenarios: list[ast.ClassDef] = []

        for stmt in node.body:
            if not isinstance(stmt, ast.With):
                continue
            step = self._get_name(stmt)
            if step == "given":
                background_givens.append(stmt.body)
            elif step == "scenario":
                per_scenario_givens = (
                    background_givens if scope == "each" else []
                )
                scenarios.append(
                    self._transform_scenario(stmt, per_scenario_givens)
                )

        story_givens = background_givens if scope == "all" else []
        return story_givens, scenarios

    def _inject_story_givens(
        self,
        body: list[ast.stmt],
        givens: list[list[ast.stmt]],
        node: ast.AST,
    ) -> list[ast.stmt]:
        extra: list[ast.stmt] = [stmt for block in givens for stmt in block]
        for index, stmt in enumerate(body):
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "before_all":
                merged = list(stmt.body) + extra
                body[index] = ast.copy_location(
                    ast.FunctionDef(
                        name="before_all",
                        args=stmt.args,
                        body=merged,
                        decorator_list=stmt.decorator_list,
                    ),
                    stmt,
                )
                return body

        body.insert(
            0,
            ast.copy_location(
                ast.FunctionDef(
                    name="before_all",
                    args=self._generate_argument("self"),
                    body=extra,
                    decorator_list=[],
                ),
                node,
            ),
        )
        return body

    def _transform_scenario(
        self,
        node: ast.With,
        background_givens: list[list[ast.stmt]],
    ) -> ast.ClassDef:
        context_expr = self._context_expr_for(node)
        scenario_name = self._human_readable_context_expr(context_expr)

        scenario_givens: list[list[ast.stmt]] = []
        whens: list[list[ast.stmt]] = []
        thens: list[tuple[str, list[ast.stmt]]] = []
        last_kind: str | None = None

        for stmt in node.body:
            if not isinstance(stmt, ast.With):
                continue
            step = self._get_name(stmt)
            label = self._human_readable_context_expr(self._context_expr_for(stmt))
            if step == "given":
                scenario_givens.append(stmt.body)
                last_kind = "given"
            elif step == "when":
                whens.append(stmt.body)
                last_kind = "when"
            elif step == "and_":
                if last_kind in ("when", "and_when"):
                    whens.append(stmt.body)
                    last_kind = "and_when"
                elif last_kind in ("then", "and_then"):
                    thens.append((label, stmt.body))
                    last_kind = "and_then"
                else:
                    whens.append(stmt.body)
                    last_kind = "when"
            elif step == "then":
                thens.append((label, stmt.body))
                last_kind = "then"

        setup_body: list[ast.stmt] = []
        for block in (*background_givens, *scenario_givens, *whens):
            setup_body.extend(block)

        class_body: list[ast.stmt] = []
        if setup_body:
            class_body.append(
                ast.copy_location(
                    ast.FunctionDef(
                        name="before_all",
                        args=self._generate_argument("self"),
                        body=setup_body,
                        decorator_list=[],
                    ),
                    node,
                )
            )

        for index, (label, body) in enumerate(thens):
            example_name = f"Then {label}" if index == 0 else label
            display_name = f"it Then {label}" if index == 0 else f"it {label}"
            class_body.append(
                self._make_example_function(example_name, display_name, body, node)
            )

        return ast.copy_location(
            ast.ClassDef(
                name=self._prefix_with_sequence(f"Scenario_{_slug(scenario_name)}"),
                bases=[],
                keywords=[],
                body=class_body,
                decorator_list=[
                    self._set_attribute("_example_group", True),
                    self._set_attribute("_example_name", scenario_name),
                    self._set_attribute("_tags", []),
                    self._set_attribute("_pending", False),
                    self._set_attribute("_shared", False),
                ],
            ),
            node,
        )

    def _make_example_function(
        self,
        function_name: str,
        example_name: str,
        body: list[ast.stmt],
        node: ast.AST,
    ) -> ast.FunctionDef:
        return ast.copy_location(
            ast.FunctionDef(
                name=self._prefix_with_sequence(function_name),
                args=self._generate_argument("self"),
                body=body,
                decorator_list=[
                    self._set_attribute("_example", True),
                    self._set_attribute("_example_name", example_name),
                    self._set_attribute("_tags", []),
                    self._set_attribute("_pending", False),
                ],
            ),
            node,
        )


class StoryExampleCollector(ExampleCollector):
    STORY_SUFFIXES = (".e2e.py", ".front-end.py", ".back-end.py")

    def __init__(self, paths: list[str]) -> None:
        super().__init__(paths)
        self._node_transformer = StoryNodeTransformer()

    def _collect_files_containing_examples(self) -> list[str]:
        collected: list[str] = []
        for path in self.paths:
            if not os.path.exists(path):
                continue
            if os.path.isdir(path):
                collected.extend(self._collect_story_files_in_directory(path))
            elif self._is_story_file(path):
                collected.append(path)
        collected.sort()
        return collected

    def _collect_story_files_in_directory(self, directory: str) -> list[str]:
        found: list[str] = []
        for root, _dirs, files in os.walk(directory):
            for name in files:
                if self._is_story_file(name):
                    found.append(os.path.join(self._normalize_path(root), name))
        return found

    def _is_story_file(self, path: str) -> bool:
        return path.endswith("_spec.py") or any(
            path.endswith(suffix) for suffix in self.STORY_SUFFIXES
        )


def load_story_module(path: str) -> types.ModuleType:
    collector = StoryExampleCollector([path])
    modules = collector.modules()
    if not modules:
        raise RuntimeError(f"No story examples found in {path}")
    return modules[0]


def iter_story_modules(paths: list[str]) -> Iterator[types.ModuleType]:
    collector = StoryExampleCollector(paths)
    yield from collector.modules()


def patch_mamba_collector() -> None:
    """Use StoryNodeTransformer for all Mamba loads in this process."""
    nodetransformers.TransformToSpecsNodeTransformer = StoryNodeTransformer  # type: ignore[misc]

    original_init = ExampleCollector.__init__

    def _init(collector, paths):  # type: ignore[no-untyped-def]
        original_init(collector, paths)
        collector._node_transformer = StoryNodeTransformer()

    ExampleCollector.__init__ = _init  # type: ignore[method-assign]

    if "story_test" not in sys.modules:
        sys.modules["story_test"] = sys.modules[__name__]


def main() -> None:
    """Run Mamba with story AST transforms enabled."""
    patch_mamba_collector()
    from mamba.cli import main as mamba_main

    mamba_main()


if __name__ == "__main__":
    main()

See examples in `context_tools/stories/examples/` if needed.