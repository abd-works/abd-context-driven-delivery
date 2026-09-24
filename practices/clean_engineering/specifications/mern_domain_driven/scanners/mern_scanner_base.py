"""Base scanners for MERN architecture checks. Scanner and Violation live in
``_scan_base`` beside these files — same idea as Draw.io's ``_drawio_base``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from practices.clean_engineering.specifications.mern_domain_driven.scanners._scan_base import (
    Scanner,
    Violation,
)

__all__ = ["MERNScanner", "Scanner", "TypeScriptScanner", "Violation"]

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


class TypeScriptScanner(MERNScanner):
    """MERNScanner backed by tree-sitter TypeScript AST analysis.

    Falls back to returning no structured results when tree-sitter is not
    installed (``pip install "tree-sitter>=0.23" tree-sitter-typescript``) -
    subclasses relying purely on structured extraction return no violations
    rather than raising.
    """

    TREE_SITTER_AVAILABLE: bool = _TREE_SITTER_AVAILABLE

    def _txt(self, node) -> str:
        if node is None:
            return ""
        b = node.text
        return b.decode("utf-8", errors="replace") if isinstance(b, bytes) else str(b or "")


    def _find_all(self, node, *types: str) -> list:
        results: list = []
        if node.type in types:
            results.append(node)
        for child in node.children:
            results.extend(self._find_all(child, *types))
        return results


    _MODIFIER_TYPES = frozenset(
        {"public", "private", "protected", "abstract", "static", "readonly", "async", "override", "declare"}
    )


    def _get_modifiers(self, node) -> List[str]:
        mods: List[str] = []
        for child in node.children:
            if child.type in self._MODIFIER_TYPES:
                mods.append(child.type)
            elif child.type == "accessibility_modifier":
                mods.append(self._txt(child))
        return mods


    def _parse_method_node(self, method_node) -> MethodInfo:
        name_node = method_node.child_by_field_name("name")
        name = self._txt(name_node)
        modifiers = self._get_modifiers(method_node)
        return_type_node = method_node.child_by_field_name("return_type")
        return_type = self._txt(return_type_node).lstrip(":").strip() if return_type_node else None
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


    def _parse_property_node(self, prop_node) -> PropertyInfo:
        name_node = prop_node.child_by_field_name("name")
        name = self._txt(name_node)
        modifiers = self._get_modifiers(prop_node)
        type_node = prop_node.child_by_field_name("type")
        type_ann = self._txt(type_node).lstrip(":").strip() if type_node else None
        return PropertyInfo(
            name=name,
            type_annotation=type_ann,
            modifiers=modifiers,
            start_line=prop_node.start_point[0] + 1,
        )


    def _type_name_from_item(self, item) -> str:
        if item.type in ("type_identifier", "identifier"):
            return self._txt(item)
        if item.type == "generic_type":
            inner = item.child_by_field_name("name")
            return self._txt(inner) if inner else self._txt(item)
        return ""


    def _parse_class_node(self, class_node, is_exported: bool = False) -> ClassInfo:
        name_node = class_node.child_by_field_name("name")
        name = self._txt(name_node)
        start_line = class_node.start_point[0] + 1
        end_line = class_node.end_point[0] + 1
        is_abstract = any(c.type == "abstract" for c in class_node.children)
        extends, implements = self._class_heritage(class_node)
        methods: List[MethodInfo] = []
        properties: List[PropertyInfo] = []
        body = class_node.child_by_field_name("body")
        if body:
            for member in body.children:
                if member.type in ("method_definition", "abstract_method_signature"):
                    methods.append(self._parse_method_node(member))
                elif member.type in ("public_field_definition", "field_definition"):
                    properties.append(self._parse_property_node(member))
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


    def _class_heritage(self, class_node) -> tuple[Optional[str], List[str]]:
        extends: Optional[str] = None
        implements: List[str] = []
        for child in class_node.children:
            if child.type != "class_heritage":
                continue
            for clause in child.children:
                if clause.type == "extends_clause":
                    extends = self._first_type_in_clause(clause) or extends
                elif clause.type == "implements_clause":
                    implements.extend(self._type_names_in_clause(clause))
        return extends, implements


    def _first_type_in_clause(self, clause) -> str:
        for item in clause.children:
            name = self._type_name_from_item(item)
            if name:
                return name
        return ""


    def _type_names_in_clause(self, clause) -> List[str]:
        names: List[str] = []
        for item in clause.children:
            name = self._type_name_from_item(item)
            if name:
                names.append(name)
        return names


    def _named_import_names(self, clause) -> tuple[list[str], Optional[str], bool]:
        names: List[str] = []
        default_name: Optional[str] = None
        is_type_only = False
        for sub in clause.children:
            if sub.type == "type":
                is_type_only = True
            elif sub.type == "identifier":
                default_name = self._txt(sub)
            elif sub.type == "named_imports":
                names.extend(self._specifier_names(sub))
        return names, default_name, is_type_only

    def _specifier_names(self, named_imports) -> List[str]:
        names: List[str] = []
        for spec in named_imports.children:
            if spec.type != "import_specifier":
                continue
            nm = spec.child_by_field_name("name")
            if nm:
                names.append(self._txt(nm))
        return names

    def _parse_imports_from_root(self, root) -> List[ImportInfo]:
        imports: List[ImportInfo] = []
        for node in self._find_all(root, "import_statement"):
            source_node = node.child_by_field_name("source")
            source = self._txt(source_node).strip("\"'`") if source_node else ""
            names: List[str] = []
            default_name: Optional[str] = None
            is_type_only = any(c.type == "type" for c in node.children)
            for child in node.children:
                if child.type != "import_clause":
                    continue
                extra, default_name, typed = self._named_import_names(child)
                names.extend(extra)
                is_type_only = is_type_only or typed
            imports.append(
                ImportInfo(
                    source=source,
                    names=names,
                    default_name=default_name,
                    is_type_only=is_type_only,
                    start_line=node.start_point[0] + 1,
                )
            )
        return imports


    def _interface_members(self, body) -> tuple[List[str], List[str]]:
        method_names: List[str] = []
        property_names: List[str] = []
        if body is None:
            return method_names, property_names
        for member in body.children:
            if member.type == "method_signature":
                mn = member.child_by_field_name("name")
                if mn:
                    method_names.append(self._txt(mn))
            elif member.type == "property_signature":
                pn = member.child_by_field_name("name")
                if pn:
                    property_names.append(self._txt(pn))
        return method_names, property_names

    def _parse_interfaces_from_root(self, root) -> List[InterfaceInfo]:
        interfaces: List[InterfaceInfo] = []
        for node in self._find_all(root, "interface_declaration"):
            name = self._txt(node.child_by_field_name("name"))
            methods, properties = self._interface_members(node.child_by_field_name("body"))
            interfaces.append(
                InterfaceInfo(
                    name=name,
                    method_names=methods,
                    property_names=properties,
                    is_exported=node.parent is not None and node.parent.type == "export_statement",
                    start_line=node.start_point[0] + 1,
                )
            )
        self._append_exported_interfaces(root, interfaces)
        return interfaces

    def _append_exported_interfaces(self, root, interfaces: List[InterfaceInfo]) -> None:
        for node in self._find_all(root, "export_statement"):
            inner = node.child_by_field_name("declaration")
            if inner is None or inner.type != "interface_declaration":
                continue
            name = self._txt(inner.child_by_field_name("name"))
            if any(i.name == name for i in interfaces):
                continue
            methods, properties = self._interface_members(inner.child_by_field_name("body"))
            interfaces.append(
                InterfaceInfo(
                    name=name,
                    method_names=methods,
                    property_names=properties,
                    is_exported=True,
                    start_line=inner.start_point[0] + 1,
                )
            )


    def _parse_calls_from_root(self, root) -> List[CallInfo]:
        calls: List[CallInfo] = []
        for node in self._find_all(root, "call_expression"):
            fn_node = node.child_by_field_name("function")
            args_node = node.child_by_field_name("arguments")
            calls.append(
                CallInfo(
                    callee=self._txt(fn_node) if fn_node else "",
                    args_text=self._txt(args_node) if args_node else "",
                    start_line=node.start_point[0] + 1,
                )
            )
        return calls

    def parse_file(self, path: Path):
        self._tree = None
        if not _TREE_SITTER_AVAILABLE:
            return None
        try:
            content = path.read_bytes()
            parser = _TSX_PARSER if path.suffix == ".tsx" else _TS_PARSER
            self._tree = parser.parse(content).root_node
            return self._tree
        except Exception:
            return None

    def find_nodes(self, node, *types: str) -> list:
        return self._find_all(node, *types) if node is not None else []

    def node_text(self, node) -> str:
        return self._txt(node)

    @property
    def classes(self) -> List[ClassInfo]:
        root = getattr(self, "_tree", None)
        if root is None:
            return []
        return self._classes_from_tree(root)

    def _classes_from_tree(self, root) -> List[ClassInfo]:
        classes: List[ClassInfo] = []
        seen_names: set = set()
        for node in self._find_all(root, "export_statement"):
            inner = node.child_by_field_name("declaration")
            if inner and inner.type == "class_declaration":
                ci = self._parse_class_node(inner, is_exported=True)
                seen_names.add(ci.name)
                classes.append(ci)
        for node in self._find_all(root, "class_declaration"):
            if node.parent is not None and node.parent.type == "export_statement":
                continue
            ci = self._parse_class_node(node, is_exported=False)
            if ci.name not in seen_names:
                classes.append(ci)
        return classes

    @property
    def imports(self) -> List[ImportInfo]:
        root = getattr(self, "_tree", None)
        return self._parse_imports_from_root(root) if root is not None else []

    @property
    def interfaces(self) -> List[InterfaceInfo]:
        root = getattr(self, "_tree", None)
        return self._parse_interfaces_from_root(root) if root is not None else []

    @property
    def calls(self) -> List[CallInfo]:
        root = getattr(self, "_tree", None)
        return self._parse_calls_from_root(root) if root is not None else []

    def has_import_from(self, source: str) -> bool:
        return any(imp.source == source for imp in self.imports)

    def imported_names_from(self, source: str) -> List[str]:
        for imp in self.imports:
            if imp.source == source:
                return imp.names
        return []

    def calls_matching(self, *patterns: str) -> List[CallInfo]:
        import re

        return [call for call in self.calls if any(re.search(p, call.callee) for p in patterns)]

    def source_files(self, directory: Path) -> List[Path]:
        files: List[Path] = []
        for f in sorted(directory.rglob("*.ts")):
            if "node_modules" not in f.parts:
                files.append(f)
        for f in sorted(directory.rglob("*.tsx")):
            if "node_modules" not in f.parts:
                files.append(f)
        return files
