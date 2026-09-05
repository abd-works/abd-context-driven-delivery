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
