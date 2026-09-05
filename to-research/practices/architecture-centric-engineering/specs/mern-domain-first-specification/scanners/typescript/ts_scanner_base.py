"""Tree-sitter TypeScript AST base for MERN architecture scanners.

Provides structured extraction of TypeScript classes, interfaces, imports,
method calls, and more using tree-sitter >= 0.23 with the tree_sitter_typescript
grammar. All deep MERN scanners inherit from TypeScriptScanner.

Falls back gracefully when tree-sitter is not installed (scan methods still
run via MERNScanner base, which uses regex instead).

Install: pip install "tree-sitter>=0.23" tree-sitter-typescript
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import tree_sitter as _ts
    import tree_sitter_typescript as _tsts

    _TS_LANG = _ts.Language(_tsts.language_typescript())
    _TSX_LANG = _ts.Language(_tsts.language_tsx())
    _TS_PARSER = _ts.Parser(_TS_LANG)
    _TSX_PARSER = _ts.Parser(_TSX_LANG)
    _TREE_SITTER_AVAILABLE = True
except Exception:
    _TREE_SITTER_AVAILABLE = False
    _TS_LANG = _TSX_LANG = _TS_PARSER = _TSX_PARSER = None

try:
    from .mern_scanner import MERNScanner
except ImportError:
    from mern_scanner import MERNScanner


# ---------------------------------------------------------------------------
# Data classes
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
    implements: List[str]          # interface names from `implements` clause
    extends: Optional[str]         # base class name
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
    source: str              # e.g. 'mongodb', '@pawplace/store-shared'
    names: List[str]         # named imports: ['Collection', 'Db']
    default_name: Optional[str]
    is_type_only: bool
    start_line: int


@dataclass
class CallInfo:
    callee: str              # e.g. 'this.collection.findOne', 'Schema.parse'
    args_text: str
    start_line: int


# ---------------------------------------------------------------------------
# Internal tree-sitter helpers
# ---------------------------------------------------------------------------

def _txt(node) -> str:
    """Decode a tree-sitter node's bytes to a string."""
    if node is None:
        return ''
    b = node.text
    return b.decode('utf-8', errors='replace') if isinstance(b, bytes) else str(b or '')


def _find_all(node, *types: str) -> list:
    """Recursively collect all descendant nodes whose type is in *types*."""
    results: list = []
    if node.type in types:
        results.append(node)
    for child in node.children:
        results.extend(_find_all(child, *types))
    return results


def _find_first(node, *types: str):
    """Return the first descendant whose type is in *types*, or None."""
    if node.type in types:
        return node
    for child in node.children:
        result = _find_first(child, *types)
        if result is not None:
            return result
    return None


_MODIFIER_TYPES = frozenset({
    'public', 'private', 'protected', 'abstract', 'static',
    'readonly', 'async', 'override', 'declare',
})


def _get_modifiers(node) -> List[str]:
    mods: List[str] = []
    for child in node.children:
        if child.type in _MODIFIER_TYPES:
            mods.append(child.type)
        elif child.type == 'accessibility_modifier':
            mods.append(_txt(child))
    return mods


def _parse_class_node(class_node, is_exported: bool = False) -> ClassInfo:
    name_node = class_node.child_by_field_name('name')
    name = _txt(name_node)
    start_line = class_node.start_point[0] + 1
    end_line = class_node.end_point[0] + 1

    is_abstract = any(c.type == 'abstract' for c in class_node.children)

    implements: List[str] = []
    extends: Optional[str] = None

    for child in class_node.children:
        if child.type == 'class_heritage':
            for clause in child.children:
                if clause.type == 'extends_clause':
                    for item in clause.children:
                        if item.type in ('type_identifier', 'identifier'):
                            extends = _txt(item)
                            break
                        elif item.type == 'generic_type':
                            inner = item.child_by_field_name('name')
                            extends = _txt(inner) if inner else _txt(item)
                            break
                elif clause.type == 'implements_clause':
                    for item in clause.children:
                        if item.type == 'type_identifier':
                            implements.append(_txt(item))
                        elif item.type == 'generic_type':
                            inner = item.child_by_field_name('name')
                            implements.append(_txt(inner) if inner else _txt(item))

    methods: List[MethodInfo] = []
    properties: List[PropertyInfo] = []
    body = class_node.child_by_field_name('body')
    if body:
        for member in body.children:
            if member.type in ('method_definition', 'abstract_method_signature'):
                methods.append(_parse_method_node(member))
            elif member.type in ('public_field_definition', 'field_definition'):
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


def _parse_method_node(method_node) -> MethodInfo:
    name_node = method_node.child_by_field_name('name')
    name = _txt(name_node)
    modifiers = _get_modifiers(method_node)
    return_type_node = method_node.child_by_field_name('return_type')
    return_type = _txt(return_type_node).lstrip(':').strip() if return_type_node else None
    params_node = method_node.child_by_field_name('parameters')
    param_count = 0
    if params_node:
        param_count = sum(
            1 for c in params_node.children
            if c.type not in (',', '(', ')', 'comment')
        )
    return MethodInfo(
        name=name,
        is_async='async' in modifiers,
        is_static='static' in modifiers,
        is_abstract='abstract' in modifiers,
        modifiers=modifiers,
        return_type=return_type,
        param_count=param_count,
        start_line=method_node.start_point[0] + 1,
        end_line=method_node.end_point[0] + 1,
    )


def _parse_property_node(prop_node) -> PropertyInfo:
    name_node = prop_node.child_by_field_name('name')
    name = _txt(name_node)
    modifiers = _get_modifiers(prop_node)
    type_node = prop_node.child_by_field_name('type')
    type_ann = _txt(type_node).lstrip(':').strip() if type_node else None
    return PropertyInfo(
        name=name,
        type_annotation=type_ann,
        modifiers=modifiers,
        start_line=prop_node.start_point[0] + 1,
    )


def _parse_imports_from_root(root) -> List[ImportInfo]:
    imports: List[ImportInfo] = []
    for node in _find_all(root, 'import_statement'):
        start_line = node.start_point[0] + 1
        source_node = node.child_by_field_name('source')
        source = _txt(source_node).strip('"\'`') if source_node else ''
        names: List[str] = []
        default_name: Optional[str] = None
        # `import type` has a 'type' keyword child — detect it
        is_type_only = any(c.type == 'type' for c in node.children)
        for child in node.children:
            if child.type == 'import_clause':
                for sub in child.children:
                    if sub.type == 'type':
                        is_type_only = True
                    elif sub.type == 'identifier':
                        default_name = _txt(sub)
                    elif sub.type == 'named_imports':
                        for spec in sub.children:
                            if spec.type == 'import_specifier':
                                nm = spec.child_by_field_name('name')
                                if nm:
                                    names.append(_txt(nm))
        imports.append(ImportInfo(
            source=source,
            names=names,
            default_name=default_name,
            is_type_only=is_type_only,
            start_line=start_line,
        ))
    return imports


def _parse_interfaces_from_root(root) -> List[InterfaceInfo]:
    interfaces: List[InterfaceInfo] = []
    for node in _find_all(root, 'interface_declaration'):
        name_node = node.child_by_field_name('name')
        name = _txt(name_node)
        is_exported = (node.parent is not None and node.parent.type == 'export_statement')
        method_names: List[str] = []
        property_names: List[str] = []
        body = node.child_by_field_name('body')
        if body:
            for member in body.children:
                if member.type == 'method_signature':
                    mn = member.child_by_field_name('name')
                    if mn:
                        method_names.append(_txt(mn))
                elif member.type == 'property_signature':
                    pn = member.child_by_field_name('name')
                    if pn:
                        property_names.append(_txt(pn))
        interfaces.append(InterfaceInfo(
            name=name,
            method_names=method_names,
            property_names=property_names,
            is_exported=is_exported,
            start_line=node.start_point[0] + 1,
        ))
    # Also check export_statement wrapping an interface_declaration
    for node in _find_all(root, 'export_statement'):
        inner = node.child_by_field_name('declaration')
        if inner and inner.type == 'interface_declaration':
            name_node = inner.child_by_field_name('name')
            name = _txt(name_node)
            if not any(i.name == name for i in interfaces):
                method_names = []
                property_names = []
                body = inner.child_by_field_name('body')
                if body:
                    for member in body.children:
                        if member.type == 'method_signature':
                            mn = member.child_by_field_name('name')
                            if mn:
                                method_names.append(_txt(mn))
                        elif member.type == 'property_signature':
                            pn = member.child_by_field_name('name')
                            if pn:
                                property_names.append(_txt(pn))
                interfaces.append(InterfaceInfo(
                    name=name,
                    method_names=method_names,
                    property_names=property_names,
                    is_exported=True,
                    start_line=inner.start_point[0] + 1,
                ))
    return interfaces


def _parse_calls_from_root(root) -> List[CallInfo]:
    calls: List[CallInfo] = []
    for node in _find_all(root, 'call_expression'):
        fn_node = node.child_by_field_name('function')
        args_node = node.child_by_field_name('arguments')
        callee = _txt(fn_node) if fn_node else ''
        args_text = _txt(args_node) if args_node else ''
        calls.append(CallInfo(
            callee=callee,
            args_text=args_text,
            start_line=node.start_point[0] + 1,
        ))
    return calls


# ---------------------------------------------------------------------------
# TypeScriptScanner — the base all deep MERN scanners inherit from
# ---------------------------------------------------------------------------

class TypeScriptScanner(MERNScanner):
    """MERNScanner subclass backed by tree-sitter TypeScript AST analysis.

    Subclasses implement scan(context) using the rich extraction methods
    provided here. When tree-sitter is unavailable the base parse_file()
    returns None and callers should fall back to regex heuristics.
    """

    TREE_SITTER_AVAILABLE: bool = _TREE_SITTER_AVAILABLE

    # ------------------------------------------------------------------ #
    # Parsing                                                              #
    # ------------------------------------------------------------------ #

    def parse_file(self, path: Path):
        """Parse a .ts / .tsx file; return the AST root node or None."""
        if not _TREE_SITTER_AVAILABLE:
            return None
        try:
            content = path.read_bytes()
            parser = _TSX_PARSER if path.suffix == '.tsx' else _TS_PARSER
            return parser.parse(content).root_node
        except Exception:
            return None

    # ------------------------------------------------------------------ #
    # Node traversal helpers                                               #
    # ------------------------------------------------------------------ #

    def find_nodes(self, node, *types: str) -> list:
        return _find_all(node, *types) if node is not None else []

    def find_first(self, node, *types: str):
        return _find_first(node, *types) if node is not None else None

    def node_text(self, node) -> str:
        return _txt(node)

    # ------------------------------------------------------------------ #
    # Structured extraction                                                #
    # ------------------------------------------------------------------ #

    def get_classes(self, root) -> List[ClassInfo]:
        """All class declarations in the file, with export flag set."""
        if root is None:
            return []
        classes: List[ClassInfo] = []
        seen_names: set = set()
        # exported classes
        for node in _find_all(root, 'export_statement'):
            inner = node.child_by_field_name('declaration')
            if inner and inner.type == 'class_declaration':
                ci = _parse_class_node(inner, is_exported=True)
                seen_names.add(ci.name)
                classes.append(ci)
        # non-exported classes
        for node in _find_all(root, 'class_declaration'):
            if node.parent is not None and node.parent.type == 'export_statement':
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

    # ------------------------------------------------------------------ #
    # Convenience query methods                                            #
    # ------------------------------------------------------------------ #

    def has_import_from(self, root, *sources: str) -> bool:
        for imp in self.get_imports(root):
            if imp.source in sources:
                return True
        return False

    def imported_names_from(self, root, source: str) -> List[str]:
        for imp in self.get_imports(root):
            if imp.source == source:
                return imp.names
        return []

    def calls_matching(self, root, *patterns: str) -> List[CallInfo]:
        import re
        results: List[CallInfo] = []
        for call in self.get_calls(root):
            if any(re.search(p, call.callee) for p in patterns):
                results.append(call)
        return results

    def get_all_source_files(self, directory: Path) -> List[Path]:
        """All .ts and .tsx files under a directory (no node_modules)."""
        files: List[Path] = []
        for f in sorted(directory.rglob('*.ts')):
            if 'node_modules' not in f.parts:
                files.append(f)
        for f in sorted(directory.rglob('*.tsx')):
            if 'node_modules' not in f.parts:
                files.append(f)
        return files

    # ------------------------------------------------------------------ #
    # Violation builder                                                    #
    # ------------------------------------------------------------------ #

    def v(
        self,
        message: str,
        location: str,
        line: int = 0,
        severity: str = 'error',
    ) -> Dict[str, Any]:
        return {
            'rule': self.rule,
            'message': message,
            'location': location,
            'line': line,
            'severity': severity,
        }


# ---------------------------------------------------------------------------
# Standard __main__ entrypoint factory
# ---------------------------------------------------------------------------

def run_scanner_main(scanner_class, rule_name: str) -> None:
    """Standard CLI entrypoint for all MERN scanners.

    Parses --workspace, builds context, runs scan(), prints violations to
    stderr as Python dict literals (required by run_scanners.py), and exits
    with code 1 if violations found, 0 if clean.
    """
    import argparse
    import sys

    p = argparse.ArgumentParser()
    p.add_argument('--workspace', type=Path, default=Path.cwd())
    p.add_argument('--story-graph', type=Path, default=None)
    args = p.parse_args()

    context = {'project_root': str(args.workspace.resolve())}
    scanner = scanner_class(rule_name)
    violations = scanner.scan(context)

    for v in violations:
        out = {
            'violation_message': v.get('message', str(v)),
            'severity': v.get('severity', 'error'),
            'location': v.get('location', ''),
            'line': v.get('line', 0),
        }
        print(out, file=sys.stderr)

    sys.exit(1 if violations else 0)
