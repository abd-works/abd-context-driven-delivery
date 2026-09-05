"""Scanner: arg naming — verify argument names are preserved across layers.

Checks:
1. For each public method in shared/, extract its parameter names.
2. Compare with the matching method in the controller and service.
3. Flag when the same positional arg has a different name across tiers.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from .ts_scanner_base import TypeScriptScanner
except ImportError:
    from ts_scanner_base import TypeScriptScanner


_METHOD_WITH_PARAMS_RE = re.compile(
    r'(?:async\s+)?(\w+)\s*\(([^)]*)\)\s*(?::\s*[^{]+)?\s*\{',
)

_PARAM_NAME_RE = re.compile(r'(\w+)\s*[?:]')


def _extract_param_names(params_str: str) -> List[str]:
    """Extract parameter names from a TypeScript method signature."""
    names = []
    for part in params_str.split(','):
        part = part.strip()
        if not part:
            continue
        m = _PARAM_NAME_RE.match(part)
        if m:
            names.append(m.group(1))
    return names


def _extract_methods_with_params(path: Path) -> Dict[str, List[str]]:
    """Map method name → list of param names for a file."""
    result: Dict[str, List[str]] = {}
    try:
        content = path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return result
    for m in _METHOD_WITH_PARAMS_RE.finditer(content):
        name = m.group(1)
        if name == 'constructor' or name[0].isupper():
            continue
        params = _extract_param_names(m.group(2))
        if params:
            result[name] = params
    return result


class ArgNamingScanner(TypeScriptScanner):
    """Check that argument names are preserved across shared/controller/service."""

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

        shared_dir = domain_path / 'shared'
        server_dir = domain_path / 'server'
        if not shared_dir.exists() or not server_dir.exists():
            return violations

        shared_methods: Dict[str, List[str]] = {}
        for ts_file in shared_dir.glob('*.ts'):
            if ts_file.name in ('index.ts',) or ts_file.name.endswith('.schema.ts'):
                continue
            shared_methods.update(_extract_methods_with_params(ts_file))

        service_methods: Dict[str, List[str]] = {}
        for ts_file in server_dir.glob('*.service.ts'):
            service_methods.update(_extract_methods_with_params(ts_file))

        for method_name, shared_params in shared_methods.items():
            if method_name in service_methods:
                service_params = service_methods[method_name]
                # Skip 'req' and 'res' params (controller-specific)
                service_domain_params = [
                    p for p in service_params if p not in ('req', 'res', 'body')
                ]
                for i, (sp, svc_p) in enumerate(
                    zip(shared_params, service_domain_params)
                ):
                    if sp != svc_p:
                        violations.append(self.v(
                            f"Arg name drift in '{method_name}': shared/ uses "
                            f"'{sp}' but service uses '{svc_p}' at position {i}. "
                            f"Keep the same name across layers.",
                            str(server_dir),
                            severity='warning',
                        ))

        return violations


if __name__ == '__main__':
    try:
        from ts_scanner_base import run_scanner_main
    except ImportError:
        from scanners.typescript.ts_scanner_base import run_scanner_main
    run_scanner_main(ArgNamingScanner, 'preserve-arg-names-across-layers')
