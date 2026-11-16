"""What one source file imports: the classes it names, each with the module it names it from, and the files its
relative script imports reach."""

from __future__ import annotations

import posixpath
import re
from pathlib import Path
from typing import List, NamedTuple

_SCRIPT_IMPORT = re.compile(r"""(?:\bfrom\s*|\brequire\s*\(\s*|\bimport\s*\(?\s*)['"](\.{1,2}/[^'"]+)['"]""")
# An import or re-export TypeScript erases: `import type { A } from './x'`, or a braced list whose every name is
# marked `type`. It names a type for an annotation and never runs, as Python's `if TYPE_CHECKING:` imports do.
_TYPE_IMPORT_STATEMENT = re.compile(r"""\b(?:import|export)\s+type\b[^;'"]*?\bfrom\s*['"][^'"]+['"]""")
_BRACED_IMPORT_STATEMENT = re.compile(r"""\b(?:import|export)\s*\{([^}]*)\}\s*from\s*['"][^'"]+['"]""")
# Python's `from module import names`, the names on one line or in parentheses.
_PY_FROM_IMPORT = re.compile(r"^[ \t]*from[ \t]+(\.*[\w.]*)[ \t]+import[ \t]+(\([^)]*\)|[^\n]+)", re.M)
# Python's `import a.b.c`, `import a.b.c as g`, or several of them.
_PY_IMPORT = re.compile(r"^[ \t]*import[ \t]+([\w.]+(?:[ \t]+as[ \t]+\w+)?(?:[ \t]*,[ \t]*[\w.]+(?:[ \t]+as[ \t]+\w+)?)*)", re.M)
_PY_COMMENT = re.compile(r"#[^\n]*")
# A script's `import … from '…'` or `export … from '…'`, its clause before `from`, and the module it names.
_JS_FROM = re.compile(r"""\b(import|export)\s+((?:(?!\b(?:import|export)\b)[^;'"])*?)\s*\bfrom\s*['"]([^'"]+)['"]""")
_JS_CLAUSE = re.compile(r"(?:type\s+)?(?:([\w$]+)\s*,?\s*)?(?:\{([^}]*)\}|\*(?:\s+as\s+([\w$]+))?)?")
_ALIAS = re.compile(r"\s+as\s+")
_NAME = re.compile(r"[\w$]+")
# What every name a star import brings in is recorded as.
STAR = "*"
# The path alias a script imports the generated language adapters by. Each adapter module mirrors the Python module it is
# generated from (`@cdd/space/kanban/fidelity-progress` for `space/kanban/fidelity_progress.py`), and sends a class's
# data as `{Class}Data`.
LANGUAGE_ADAPTER_ALIAS = "@cdd/"
_ADAPTER_DATA_SUFFIX = "Data"
# The file an import names, after the path its import reads as: a Python module or package, or a script file.
_IMPORTED_FILE_ENDINGS = (".py", "/__init__.py", "", ".ts", ".tsx", ".js", ".jsx", "/index.ts", "/index.tsx", "/index.js")


def imported_files(target: str) -> List[str]:
    """The files an import of target may name, from the source root: a Python module or package, or a script file;
    TypeScript names the compiled `./x.js` for its source `x.ts`."""
    bases = [target, target.removesuffix(".js")] if target.endswith(".js") else [target]
    return [f"{base}{ending}" for base in bases for ending in _IMPORTED_FILE_ENDINGS]


class ClassReference(NamedTuple):
    """<<Value Object>> A class name a file imports, re-exports, or reaches as `module.Class`, with the module it names
    it from: a path from the source root without its extension (`harness/graph/graph`), or a package's name as the
    import spells it when the import leaves the source root (`typing`, `react`, a language adapter's `@cdd/x`). A star import's name is
    ``STAR``. Saved with the graph as ``[source, name]``."""

    source: str
    name: str

    def files(self) -> List[str]:
        """The files the module it names it from may be, from the source root; for a language adapter, the Python
        module the adapter is generated from."""
        if self._through_adapter():
            return imported_files(self.source.removeprefix(LANGUAGE_ADAPTER_ALIAS).replace("-", "_"))
        return imported_files(self.source)

    def names(self) -> List[str]:
        """The class names it may name: its own, and for a language adapter's `{Class}Data`, the class it sends."""
        if self._through_adapter() and self.name.endswith(_ADAPTER_DATA_SUFFIX) and self.name != _ADAPTER_DATA_SUFFIX:
            return [self.name, self.name.removesuffix(_ADAPTER_DATA_SUFFIX)]
        return [self.name]

    def _through_adapter(self) -> bool:
        return self.source.startswith(LANGUAGE_ADAPTER_ALIAS)


class ScriptImports:
    """<<Value Object>> The imports of one source file's text, in Python or a script language."""

    def __init__(self, source_text: str) -> None:
        self._text = source_text

    def class_references(self, file: Path, root: Path) -> List[ClassReference]:
        """Each class name the file at file imports or re-exports, or reaches as `module.Class` through a module it
        imports, with the module it names it from, in order, each once."""
        package = file.parent.relative_to(root).as_posix()
        found = PythonImports(self._text, package) if file.suffix == ".py" else ScriptImportClauses(self._text, package)
        return list(dict.fromkeys(found.references()))

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


class QualifiedNames:
    """The local names a file binds to modules it imports, and the classes it reaches through them as `local.Class`."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._modules: dict[str, str] = {}

    def bind(self, local: str, module: str) -> None:
        """The file reaches module through local, such as `g` for `import harness.graph.graph as g`."""
        self._modules[local] = module

    def references(self) -> List[ClassReference]:
        found: List[ClassReference] = []
        for local, module in self._modules.items():
            pattern = re.compile(rf"(?<![\w$.]){re.escape(local)}\.([A-Z]\w*)\b")
            found.extend(ClassReference(module, name) for name in pattern.findall(self._text))
        return found


class PythonImports:
    """<<Value Object>> The class names a Python file's text imports, with the module each comes from: `from a.b import
    C`, relative ones against the file's package, and the classes it reaches as `g.C` through `import a.b as g`,
    `import a.b`, or `from a import b`. Imports under `if TYPE_CHECKING:` name a class too."""

    def __init__(self, text: str, package: str) -> None:
        self._text = text
        self._package = [] if package in ("", ".") else package.split("/")
        self._qualified = QualifiedNames(text)

    def references(self) -> List[ClassReference]:
        found: List[ClassReference] = []
        for module, names in _PY_FROM_IMPORT.findall(self._text):
            found.extend(self._from_import(self._module_path(module), names))
        for listed in _PY_IMPORT.findall(self._text):
            self._bind_imports(listed)
        return found + self._qualified.references()

    def _from_import(self, module: str, names: str) -> List[ClassReference]:
        """The names one `from module import names` brings in. A lower-case name may be a module of its package, which
        the file reaches classes through."""
        found: List[ClassReference] = []
        for item in _PY_COMMENT.sub("", names).strip().strip("()\\").split(","):
            parts = _ALIAS.split(item.strip())
            name = parts[0].strip()
            if name == STAR or _NAME.fullmatch(name):
                found.append(ClassReference(module, name))
            if _NAME.fullmatch(name) and not name[0].isupper():
                self._qualified.bind(parts[-1].strip(), f"{module}/{name}")
        return found

    def _bind_imports(self, listed: str) -> None:
        for item in listed.split(","):
            parts = _ALIAS.split(item.strip())
            self._qualified.bind(parts[-1].strip(), parts[0].strip().replace(".", "/"))

    def _module_path(self, module: str) -> str:
        """The path from the source root a `from` import's module names: `a/b` for `a.b`, and a relative one against the
        file's package."""
        level = len(module) - len(module.lstrip("."))
        named = [part for part in module[level:].split(".") if part]
        base = self._package[: len(self._package) - level + 1] if level else []
        return "/".join(base + named)


class ScriptImportClauses:
    """<<Value Object>> The class names a script file's text imports or re-exports, with the module each comes from:
    `import D, { A, B as C } from`, `import * as ns from` with `ns.X`, `export { A } from`, and `export * from`. A
    relative module is a path from the source root; any other keeps its spelling."""

    def __init__(self, text: str, package: str) -> None:
        self._text = text
        self._package = "" if package == "." else package
        self._qualified = QualifiedNames(text)

    def references(self) -> List[ClassReference]:
        found: List[ClassReference] = []
        for keyword, clause, specifier in _JS_FROM.findall(self._text):
            shape = _JS_CLAUSE.fullmatch(clause.strip())
            if shape is not None:
                found.extend(self._clause(keyword, shape, self._module(specifier)))
        return found + self._qualified.references()

    def _clause(self, keyword: str, shape: re.Match, module: str) -> List[ClassReference]:
        default, braced, namespace = shape.groups()
        names = [default] if default and keyword == "import" else []
        names.extend(_ALIAS.split(item.strip().removeprefix("type "))[0].strip() for item in (braced or "").split(","))
        if namespace:
            self._qualified.bind(namespace, module)
        elif "*" in shape.group(0) and keyword == "export":
            names.append(STAR)
        return [ClassReference(module, name) for name in names if name == STAR or _NAME.fullmatch(name or "")]

    def _module(self, specifier: str) -> str:
        if not specifier.startswith("."):
            return specifier
        return posixpath.normpath(posixpath.join(self._package, specifier))
