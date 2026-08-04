"""Scanner: do not invent a parallel object model beside a live hierarchy.

Rule: do-not-invent-parallel-object-models

When existing objects already carry the data, wrap or extend them. A package
that defines a coordinating *Model/*Schema holding two or more *Entry/*Dto/
*Record bag types, plus a *Scraper (or scrape/build_model/to_model) that
builds that model, is the scrape-then-second-model anti-pattern.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

from code_scanner import CodeScanner

RULE = "do-not-invent-parallel-object-models"

_MODEL_RE = re.compile(r".+(Model|Schema)$")
_ENTRY_RE = re.compile(r".+(Entry|Dto|Record)$")
_SCRAPER_RE = re.compile(r".*Scraper$")
_SCRAPE_METHODS = frozenset({"scrape", "build_model", "to_model"})


class DoNotInventParallelObjectModelsScanner(CodeScanner):
    """Flag scraped *Model + *Entry families beside a live object hierarchy."""

    RULE = RULE

    def scan(self, root: Path, files: list[Path]) -> list:
        # Explicit paths (repair fixtures under examples/) must still be scanned.
        classes = self._collect_classes(root, files)
        if not classes:
            return []

        models = {name: meta for name, meta in classes.items() if _MODEL_RE.match(name)}
        entries = {name for name in classes if _ENTRY_RE.match(name)}
        if not models or len(entries) < 2:
            return []

        scrapers = self._scrapers_building_models(classes, set(models))
        if not scrapers:
            return []

        violations = []
        for model_name, meta in models.items():
            held = sorted(entries & meta["type_refs"])
            if len(held) < 2:
                continue
            builders = sorted(
                scraper for scraper, built in scrapers.items() if model_name in built
            )
            if not builders:
                continue
            entry_list = ", ".join(held)
            scraper_list = ", ".join(builders)
            violations.append(
                self.violation(
                    f"Parallel object model '{model_name}' holds [{entry_list}] "
                    f"and is built by [{scraper_list}]. Wrap or extend the live "
                    f"hierarchy instead of scraping into a second model "
                    f"({RULE}).",
                    location=str(meta["path"]),
                    line=meta["lineno"],
                )
            )
        return violations

    def _collect_classes(
        self, root: Path, files: list[Path]
    ) -> dict[str, dict]:
        collected: dict[str, dict] = {}
        for file_path in files:
            path = file_path if file_path.is_absolute() else Path(root) / file_path
            if not path.is_file() or path.suffix.lower() != ".py":
                continue
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                collected[node.name] = {
                    "path": path,
                    "lineno": node.lineno,
                    "type_refs": self._type_refs_in_class(node),
                    "methods": {
                        child.name: child
                        for child in node.body
                        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                    },
                }
        return collected

    def _type_refs_in_class(self, node: ast.ClassDef) -> set[str]:
        refs: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, ast.AnnAssign):
                refs.update(self._names_from_annotation(child.annotation))
            elif isinstance(child, ast.arg) and child.annotation is not None:
                refs.update(self._names_from_annotation(child.annotation))
            elif isinstance(child, ast.FunctionDef) and child.returns is not None:
                refs.update(self._names_from_annotation(child.returns))
            elif isinstance(child, ast.AsyncFunctionDef) and child.returns is not None:
                refs.update(self._names_from_annotation(child.returns))
            elif isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                refs.add(child.func.id)
        return refs

    def _names_from_annotation(self, annotation: ast.AST) -> set[str]:
        names: set[str] = set()
        if isinstance(annotation, ast.Name):
            names.add(annotation.id)
        elif isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
            names.add(annotation.value)
        elif isinstance(annotation, ast.Attribute):
            names.add(annotation.attr)
        elif isinstance(annotation, ast.Subscript):
            names.update(self._names_from_annotation(annotation.value))
            names.update(self._names_from_annotation(annotation.slice))
        elif isinstance(annotation, ast.Tuple):
            for elt in annotation.elts:
                names.update(self._names_from_annotation(elt))
        elif isinstance(annotation, ast.BinOp):  # X | Y
            names.update(self._names_from_annotation(annotation.left))
            names.update(self._names_from_annotation(annotation.right))
        return names

    def _scrapers_building_models(
        self, classes: dict[str, dict], model_names: set[str]
    ) -> dict[str, set[str]]:
        found: dict[str, set[str]] = {}
        for name, meta in classes.items():
            is_scraper_type = bool(_SCRAPER_RE.match(name))
            has_scrape_method = any(
                method_name in _SCRAPE_METHODS for method_name in meta["methods"]
            )
            if not (is_scraper_type or has_scrape_method):
                continue
            built = model_names & meta["type_refs"]
            if built:
                found[name] = built
        return found


if __name__ == "__main__":
    from scanners import run_scanner_main
    from code_scanner import collect_python_files

    raise SystemExit(
        run_scanner_main(
            DoNotInventParallelObjectModelsScanner,
            RULE,
            collect_python_files,
        )
    )
