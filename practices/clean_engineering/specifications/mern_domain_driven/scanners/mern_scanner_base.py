"""Base scanners for MERN architecture compliance checks - ported from the
old-world abd-skills MERN domain-first specification onto the shared
scan.Scanner / ScannerCollection contract used by every other
context tool (clean_engineering, stories, ...).

MERNScanner keeps the same helper methods and names as the old world's
mern_scanner.py, but every helper takes ``root: Path`` directly (Scanner.scan
already resolves and passes root) instead of a ``context: Dict`` with a
``project_root`` key - the only real shape change concrete scanners need.

TypeScriptScanner adds the same tree-sitter TypeScript AST extraction the old
ts_scanner_base.py provided (classes, interfaces, imports, calls), unchanged,
so every AST-based concrete scanner ports with no logic changes at all.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from scan.scanner import Scanner
from scan.violation import Violation

try:
    import tree_sitter as _ts
    import tree_sitter_typescript as _tsts

    _TS_LANG = _ts.Language(_tsts.language_typescript())
    _TSX_LANG = _ts.Language(_tsts.language_tsx())
    _TS_PARSER = _ts.Parser(_TS_LANG)
    _TSX_PARSER = _ts.Parser(_TSX_LANG)
    _TREE_SITTER_AVAILABLE = True
except Exception:  # pragma: no cover - exercised only when the optional dep is absent
    _TREE_SITTER_AVAILABLE = False
    _TS_LANG = _TSX_LANG = _TS_PARSER = _TSX_PARSER = None


class MERNScanner(Scanner):
    """Base class for domain-first MERN architecture scanners.

    Concrete scanners override ``scan(self, root, files)`` (project-wide
    checks - package structure, cross-file naming) or ``scan_file`` (one file
    at a time, via the inherited ``Scanner.scan`` loop).
    """

    RULE: str = ""

    def v(
        self,
        message: str,
        location: str = "",
        line: int = 0,
        severity: str = "error",
    ) -> Violation:
        """Old-world shorthand for ``self.violation(...)`` - kept so ported
        scanner bodies need no call-site changes beyond the base class."""
        return self.violation(message, location=location, line=line, severity=severity)

    def _find_domain_packages(self, project_root: Path) -> List[Path]:
        """Domain dirs under packages/ — either top-level or nested inside a
        feature package (e.g. ``packages/wires/recipients/``). A domain dir
        has the three-file layout (``<domain>.ts``, ``<domain>-server.ts``,
        ``<domain>-client.tsx``) or legacy ``shared/`` / ``client/`` /
        ``server/`` folders. Excludes composition roots."""
        packages_dir = project_root / "packages"
        if not packages_dir.exists():
            return []

        excluded = {"node_modules"}
        domain_packages: List[Path] = []

        def consider(path: Path) -> None:
            if self._is_domain_dir(path) and path not in domain_packages:
                domain_packages.append(path)

        for child in packages_dir.iterdir():
            if not child.is_dir():
                continue
            if child.name in excluded or child.name.startswith("."):
                continue
            consider(child)
            # Feature packages nest domain modules one level down
            # (packages/wires/recipients/).
            if self._domain_core_file(child) is None:
                for nested in child.iterdir():
                    if not nested.is_dir() or nested.name.startswith("."):
                        continue
                    if nested.name in {"node_modules", "dist", "build"}:
                        continue
                    consider(nested)
        return domain_packages

    def _is_domain_dir(self, path: Path) -> bool:
        if self._domain_core_file(path) is not None and (
            self._server_file(path) is not None or self._client_file(path) is not None
        ):
            return True
        return any((path / tier).is_dir() for tier in ("shared", "client", "server"))

    def _domain_core_file(self, domain_path: Path) -> Path | None:
        """``<domain>.ts`` — framework-free domain core (was shared/)."""
        candidates = [
            domain_path / f"{domain_path.name}.ts",
            domain_path / f"{domain_path.name.rstrip('s')}.ts",
        ]
        for path in candidates:
            if path.is_file():
                return path
        for path in sorted(domain_path.glob("*.ts")):
            name = path.name
            if name in {"index.ts", "app.ts", "serve.ts", "main.ts"}:
                continue
            if name.endswith("-server.ts"):
                continue
            if name.endswith(".test.ts") or name.endswith(".spec.ts"):
                continue
            if name.endswith("-client.ts"):
                continue
            return path
        return None

    def _server_file(self, domain_path: Path) -> Path | None:
        """``<domain>-server.ts`` (not feature-package ``serve.ts`` / ``app.ts``)."""
        singular = domain_path.name.rstrip("s")
        for name in (
            f"{singular}-server.ts",
            f"{domain_path.name}-server.ts",
        ):
            path = domain_path / name
            if path.is_file():
                return path
        matches = sorted(domain_path.glob("*-server.ts"))
        return matches[0] if matches else None

    def _client_file(self, domain_path: Path) -> Path | None:
        """``<domain>-client.tsx`` (or legacy ``client.tsx``)."""
        singular = domain_path.name.rstrip("s")
        for name in (
            f"{singular}-client.tsx",
            f"{singular}-client.ts",
            f"{domain_path.name}-client.tsx",
            f"{domain_path.name}-client.ts",
            "client.tsx",
            "client.ts",
        ):
            path = domain_path / name
            if path.is_file():
                return path
        matches = sorted(domain_path.glob("*-client.tsx")) + sorted(
            domain_path.glob("*-client.ts")
        )
        return matches[0] if matches else None

    def _find_tier_files(self, domain_path: Path, tier: str, pattern: str = "*.ts") -> List[Path]:
        """Files for one tier. Prefers the three-file layout; falls back to
        legacy ``<tier>/`` directories."""
        if tier in ("shared", "domain", "core"):
            core = self._domain_core_file(domain_path)
            return [core] if core is not None else []
        if tier == "server":
            server = self._server_file(domain_path)
            if server is not None:
                return [server]
        if tier == "client":
            client = self._client_file(domain_path)
            if client is not None:
                return [client]
        tier_dir = domain_path / tier
        if not tier_dir.exists():
            return []
        return list(tier_dir.glob(pattern))

    def _find_test_folders(self, project_root: Path) -> List[Path]:
        """Lowest-level sub-epic test folders under tests/."""
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            return []

        sub_epic_folders = []
        for epic_dir in tests_dir.iterdir():
            if not epic_dir.is_dir() or epic_dir.name.startswith("."):
                continue
            for sub_epic_dir in epic_dir.rglob("*"):
                if not sub_epic_dir.is_dir():
                    continue
                has_test_files = any(
                    f.name.endswith((".test.ts", ".test.tsx", ".spec.ts"))
                    for f in sub_epic_dir.iterdir()
                    if f.is_file()
                )
                if has_test_files:
                    sub_epic_folders.append(sub_epic_dir)
        return sub_epic_folders

    def _read_file_content(self, file_path: Path) -> Optional[str]:
        try:
            return file_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None


# ---------------------------------------------------------------------------
# Data classes - unchanged from the old ts_scanner_base.py
# ---------------------------------------------------------------------------

@dataclass
class MethodInfo:
    name: str
    is_async: bool
    is_static: bool
    is_abstract: bool
    modifiers: List[str]
    return_type: Optional[str]
    param_count: int
    start_line: int
    end_line: int


@dataclass
class PropertyInfo:
    name: str
    type_annotation: Optional[str]
    modifiers: List[str]
    start_line: int


@dataclass
class ClassInfo:
    name: str
    implements: List[str]
    extends: Optional[str]
    methods: List[MethodInfo]
    properties: List[PropertyInfo]
    is_abstract: bool
    is_exported: bool
    start_line: int
    end_line: int


@dataclass
class InterfaceInfo:
    name: str
    method_names: List[str]
    property_names: List[str]
    is_exported: bool
    start_line: int


@dataclass
class ImportInfo:
    source: str
    names: List[str]
    default_name: Optional[str]
    is_type_only: bool
    start_line: int


@dataclass
class CallInfo:
    callee: str
    args_text: str
    start_line: int


def _txt(node) -> str:
    if node is None:
        return ""
    b = node.text
    return b.decode("utf-8", errors="replace") if isinstance(b, bytes) else str(b or "")


def _find_all(node, *types: str) -> list:
    results: list = []
    if node.type in types:
        results.append(node)
    for child in node.children:
        results.extend(_find_all(child, *types))
    return results


_MODIFIER_TYPES = frozenset(
    {"public", "private", "protected", "abstract", "static", "readonly", "async", "override", "declare"}
)


def _get_modifiers(node) -> List[str]:
    mods: List[str] = []
    for child in node.children:
        if child.type in _MODIFIER_TYPES:
            mods.append(child.type)
        elif child.type == "accessibility_modifier":
            mods.append(_txt(child))
    return mods


def _parse_method_node(method_node) -> MethodInfo:
    name_node = method_node.child_by_field_name("name")
    name = _txt(name_node)
    modifiers = _get_modifiers(method_node)
    return_type_node = method_node.child_by_field_name("return_type")
    return_type = _txt(return_type_node).lstrip(":").strip() if return_type_node else None
    params_node = method_node.child_by_field_name("parameters")
    param_count = 0
    if params_node:
        param_count = sum(1 for c in params_node.children if c.type not in (",", "(", ")", "comment"))
    return MethodInfo(
        name=name,
        is_async="async" in modifiers,
        is_static="static" in modifiers,
        is_abstract="abstract" in modifiers,
        modifiers=modifiers,
        return_type=return_type,
        param_count=param_count,
        start_line=method_node.start_point[0] + 1,
        end_line=method_node.end_point[0] + 1,
    )


def _parse_property_node(prop_node) -> PropertyInfo:
    name_node = prop_node.child_by_field_name("name")
    name = _txt(name_node)
    modifiers = _get_modifiers(prop_node)
    type_node = prop_node.child_by_field_name("type")
    type_ann = _txt(type_node).lstrip(":").strip() if type_node else None
    return PropertyInfo(
        name=name,
        type_annotation=type_ann,
        modifiers=modifiers,
        start_line=prop_node.start_point[0] + 1,
    )


def _parse_class_node(class_node, is_exported: bool = False) -> ClassInfo:
    name_node = class_node.child_by_field_name("name")
    name = _txt(name_node)
    start_line = class_node.start_point[0] + 1
    end_line = class_node.end_point[0] + 1
    is_abstract = any(c.type == "abstract" for c in class_node.children)

    implements: List[str] = []
    extends: Optional[str] = None
    for child in class_node.children:
        if child.type == "class_heritage":
            for clause in child.children:
                if clause.type == "extends_clause":
                    for item in clause.children:
                        if item.type in ("type_identifier", "identifier"):
                            extends = _txt(item)
                            break
                        elif item.type == "generic_type":
                            inner = item.child_by_field_name("name")
                            extends = _txt(inner) if inner else _txt(item)
                            break
                elif clause.type == "implements_clause":
                    for item in clause.children:
                        if item.type == "type_identifier":
                            implements.append(_txt(item))
                        elif item.type == "generic_type":
                            inner = item.child_by_field_name("name")
                            implements.append(_txt(inner) if inner else _txt(item))

    methods: List[MethodInfo] = []
    properties: List[PropertyInfo] = []
    body = class_node.child_by_field_name("body")
    if body:
        for member in body.children:
            if member.type in ("method_definition", "abstract_method_signature"):
                methods.append(_parse_method_node(member))
            elif member.type in ("public_field_definition", "field_definition"):
                properties.append(_parse_property_node(member))

    return ClassInfo(
        name=name,
        implements=implements,
        extends=extends,
        methods=methods,
        properties=properties,
        is_abstract=is_abstract,
        is_exported=is_exported,
        start_line=start_line,
        end_line=end_line,
    )


def _parse_imports_from_root(root) -> List[ImportInfo]:
    imports: List[ImportInfo] = []
    for node in _find_all(root, "import_statement"):
        start_line = node.start_point[0] + 1
        source_node = node.child_by_field_name("source")
        source = _txt(source_node).strip("\"'`") if source_node else ""
        names: List[str] = []
        default_name: Optional[str] = None
        is_type_only = any(c.type == "type" for c in node.children)
        for child in node.children:
            if child.type == "import_clause":
                for sub in child.children:
                    if sub.type == "type":
                        is_type_only = True
                    elif sub.type == "identifier":
                        default_name = _txt(sub)
                    elif sub.type == "named_imports":
                        for spec in sub.children:
                            if spec.type == "import_specifier":
                                nm = spec.child_by_field_name("name")
                                if nm:
                                    names.append(_txt(nm))
        imports.append(
            ImportInfo(
                source=source,
                names=names,
                default_name=default_name,
                is_type_only=is_type_only,
                start_line=start_line,
            )
        )
    return imports


def _parse_interfaces_from_root(root) -> List[InterfaceInfo]:
    interfaces: List[InterfaceInfo] = []

    def _members(body) -> tuple[List[str], List[str]]:
        method_names: List[str] = []
        property_names: List[str] = []
        if body:
            for member in body.children:
                if member.type == "method_signature":
                    mn = member.child_by_field_name("name")
                    if mn:
                        method_names.append(_txt(mn))
                elif member.type == "property_signature":
                    pn = member.child_by_field_name("name")
                    if pn:
                        property_names.append(_txt(pn))
        return method_names, property_names

    for node in _find_all(root, "interface_declaration"):
        name_node = node.child_by_field_name("name")
        name = _txt(name_node)
        is_exported = node.parent is not None and node.parent.type == "export_statement"
        method_names, property_names = _members(node.child_by_field_name("body"))
        interfaces.append(
            InterfaceInfo(
                name=name,
                method_names=method_names,
                property_names=property_names,
                is_exported=is_exported,
                start_line=node.start_point[0] + 1,
            )
        )

    for node in _find_all(root, "export_statement"):
        inner = node.child_by_field_name("declaration")
        if inner and inner.type == "interface_declaration":
            name_node = inner.child_by_field_name("name")
            name = _txt(name_node)
            if not any(i.name == name for i in interfaces):
                method_names, property_names = _members(inner.child_by_field_name("body"))
                interfaces.append(
                    InterfaceInfo(
                        name=name,
                        method_names=method_names,
                        property_names=property_names,
                        is_exported=True,
                        start_line=inner.start_point[0] + 1,
                    )
                )
    return interfaces


def _parse_calls_from_root(root) -> List[CallInfo]:
    calls: List[CallInfo] = []
    for node in _find_all(root, "call_expression"):
        fn_node = node.child_by_field_name("function")
        args_node = node.child_by_field_name("arguments")
        calls.append(
            CallInfo(
                callee=_txt(fn_node) if fn_node else "",
                args_text=_txt(args_node) if args_node else "",
                start_line=node.start_point[0] + 1,
            )
        )
    return calls


class TypeScriptScanner(MERNScanner):
    """MERNScanner backed by tree-sitter TypeScript AST analysis.

    Falls back to returning no structured results when tree-sitter is not
    installed (``pip install "tree-sitter>=0.23" tree-sitter-typescript``) -
    subclasses relying purely on structured extraction return no violations
    rather than raising.
    """

    TREE_SITTER_AVAILABLE: bool = _TREE_SITTER_AVAILABLE

    def parse_file(self, path: Path):
        if not _TREE_SITTER_AVAILABLE:
            return None
        try:
            content = path.read_bytes()
            parser = _TSX_PARSER if path.suffix == ".tsx" else _TS_PARSER
            return parser.parse(content).root_node
        except Exception:
            return None

    def find_nodes(self, node, *types: str) -> list:
        return _find_all(node, *types) if node is not None else []

    def node_text(self, node) -> str:
        return _txt(node)

    def get_classes(self, root) -> List[ClassInfo]:
        if root is None:
            return []
        classes: List[ClassInfo] = []
        seen_names: set = set()
        for node in _find_all(root, "export_statement"):
            inner = node.child_by_field_name("declaration")
            if inner and inner.type == "class_declaration":
                ci = _parse_class_node(inner, is_exported=True)
                seen_names.add(ci.name)
                classes.append(ci)
        for node in _find_all(root, "class_declaration"):
            if node.parent is not None and node.parent.type == "export_statement":
                continue
            ci = _parse_class_node(node, is_exported=False)
            if ci.name not in seen_names:
                classes.append(ci)
        return classes

    def get_imports(self, root) -> List[ImportInfo]:
        return _parse_imports_from_root(root) if root is not None else []

    def get_interfaces(self, root) -> List[InterfaceInfo]:
        return _parse_interfaces_from_root(root) if root is not None else []

    def get_calls(self, root) -> List[CallInfo]:
        return _parse_calls_from_root(root) if root is not None else []

    def has_import_from(self, root, *sources: str) -> bool:
        return any(imp.source in sources for imp in self.get_imports(root))

    def imported_names_from(self, root, source: str) -> List[str]:
        for imp in self.get_imports(root):
            if imp.source == source:
                return imp.names
        return []

    def calls_matching(self, root, *patterns: str) -> List[CallInfo]:
        import re

        return [call for call in self.get_calls(root) if any(re.search(p, call.callee) for p in patterns)]

    def get_all_source_files(self, directory: Path) -> List[Path]:
        files: List[Path] = []
        for f in sorted(directory.rglob("*.ts")):
            if "node_modules" not in f.parts:
                files.append(f)
        for f in sorted(directory.rglob("*.tsx")):
            if "node_modules" not in f.parts:
                files.append(f)
        return files
