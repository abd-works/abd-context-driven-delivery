---
name: stories-acceptance_tests
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-acceptance_tests

Use stories guidance at `acceptance_tests` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-scenarios
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

## acceptance_tests

**Default format:** typescript

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam. `{tier}` is `front-end`, `back-end`, or any other system name you are proving. No `{story}/` folder and no `*_story` / `*_test_helper` split. Fixtures live in `examples/` and `givens.ts` at the lowest shared epic / sub-epic / story folder.

### Rules

- **`behavioral-observable-outcomes`** — same rule as **scenarios**: assertions stay in domain-observable terms, never internals.
- **`explore-full-interaction-surface`** — same rule as **scenarios**: acceptance_tests must cover the explored interaction surface, not just translate the first main-flow scenario into Playwright. Trace react-hook-form rules, shared validation components, and stubbed failure modes during the sandbox walk-through; add a `scenario()` per distinct behavior.
- **`gwt-steps-trace-to-domain-operations`** — same rule as **scenarios**: each step in the test traces to a named domain operation or property. A hop to the next step is a named operation on the arriving aggregate, not a route or `waitForCompletion()`.
- **`reconcile-live-immediately`** — same rule as **scenarios**: live disagreement updates the sketch before the test is locked.
- **`explain-deep-link-arrival`** — same rule as **scenarios**.
- **`given-only-what-the-system-checks`** — same rule as **scenarios**.
- **`when-holds-the-operation`** — same rule as **scenarios**.
- **`then-and-chaining`** — same rule as **scenarios**.
- **`extract-assertion-helper`** — same rule as **scenarios**.
- **`infrastructure-in-lifecycle-hooks`** — same rule as **scenarios**.
- **`load-with-identity-in-hand`** — same rule as **scenarios**.
- **`seed-prior-story-as-given`** — same rule as **scenarios**.
- **`reuse-owning-aggregate-stubs`** — same rule as **scenarios**.

---

## Templates

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
# Pattern: with story / with given / with when / with then / with and_ — Mamba blocks via story_test.py.

from __future__ import annotations

from mamba import after, before

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import {AggregatePascal}
from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        self.{app_camel} = {AppPascal}E2e.initialize(config)

    with after.all:
        if self.{app_camel}:
            self.{app_camel}.close()

    with background():
        with given("{background given step}"):
            self.{app_camel}.{background_operation}()

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with then("{observable surface outcome}"):
                pass  # Assert {observable surface outcome}

        with scenario("{validation branch while typing}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with and_("{follow-on when step}"):
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()

            with then("{validation message on domain object}"):
                pass  # Assert {validation message on domain object}

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
                pass  # Assert {error cleared on domain object}

        with scenario("{main-flow outcome}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with when("{submit operation on domain object}"):
                self.{aggregate_camel}.{field} = {valid_aggregate_value}
                self.{aggregate_camel}.{operation}()

            with then("{post-condition on loaded aggregate}"):
                pass  # Assert {post-condition on loaded aggregate}


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


def background() -> None:
    pass


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

    def visit_Module(self, node: ast.Module) -> ast.Module:
        node = super().visit_Module(node)
        expanded: list[ast.stmt] = []
        for stmt in node.body:
            if isinstance(stmt, ast.With):
                name = self._get_name(stmt)
                if name == "background":
                    expanded.extend(self._expand_background(stmt))
                    continue
                if name == "scenario":
                    expanded.append(self._transform_scenario(stmt, []))
                    continue
            expanded.append(stmt)
        node.body = expanded
        return node

    def _transform_story(self, node: ast.With) -> ast.ClassDef:
        context_expr = self._context_expr_for(node)
        story_name = self._human_readable_context_expr(context_expr)
        body: list[ast.stmt] = []

        for stmt in node.body:
            if isinstance(stmt, ast.With) and self._get_name(stmt) == "background":
                body.extend(self._expand_background(stmt))
            else:
                transformed = self.visit(stmt)
                if isinstance(transformed, ast.stmt):
                    body.append(transformed)

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

    def _expand_background(self, node: ast.With) -> list[ast.ClassDef]:
        background_givens: list[list[ast.stmt]] = []
        scenarios: list[ast.ClassDef] = []

        for stmt in node.body:
            if not isinstance(stmt, ast.With):
                continue
            step = self._get_name(stmt)
            if step == "given":
                background_givens.append(stmt.body)
            elif step == "scenario":
                scenarios.append(
                    self._transform_scenario(stmt, background_givens)
                )

        return scenarios

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