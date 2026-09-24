"""Transformer mix-in — bind a logical Jinja template and recurse."""

from __future__ import annotations

from typing import Any, List

from jinja2 import Environment, TemplateNotFound


class Transformer:
    _logical_template = ""
    _tests_folder = "tests"

    def children(self) -> List[Any]:
        return []

    def get_templates_for(self, kind: str) -> list:
        if kind != "logical" or self._environment is None:
            return []
        if not self._logical_template:
            return []
        try:
            return [self._environment.get_template(f"{self._logical_template}.j2")]
        except TemplateNotFound:
            return []

    def render(self, kind: str) -> dict[str, str]:
        self._ensure_file_store()
        templates = self.get_templates_for(kind)
        if templates:
            for template in templates:
                self._apply_template(template)
        for child in self.children():
            self._render_child(child, kind)
        return self._root_files()

    def attach_environment(self, environment: Environment, root: "Transformer" | None = None) -> None:
        self._environment = environment
        self._file_root = root or self
        if root is None:
            self._files = {}
        for child in self.children():
            if isinstance(child, Transformer):
                child.attach_environment(environment, self._file_root)

    def _ensure_file_store(self) -> None:
        if getattr(self, "_file_root", None) is None:
            self._file_root = self
            self._files = {}
        if getattr(self, "_environment", None) is None:
            self._environment = None

    def _apply_template(self, template) -> None:
        path = self._output_path()
        if not path:
            return
        self._file_root._files[path] = template.render(node=self)

    def _render_child(self, child: Any, kind: str) -> None:
        if not isinstance(child, Transformer):
            return
        child._tests_folder = self._child_folder()
        child.render(kind)

    def _output_path(self) -> str:
        return ""

    def _child_folder(self) -> str:
        return self._tests_folder

    def _root_files(self) -> dict[str, str]:
        return getattr(self._file_root, "_files", {})
