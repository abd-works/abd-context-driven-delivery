"""Scanner: `missing-spec` - every module with a public surface must have a spec
that actually observes something.

Rule: missing-spec

A Python file is considered specifiable when it defines at least one public class
or public top-level function. Such a file must be covered by a spec in the same
folder - one named after it (`<stem>_spec.py`, `<stem>_agent_spec.py`) or a package
spec that imports it - and that spec must contain at least one `it` observation.
A module with no spec, or with a spec that declares no observations, has no
specified behavior at all: BDD cannot report clean on it.

This is the structural floor under `full-surface-coverage`. That rule asks whether
every public member is observed; this one asks whether anything is observed at all.

FP profile: LOW. Structural check; fires only on files with real public definitions,
and never inside template or scanner folders. Demo folders are handled by the shared
skip list, which yields to any path the caller named explicitly.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

from scan import Scanner, ScannerRunner

_SKIP_DIR_NAMES = frozenset(
    {
        ".context",
        ".git",
        "__pycache__",
        ".venv",
        "build",
        "coverage",
        "dist",
        "node_modules",
        "scanners",
        "templates",
        "venv",
    }
)

_NON_MODULE_FILENAMES = frozenset({"__init__.py", "conftest.py", "register.py", "setup.py"})

_OBSERVATION_RE = re.compile(r"\bit\s*\(", re.MULTILINE)


class MissingSpecScanner(Scanner):
    """Flag modules with a public surface but no spec, or a spec with no observations."""

    RULE = "missing-spec"

    def scan_file(self, root: Path, file_path: Path) -> list:
        if file_path.suffix != ".py":
            return []
        if self._is_skipped(file_path) or not self._is_module_source(file_path):
            return []
        surface = self._public_surface(file_path)
        if not surface:
            return []

        specs = self._covering_specs(file_path, surface)
        if not specs:
            return [
                self.violation(
                    f"Module '{file_path.name}' defines a public surface "
                    f"({', '.join(sorted(surface))}) but no spec beside it observes any of it. "
                    f"Add {file_path.stem}_spec.py and specify the behavior before the module "
                    f"counts as specified.",
                    location=str(file_path),
                )
            ]
        if any(self._observes_behavior(spec) for spec in specs):
            return []
        return [
            self.violation(
                f"Module '{file_path.name}' has a spec that declares no observations. "
                f"Add at least one `it should …` to {specs[0].name}.",
                location=str(specs[0]),
            )
        ]

    def _is_skipped(self, path: Path) -> bool:
        return any(part in _SKIP_DIR_NAMES for part in path.parts)

    def _is_module_source(self, path: Path) -> bool:
        name = path.name
        if name in _NON_MODULE_FILENAMES:
            return False
        return not (
            name.endswith("_spec.py")
            or "_spec." in name
            or name.startswith("test_")
            or name.endswith("_test.py")
            or "_test_helper" in name
        )

    def _public_surface(self, path: Path) -> set[str]:
        """Top-level public class and function names defined by *path*."""
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError, UnicodeDecodeError):
            return set()
        definitions = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        return {
            node.name
            for node in tree.body
            if isinstance(node, definitions) and not node.name.startswith("_")
        }

    def _covering_specs(self, path: Path, surface: set[str]) -> list[Path]:
        """Specs in the same folder that reach into *path*.

        A spec named after the module (``<stem>_spec.py``, ``<stem>_agent_spec.py``)
        covers it by convention. Any other spec in the folder - a package spec such
        as ``_focus_spec.py`` covering several files - counts only when it imports
        the module or names one of its public definitions. Stories artifacts are
        covered by their tier helpers rather than a ``_spec`` file.
        """
        folder = path.parent
        named = set(folder.glob(f"{path.stem}*_spec.py"))
        named |= set(folder.glob(f"{path.stem.removesuffix('_story')}_test_helper.*.py"))
        reference = self._reference_pattern(path.stem, surface)
        package_level = {
            spec for spec in folder.glob("*_spec.py") if reference.search(self._read(spec))
        }
        return sorted((named | package_level) - {path})

    def _reference_pattern(self, stem: str, surface: set[str]) -> re.Pattern[str]:
        """Match a code reference - an import of the module or one of its public
        names. Prose alone does not count; the module name in a sentence is not
        an observation of its behavior."""
        module = re.escape(stem)
        alternatives = [
            rf"import\s+[\w.]*\b{module}\b",
            rf"from\s+[\w.]*\b{module}\b\s+import",
            *(rf"\b{re.escape(name)}\b" for name in sorted(surface)),
        ]
        return re.compile("|".join(alternatives))

    def _read(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return ""

    def _observes_behavior(self, spec_path: Path) -> bool:
        """A mamba spec observes through `it(…)`; a tier helper observes through the
        story interface it implements, so its presence is the observation."""
        if "_test_helper." in spec_path.name:
            return True
        return bool(_OBSERVATION_RE.search(self._read(spec_path)))


if __name__ == "__main__":

    def collect_python_files(root: Path) -> list[Path]:
        return sorted(root.rglob("*.py"))

    raise SystemExit(
        ScannerRunner.run_scanner_main(
            MissingSpecScanner, MissingSpecScanner.RULE, collect_python_files
        )
    )
