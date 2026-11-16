"""What one source file imports: the class names it brings in, and the files its relative script imports reach."""

from __future__ import annotations

import re
from pathlib import Path
from typing import List

_SCRIPT_IMPORT = re.compile(r"""(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*\(?\s*)['"](\.{1,2}/[^'"]+)['"]""")
# An import or re-export TypeScript erases: `import type { A } from './x'`, or a braced list whose every name is
# marked `type`. It names a type for an annotation and never runs, as Python's `if TYPE_CHECKING:` imports do.
_TYPE_IMPORT_STATEMENT = re.compile(r"""\b(?:import|export)\s+type\b[^;'"]*?\bfrom\s*['"][^'"]+['"]""")
_BRACED_IMPORT_STATEMENT = re.compile(r"""\b(?:import|export)\s*\{([^}]*)\}\s*from\s*['"][^'"]+['"]""")
_PY_FROM_IMPORT = re.compile(r"^\s*from\s+[\w.]+\s+import\s+(\([^)]*\)|[^\n]+)", re.M)
_JS_IMPORT = re.compile(r"\bimport\s+(?:type\s+)?([\w$]+)?\s*,?\s*(?:\{([^}]*)\})?\s*from\b")
_QUALIFIED_CLASS = re.compile(r"\.([A-Z]\w*)\b")
_IMPORT_ALIAS = re.compile(r"\s+as\s+\w+")


class ScriptImports:
    """<<Value Object>> The imports of one source file's text, in Python or a script language."""

    def __init__(self, source_text: str) -> None:
        self._text = source_text

    def class_names(self) -> set[str]:
        """The names the file imports (`from x import A`, `import { A } from`) or reaches as `module.Class`."""
        names: set[str] = set(_QUALIFIED_CLASS.findall(self._text))
        for match in _PY_FROM_IMPORT.finditer(self._text):
            names.update(_IMPORT_ALIAS.sub("", item).strip() for item in match.group(1).strip("()").split(","))
        for default, braced in _JS_IMPORT.findall(self._text):
            names.add(default)
            names.update(_IMPORT_ALIAS.sub("", item).strip() for item in (braced or "").split(","))
        names.discard("")
        return names

    def targets(self, file: Path, root: Path) -> List[str]:
        """Root-relative paths named by the relative script imports (`./x`, `../y`) of file that run. A type-only
        import is erased by TypeScript, so it is no dependency and is left out."""
        found: List[str] = []
        for specifier in _SCRIPT_IMPORT.findall(self._without_type_imports()):
            resolved = (file.parent / specifier).resolve()
            if resolved.is_relative_to(root.resolve()):
                found.append(resolved.relative_to(root.resolve()).as_posix())
        return found

    def _without_type_imports(self) -> str:
        """The source with every import TypeScript erases blanked: `import type ...`, and `import { type A, type B } ...`."""
        text = _TYPE_IMPORT_STATEMENT.sub("", self._text)
        return _BRACED_IMPORT_STATEMENT.sub(lambda match: "" if self._all_marked_type(match.group(1)) else match.group(0), text)

    def _all_marked_type(self, braced_names: str) -> bool:
        names = [item.strip() for item in braced_names.split(",") if item.strip()]
        return bool(names) and all(name.startswith("type ") for name in names)
