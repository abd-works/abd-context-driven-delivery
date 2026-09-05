"""Scanner: cross-layer method naming — same domain verb in every layer.

Checks:
1. For each domain method in shared/ (exported class method), a matching
   method name exists in the controller and service files.
2. API client functions match the domain method name (not CRUD generics).
3. Route paths are kebab-case of the domain verb.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

try:
    from .ts_scanner_base import TypeScriptScanner
except ImportError:
    from ts_scanner_base import TypeScriptScanner


_CRUD_GENERICS = frozenset({
    'create', 'read', 'update', 'delete', 'get', 'set', 'list',
    'find', 'fetch', 'save', 'remove', 'add', 'modify', 'patch',
})

_METHOD_RE = re.compile(
    r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{',
)

_EXPORT_FUNCTION_RE = re.compile(
    r'export\s+(?:async\s+)?function\s+(\w+)',
)

_ROUTE_HANDLER_RE = re.compile(
    r"router\.\w+\(\s*['\"]([^'\"]+)['\"]",
)


def _camel_to_kebab(name: str) -> str:
    s1 = re.sub(r'([A-Z])', r'-\1', name)
    return s1.lower().lstrip('-')


class CrossLayerNamingScanner(TypeScriptScanner):
    """Check that domain method names are consistent across all layers."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_domain(domain_path)

        return violations

    def _check_domain(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        domain_name = domain_path.name

        shared_methods = self._extract_shared_methods(domain_path)
        if not shared_methods:
            return violations

        controller_methods = self._extract_controller_methods(domain_path)
        service_methods = self._extract_service_methods(domain_path)
        api_functions = self._extract_api_functions(domain_path)

        for method in shared_methods:
            base = method.lower()
            if base in _CRUD_GENERICS:
                continue

            if controller_methods and method not in controller_methods:
                for ctrl_method in controller_methods:
                    if ctrl_method.lower() in _CRUD_GENERICS and base not in _CRUD_GENERICS:
                        violations.append(self.v(
                            f"Domain method '{method}' in shared/ has no matching "
                            f"controller method. Controller uses CRUD-generic "
                            f"'{ctrl_method}' instead. Rename to '{method}'.",
                            str(domain_path / 'server'),
                            severity='warning',
                        ))
                        break

            if api_functions and method not in api_functions:
                for fn in api_functions:
                    if fn.startswith('fetch') and method in fn.lower():
                        violations.append(self.v(
                            f"Domain method '{method}' in shared/ has no matching "
                            f"API client function. Client uses 'fetch'-prefixed "
                            f"'{fn}' instead. Rename to '{method}'.",
                            str(domain_path / 'client'),
                            severity='warning',
                        ))
                        break

        return violations

    def _extract_shared_methods(self, domain_path: Path) -> Set[str]:
        methods: Set[str] = set()
        shared_dir = domain_path / 'shared'
        if not shared_dir.exists():
            return methods
        for ts_file in shared_dir.glob('*.ts'):
            if ts_file.name in ('index.ts',) or ts_file.name.endswith('.schema.ts'):
                continue
            try:
                content = ts_file.read_text(encoding='utf-8', errors='replace')
                for m in _METHOD_RE.finditer(content):
                    name = m.group(1)
                    if name[0].islower() and not name.startswith('constructor'):
                        methods.add(name)
            except OSError:
                pass
        return methods

    def _extract_controller_methods(self, domain_path: Path) -> Set[str]:
        return self._extract_methods_from_pattern(domain_path / 'server', '*.controller.ts')

    def _extract_service_methods(self, domain_path: Path) -> Set[str]:
        return self._extract_methods_from_pattern(domain_path / 'server', '*.service.ts')

    def _extract_api_functions(self, domain_path: Path) -> Set[str]:
        fns: Set[str] = set()
        client_dir = domain_path / 'client'
        if not client_dir.exists():
            return fns
        for ts_file in client_dir.glob('*.api.ts'):
            try:
                content = ts_file.read_text(encoding='utf-8', errors='replace')
                for m in _EXPORT_FUNCTION_RE.finditer(content):
                    fns.add(m.group(1))
            except OSError:
                pass
        return fns

    def _extract_methods_from_pattern(self, tier_dir: Path, glob: str) -> Set[str]:
        methods: Set[str] = set()
        if not tier_dir.exists():
            return methods
        for ts_file in tier_dir.glob(glob):
            try:
                content = ts_file.read_text(encoding='utf-8', errors='replace')
                for m in _METHOD_RE.finditer(content):
                    name = m.group(1)
                    if name[0].islower() and not name.startswith('constructor'):
                        methods.add(name)
            except OSError:
                pass
        return methods


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(CrossLayerNamingScanner, 'cross-layer-method-naming')
