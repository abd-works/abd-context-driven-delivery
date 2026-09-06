"""Scanner: view naming — React components end with View, domain-aligned stem.

Checks:
1. Every .tsx component file in client/ exports a component whose name ends
   with 'View'.
2. No ad-hoc suffixes (Form, Panel, Container, Wrapper) on domain components.
3. File names match the exported component name.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

try:
    from .ts_scanner_base import TypeScriptScanner
except ImportError:
    from ts_scanner_base import TypeScriptScanner


_EXPORT_COMPONENT_RE = re.compile(
    r'export\s+(?:default\s+)?(?:function|const)\s+([A-Z]\w+)',
)

_EXEMPT_FILENAMES = frozenset({
    'App', 'main', 'icons', 'vite-env', 'index',
})

_WRONG_SUFFIXES = frozenset({
    'Form', 'Panel', 'Container', 'Wrapper', 'Page', 'Widget',
    'Bar', 'Sidebar', 'Modal', 'Drawer',
})


class ViewNamingScanner(TypeScriptScanner):
    """Check that client .tsx components follow the {Domain}View naming."""

    def scan(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        project_root = self._get_project_root(context)
        if project_root is None:
            return violations

        for domain_path in self._find_domain_packages(project_root):
            violations += self._check_client(domain_path)

        return violations

    def _check_client(self, domain_path: Path) -> List[Dict[str, Any]]:
        violations: List[Dict[str, Any]] = []
        client_dir = domain_path / 'client'
        if not client_dir.exists():
            return violations

        for tsx_file in sorted(client_dir.rglob('*.tsx')):
            if 'node_modules' in tsx_file.parts or 'pages' in tsx_file.parts:
                continue
            stem = tsx_file.stem
            if stem in _EXEMPT_FILENAMES or stem.startswith('_'):
                continue

            try:
                content = tsx_file.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue

            exported = [m.group(1) for m in _EXPORT_COMPONENT_RE.finditer(content)]

            for comp_name in exported:
                if not comp_name.endswith('View'):
                    for suffix in _WRONG_SUFFIXES:
                        if comp_name.endswith(suffix):
                            base = comp_name[:-len(suffix)]
                            violations.append(self.v(
                                f"Component '{comp_name}' in {tsx_file.name} uses "
                                f"suffix '{suffix}'. Rename to '{base}View' to "
                                f"follow the consistent View naming convention.",
                                str(tsx_file),
                                severity='warning',
                            ))
                            break
                    else:
                        violations.append(self.v(
                            f"Component '{comp_name}' in {tsx_file.name} does not "
                            f"end with 'View'. Rename to '{comp_name}View'.",
                            str(tsx_file),
                            severity='warning',
                        ))

                if comp_name != stem and comp_name != f'{stem}':
                    if not stem.endswith('View') and comp_name.endswith('View'):
                        violations.append(self.v(
                            f"File '{tsx_file.name}' does not match component "
                            f"name '{comp_name}'. Rename file to "
                            f"'{comp_name}.tsx'.",
                            str(tsx_file),
                            severity='warning',
                        ))

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(ViewNamingScanner, 'consistent-view-naming')
