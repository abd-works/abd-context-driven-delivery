"""Every name the repository's code calls or imports still exists.

A rename finished in one place and not another, or a merge that drops an import, leaves code that still parses and
fails only when the line runs: a renamed member still called after a merge, ``contextmanager`` lost from a file's
imports, a TypeScript getter renamed while the chat bar still read the old name. This check reads the whole
repository and names each such place, so a spec can hold the repository to having none.

Python is checked three ways:

- **Undefined names**: a name a file uses that nothing in it defines or imports (ruff's F821 and F822, the checks
  pyflakes makes).
- **Imports of the repository's own modules**: ``from a.b import c`` where ``a.b`` is a module of this repository and
  it neither defines ``c`` nor holds a module ``c``.
- **Members**: ``x.name`` where no code reachable from the repository defines ``name`` at all: no function, class,
  method, field, assigned attribute or keyword of that name in the repository, the standard library or the packages
  the repository imports. A renamed member still called under its old name, anywhere, is such a name.

TypeScript is checked with the TypeScript compiler over each project that has a ``tsconfig.json`` and each Claude Code
mod (a folder holding ``cdd-mod.json`` or ``hooks/hooks.json`` with a ``types`` folder), reporting the compiler's
errors that say a name does not exist: a property, an export, a module or a name it cannot find.

Run it: ``python scripts/names_exist/names_exist.py`` lists every missing name and exits 1 when there is one.
"""
from __future__ import annotations

import ast
import builtins
import importlib
import importlib.metadata
import importlib.util
import json
import os
import re
import subprocess
import sys
import sysconfig
import tempfile
import warnings
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import cache, cached_property
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
# The folders scripts/test.ps1 puts on the path, so a module is named here as the specs import it.
IMPORT_ROOTS = (".", "cdd_guidance/actions", "tools", "cdd_guidance/practices", "cdd_guidance/patterns")
# Code kept only for the record (.retired), session work (.sessions), templates whose text holds placeholders such as
# {domain}, and the sample projects the practices read and write (_examples, fixtures, .context), which are partial or
# faulty on purpose, are not code that runs.
LEFT_OUT = re.compile(r"(^|/)(\.retired|\.sessions|node_modules|templates|_examples|fixtures|\.context)(/|$)|\{")
# The names Mamba gives a spec's body (its blocks become methods of a class it writes) and a story test's steps.
SPEC_BUILTINS = ("self", "description", "describe", "context", "it", "before", "after", "_it", "_context", "_description", "fit", "fcontext", "fdescription")
_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
# A string that is only identifiers, as namedtuple("Point", "x y") and __slots__ spell fields; a sentence is not.
_IDENTIFIERS = re.compile(r"[A-Za-z_][A-Za-z0-9_]*([\s,]+[A-Za-z_][A-Za-z0-9_]*)*")
_DOTTED = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*")
# Receivers whose members Python finds only at run time: a Windows library loaded through ctypes, which answers any
# function it exports, and the POSIX-only modules, which are not there to read on Windows.
_RUN_TIME_RECEIVERS = re.compile(r"windll|WinDLL|kernel32|iphlpapi|psapi|ntdll|user32|advapi32|\b_?kernel\b|\bfcntl\b|\btermios\b|\bresource\b")
# The TypeScript compiler's errors that say a name does not exist.
_TS_NAME_ERRORS = {
    "TS2304": "cannot find name",
    "TS2305": "module has no exported member",
    "TS2307": "cannot find module",
    "TS2339": "property does not exist",
    "TS2551": "property does not exist",
    "TS2552": "cannot find name",
    "TS2614": "module has no exported member",
    "TS2694": "namespace has no exported member",
    "TS2724": "module has no exported member",
}
_TS_ERROR = re.compile(r"^(?P<file>[^(\r\n]+)\((?P<line>\d+),\d+\): error (?P<code>TS\d+): (?P<text>.*)$")
_TS_PROPERTY_ON = re.compile(r"does not exist on type '(?P<type>.*)'")


@dataclass(frozen=True, order=True)
class MissingName:
    """One place the code names something that does not exist: the file from the repository's root, its line, the
    name, and what kind of name is missing."""

    file: str
    line: int
    name: str
    kind: str

    def __str__(self) -> str:
        return f"{self.file}:{self.line}: {self.kind}: {self.name}"


def _defined_in(tree: ast.AST) -> set[str]:
    """Every name one file defines anywhere in it: functions, classes, assigned names and attributes, keyword
    arguments, parameters, imported names, and each string that is a single identifier (getattr, setattr, namedtuple
    fields, __slots__). It walks the tree without recursion, since some library files nest deeper than Python's stack."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and not isinstance(node.ctx, ast.Load):
            names.add(node.id)
        elif isinstance(node, ast.Attribute) and not isinstance(node.ctx, ast.Load):
            names.add(node.attr)
            # A member configured where it is set up, as ctypes does (kernel.CreateJobObjectW.restype = ...), exists.
            if isinstance(node.value, ast.Attribute):
                names.add(node.value.attr)
        elif isinstance(node, ast.arg):
            names.add(node.arg)
        elif isinstance(node, ast.keyword) and node.arg:
            names.add(node.arg)
        elif isinstance(node, ast.alias):
            names.add((node.asname or node.name).split(".")[0])
            names.update(node.name.split("."))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value.startswith("--"):
            # An argparse option, which the parsed arguments hold under its name with dashes made underscores.
            names.add(node.value.lstrip("-").replace("-", "_"))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str) and _IDENTIFIERS.fullmatch(node.value.strip()):
            names.update(re.split(r"[\s,]+", node.value.strip()))
    return names


def _names_defined_in_file(path: Path) -> set[str]:
    """Every name one file defines, or none when it does not parse: read in a worker process, since reading the
    standard library and the imported packages one file after another takes over a minute."""
    tree = _parsed(path)
    return _defined_in(tree) if tree is not None else set()


@cache
def _distributions_by_module() -> dict[str, list[str]]:
    """Each top-level module's installed distributions, read once: reading them takes nearly a second."""
    return importlib.metadata.packages_distributions()


def _parsed(path: Path) -> ast.Module | None:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", SyntaxWarning)
            return ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except (SyntaxError, ValueError, RecursionError):
        return None


class _ModuleIndex:
    """The repository's own Python modules by their dotted name under each import root, and what each defines at its
    top level."""

    def __init__(self, repo: Path) -> None:
        self._repo = repo
        self._roots = [repo / root for root in IMPORT_ROOTS]
        self._paths: dict[str, Path | None] = {}
        self._top_levels: dict[Path, _TopLevel | None] = {}

    def is_ours(self, dotted: str) -> bool:
        """Whether dotted names a module or package of the repository under one of its import roots."""
        return self.path_of(dotted) is not None

    def first_part_is_ours(self, dotted: str) -> bool:
        first = dotted.split(".")[0]
        return any((root / first).is_dir() or (root / f"{first}.py").is_file() for root in self._roots)

    def path_of(self, dotted: str) -> Path | None:
        """The file (module.py, or a package's __init__.py) or folder (a namespace package) dotted names, looked up
        once for each name: the files are imported from thousands of times."""
        if dotted not in self._paths:
            self._paths[dotted] = self._found_path(dotted)
        return self._paths[dotted]

    def _found_path(self, dotted: str) -> Path | None:
        parts = dotted.split(".")
        for root in self._roots:
            base = root.joinpath(*parts)
            if base.with_suffix(".py").is_file():
                return base.with_suffix(".py")
            if base.is_dir():
                return base / "__init__.py" if (base / "__init__.py").is_file() else base
        return None

    def offers(self, dotted: str, name: str) -> bool:
        """Whether ``from dotted import name`` finds name: a module of that name inside the package, or a name the
        module defines at its top level; a module that defines __getattr__ or imports * offers any name."""
        if self.is_ours(f"{dotted}.{name}"):
            return True
        path = self.path_of(dotted)
        if path is None or path.is_dir():
            return False
        top_level = self._top_level(path)
        return top_level is None or name in top_level

    def _top_level(self, path: Path) -> _TopLevel | None:
        """What the module at path defines at its top level, read once; None when it does not parse."""
        if path not in self._top_levels:
            tree = _parsed(path)
            self._top_levels[path] = _TopLevel(tree) if tree is not None else None
        return self._top_levels[path]


class _TopLevel:
    """The names a module defines at its top level, looking into its if, try and with blocks."""

    def __init__(self, tree: ast.Module) -> None:
        self.names: set[str] = set()
        self._read(tree.body)

    def _read(self, body: list[ast.stmt]) -> None:
        for statement in body:
            if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                self.names.add(statement.name)
                if statement.name == "__getattr__":
                    self.names.add("*")
            elif isinstance(statement, ast.TypeAlias):
                self.names.add(statement.name.id)
            elif isinstance(statement, (ast.Import, ast.ImportFrom)):
                for alias in statement.names:
                    self.names.add("*" if alias.name == "*" else (alias.asname or alias.name).split(".")[0])
            elif isinstance(statement, (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For, ast.AsyncFor, ast.With, ast.AsyncWith)):
                for target in ast.walk(statement):
                    if isinstance(target, ast.Name) and not isinstance(target.ctx, ast.Load):
                        self.names.add(target.id)
            for inner in ("body", "orelse", "finalbody", "handlers"):
                block = getattr(statement, inner, None)
                if isinstance(block, list) and not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    self._read([part for part in block if isinstance(part, ast.stmt)] + [stmt for handler in block if isinstance(handler, ast.ExceptHandler) for stmt in handler.body])

    def __contains__(self, name: str) -> bool:
        return name in self.names or "*" in self.names


class PythonNames:
    """The names the repository's Python code uses that do not exist."""

    def __init__(self, repo: Path = REPO, files: list[str] | None = None, reads_outside: bool = True) -> None:
        """repo is the checkout read; files, when given, are the only files checked and read; reads_outside says whether
        the names the standard library and the imported packages define are read from their source, which takes about
        a minute, or only those Python reports for the built-in types."""
        self._repo = repo
        self._files = files
        self._reads_outside = reads_outside
        self._modules = _ModuleIndex(repo)

    @cached_property
    def files(self) -> list[str]:
        """The repository's Python files, from its root, that are code that runs."""
        if self._files is not None:
            return self._files
        listed = subprocess.run(["git", "ls-files", "-z", "*.py"], cwd=self._repo, capture_output=True, text=True, check=True).stdout
        return sorted(name for name in listed.split("\0") if name and not LEFT_OUT.search(name) and (self._repo / name).is_file())

    @cached_property
    def _trees(self) -> dict[str, ast.Module]:
        return {name: tree for name in self.files if (tree := _parsed(self._repo / name)) is not None}

    @cached_property
    def _every_tree(self) -> list[ast.Module]:
        """Every Python file the repository tracks, the sample projects too: the specs call what those define."""
        if self._files is not None:
            return list(self._trees.values())
        listed = subprocess.run(["git", "ls-files", "-z", "*.py"], cwd=self._repo, capture_output=True, text=True, check=True).stdout
        trees = self._trees
        return [
            tree
            for name in listed.split("\0")
            if name and (tree := trees.get(name) or (_parsed(self._repo / name) if (self._repo / name).is_file() else None)) is not None
        ]

    def missing(self) -> list[MissingName]:
        return sorted({*self.undefined_names(), *self.missing_imports(), *self.missing_members()})

    def undefined_names(self) -> list[MissingName]:
        """Names a file uses that nothing in it defines or imports, as ruff's F821 and F822 report them."""
        specs = [file for file in self.files if self._is_a_spec(file)]
        others = [file for file in self.files if not self._is_a_spec(file)]
        return [*self._ruff_undefined(others, ()), *(found for found in self._ruff_undefined(specs, SPEC_BUILTINS) if not self._defined_later(found))]

    def _defined_later(self, found: MissingName) -> bool:
        """Whether a spec defines the name at its top level below where it uses it: Mamba runs a spec's blocks only once
        the whole module has run, so a helper written at the end of the file is defined by then."""
        tree = self._trees.get(found.file)
        return tree is not None and found.name in _TopLevel(tree).names

    def _is_a_spec(self, file: str) -> bool:
        """Whether Mamba runs the file: a spec, or a file that imports mamba."""
        tree = self._trees.get(file)
        imports_mamba = tree is not None and any(
            isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "mamba" for node in ast.walk(tree)
        )
        return file.endswith(("_spec.py", ".test.py")) or imports_mamba

    def _ruff_undefined(self, files: list[str], builtins_given: tuple[str, ...]) -> list[MissingName]:
        found: list[MissingName] = []
        given = ["--config", f"builtins = {json.dumps(list(builtins_given))}"] if builtins_given else ["--isolated"]
        for start in range(0, len(files), 400):
            batch = files[start:start + 400]
            run = subprocess.run(
                [sys.executable, "-m", "ruff", "check", *given, "--no-cache", "--select", "F821,F822", "--output-format", "json", *batch],
                cwd=self._repo, capture_output=True, text=True, encoding="utf-8",
            )
            if run.returncode not in (0, 1):
                raise RuntimeError(f"ruff could not check the files: {run.stderr.strip()}")
            for finding in json.loads(run.stdout or "[]"):
                name = re.search(r"`([^`]+)`", finding["message"])
                file = Path(finding["filename"]).resolve().relative_to(self._repo.resolve()).as_posix()
                found.append(MissingName(file, finding["location"]["row"], name.group(1) if name else finding["message"], "undefined name"))
        return found

    def missing_imports(self) -> list[MissingName]:
        """``from a.b import c`` of the repository's own module a.b, which neither defines c nor holds a module c; and
        ``import a.b`` or ``from a.b import ...`` of a module the repository's package a does not hold."""
        found: list[MissingName] = []
        for file, tree in self._trees.items():
            package = self._package_of(file)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    found.extend(self._from_import(file, package, node))
                elif isinstance(node, ast.Import):
                    found.extend(
                        MissingName(file, node.lineno, alias.name, "module the repository does not hold")
                        for alias in node.names
                        if self._modules.first_part_is_ours(alias.name) and not self._modules.is_ours(alias.name) and not self._is_external(alias.name)
                    )
        return found

    def _from_import(self, file: str, package: str, node: ast.ImportFrom) -> list[MissingName]:
        if node.level:
            parts = package.split(".") if package else []
            base = parts[: len(parts) - (node.level - 1)] if node.level > 1 else parts
            dotted = ".".join([*base, *([node.module] if node.module else [])])
        else:
            dotted = node.module or ""
        if not dotted or not self._modules.first_part_is_ours(dotted) or self._is_external(dotted):
            return []
        if not self._modules.is_ours(dotted):
            return [MissingName(file, node.lineno, dotted, "module the repository does not hold")]
        return [
            MissingName(file, node.lineno, f"{dotted}.{alias.name}", "name its module does not define")
            for alias in node.names
            if alias.name != "*" and not self._modules.offers(dotted, alias.name)
        ]

    def _package_of(self, file: str) -> str:
        """The dotted package a file is in, from the deepest import root that holds it."""
        path = (self._repo / file).resolve()
        for root in sorted((Path(self._repo / root).resolve() for root in IMPORT_ROOTS), key=lambda folder: len(folder.parts), reverse=True):
            if root in path.parents:
                return ".".join(path.parent.relative_to(root).parts)
        return ""

    def _is_external(self, dotted: str) -> bool:
        """Whether an installed package, not the repository, answers this name: a repository folder that shares its
        first part with one, such as harness/mcp beside the mcp SDK, is imported as harness.mcp."""
        first = dotted.split(".")[0]
        try:
            spec = importlib.util.find_spec(first)
        except (ImportError, ValueError):
            return False
        origin = Path(spec.origin).resolve() if spec and spec.origin else None
        return origin is not None and self._repo.resolve() not in origin.parents

    def missing_members(self) -> list[MissingName]:
        """``x.name`` where nothing the code can reach defines name."""
        known = self._known_names
        found: list[MissingName] = []
        for file, tree in self._trees.items():
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Load) and node.attr not in known and not _RUN_TIME_RECEIVERS.search(ast.unparse(node.value)):
                    if not self._missing_on_purpose(file, node.lineno):
                        found.append(MissingName(file, node.lineno, node.attr, "member nothing defines"))
        return found

    def _missing_on_purpose(self, file: str, line: int) -> bool:
        """Whether the line says it names a missing member on purpose (``# noqa: names-exist``), as a spec of what
        happens when one is missing does."""
        return "noqa: names-exist" in self._lines_of(file)[line - 1]

    def _lines_of(self, file: str) -> list[str]:
        return (self._repo / file).read_text(encoding="utf-8", errors="replace").splitlines()

    @cached_property
    def _known_names(self) -> set[str]:
        """Every name defined in the repository, the standard library and the packages it imports, and every
        attribute of the built-in types and of what those packages hold."""
        names: set[str] = set()
        for tree in self._every_tree:
            names |= _defined_in(tree)
        for defined in self._names_outside():
            names |= defined
        names |= _LiveNames(self._imported if self._reads_outside else set()).names
        return names

    def _names_outside(self) -> list[set[str]]:
        """The names each file of the standard library and the imported packages defines, read in worker processes."""
        if not self._reads_outside:
            return []
        with ProcessPoolExecutor(max_workers=min(16, os.cpu_count() or 1)) as workers:
            return list(workers.map(_names_defined_in_file, self._outside_sources(), chunksize=64))

    @cached_property
    def _imported(self) -> set[str]:
        """The packages outside the repository its code imports, read once."""
        return self._imported_packages()

    def _imported_packages(self) -> set[str]:
        imported: set[str] = set()
        for tree in self._trees.values():
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                    imported.add(node.module)
                elif self._imports_by_name(node):
                    imported.add(node.args[0].value)
        return {name for name in imported if not self._modules.first_part_is_ours(name) or self._is_external(name)}

    @staticmethod
    def _imports_by_name(node: ast.AST) -> bool:
        """Whether node imports a module named by a string, as ``importlib.import_module("lizard")`` does, so a
        package the code loads only when it needs it is read too."""
        if not isinstance(node, ast.Call) or not node.args or not isinstance(node.args[0], ast.Constant):
            return False
        called = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
        value = node.args[0].value
        return "import" in called and isinstance(value, str) and _DOTTED.fullmatch(value) is not None

    @staticmethod
    def _distribution_files(first: str) -> list[Path]:
        """The Python files of the installed distribution that provides the top-level module first, so a package
        split over several top-level folders, as lizard is (lizard, lizard_ext, lizard_languages), is read whole."""
        found: list[Path] = []
        for distribution in _distributions_by_module().get(first, []):
            for file in importlib.metadata.files(distribution) or []:
                if file.suffix == ".py":
                    found.append(Path(file.locate()))
        return found

    def _outside_sources(self) -> list[Path]:
        """The Python source of the standard library and of each installed package the repository imports."""
        folders = {Path(sysconfig.get_paths()["stdlib"])}
        for first in {name.split(".")[0] for name in self._imported}:
            try:
                spec = importlib.util.find_spec(first)
            except (ImportError, ValueError):
                continue
            folders.update(self._distribution_files(first))
            if spec and spec.submodule_search_locations:
                folders.update(Path(location) for location in spec.submodule_search_locations)
            elif spec and spec.origin and spec.origin.endswith(".py"):
                folders.add(Path(spec.origin))
        sources: list[Path] = []
        for folder in folders:
            if folder.is_file():
                sources.append(folder)
                continue
            for path in folder.rglob("*.py"):
                if "site-packages" in path.parts and folder.name != path.parts[len(folder.parts) - 1] and folder.name == "Lib":
                    continue
                sources.append(path)
        return sources


class _LiveNames:
    """The attributes Python itself reports for the built-in types and for each module the repository imports and
    the classes in it, for the parts written in C that have no source to read."""

    def __init__(self, modules: set[str]) -> None:
        self.names: set[str] = set(dir(builtins))
        seen: set[int] = set()
        for value in vars(builtins).values():
            self._take(value, seen)
        for name in sorted(modules):
            try:
                module = importlib.import_module(name)
            except Exception:  # A package that fails to import here still has its source read.
                continue
            self._take(module, seen)
            for value in list(vars(module).values()):
                self._take(value, seen)

    def _take(self, value: object, seen: set[int]) -> None:
        if id(value) in seen:
            return
        seen.add(id(value))
        try:
            self.names.update(dir(value))
        except Exception:  # An object whose dir fails holds no names to take.
            return
        if isinstance(value, type):
            for base in value.__mro__:
                self.names.update(vars(base))


class TypeScriptNames:
    """The names the repository's TypeScript uses that the TypeScript compiler cannot find."""

    def __init__(self, repo: Path = REPO) -> None:
        self._repo = repo

    @cached_property
    def projects(self) -> list[Path]:
        """Each folder with a tsconfig.json and its own installed compiler."""
        listed = subprocess.run(["git", "ls-files", "-z", "*tsconfig.json"], cwd=self._repo, capture_output=True, text=True, check=True).stdout
        folders = [(self._repo / name).parent for name in listed.split("\0") if name and not LEFT_OUT.search(name)]
        return sorted(folder for folder in folders if (folder / "node_modules" / "typescript").is_dir())

    @cached_property
    def mods(self) -> list[Path]:
        """Each Claude Code mod of the repository: a folder with hooks/hooks.json and a types folder."""
        listed = subprocess.run(["git", "ls-files", "-z", "*hooks/hooks.json"], cwd=self._repo, capture_output=True, text=True, check=True).stdout
        folders = [(self._repo / name).parent.parent for name in listed.split("\0") if name and not LEFT_OUT.search(name)]
        return sorted(folder for folder in folders if (folder / "types").is_dir())

    def missing(self) -> list[MissingName]:
        found: list[MissingName] = []
        for project in self.projects:
            found.extend(self._compiled(project, ["-p", str(project / "tsconfig.json")], project))
        claude_code_types = self._claude_code_types()
        compiler = self._compiler()
        for mod in self.mods:
            if claude_code_types is None or compiler is None:
                found.append(MissingName(mod.relative_to(self._repo).as_posix(), 0, "claude-code types", "the mod cannot be checked: no installed copy of a Claude Code mod holds the app's types"))
                continue
            found.extend(self._compiled_mod(mod, claude_code_types))
        return sorted(set(found))

    def _compiler(self) -> Path | None:
        return next((project / "node_modules" / "typescript" / "bin" / "tsc" for project in self.projects), None)

    def _compiled(self, project: Path, arguments: list[str], folder: Path, compiler: Path | None = None) -> list[MissingName]:
        tsc = compiler or project / "node_modules" / "typescript" / "bin" / "tsc"
        run = subprocess.run(["node", str(tsc), "--noEmit", "--pretty", "false", *arguments], cwd=folder, capture_output=True, text=True, encoding="utf-8")
        found: list[MissingName] = []
        for line in run.stdout.splitlines():
            error = _TS_ERROR.match(line.strip())
            if error is None or error.group("code") not in _TS_NAME_ERRORS or not self._is_a_missing_name(error):
                continue
            path = (folder / error.group("file")).resolve()
            try:
                file = path.relative_to(self._repo.resolve()).as_posix()
            except ValueError:
                file = path.as_posix()
            found.append(MissingName(file, int(error.group("line")), error.group("text"), _TS_NAME_ERRORS[error.group("code")]))
        return found

    @staticmethod
    def _is_a_missing_name(error: re.Match) -> bool:
        """Whether the compiler says a name is missing from something it knows: a property on a type it can name, not
        on a type it could not tell (never, {}, any) or a union it could not narrow; and not a node: module, which the
        runtime gives the mods though their types leave Node out."""
        text = error.group("text")
        if "'node:" in text:
            return False
        typed = _TS_PROPERTY_ON.search(text)
        if typed is None:
            return True
        shown = typed.group("type")
        return shown not in ("never", "{}", "any", "unknown", "object") and " | " not in shown

    def _claude_code_types(self) -> Path | None:
        """The Claude Code types an installed mod copy holds (``~/.claude/dev-mods/*/*/.claude-plugin/types``), the
        newest: the desktop app writes them when it loads a mod, and the repository holds none of its own."""
        installed = sorted((Path.home() / ".claude" / "dev-mods").glob("*/*/.claude-plugin/types/claude-code"), key=lambda path: path.stat().st_mtime, reverse=True)
        return installed[0].parent if installed else None

    def _compiled_mod(self, mod: Path, types: Path) -> list[MissingName]:
        adapters = self._repo / ".claude" / "language-adapters" / "typescript"
        config = {
            "compilerOptions": {
                "target": "es2023", "lib": ["es2023", "dom"], "module": "esnext", "moduleResolution": "bundler",
                "strict": True, "noEmit": True, "skipLibCheck": True, "jsx": "react", "jsxFactory": "h", "jsxFragmentFactory": "Fragment",
                "typeRoots": [types.as_posix()], "types": ["claude-code", "claude-code-tools", "claude-code-mcp"],
                "baseUrl": self._repo.as_posix(), "paths": {"@cdd/*": [f"{adapters.as_posix()}/*"]},
            },
            "include": [(mod / "hooks").as_posix(), (mod / "types").as_posix()],
        }
        with tempfile.TemporaryDirectory(prefix="names-exist-") as folder:
            written = Path(folder) / "tsconfig.json"
            written.write_text(json.dumps(config), encoding="utf-8")
            return [found for found in self._compiled(mod, ["-p", str(written)], self._repo, self._compiler()) if not found.file.startswith("/") and ":" not in found.file[:3]]


class RepositoryNames:
    """Every name the repository's Python and TypeScript use that does not exist."""

    def __init__(self, repo: Path = REPO) -> None:
        self.python = PythonNames(repo)
        self.typescript = TypeScriptNames(repo)

    def missing(self) -> list[MissingName]:
        return [*self.python.missing(), *self.typescript.missing()]


if __name__ == "__main__":
    missing = RepositoryNames().missing()
    for name in missing:
        print(name)
    print(f"{len(missing)} missing names")
    sys.exit(1 if missing else 0)
